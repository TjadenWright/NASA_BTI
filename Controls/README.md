<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Space Trajectory logo.jpg" alt="Space Trajectory" title="Space Trajectory" />

# Controls
## V1 and V2 of the Controls
* Used for the prototype rover.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/prototype rover.png" alt="prototype rover" title="prototype rover" />

## V3 of the controls
* Visual representation of the communication between Arduino and Python.
* This is used for the actual rover.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/controls_architecture.png" alt="Controls Architecture" title="Controls Architecture" />

## V3 Software Pinout
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
| LOAD CELL	| NAU7802SGI | IN | Channels 15, 14, 12, and 13 | Channels 16, 14, 13, and 12 |
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






