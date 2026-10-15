# SPDX-License-Identifier: Apache-2.0
"""AMH0004 register integration tests, not an RF/audio quality simulation.

Execute real RX setup, AM-fix, modulation, TX preparation, and Spectrum entry/
exit. Mock the BK4819 register bus, RSSI and delays. Keep all controller logic.
"""
import hashlib
import struct
import tempfile
import unittest
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_PC, UC_ARM_REG_LR
from test_channel_name import ROOT, SYMS, tool, CHANNEL_OFFSET
from test_spectrum_save import SpectrumRadio, L as SL
from test_vfo_save import L

with tempfile.TemporaryDirectory() as folder:
    p=Path(folder)
    (p/'layout.c').write_text('#include <stddef.h>\n#include "radio.h"\n'
        'const unsigned int layout[] __attribute__((section(".test_layout"))) = {'
        'offsetof(VFO_Info_t,pRX),offsetof(VFO_Info_t,pTX)};')
    tool('arm-none-eabi-gcc','-mcpu=cortex-m0','-fshort-enums','-I',ROOT,
         '-c',p/'layout.c','-o',p/'layout.o')
    tool('arm-none-eabi-objcopy','-O','binary','-j','.test_layout',p/'layout.o',p/'layout.bin')
    PRX,PTX=struct.unpack('<II',(p/'layout.bin').read_bytes())


class AgcRadio(SpectrumRadio):
    def __init__(self,active=0):
        self.stop_on_poll=False
        super().__init__()
        self.regs={}
        self.reg_writes=[]
        self.rssi=80
        self.active=active
        self.set8('gCurrentFunction',0)
        self.set8('gScreenToDisplay',0)
        self.set8('gScanState',L['SCAN_OFF'])
        self.set8('gCssScanMode',L['CSS_OFF'])
        self.uc.mem_write(SYMS['gEeprom']+L['TX_CHANNEL'],bytes([active]))
        self.uc.mem_write(SYMS['gEeprom']+L['RX_CHANNEL'],bytes([active]))
        for i in range(2):
            ptr=self.vfo(i)
            self.uc.mem_write(ptr+CHANNEL_OFFSET,bytes([L['VFO_FIRST']+1]))
            self.uc.mem_write(ptr+L['ConfigRX'],struct.pack('<I',12345000))
            self.uc.mem_write(ptr+L['ConfigTX'],struct.pack('<I',12345000))
            self.uc.mem_write(ptr+PRX,struct.pack('<I',ptr+L['ConfigRX']))
            self.uc.mem_write(ptr+PTX,struct.pack('<I',ptr+L['ConfigTX']))
        for name in ('gRxVfo','gTxVfo','gCurrentVfo'):
            self.uc.mem_write(SYMS[name],struct.pack('<I',self.vfo(active)))
        for name in ('BK4819_ReadRegister','BK4819_WriteRegister','BK4819_GetRSSI',
                     'SYSTICK_DelayUs','BACKLIGHT_TurnOn'):
            self.uc.hook_add(UC_HOOK_CODE,self.register_bus,
                begin=SYMS[name],end=SYMS[name])
        self.call('AM_fix_init')

    def register_bus(self,uc,address,size,data):
        reg=uc.reg_read(UC_ARM_REG_R0)
        if address==SYMS['BK4819_ReadRegister']:
            uc.reg_write(UC_ARM_REG_R0,self.regs.get(reg,0))
        elif address==SYMS['BK4819_WriteRegister']:
            value=uc.reg_read(UC_ARM_REG_R1)&0xffff
            self.regs[reg]=value
            self.reg_writes.append((reg,value))
        elif address==SYMS['BK4819_GetRSSI']:
            uc.reg_write(UC_ARM_REG_R0,self.rssi)
        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))

    def peripheral(self,uc,address,size,data):
        if self.stop_on_poll and address==SYMS['GetKey']:
            self.set8('isInitialized',0)
        super().peripheral(uc,address,size,data)

    def modulation(self,mode):
        self.uc.mem_write(self.vfo(self.active)+SL['VFO_MODULATION'],bytes([mode]))
        self.uc.mem_write(self.vfo(self.active)+L['AM_CHANNEL_MODE'],bytes([mode]))

    def setup(self,mode):
        self.modulation(mode)
        self.call('RADIO_SetupRegisters',1)

    def index(self):
        return struct.unpack('<I',self.uc.mem_read(SYMS['gain_table_index']+4*self.active,4))[0]


class AmHardwareAgcTests(unittest.TestCase):
    def test_am_selects_fixed_slot_three_preserving_low_bits_both_vfos(self):
        for active in (0,1):
            for initial in (0,0x302e,0x7abc,0xffff):
                r=AgcRadio(active);r.regs[0x7e]=initial;r.setup(1)
                self.assertEqual(r.regs[0x7e],0xb000|(initial&0xfff))
                self.assertEqual(r.writes,[])

    def test_non_am_modes_restore_automatic_agc(self):
        for mode in (0,2,3,4):
            r=AgcRadio();r.regs[0x7e]=0xbabc;r.setup(mode)
            self.assertEqual(r.regs[0x7e],0x3abc)

    def test_am_fm_am_transition_and_active_vfo_switch(self):
        r=AgcRadio();r.regs[0x7e]=0x302e
        for active,mode,expected in ((0,1,0xb02e),(1,0,0x302e),(0,1,0xb02e)):
            r.active=active
            r.uc.mem_write(SYMS['gRxVfo'],struct.pack('<I',r.vfo(active)))
            r.uc.mem_write(SYMS['gEeprom']+L['RX_CHANNEL'],bytes([active]))
            r.setup(mode);self.assertEqual(r.regs[0x7e],expected)

    def test_software_controller_still_adjusts_reg13_under_fixed_agc(self):
        r=AgcRadio();r.regs[0x7e]=0x302e;r.setup(1)
        for _ in range(40):r.call('AM_fix_10ms',0)
        self.assertEqual(r.regs[0x13],0x3ff)
        self.assertEqual(r.regs[0x7e],0xb02e)
        high_index=r.index();r.rssi=300;r.call('AM_fix_10ms',0)
        self.assertLess(r.index(),high_index)
        self.assertEqual(r.regs[0x7e],0xb02e)

    def test_am_controller_does_not_change_gain_while_tx_or_power_save(self):
        for function in (1,5):
            r=AgcRadio();r.setup(1);r.reg_writes.clear()
            r.set8('gCurrentFunction',function);before=r.index()
            r.call('AM_fix_10ms',0)
            self.assertEqual(r.index(),before)
            self.assertEqual(r.reg_writes,[])

    def test_tx_preparation_then_am_rx_restores_software_control(self):
        r=AgcRadio();r.regs[0x7e]=0x302e;r.setup(1)
        r.call('BK4819_PrepareTransmit')
        self.assertEqual(r.regs[0x7e],0x302e)
        r.setup(1)
        self.assertEqual(r.regs[0x7e],0xb02e)

    def test_start_listening_keeps_am_fixed_and_fm_automatic(self):
        for mode,expected in ((1,0xb02e),(0,0x302e)):
            r=AgcRadio();r.regs[0x7e]=0x302e;r.setup(mode)
            r.call('APP_StartListening',2,1)
            self.assertEqual(r.regs[0x7e],expected)

    def test_spectrum_entry_uses_automatic_agc_and_exit_restores_am(self):
        r=AgcRadio();r.regs[0x7e]=0x302e;r.setup(1)
        r.stop_on_poll=True
        r.call('APP_RunSpectrum')
        self.assertEqual(r.regs[0x7e],0x302e)
        self.assertEqual(r.regs[0x7e]&0x8000,0)
        # Execute the existing Spectrum EXIT dispatch and register restore.
        r.set8('currentState',SL['SPECTRUM'])
        r.tap(13)
        self.assertEqual(r.regs[0x7e],0xb02e)

    def test_original_gain_controller_and_table_are_byte_identical_to_baseline(self):
        # SHA256 of the unchanged FAGCI/VFO0003 controller and gain table.
        self.assertEqual(hashlib.sha256((ROOT/'am_fix.c').read_bytes()).hexdigest(),
                         '53fddfd6b05c38546d165ca59c6608e24b83ccc7e9e5d5f8c1f932df174a1749')


if __name__=='__main__':unittest.main()

