# SPDX-License-Identifier: Apache-2.0
"""Compiled ARM profile save/reload tests; bus mocks do not model RF quality."""
import struct
import tempfile
import unittest
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
from test_channel_name import ROOT,SYMS,tool,CHANNEL_OFFSET
from test_am_hardware_agc import AgcRadio
from test_spectrum_save import L as SL
from test_vfo_save import L

with tempfile.TemporaryDirectory() as folder:
    p=Path(folder)
    (p/'layout.c').write_text('#include <stddef.h>\n#include "radio.h"\n'
        'const unsigned int a[] __attribute__((section(".test_layout"))) = {'
        'offsetof(VFO_Info_t,RxGain),offsetof(VFO_Info_t,RxIF),offsetof(VFO_Info_t,RxManual)};')
    tool('arm-none-eabi-gcc','-mcpu=cortex-m0','-fshort-enums','-I',ROOT,'-c',p/'layout.c','-o',p/'layout.o')
    tool('arm-none-eabi-objcopy','-O','binary','-j','.test_layout',p/'layout.o',p/'layout.bin')
    GAIN,IF,MANUAL=struct.unpack('<3I',(p/'layout.bin').read_bytes())


class ProfileRadio(AgcRadio):
    def __init__(self,active=0):
        super().__init__(active)
        for name in ('APP_CheckKeys','UART_IsCommandAvailable','GUI_DisplayScreen','UI_DisplayStatus'):
            self.uc.hook_add(UC_HOOK_CODE,self.skip_input,begin=SYMS[name],end=SYMS[name])

    def skip_input(self,uc,address,size,data):
        uc.reg_write(UC_ARM_REG_R0,0)
        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))

    def begin(self,manual=False,state=None):
        self.regs[0x13]=0x83a5;self.regs[0x3d]=0x2345
        self.configure(1,1,9)
        self.open_save(14552500,SL['STILL'] if state is None else state,tuned=14552500)
        if manual:self.tap(15)

    def restart(self,slot,active=0):
        r=ProfileRadio(active)
        r.eeprom=bytearray(self.eeprom);r.sync_attributes()
        r.uc.mem_write(SYMS['gEeprom']+L['ScreenChannel'],bytes([slot,slot]))
        r.call('RADIO_ConfigureChannel',active,2)
        return r

    def profile(self):
        ptr=self.vfo(self.active)
        return (struct.unpack('<H',self.uc.mem_read(ptr+GAIN,2))[0],
                struct.unpack('<H',self.uc.mem_read(ptr+IF,2))[0],
                self.uc.mem_read(ptr+MANUAL,1)[0])


class RxProfileTests(unittest.TestCase):
    def test_auto_is_default_and_manual_is_explicit_only_in_still(self):
        r=ProfileRadio();r.begin();self.assertEqual(r.get8('saveManual'),0)
        r.tap(15);self.assertEqual(r.get8('saveManual'),1)
        r.tap(15);self.assertEqual(r.get8('saveManual'),0)
        r=ProfileRadio();r.begin(state=SL['SPECTRUM']);r.tap(15)
        self.assertEqual(r.get8('saveManual'),0)

    def test_mode_switch_invalidates_confirmation_and_holding_f_does_not_toggle(self):
        r=ProfileRadio();r.begin();r.tap(10);r.tap(15)
        self.assertEqual(r.get8('saveConfirm'),0)
        r.hold(15);self.assertEqual(r.get8('saveManual'),1)
        self.assertEqual(r.writes,[])
        r.release();r.tap(10);self.assertEqual(r.writes,[])
        r.tap(10);self.assertTrue(r.writes)

    def test_manual_save_snapshots_registers_and_only_changes_target_eeprom_fields(self):
        for slot in range(200):
            r=ProfileRadio();r.mark(slot,0xc2)
            before=bytes(r.eeprom);r.begin(True);r.select(slot)
            r.regs[0x13]=0;r.regs[0x3d]=0 # captured settings must remain pinned
            r.confirm()
            expected=bytearray(before)
            expected[16*slot:16*slot+16]=struct.pack('<II8B',14552500,0,0,0,0,0x10,10,0,9,0)
            # TXP0007 keeps an existing destination RX-only marker.
            if before[slot*16+15] & 0xf0 == 0xa0:expected[slot*16+15] |= 0xa0
            expected[0xd60+slot]=0xc2
            expected[0xf50+16*slot+10:0xf50+16*slot+16]=struct.pack('<HHH',0x3a5,0x2345,0x5852)
            with self.subTest(slot=slot):self.assertEqual(r.eeprom,expected)

    def test_new_slot_profile_survives_name_clear_and_restart_both_vfos(self):
        r=ProfileRadio();r.begin(True);r.confirm()
        self.assertEqual(r.eeprom[0xf50:0xf5a],b'\0'*10)
        for active in (0,1):
            restarted=r.restart(0,active)
            self.assertEqual(restarted.profile(),(0x3a5,0x2345,1))

    def test_manual_am_keeps_gain_and_if_during_listening_and_timer_ticks(self):
        r=ProfileRadio();r.begin(True);r.confirm();r=r.restart(0)
        r.setup(1);self.assertEqual(r.regs[0x7e]&0xf000,0xb000)
        r.call('APP_StartListening',2,1)
        for _ in range(60):r.call('APP_TimeSlice10ms')
        self.assertEqual((r.regs[0x13],r.regs[0x3d]),(0x3a5,0x2345))

    def test_manual_fm_uses_fixed_gain_and_does_not_normalize_it_on_listening(self):
        r=ProfileRadio();r.begin(True);r.confirm();r=r.restart(0)
        r.setup(0);r.call('APP_StartListening',2,1)
        self.assertEqual(r.regs[0x7e]&0xf000,0xb000)
        self.assertEqual((r.regs[0x13],r.regs[0x3d]),(0x3a5,0x2345))

    def test_auto_overwrite_clears_previous_manual_marker_and_restores_am_control(self):
        r=ProfileRadio();r.begin(True);r.confirm()
        r.begin();r.select(0);r.confirm()
        self.assertEqual(r.eeprom[0xf5e:0xf60],b'\xff\xff')
        r=r.restart(0);self.assertEqual(r.profile()[2],0)
        r.setup(1)
        for _ in range(50):r.call('APP_TimeSlice10ms')
        self.assertEqual(r.regs[0x13],0x3ff)

    def test_invalid_marker_or_gain_is_ignored(self):
        for gain,marker in ((0x3a5,0xffff),(0x3a5,0),(0xffff,0x5852),(0x400,0x5852)):
            r=ProfileRadio();r.mark(0,0xc2)
            r.eeprom[:16]=struct.pack('<II8B',14552500,0,0,0,0,0x10,8,0,9,0)
            r.eeprom[0xf5a:0xf60]=struct.pack('<HHH',gain,0x2345,marker)
            r=r.restart(0);self.assertEqual(r.profile()[2],0)

    def test_switch_to_vfo_drops_manual_profile(self):
        r=ProfileRadio();r.begin(True);r.confirm();r=r.restart(0)
        r.uc.mem_write(SYMS['gEeprom']+L['ScreenChannel'],bytes([L['VFO_FIRST'],L['VFO_FIRST']]))
        r.call('RADIO_ConfigureChannel',0,2)
        self.assertEqual(r.profile()[2],0)
        r.setup(0);self.assertEqual(r.regs[0x7e]&0xf000,0x3000)

    def test_rename_preserves_profile(self):
        r=ProfileRadio();r.begin(True);r.confirm()
        profile=bytes(r.eeprom[0xf5a:0xf60])
        ptr=0x2000e000;r.uc.mem_write(ptr,b'RX PROFILE\0')
        r.call('SETTINGS_SaveChannelName',0,ptr)
        self.assertEqual(r.eeprom[0xf5a:0xf60],profile)

    def test_switching_manual_channel_to_auto_restores_default_if_before_listening(self):
        for mode in (0,1,2):
            r=ProfileRadio();r.begin(True);r.confirm();r=r.restart(0)
            r.setup(1)
            r.uc.mem_write(r.vfo(0)+MANUAL,b'\0')
            r.setup(mode)
            self.assertEqual(r.regs[0x3d],0 if mode==2 else 0x2aab)
            self.assertEqual(r.regs[0x13],0x3be)
            self.assertEqual(r.regs[0x7e]&0xf000,0xb000 if mode==1 else 0x3000)

    def test_regular_vfo_mem_ch_overwrite_clears_manual_profile(self):
        r=ProfileRadio();r.begin(True);r.confirm()
        self.assertEqual(r.uc.mem_read(r.vfo(0)+MANUAL,1),b'\0')
        r.call('SETTINGS_SaveChannel',0,0,r.vfo(0),2)
        self.assertEqual(r.eeprom[0xf5e:0xf60],b'\xff\xff')

    def test_cancel_manual_save_preserves_whole_eeprom(self):
        for confirm in (False,True):
            r=ProfileRadio();before=bytes(r.eeprom);r.begin(True)
            if confirm:r.tap(10)
            r.tap(13)
            self.assertEqual(r.eeprom,before)
            self.assertEqual(r.writes,[])

    def test_tx_uses_default_registers_then_rx_restores_profile(self):
        r=ProfileRadio();r.begin(True);r.confirm();r=r.restart(0)
        r.setup(1);r.call('RADIO_SetTxParameters')
        self.assertEqual((r.regs[0x13],r.regs[0x3d]),(0x3be,0x2aab))
        r.setup(1);r.call('APP_StartListening',2,1)
        self.assertEqual((r.regs[0x13],r.regs[0x3d]),(0x3a5,0x2345))

    def test_render_manual_save_menu(self):
        r=ProfileRadio();r.begin(True);r.call('SPECTRUM_Render')
        frame=bytes(r.uc.mem_read(SYMS['gFrameBuffer'],896))
        for i,char in enumerate(b'RX:MANUAL F:MODE'):
            glyph=bytes(r.uc.mem_read(SYMS['gFontSmall']+(char-32)*6,6))
            self.assertEqual(frame[4*128+8+7*i:4*128+14+7*i],glyph)
        r.tap(10);r.call('SPECTRUM_Render');self.assertEqual(r.writes,[])


class OptimizedStartupTests(unittest.TestCase):
    def test_vectors_retain_all_referenced_interrupt_handlers(self):
        import re
        source=(ROOT/'start.S').read_text()
        vector_source=source.split('.section .text.isr',1)[1].split('.section .text',1)[0]
        values=struct.unpack('<'+'I'*(len(re.findall(r'\.long\s',vector_source))),
            (ROOT/'firmware.bin').read_bytes()[:4*len(re.findall(r'\.long\s',vector_source))])
        for word,value in zip(re.findall(r'\.long\s+([^\r\n]+)',vector_source),values):
            if '+' in word:
                name=word.split('+')[0].strip()
                self.assertEqual(value,SYMS[name]|1)
            else:self.assertEqual(value,int(word,0))

    def test_data_init_and_bss_init_execute_after_linker_optimization(self):
        r=ProfileRadio();firmware=(ROOT/'firmware.bin').read_bytes()
        a,b=SYMS['sram_data_start'],SYMS['sram_data_end']
        r.uc.mem_write(a,b'\xaa'*(b-a));r.call('DATA_Init')
        self.assertEqual(bytes(r.uc.mem_read(a,b-a)),firmware[SYMS['flash_data_start']:SYMS['flash_data_start']+b-a])
        a,b=SYMS['__bss_start__'],SYMS['__bss_end__']
        r.uc.mem_write(a,b'\xaa'*(b-a));r.call('BSS_Init')
        self.assertEqual(bytes(r.uc.mem_read(a,b-a)),b'\0'*(b-a))


if __name__=='__main__':unittest.main()

