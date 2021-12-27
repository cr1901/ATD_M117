import serial
import csv

def csv_row(inp, out):
    # Modified from: https://stackoverflow.com/a/8898859
    def bits(number, len):
        curr = 0
        while curr < len:
           yield number & 1
           number = number >> 1
           curr = curr + 1

    in_map = [
        "SW 1",
        "SW 2",
        "SW 3",
        "A16",
        "A17",
        "A18",
        "A19",
        "Delayed /SMEM{R,W}",
        "/REFRESH",
        "/SMEMW",
        "/SMEMR"
    ]

    out_map = [
        "/WE All Banks",
        "/RAS All Banks",
        "Data Bus Direction",
        "/CAS Bank 1",
        "/CAS Bank 2",
        "/CAS Bank 3",
        "DRAM A8 All Banks"
    ]

    if inp is None or out is None:
        return in_map + out_map

    row_dict = dict()

    for n_i, b_i in enumerate(bits(inp, 11)):
        row_dict[in_map[n_i]] = b_i

    for n_o, b_o in enumerate(bits(out, 7)):
        row_dict[out_map[n_o]] = b_o

    return row_dict



def do_PALdump(do_csv, port, out_file):
    print("First read... reset iCEBreaker now.")
    with serial.Serial(port, 115200, timeout=None) as ser:
        contents1 = ser.read(2048)

    print("Second read... reset iCEBreaker now.")
    with serial.Serial(port, 115200, timeout=None) as ser:
        contents2 = ser.read(2048)

    if contents1 == contents2:
        print("Read appears okay. Dumping contents into file...")

        if do_csv:
            with open(out_file, "w") as csvfile:
                fieldnames = csv_row(None, None)
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for n, c in enumerate(contents1):
                    writer.writerow(csv_row(n, c))
        else:
            with open(out_file, "w") as fp:
                for n, c in enumerate(contents1):
                    fp.write("{0:011b}: {1:07b}\n".format(n, c))
