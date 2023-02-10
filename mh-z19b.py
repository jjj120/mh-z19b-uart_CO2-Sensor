from machine import Pin, UART
import time, sys

class MHZ19B_UART:
    def __init__(self, uart: UART):
        self.uart = uart
        self.uart.init(baudrate=9600, bits=8, parity=None, stop=1)

    def read(self) -> int:
        """
        Reads and returns the current CO2 level it in ppm
        NOTE: returns -1 if sensor returns none, -2 if checksum incorrect
        """
        return self.readCO2()
    
    def readCO2(self) -> int:
        """
        Reads and returns the current CO2 level it in ppm
        NOTE: returns -1 if sensor returns none, -2 if checksum incorrect
        """
        self.__sendCommand(command=0x86)
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
        return self.zeroCalibrate()

    def zeroCalibrate(self) -> None:
        """
        Calibrates zero-point of sensor (400ppm)
        NOTE: Zero point is 400ppm, please make sure the sensor had been running under 400ppm for at least 20 minutes!
        """
        self.__sendCommand(command=0x87)
        return
    
    def spanPointCalibration(self, upperValue: int) -> None:
        """
        Calibrates the upper limit of the span, should be at least 1000ppm (recommended 2000ppm)
        NOTE: Make sure to calibrate first
        """
        highByte = int(upperValue / 256)
        lowByte = upperValue % 256
        self.__sendCommand(command=0x88, highByte=highByte, lowByte=lowByte)
        return
    
    def setAutoCalibration(self, calibration: bool=True) -> None:
        """
        Set auto baseline correction (from factory set to True), calibrates every 24 hours
        NOTE: Recommended for indoor use (e.g. homes, offices, schools, ...), NOT recommended for greenhouse, farm or refrigerator
        """
        if calibration: commandByte = 0xA0
        else:           commandByte = 0x00
        self.__sendCommand(command=commandByte)
        return

    def sensorDetectionRange(self, upperValue: int) -> None:
        """
        Calibrates the upper limit of the detection, can be 2000ppm or 5000ppm
        NOTE: Make sure to calibrate first
        """
        highByte = int(upperValue / 256)
        lowByte = upperValue % 256
        self.__sendCommand(command=0x88, highByte=highByte, lowByte=lowByte)
        return

    def __sendCommand(self, startByte=0xFF, sensorNumber: int=0x01, command: int=0x86, highByte: int=0x00, lowByte: int=0x00) -> bool: 
        """
        --internal only-- Sends specified command to sensor (sends read command by default)
        NOTE: commands are specified in datasheet, e.g. here: https://www.ribu.at/mediafiles/datasheets/mh-z19b-co2-ver1_0.pdf
        """
        buffer = bytearray([startByte, sensorNumber, command, highByte, lowByte, 0x00, 0x00, 0x00])
        buffer.append(self.__calcChecksum(buffer))
        self.uart.write(buffer)
        return False
    
    def __calcChecksum(self, data: bytes) -> int:
        data = data[1:-1]
        checksum = 0
        for byte in data:
            checksum += byte
        
        return 0xFF - (checksum % 0xFF) + 1

    def __checkChecksum(self, data: bytes) -> bool:
        checksum = self.__calcChecksum(data)
        return (checksum == list(data)[-1] - 1)
    
    


if __name__ == '__main__':
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