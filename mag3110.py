#!/usr/bin/env python2

# MAG3110 : Three-axis magnetometer
# This script can calibrate the sensor and acquire data.
# It will output magnetic field on the three axis in micro Tesla.

import smbus
import os
import time

# I2C constants
bus = smbus.SMBus(1)		# 0 if /dev/i2c-0 exists, 1 if /dev/i2c-1 exists
ADDR		= 0x0E
CTRL_REG1	= 0x10
CTRL_REG2	= 0x11



### MAG3110's class
class Mag3110:
	def __init__(self):
		who_am_i = bus.read_byte_data( ADDR, 0x07 )
		if who_am_i == 0xc4:
			bus.write_byte_data( ADDR, CTRL_REG1, 0x00 )
			bus.write_byte_data( ADDR, CTRL_REG2, 0x80 )
			return
		else:
			print "Device ID is", hex(who_am_i), " instead of 0xC4"
			exit(1)


	def get_mag(self):
		x = 0
		y = 1
		z = 2
		mag=[0,0,0]
		# Set TM = 1, and output data rate = 10 Hz (100 ms between each acquisition)
		bus.write_byte_data( ADDR, CTRL_REG1, 0x1A )
		while 1:
			dr_status = bus.read_byte_data( ADDR, 0x00 )
			if dr_status & 0x8:
				break
		# Read data
		mag_block_data = bus.read_i2c_block_data( ADDR, 0x01, 6 )
		mag[x] = (mag_block_data[0] << 8) + mag_block_data[1]
		mag[y] = (mag_block_data[2] << 8) + mag_block_data[3]
		mag[z] = (mag_block_data[4] << 8) + mag_block_data[5]
		# Convert 2's complement to integer
		for i in range (0, 3):
			if mag[i] & (1<<15):
				mag[i] -= 1<<16
		return (mag[x], mag[y], mag[z])
	
	def calibrate(self):
		x_max = -3000
		x_min = 3000
		y_max = -3000
		y_min = 3000
		z_max = -3000
		z_min = 3000
		print "Calibration :"
		print "Rotate your board for 360 degrees on the three axis."
		print "Press Ctrl+C when you finish."
		try:
			while 1:
				(x, y, z) = self.get_mag()
				if x>x_max: x_max=x
				if x<x_min: x_min=x

				if y>y_max: y_max=y
				if y<y_min: y_min=y

				if z>z_max: z_max=z
				if z<z_min: z_min=z
				time.sleep(0.1)
		except KeyboardInterrupt:
			self.standby()
			print
			x_off = ( x_max + x_min )/2
			y_off = ( y_max + y_min )/2
			z_off = ( z_max + z_min )/2
			print "X_MAX :", x_max, "\tX_MIN :", x_min, "\tX_OFF :", x_off
			print "Y_MAX :", y_max, "\tY_MIN :", y_min, "\tY_OFF :", y_off
			print "Z_MAX :", z_max, "\tZ_MIN :", z_min, "\tZ_OFF :", z_off
			with open("mag_offsets.txt","w") as f:
				f.write(  str(x_off) + " " + str(y_off) + " " + str(z_off)  )
			return

	def acquisition(self):
		try:
			x_off = 0
			y_off = 0
			z_off = 0
			x_max = -3000
			x_min = 3000
			y_max = -3000
			y_min = 3000
			z_max = -3000
			z_min = 3000
			if os.path.exists("mag_offsets.txt")==False:
				print "WARNING: No calibration was made."
				print "         Therefore, the acquisition will output incorrect values"
			else:
				with open("mag_offsets.txt", "r") as f:
					s = f.readline()
					[x_off, y_off, z_off] = s.split()
					x_off = int(x_off)
					y_off = int(y_off)
					z_off = int(z_off)
			print "Press Ctrl+C to stop acquisition and go back to the menu"
			time.sleep(1)
			while 1:
				(x, y, z) = self.get_mag()
				print "MAG3110:\tX.", x-x_off, "uT",\
					      "\tY.", y-y_off, "uT",\
					      "\tZ.", z-z_off, "uT"
				time.sleep(0.1)
		except KeyboardInterrupt:
			self.standby()
			print
		finally:
			mag.standby()
	
	def standby(self):
		bus.write_byte_data(ADDR, CTRL_REG1, 0x00)
		return



### Main
choice = 0
mag = Mag3110()
options = { 	0:exit,
		1:mag.calibrate,
		2:mag.acquisition,
		}
while 1:
	try:
		choice = int( raw_input("\nYou should calibrate the sensor before the acquisition.\n"\
					"What do you want to do?\n"\
					"\t1 : Calibrate the MAG3110 sensor\n"\
					"\t2 : Acquisition\n"\
					"\t0 : Exit\n"\
					"Enter your choice : "	) )
		if options.has_key(choice):
			options[choice]()
		else:
			print "\nWrong number. Try again."
	except ValueError:
		print "\nEnter a number. Try again."
