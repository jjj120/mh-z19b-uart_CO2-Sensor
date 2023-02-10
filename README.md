# Micropython Library for MH-Z19B CO2 Sensor

This library includes a simple class to get data and calibrate a connected MH-Z19B CO2 Sensor. It is only tested on the Raspberry Pi Pico (H) with micropython 1.19.1, but it should work on all newer versions of micropython and other boards, that support micropython and UART. 

It implements all commands detailed in the [datasheet](https://www.ribu.at/mediafiles/datasheets/mh-z19b-co2-ver1_0.pdf). 

## Usage

For the simplest example, connect the sensor as follows: 

| Raspberry Pi Pico               | Sensor Pins | Cable Colors | Usage                              |
|-----------------------|-------------|--------------|------------------------------------|
| GND Pin (e.g. Pin 38) | GND         | Black        | Ground, 0V                         |
| VBus (Pin 40)         | Vin         | Red          | Voltag Input, 5V                   |
| TX (e.g. GPIO 0)      | RX          | Blue         | Sensor Data receiving, 3.3V        |
| RX (e.g. GPIO 1)      | TX          | Green        | Sensor Data transmitting, 3.3V     |
| Not used              | HD          |              | Pin to manually calibrate          |
| Not used              | PWM         |              | PWM Output                         |
| Not used              | VO          | Brown        | Analog output (0.4~2V) or (0~2.5V) |

Use the following code: 
```python
import machine, UART
from mh-z19b import MHZ19B_UART

tx = machine.Pin(0, Pin.OUT)
rx = machine.Pin(1, Pin.IN)
uart = UART(0, tx=tx, rx=rx)
mhz19b = MHZ19B_UART(uart)
print(mhz19b.read())
```

## Functions

### Constructor MHZ19B_UART(uart)
The class has a normal constructor, that takes the [UART interface object](https://docs.micropython.org/en/latest/library/machine.UART.html) and returns an instance of the class. 


### MHZ19B_UART.read() and MHZ19B_UART.readCO2()
The read functions take no arguments and return the CO2 concentration of the air in ppm (parts per million). 

The two read functions do exactly the same, they are only there to have clearer names. 


### MHZ19B_UART.calibrate() and MHZ19B_UART.zeroCalibrate()
The calibrate functions calibrate the zero-point of the sensor (400ppm). Make sure to operate the sensor in 400ppm climate (outside) for at least 20 mins before calibrating. 

Calibrating can also be done by connecting the HD-Pin of the sensor to GND for at least 7 secs. Additionally the sensor can also calibrate itself by using the internal ABC-logic (Automatic Baseline Correction). This is turned on by default, but can be turned off by using the [setAutoCalibration()](#mhz19b_uartsetautocalibration) function. 


### MHZ19B_UART.spanPointCalibration(upperValue: int)
Calibrates the upper limit of the span, should be at least 1000ppm (recommended 2000ppm). The upperValue should be the ppm for the span upper limit. 


### MHZ19B_UART.setAutoCalibration(calibration: boolean)
Turns on or off the internal ABC-logic (Automatic Baseline Correction) in the sensor. For further information, look in the [datasheet](https://www.ribu.at/mediafiles/datasheets/mh-z19b-co2-ver1_0.pdf). 


### MHZ19B_UART.sensorDetectionRange(upperValue: int)
Sets the upper limit of the sensor detection range. Can either be 2000ppm or 5000ppm. This affects the reading accuracy, it is ± (50ppm +3% of reading value), so the higher the read value, the lower the accuracy. 


## Other things to know

The MH-Z19B Sensor also has PWM and analog outputs, these are not supported/used by this library. If you have made one or know about one, I'll happily link it here :)
