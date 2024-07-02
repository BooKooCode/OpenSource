# Espresso Monitor Transmission protocol
- Contact Us: develop@bookoocoffee.com
- Last Update: 2April 8, 2024
>  All BLE UUIDs adopted by the Espresso Monitor use a simplified representation of the 16-bit UUID, and its corresponding 128-bit UUID is the unified structure agreed upon by the Bluetooth Association, i.e. 0000 xxxx -0000-1000-8000-00805F9B34FB

## 1. Bluetooth Protocol Basic Info And Check Sum
> All data are transferred in hexadecimal

### Basic Info

Service UUID: 0x0FFF

Characteristic UUID:

- Command Characteristic UUID: 0xFF01
- Extraction Data Characteristic UUID: 0xFF02

### Check Sum Method

Method: XOR Calculation
```
CheckSum = Header1 ^ Header2 ^ Data0 ^ Data1 ^ ... ^ DataN

if CheckSum == DataSUM
    pass
```

## 2. Transmission Data

### Command Data

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 | DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| PRODUCT NUMBER | TYPE | DATA1 | DATA2 | DATA3 | DATA4 | DATASUM |DESCRIPTION |
| 02 | 0C | 00 | 00 | 00 | 00 | 0e | Send a stop extraction command |
| 02 | 0C | 01 | 00 | 00 | 00 | 0f | Send a start extraction command |

### Extraction data
>Pressure data is sent by default as a two-byte unsigned short integer in bar, pressure * 100.

| BYTE1 | BYTE2 | BYTE3 | BYTE4 | BYTE5 | BYTE6 | BYTE7 | BYTE8 |BYTE9 |BYTE10 |DESCRIPTION |
| ----------- | ----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |----------- |
| 02 | 1B | 00 | 00 | <br>Pressure*100(bar)  <br><br> High byte of a unsigned Short integer	 | <br>Pressure*100(bar)   <br><br> Low byte of a unsigned Short integer	 | Percentage of power remaining (%) |00 |00 |00 | Receives pressure data |

### Other Data

It is currently not open, so contact us if you need it.

Email: develop@bookoocoffee.com
