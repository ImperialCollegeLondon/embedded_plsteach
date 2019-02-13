import smbus
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)
print(chan.value, chan.voltage)


reg_addr = 0
bus_addr = 0x48

"""
bus = smbus.SMBus(1)
n = 4
readi2c = bus.read_i2c_block_data(bus_addr,reg_addr,n)
writebyte = bus.write_byte(bus_addr, data)
print(readi2c)
"""

#print(res)
#write_i2
