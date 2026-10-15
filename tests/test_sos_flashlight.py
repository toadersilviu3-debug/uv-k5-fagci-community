# SPDX-License-Identifier: Apache-2.0
"""Verify actual ARM GPIO output and timing, with the existing radio fixture."""
import struct
import unittest
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC, UC_ARM_REG_LR
from test_channel_name import SYMS
from test_am_hardware_agc import AgcRadio
from test_vfo_save import L

GPIOC_DATA=0x40061000
LED=1<<3
# Three dots, letter gap, three dashes, letter gap, three dots, word gap.
SOS='10101'+'000'+'11101110111'+'000'+'10101'+'0000000'


class LedRadio(AgcRadio):
    def __init__(self):
        super().__init__()
        self.uc.mem_write(SYMS['gEeprom']+L['KEY_2_SHORT_PRESS_ACTION'],b'\x01')
        self.uc.mem_write(GPIOC_DATA,struct.pack('<I',0xA5A5A5A5&~LED))
        for name in ('APP_CheckKeys','UART_IsCommandAvailable'):
            self.uc.hook_add(UC_HOOK_CODE,self.skip_input,
                             begin=SYMS[name],end=SYMS[name])

    def skip_input(self,uc,address,size,data):
        uc.reg_write(UC_ARM_REG_R0,0)
        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))

    def press(self):
        self.call('ACTION_Handle',22,1,0)
        self.call('ACTION_Handle',22,0,0)

    def led(self):
        return int(bool(struct.unpack('<I',self.uc.mem_read(GPIOC_DATA,4))[0]&LED))

    def tick(self):
        self.call('ACTION_FlashLightTick')
        return str(self.led())

    def start_sos(self):
        self.press();self.press()
        assert self.get8('gFlashLightState')==2


class SosFlashlightTests(unittest.TestCase):
    def test_three_short_presses_select_on_sos_off(self):
        r=LedRadio()
        r.press();self.assertEqual((r.get8('gFlashLightState'),r.led()),(1,1))
        r.press();self.assertEqual((r.get8('gFlashLightState'),r.led()),(2,0))
        r.press();self.assertEqual((r.get8('gFlashLightState'),r.led()),(0,0))

    def test_sos_output_repeats_with_three_unit_letter_and_seven_unit_word_gaps(self):
        r=LedRadio();r.start_sos()
        self.assertEqual(''.join(r.tick() for _ in range(34*5)),SOS*5)

    def test_restart_from_every_position_begins_with_first_dot(self):
        for count in range(1,35):
            r=LedRadio();r.start_sos()
            for _ in range(count):r.tick()
            r.press();r.press();r.press() # OFF, ON, SOS
            self.assertEqual(''.join(r.tick() for _ in range(34)),SOS)

    def test_continuous_and_off_modes_do_not_blink(self):
        r=LedRadio()
        self.assertEqual(''.join(r.tick() for _ in range(70)),'0'*70)
        r.press()
        self.assertEqual(''.join(r.tick() for _ in range(70)),'1'*70)

    def test_gpio_changes_only_flashlight_pin_and_never_writes_eeprom(self):
        r=LedRadio();before=bytes(r.eeprom)
        unrelated=struct.unpack('<I',r.uc.mem_read(GPIOC_DATA,4))[0]&~LED
        r.start_sos()
        for _ in range(70):
            r.tick()
            self.assertEqual(struct.unpack('<I',r.uc.mem_read(GPIOC_DATA,4))[0]&~LED,unrelated)
        self.assertEqual(r.eeprom,before)
        self.assertEqual(r.writes,[])

    def test_real_10ms_scheduler_produces_160ms_morse_units_and_runs_am_fix(self):
        r=LedRadio();r.setup(1);r.start_sos()
        r.uc.mem_write(SYMS['gFlashLightBlinkCounter'],b'\0\0')
        for _ in range(15):
            r.call('APP_TimeSlice10ms')
            self.assertEqual(r.led(),0)
        r.call('APP_TimeSlice10ms');self.assertEqual(r.led(),1)
        # First unit was just started. Sample once after every further 160 ms.
        result='1'
        for _ in range(33):
            for _ in range(16):r.call('APP_TimeSlice10ms')
            result+=str(r.led())
        self.assertEqual(result,SOS)
        self.assertEqual(r.regs[0x7e],0xb000)
        self.assertEqual(r.regs[0x13],0x3ff)


if __name__=='__main__':unittest.main()
