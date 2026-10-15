"""Compiled menu dispatch, EEPROM writes and CHIRP interoperability; no RF."""
import struct
import unittest
from test_firmware_interop import ProfileRadio
from test_tx_inhibit import TX_INHIBIT,inhibit
from test_channel_name import SYMS,CHANNEL_OFFSET,KEY_MENU,KEY_DOWN,KEY_EXIT
from test_vfo_save import L
from test_driver import image,radio,extra

TX_MENU=50


class TxMenuTests(unittest.TestCase):
    def saved(self,slot=24,active=0,blocked=False):
        arm=ProfileRadio(active)
        arm.eeprom=bytearray(image(slot=slot))
        if blocked:arm.eeprom[slot*16+15]=0xa7
        return arm.restart(slot,active)

    def menu(self,arm):
        arm.set8('gScreenToDisplay',2)
        arm.set8('gMenuListCount',51)
        arm.set8('gMenuCursor',TX_MENU)
        arm.set8('gIsInSubMenu',0)
        arm.set8('gFlagAcceptSetting',0)
        arm.set8('gFlagRefreshSetting',0)
        arm.set8('gInputBoxIndex',0)
        arm.call('MENU_ShowCurrentSetting')

    def selection(self,arm):return struct.unpack('<I',arm.uc.mem_read(SYMS['gSubMenuSelection'],4))[0]

    def test_all_200_slots_only_change_flag_and_chirp_decodes_it(self):
        for slot in range(200):
            arm=self.saved(slot,slot%2)
            before=bytes(arm.eeprom)
            self.assertEqual(arm.call('SETTINGS_SetChannelTxEnabled',slot,0),1)
            expected=bytearray(before);expected[slot*16+15]=0xa7
            self.assertEqual(arm.eeprom,expected)
            self.assertEqual(arm.writes,[(slot*16+8,bytes(expected[slot*16+8:slot*16+16]))])
            mem=radio(bytes(arm.eeprom)).get_memory(slot+1)
            self.assertEqual(mem.duplex,'off')
            self.assertEqual(str(extra(mem,'rxmode').value),'MANUAL')
            self.assertEqual(arm.call('SETTINGS_SetChannelTxEnabled',slot,1),1)
            self.assertEqual(arm.eeprom,before)

    def test_normal_menu_direct_number_51_then_save_and_restart(self):
        arm=self.saved();self.menu(arm)
        arm.set8('gMenuCursor',0)
        arm.key(5);arm.key(1);arm.finish()
        self.assertEqual(arm.get8('gMenuCursor'),50)
        self.assertEqual(self.selection(arm),1)
        arm.key(KEY_MENU);arm.key(KEY_DOWN)
        self.assertEqual(self.selection(arm),0)
        self.assertEqual(arm.writes,[])
        arm.key(KEY_MENU);arm.finish()
        self.assertEqual(inhibit(arm),1)
        restarted=arm.restart(24)
        self.assertEqual(inhibit(restarted),1)
        self.menu(restarted)
        self.assertEqual(self.selection(restarted),0)

    def test_exit_cancels_without_any_eeprom_or_rx_register_change(self):
        for blocked in (False,True):
            arm=self.saved(blocked=blocked);self.menu(arm)
            before=bytes(arm.eeprom)
            arm.key(KEY_MENU);arm.key(KEY_DOWN);arm.key(KEY_EXIT);arm.finish()
            self.assertEqual(arm.eeprom,before)
            self.assertEqual(arm.writes,[])
            self.assertEqual(arm.reg_writes,[])
            self.assertEqual(self.selection(arm),int(not blocked))

    def test_both_vfo_caches_updated_immediately_and_global_off_retained(self):
        arm=self.saved()
        arm.call('RADIO_ConfigureChannel',1,2)
        arm.set8('gSetting_ALL_TX',2)
        arm.call('SETTINGS_SetChannelTxEnabled',24,0)
        self.assertEqual([arm.uc.mem_read(arm.vfo(i)+TX_INHIBIT,1)[0] for i in (0,1)],[1,1])
        arm.call('SETTINGS_SetChannelTxEnabled',24,1)
        self.assertEqual([arm.uc.mem_read(arm.vfo(i)+TX_INHIBIT,1)[0] for i in (0,1)],[0,0])
        self.assertEqual(arm.get8('gSetting_ALL_TX'),2)
        self.assertEqual(arm.call('FREQUENCY_Check',arm.vfo(0)),0)

    def test_unchanged_choice_avoids_eeprom_wear(self):
        for blocked in (False,True):
            arm=self.saved(blocked=blocked);self.menu(arm)
            arm.key(KEY_MENU);arm.key(KEY_MENU);arm.finish()
            self.assertEqual(arm.writes,[])

    def test_vfo_noaa_empty_and_invalid_slots_reject_writes(self):
        arm=self.saved();before=bytes(arm.eeprom)
        for slot in (0,199,200,206,207,255):
            self.assertEqual(arm.call('SETTINGS_SetChannelTxEnabled',slot,0),0)
        for slot in (0,199,200,206,207,255):
            arm.uc.mem_write(arm.vfo(0)+CHANNEL_OFFSET,bytes([slot]))
            self.menu(arm);arm.key(KEY_MENU)
            self.assertEqual(arm.get8('gMenuTxChannel'),255)
            self.assertEqual(arm.get8('gIsInSubMenu'),0)
        self.assertEqual(arm.eeprom,before)
        self.assertEqual(arm.writes,[])

    def test_channel_is_pinned_when_other_vfo_becomes_current(self):
        arm=self.saved();self.menu(arm);arm.key(KEY_MENU);arm.key(KEY_DOWN)
        arm.uc.mem_write(arm.vfo(1)+CHANNEL_OFFSET,b'\x25')
        arm.uc.mem_write(SYMS['gTxVfo'],struct.pack('<I',arm.vfo(1)))
        before=bytes(arm.eeprom)
        arm.key(KEY_MENU);arm.finish()
        expected=bytearray(before);expected[24*16+15]=0xa7
        self.assertEqual(arm.eeprom,expected)
        self.assertEqual(arm.uc.mem_read(arm.vfo(0)+TX_INHIBIT,1),b'\x01')
        self.assertEqual(arm.uc.mem_read(arm.vfo(1)+TX_INHIBIT,1),b'\0')

    def test_ptt_side_keys_f_and_held_menu_do_not_commit(self):
        arm=self.saved();self.menu(arm);arm.key(KEY_MENU);arm.key(KEY_DOWN)
        for key in (21,20,22,15):arm.key(key)
        for _ in range(5):arm.key(KEY_MENU,1,1)
        self.assertEqual(arm.get8('gIsInSubMenu'),1)
        self.assertEqual(arm.get8('gFlagAcceptSetting'),0)
        self.assertEqual(arm.writes,[])
        self.assertEqual(inhibit(arm),0)

    def test_chirp_enable_then_radio_menu_reports_enabled(self):
        arm=self.saved(blocked=True)
        driver=radio(bytes(arm.eeprom));mem=driver.get_memory(25)
        extra(mem,'txenabled').value=True;driver.set_memory(mem)
        arm.eeprom=bytearray(driver.get_mmap().get_packed());arm=arm.restart(24)
        self.menu(arm)
        self.assertEqual(self.selection(arm),1)

    def test_corrupt_scramble_values_keep_firmware_effective_default(self):
        for value in (0xff,0x17,0xaf):
            arm=self.saved();arm.eeprom[24*16+15]=value
            arm.call('SETTINGS_SetChannelTxEnabled',24,0)
            self.assertEqual(arm.eeprom[24*16+15],0xa0)

    def test_ui_shows_target_and_global_off_and_vfo_mr_only(self):
        arm=self.saved();self.menu(arm);arm.set8('gSetting_ALL_TX',2)
        arm.call('UI_DisplayMenu')
        frame=bytes(arm.uc.mem_read(SYMS['gFrameBuffer'],896))
        for page,text in ((0,b'CH-025'),(4,b'GLOBAL OFF')):
            for i,c in enumerate(text):
                glyph=bytes(arm.uc.mem_read(SYMS['gFontSmall']+(c-32)*6,6))
                start=page*128+58+i*7
                self.assertEqual(frame[start:start+6],glyph)
        arm.uc.mem_write(arm.vfo(0)+CHANNEL_OFFSET,bytes([L['VFO_FIRST']]))
        self.menu(arm);arm.call('UI_DisplayMenu')
        frame=bytes(arm.uc.mem_read(SYMS['gFrameBuffer'],896))
        for i,c in enumerate(b'MR ONLY'):
            glyph=bytes(arm.uc.mem_read(SYMS['gFontSmall']+(c-32)*6,6))
            self.assertEqual(frame[2*128+58+i*7:2*128+64+i*7],glyph)


if __name__=='__main__':unittest.main(verbosity=2)
