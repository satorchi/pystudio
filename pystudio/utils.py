from .pystudio import (
    _MAX_NB_REQUEST_PER_CLIENT as MAX_NB_REQUEST_PER_CLIENT,
    _META_FLAG as META_FLAG, _TF_FLAG as TF_FLAG)
import warnings


class PyStudioWarning(UserWarning):
    pass

warnings.simplefilter('always', category=PyStudioWarning)
