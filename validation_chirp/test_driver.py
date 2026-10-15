import base64
import binascii
import importlib.util
import os
import struct
import tempfile
import unittest
from pathlib import Path
from chirp import chirp_common,memmap,errors

ROOT=Path(__file__).resolve().parents[2]
DRIVER=Path(os.environ.get('UVK5_DRIVER',ROOT/'outputs/uvk5_fagci_txm0008.py'))
spec=importlib.util.spec_from_file_location('uvk5_fagci_txm0008',DRIVER)
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)


def image(slot=0,mode=1,step=9,narrow=0,manual=True):
    raw=bytearray(b'\xff'*8192)
    raw[0xe40:0xf50]=b'\0'*0x110
    raw[0xeb0:0xed0]=b'\0'*32
    raw[slot*16:slot*16+16]=struct.pack('<II8B',11995000,60000,12,5,0x13,mode<<4|2,
        0x98|narrow<<1,0x87,step,7)
    raw[0xd60+slot]=0xf1 # band nibble 1, both scan lists, reserved bits retained
    raw[0xf50+16*slot:0xf60+16*slot]=b'AEROPORT\0\0'+struct.pack('<HHH',0x3a5,0x2345,0x5852 if manual else 0xffff)
    return bytes(raw)


def radio(raw=None,downloaded=True):
    raw=raw or image()
    r=d.UVK5FagciTXM0008(memmap.MemoryMapBytes(raw))
    r.status_fn=lambda s:None
    if downloaded:
        r._metadata['txp_firmware']=d.FIRMWARE
        r._metadata['txp_baseline']=base64.b64encode(raw).decode()
    return r


def extra(m,key):return m.extra[key]


def setting(group,key):
    for s in group:
        if isinstance(s,d.RadioSetting):
            if s.get_name()==key:return s
        else:
            found=setting(s,key)
            if found:return found


class FakeSerial:
    """Model firmware UART framing, EEPROM replies and byte writes, not RF."""
    def __init__(self,raw=None,firmware=d.FIRMWARE,fragment=False):
        self.raw=bytearray(raw or image());self.version=firmware;self.fragment=fragment
        self.buffer=b'';self.commands=[];self.writes=[];self.reset=False
        self.bad_ack=False;self.ignore_write=False;self.bad_read=False;self.drop_hellos=0;self.aes_locked=False

    def reply(self,body):
        self.buffer+=b'\xab\xcd'+bytes([len(body),0])+d._xor(body)+b'\0\0\xdc\xba'

    def write(self,packet):
        assert packet[:2]==b'\xab\xcd' and packet[-2:]==b'\xdc\xba'
        payload=d._xor(packet[4:-2]);assert struct.unpack('<H',payload[-2:])[0]==binascii.crc_hqx(payload[:-2],0)
        payload=payload[:-2];code,length=struct.unpack_from('<HH',payload)
        assert len(payload)==length+4
        self.commands.append(code)
        if code==0x514:
            if self.drop_hellos:self.drop_hellos-=1
            else:self.reply(struct.pack('<HH',0x515,36)+self.version.encode().ljust(16,b'\0')+bytes([int(self.aes_locked)])+bytes(19))
        elif code==0x51b:
            address,size,_=struct.unpack_from('<HBB',payload,4)
            self.reply(struct.pack('<HHHBB',0x51c,size+4,address+(8 if self.bad_read else 0),size,0)+self.raw[address:address+size])
        elif code==0x51d:
            address,size,allow=struct.unpack_from('<HBB',payload,4)
            assert size==8 and address%8==0 and allow==0
            self.writes.append((address,payload[12:]))
            if not self.ignore_write:self.raw[address:address+size]=payload[12:]
            self.reply(struct.pack('<HHH',0x51e,2,address+(8 if self.bad_ack else 0)))
        elif code==0x5dd:self.reset=True
        else:raise AssertionError(hex(code))
        return len(packet)

    def read(self,count):
        count=min(count,3) if self.fragment else count
        result,self.buffer=self.buffer[:count],self.buffer[count:]
        return result


class MappingTests(unittest.TestCase):
    def test_band_attribute_uses_full_nibble_like_firmware(self):
        for band in range(16):
            raw=bytearray(image());raw[0xd60]=0xf0|band
            r=radio(bytes(raw));m=r.get_memory(1)
            self.assertEqual(m.empty,band>6)
            r.set_memory(m)
            self.assertEqual(r.get_mmap().get_packed(),raw)

    def test_tx_disable_changes_only_scramble_flag_byte_preserves_offset_profile(self):
        original = image()
        r = radio(original)
        m = r.get_memory(1)
        extra(m,'txenabled').value = False
        r.set_memory(m)
        expected = bytearray(original)
        expected[15] = 0xa7
        self.assertEqual(r.get_mmap().get_packed(), expected)
        m = r.get_memory(1)
        self.assertEqual(m.duplex, 'off')
        self.assertEqual(int(extra(m,'scramble').value), 7)
        extra(m,'txenabled').value = True
        r.set_memory(m)
        self.assertEqual(r.get_mmap().get_packed(), original)
        self.assertEqual(r.get_memory(1).duplex, '-')

    def test_duplex_off_uses_dedicated_flag_and_frequency_edit_keeps_it(self):
        r = radio()
        m = r.get_memory(1)
        old_offset = r.get_mmap().get_packed()[4:8]
        m.duplex = 'off'
        r.set_memory(m)
        self.assertEqual(r.get_mmap().get_packed()[4:8], old_offset)
        m = r.get_memory(1)
        m.freq = 125000000
        extra(m,'scramble').value = 2
        r.set_memory(m)
        self.assertEqual(r.get_memory(1).duplex, 'off')
        self.assertEqual(r.get_mmap().get_packed()[15], 0xa2)
        self.assertEqual(r.get_mmap().get_packed()[4:8], old_offset)

    def test_duplex_reenable_removes_dedicated_flag(self):
        r = radio()
        m = r.get_memory(1)
        m.duplex = 'off'
        r.set_memory(m)
        m = r.get_memory(1)
        m.duplex = '+'
        r.set_memory(m)
        self.assertEqual(r.get_memory(1).duplex, '+')
        self.assertTrue(bool(extra(r.get_memory(1),'txenabled').value))

    def test_tx_disabled_noop_preserves_all_200_memories_and_profile(self):
        for slot in range(200):
            raw = bytearray(image(slot=slot))
            raw[slot*16+15] = 0xaa
            r = radio(bytes(raw))
            m = r.get_memory(slot+1)
            self.assertEqual(m.duplex, 'off')
            r.set_memory(m)
            self.assertEqual(r.get_mmap().get_packed(), raw)

    def test_all_band_endpoints_pass_chirp_validation(self):
        r = radio(image(mode=0))
        for low, high in d.BANDS:
            for freq in (low, high):
                m = r.get_memory(1)
                m.freq, m.duplex, m.offset = freq, '', 0
                self.assertEqual(r.validate_memory(m), [])

    def test_mode_change_to_fm_clears_hidden_am_tones(self):
        r = radio()
        m = r.get_memory(1)
        self.assertEqual(m.tmode, '')
        m.mode = 'FM'
        r.set_memory(m)
        self.assertEqual(r.get_memory(1).tmode, '')
        self.assertEqual(r.get_mmap().get_packed()[8:11], bytes(3))

    def test_usb_auto_to_manual_uses_usb_default_if(self):
        r = radio(image(mode=2, manual=False))
        m = r.get_memory(1)
        self.assertEqual(int(extra(m,'rxif').value), 0)
        extra(m,'rxmode').value = 'MANUAL'
        r.set_memory(m)
        self.assertEqual(struct.unpack_from('<HHH', r.get_mmap().get_packed(), 0xf5a), (0x3be, 0, 0x5852))

    def test_bypass_mode_rejects_ctcss_in_validation(self):
        r = radio(image(mode=3))
        m = r.get_memory(1)
        m.tmode = 'Tone'
        self.assertTrue(any(isinstance(x, chirp_common.ValidationError) for x in r.validate_memory(m)))

    def test_noop_all_200_slots_preserves_entire_eeprom(self):
        for slot in range(200):
            raw=image(slot=slot,mode=slot%5,step=slot%12,narrow=slot%2)
            r=radio(raw);m=r.get_memory(slot+1);r.set_memory(m)
            self.assertEqual(r.get_mmap().get_packed(),raw)

    def test_exact_modes_steps_bandwidth_and_profile(self):
        for mode in range(5):
            for step in range(12):
                for narrow in range(2):
                    r=radio(image(mode=mode,step=step,narrow=narrow));m=r.get_memory(1)
                    self.assertEqual(m.tuning_step,d.STEPS[step])
                    self.assertEqual(m.mode,('NFM' if narrow else 'FM') if mode in (0,3,4) else ('NAM' if narrow else 'AM') if mode==1 else 'USB')
                    self.assertEqual(int(extra(m,'bandwidth').value),narrow)
                    self.assertEqual(int(extra(m,'demod').value),mode-2 if mode>2 else 0)
                    self.assertEqual(str(extra(m,'rxmode').value),'MANUAL')
                    self.assertEqual(tuple(int(extra(m,k).value) for k in ('lnas','lna','mix','pga','rxif')),(3,5,0,5,0x2345))

    def test_aero_shows_am_not_ijv_fm_and_actual_step(self):
        m=radio().get_memory(1)
        self.assertEqual((m.freq,m.name,m.mode,m.tuning_step),(119950000,'AEROPORT','AM',12.5))
        self.assertEqual(m.tmode,'')

    def test_name_edit_changes_only_ten_name_bytes_and_keeps_profile(self):
        raw=image();r=radio(raw);m=r.get_memory(1);m.name='NEW';r.set_memory(m)
        expected=bytearray(raw);expected[0xf50:0xf5a]=b'NEW'+bytes(7)
        self.assertEqual(r.get_mmap().get_packed(),expected)

    def test_frequency_136mhz_uses_fagci_band_two(self):
        r=radio();m=r.get_memory(1);m.freq=136000000;r.set_memory(m)
        self.assertEqual(r.get_mmap()[0xd60][0]&7,2)

    def test_global_settings_noop_preserves_even_unknown_bytes(self):
        for raw in (image(),bytes((i*17+3)%256 for i in range(8192)),b'\xff'*8192):
            r=radio(raw);s=r.get_settings();r.set_settings(s)
            self.assertEqual(r.get_mmap().get_packed(),raw)

    def test_edit_global_settings_changes_only_requested_offsets(self):
        raw=image();r=radio(raw);s=r.get_settings()
        setting(s,'sql').value=4;setting(s,'dw').value='CHAN_B'
        setting(s,'key2').value='Flashlight / SOS';setting(s,'logo1').value='TEST'
        r.set_settings(s);expected=bytearray(raw)
        expected[0xe71]=4;expected[0xe7c]=2;expected[0xe93]=1;expected[0xeb0:0xec0]=b'TEST'+bytes(12)
        self.assertEqual(r.get_mmap().get_packed(),expected)

    def test_dtmf_and_fm_contact_offsets(self):
        raw=image();r=radio(raw);s=r.get_settings()
        setting(s,'up').value='12AB';setting(s,'down').value='34#'
        setting(s,'fm0').value='99.5';setting(s,'contact15name').value='CALL'
        setting(s,'contact15code').value='123';r.set_settings(s)
        expected=bytearray(raw);expected[0xef8:0xf08]=b'12AB'+bytes(12)
        expected[0xf08:0xf18]=b'34#'+bytes(13);struct.pack_into('<H',expected,0xe40,995)
        expected[0x1cf0:0x1cf8]=b'CALL'+bytes(4);expected[0x1cf8:0x1cfb]=b'123'
        self.assertEqual(r.get_mmap().get_packed(),expected)

    def test_tones_dcs_polarities_match_firmware_nibbles(self):
        for kind,values in ((1,d.TONES),(2,d.DTCS),(3,d.DTCS)):
            for index,value in enumerate(values):
                raw=bytearray(image(mode=0));raw[8:11]=bytes([index,index,kind<<4|kind])
                r=radio(bytes(raw));m=r.get_memory(1)
                tone = ('Tone', value, None) if kind == 1 else ('DTCS', value, 'R' if kind == 3 else 'N')
                self.assertEqual(chirp_common.split_tone_encode(m), (tone, tone))
                r.set_memory(m);self.assertEqual(r.get_mmap().get_packed(),raw)

    def test_edit_tones_encodes_rx_and_tx_separately(self):
        r=radio(image(mode=0));m=r.get_memory(1)
        m.tmode='Cross';m.cross_mode='Tone->DTCS';m.rtone=88.5;m.rx_dtcs=23;m.dtcs_polarity='NR'
        r.set_memory(m);raw=r.get_mmap().get_packed()
        self.assertEqual(raw[8:11],bytes([d.DTCS.index(23),d.TONES.index(88.5),0x13]))

    def test_gain_edits_require_explicit_manual_mode(self):
        r=radio(image(manual=False));m=r.get_memory(1);extra(m,'pga').value=0
        with self.assertRaises(errors.InvalidValueError):r.set_memory(m)
        extra(m,'rxmode').value='MANUAL';extra(m,'rxif').value=1234;r.set_memory(m)
        self.assertEqual(struct.unpack_from('<HHH',r.get_mmap().get_packed(),0xf5a),(0x3b8,1234,0x5852))

    def test_switch_to_auto_only_invalidates_marker(self):
        raw=image();r=radio(raw);m=r.get_memory(1);extra(m,'rxmode').value='AUTO';r.set_memory(m)
        expected=bytearray(raw);expected[0xf5e:0xf60]=b'\xff\xff'
        self.assertEqual(r.get_mmap().get_packed(),expected)

    def test_invalid_profile_gain_or_tag_is_auto_and_preserved(self):
        for gain,tag in ((0xffff,0x5852),(0x400,0x5852),(0x3a5,0xffff),(0x3a5,0x5853)):
            raw=bytearray(image());struct.pack_into('<HHH',raw,0xf5a,gain,123,tag)
            r=radio(bytes(raw));m=r.get_memory(1);self.assertEqual(str(extra(m,'rxmode').value),'AUTO')
            r.set_memory(m);self.assertEqual(r.get_mmap().get_packed(),raw)

    def test_new_nfm_channel_keeps_narrow_and_preserves_other_eeprom(self):
        r=radio();m=r.get_memory(200);m.empty=False;m.freq=446006250;m.mode='NFM';m.name='PMR'
        m.tuning_step=12.5;m.power=d.POWER[0];r.set_memory(m)
        saved=r.get_memory(200)
        self.assertEqual((saved.mode,saved.freq,saved.name,saved.tuning_step),('NFM',446006250,'PMR',12.5))
        self.assertEqual(r.get_mmap().get_packed()[0x1d00:],image()[0x1d00:])

    def test_delete_and_recreate_cannot_inherit_stale_manual_profile(self):
        r=radio();m=r.get_memory(1);m.empty=True;r.set_memory(m)
        m=r.get_memory(1);self.assertTrue(m.empty);m.empty=False;m.freq=145000000;m.name='NEW';m.power=d.POWER[0]
        r.set_memory(m);self.assertEqual(str(extra(r.get_memory(1),'rxmode').value),'AUTO')

    def test_preserve_byp_raw_on_unrelated_edit_and_can_select_them(self):
        for mode in (3,4):
            r=radio(image(mode=mode));m=r.get_memory(1);m.name='SPECIAL';r.set_memory(m)
            self.assertEqual(r.get_mmap().get_packed()[11]>>4&7,mode)
        r=radio(image(mode=0));m=r.get_memory(1);extra(m,'demod').value='RAW';r.set_memory(m)
        self.assertEqual(r.get_mmap().get_packed()[11]>>4&7,4)

    def test_bandwidth_bcl_dtmf_scan_and_unknown_bits(self):
        raw=image(mode=0);r=radio(raw);m=r.get_memory(1)
        extra(m,'bcl').value=False;extra(m,'pttid').value='EOT';extra(m,'scanlists').value='List 2'
        extra(m,'bandwidth').value='NARROW';r.set_memory(m);result=r.get_mmap().get_packed()
        self.assertEqual(result[12],raw[12]&~16|2)
        self.assertEqual(result[13],raw[13]&~6|4)
        self.assertEqual(result[0xd60],raw[0xd60]&0x3f|0x40)

    def test_saved_native_image_reopens_with_baseline(self):
        r=radio()
        with tempfile.TemporaryDirectory() as folder:
            p=str(Path(folder)/'rxp.img');r.save(p)
            reopened=d.UVK5FagciTXM0008(p)
            self.assertEqual(reopened._metadata['txp_baseline'],r._metadata['txp_baseline'])
            self.assertEqual(reopened.get_mmap().get_packed(),r.get_mmap().get_packed())


class SerialTests(unittest.TestCase):
    def test_aes_locked_radio_rejected_before_zeroed_eeprom_can_be_read(self):
        pipe = FakeSerial()
        pipe.aes_locked = True
        r = d.UVK5FagciTXM0008(pipe)
        with self.assertRaisesRegex(errors.RadioError, 'AES'):
            r.sync_in()
        self.assertEqual(pipe.commands, [0x514])
        self.assertEqual(pipe.writes, [])

    def test_initial_hello_timeout_can_retry_without_writing_eeprom(self):
        pipe = FakeSerial()
        pipe.drop_hellos = 2
        r = d.UVK5FagciTXM0008(pipe)
        r.status_fn = lambda s: None
        r.sync_in()
        self.assertEqual(pipe.commands[:3], [0x514]*3)
        self.assertEqual(pipe.writes, [])
        self.assertEqual(r.get_memory(1).mode, 'AM')

    def test_download_full_image_with_fragmented_serial_reads(self):
        pipe=FakeSerial(fragment=True);r=d.UVK5FagciTXM0008(pipe);r.status_fn=lambda s:None;r.sync_in()
        self.assertEqual(r.get_mmap().get_packed(),image())
        self.assertEqual(len(pipe.writes),0);self.assertEqual(pipe.commands.count(0x51b),64)

    def test_wrong_firmware_rejected_before_eeprom_read_or_write(self):
        for version in ('IJV 2.9','OSFW-SOS0005','OSFW-TXM00080','OSFW-4dcc901'):
            pipe=FakeSerial(firmware=version);r=d.UVK5FagciTXM0008(pipe)
            with self.assertRaises(errors.RadioError):r.sync_in()
            self.assertEqual(pipe.commands,[0x514]);self.assertEqual(pipe.writes,[])

    def test_upload_changes_only_edited_bytes_preserving_fresh_radio_data(self):
        r=radio();m=r.get_memory(1);m.name='NEW';r.set_memory(m)
        pipe=FakeSerial();pipe.raw[0xf57]=ord('Z');pipe.raw[0x1e00]=42;r.pipe=pipe
        # Byte 7 was originally T in AEROPORT and is edited by this rename;
        # choose instead a truly unedited profile byte in the same second block.
        pipe.raw[0xf57]=image()[0xf57]
        pipe.raw[0xf5b]=2
        before=bytes(pipe.raw);r.sync_out()
        expected=bytearray(before);expected[0xf50:0xf5a]=b'NEW'+bytes(7)
        self.assertEqual(pipe.raw,expected)
        self.assertTrue(pipe.reset)
        self.assertTrue(all(address<0x1d00 and len(payload)==8 for address,payload in pipe.writes))

    def test_all_conflicts_preflight_before_any_write(self):
        r=radio();m=r.get_memory(1);m.name='CHANGEABC';r.set_memory(m)
        pipe=FakeSerial();pipe.raw[0xf58]=ord('X');r.pipe=pipe
        with self.assertRaises(errors.RadioError):r.sync_out()
        self.assertEqual(pipe.writes,[])

    def test_calibration_aes_and_password_modifications_blocked(self):
        for address in (0x1d00,0x1e00,0x1f88,0x1fff,0xf30,0xf3f,0xe98,0xe9f):
            r=radio();raw=bytearray(r.get_mmap().get_packed());raw[address]^=1;r._mmap=memmap.MemoryMapBytes(bytes(raw))
            pipe=FakeSerial();r.pipe=pipe
            with self.assertRaises(errors.RadioError):r.sync_out()
            self.assertEqual(pipe.writes,[]);self.assertEqual(pipe.commands,[])

    def test_ijv_or_raw_image_without_download_baseline_rejected(self):
        r=radio(downloaded=False);pipe=FakeSerial();r.pipe=pipe
        with self.assertRaises(errors.RadioError):r.sync_out()
        self.assertEqual(pipe.commands,[])

    def test_write_ack_and_readback_failures_report_errors(self):
        for failure in ('bad_ack','ignore_write'):
            r=radio();m=r.get_memory(1);m.name='NEW';r.set_memory(m)
            pipe=FakeSerial();setattr(pipe,failure,True);r.pipe=pipe
            with self.assertRaises(errors.RadioError):r.sync_out()
            self.assertFalse(pipe.reset)

    def test_noop_upload_writes_nothing_and_does_not_reset(self):
        r=radio();pipe=FakeSerial();r.pipe=pipe;r.sync_out()
        self.assertEqual(pipe.writes,[]);self.assertFalse(pipe.reset)

    def test_invalid_eeprom_read_reply_is_rejected(self):
        pipe=FakeSerial();pipe.bad_read=True
        with self.assertRaises(errors.RadioError):d._read_block(pipe,0,128)

    def test_incomplete_serial_reply_is_rejected(self):
        class Silent(FakeSerial):
            def read(self,count):return b''
        with self.assertRaises(errors.RadioError):d._hello(Silent())

    def test_profile_upload_verifies_every_written_block(self):
        r=radio(image(manual=False));m=r.get_memory(1);extra(m,'rxmode').value='MANUAL'
        extra(m,'lna').value=7;extra(m,'rxif').value=777;r.set_memory(m)
        pipe=FakeSerial(image(manual=False));r.pipe=pipe;r.sync_out()
        self.assertEqual(struct.unpack_from('<HHH',pipe.raw,0xf5a),(0x3fe,777,0x5852))
        self.assertEqual([address for address,_ in pipe.writes],[0xf58])


if __name__=='__main__':unittest.main(verbosity=2)
