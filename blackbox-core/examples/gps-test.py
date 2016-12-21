from adapters import GPSAdapter

x = GPSAdapter()
for i in range(0,1000):
    gps = x.get_current_gps()
    print(gps)
