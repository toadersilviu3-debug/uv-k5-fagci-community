# SPDX-License-Identifier: Apache-2.0
# Added for the independent SPC0002 community fork, 2026-10-13.
"""ARM integration tests for Spectrum SK2 capture, confirmation, and EEPROM.

Uses the same compiled image as the name tests. In addition to EEPROM/LCD,
mock keyboard polling, UART logging, and delays; execute actual UI dispatch,
channel serialization, validity checks, and channel reload code.
"""
import struct
import tempfile
import unittest
from pathlib import Path

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC, UC_ARM_REG_LR
from test_channel_name import ROOT, Radio, SYMS, tool, CHANNEL_OFFSET, NAME_OFFSET
from test_channel_name import KEY_MENU, KEY_UP, KEY_DOWN, KEY_EXIT, KEY_PTT

SK2, INVALID = 22, 255
with tempfile.TemporaryDirectory() as folder:
    p = Path(folder)
    names = ['PEAK_F', 'MODULATION', 'BANDWIDTH', 'STEP', 'POWER', 'SCREEN_CHANNEL',
             'CONFIG_RX', 'CONFIG_TX', 'VFO_MODULATION', 'VFO_BANDWIDTH', 'VFO_STEP',
             'KBD_COUNTER', 'SPECTRUM', 'STILL', 'SAVE_CHANNEL']
    (p / 'layout.c').write_text('''
#include <stddef.h>
#include "app/spectrum.h"
const unsigned int layout[] __attribute__((section(".test_layout"))) = {
 offsetof(PeakInfo, f), offsetof(SpectrumSettings, modulationType),
 offsetof(SpectrumSettings, listenBw), offsetof(SpectrumSettings, scanStepIndex),
 offsetof(VFO_Info_t, OUTPUT_POWER), offsetof(EEPROM_Config_t, ScreenChannel),
 offsetof(VFO_Info_t, ConfigRX), offsetof(VFO_Info_t, ConfigTX),
 offsetof(VFO_Info_t, ModulationType), offsetof(VFO_Info_t, CHANNEL_BANDWIDTH),
 offsetof(VFO_Info_t, STEP_SETTING), offsetof(KeyboardState, counter),
 SPECTRUM, STILL, SAVE_CHANNEL
};
''')
    tool('arm-none-eabi-gcc', '-Os', '-mcpu=cortex-m0', '-fshort-enums', '-I', ROOT,
         '-I', ROOT / 'external/CMSIS_5/CMSIS/Core/Include',
         '-I', ROOT / 'external/CMSIS_5/Device/ARM/ARMCM0/Include',
         '-c', p / 'layout.c', '-o', p / 'layout.o')
    tool('arm-none-eabi-objcopy', '-O', 'binary', '-j', '.test_layout',
         p / 'layout.o', p / 'layout.bin')
    L = dict(zip(names, struct.unpack('<15I', (p / 'layout.bin').read_bytes())))


class SpectrumRadio(Radio):
    def __init__(self, eeprom=None):
        super().__init__(eeprom)
        self.input_key = INVALID
        self.screens = []
        for name in ('GetKey', 'SYSTEM_DelayMs', 'UART_LogSend'):
            self.uc.hook_add(UC_HOOK_CODE, self.peripheral,
                             begin=SYMS[name], end=SYMS[name])
        if type(self) is SpectrumRadio:
            self.uc.hook_add(UC_HOOK_CODE, self.peripheral,
                begin=SYMS['BK4819_ReadRegister'], end=SYMS['BK4819_ReadRegister'])
        self.uc.hook_add(UC_HOOK_CODE, self.lcd, begin=SYMS['ST7565_BlitFullScreen'], end=SYMS['ST7565_BlitFullScreen'])
        if eeprom is None:
            self.eeprom[0xD60:0xD60 + 200] = b'\xff' * 200
            self.mark(37, 0xC5)
        self.sync_attributes()
        for i in range(2):
            self.uc.mem_write(self.vfo(i) + L['POWER'], b'\x02')

    def lcd(self, uc, address, size, data):
        self.screens.append(bytes(uc.mem_read(SYMS['gFrameBuffer'], 896)))

    def peripheral(self, uc, address, size, data):
        if address == SYMS['GetKey']:
            uc.reg_write(UC_ARM_REG_R0, self.input_key)
        elif address == SYMS['BK4819_ReadRegister']:
            reg = uc.reg_read(UC_ARM_REG_R0)
            uc.reg_write(UC_ARM_REG_R0, {0x13: 0x3BE, 0x3D: 0x2AAB}.get(reg, 0))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def sync_attributes(self):
        self.uc.mem_write(SYMS['gMR_ChannelAttributes'], bytes(self.eeprom[0xD60:0xD60 + 200]))

    def mark(self, slot, value):
        self.eeprom[0xD60 + slot] = value
        self.uc.mem_write(SYMS['gMR_ChannelAttributes'] + slot, bytes([value]))

    def frequency(self, value, state=None, tuned=None):
        self.uc.mem_write(SYMS['peak'] + L['PEAK_F'], struct.pack('<I', value))
        self.uc.mem_write(SYMS['fMeasure'], struct.pack('<I', tuned if tuned is not None else value + 2500))
        self.set8('currentState', L['SPECTRUM'] if state is None else state)

    def configure(self, modulation=0, bandwidth=0, step=10):
        for key, value in [('MODULATION', modulation), ('BANDWIDTH', bandwidth), ('STEP', step)]:
            self.uc.mem_write(SYMS['settings'] + L[key], bytes([value]))

    def press(self, key):
        self.input_key = key
        # Debounce threshold: same physical-key transition as the fifth poll.
        self.uc.mem_write(SYMS['kbd'], bytes([key, key, 4]))
        self.call('HandleUserInput')

    def release(self):
        self.input_key = INVALID
        self.call('HandleUserInput')

    def tap(self, key):
        self.press(key)
        self.release()

    def hold(self, key, polls=50):
        self.input_key = key
        self.uc.mem_write(SYMS['kbd'], bytes([key, key, 41]))
        for _ in range(polls):
            self.call('HandleUserInput')

    def open_save(self, frequency=14552500, state=None, tuned=None):
        self.frequency(frequency, state, tuned)
        self.tap(SK2)
        self.assert_save()

    def assert_save(self):
        assert self.get8('currentState') == L['SAVE_CHANNEL']

    def select(self, slot):
        for _ in range(200):
            if self.get8('saveChannel') == slot:
                return
            self.tap(KEY_UP)
        raise AssertionError('slot not selectable')

    def confirm(self):
        self.tap(KEY_MENU)
        self.tap(KEY_MENU)


class SpectrumSaveTests(unittest.TestCase):
    def test_sk2_uses_displayed_peak_not_sweeping_frequency(self):
        radio = SpectrumRadio()
        radio.open_save(14552500, tuned=14600000)
        self.assertEqual(struct.unpack('<I', radio.uc.mem_read(SYMS['saveFrequency'], 4))[0], 14552500)
        self.assertEqual(radio.get8('saveChannel'), 0)
        self.assertFalse(radio.writes)

    def test_sk2_in_still_uses_actual_tuned_frequency(self):
        radio = SpectrumRadio()
        radio.open_save(14552500, state=L['STILL'], tuned=14552610)
        radio.confirm()
        self.assertEqual(struct.unpack('<I', radio.eeprom[:4])[0], 14552610)
        self.assertEqual(radio.get8('currentState'), L['STILL'])

    def test_invalid_peak_or_transmission_does_not_open_save(self):
        for frequency in (0, 1499999, 134000001):
            radio = SpectrumRadio()
            radio.frequency(frequency)
            radio.tap(SK2)
            self.assertEqual(radio.get8('currentState'), L['SPECTRUM'])
            self.assertFalse(radio.writes)
        radio = SpectrumRadio()
        radio.frequency(14552500, L['STILL'])
        radio.set8('isTransmitting', 1)
        radio.press(SK2)
        self.assertEqual(radio.get8('currentState'), L['STILL'])
        self.assertFalse(radio.writes)

    def test_all_200_occupied_slots_change_only_target_channel_and_attribute(self):
        radio = SpectrumRadio()
        radio.eeprom[0xD60:0xD60 + 200] = b'\xc5' * 200
        radio.sync_attributes()
        for slot in range(200):
            with self.subTest(slot=slot + 1):
                radio.open_save()
                self.assertEqual(radio.get8('saveChannel'), 0)  # all occupied
                radio.set8('saveChannel', slot)
                before = bytes(radio.eeprom)
                radio.writes.clear()
                radio.confirm()
                expected = bytearray(before)
                expected[slot * 16:slot * 16 + 16] = struct.pack('<II', 14552500, 0) + bytes([0, 0, 0, 0, 8, 0, 10, 0])
                # TXP0007 preserves a destination's explicit RX-only flag.
                if before[slot*16+15] & 0xf0 == 0xa0:
                    expected[slot*16+15] |= 0xa0
                expected[0xD60 + slot] = 0xC2  # VHF band, both scan lists
                self.assertEqual(radio.eeprom, expected)
                allowed = {slot * 16, slot * 16 + 8, 0xD60 + (slot & ~7)}
                self.assertTrue(all(address in allowed for address, _ in radio.writes))
                self.assertEqual(radio.get8('gFlagResetVfos'), 1)
                self.assertEqual(radio.get8('gVfoConfigureMode'), 2)

    def test_new_channel_clears_old_unused_name_preserves_reserved_and_calibration(self):
        radio = SpectrumRadio()
        radio.open_save()
        before = bytes(radio.eeprom)
        radio.confirm()
        expected = bytearray(before)
        expected[:16] = struct.pack('<II', 14552500, 0) + bytes([0, 0, 0, 0, 8, 0, 10, 0])
        expected[0xD60] = 0xC2
        expected[0xF50:0xF5A] = b'\0' * 10
        self.assertEqual(radio.eeprom, expected)

    def test_first_free_channel_and_slot_wrap(self):
        radio = SpectrumRadio()
        for slot in range(8):
            radio.mark(slot, 0xC2)
        radio.open_save()
        self.assertEqual(radio.get8('saveChannel'), 8)
        radio.set8('saveChannel', 0)
        radio.tap(KEY_DOWN)
        self.assertEqual(radio.get8('saveChannel'), 199)
        radio.tap(KEY_UP)
        self.assertEqual(radio.get8('saveChannel'), 0)

    def test_one_menu_and_holding_menu_do_not_save(self):
        radio = SpectrumRadio()
        radio.open_save()
        before = bytes(radio.eeprom)
        radio.press(KEY_MENU)
        self.assertEqual(radio.get8('saveConfirm'), 1)
        radio.hold(KEY_MENU)
        self.assertEqual(radio.eeprom, before)
        self.assertFalse(radio.writes)
        radio.release()
        radio.tap(KEY_MENU)
        self.assertTrue(radio.writes)

    def test_changed_slot_requires_new_confirmation(self):
        radio = SpectrumRadio()
        radio.open_save()
        radio.tap(KEY_MENU)
        radio.tap(KEY_UP)
        self.assertEqual(radio.get8('saveConfirm'), 0)
        radio.tap(KEY_MENU)
        self.assertFalse(radio.writes)
        radio.tap(KEY_MENU)
        self.assertTrue(radio.writes)

    def test_cancel_at_either_stage_preserves_whole_eeprom_and_vfos(self):
        for confirm in (False, True):
            radio = SpectrumRadio()
            radio.open_save()
            before = bytes(radio.eeprom)
            vfo_before = bytes(radio.uc.mem_read(SYMS['gEeprom'], 300))
            if confirm:
                radio.tap(KEY_MENU)
            radio.tap(KEY_EXIT)
            self.assertEqual(radio.get8('currentState'), L['SPECTRUM'])
            self.assertEqual(radio.eeprom, before)
            self.assertEqual(bytes(radio.uc.mem_read(SYMS['gEeprom'], 300)), vfo_before)
            self.assertFalse(radio.writes)

    def test_held_sk2_waits_for_release_and_ptt_is_ignored_in_save(self):
        radio = SpectrumRadio()
        radio.frequency(14552500)
        radio.press(SK2)
        radio.hold(SK2)
        self.assertEqual(radio.get8('currentState'), L['SAVE_CHANNEL'])
        radio.release()
        radio.tap(KEY_PTT)
        self.assertEqual(radio.get8('isTransmitting'), 0)
        self.assertFalse(radio.writes)

    def test_frequency_stays_captured_and_other_keys_do_not_change_modulation(self):
        radio = SpectrumRadio()
        radio.configure(2, 2, 3)
        radio.open_save()
        radio.uc.mem_write(SYMS['peak'] + L['PEAK_F'], struct.pack('<I', 14600000))
        for key in (0, 5, 6, SK2):
            radio.tap(key)
        radio.confirm()
        self.assertEqual(struct.unpack('<I', radio.eeprom[:4])[0], 14552500)
        self.assertEqual(radio.eeprom[11] >> 4, 2)
        self.assertEqual(radio.eeprom[14], 3)

    def test_all_modulations_bandwidths_and_steps_persist_after_channel_reload(self):
        for modulation in range(5):
            for bandwidth in range(3):
                for step in range(12):
                    with self.subTest(modulation=modulation, bandwidth=bandwidth, step=step):
                        radio = SpectrumRadio()
                        radio.configure(modulation, bandwidth, step)
                        radio.open_save()
                        radio.confirm()
                        restarted = SpectrumRadio(radio.eeprom)
                        restarted.uc.mem_write(SYMS['gEeprom'] + L['SCREEN_CHANNEL'], b'\0\0')
                        restarted.call('RADIO_ConfigureChannel', 0, 2)
                        vfo = restarted.vfo(0)
                        self.assertEqual(struct.unpack('<I', restarted.uc.mem_read(vfo + L['CONFIG_RX'], 4))[0], 14552500)
                        self.assertEqual(struct.unpack('<I', restarted.uc.mem_read(vfo + L['CONFIG_TX'], 4))[0], 14552500)
                        self.assertEqual(restarted.uc.mem_read(vfo + L['VFO_MODULATION'], 1)[0], modulation)
                        self.assertEqual(restarted.uc.mem_read(vfo + L['VFO_BANDWIDTH'], 1)[0], int(bandwidth != 0))
                        self.assertEqual(restarted.uc.mem_read(vfo + L['VFO_STEP'], 1)[0], step)

    def test_name_editor_can_rename_channel_created_by_spectrum(self):
        radio = SpectrumRadio()
        radio.open_save()
        radio.confirm()
        radio.uc.mem_write(radio.vfo(1) + CHANNEL_OFFSET, b'\0')
        radio.call('MENU_ShowCurrentSetting')
        self.assertEqual(radio.text(), b'          \0')
        radio.key(KEY_MENU)
        radio.key(7)
        radio.key(KEY_MENU)
        radio.finish()
        self.assertEqual(radio.eeprom[0xF50:0xF5A], b'7' + b'\0' * 9)

    def test_save_menu_and_confirmation_render_without_frame_overflow(self):
        radio = SpectrumRadio()
        radio.eeprom[0xD60:0xD60 + 200] = b'\xc5' * 200
        radio.sync_attributes()
        radio.open_save(134000000)
        radio.set8('saveChannel', 199)
        radio.call('SPECTRUM_Render')
        radio.tap(KEY_MENU)
        radio.call('SPECTRUM_Render')
        for frame in radio.screens:
            self.assertEqual(len(frame), 896)
            self.assertEqual(frame[6 * 128:7 * 128], b'\0' * 128)
        self.assertGreaterEqual(len(radio.screens), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
