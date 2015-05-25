#!/usr/bin/env python2

# MMA8491Q : Three-axis accelerometer
# This script will acquire the data.
# It will output the acceleration in milli g ( 1g = 9,81m/s^2 ).
# NB : i2cdetect will not be able to detect this device until its enable signal is set to 1.

import smbus
import time
import os

# I2C constants
bus = smbus.SMBus(1)		 # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
ADDR	= 0x55

# MMA8491Q's class
class Mma8491q:
	def __init__(self):
		try:
			# Enable GPIO 25 (pin 22 - GPIO_GEN6 for RPi, EN_22 for Sensor Board)
			os.system("echo 25 > /sys/class/gpio/export")
			# Set "out" direction
			os.system("echo out > /sys/class/gpio/gpio25/direction")
			self.active()
			bus.read_byte_data(ADDR, 0x00)
			self.shutdown()
			return
		except:
			print "Device not active or not enabled."
			exit(1)


	def get_acc(self):
		a = [0, 0, 0]
		x = 0
		y = 1
		z = 2
		self.active()
		status = bus.read_byte_data(ADDR, 0x00)
		while status==0:
			print bin(status) 
			time.sleep(0.01)
		acc_block_data = bus.read_i2c_block_data(ADDR,0x01,6)
		self.shutdown()
		a[x] = ( (acc_block_data[0] << 8) + acc_block_data[1] ) >> 2
		a[y] = ( (acc_block_data[2] << 8) + acc_block_data[3] ) >> 2
		a[z] = ( (acc_block_data[4] << 8) + acc_block_data[5] ) >> 2
		# Convert 2's complement to integer
		for i in range(0,3):
			if (a[i]>>13)==1:
				a[i] -= 1<<14
		return a

	def active(self):
		# EN = high
		os.system("echo 1 > /sys/class/gpio/gpio25/value")
		return

	def shutdown(self):
		# EN = low
		os.system("echo 0 > /sys/class/gpio/gpio25/value")
		return


# Main
mma = Mma8491q()
x = 0
y = 1
z = 2

try:
	while 1:
		a = mma.get_acc()
		print "MMA8491Q:\tX.", a[x], "mg", "\tY.", a[y], "mg", "\tZ.", a[z], "mg"
		time.sleep(0.1)
except KeyboardInterrupt:
	print
finally:
	mma.shutdown()
	os.system("echo 25 > /sys/class/gpio/unexport")		# Disable GPIO 25 (pin 22 - GPIO_GEN6)
