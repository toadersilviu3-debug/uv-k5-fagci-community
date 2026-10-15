# AMH0004 - experimental AM hardware AGC integration test

Based on VFO0003, retaining NAME, Spectrum saving and long-SK2 VFO saving. Not yet field-validated or published on GitHub.

Normal AM RX setup now selects BK4819 fixed gain-table slot 3 (REG_13), setting REG_7E bit 15 while preserving bits 11:0. The unchanged FAGCI software AM-fix controller can then control gain without automatic hardware table selection competing with it. Other modulation modes restore automatic hardware AGC.

Spectrum temporarily uses automatic hardware AGC because this FAGCI Spectrum loop does not run AM-fix. Existing Spectrum exit restores the saved register mode. This is not a software AM-fix implementation for Spectrum.

The original FAGCI gain table, RSSI target, hysteresis and hold/recovery algorithm are byte-identical to VFO0003. No Egzumer gain table was ported. The fixed-AGC integration principle was identified in Egzumer 0.22; all original credits/licenses remain.

Test normal channel/VFO AM reception on a known airband frequency. Use the same antenna, position, bandwidth and volume for both builds. Temporarily set SQL=0, DW=OFF and SAVE=OFF to isolate AGC from squelch/dual-watch/power-saving effects. Compare intelligibility of weak transmissions, distortion on stronger signals, volume pumping and recovery after a strong signal. Check switching back to FM and leaving Spectrum. AERO transmission is not needed for this test.

Keep the radio's own configuration/calibration backups. Use the raw or packed image required by your loader; no reset is required. Roll back to VFO0003 if behavior worsens. Aircraft signals vary, and louder audio or changed RSSI is not proof of improved RF sensitivity.

All 47 ARM-emulation tests passed, including nine AGC integration tests. Simulated peripherals verify register behavior, not measured RF/audio performance. Raw firmware: 61,324 bytes of the 61,440-byte flash limit (116 bytes remaining). Built with ARM GCC 16.1.0.
