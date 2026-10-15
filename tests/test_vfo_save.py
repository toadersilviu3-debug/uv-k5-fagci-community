# SPDX-License-Identifier: Apache-2.0
"""Execute compiled key dispatch, menu confirmation and EEPROM serialization.

Mock peripheral delays/audio and RF setup, not the key/menu/save implementation.
"""
import struct
import tempfile
import unittest
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_LR
from test_channel_name import ROOT, SYMS, tool, CHANNEL_OFFSET
from test_channel_name import KEY_MENU, KEY_UP, KEY_DOWN, KEY_EXIT, KEY_PTT
from test_spectrum_save import SpectrumRadio, SK2, L as SL

fields = ['TX_CHANNEL', 'RX_CHANNEL', 'KEY_LOCK', 'KEY_2_SHORT_PRESS_ACTION',
          'KEY_2_LONG_PRESS_ACTION', 'ScreenChannel', 'FreqChannel', 'MrChannel']
vfields = ['ConfigRX', 'ConfigTX', 'Band', 'FREQUENCY_OF_DEVIATION',
           'FREQUENCY_DEVIATION_SETTING', 'AM_CHANNEL_MODE', 'STEP_SETTING',
           'CHANNEL_BANDWIDTH', 'OUTPUT_POWER', 'BUSY_CHANNEL_LOCK',
           'FrequencyReverse', 'DTMF_PTT_ID_TX_MODE', 'DTMF_DECODING_ENABLE',
           'SCRAMBLING_TYPE', 'SCANLIST1_PARTICIPATION', 'SCANLIST2_PARTICIPATION',
           'StepFrequency']
with tempfile.TemporaryDirectory() as folder:
    p = Path(folder)
    entries = [f'offsetof(EEPROM_Config_t, {f})' for f in fields]
    entries += [f'offsetof(VFO_Info_t, {f})' for f in vfields]
    entries += ['MENU_MEM_CH', 'FREQ_CHANNEL_FIRST', 'SCAN_OFF', 'CSS_SCAN_MODE_OFF']
    (p/'layout.c').write_text('#include <stddef.h>\n#include "settings.h"\n'
        '#include "ui/menu.h"\n#include "misc.h"\n#include "app/scanner.h"\n'
        'const unsigned int layout[] __attribute__((section(".test_layout"))) = {'
        + ','.join(entries) + '};')
    tool('arm-none-eabi-gcc', '-mcpu=cortex-m0', '-fshort-enums', '-I', ROOT,
         '-c', p/'layout.c', '-o', p/'layout.o')
    tool('arm-none-eabi-objcopy', '-O', 'binary', '-j', '.test_layout',
         p/'layout.o', p/'layout.bin')
    values = struct.unpack('<'+'I'*len(entries), (p/'layout.bin').read_bytes())
    L = dict(zip(fields+vfields+['MEM_CH','VFO_FIRST','SCAN_OFF','CSS_OFF'], values))


class VfoRadio(SpectrumRadio):
    def __init__(self, active=1):
        super().__init__()
        self.active = active
        self.set8('gScreenToDisplay', 0)
        self.set8('gRequestDisplayScreen', 255)
        self.set8('gCurrentFunction', 0)
        self.set8('gScanState', L['SCAN_OFF'])
        self.set8('gCssScanMode', L['CSS_OFF'])
        self.uc.mem_write(SYMS['gTxVfo'], struct.pack('<I', self.vfo(active)))
        self.uc.mem_write(SYMS['gRxVfo'], struct.pack('<I', self.vfo(active)))
        self.uc.mem_write(SYMS['gCurrentVfo'], struct.pack('<I', self.vfo(active)))
        self.config('TX_CHANNEL', active)
        self.config('RX_CHANNEL', active)
        self.config('KEY_2_SHORT_PRESS_ACTION', 2)
        self.config('KEY_2_LONG_PRESS_ACTION', 2)
        for name in ('AUDIO_PlayBeep', 'RADIO_SetupRegisters', 'RADIO_ConfigureChannel',
                     'BACKLIGHT_TurnOn'):
            self.uc.hook_add(UC_HOOK_CODE, self.no_peripheral,
                             begin=SYMS[name], end=SYMS[name])
        self.uc.mem_write(self.vfo(active)+CHANNEL_OFFSET, bytes([L['VFO_FIRST']+2]))
        self.field('ConfigRX', 14552500, 4)
        self.field('ConfigTX', 14552500, 4)
        self.field('Band', self.call('FREQUENCY_GetBand', 14552500))
        self.field('OUTPUT_POWER', 0)

    def no_peripheral(self, uc, address, size, data):
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def config(self, name, value):
        self.uc.mem_write(SYMS['gEeprom']+L[name], bytes([value]))

    def field(self, name, value, size=1):
        self.uc.mem_write(self.vfo(self.active)+L[name], value.to_bytes(size,'little'))

    def event(self, key, pressed=1, held=0):
        self.call('APP_ProcessKey', key, pressed, held)

    def tap_key(self, key):
        self.event(key)
        self.event(key, 0)

    def open(self):
        self.event(SK2)
        self.event(SK2, 1, 1)
        self.event(SK2, 0, 1)
        assert self.get8('gScreenToDisplay') == 2
        assert self.get8('gMenuCursor') == L['MEM_CH']
        assert self.get8('gIsInSubMenu') == 1

    def slot(self, slot):
        self.uc.mem_write(SYMS['gSubMenuSelection'], struct.pack('<I',slot))

    def selected(self):
        return struct.unpack('<I', self.uc.mem_read(SYMS['gSubMenuSelection'],4))[0]


class VfoSaveTests(unittest.TestCase):
    def test_short_press_keeps_configured_action(self):
        r=VfoRadio(); r.tap_key(SK2)
        self.assertEqual(r.get8('gScreenToDisplay'),0)
        self.assertEqual(r.uc.mem_read(r.vfo(1)+L['OUTPUT_POWER'],1),b'\x01')

    def test_long_press_opens_first_free_without_writing(self):
        for active in (0,1):
            r=VfoRadio(active); r.mark(0,2); r.mark(1,2)
            before=bytes(r.eeprom); r.open()
            self.assertEqual(r.selected(),2)
            self.assertEqual(r.eeprom,before)
            self.assertEqual(r.writes,[])
            self.assertEqual(r.uc.mem_read(r.vfo(active)+L['OUTPUT_POWER'],1),b'\0')

    def test_all_full_defaults_first_and_slot_wraps(self):
        r=VfoRadio()
        for slot in range(200): r.mark(slot,2)
        r.open(); self.assertEqual(r.selected(),0)
        r.tap_key(KEY_DOWN); self.assertEqual(r.selected(),199)
        r.tap_key(KEY_UP); self.assertEqual(r.selected(),0)

    def test_cancel_at_both_stages_never_writes(self):
        for confirm in (False,True):
            r=VfoRadio(); before=bytes(r.eeprom); r.open()
            if confirm:r.tap_key(KEY_MENU)
            r.tap_key(KEY_EXIT); r.tap_key(KEY_EXIT)
            self.assertEqual(r.get8('gScreenToDisplay'),0)
            self.assertEqual(r.eeprom,before)
            self.assertEqual(r.writes,[])

    def test_first_menu_and_held_menu_cannot_write(self):
        r=VfoRadio(); r.open(); r.event(KEY_MENU)
        for _ in range(10):r.event(KEY_MENU,1,1)
        r.event(KEY_MENU,0,1)
        self.assertEqual(r.get8('gAskForConfirmation'),1)
        self.assertEqual(r.writes,[])

    def test_changing_slot_invalidates_confirmation_arrows_and_digits(self):
        for keys in ((KEY_DOWN,), (0,0,5)):
            r=VfoRadio(); r.open(); r.tap_key(KEY_MENU)
            for key in keys:r.tap_key(key)
            self.assertEqual(r.get8('gAskForConfirmation'),0)
            r.tap_key(KEY_MENU)
            self.assertEqual(r.writes,[])
            self.assertEqual(r.get8('gAskForConfirmation'),1)

    def test_ptt_and_side_keys_ignored_in_destination_menu(self):
        r=VfoRadio(); r.open()
        for key in (KEY_PTT,SK2,23):
            r.event(key);r.event(key,1,1);r.event(key,0,1)
        self.assertEqual(r.get8('gCurrentFunction'),0)
        self.assertEqual(r.get8('gFlagPrepareTX'),0)
        self.assertEqual(r.writes,[])
        self.assertEqual(r.get8('gIsInSubMenu'),1)

    def test_pending_frequency_or_keypad_lock_does_not_capture_old_frequency(self):
        for guard in ('freqInputIndex','KEY_LOCK'):
            r=VfoRadio()
            if guard=='KEY_LOCK':r.config(guard,1)
            else:r.set8(guard,5)
            r.event(SK2);r.event(SK2,1,1);r.event(SK2,0,1)
            self.assertEqual(r.get8('gScreenToDisplay'),0)
            self.assertEqual(r.writes,[])

    def test_mr_and_other_screens_keep_configured_long_action(self):
        for screen,channel in ((0,37),(2,L['VFO_FIRST']),(1,L['VFO_FIRST'])):
            r=VfoRadio();r.set8('gScreenToDisplay',screen)
            r.uc.mem_write(r.vfo(1)+CHANNEL_OFFSET,bytes([channel]))
            r.call('ACTION_Handle',SK2,1,1)
            self.assertEqual(r.get8('gScreenToDisplay'),screen)
            self.assertEqual(r.uc.mem_read(r.vfo(1)+L['OUTPUT_POWER'],1),b'\x01')

    def test_manual_frequency_entry_accept_then_long_sk2_saves_entered_frequency(self):
        r=VfoRadio();r.field('StepFrequency',1250,2)
        r.field('ConfigRX',14500000,4)
        for key in (1,4,5,14,5,2,5):r.tap_key(key)
        self.assertGreater(r.get8('freqInputIndex'),0)
        r.tap_key(KEY_MENU)
        self.assertEqual(r.get8('freqInputIndex'),0)
        self.assertEqual(struct.unpack('<I',r.uc.mem_read(r.vfo(1)+L['ConfigRX'],4))[0],14552500)
        r.writes.clear();r.open();r.tap_key(KEY_MENU);r.tap_key(KEY_MENU)
        self.assertEqual(struct.unpack('<I',r.eeprom[:4])[0],14552500)

    def test_all_200_slots_save_vfo_parameters_and_preserve_unrelated_eeprom(self):
        for slot in range(200):
            r=VfoRadio(active=slot%2); r.mark(slot,0xC2)
            r.field('AM_CHANNEL_MODE',slot%5)
            r.field('FREQUENCY_OF_DEVIATION',60000,4)
            r.field('FREQUENCY_DEVIATION_SETTING',2)
            r.field('STEP_SETTING',8)
            r.field('CHANNEL_BANDWIDTH',1)
            r.field('OUTPUT_POWER',2)
            r.field('BUSY_CHANNEL_LOCK',1)
            r.field('FrequencyReverse',1)
            r.field('DTMF_PTT_ID_TX_MODE',3)
            r.field('DTMF_DECODING_ENABLE',1)
            r.field('SCRAMBLING_TYPE',7)
            r.field('SCANLIST1_PARTICIPATION',1)
            r.field('SCANLIST2_PARTICIPATION',1)
            r.uc.mem_write(r.vfo(r.active)+L['ConfigRX']+4,b'\x03\x0c')
            r.uc.mem_write(r.vfo(r.active)+L['ConfigTX']+4,b'\x01\x05')
            before=bytes(r.eeprom)
            r.open();r.slot(slot);r.tap_key(KEY_MENU);r.tap_key(KEY_MENU)
            expected=bytearray(before)
            expected[16*slot:16*slot+16]=struct.pack('<II8B',14552500,60000,
                12,5,0x13,(slot%5)<<4|2,0x1B,7,8,7)
            # TXP0007 keeps an existing destination RX-only marker.
            if before[slot*16+15] & 0xf0 == 0xa0:expected[slot*16+15] |= 0xa0
            expected[0xD60+slot]=0xC2
            with self.subTest(slot=slot):
                self.assertEqual(r.eeprom,expected)
                self.assertTrue(r.writes)
                self.assertEqual(r.get8('gIsInSubMenu'),0)


if __name__=='__main__':unittest.main()
