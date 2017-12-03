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


def main(in_path, out_path):
    '''
    Extracts SSDSim compadible trace data
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    with open(in_path) as in_file, open(out_path, 'w') as out_file:
        end_of_header = False
        for next_line in in_file:
            # Remove Excess Whitespace
            line = " ".join(next_line.split())

            # Process Header
            if not end_of_header:
                if line.startswith("DiskRead"):
                    logger.debug(line)
                elif line.startswith("EndHeader"):
                    end_of_header = True
                continue

            # extract the record and parse its fields
            if line.startswith("DiskWrite") or line.startswith("DiskRead"):
                record = line.split(", ")
                # format:   time   device   offset   size   op
                try:
                    fields = [micro_to_nano(record[1]),
                              record[8],
                              hexadecimal_to_decimal(record[5]),
                              hexadecimal_to_decimal(record[6]),
                              operation_to_int(record[0])]
                except IndexError:
                    logger.debug(line)
                    continue
                new_line = " ".join(fields)
                out_file.write(new_line + "\n")


if __name__ == "__main__":
    if len(sys.argv) is 1:
        main("raw/24Hour_RADIUS.08-30-2007.02-49-AM.csv", "Radius.trace")
        main("raw/Exchange.12-13-2007.04-01-AM.trace.csv", "Exchange.trace")
        main("raw/DevDivRelease.03-06-2008.10-22-AM.trace.csv", "DevToolReleaseServer.trace")
        main("raw/CFS.2008-03-10.12-56.trace.csv.csv", "MSNStorageMetaDataServer.trace")
        main("raw/MSNFS.2008-03-10.03-03.trace.csv.csv", "MSNStorageServer.trace")
    elif len(sys.argv) is 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("[Usage]\n\tpython parse [input file] [output file]\n")
