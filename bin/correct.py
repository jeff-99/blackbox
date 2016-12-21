import sys, time

def main():
    b = time.time()
    last_line = []
    outfilename  = sys.argv[1].split(".")[0] + "_fixed.csv"
    with open( outfilename, 'w') as outfile:
        with open(sys.argv[1], 'r') as infile:
            for new_line in infile:
                data = new_line.split(",")
                if data[1] is None or data[1] == 'None':
                    data[1] = last_line[1]
                    data[2] = last_line[2]
                    data[3] = last_line[3]

                last_line = data

                outfile.write(",".join(data))
    e = time.time()
    r = (e-b) * 1000
    print("Runtime in ms= {}".format(r))

if __name__ == '__main__':
    main()