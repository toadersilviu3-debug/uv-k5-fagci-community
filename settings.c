/* Modified 2026-10-14 for TXP0007: persistent per-memory TX inhibition. */
/* Copyright 2023 Dual Tachyon
 * https://github.com/DualTachyon
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 *     Unless required by applicable law or agreed to in writing, software
 *     distributed under the License is distributed on an "AS IS" BASIS,
 *     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *     See the License for the specific language governing permissions and
 *     limitations under the License.
 */
/* Modified 2026-10-14, RXP0006: RX profiles or LTO/test call boundaries.
 * Original authors/licenses retained. See CHANGELOG.md.
 */

/* Modified 2026-10-13 in the independent SPC0002 community fork.
 * Added name-only EEPROM persistence preserving six reserved slot bytes.
 * Original copyright/license notices are retained. See CHANGELOG.md.
 */


#include <string.h>
#if defined(ENABLE_FMRADIO)
#include "app/fm.h"
#endif
#include "driver/eeprom.h"
#if defined(ENABLE_UART)
#include "driver/uart.h"
#endif
#include "misc.h"
#include "settings.h"

EEPROM_Config_t gEeprom;

#if defined(ENABLE_FMRADIO)
void SETTINGS_SaveFM(void)
{
	uint8_t i;
	struct {
		uint16_t Frequency;
		uint8_t Channel;
		bool IsChannelSelected;
		uint8_t Padding[4];
	} State;

#if defined(ENABLE_UART)
	UART_LogSend("sFm\r\n", 5);
#endif

	memset(&State, 0xFF, sizeof(State));
	State.Channel = gEeprom.FM_SelectedChannel;
	State.Frequency = gEeprom.FM_SelectedFrequency;
	State.IsChannelSelected = gEeprom.FM_IsMrMode;

	EEPROM_WriteBuffer(0x0E88, &State);
	for (i = 0; i < 5; i++) {
		EEPROM_WriteBuffer(0x0E40 + (i * 8), &gFM_Channels[i * 4]);
	}
}
#endif

void SETTINGS_SaveVfoIndices(void)
{
	uint8_t State[8];

#if defined(ENABLE_UART)
	UART_LogSend("sidx\r\n", 6);
#endif

	State[0] = gEeprom.ScreenChannel[0];
	State[1] = gEeprom.MrChannel[0];
	State[2] = gEeprom.FreqChannel[0];
	State[3] = gEeprom.ScreenChannel[1];
	State[4] = gEeprom.MrChannel[1];
	State[5] = gEeprom.FreqChannel[1];
	State[6] = gEeprom.NoaaChannel[0];
	State[7] = gEeprom.NoaaChannel[1];

	EEPROM_WriteBuffer(0x0E80, State);
}

void SETTINGS_SaveSettings(void)
{
	uint8_t State[8];
	uint32_t Password[2];

#if defined(ENABLE_UART)
	UART_LogSend("spub\r\n", 6);
#endif

	State[0] = gEeprom.CHAN_1_CALL;
	State[1] = gEeprom.SQUELCH_LEVEL;
	State[2] = gEeprom.TX_TIMEOUT_TIMER;
	State[3] = gEeprom.NOAA_AUTO_SCAN;
	State[4] = gEeprom.KEY_LOCK;
	State[5] = gEeprom.VOX_SWITCH;
	State[6] = gEeprom.VOX_LEVEL;
	State[7] = gEeprom.MIC_SENSITIVITY;

	EEPROM_WriteBuffer(0x0E70, State);

	State[0] = 0xFF;
	State[1] = gEeprom.CHANNEL_DISPLAY_MODE;
	State[2] = gEeprom.CROSS_BAND_RX_TX;
	State[3] = gEeprom.BATTERY_SAVE;
	State[4] = gEeprom.DUAL_WATCH;
	State[5] = gEeprom.BACKLIGHT;
	State[6] = gEeprom.TAIL_NOTE_ELIMINATION;
	State[7] = gEeprom.VFO_OPEN;

	EEPROM_WriteBuffer(0x0E78, State);

	State[0] = gEeprom.BEEP_CONTROL;
	State[1] = gEeprom.KEY_1_SHORT_PRESS_ACTION;
	State[2] = gEeprom.KEY_1_LONG_PRESS_ACTION;
	State[3] = gEeprom.KEY_2_SHORT_PRESS_ACTION;
	State[4] = gEeprom.KEY_2_LONG_PRESS_ACTION;
	State[5] = gEeprom.SCAN_RESUME_MODE;
	State[6] = gEeprom.AUTO_KEYPAD_LOCK;
	State[7] = gEeprom.POWER_ON_DISPLAY_MODE;

	EEPROM_WriteBuffer(0x0E90, State);

	memset(Password, 0xFF, sizeof(Password));

	Password[0] = gEeprom.POWER_ON_PASSWORD;

	EEPROM_WriteBuffer(0x0E98, State);

	memset(State, 0xFF, sizeof(State));

	State[0] = gEeprom.VOICE_PROMPT;

	EEPROM_WriteBuffer(0x0EA0, State);

	State[0] = 0xFF;
	State[1] = gEeprom.ROGER;
	State[2] = gEeprom.REPEATER_TAIL_TONE_ELIMINATION;
	State[3] = gEeprom.TX_CHANNEL;

	EEPROM_WriteBuffer(0x0EA8, State);

	State[0] = gEeprom.DTMF_SIDE_TONE;
	State[1] = gEeprom.DTMF_SEPARATE_CODE;
	State[2] = gEeprom.DTMF_GROUP_CALL_CODE;
	State[3] = gEeprom.DTMF_DECODE_RESPONSE;
	State[4] = gEeprom.DTMF_AUTO_RESET_TIME;
	State[5] = gEeprom.DTMF_PRELOAD_TIME / 10U;
	State[6] = gEeprom.DTMF_FIRST_CODE_PERSIST_TIME / 10U;
	State[7] = gEeprom.DTMF_HASH_CODE_PERSIST_TIME / 10U;

	EEPROM_WriteBuffer(0x0ED0, State);

	memset(State, 0xFF, sizeof(State));

	State[0] = gEeprom.DTMF_CODE_PERSIST_TIME / 10U;
	State[1] = gEeprom.DTMF_CODE_INTERVAL_TIME / 10U;
	State[2] = gEeprom.PERMIT_REMOTE_KILL;

	EEPROM_WriteBuffer(0x0ED8, State);

	State[0] = gEeprom.SCAN_LIST_DEFAULT;
	State[1] = gEeprom.SCAN_LIST_ENABLED[0];
	State[2] = gEeprom.SCANLIST_PRIORITY_CH1[0];
	State[3] = gEeprom.SCANLIST_PRIORITY_CH2[0];
	State[4] = gEeprom.SCAN_LIST_ENABLED[1];
	State[5] = gEeprom.SCANLIST_PRIORITY_CH1[1];
	State[6] = gEeprom.SCANLIST_PRIORITY_CH2[1];
	State[7] = 0xFF;

	EEPROM_WriteBuffer(0x0F18, State);

	memset(State, 0xFF, sizeof(State));

	State[0] = gSetting_F_LOCK;
	State[1] = gSetting_350TX;
	State[2] = false;
	State[3] = gSetting_200TX;
	State[4] = gSetting_500TX;
	State[5] = gSetting_ALL_TX;
	State[6] = gSetting_ScrambleEnable;

	EEPROM_WriteBuffer(0x0F40, State);
}

// Rename only: preserve channel parameters and the six reserved slot bytes.
__attribute__((noinline)) bool SETTINGS_SaveChannelName(uint8_t Channel, const char *Name)
{
	uint8_t Slot[16], Original[16];
	uint8_t Length = 10;
	if (!IS_MR_CHANNEL(Channel) || !RADIO_CheckValidChannel(Channel, false, 0))
		return false;
	const uint16_t Address = 0x0F50 + Channel * 16;
	EEPROM_ReadBuffer(Address, Slot, sizeof(Slot));
	memcpy(Original, Slot, sizeof(Slot));
	while (Length && Name[Length - 1] == ' ')
		Length--;
	memset(Slot, 0, 10);
	memcpy(Slot, Name, Length);
	for (uint8_t Offset = 0; Offset < 16; Offset += 8) {
		if (memcmp(Slot + Offset, Original + Offset, 8))
			EEPROM_WriteBuffer(Address + Offset, Slot + Offset);
	}
	// Both VFOs may refer to the same memory channel.
	for (uint8_t VFO = 0; VFO < 2; VFO++) {
		VFO_Info_t *Info = &gEeprom.VfoInfo[VFO];
		if (Info->CHANNEL_SAVE == Channel) {
			memset(Info->Name, 0, sizeof(Info->Name));
			memcpy(Info->Name, Slot, 10);
		}
	}
	return true;
}

// Modified 2026-10-14, TXM0008: update only the existing TX flag byte.
__attribute__((noinline)) bool SETTINGS_SetChannelTxEnabled(uint8_t Channel, bool Enabled) {
  if (!IS_MR_CHANNEL(Channel) || !RADIO_CheckValidChannel(Channel, false, 0))
    return false;
  uint8_t block[8];
  const uint16_t address = Channel * 16 + 8;
  EEPROM_ReadBuffer(address, block, sizeof(block));
  uint8_t scramble = block[7];
  if ((scramble & 0xF0) == 0xA0) scramble &= 0x0F;
  if (scramble > 10) scramble = 0;
  const uint8_t value = scramble | (Enabled ? 0 : 0xA0);
  if (block[7] != value) {
    block[7] = value;
    EEPROM_WriteBuffer(address, block);
  }
  for (uint8_t vfo = 0; vfo < 2; vfo++)
    if (gEeprom.VfoInfo[vfo].CHANNEL_SAVE == Channel)
      gEeprom.VfoInfo[vfo].TxInhibit = !Enabled;
  return true;
}

// RXP0006: the six bytes after the ten-character name hold an optional
// RX-only profile: gain (10 bits), IF (16 bits), and marker bytes 52 58.
static void SETTINGS_SaveRxProfile(uint8_t Channel, const VFO_Info_t *pVFO) {
  uint16_t slot[4];
  const uint16_t address = 0x0F58 + Channel * 16;
  EEPROM_ReadBuffer(address, slot, 8);
  if (pVFO->RxManual) {
    slot[1] = pVFO->RxGain & 0x03FF;
    slot[2] = pVFO->RxIF;
    slot[3] = 0x5852;
  } else {
    if (slot[3] != 0x5852)
      return;
    slot[3] = 0xFFFF;
  }
  EEPROM_WriteBuffer(address, slot);
}

__attribute__((noinline)) void SETTINGS_SaveChannel(uint8_t Channel, uint8_t VFO, const VFO_Info_t *pVFO, uint8_t Mode)
{
#if defined(ENABLE_UART)
	UART_LogSend("schn\r\n", 6);
#endif

	if (IS_NOT_NOAA_CHANNEL(Channel)) {
		uint16_t OffsetMR;
		uint16_t OffsetVFO;

		OffsetMR = 0x0000 + (Channel * 16);
		OffsetVFO = OffsetMR;
		if (!IS_MR_CHANNEL(Channel)) {
			if (VFO == 0) {
				OffsetVFO = 0x0C80 + ((Channel - FREQ_CHANNEL_FIRST) * 32);
			} else {
				OffsetVFO = 0x0C90 + ((Channel - FREQ_CHANNEL_FIRST) * 32);
			}
		}

		if (Mode == 2 || !IS_MR_CHANNEL(Channel)) {
			uint32_t State32[2];
			uint8_t State8[8];

			State32[0] = pVFO->ConfigRX.Frequency;
			State32[1] = pVFO->FREQUENCY_OF_DEVIATION;

			EEPROM_WriteBuffer(OffsetVFO + 0, State32);

			State8[0] = pVFO->ConfigRX.Code;
			State8[1] = pVFO->ConfigTX.Code;
			State8[2] = (pVFO->ConfigTX.CodeType << 4) | pVFO->ConfigRX.CodeType;
			State8[3] = (pVFO->AM_CHANNEL_MODE << 4) | pVFO->FREQUENCY_DEVIATION_SETTING;
			State8[4] = 0
				| (pVFO->BUSY_CHANNEL_LOCK << 4)
				| (pVFO->OUTPUT_POWER << 2)
				| (pVFO->CHANNEL_BANDWIDTH << 1)
				| (pVFO->FrequencyReverse << 0)
				;
			State8[5] = (pVFO->DTMF_PTT_ID_TX_MODE << 1) | pVFO->DTMF_DECODING_ENABLE;
			State8[6] = pVFO->STEP_SETTING;
            bool inhibit = false;
            if (IS_MR_CHANNEL(Channel)) {
                uint8_t previous[8];
                EEPROM_ReadBuffer(OffsetMR + 8, previous, 8);
                // Saving from Spectrum/VFO must not silently unlock a slot.
                // Explicit CHIRP TX enable clears the EEPROM marker directly.
                inhibit = pVFO->TxInhibit ||
                    ((gMR_ChannelAttributes[Channel] & MR_CH_BAND_MASK) < 7 &&
                     (previous[7] & 0xF0) == 0xA0);
            }
			State8[7] = pVFO->SCRAMBLING_TYPE | (inhibit ? 0xA0 : 0);

			EEPROM_WriteBuffer(OffsetVFO + 8, State8);

			SETTINGS_UpdateChannel(Channel, pVFO, true);

			if (IS_MR_CHANNEL(Channel)) {
                SETTINGS_SaveRxProfile(Channel, pVFO);
#ifndef ENABLE_KEEPNAMEONSAVE					
				memset(&State32, 0xFF, sizeof(State32));
				EEPROM_WriteBuffer(OffsetMR + 0x0F50, State32);
				EEPROM_WriteBuffer(OffsetMR + 0x0F58, State32);
#else				  
				if (Mode >= 3) {	// save the channel name - source OneOfEleven
					memmove(State8, pVFO->Name + 0, 8);
					EEPROM_WriteBuffer(0x0F50 + OffsetMR, State8);
					memset(State8, 0xFF, sizeof(State8));
					memmove(State8, pVFO->Name + 8, 2);
					EEPROM_WriteBuffer(0x0F58 + OffsetMR, State8);
				}
#endif													 
			}
		}
	}
}

void SETTINGS_UpdateChannel(uint8_t Channel, const VFO_Info_t *pVFO, bool bUpdate)
{
#if defined(ENABLE_UART)
	UART_LogSend("svalid\r\n", 8);
#endif

	if (IS_NOT_NOAA_CHANNEL(Channel)) {
		uint8_t State[8];
		uint16_t Offset;
		uint8_t Attributes;

		Offset = 0x0D60 + (Channel & ~7U);
		EEPROM_ReadBuffer(Offset, State, sizeof(State));
		if (bUpdate) {
			Attributes = 0
				| (pVFO->SCANLIST1_PARTICIPATION << 7)
				| (pVFO->SCANLIST2_PARTICIPATION << 6)
				| (pVFO->Band << 0);
			if (State[Channel & 7U] == Attributes) {
				return;
			}
		} else {
			Attributes = 0xFF;
		}
		State[Channel & 7U] = Attributes;
		EEPROM_WriteBuffer(Offset, State);
		gMR_ChannelAttributes[Channel] = Attributes;
	}
}

