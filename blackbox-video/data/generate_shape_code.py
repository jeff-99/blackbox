import csv
import json


# total radius of image
height = 375


# read and convert image tuples ( angle, radius) to separate lists of commands for the motorcycle
angle_mods = []
radii = []

with open('motor.csv', 'r') as f:
    reader = csv.reader(f,delimiter=',')
    for line in reader:
        angle_mod = float(line[0]) - 90.0
        angle_mods.append(angle_mod)

        radius = float(line[1]) / height
        radius_string = "{} * self.radius".format(radius)
        radii.append(radius_string)

print(json.dumps(radii).replace('"',''))
print(json.dumps(angle_mods))


# read and convert image tuples ( angle, radius) to separate lists of commands for the headlights
angle_mods2 = []
radii2 = []
with open('headlight.csv', 'r') as f:
    reader = csv.reader(f,delimiter=',')
    for line in reader:
        angle_mod = float(line[0]) - 90.0
        angle_mods2.append(angle_mod)

        radius = float(line[1]) / height
        radius_string = "{} * self.radius".format(radius)
        radii2.append(radius_string)

print(json.dumps(radii2).replace('"',''))
print(json.dumps(angle_mods2))

