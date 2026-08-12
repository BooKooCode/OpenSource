# ULTRA SCALE Transmission protocol
- Contact Us: develop@bookoocoffee.com
- Last Update: August 12, 2026

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
| 03 | 0A | 02 | 00 | 00~05 (Beep level) | checkSum | Adjust the beep size, 0 means no beeper sound on | |
| 03 | 0A | 03 | 00 | 05~1e (Auto-off duration) | checkSum | Adjust the automatic shutdown duration from 5-30 minutes | |
| 03 | 0A | 04 | 00 | 00 | checkSum | Send the start timer command | Only effective in timing-mode and ratio-mode. |
| 03 | 0A | 05 | 00 | 00 | checkSum | Send the stop timer command | Only effective in timing-mode and ratio-mode. |
| 03 | 0A | 06 | 00 | 00 | checkSum | Send the reset timer command | Only effective in timing-mode and ratio-mode. |
| 03 | 0A | 07 | 00 | 00 | checkSum | Send the tare and start time command (recommend) |  |
| 03 | 0A | 08 | 00/01 | 00 | checkSum | Whether or not flow smoothing is turned on, 00 means it is not turned on, 01 means it is turned on | |
| 03 | 0A | 09 | 00 | 00 | checkSum | Send the calibration command. | Only effective in weight-mode |
| 03 | 0A | 0B | 00/01 | 00 | checkSum | Set the stop condition for automatic-mode, 00 means that the stop condition is the liquid flow stopping, and 01 means that the stop condition is the container being removed. | |
| 03 | 0A | 0D | Powder weight * 10<br>High byte | Powder weight * 10<br>Low byte | checkSum | Set the powder weight | Unit: gram, valid range: 0.1-999.0 g. Available in beta firmware V3.2.4 and later, or release firmware V4.0.0 and later. |
| 03 | 0A | 15 | 00 | 00 | checkSum | Send the shutdown command | Available in release firmware V4.0.0 and later. Not valid while charging. |


### Receiving Weight

>Note: The weight value returned in the data packet is always in grams

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 |  DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0B | <br>MillSeconds <br><br><br> High byte of an unsigned 24-bit integer |MillSeconds <br><br><br> Mid byte of an unsigned 24-bit integer |MillSeconds <br><br><br> Low byte of an unsigned 24-bit integer | unit of weight <br><br>01:Gram<br>02:Ounce |Weight symbol data points (+/-)|<br>Grams weight * 100 <br><br><br> High byte of an unsigned 24-bit integer |<br>Grams weight * 100 <br><br><br> Mid byte of an unsigned 24-bit integer |<br>Grams weight * 100 <br><br><br> Low byte of an unsigned 24-bit integer |Flow rate symbol data points (+/-)|Flow rate*100 <br><br><br> High byte of an unsigned Short integer|Flow rate*100 <br><br><br> Low byte of an unsigned Short integer|Percentage of remaining power | standby time (min * 10) <br><br><br> High byte of an unsigned Short integer |standby time (min * 10) <br><br><br> Low byte of an unsigned Short integer| Buzzer gear | Flow Rate Smoothing Switch |00 |checkSum | Get time, weight, flow rate and power percentage data on the scale |

### Receiving Powder Weight

>Note: The powder weight unit is grams

>Available in beta firmware V3.2.4 and later, or release firmware V4.0.0 and later.

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 | DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0F | Powder weight symbol data points (+/-) | Powder weight * 100<br>High byte of an unsigned 24-bit integer | Powder weight * 100<br>Mid byte of an unsigned 24-bit integer | Powder weight * 100<br>Low byte of an unsigned 24-bit integer |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |00 |checkSum | Get powder weight data on the scale |

### Receiving Automatic Mode Event And Settlement Data

>Available in beta firmware V3.2.4 and later, or release firmware V4.0.0 and later.

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 | DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0D | Event state<br>00:Stopped<br>01:Started<br>02:Ready<br>03:Exit ready<br>04:Exit done | MillSeconds<br>High byte of an unsigned 24-bit integer | MillSeconds<br>Mid byte of an unsigned 24-bit integer | MillSeconds<br>Low byte of an unsigned 24-bit integer | Weight symbol data points (+/-) | Grams weight * 100<br>High byte of an unsigned 24-bit integer | Grams weight * 100<br>Mid byte of an unsigned 24-bit integer | Grams weight * 100<br>Low byte of an unsigned 24-bit integer | Flow rate symbol data points (+/-) | Flow rate * 100<br>High byte of an unsigned Short integer | Flow rate * 100<br>Low byte of an unsigned Short integer |00 |00 |00 |00 |00 |00 |checkSum | Get automatic mode event and settlement data on the scale |

### Other Data

It is currently not open, so contact us if you need it.

Email: develop@bookoocoffee.com
