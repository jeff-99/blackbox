import csv
import random
import time

def nice_angles():
    return list(range(-45,30,2)) + list((reversed(range(-65,30,2)))) + list(range(-65,0,5)) + list(range(0,80,3))

def generate_data_record(prev_record):
    angle_mod = float(random.randint(-10,10))
    speed_mod = 0
    if random.randint(0,2) == 1:
        speed_mod = float(random.randint(-5,5))
    if not prev_record is None:
        return (prev_record[0] + angle_mod, abs(prev_record[1] + speed_mod),prev_record[2] + 0.25)
    else:
        return (0 + angle_mod, 100 + speed_mod, time.time())

def generate_data():
    f = open('data.csv','w')
    writer = csv.writer(f)
    previous = None
    for i in range(0,10000):
        data = generate_data_record(previous)
        previous = data

        writer.writerow(data)
    f.close()


if __name__ == '__main__':
    generate_data()