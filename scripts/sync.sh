#!/usr/bin/env bash

rsync -azP --delete --dry-run $1 pi@192.168.1.201:/home/pi/blackbox