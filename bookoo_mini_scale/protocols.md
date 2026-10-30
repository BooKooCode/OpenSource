# MINI SCALE Transmission protocol
- Contact Us: develop@bookoocoffee.com
- Last Update: October 30, 2026

>All BLE UUIDs adopted by the BOOKOO MINI SCALE use a simplified representation of the 16-bit UUID, and its corresponding 128-bit UUID is the unified structure agreed upon by the Bluetooth Association, i.e. 0000 xxxx -0000-1000-8000-00805F9B34FB

## 1. Bluetooth Protocol Basic Info And Check Sum
> All data are transferred in hexadecimal

### Basic Info

Service UUID: 0x0FFE

Characteristic UUID:

- Command Characteristic UUID: 0xFF12
- Weight Data Characteristic UUID: 0xFF11

### Check Sum Method

Method: XOR Calculation
```
CheckSum = Header1 ^ Header2 ^ Data1 ^ Data2 ^ ... ^ DataN

if CheckSum == DataSUM
    pass
```

# 2. Transmission Data

### Command Data

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | DESCRIPTION | NOTE |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER<br>(Header&nbsp;1) | TYPE<br>(Header&nbsp;2) | DATA1 | DATA2 | DATA3 | DATASUM | DESCRIPTION | NOTE |
| 03 | 0A | 01 | 00 | 00 | checkSum | Send the tare command | Release V1.0.0-V1.0.1: only effective in weight-mode or timing-mode. From release V1.0.2: also effective in automatic ready. All these versions: ignored during automatic running, automatic done, or calibration. |
| 03 | 0A | 02 | 00 | 00~05 (Beep level) | checkSum | Adjust the beep volume; 00 means mute | Available from release V1.0.0. No working-mode restriction. Values above 05 are clamped to 05. The setting is saved. |
| 03 | 0A | 03 | 00 | 05~1e (Auto-off duration) | checkSum | Adjust the automatic shutdown duration from 5-30 minutes | |
| 03 | 0A | 04 | 00 | 00 | checkSum | Send the start timer command | Only effective in timing-mode when the timer is reset. Does not resume a stopped timer or start automatic-mode extraction. |
| 03 | 0A | 05 | 00 | 00 | checkSum | Send the stop timer command | From release V1.0.0: in timing-mode, only effective while the timer is running. From release V1.0.2: also ends extraction and enters automatic done during automatic running; V1.0.0-V1.0.1 do not support this automatic-mode action. |
| 03 | 0A | 06 | 00 | 00 | checkSum | Send the reset timer command | Available from release V1.0.0. Only effective in timing-mode when the timer is stopped. Ignored while the timer is running and in automatic-mode. |
| 03 | 0A | 07 | 00 | 00 | checkSum | Send the tare and start time command (recommend) | From release V1.0.0: in weight-mode, tares without starting the timer; in timing-mode, tares, resets the timer and starts it. From release V1.0.2: also starts extraction in automatic ready; V1.0.0-V1.0.1 do not support this automatic-mode action. All these versions: ignored during automatic running, automatic done, or calibration. |
| 03 | 0A | 08 | 00/01 | 00 | checkSum | Set flow rate smoothing: 00 = off, 01 = on | Available from release V1.0.0. No working-mode restriction. The setting is saved. |
| 03 | 0A | 11 | 00 | 00 | checkSum | Send the shutdown command | <mark><strong><em>Available in public release V1.4.2 and later. Not supported in public release V1.4.1 or earlier, or beta V1.5.0.0806.</em></strong></mark> Requests sleep while the BLE connection is active; BLE disconnects as the scale enters sleep. BYTE4 and BYTE5 must both be 00; otherwise the command is rejected. |
| 03 | 0A | 12 | 00 | 00 | checkSum | Reset the automatic shutdown countdown | <mark><strong><em>Available in public release V1.4.2 and later. Not supported in public release V1.4.1 or earlier, or beta V1.5.0.0806.</em></strong></mark> BYTE4 and BYTE5 must both be 00; otherwise the command is rejected. The countdown is reset on the next standby check in weight-mode, timing-mode, or automatic-mode (ready, running, or done). This command does not change the configured automatic shutdown duration. Send it in advance and periodically to keep the scale awake, rather than waiting until the last packet before automatic shutdown. |

### Receiving Weight

>Note: The current weight unit only supports grams

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 |  DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0B | <br>MillSeconds <br><br><br> High byte of an unsigned 24-bit integer |MillSeconds <br><br><br> Mid byte of an unsigned 24-bit integer |MillSeconds <br><br><br> Low byte of an unsigned 24-bit integer | unit of weight |Weight symbol data points (+/-)|<br>Grams weight * 100 <br><br><br> High byte of an unsigned 24-bit integer |<br>Grams weight * 100 <br><br><br> Mid byte of an unsigned 24-bit integer |<br>Grams weight * 100 <br><br><br> Low byte of an unsigned 24-bit integer |Flow rate symbol data points (+/-)|Flow rate*100 <br><br><br> High byte of an unsigned Short integer|Flow rate*100 <br><br><br> Low byte of an unsigned Short integer|Percentage of remaining power | standby time (min * 10) <br><br><br> High byte of an unsigned Short integer |standby time (min * 10) <br><br><br> Low byte of an unsigned Short integer| Buzzer gear | Flow Rate Smoothing Switch |Reserved |checkSum | Get time, weight, flow rate and power percentage data on the scale |

### Other Data

It is currently not open, so contact us if you need it.

Email: develop@bookoocoffee.com
