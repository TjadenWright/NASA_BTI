# NASA_BTI
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Space Trajectory logo.jpg" alt="Space Trajectory" title="Space Trajectory" />

# Custom Arduino Functions
## Table 1. Arduino Library Files
| Device  | Description | Folder Location |
| ------------- | ------------- |--------------|
| ADS1219 | I2C 24 bit ADC for the Motor/Actuator Board | [NASA_BTI/Arduino/ADS1219_code/ADS1219](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/ADS1219_code/ADS1219) | 
| PCF8574 | I2C GPIO Expander | [NASA_BTI/Arduino/PCF8574_and_PWM_code/PCF8574](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/PCF8574_and_PWM_code/PCF8574) | 
| TCA9548A | I2C Mux for the Motherboard | [NASA_BTI/Arduino/TCA9548A_code/TCA9548A](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/TCA9548A_code/TCA9548A) |
| TMP1075 | I2C Temperature Sensor for board temperature | [NASA_BTI/Arduino/TMP1075_code/TMP1075](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/TMP1075_code/TMP1075) |
| VNH7070 | I2C Hbridge for the Actuator Board | [NASA_BTI/Arduino/VNH7070_code/VNH7070](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/VNH7070_code/VNH7070) |
| DS3930* | I2C Digipot with GPIO Expander | [NASA_BTI/Arduino/DS3930_code/DS3930](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/DS3930_code/DS3930) |
| MCP45HVX1* | I2C high voltage Digipot | [NASA_BTI/Arduino/MCP45HVX1_code/MCP45HVX1](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/MCP45HVX1_code/MCP45HVX1) |


## Arduino Setup
* Make sure to put any custom functions from Table 1. in the arduino library folder: \Documents\Arduino\libraries\
* Any devices with * in their name are optional as they are no longer used.

## Combined Controls Software Pinout
### [Arduino Mega 2560](https://www.amazon.com/ARDUINO-MEGA-2560-REV3-A000067/dp/B0046AMGW0/ref=asc_df_B0046AMGW0/?tag=hyprod-20&linkCode=df0&hvadid=309743296044&hvpos=&hvnetw=g&hvrand=49053266616977050&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=1025714&hvtargid=pla-516265455074&psc=1&mcid=5a8163990af63657ae8d0acd875032ba&gclid=Cj0KCQjwwYSwBhDcARIsAOyL0fihiKt0s13scxhQRWIWF-R_5dx5jALIs2MZE2kc4TPAUg5bMTdHDSsaAnjSEALw_wcB)
* This Arduino will be used for Channels 1-8.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/arduino_mega.png" alt="arduino_mega" title="arduino_mega" />

### Arduino Leonardo ([Latte Panda Sigma](https://www.dfrobot.com/product-2748.html))
* This Arduino will be used for Channels 9-16.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/panda.png" alt="panda" title="panda" />

### Table 1a. Motherboard Controls
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| EFUSE_EN | PCF8574 (P1) |	OUT	| Channel 15 | Channel 16 |

### Table 1b. Motherboard Diagnostics
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| CURRENT |	ADS1219 (Channel 3)	| IN |	Channel 15	| Channel 16 |
| OC FAULT | PCF8574 (P2) |	IN |	Channel 15 | Channel 16 |
| OT ALERT	| PCF8574 (P0) | IN | Channel 15 | Channel 16 |
| BOARD TEMP | TMP1075DR | IN |Channel 15 |Channel 16 |
| LOAD CELL	| NAU7802SGI | IN | Channels 15, 14, 12, and 13 | Channels 16, 15, 14, and 13 |
| OFF BOARD TEMP | MCP9601 | IN | Channels 0-14 | Channels 1-15 |


### Table 2a. Motor Board Controls
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| Motor Enable | PCF8574_0 (P1) | OUT |Channels 0-14 | Channels 1-15 |
| EFUSE_EN | PCF8574_1 (P0) | OUT | Channels 0-14 | Channels 1-15 |
| PWM | Arduin Pin | OUT | Channels 0-14 | Channels 1-15 | 
| FR | PCF8574_0 (P0) | OUT	| Channels 0-14	| Channels 1-15 |
| BREAK	| PCF8574_1 (P2) | OUT | Channels 0-14	| Channels 1-15 |

### Table 2b. Motor Board Diagnostics
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| ALARM	| PCF8574_0 (P4) | IN |	Channels 0-14 | Channels 1-15 |
| BOARD TEMP | TMP1075DR | IN | Channels 0-14 | Channels 1-15 |
| CURRENT | ADS1219 (Channel 2)	| IN | Channels 0-14 | Channels 1-15 |
| OC FAULT	| PCF8574_1 (P1) | IN | Channels 0-14 | Channels 1-15 |
| SPEED	| ADS1219 (Channel 1) | IN | Channels 0-14 | Channels 1-15 |


### Table 3a. Actuator Board Controls
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| EFUSE_EN | PCF8574_1 (P0) | OUT | Channels 0-14 | Channels 1-15 |
| PWM | Arduin Pin | OUT | Channels 0-14 | Channels 1-15 | 
| FR | PCF8574_0 (P6, P5, and P7) | OUT	| Channels 0-14	| Channels 1-15 |

### Table 3b. Actuator Board Diagnostics
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| BOARD TEMP | TMP1075DR | IN | Channels 0-14 | Channels 1-15 |
| CURRENT | ADS1219 (Channel 2)	| IN | Channels 0-14 | Channels 1-15 |
| OC FAULT	| PCF8574_1 (P1) | IN | Channels 0-14 | Channels 1-15 |
| FEEDBACK	| ADS1219 (Channel 0) | IN | Channels 0-14 | Channels 1-15 |

### Table 4a. Slew Gear Board Controls
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| Motor Enable | PCF8574_0 (P1) | OUT |Channels 0-14 | Channels 1-15 |
| EFUSE_EN | PCF8574_1 (P0) | OUT | Channels 0-14 | Channels 1-15 |
| PWM | Arduin Pin | OUT | Channels 0-14 | Channels 1-15 | 
| FR | PCF8574_0 (P0) | OUT	| Channels 0-14	| Channels 1-15 |
| BREAK	| PCF8574_1 (P2) | OUT | Channels 0-14	| Channels 1-15 |

### Table 4b. Slew Gear Board Diagnostics
| ICs Data  | Device | IN or OUT | Motherboard Channel | Software Channel |
| ----------| ------ |-----------| ------------------- | ---------------- |
| ALARM	| PCF8574_0 (P4) | IN |	Channels 0-14 | Channels 1-15 |
| BOARD TEMP | TMP1075DR | IN | Channels 0-14 | Channels 1-15 |
| CURRENT | ADS1219 (Channel 2)	| IN | Channels 0-14 | Channels 1-15 |
| OC FAULT	| PCF8574_1 (P1) | IN | Channels 0-14 | Channels 1-15 |
| FEEDBACK	| ADS1219 (Channel 0) | IN | Channels 0-14 | Channels 1-15 |

