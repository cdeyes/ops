# -*- coding: utf-8 -*-
import string
import random
import getopt
import sys


def generate_string(mode, slen):
    if mode == 's':
        pwd = ''.join([(string.letters+string.digits+'@#%^&*=')[x]for x in random.sample(range(69), int(slen))])
    else:
        pwd = ''.join([(string.letters+string.digits)[x] for x in random.sample(range(62), int(slen))])
    return pwd


def merge(mode, lens):
    count = 62
    cs = ''
    if lens < count:
        cs = generate_string(mode, lens)
    else:
        quotient = lens / count
        remainder = lens % count
        for i in range(quotient):
            cs = cs + generate_string(mode, count)
        cs = cs + generate_string(mode, remainder)
    return cs


def main():
    mode = 'w'
    lens = 14
    limit = 256
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:l:", ['help'])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    if len(sys.argv) == 1:
        info = generate_string(mode, lens)
    else:
        for o, a in opts:
            if o in ("-h", "--help"):
                print "%s -m (w|s) -l numbers" % sys.argv[0]
                print "-m w is letters+digits, s is add specital characters;default is w"
                print "-l len , defualt is 14"
                sys.exit(1)
            elif o == "-m":
                mode = a
                modes = ('w', 's')
                if mode not in modes:
                    mode = 'w'
            elif o == "-l":
                if a.isdigit():
                    if int(a) <= limit:
                        lens = int(a)
        info = merge(mode, lens)
    return info


if __name__ == '__main__':
    print main()
