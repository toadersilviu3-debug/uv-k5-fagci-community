# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# UV-K5 driver (c) 2023 Jacek Lipkowski <sq5bpf@lipkowski.org>.
# Serial transport based on that driver, originally based on template.py
# Copyright 2012 Dan Smith <dsmith@danplanet.com>. The supplied IJV adaptation
# credits Julian Lilov LZ1JDL and Francesco IK8JHL. Their firmware-specific
# EEPROM interpretation is NOT used here.
# TXM0008 mapping and RX profiles: independent community adaptation, 2026-10-14,
# prepared with Codex assistance. No endorsement by upstream authors implied.
# This program is free software under GPL version 3 or later, WITHOUT WARRANTY.
# See COPYING_GPL3.txt. Only OSFW-TXM0008 is accepted, before any EEPROM access.

import base64
import binascii
import logging
import struct

from chirp import chirp_common, directory, errors, memmap
from chirp.settings import (RadioSettings, RadioSetting, RadioSettingGroup,
                            RadioSettingValueBoolean, RadioSettingValueInteger,
                            RadioSettingValueList, RadioSettingValueString)

LOG = logging.getLogger(__name__)
FIRMWARE = "OSFW-TXM0008"
MEM_SIZE = 0x2000
BLOCK = 0x80
TIMESTAMP = b"\x6a\x39\x57\x64"
XOR_KEY = bytes.fromhex("16 6c 14 e6 2e 91 0d 40 21 35 d5 40 13 03 e9 80")
STEPS = [0.01, 0.1, 0.5, 1.0, 2.5, 5.0, 6.25, 8.33, 10.0, 12.5, 25.0, 100.0]
BANDS = [(15000000, 107999900), (108000000, 135999900),
         (136000000, 173999900), (174000000, 349999900),
         (350000000, 399999900), (400000000, 469999900),
         (470000000, 1340000000)]
TONES = [67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8, 97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8, 136.5, 141.3, 146.2, 151.4, 156.7, 159.8, 162.2, 165.5, 167.9, 171.3, 173.8, 177.3, 179.9, 183.5, 186.2, 189.9, 192.8, 196.6, 199.5, 203.5, 206.5, 210.7, 218.1, 225.7, 229.1, 233.6, 241.8, 250.3, 254.1]
DTCS = [23, 25, 26, 31, 32, 36, 43, 47, 51, 53, 54, 65, 71, 72, 73, 74, 114, 115, 116, 122, 125, 131, 132, 134, 143, 145, 152, 155, 156, 162, 165, 172, 174, 205, 212, 223, 225, 226, 243, 244, 245, 246, 251, 252, 255, 261, 263, 265, 266, 271, 274, 306, 311, 315, 325, 331, 332, 343, 346, 351, 356, 364, 365, 371, 411, 412, 413, 423, 431, 432, 445, 446, 452, 454, 455, 462, 464, 465, 466, 503, 506, 516, 523, 526, 532, 546, 565, 606, 612, 624, 627, 631, 632, 654, 662, 664, 703, 712, 723, 731, 732, 734, 743, 754]
POWER = [chirp_common.PowerLevel("Low", watts=1),
         chirp_common.PowerLevel("Mid", watts=2.5),
         chirp_common.PowerLevel("High", watts=5)]
MODELS = ["FM", "AM", "USB", "BYP", "RAW"]


def _xor(data):
    return bytes(value ^ XOR_KEY[i % 16] for i, value in enumerate(data))


def _read_exact(pipe, size):
    result = b""
    while len(result) < size:
        part = pipe.read(size - len(result))
        if not part:
            raise errors.RadioError("Incomplete serial reply (%d/%d bytes)" % (len(result), size))
        result += part
    return result


def _exchange(pipe, payload, response=True):
    crc = struct.pack("<H", binascii.crc_hqx(payload, 0))
    packet = b"\xab\xcd" + bytes([len(payload), 0]) + _xor(payload + crc) + b"\xdc\xba"
    try:
        count = pipe.write(packet)
        if count is not None and count != len(packet):
            raise errors.RadioError("Incomplete serial write")
        if not response:
            return b""
        header = _read_exact(pipe, 4)
        if header[:2] != b"\xab\xcd" or header[3] != 0:
            raise errors.RadioError("Invalid radio reply header")
        body = _read_exact(pipe, header[2])
        footer = _read_exact(pipe, 4)
        if footer[2:] != b"\xdc\xba":
            raise errors.RadioError("Invalid radio reply footer")
        return _xor(body)
    except errors.RadioError:
        raise
    except Exception as exc:
        raise errors.RadioError("Serial communication failed: %s" % exc)


def _hello(pipe):
    pipe.timeout = 0.8
    for attempt in range(3):
        try:
            answer = _exchange(pipe, b"\x14\x05\x04\x00" + TIMESTAMP)
            break
        except errors.RadioError:
            if attempt == 2:
                raise
            if hasattr(pipe, "reset_input_buffer"):
                pipe.reset_input_buffer()
    if len(answer) != 40 or answer[:4] != b"\x15\x05\x24\x00":
        raise errors.RadioError("Invalid firmware identification reply")
    version = answer[4:20].split(b"\0", 1)[0].split(b"\xff", 1)[0].decode("ascii", "replace")
    if version != FIRMWARE:
        raise errors.RadioError("This driver requires %s; radio reports %s" % (FIRMWARE, version))
    if answer[20]:
        raise errors.RadioError("Custom AES-locked programming is not supported by this driver")
    return version


def _read_block(pipe, address, size):
    reply = _exchange(pipe, b"\x1b\x05\x08\x00" + struct.pack("<HBB", address, size, 0) + TIMESTAMP)
    if (len(reply) != size + 8 or reply[:4] != struct.pack("<HH", 0x051c, size+4) or
            struct.unpack_from("<H", reply, 4)[0] != address or reply[6] != size):
        raise errors.RadioError("Incorrect EEPROM read reply at 0x%04X" % address)
    return reply[8:]


def _write_block(pipe, address, data):
    if address % 8 or len(data) != 8:
        raise errors.RadioError("Unaligned EEPROM write rejected")
    command = b"\x1d\x05" + struct.pack("<BBHBB", len(data) + 8, 0, address, len(data), 0)
    reply = _exchange(pipe, command + TIMESTAMP + data)
    if len(reply) != 6 or reply[:4] != b"\x1e\x05\x02\x00" or struct.unpack_from("<H", reply, 4)[0] != address:
        raise errors.RadioError("Incorrect EEPROM write acknowledgement at 0x%04X" % address)


def _band(freq):
    for index, (low, high) in enumerate(BANDS):
        if low <= freq <= high:
            return index
    raise errors.InvalidValueError("Frequency is outside the TXM0008 bands")


def _text(data):
    raw = data.split(b"\0", 1)[0].split(b"\xff", 1)[0]
    return "".join(chr(c) if 32 <= c <= 126 else " " for c in raw).rstrip()


def _list(name, label, options, index):
    return RadioSetting(name, label, RadioSettingValueList(options, current_index=max(0, min(index, len(options)-1))))


def _integer(name, label, low, high, value):
    return RadioSetting(name, label, RadioSettingValueInteger(low, high, max(low, min(high, value))))


def _extras(memory):
    return {setting.get_name(): setting.value for setting in memory.extra}


def _tone_decode(kind, code):
    if kind == 1 and code < len(TONES):
        return "Tone", TONES[code], None
    if kind in (2, 3) and code < len(DTCS):
        return "DTCS", DTCS[code], "R" if kind == 3 else "N"
    return "", None, None


def _tone_encode(tone):
    kind, value, polarity = tone
    if not kind:
        return 0, 0
    if kind == "Tone" and value in TONES:
        return 1, TONES.index(value)
    if kind == "DTCS" and value in DTCS:
        return (3 if polarity == "R" else 2), DTCS.index(value)
    raise errors.InvalidValueError("Unsupported tone or DCS code")


# (key, label, address, options OR (min,max), offset added for display).
SETTINGS = [
    ("call", "One-touch call channel", 0xe70, (1, 200), 1),
    ("sql", "Squelch", 0xe71, (0, 9), 0),
    ("tot", "TX timeout", 0xe72, ["OFF"] + ["%d min" % n for n in range(1, 11)], 0),
    ("keylock", "Keypad lock", 0xe74, ["OFF", "ON"], 0),
    ("vox", "VOX", 0xe75, ["OFF", "ON"], 0),
    ("voxlevel", "VOX level", 0xe76, (1, 10), 1),
    ("mic", "Microphone sensitivity", 0xe77, (0, 4), 0),
    ("mdf", "Channel display", 0xe79, ["FREQ", "CHAN", "NAME", "NAME+F"], 0),
    ("crossband", "Cross-band (menu WX)", 0xe7a, ["OFF", "CHAN_A", "CHAN_B"], 0),
    ("save", "Battery saving", 0xe7b, ["OFF", "1:1", "1:2", "1:3", "1:4"], 0),
    ("dw", "Dual Watch", 0xe7c, ["OFF", "CHAN_A", "CHAN_B"], 0),
    ("backlight", "Backlight", 0xe7d, ["OFF", "5 sec", "10 sec", "20 sec", "1 min", "2 min", "ON"], 0),
    ("ste", "Squelch tail elimination", 0xe7e, ["OFF", "ON"], 0),
    ("vfo", "VFO mode available", 0xe7f, ["OFF", "ON"], 0),
    ("beep", "Keypad beep", 0xe90, ["OFF", "ON"], 0),
    ("scanresume", "Scan resume", 0xe95, ["TO", "CO", "SE"], 0),
    ("autolock", "Automatic keypad lock", 0xe96, ["OFF", "ON"], 0),
    ("startup", "Startup display", 0xe97, ["FULL", "MSG", "VOL"], 0),
    ("voice", "Stored voice setting (no playback in firmware)", 0xea0, ["OFF", "CHI", "ENG"], 0),
    ("roger", "End-of-transmission signal", 0xea9, ["OFF", "ROGER", "MDC"], 0),
    ("tail", "Repeater tail delay (100 ms units)", 0xeaa, (0, 10), 0),
    ("txvfo", "Active transmit VFO", 0xeab, ["A", "B"], 0),
    ("scanlist", "Default scan list", 0xf18, ["LIST1", "LIST2"], 0),
    ("priority1", "List 1 priority scan", 0xf19, ["OFF", "ON"], 0),
    ("priority2", "List 2 priority scan", 0xf1c, ["OFF", "ON"], 0),
    ("flock", "TX frequency-limit profile", 0xf40, ["OFF", "FCC", "CE", "GB", "LPD PMR", "Reserved"], 0),
    ("350tx", "350 MHz TX permission", 0xf41, ["OFF", "ON"], 0),
    ("200tx", "200 MHz TX permission", 0xf43, ["OFF", "ON"], 0),
    ("500tx", "500 MHz TX permission", 0xf44, ["OFF", "ON"], 0),
    ("alltx", "Overall TX permission", 0xf45, ["DEFAULT", "ENABLE", "DISABLE"], 0),
    ("scren", "Global scrambling", 0xf46, ["OFF", "ON"], 0),
]
KEY_ACTIONS = ["None", "Flashlight / SOS", "TX power", "Monitor", "Scan", "VOX",
               "Reserved (no action)", "FM broadcast", "1750 Hz"]
for _index, _label in enumerate(["Side 1 short", "Side 1 long", "Side 2 short",
                                "Side 2 long (VFO save takes priority)"]):
    SETTINGS.append(("key%d" % _index, _label, 0xe91 + _index, KEY_ACTIONS, 0))
for _key, _label, _addr in [("side", "DTMF sidetone", 0xed0),
                            ("response", "DTMF response", 0xed3),
                            ("remote", "DTMF remote kill permission", 0xeda)]:
    SETTINGS.append((_key, _label, _addr, ["NULL", "RING", "REPLY", "BOTH"] if _key == "response" else ["OFF", "ON"], 0))
SETTINGS.append(("hold", "DTMF hold time (seconds)", 0xed4, (5, 60), 0))
for _key, _label, _addr in [("pre", "DTMF pre-delay", 0xed5), ("first", "DTMF first symbol", 0xed6),
                            ("hash", "DTMF star/hash symbol", 0xed7), ("persist", "DTMF symbol", 0xed8),
                            ("interval", "DTMF interval", 0xed9)]:
    SETTINGS.append((_key, _label + " (10 ms units)", _addr, (0, 100), 0))
STRINGS = [("logo1", "Startup message line 1", 0xeb0, 16), ("logo2", "Startup message line 2", 0xec0, 16),
           ("ani", "ANI ID", 0xee0, 8), ("kill", "Stored kill code (unused in TXM0008)", 0xee8, 8),
           ("revive", "DTMF revive code", 0xef0, 8), ("up", "DTMF beginning code", 0xef8, 16),
           ("down", "DTMF end code", 0xf08, 16)]


@directory.register
class UVK5FagciTXM0008(chirp_common.CloneModeRadio):
    VENDOR = "Quansheng"
    MODEL = "UV-K5 FAGCI TXM0008"
    BAUD_RATE = 38400
    NEEDS_COMPAT_SERIAL = False
    _memsize = MEM_SIZE

    @classmethod
    def get_prompts(cls):
        prompts = chirp_common.RadioPrompts()
        prompts.experimental = "Experimental TXM0008 driver. First download and save a new image with THIS driver. Do not upload images created with the IJV driver."
        prompts.pre_download = "Use normal radio mode, not Spectrum. Turn the radio on and connect the programming cable firmly. This driver accepts OSFW-TXM0008 only."
        prompts.pre_upload = "Use an image downloaded with this TXM0008 driver. Only edited bytes are merged into the radio; calibration, AES keys and password are not uploaded."
        return prompts

    def get_features(self):
        rf = chirp_common.RadioFeatures()
        rf.has_bank = False
        rf.has_settings = True
        rf.has_rx_dtcs = True
        rf.has_ctone = True
        rf.has_cross = True
        rf.has_nostep_tuning = True
        rf.valid_name_length = 10
        rf.valid_characters = "".join(chr(n) for n in range(32, 127))
        rf.memory_bounds = (1, 200)
        rf.valid_modes = ["FM", "NFM", "AM", "NAM", "USB"]
        rf.valid_tuning_steps = STEPS
        # CHIRP validates upper bounds as exclusive; firmware uses inclusive.
        rf.valid_bands = [(low, high + 1) for low, high in BANDS]
        rf.valid_power_levels = POWER
        rf.valid_dtcs_codes = DTCS
        rf.valid_tones = TONES
        rf.valid_tmodes = ["", "Tone", "TSQL", "DTCS", "Cross"]
        rf.valid_cross_modes = ["Tone->Tone", "Tone->DTCS", "DTCS->Tone", "->Tone", "->DTCS", "DTCS->", "DTCS->DTCS"]
        rf.valid_duplexes = ["", "+", "-", "off"]
        rf.valid_skips = ["", "S"]
        return rf

    def process_mmap(self):
        if len(self._mmap.get_packed()) != MEM_SIZE:
            raise errors.RadioError("TXM0008 requires an 8192-byte EEPROM image")

    def sync_in(self):
        version = _hello(self.pipe)
        status = chirp_common.Status()
        status.msg, status.max = "Reading TXM0008 EEPROM", MEM_SIZE
        data = bytearray()
        for address in range(0, MEM_SIZE, BLOCK):
            data.extend(_read_block(self.pipe, address, BLOCK))
            status.cur = len(data)
            self.status_fn(status)
        self._mmap = memmap.MemoryMapBytes(bytes(data))
        self._metadata["txp_firmware"] = version
        self._metadata["txp_baseline"] = base64.b64encode(data).decode("ascii")
        self.process_mmap()

    def sync_out(self):
        # Preflight EVERY conflict before the first write. Merge only edited
        # bytes into fresh 8-byte blocks, preserving newer radio-side changes.
        if self._metadata.get("txp_firmware") != FIRMWARE:
            raise errors.RadioError("Download a NEW image using the TXM0008 driver first")
        try:
            baseline = base64.b64decode(self._metadata["txp_baseline"], validate=True)
        except Exception:
            raise errors.RadioError("Image has no valid TXM0008 baseline; download again")
        desired = self._mmap.get_packed()
        if len(baseline) != MEM_SIZE or len(desired) != MEM_SIZE:
            raise errors.RadioError("Invalid TXM0008 image size")
        dirty = [i for i in range(MEM_SIZE) if desired[i] != baseline[i]]
        for address in dirty:
            if address >= 0x1d00 or 0xf30 <= address < 0xf40 or 0xe98 <= address < 0xea0:
                raise errors.RadioError("Protected EEPROM modification at 0x%04X rejected" % address)
        _hello(self.pipe)
        blocks = sorted(set(address & ~7 for address in dirty))
        status = chirp_common.Status()
        status.msg, status.max = "Checking edited blocks", max(1, len(blocks))
        pending = []
        for index, address in enumerate(blocks):
            current = _read_block(self.pipe, address, 8)
            merged = bytearray(current)
            for offset in range(8):
                pos = address + offset
                if desired[pos] != baseline[pos]:
                    if current[offset] not in (baseline[pos], desired[pos]):
                        raise errors.RadioError("Radio data changed at 0x%04X. Download again before editing." % pos)
                    merged[offset] = desired[pos]
            if merged != current:
                pending.append((address, bytes(merged)))
            status.cur = index + 1
            self.status_fn(status)
        status.msg, status.max = "Writing and verifying edited blocks", max(1, len(pending))
        for index, (address, merged) in enumerate(pending):
            _write_block(self.pipe, address, merged)
            if _read_block(self.pipe, address, 8) != merged:
                raise errors.RadioError("Write verification failed at 0x%04X. Download again." % address)
            status.cur = index + 1
            self.status_fn(status)
        self._metadata["txp_baseline"] = base64.b64encode(desired).decode("ascii")
        if pending:
            _exchange(self.pipe, b"\xdd\x05\x00\x00", response=False)

    def get_raw_memory(self, number):
        index = self._index(number)
        data = self._mmap.get_packed()
        return "channel=%s attr=%02x name/profile=%s" % (
            data[index*16:index*16+16].hex(), data[0xd60+index], data[0xf50+index*16:0xf60+index*16].hex())

    @staticmethod
    def _index(number):
        if not isinstance(number, int) or not 1 <= number <= 200:
            raise errors.InvalidMemoryLocation("Memory must be 1..200")
        return number - 1

    def get_memory(self, number):
        index = self._index(number)
        data = self._mmap.get_packed()
        channel = data[index*16:index*16+16]
        attr = data[0xd60+index]
        name = data[0xf50+index*16:0xf60+index*16]
        memory = chirp_common.Memory()
        memory.number = number
        freq, offset = struct.unpack_from("<II", channel)
        memory.empty = freq in (0, 0xffffffff) or (attr & 15) > 6
        memory.freq = 0 if memory.empty else freq*10
        memory.name = "" if memory.empty else _text(name[:10])
        memory.offset = 0 if memory.empty else offset*10
        shift = channel[11] & 15
        memory.duplex = {1: "+", 2: "-"}.get(shift, "") if offset else ""
        tx_inhibit = not memory.empty and channel[15] & 0xf0 == 0xa0
        if tx_inhibit:
            memory.duplex = "off"
        modulation = channel[11] >> 4 & 7
        modulation = modulation if modulation < 5 and not memory.empty else 0
        narrow = bool(channel[12] & 2) if not memory.empty else False
        memory.mode = ("NFM" if narrow else "FM") if modulation in (0, 3, 4) else (("NAM" if narrow else "AM") if modulation == 1 else "USB")
        memory.tuning_step = STEPS[channel[14]] if channel[14] < len(STEPS) and not memory.empty else 12.5
        power = channel[12] >> 2 & 3
        memory.power = POWER[power if power < 3 and not memory.empty else 0]
        scan = attr >> 6 if not memory.empty else 3
        memory.skip = "" if scan else "S"
        if not memory.empty and modulation == 0:
            chirp_common.split_tone_decode(memory, _tone_decode(channel[10] >> 4, channel[9]), _tone_decode(channel[10] & 15, channel[8]))
        extra = RadioSettingGroup("extra", "Channel parameters")
        extra.append(RadioSetting("txenabled", "TX enabled (subject to global limits)",
                                  RadioSettingValueBoolean(not tx_inhibit)))
        extra.append(_list("demod", "Special demodulator (BYP/RAW use FM column)", ["Use Mode column", "BYP", "RAW"], modulation-2 if modulation in (3,4) else 0))
        extra.append(_list("bandwidth", "Filter bandwidth", ["WIDE", "NARROW"], int(narrow)))
        for key, label, value in [("bcl", "Busy-channel lock", channel[12] & 16),
                                  ("reverse", "Reverse RX/TX", channel[12] & 1),
                                  ("dtmfdecode", "DTMF decode", channel[13] & 1)]:
            extra.append(RadioSetting(key, label, RadioSettingValueBoolean(bool(value) if not memory.empty else False)))
        extra.append(_list("pttid", "DTMF PTT ID", ["OFF", "BOT", "EOT", "BOTH"], channel[13] >> 1 & 3 if not memory.empty else 0))
        scramble = channel[15] & 15 if tx_inhibit else channel[15]
        extra.append(_integer("scramble", "Scrambling", 0, 10, scramble if not memory.empty else 0))
        extra.append(_list("scanlists", "Scan lists", ["Neither", "List 2", "List 1", "Both"], scan))
        gain, rxif, marker = struct.unpack_from("<HHH", name, 10)
        manual = not memory.empty and marker == 0x5852 and gain <= 0x3ff
        if not manual:
            gain, rxif = 0x3be, (0 if modulation == 2 else 0x2aab)
        extra.append(_list("rxmode", "RX profile (MANUAL fixes gain; disables AM-fix)", ["AUTO", "MANUAL"], int(manual)))
        for key, label, high, value in [("lnas", "RX LNAs level", 3, gain >> 8 & 3),
                                       ("lna", "RX LNA level", 7, gain >> 5 & 7),
                                       ("mix", "RX MIX level", 3, gain >> 3 & 3),
                                       ("pga", "RX PGA level", 7, gain & 7),
                                       ("rxif", "RX IF register (decimal)", 65535, rxif)]:
            extra.append(_integer(key, label, 0, high, value))
        memory.extra = extra
        return memory

    def set_memory(self, memory):
        index = self._index(memory.number)
        old = self.get_memory(memory.number)
        if memory.empty and old.empty:
            return
        data = bytearray(self._mmap.get_packed())
        start, attrpos, namepos = index*16, 0xd60+index, 0xf50+index*16
        if memory.empty:
            data[start:start+16] = b"\xff"*16
            data[attrpos] = 0xff
            data[namepos:namepos+10] = b"\0"*10
            data[namepos+14:namepos+16] = b"\xff\xff"
            self._mmap = memmap.MemoryMapBytes(bytes(data))
            return
        if memory.freq % 10:
            raise errors.InvalidValueError("TXM0008 frequency resolution is 10 Hz")
        band = _band(memory.freq)
        extra, oldextra = _extras(memory), _extras(old)
        def changed(key):
            return key in extra and (old.empty or str(extra[key]) != str(oldextra[key]))
        if old.empty:
            data[start:start+16] = bytes(16)
            data[start+14] = 9
            data[attrpos] = 0xc0 | band
            data[namepos:namepos+10] = b"\0"*10
            data[namepos+14:namepos+16] = b"\xff\xff"
        if old.empty or memory.freq != old.freq:
            struct.pack_into("<I", data, start, memory.freq//10)
            data[attrpos] = data[attrpos] & 0xf0 | band
        if old.empty or memory.name != old.name:
            if len(memory.name) > 10 or any(not 32 <= ord(c) <= 126 for c in memory.name):
                raise errors.InvalidValueError("Names allow ten printable ASCII characters")
            data[namepos:namepos+10] = memory.name.encode("ascii").ljust(10, b"\0")
        if (old.empty or (memory.duplex, memory.offset) != (old.duplex, old.offset)) and memory.duplex != "off":
            offset = memory.offset
            if offset < 0 or offset % 10 or memory.duplex not in ("", "+", "-", "off"):
                raise errors.InvalidValueError("Invalid duplex or offset")
            struct.pack_into("<I", data, start+4, offset//10)
            shift = 2 if memory.duplex == "-" else (1 if memory.duplex == "+" else 0)
            data[start+11] = data[start+11] & 0xf0 | shift
        if old.empty or memory.tuning_step != old.tuning_step:
            if memory.tuning_step not in STEPS:
                raise errors.InvalidValueError("Unsupported TXM0008 tuning step")
            data[start+14] = STEPS.index(memory.tuning_step)
        if old.empty or memory.power != old.power:
            if memory.power not in POWER:
                raise errors.InvalidValueError("Choose Low, Mid or High power")
            data[start+12] = data[start+12] & ~12 | POWER.index(memory.power) << 2
        if old.empty or memory.mode != old.mode or changed("demod"):
            modulation = {"FM":0, "NFM":0, "AM":1, "NAM":1, "USB":2}.get(memory.mode)
            if modulation is None:
                raise errors.InvalidValueError("Unsupported mode")
            if changed("demod") and int(extra["demod"]):
                modulation = int(extra["demod"]) + 2
            data[start+11] = data[start+11] & 0x8f | modulation << 4
        if old.empty or memory.mode != old.mode or changed("bandwidth"):
            narrow = memory.mode in ("NFM", "NAM")
            if changed("bandwidth") and (not old.empty or str(extra["bandwidth"]) != str(oldextra["bandwidth"])):
                narrow = bool(int(extra["bandwidth"]))
            data[start+12] = data[start+12] & ~2 | int(narrow) << 1
        if (old.empty or memory.mode != old.mode or changed("demod") or
                chirp_common.split_tone_encode(memory) != chirp_common.split_tone_encode(old)):
            tx, rx = chirp_common.split_tone_encode(memory)
            txkind, txcode = _tone_encode(tx)
            rxkind, rxcode = _tone_encode(rx)
            data[start+8:start+11] = bytes([rxcode, txcode, txkind << 4 | rxkind])
        for key, pos, mask, shift in [("bcl",12,16,4),("reverse",12,1,0),("dtmfdecode",13,1,0),("pttid",13,6,1)]:
            if changed(key):
                data[start+pos] = data[start+pos] & ~mask | (int(extra[key]) << shift) & mask
        tx_changed = changed("txenabled") or memory.duplex != old.duplex
        if old.empty or tx_changed or changed("scramble"):
            inhibit = old.duplex == "off"
            if old.empty or memory.duplex != old.duplex:
                inhibit = memory.duplex == "off"
            if changed("txenabled"):
                inhibit = not bool(int(extra["txenabled"]))
            scramble = int(extra.get("scramble", oldextra["scramble"]))
            data[start+15] = scramble | (0xa0 if inhibit else 0)
        if old.empty or memory.skip != old.skip or changed("scanlists"):
            scan = int(extra["scanlists"]) if "scanlists" in extra else 3
            if memory.skip != old.skip:
                scan = 0 if memory.skip == "S" else (scan or 3)
            data[attrpos] = data[attrpos] & 0x3f | scan << 6
        profile_changed = any(changed(k) for k in ("rxmode","lnas","lna","mix","pga","rxif"))
        if profile_changed:
            if (not int(extra.get("rxmode", 0)) and not int(oldextra["rxmode"]) and
                    any(k in extra and str(extra[k]) != str(oldextra[k]) for k in ("lnas","lna","mix","pga","rxif"))):
                raise errors.InvalidValueError("Select RX profile MANUAL before editing gain/IF")
            if int(extra.get("rxmode", 0)):
                gain = int(extra["lnas"]) << 8 | int(extra["lna"]) << 5 | int(extra["mix"]) << 3 | int(extra["pga"])
                struct.pack_into("<HHH", data, namepos+10, gain, int(extra["rxif"]), 0x5852)
            elif data[namepos+14:namepos+16] == b"RX":
                data[namepos+14:namepos+16] = b"\xff\xff"
        self._mmap = memmap.MemoryMapBytes(bytes(data))

    def validate_memory(self, memory):
        result = super().validate_memory(memory)
        demod = int(_extras(memory).get("demod", 0))
        if not memory.empty and (memory.mode not in ("FM", "NFM") or demod) and memory.tmode:
            result.append(chirp_common.ValidationError("TXM0008 uses CTCSS/DCS only in FM"))
        return result

    def get_settings(self):
        data = self._mmap.get_packed()
        basic = RadioSettingGroup("basic", "Radio / scan / keys")
        strings = RadioSettingGroup("codes", "Messages and DTMF")
        fm = RadioSettingGroup("fm", "FM broadcast presets")
        contacts = RadioSettingGroup("contacts", "DTMF contacts")
        for key, label, address, values, offset in SETTINGS:
            if isinstance(values, list):
                basic.append(_list(key, label, values, data[address]))
            else:
                basic.append(_integer(key, label, values[0], values[1], data[address]+offset))
        for key, address in [("list1ch1",0xf1a),("list1ch2",0xf1b),("list2ch1",0xf1d),("list2ch2",0xf1e)]:
            basic.append(_list(key, key + " priority channel", ["None"]+["CH-%03d" % n for n in range(1,201)], data[address]+1 if data[address]<200 else 0))
        for key, label, address, size in STRINGS:
            strings.append(RadioSetting(key, label, RadioSettingValueString(0,size,_text(data[address:address+size]),autopad=False)))
        for key, label, address in [("separate","DTMF separator",0xed1),("group","DTMF group code",0xed2)]:
            strings.append(_list(key,label,list("0123456789ABCD*#"), "0123456789ABCD*#".find(chr(data[address])) if chr(data[address]) in "0123456789ABCD*#" else 14))
        for index in range(20):
            value = struct.unpack_from("<H",data,0xe40+index*2)[0]
            current = "%.1f" % (value/10) if 760<=value<=1080 else ""
            fm.append(RadioSetting("fm%d" % index,"FM preset %d (MHz; blank=empty)" % (index+1),RadioSettingValueString(0,5,current,autopad=False)))
        for index in range(16):
            address=0x1c00+index*16
            contacts.append(RadioSetting("contact%dname" % index,"Contact %d name" % (index+1),RadioSettingValueString(0,8,_text(data[address:address+8]),autopad=False)))
            contacts.append(RadioSetting("contact%dcode" % index,"Contact %d DTMF ID" % (index+1),RadioSettingValueString(0,3,_text(data[address+8:address+11]),autopad=False)))
        return RadioSettings(basic,strings,fm,contacts)

    def set_settings(self, settings):
        data = bytearray(self._mmap.get_packed())
        specs = {row[0]: row for row in SETTINGS}
        texts = {row[0]: row for row in STRINGS}
        def apply(group):
            for setting in group:
                if not isinstance(setting, RadioSetting):
                    apply(setting)
                    continue
                if not setting.changed():
                    continue
                key = setting.get_name()
                value = setting.value
                if key in specs:
                    _,_,address,_,offset=specs[key]
                    data[address]=int(value)-offset
                elif key in texts:
                    _,_,address,size=texts[key]
                    text=str(value)
                    if key not in ("logo1","logo2") and any(c not in "0123456789ABCD*#" for c in text):
                        raise errors.InvalidValueError("DTMF codes allow 0-9 A-D * #")
                    data[address:address+size]=text.encode("ascii").ljust(size,b"\0")
                elif key in ("list1ch1","list1ch2","list2ch1","list2ch2"):
                    data[{"list1ch1":0xf1a,"list1ch2":0xf1b,"list2ch1":0xf1d,"list2ch2":0xf1e}[key]]=(int(value)-1)&255
                elif key in ("separate","group"):
                    data[0xed1 if key=="separate" else 0xed2]=ord(str(value))
                elif key.startswith("fm"):
                    number=int(key[2:]);text=str(value).strip()
                    freq=chirp_common.parse_freq(text) if text else 0
                    if text and (not 76000000<=freq<=108000000 or freq%100000):
                        raise errors.InvalidValueError("FM presets require 76.0..108.0 MHz in 0.1 MHz steps")
                    struct.pack_into("<H",data,0xe40+number*2,freq//100000 if text else 0xffff)
                elif key.startswith("contact"):
                    number=int(key[7:].split("name")[0].split("code")[0])
                    isname=key.endswith("name");size=8 if isname else 3
                    address=0x1c00+number*16+(0 if isname else 8)
                    text=str(value)
                    if not isname and text and (len(text)!=3 or any(c not in "0123456789ABCD*#" for c in text)):
                        raise errors.InvalidValueError("Contact ID must contain three DTMF characters")
                    data[address:address+size]=text.encode("ascii").ljust(size,b"\0")
                else:
                    raise errors.InvalidValueError("Unknown TXM0008 setting: %s" % key)
        apply(settings)
        self._mmap = memmap.MemoryMapBytes(bytes(data))
