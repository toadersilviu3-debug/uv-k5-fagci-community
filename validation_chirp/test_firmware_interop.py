"""Actual compiled TXM0008 EEPROM serializer/loader interoperates with CHIRP.

Requires Unicorn and the existing compiled firmware test harness. No hardware I/O.
"""
import sys
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FW_ROOT=Path(os.environ.get('UVK5_FIRMWARE_DIR',ROOT/'work/uv-k5-TXM0008'))
sys.path.insert(0, str(FW_ROOT / 'tests'))
from test_rx_profile import ProfileRadio
from test_driver import radio, extra


class FirmwareInteropTests(unittest.TestCase):
    def saved(self, slot, manual):
        arm = ProfileRadio()
        arm.begin(manual)
        arm.select(slot)
        arm.confirm()
        return arm

    def test_compiled_spectrum_save_decodes_and_roundtrips_in_chirp(self):
        for slot in (0, 24, 199):
            for manual in (False, True):
                arm = self.saved(slot, manual)
                raw = bytes(arm.eeprom)
                driver = radio(raw)
                memory = driver.get_memory(slot + 1)
                with self.subTest(slot=slot, manual=manual):
                    self.assertFalse(memory.empty)
                    self.assertEqual(memory.freq, 145525000)
                    self.assertEqual(memory.mode, 'NAM')
                    self.assertEqual(memory.tuning_step, 12.5)
                    self.assertEqual(str(memory.power), 'High')
                    self.assertEqual(str(extra(memory, 'rxmode').value), 'MANUAL' if manual else 'AUTO')
                    if manual:
                        self.assertEqual([int(extra(memory, key).value) for key in ('lnas', 'lna', 'mix', 'pga', 'rxif')], [3,5,0,5,0x2345])
                    driver.set_memory(memory)
                    self.assertEqual(driver.get_mmap().get_packed(), raw)

    def test_chirp_edits_load_in_compiled_firmware_both_vfos(self):
        arm = self.saved(24, True)
        driver = radio(bytes(arm.eeprom))
        memory = driver.get_memory(25)
        memory.name = 'AERO TEST'
        memory.freq = 119950000
        memory.mode = 'AM'
        memory.tuning_step = 8.33
        extra(memory, 'pga').value = 2
        extra(memory, 'rxif').value = 0x1234
        driver.set_memory(memory)
        edited = driver.get_mmap().get_packed()
        arm.eeprom = bytearray(edited)
        for vfo in (0, 1):
            restarted = arm.restart(24, vfo)
            self.assertEqual(restarted.profile(), (0x3a2, 0x1234, 1))
            restarted.setup(1)
            self.assertEqual((restarted.regs[0x13], restarted.regs[0x3d]), (0x3a2, 0x1234))
            self.assertEqual(restarted.regs[0x7e] & 0xf000, 0xb000)
        readback = radio(edited).get_memory(25)
        self.assertEqual((readback.name, readback.freq, readback.mode, readback.tuning_step), ('AERO TEST',119950000,'AM',8.33))

    def test_chirp_disabling_manual_profile_reenables_compiled_am_fix(self):
        arm = self.saved(0, True)
        driver = radio(bytes(arm.eeprom))
        memory = driver.get_memory(1)
        extra(memory, 'rxmode').value = 'AUTO'
        driver.set_memory(memory)
        arm.eeprom = bytearray(driver.get_mmap().get_packed())
        restarted = arm.restart(0)
        self.assertEqual(restarted.profile()[2], 0)
        restarted.setup(1)
        for _ in range(50):
            restarted.call('APP_TimeSlice10ms')
        self.assertEqual(restarted.regs[0x13], 0x3ff)


if __name__ == '__main__':
    unittest.main(verbosity=2)
