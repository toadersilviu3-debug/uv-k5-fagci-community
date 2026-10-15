"""Run actual TXM0008 ARM code; no physical radio or RF operations."""
import struct
import tempfile
import unittest
from pathlib import Path
from test_firmware_interop import ProfileRadio, FW_ROOT
from test_driver import radio, extra, d
from test_channel_name import SYMS, tool
from test_vfo_save import L
from test_spectrum_save import L as SL
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_LR

with tempfile.TemporaryDirectory() as folder:
    p=Path(folder)
    (p/'layout.c').write_text('#include <stddef.h>\n#include "radio.h"\n'
        'const unsigned int a[] __attribute__((section(".test_layout"))) = {offsetof(VFO_Info_t,TxInhibit)};')
    tool('arm-none-eabi-gcc','-mcpu=cortex-m0','-fshort-enums','-I',FW_ROOT,'-c',p/'layout.c','-o',p/'layout.o')
    tool('arm-none-eabi-objcopy','-O','binary','-j','.test_layout',p/'layout.o',p/'layout.bin')
    TX_INHIBIT=struct.unpack('<I',(p/'layout.bin').read_bytes())[0]


def inhibit(arm):return arm.uc.mem_read(arm.vfo(arm.active)+TX_INHIBIT,1)[0]
def skip(uc,address,size,data):uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))


class TxInhibitTests(unittest.TestCase):
    def saved(self,slot=0,blocked=True):
        arm=ProfileRadio()
        arm.begin(True);arm.select(slot);arm.confirm()
        driver=radio(bytes(arm.eeprom))
        memory=driver.get_memory(slot+1)
        extra(memory,'txenabled').value=not blocked
        driver.set_memory(memory)
        arm.eeprom=bytearray(driver.get_mmap().get_packed())
        return arm.restart(slot)

    def test_all_200_channels_block_even_with_global_tx_enable_both_vfos(self):
        base=self.saved()
        for slot in range(200):
            start=slot*16
            base.eeprom[start:start+16]=base.eeprom[:16]
            base.eeprom[0xd60+slot]=0xc2
            for active in (0,1):
                arm=base.restart(slot,active)
                arm.set8('gSetting_ALL_TX',1)
                self.assertEqual(inhibit(arm),1)
                self.assertEqual(arm.call('FREQUENCY_Check',arm.vfo(active)),0)

    def test_legacy_scrambling_and_unset_values_keep_original_tx_behavior(self):
        base=self.saved(blocked=False)
        for value in (*range(11),0xff,0x10,0xb7):
            base.eeprom[15]=value
            arm=base.restart(0)
            arm.set8('gSetting_ALL_TX',1)
            self.assertEqual(inhibit(arm),0)
            self.assertEqual(arm.call('FREQUENCY_Check',arm.vfo(0)),1)

    def test_enable_respects_global_disabled_and_frequency_limits(self):
        arm=self.saved(blocked=False)
        arm.set8('gSetting_ALL_TX',2)
        self.assertEqual(arm.call('FREQUENCY_Check',arm.vfo(0)),0)
        arm.set8('gSetting_ALL_TX',0);arm.set8('gSetting_F_LOCK',0)
        self.assertEqual(arm.call('FREQUENCY_Check',arm.vfo(0)),1)
        arm.eeprom[:4]=struct.pack('<I',11995000);arm.eeprom[0xd60]=0xc1
        arm=arm.restart(0)
        arm.set8('gSetting_ALL_TX',0);arm.set8('gSetting_F_LOCK',0)
        self.assertEqual(arm.call('FREQUENCY_Check',arm.vfo(0)),0)

    def test_reverse_and_offset_cannot_bypass_flag(self):
        base=self.saved()
        for reverse in (0,1):
            for shift in (0,1,2):
                base.eeprom[12]=(base.eeprom[12]&~1)|reverse
                base.eeprom[11]=(base.eeprom[11]&0xf0)|shift
                arm=base.restart(0);arm.set8('gSetting_ALL_TX',1)
                self.assertEqual(arm.call('FREQUENCY_Check',arm.vfo(0)),0)

    def test_channel_resave_preserves_flag_scrambling_and_rx_profile(self):
        arm=self.saved()
        arm.uc.mem_write(arm.vfo(0)+L['SCRAMBLING_TYPE'],b'\x09')
        arm.call('SETTINGS_SaveChannel',0,0,arm.vfo(0),2)
        self.assertEqual(arm.eeprom[15],0xa9)
        arm=arm.restart(0)
        self.assertEqual(inhibit(arm),1)
        self.assertEqual(arm.profile(),(0x3a5,0x2345,1))

    def test_switching_to_vfo_drops_memory_inhibit(self):
        arm=self.saved()
        arm.uc.mem_write(SYMS['gEeprom']+L['ScreenChannel'],bytes([L['VFO_FIRST'],L['VFO_FIRST']]))
        arm.call('RADIO_ConfigureChannel',0,2)
        self.assertEqual(inhibit(arm),0)

    def test_vfo_and_spectrum_overwrite_keep_destination_tx_disabled(self):
        base=self.saved()
        for manual in (False,True):
            arm=base.restart(0)
            arm.uc.mem_write(arm.vfo(0)+TX_INHIBIT,b'\0')
            arm.call('SETTINGS_SaveChannel',0,0,arm.vfo(0),2)
            self.assertEqual(arm.eeprom[15]&0xf0,0xa0)
            arm.begin(manual);arm.select(0);arm.confirm()
            arm=arm.restart(0)
            self.assertEqual(inhibit(arm),1)

    def test_empty_slot_stale_marker_is_not_restored_by_spectrum_save(self):
        arm=self.saved()
        arm.mark(0,0xff)
        arm.begin();arm.select(0);arm.confirm()
        arm=arm.restart(0)
        self.assertEqual(inhibit(arm),0)

    def test_normal_ptt_and_all_alarm_paths_do_not_enter_transmit(self):
        for alarm in range(4):
            arm=self.saved();arm.set8('gSetting_ALL_TX',1);arm.set8('gAlarmState',alarm)
            arm.uc.hook_add(UC_HOOK_CODE,skip,begin=SYMS['AUDIO_PlayBeep'],end=SYMS['AUDIO_PlayBeep'])
            arm.call('RADIO_PrepareTX')
            self.assertEqual(arm.get8('gCurrentFunction'),0)
            self.assertEqual(arm.get8('VfoState'),3)
            self.assertEqual(arm.reg_writes,[])

    def test_low_level_tx_setup_does_not_program_transmitter(self):
        arm=self.saved()
        arm.call('RADIO_SetTxParameters')
        self.assertEqual(arm.reg_writes,[])

    def test_spectrum_ptt_and_direct_toggle_are_blocked(self):
        arm=self.saved();arm.set8('gSetting_ALL_TX',1)
        arm.uc.hook_add(UC_HOOK_CODE,skip,begin=SYMS['UpdateBatteryInfo'],end=SYMS['UpdateBatteryInfo'])
        arm.set8('gBatteryDisplayLevel',4)
        arm.frequency(14552500,SL['STILL'],14552500)
        arm.tap(21)
        self.assertEqual(arm.get8('txAllowState'),3)
        self.assertEqual(arm.get8('isTransmitting'),0)
        arm.call('ToggleTX',1)
        self.assertEqual(arm.get8('isTransmitting'),0)
        self.assertEqual(arm.reg_writes,[])


if __name__=='__main__':unittest.main(verbosity=2)
