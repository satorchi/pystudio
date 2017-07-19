from __future__ import print_function
from collections import namedtuple
import os

FILENAME = os.path.join(
    os.path.dirname(__file__), 'data', 'projectOptions.ini')

CommandEntry = namedtuple('CommandEntry',
                          'name id nbytes args format description')

ArgumentEntry = namedtuple('ArgumentEntry',
                           'name size pyarg cytype nptype dstype rtype')

NBYTES_CODE = {
    1: 'uint8',
    2: 'uint16',
    3: 'uint32', # ASIC_RowColumnRange handled as quint32 by dispatcher access
    4: 'uint32',
    8: 'uint64',
}


def convert_arg(name, rtype):
    atype = rtype
    try:
        size, atype = atype.split('*')
        size = int(size)
    except ValueError:
        size = 0
    try:
        nbits = int(atype)
        if nbits < 1:
            raise ValueError('Invalid command argument type.')
        nbytes = (nbits - 1) // 8 + 1  # least number of bytes to store nbits
        type_ = NBYTES_CODE[nbytes]
        pyarg = 'int ' + name
        cytype = 'q' + type_
        nptype = 'np.' + type_
        if size == 0:
            dstype = 'int'
        else:
            dstype = type_
    except ValueError:
        pyarg = {'bytearray': '{0} not None',
                 'double': 'float {0}',
                 'float': 'float {0}',
                 'string_0': 'str {0}'}[atype].format(name)
        cytype = {'bytearray': 'QByteArray',
                  'double': 'double',
                  'float': 'float',
                  'string_0': 'QString'}[atype]
        nptype = {'bytearray': '',
                  'double': 'np.float64',
                  'float': 'np.float32',
                  'string_0': ''}[atype]
        dstype = {'bytearray': 'uint8[:]',
                  'double': 'float64',
                  'float': 'float32',
                  'string_0': 'str'}[atype]
    if size > 0:
        pyarg = name + ' not None'
        dstype += '[{}]'.format(size)
    if atype == 'bytearray':
        pyarg
    return ArgumentEntry(name, size, pyarg, cytype, nptype, dstype, rtype)


def read_command(line):
    try:
        icomment = line.index('#')
        line, description = line[:icomment], line[icomment+1:]
    except ValueError:
        description = ''
    line = line.strip()
    description = description.strip()
    info = [_.strip() for _ in line.split(',')]
    name = info[0]
    id = int(info[1])
    nbytes = int(info[2])
    args = [convert_arg(info[i], info[i+1])
            for i in range(4, len(info)-1, 2)]
    format = info[-1]
    return CommandEntry(
        name, id, nbytes, args, format, description)


def read_commands(filename=FILENAME):
    out = []
    with open(filename) as f:
        while True:
            line = f.readline()
            if line.startswith('[commands]'):
                break
        for line in f:
            line = line.strip()
            if line == '':
                continue
            if line == '[telemetries]':
                break
            line = line.replace(r'\t', ' ').replace(r'\n', '\n')
            pos = line.index('=')
            section = line[:pos]
            if section == r'trash\commands':
                continue
            line = line[pos+2:-1]
            out.extend([read_command(_) for _ in line.split('\n')
                        if len(_) > 0 and not _.startswith('#')])

    filename2 = os.path.join(
        os.path.dirname(__file__), 'data', 'commands_dispatcher.txt')
    with open(filename2) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line.startswith('#'):
                continue
            out.append(read_command(line))
    return out
