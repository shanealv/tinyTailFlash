import sys
import logging


def operation_to_int(ope):
    '''
    Converts a operation string to an int
    '''
    if ope == "DiskWrite":
        return "0"
    elif ope == "DiskRead":
        return "1"


def hexadecimal_to_decimal(hex_str):
    '''
    Converts a hex string byte offset to subpage offset
    NOTE: subpage capacity = 512 bytes, see page.parameters
    '''
    return str(int(hex_str, 0) // 512)


def micro_to_nano(microsecs):
    '''
    Converts a decimal string of microseconds to nanoseconds
    '''
    return microsecs + "000"


def scan_trace(file_name, on_visit):
    '''
    Scans a trace CSV file
    Calls on_visit(record, device) on each R/W line
    '''
    reads = 0
    writes = 0
    ops = 0
    devices = dict()
    with open(file_name) as trace:
        end_of_header = False
        for next_line in trace:
            # trim whitespace
            line = " ".join(next_line.split())

            # skip header
            if not end_of_header:
                if line.startswith("EndHeader"):
                    end_of_header = True
                continue

            # filter reads and writes
            ops += 1
            if line.startswith("DiskRead"):
                reads += 1
            elif line.startswith("DiskWrite"):
                writes += 1
            else:
                continue

            # extra device and add to counter
            record = line.split(", ")
            if len(record) < 9:
                continue
            device = record[8]
            if device in devices:
                devices[device] += 1
            else:
                devices[device] = 1

            on_visit(record, device)
    return (reads, writes, ops, devices)


def main(in_path, out_path):
    '''
    Extracts SSDSim compadible trace data
    '''
    log = logging.getLogger(__name__)
    log.info("Parsing %s...", in_path)

    # get basic stats
    reads, writes, ops, devices = scan_trace(in_path, lambda record, device: None)
    total = reads + writes
    t_ratio, r_ratio, w_ratio = (total/ops, reads/total, writes/total)
    log.info("Total Lines: %-7d  R: %-7d  W: %-7d  R+W: %-7d", ops, reads, writes, total)
    log.info("Total IO:    %06.3f%%  R: %06.3f%%  W: %06.3f%%", t_ratio, r_ratio, w_ratio)

    max_device = -1
    max_io = 0
    for device in devices:
        if devices[device] > max_io:
            max_device = device

    log.info("Most Common Device is %s with %d iops (%08.5f%%)",
             max_device, devices[max_device], devices[max_device] / total)

    # run again but extract records
    with open(out_path, 'w') as gen:
        def visit(record, device):
            '''
            Saves the records for the most common device
            '''
            if device != max_device:
                return
            fields = [micro_to_nano(record[1]),
                      record[8],
                      hexadecimal_to_decimal(record[5]),
                      hexadecimal_to_decimal(record[6]),
                      operation_to_int(record[0])]
            new_line = " ".join(fields)
            gen.write(new_line + "\n")

        scan_trace(in_path, visit)


if __name__ == "__main__":
    if len(sys.argv) is 1:
        log = logging.getLogger(__name__)
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        log.addHandler(ch)
        main("raw/24Hour_RADIUS.08-30-2007.02-49-AM.csv", "Radius.trace")
        main("raw/Exchange.12-13-2007.04-01-AM.trace.csv", "Exchange.trace")
        main("raw/DevDivRelease.03-06-2008.10-22-AM.trace.csv", "DevToolReleaseServer.trace")
        main("raw/CFS.2008-03-10.12-56.trace.csv.csv", "MSNStorageMetaDataServer.trace")
        main("raw/MSNFS.2008-03-10.03-03.trace.csv.csv", "MSNStorageServer.trace")
    elif len(sys.argv) is 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("[Usage]\n\tpython parse [input file] [output file]\n")
