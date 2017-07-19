from .pystudio import DispatcherAccess, TimeoutError
from . import utils

def _check_dispatcher_files():
    import os
    import sys
    msg = []
    dest = os.path.dirname(sys.executable)
    src = os.path.join(os.path.dirname(__file__), 'data')
    for f in ('parametersDescription.dispatcher',
              'parametersTF.dispatcher'):
        f_ = os.path.join(dest, f)
        if not os.path.exists(f_):
            msg.append("The file '{}' has not been copied into '{}'.".
                       format(os.path.join(src, f), dest))
    if len(msg) > 0:
        raise ImportError('\n'.join(msg))

def get_client():
    from . import pystudio
    return pystudio._last_client

_check_dispatcher_files()

__version__ = u'2.0.0'
