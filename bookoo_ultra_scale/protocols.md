# ULTRA SCALE Transmission protocol
- Contact Us: develop@bookoocoffee.com
- Last Update: September 3, 2026

>All BLE UUIDs adopted by the BOOKOO ULTRA SCALE use a simplified representation of the 16-bit UUID, and its corresponding 128-bit UUID is the unified structure agreed upon by the Bluetooth Association, i.e. 0000 xxxx -0000-1000-8000-00805F9B34FB

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
| PRODUCT NUMBER<br>(Header&nbsp;1) | TYPE<br>(Header&nbsp;2) | DATA1 | DATA2 | DATA3 |  DATASUM |DESCRIPTION |
| 03 | 0A | 01 | 00 | 00 | checkSum | Send the tare command | Not valid during automatic mode operation. |
| 03 | 0A | 02 | 00 | 00~03 (Beep level) | checkSum | Adjust the beep volume, 00 means mute, and 01-03 indicate low, medium, and high volume levels | <mark><strong><em>For release firmware V4.0.0 and later, the valid range is 00-03.</em></strong></mark> |
| 03 | 0A | 03 | 00 | 05~1e (Auto-off duration) | checkSum | Adjust the automatic shutdown duration from 5-30 minutes | |
| 03 | 0A | 04 | 00 | 00 | checkSum | Send the start timer command | Only effective in timing-mode and ratio-mode. |
| 03 | 0A | 05 | 00 | 00 | checkSum | Send the stop timer command | Only effective in timing-mode and ratio-mode. |
| 03 | 0A | 06 | 00 | 00 | checkSum | Send the reset timer command | Only effective in timing-mode and ratio-mode. |
| 03 | 0A | 07 | 00 | 00 | checkSum | Send the tare and start time command (recommend) |  |
| 03 | 0A | 08 | 00/01 | 00 | checkSum | Whether or not flow smoothing is turned on, 00 means it is not turned on, 01 means it is turned on | |
| 03 | 0A | 09 | 00 | 00 | checkSum | Send the calibration command. | Only effective in weight-mode |
| 03 | 0A | 0B | 00/01 (Stop condition) | 00 | checkSum | Set the stop condition for automatic-mode: 00 = liquid flow stopping, 01 = container being removed. | <mark><strong><em>V3.1.2 and below: BYTE4 is the stopping condition; BYTE5 must be 00. Target mode not selected. Example: 03 0A 0B 00 00 02 Set liquid flow to stop. Do not use this format in version V4.0.0.</em></strong></mark> |
| 03 | 0A | 0B | 01/02 (Target mode) | 00/01/02 (Stop condition) | checkSum | Set the automatic stop condition separately for each mode. Target mode: 01 = timing-mode, 02 = ratio-mode. Stop condition: 00 = liquid flow stopping, 01 = filter being removed, 02 = server being removed. | <mark><strong><em>V4.0.0 (400) and later: BYTE4 selects the target mode; BYTE5 selects the stop condition for its automatic submode. Example: 03 0A 0B 01 00 03 sets liquid-flow stopping for timing-mode; use 03 0A 0B 02 00 00 for ratio-mode. To configure both modes, send one command for each. The 311 and 400 parameter formats are not interchangeable.</em></strong></mark> |
| 03 | 0A | 0D | Powder weight * 10<br>High byte | Powder weight * 10<br>Low byte | checkSum | Set the powder weight | Unit: gram, valid range: 0.1-999.0 g. <mark><strong><em>Available in beta firmware V3.2.4 and later, or release firmware V4.0.0 and later.</em></strong></mark> |
| 03 | 0A | 15 | 00 | 00 | checkSum | Send the shutdown command | <mark><strong><em>Available in release firmware V4.0.0 and later.</em></strong></mark> Not valid while charging. |
| 03 | 0A | 25 | 00 | 00 | checkSum | Reset the automatic shutdown countdown | <mark><strong><em>Available in release firmware V4.0.1 and later.</em></strong></mark> It is recommended to send this command in advance and periodically to keep the scale awake, rather than waiting until the last packet before automatic shutdown. This command does not change the configured automatic shutdown duration. |


### Receiving Weight

>Note: The weight value returned in the data packet is always in grams

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 |  DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0B | <br>MillSeconds <br><br><br> High byte of an unsigned 24-bit integer |MillSeconds <br><br><br> Mid byte of an unsigned 24-bit integer |MillSeconds <br><br><br> Low byte of an unsigned 24-bit integer | unit of weight <br><br>01:Gram<br>02:Ounce |Weight symbol data points (+/-)|<br>Grams weight * 100 <br><br><br> High byte of an unsigned 24-bit integer |<br>Grams weight * 100 <br><br><br> Mid byte of an unsigned 24-bit integer |<br>Grams weight * 100 <br><br><br> Low byte of an unsigned 24-bit integer |Flow rate symbol data points (+/-)|Flow rate*100 <br><br><br> High byte of an unsigned Short integer|Flow rate*100 <br><br><br> Low byte of an unsigned Short integer|Percentage of remaining power | standby time (min * 10) <br><br><br> High byte of an unsigned Short integer |standby time (min * 10) <br><br><br> Low byte of an unsigned Short integer| Buzzer gear | Flow Rate Smoothing Switch |00 |checkSum | Get time, weight, flow rate and power percentage data on the scale |

### Receiving Powder Weight

>Note: The powder weight unit is grams

><mark><strong><em>Available in beta firmware V3.2.4 and later, or release firmware V4.0.0 and later.</em></strong></mark>

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 | DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0F | Powder weight symbol data points (+/-) | Powder weight * 100<br>High byte of an unsigned 24-bit integer | Powder weight * 100<br>Mid byte of an unsigned 24-bit integer | Powder weight * 100<br>Low byte of an unsigned 24-bit integer |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |checkSum | Get powder weight data on the scale |

### Receiving Automatic Mode Event And Settlement Data

><mark><strong><em>Available in beta firmware V3.2.4 and later, or release firmware V4.0.0 and later.</em></strong></mark>

>Event trigger: 02 is sent when automatic mode enters ready; 01 is sent when brewing starts automatically or by command; 00 is sent when brewing ends by the configured automatic stop condition or by command; 03 is sent when exiting ready; 04 is sent when exiting done.

>BYTE11-BYTE13 contain the average flow rate in timing mode, or the ratio result (liquid weight / powder weight) in ratio mode.

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 | DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0D | Event state<br>00:Stopped<br>01:Started<br>02:Ready<br>03:Exit ready<br>04:Exit done | MillSeconds<br>High byte of an unsigned 24-bit integer | MillSeconds<br>Mid byte of an unsigned 24-bit integer | MillSeconds<br>Low byte of an unsigned 24-bit integer | Weight symbol data points (+/-) | Grams weight * 100<br>High byte of an unsigned 24-bit integer | Grams weight * 100<br>Mid byte of an unsigned 24-bit integer | Grams weight * 100<br>Low byte of an unsigned 24-bit integer | Result symbol data points (+/-) | Average flow rate or ratio result * 100<br>High byte of an unsigned Short integer | Average flow rate or ratio result * 100<br>Low byte of an unsigned Short integer |00 |00 |00 |00 |00 |00 |checkSum | Get automatic mode event and settlement data on the scale |

### Other Data

It is currently not open, so contact us if you need it.

Email: develop@bookoocoffee.com
