#!/usr/bin/env python2

# MPL3115A2 : Altitude, pressure and temperature sensor
# This script acquire the data.
# It will output the temperature in Celsius degree, and either the pressure in Pascal, either the altitude in meter.

import smbus
import time

alt_bar = 1			# 0 to choose altimeter, 1 to choose barometer

# Special character
deg = u'\N{DEGREE SIGN}'

# I2C constants
bus = smbus.SMBus(1)		# 0 if /dev/i2c-0 exists, 1 if /dev/i2c-1 exists
ADDR		= 0x60
PT_DATA_CFG	= 0x13
CTRL_REG1	= 0x26
CTRL_REG2	= 0x27
CTRL_REG3	= 0x28
CTRL_REG4	= 0x29
CTRL_REG5	= 0x2a

# Enable event flags
#bus.write_byte_data(ADDR, PT_DATA_CFG, 0x07)



### MPL3115A2's class
class Mpl3115a2:
	def __init__(self):
		who_am_i = bus.read_byte_data(ADDR, 0x0C)
		if who_am_i == 0xc4:
			if alt_bar==0:
				# Set altimeter & set oversample ratio to 128
				bus.write_byte_data(ADDR, CTRL_REG1, 0xb8)
			else:
				# Set barometer & set oversample ratio to 128
				bus.write_byte_data(ADDR, CTRL_REG1, 0x08)	
			bus.write_byte_data(ADDR, CTRL_REG2, 0x00)
			bus.write_byte_data(ADDR, CTRL_REG3, 0x17)
			bus.write_byte_data(ADDR, CTRL_REG4, 0x00)
			bus.write_byte_data(ADDR, CTRL_REG5, 0x00)
			bus.write_byte_data(ADDR, PT_DATA_CFG, 0x07)	# Enable event flags
			return
		else:
			print "Device ID is ", hex(who_am_i), " instead of 0xC4."
			exit(1)

	def get_alt(self):
		alt_block_data = bus.read_i2c_block_data(ADDR,0x01,3)
		alt_msb = alt_block_data[0]
		alt_csb = alt_block_data[1]
		alt_lsb = alt_block_data[2]
		alt_int = (alt_msb << 8) + alt_csb
		# Integer part : convert 2's complement to integer
		if alt_int & (1<<15):
			alt_int -= 1<<16
		# Decimal part
		# Example : alt_lsb = 0xE0  ->  alt_dec = "0,E" = 0xE0>>8 = 14/256.0 = 0,875
		alt_dec = alt_lsb / 256.0
		return (alt_int + alt_dec)
	
	def get_bar(self):
		bar_block_data = bus.read_i2c_block_data(ADDR,0x01,3)
		bar_msb = bar_block_data[0]
		bar_csb = bar_block_data[1]
		bar_lsb = bar_block_data[2]
		bar_int = (bar_msb << 10) + (bar_csb << 2) + (bar_msb >> 6)
		bar_dec = (bar_msb >> 4) & 0x03
		bar_dec /= 4.0
		return (bar_int + bar_dec)

	def get_temp(self):
		temp_block_data = bus.read_i2c_block_data(ADDR,0x04,2)
		temp_int = temp_block_data[0]
		temp_dec = temp_block_data[1]
		# Integer part : convert 2's complement to integer
		if temp_int & (1<<15):
			temp_int -= 1<<16
		# Decimal part (cf decimal part of altimeter above to understand why we divide by 256.0)
		temp_dec = temp_dec / 256.0
		return (temp_int + temp_dec)

	def active(self):
		val = bus.read_byte_data(ADDR,0x26)
		val = val | 0x01
		bus.write_byte_data(ADDR,0x26,val)
		return

	def standby(self):
		val = bus.read_byte_data(ADDR,0x26)
		val = val & ~0x01
		bus.write_byte_data(ADDR,0x26,val)
		return



### Main
print "Press Ctrl+C to exit."
mpl = Mpl3115a2()
mpl.active()
time.sleep(1)
try:
	while 1:
		if alt_bar==0:
			print "MPL3115:", "\tAlt.", mpl.get_alt(), "m\tTemp:", mpl.get_temp(), deg+"C"
		else:
			print "MPL3115:", "\tBar.", mpl.get_bar(), "Pa\tTemp.", mpl.get_temp(), deg+"C"
		time.sleep(0.1)
except KeyboardInterrupt:
	print
finally:
	mpl.standby()
