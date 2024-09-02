# MINI SCALE Transmission protocol
- Contact Us: develop@bookoocoffee.com
- Last Update: 2April 8, 2024

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
CheckSum = Header1 ^ Header2 ^ Data0 ^ Data1 ^ ... ^ DataN

if CheckSum == DataSUM
    pass
```

# 2. Transmission Data

### Command Data

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 |  DATASUM |DESCRIPTION |
| 03 | 0A | 01 | 00 | 00 | 08 | Send the tare command |
| 03 | 0A | 02 | 00~05 (Beep level) | 00 | checkSum | Adjust the beep size, 0 means no beeper sound on |
| 03 | 0A | 03 | 01~1e (Auto-off duration) | 00 | checkSum | Adjust the automatic shutdown duration from 1-30 minutes |
| 03 | 0A | 04 | 00 | 00 | 0a | Send the start timer command |
| 03 | 0A | 05 | 00 | 00 | 0d | Send the stop timer command |
| 03 | 0A | 06 | 00 | 00 | 0c | Send the reset timer command |
| 03 | 0A | 07 | 00 | 00 | 00 | Send the tare and start time command (recommend) |
| 03 | 0A | 08 | 00/01 | 00 | checkSum | Whether or not flow smoothing is turned on, 00 means it is not turned on, 01 means it is turned on |

### Receiving Weight

>Note: The current weight unit only supports grams

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 |BYTE8 |BYTE9 |BYTE10 |BYTE11 |BYTE12 |BYTE13 |BYTE14 |BYTE15 |BYTE16 |BYTE17 |BYTE18 |BYTE19 |BYTE20 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 |  DATA4 | DATA5 | DATA6 | DATA7 | DATA8 | DATA9 | DATA10 | DATA11 | DATA12 | DATA13 | DATA14 | DATA15 | DATA16 | DATA17 | DATASUM |DESCRIPTION |
| 03 | 0B | <br>MillSeconds <br><br><br> High byte of a unsigned Short integer	|MillSeconds <br><br><br> Mid byte of a unsigned Short integer |MillSeconds <br><br><br> Low byte of a unsigned Short integer | unit of weight |Weight symbol data points (+/-)|<br>Grams weight * 100 <br><br><br> High byte of a unsigned Short integer |<br>Grams weight * 100 <br><br><br> Mid byte of a unsigned Short integer |<br>Grams weight * 100 <br><br><br> Low byte of a unsigned Short integer |Flow rate symbol data points (+/-)|Flow rate*100 <br><br><br> High byte of a unsigned Short integer|Flow rate*100 <br><br><br> Low byte of a unsigned Short integer|Percentage of remaining power | standby time (min) <br><br><br> High byte of a unsigned Short integer |standby time (min) <br><br><br> Low byte of a unsigned Short integer| Buzzer gear | Flow Rate Smoothing Switch |00 |00 | Get time, weight, flow rate and power percentage data on the scale |

### Other Data

It is currently not open, so contact us if you need it.

Email: develop@bookoocoffee.com
