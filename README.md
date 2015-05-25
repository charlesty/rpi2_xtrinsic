# Raspberry Pi 2 and the Xtrinsic Sensor Board



### Description
---------------

This project aims to use [Freescale's Xtrinsic Sensor Board](http://www.element14.com/community/docs/DOC-65084/l/xtrinsic-sensor-board) on the Raspberry Pi 2.

This sensor board includes three i2c sensors :

- MAG3110  : three-axis magnetometer
- MMA8491Q : three-axis accelerometer
- MPL3115  : altitude, pressure and temperature sensor

It was tested with the latest Minibian OS (minimal Raspbian, Linux 3.18) and Python 2.7.

I based my work on

- [rpi_sensor_board GIT](http://git.oschina.net/embest/rpi_sensor_board)
- [MPL3115A2 sensor with Raspberry Pi](http://ciaduck.blogspot.fr/2014/12/mpl3115a2-sensor-with-raspberry-pi.html)

The rpi_sensor_board project didn't worked: every script was hanging.

That's why I developped this project.



### Requirements
----------------

1. You must install the `python-smbus` package on the Raspberry Pi 2 :

        sudo apt-get install python-smbus

2. Enable I2C on the Raspberry Pi 2 :

  - Add the following lines to `/etc/modules` :

            i2c-dev
            i2c-bcm2708

  - Add the following lines to `/etc/rc.local` before `exit 0`, in order to use repeated start (details [here](https://www.raspberrypi.org/forums/viewtopic.php?f=44&t=15840&start=25)):

            sleep 3
            echo -n 1 > /sys/module/i2c_bcm2708/parameters/combined

Then, reboot.



### How to use & output
-----------------------

Go to the path where the script are, and run a script in this way. For instance:

    cd ~/rpi2_xtrinsic
    sudo python mag3110.py

**Output**

- mag3110.py : it will output magnetic field on the three axis in micro Tesla.
- mma8491q.py : it will output the acceleration in milli g ( 1g = 9,81m/s^2 ).
- mpl3115a1.py : it will output the temperature in Celsius degree, and either the pressure in Pascal, either the altitude in meter.

**Warning**

The altimeter gave me incoherent values.
Indeed, it sometimes returns negative altitude whereas I am at positive altitude.
