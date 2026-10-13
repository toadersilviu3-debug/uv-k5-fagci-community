# SPDX-License-Identifier: Apache-2.0
# Added for the independent SPC0002 community fork, 2026-10-13.
"""Exercise the compiled ARM firmware; mock only EEPROM I/O and LCD transfer.

Build firmware with make first. Run using Python with unicorn installed.
The generated layout uses the same short-enum ABI as the firmware.
"""
import binascii
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
    UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
)

ROOT = Path(__file__).resolve().parents[1]
BIN = Path(os.environ.get('ARM_BIN', r'C:\msys64\ucrt64\bin'))
os.environ['PATH'] = str(BIN) + os.pathsep + os.environ['PATH']


def tool(name, *args):
    return subprocess.check_output([str(BIN / (name + '.exe')), *map(str, args)])


SYMS = {}
for line in tool('arm-none-eabi-nm', '-n', ROOT / 'firmware').decode().splitlines():
    parts = line.split()
    if len(parts) == 3:
        SYMS[parts[2]] = int(parts[0], 16)

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder)
    (path / 'layout.c').write_text('''
#include <stddef.h>
#include "settings.h"
#include "ui/menu.h"
const unsigned int layout[] = {
    offsetof(EEPROM_Config_t, VfoInfo), sizeof(VFO_Info_t),
    offsetof(VFO_Info_t, CHANNEL_SAVE), offsetof(VFO_Info_t, Name),
    MENU_NAME, MENU_350TX, MENU_COUNT, MENU_RESET, MENU_SCREN
};
''')
    tool('arm-none-eabi-gcc', '-mcpu=cortex-m0', '-fshort-enums', '-I', ROOT,
         '-c', path / 'layout.c', '-o', path / 'layout.o')
    tool('arm-none-eabi-objcopy', '-O', 'binary', '-j', '.rodata',
         path / 'layout.o', path / 'layout.bin')
    VFO_OFFSET, VFO_SIZE, CHANNEL_OFFSET, NAME_OFFSET, NAME_MENU, NORMAL_COUNT, \
        FULL_COUNT, RESET_MENU, SCREN_MENU = struct.unpack('<9I', (path / 'layout.bin').read_bytes())

KEY_MENU, KEY_UP, KEY_DOWN, KEY_EXIT, KEY_STAR, KEY_F, KEY_PTT = 10, 11, 12, 13, 14, 15, 21


class Radio:
    def __init__(self, eeprom=None, channel=37, active_vfo=1):
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.uc.mem_map(0, 0x20000)
        self.uc.mem_map(0x20000000, 0x10000)
        self.uc.mem_map(0x40000000, 0x100000)
        firmware = (ROOT / 'firmware.bin').read_bytes()
        self.uc.mem_write(0, firmware)
        start, end = SYMS['sram_data_start'], SYMS['sram_data_end']
        self.uc.mem_write(start, firmware[SYMS['flash_data_start']:SYMS['flash_data_start'] + end - start])
        self.eeprom = bytearray(eeprom if eeprom is not None else bytes((i * 17 + 3) % 256 for i in range(8192)))
        self.writes = []
        self.uc.hook_add(UC_HOOK_CODE, self.io, begin=SYMS['EEPROM_ReadBuffer'], end=SYMS['EEPROM_ReadBuffer'])
        self.uc.hook_add(UC_HOOK_CODE, self.io, begin=SYMS['EEPROM_WriteBuffer'], end=SYMS['EEPROM_WriteBuffer'])
        self.uc.hook_add(UC_HOOK_CODE, self.io, begin=SYMS['ST7565_BlitFullScreen'], end=SYMS['ST7565_BlitFullScreen'])
        self.uc.mem_write(SYMS['gMR_ChannelAttributes'], bytes([0] * 200))
        self.set8('gMenuCursor', NAME_MENU)
        self.set8('gMenuListCount', NORMAL_COUNT)
        self.set8('gScreenToDisplay', 2)
        self.set8('gRequestDisplayScreen', 255)
        for vfo in range(2):
            self.uc.mem_write(self.vfo(vfo) + CHANNEL_OFFSET, bytes([channel]))
        self.uc.mem_write(SYMS['gTxVfo'], struct.pack('<I', self.vfo(active_vfo)))

    def vfo(self, index):
        return SYMS['gEeprom'] + VFO_OFFSET + index * VFO_SIZE

    def set8(self, name, value):
        self.uc.mem_write(SYMS[name], bytes([value]))

    def get8(self, name):
        return self.uc.mem_read(SYMS[name], 1)[0]

    def io(self, uc, address, size, data):
        r0, r1, r2 = [uc.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2)]
        if address == SYMS['EEPROM_ReadBuffer']:
            assert 0 <= r0 <= 8192 - r2
            uc.mem_write(r1, bytes(self.eeprom[r0:r0 + r2]))
        elif address == SYMS['EEPROM_WriteBuffer']:
            assert r0 % 8 == 0 and 0 <= r0 <= 8192 - 8
            payload = bytes(uc.mem_read(r1, 8))
            self.eeprom[r0:r0 + 8] = payload
            self.writes.append((r0, payload))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def call(self, name, *args):
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args):
            self.uc.reg_write(reg, value)
        self.uc.reg_write(UC_ARM_REG_SP, 0x2000D000)
        self.uc.reg_write(UC_ARM_REG_LR, 0x10001)
        self.uc.emu_start(SYMS[name] | 1, 0x10000, count=300000)
        if self.uc.reg_read(UC_ARM_REG_PC) != 0x10000:
            raise AssertionError(f'{name} did not return')
        return self.uc.reg_read(UC_ARM_REG_R0)

    def text(self):
        return bytes(self.uc.mem_read(SYMS['gMenuChannelName'], 11))

    def load(self, channel=37, name=b'ORIGINAL'):
        self.eeprom[0xF50 + channel * 16:0xF50 + channel * 16 + 10] = name.ljust(10, b'\0')
        self.call('MENU_ShowCurrentSetting')

    def key(self, key, pressed=1, held=0):
        self.call('MENU_ProcessKeys', key, pressed, held)

    def finish(self):
        # Same deferred acceptance and refresh sequence as APP_ProcessKey.
        if self.get8('gFlagAcceptSetting'):
            self.call('MENU_AcceptSetting')
            self.set8('gFlagAcceptSetting', 0)
            self.set8('gFlagRefreshSetting', 1)
        if self.get8('gFlagRefreshSetting'):
            self.call('MENU_ShowCurrentSetting')
            self.set8('gFlagRefreshSetting', 0)


class ChannelNameTests(unittest.TestCase):
    def test_all_200_slots_preserve_every_other_eeprom_byte(self):
        radio = Radio()
        ptr = 0x2000E000
        radio.uc.mem_write(ptr, b'ABCDEFGHIJ\0')
        for channel in range(200):
            with self.subTest(channel=channel + 1):
                before = bytes(radio.eeprom)
                radio.writes.clear()
                self.assertEqual(radio.call('SETTINGS_SaveChannelName', channel, ptr), 1)
                address = 0xF50 + 16 * channel
                expected = bytearray(before)
                expected[address:address + 10] = b'ABCDEFGHIJ'
                self.assertEqual(radio.eeprom, expected)
                self.assertEqual([w[0] for w in radio.writes], [address, address + 8])

    def test_invalid_or_empty_channels_never_write(self):
        radio = Radio()
        ptr = 0x2000E000
        radio.uc.mem_write(ptr, b'ABCDEFGHIJ\0')
        before = bytes(radio.eeprom)
        for channel in (200, 206, 207, 255):
            self.assertEqual(radio.call('SETTINGS_SaveChannelName', channel, ptr), 0)
        radio.uc.mem_write(SYMS['gMR_ChannelAttributes'] + 37, b'\xff')
        self.assertEqual(radio.call('SETTINGS_SaveChannelName', 37, ptr), 0)
        self.assertEqual(radio.writes, [])
        self.assertEqual(radio.eeprom, before)

    def test_cancel_displays_original_and_writes_nothing(self):
        radio = Radio()
        radio.load()
        before = bytes(radio.eeprom)
        self.assertEqual(radio.text(), b'ORIGINAL  \0')
        radio.key(KEY_MENU)
        radio.key(KEY_UP)
        self.assertEqual(radio.text()[0], ord('P'))
        radio.key(KEY_EXIT)
        radio.finish()
        self.assertEqual(radio.text(), b'ORIGINAL  \0')
        self.assertEqual(radio.eeprom, before)
        self.assertFalse(radio.writes)

    def test_save_reload_after_restart_and_both_vfo_caches(self):
        radio = Radio(active_vfo=1)
        radio.load(name=b'ABCDEFGHIJ')
        radio.key(KEY_MENU)
        radio.key(9)  # replace first character with 9 and advance
        radio.key(KEY_MENU)
        self.assertEqual(radio.writes, [])
        radio.finish()
        for vfo in (0, 1):
            self.assertEqual(bytes(radio.uc.mem_read(radio.vfo(vfo) + NAME_OFFSET, 16)), b'9BCDEFGHIJ' + b'\0' * 6)
        restarted = Radio(radio.eeprom)
        restarted.call('MENU_ShowCurrentSetting')
        self.assertEqual(restarted.text(), b'9BCDEFGHIJ\0')

    def test_cursor_character_wrap_digits_and_repeat_events(self):
        radio = Radio()
        radio.load(name=b'~123456789')
        radio.key(KEY_MENU)
        radio.key(KEY_UP)
        self.assertEqual(radio.text()[0], 32)
        radio.key(KEY_DOWN, held=1)
        self.assertEqual(radio.text()[0], 126)
        radio.key(KEY_STAR)
        self.assertEqual(radio.get8('gMenuNamePosition'), 9)
        radio.key(KEY_F)
        self.assertEqual(radio.get8('gMenuNamePosition'), 0)
        radio.key(5, pressed=0)
        radio.key(5, held=1)
        self.assertEqual(radio.text()[0], 126)
        radio.key(5)
        self.assertEqual(radio.text(), b'5123456789\0')
        self.assertEqual(radio.get8('gMenuNamePosition'), 1)
        radio.key(KEY_MENU, held=1)
        self.assertEqual(radio.get8('gFlagAcceptSetting'), 0)
        self.assertFalse(radio.writes)

    def test_unchanged_name_avoids_eeprom_wear(self):
        radio = Radio()
        radio.load(name=b'TEST')
        radio.key(KEY_MENU)
        radio.key(KEY_MENU)
        radio.finish()
        self.assertEqual(radio.writes, [])

    def test_shortening_and_clearing_name(self):
        radio = Radio()
        radio.load(name=b'ABCDEFGHIJ')
        ptr = 0x2000E000
        for name, expected in ((b'A B       ', b'A B' + b'\0' * 7), (b'          ', b'\0' * 10)):
            radio.uc.mem_write(ptr, name + b'\0')
            radio.call('SETTINGS_SaveChannelName', 37, ptr)
            self.assertEqual(radio.eeprom[0xF50 + 37 * 16:0xF50 + 37 * 16 + 10], expected)

    def test_vfo_and_empty_channel_cannot_enter_editor(self):
        for channel in (200, 206, 255, 37):
            radio = Radio(channel=channel)
            if channel == 37:
                radio.uc.mem_write(SYMS['gMR_ChannelAttributes'] + 37, b'\xff')
            radio.call('MENU_ShowCurrentSetting')
            radio.key(KEY_MENU)
            self.assertEqual(radio.get8('gMenuNameChannel'), 255)
            self.assertEqual(radio.get8('gIsInSubMenu'), 0)
            self.assertFalse(radio.writes)

    def test_ptt_and_timeout_discard_draft(self):
        for escape in ('ptt', 'timeout'):
            radio = Radio()
            radio.load()
            before = bytes(radio.eeprom)
            radio.key(KEY_MENU)
            radio.key(9)
            if escape == 'ptt':
                radio.key(KEY_PTT)
            radio.call('GUI_SelectNextDisplay', 0)
            radio.call('GUI_SelectNextDisplay', 2)
            radio.key(KEY_MENU)
            self.assertEqual(radio.text(), b'ORIGINAL  \0')
            self.assertEqual(radio.eeprom, before)
            self.assertFalse(radio.writes)

    def test_channel_target_remains_pinned_while_editing(self):
        radio = Radio(active_vfo=1)
        radio.load()
        radio.key(KEY_MENU)
        radio.key(9)
        radio.uc.mem_write(radio.vfo(0) + CHANNEL_OFFSET, b'\x05')
        radio.uc.mem_write(SYMS['gTxVfo'], struct.pack('<I', radio.vfo(0)))
        before = bytes(radio.eeprom)
        radio.key(KEY_MENU)
        radio.finish()
        address = 0xF50 + 37 * 16
        expected = bytearray(before)
        expected[address:address + 10] = b'9RIGINAL\0\0'
        self.assertEqual(radio.eeprom, expected)

    def test_ten_characters_and_last_cursor_fit_display(self):
        radio = Radio()
        radio.load(name=b'ABCDEFGHIJ')
        radio.key(KEY_MENU)
        radio.key(KEY_STAR)
        radio.call('UI_DisplayMenu')
        frame = bytes(radio.uc.mem_read(SYMS['gFrameBuffer'], 7 * 128))
        for index, char in enumerate(b'ABCDEFGHIJ'):
            glyph = bytes(radio.uc.mem_read(SYMS['gFontSmall'] + (char - 32) * 6, 6))
            start = 2 * 128 + 58 + index * 7
            self.assertEqual(frame[start:start + 6], glyph)
        self.assertEqual(frame[3 * 128 + 121:3 * 128 + 127], b'\x80' * 6)
        self.assertEqual(frame[3 * 128 + 127], 0)

    def test_previous_normal_menu_numbers_preserved(self):
        self.assertEqual((RESET_MENU, NAME_MENU, NORMAL_COUNT, FULL_COUNT), (48, 49, 50, 56))
        self.assertEqual(SCREN_MENU + 1, FULL_COUNT)

    def test_packed_firmware_payload_and_crc(self):
        plain = (ROOT / 'firmware.bin').read_bytes()
        packed = (ROOT / 'firmware.packed.bin').read_bytes()
        self.assertLessEqual(len(plain), 60 * 1024)
        self.assertEqual(len(packed), len(plain) + 18)
        self.assertEqual(binascii.crc_hqx(packed[:-2], 0), int.from_bytes(packed[-2:], 'little'))
        # XOR key is periodic; recover from matching prefix then decode payload.
        key = bytes(a ^ b for a, b in zip(plain[:128], packed[:128]))
        decoded = bytes(value ^ key[i % 128] for i, value in enumerate(packed[:-2]))
        self.assertEqual(decoded[:0x2000] + decoded[0x2010:], plain)
        self.assertEqual(decoded[0x2000:0x2010], b'*OSFW-SPC0002'.ljust(16, b'\0'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
