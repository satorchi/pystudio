from __future__ import print_function
from collections import namedtuple
import csv
import itertools
import re
import os

FILENAME = os.path.join(os.path.dirname(__file__), 'data', 'parameters.csv')

TYPE_CODE = {
    'uint8': 0x00,
    'uint16': 0x01,
    'uint24': 0x02,
    'uint32': 0x03,
    'uint64': 0x07,
    'int8': 0x08,
    'int16': 0x09,
    'int24': 0x0A,
    'int32': 0x0B,
    'int64': 0x0F,
    'float': 0x13,
    'double': 0x27,
    'bytearr': 0x40,
    'string': 0x80,
    '8': 0x00,
    '16': 0x01,
    '24': 0x02,
    '32': 0x03,
    '64': 0x07,
}


ParameterEntry = namedtuple('ParameterEntry',
                            'name description type shape ubound use_tf')

""" $modified: Thu 29 Jun 2017 10:10:54 CEST
    rxType now includes string
"""
rxType = re.compile(r"""
    (?P<type>\d+|int\d+|float|double|string)       # type: 4, int8
    (\[(?P<size>\d+)(:(?P<ubound>[A-Za-z0-9_]+))?\])?  # size of array: [16], [16:ubound]
    (\)(?P<shape>(\[\d+\])+))?              # replications: (8[3])[2][2]""", re.VERBOSE)


def read_params(filename=FILENAME):
    """
    Extract parameter name, description, type, dimensions, upper bound and
    whether or name a parameter should have TF (transfer function) counterpart
    from the original csv file.

    """
    out = []
    nskip = 3
    with open(filename) as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        for _ in range(nskip):
            next(reader)
        for row in reader:
            name = '{0[0]}_{0[1]}'.format(row)
            description = row[2]
            use_tf = row[4] == 'yes'
            match = rxType.search(row[3])
            if match is None:
                raise ValueError('Cannot read row {0}'.format(row))                
            ubound = match.group('ubound')
            mshape = match.group('shape')
            if mshape is None:
                shape = ()
            else:
                shape = tuple(int(_)
                              for _ in mshape[1:-1].replace('][', ' ').split())
            try:
                ptype = TYPE_CODE[match.group('type')]
            except:
                raise ValueError("Unknown parameter type:'{}'.".
                                 format(match.group('type')))
            try:
                size = int(match.group('size'))
                if size == 0:
                    raise ValueError('The case (...[0])[...] is not handled.')
                shape += (size,)
            except TypeError:
                pass
            entry = ParameterEntry(
                name, description, ptype, shape, ubound, use_tf)
            out.append(entry)

    filename_dispatcher = os.path.join(os.path.dirname(__file__), 'data',
                                       'parameters_dispatcher.txt')
    with open(filename_dispatcher) as f:
        for line in f:
            name, ptype, description = line.split(' ; ')
            entry = ParameterEntry(
                name, description, int(ptype), (), None, False)
            out.append(entry)
            
    return out


def read_all_params(filename=FILENAME):
    """
    Read the parameter table and add entries to access specific parts of
    the multi-dimensional parameters such as QUBIC_PreviewRawData. For example,
    the parameter QUBIC_PreviewRawData_1_24 accesses
    QUBIC_PreviewRawData[1][24].

    """
    params = read_params(filename)
    out = []
    for param in params:
        out.append(param)
        if len(param.shape) > 1:
            shape = (param.shape[-1],)
            for indices in itertools.product(
                    *[range(_) for _ in param.shape[:-1]]):
                name = '{0}_{1}'.format(
                    param.name, '_'.join(str(i) for i in indices))
                entry = ParameterEntry(
                    name, param.description, param.type, shape, param.ubound,
                    param.use_tf)
                out.append(entry)
    return out
