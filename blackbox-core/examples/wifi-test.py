import wifi

cell = wifi.Cell.where('wlan0',lambda c: c.ssid == 'Wifi Slort')[0]
scheme = wifi.Scheme.for_cell('wlan0','home',cell,'W59VDL43')
scheme.save()
scheme.activate()