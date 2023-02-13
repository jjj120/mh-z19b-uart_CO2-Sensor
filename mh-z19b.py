from machine import Pin, UART
import time, sys

COMM_READ = 0x86
COMM_CALIBRATE_ZERO = 0x87
COMM_CALIBRATE_SPAN = 0x88
COMM_AUTOCALIBRATION_ON = 0xA0
COMM_AUTOCALIBRATION_OFF = 0x00
COMM_DETECTION_RANGE = 0x99

class MHZ19B_UART:
    def __init__(self, uart: UART):
        #type error handling
        if type(uart) != UART: raise TypeError("given uart must be of type UART")

        #save and set uart
        self.uart = uart
        self.uart.init(baudrate=9600, bits=8, parity=None, stop=1)

    def read(self) -> int:
        """
        Reads and returns the current CO2 level it in ppm
        NOTE: returns -1 if sensor returns none, -2 if checksum incorrect
        """
        #run read CO2 command
        return self.readCO2()
    
    def readCO2(self) -> int:
        """
        Reads and returns the current CO2 level it in ppm
        NOTE: returns -1 if sensor returns none, -2 if checksum incorrect
        """
        #send command and read+check data
        self.__sendCommand(command=COMM_READ)
        data = self.uart.read(8 * 8)
        if data == None: 
            return -1
        
        if not(self.__checkChecksum(data)):
            return -2

        co2 = data[2] * 256 + data[3]
        return co2
    
    def calibrate(self) -> None:
        """
        Calibrates zero-point of sensor (400ppm)
        NOTE: Zero point is 400ppm, please make sure the sensor had been running under 400ppm for at least 20 minutes!
        """
        #run zero calibration function
        return self.zeroCalibrate()

    def zeroCalibrate(self) -> None:
        """
        Calibrates zero-point of sensor (400ppm)
        NOTE: Zero point is 400ppm, please make sure the sensor had been running under 400ppm for at least 20 minutes!
        """
        #send command
        self.__sendCommand(command=COMM_CALIBRATE_ZERO)
        return
    
    def spanPointCalibration(self, upperValue: int) -> None:
        """
        Calibrates the upper limit of the span, should be at least 1000ppm (recommended 2000ppm)
        NOTE: Make sure to calibrate first
        """
        #type error handling
        if type(upperValue) != int: raise TypeError("upperValue must be of type int")

        #input error handling
        if upperValue < 1000: raise ValueError("upperValue must be at least 1000ppm")
        if upperValue > 5000: raise ValueError("upperValue must be at most 5000ppm")

        #send command
        highByte = int(upperValue / 256)
        lowByte = upperValue % 256
        self.__sendCommand(command=COMM_CALIBRATE_SPAN, highByte=highByte, lowByte=lowByte)
        return
    
    def setAutoCalibration(self, calibration: bool=True) -> None:
        """
        Set auto baseline correction (from factory set to True), calibrates every 24 hours
        NOTE: Recommended for indoor use (e.g. homes, offices, schools, ...), NOT recommended for greenhouse, farm or refrigerator
        """
        #type error handling
        if type(calibration) != bool: raise TypeError("calibration must be of type boolean")

        #send command
        if calibration: commandByte = COMM_AUTOCALIBRATION_ON
        else:           commandByte = COMM_AUTOCALIBRATION_OFF
        self.__sendCommand(command=commandByte)
        return

    def sensorDetectionRange(self, upperValue: int) -> None:
        """
        Calibrates the upper limit of the detection, can be 2000ppm or 5000ppm
        NOTE: Make sure to calibrate first
        """
        #input error handling
        if upperValue != 2000 and upperValue != 5000: raise ValueError("upperValue must be either 2000ppm or 5000ppm")

        #send command
        highByte = int(upperValue / 256)
        lowByte = upperValue % 256
        self.__sendCommand(command=COMM_DETECTION_RANGE, highByte=highByte, lowByte=lowByte)
        return

    def __sendCommand(self, startByte=0xFF, sensorNumber: int=0x01, command: int=0x86, highByte: int=0x00, lowByte: int=0x00) -> bool: 
        """
        --internal only-- Sends specified command to sensor (sends read command by default)
        NOTE: commands are specified in datasheet, e.g. here: https://www.ribu.at/mediafiles/datasheets/mh-z19b-co2-ver1_0.pdf
        """
        #type error handling
        if type(startByte) != int: raise TypeError("startByte must be of type int")
        if type(sensorNumber) != int: raise TypeError("sensorNumber must be of type int")
        if type(command) != int: raise TypeError("command must be of type int")
        if type(highByte) != int: raise TypeError("highByte must be of type int")
        if type(lowByte) != int: raise TypeError("lowByte must be of type int")

        #input error handling
        if startByte != 0xFF: raise ValueError("startByte must be 0xFF")
        if sensorNumber != 0x01: raise ValueError("sensorNumber must be 0x01")
        if command not in [COMM_READ, COMM_CALIBRATE_ZERO, COMM_CALIBRATE_SPAN, COMM_AUTOCALIBRATION_ON, COMM_AUTOCALIBRATION_OFF, COMM_DETECTION_RANGE]: 
            raise ValueError("command is not valid")
        if highByte < 0x00 or highByte > 0xFF: raise ValueError("highByte must be between 0 and 0xFF (255)")
        if lowByte  < 0x00 or lowByte  > 0xFF: raise ValueError("lowByte must be between 0 and 0xFF (255)")

        #send command
        buffer = bytearray([startByte, sensorNumber, command, highByte, lowByte, 0x00, 0x00, 0x00])
        buffer.append(self.__calcChecksum(buffer))
        self.uart.write(buffer)
        return False
    
    def __calcChecksum(self, data: bytes) -> int:
        #type error handling
        if type(data) != bytes: raise TypeError("data must be of type bytes")

        #calculate checksum
        data = data[1:-1]
        checksum = 0
        for byte in data:
            checksum += byte
        
        return 0xFF - (checksum % 0xFF) + 1

    def __checkChecksum(self, data: bytes) -> bool:
        #type error handling
        if type(data) != bytes: raise TypeError("data must be of type bytes")
        
        #check checksum
        checksum = self.__calcChecksum(data)
        return (checksum == list(data)[-1] - 1)
    
    


if __name__ == '__main__':
    #test code
    #NOTE: this code is only for testing purposes, it is only tested on a Pi Pico
    #NOTE: test connections set tx and rx pins or connect as described here: https://github.com/jjj120/mh-z19b-uart_CO2-Sensor
    #NOTE: this code is not meant to be used in production, it is only for testing purposes
    tx = Pin(0, Pin.OUT)
    rx = Pin(1, Pin.IN)
    uart = UART(0, tx=tx, rx=rx)
    mhz19b = MHZ19B_UART(uart)

    try:
        while True:
            print(mhz19b.read())
            time.sleep(0.5)
    except KeyboardInterrupt:
        uart.deinit()
        sys.exit()