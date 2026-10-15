# SOS0005 - AMH0004 with repeated LED flashlight SOS

Experimental OSFW-SOS0005 build. Retains the AMH0004 AM hardware AGC integration, NAME editor, Spectrum saving and long-SK2 VFO saving.

The configured flashlight key cycles through steady ON, repeated SOS, and OFF with short presses. SOS is three dots, three dashes, three dots, followed by a repeat gap. Nominal Morse unit: 160 ms; dot 160 ms; dash 480 ms; inter-element gap 160 ms; inter-letter gap 480 ms; repeat gap 1120 ms. Full nominal cycle: 5.44 seconds. Actual timing can vary with firmware activity. Reactivating SOS starts from the first dot.

The implementation uses the existing application scheduler without adding blocking delays. Like the previous blinking mode, it pauses in the separate Spectrum loop and resumes on exit. RX/TX status LEDs are unchanged.

Choose raw or packed firmware according to your loader. Keep your own configuration/calibration backups; no reset is required. After flashing, verify OSFW-SOS0005 and steady/SOS/OFF operation on the normal screen. AM AGC tuning is identical to AMH0004 and still awaits RF/audio field comparison.

Built using ARM GCC 16.1.0. Raw firmware: 61,404 bytes of the 61,440-byte limit, leaving 36 bytes. Packed: 61,422 bytes. All 53 ARM-emulation tests passed (47 existing plus six SOS tests), including actual GPIO waveform, timing and AM-fix operation. Peripherals are simulated; physical-radio validation is pending. This build has not been published on GitHub.
