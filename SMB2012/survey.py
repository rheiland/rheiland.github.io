
import sys
import string
import re

linecount = -1

def processLine(line, output):
    global linecount
    line = string.strip(line) + "\n"
    if line[0] == '#':
        output.write(line)
    else:
        linecount += 1
        if (linecount % 2) == 0:
            output.write('Q1: ' + line)
        else:
            output.write('Q2: ' + line + '\n')

#        if string.find(line, 'cockroach') > -1:

        n = len(line)
        keys = string.split(line)

        if 'cockroach' in keys:
            print '------> found a cockroach!'


def usage():
    msg = """Usage:\n  python survey.py survey.txt \n
"""
    print msg


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    if len(sys.argv) > 2:
        usage()
        sys.exit(1)

    name = sys.argv[1]
    output = sys.stdout
    input = open(name, 'r')
    
    for line in input.readlines():
        processLine(line, output)
    input.close()

    output.close()


if __name__ == "__main__":
    main()

