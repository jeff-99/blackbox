#!/bin/sh

# get gpsd server!
sudo apt-get install gpsd gpsd-clients python-gps rsync
sudo apt-get install libjpeg-dev

# debian jessie fix to stop default gpsd instance
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket

# run gpsd !
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock

# install python
sudo apt-get install python3 python3-pip

# install for Bno055
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3-smbus python3-pip git

cd ~
git clone https://github.com/adafruit/Adafruit_Python_BNO055.git
cd Adafruit_Python_BNO055
sudo python3 setup.py install