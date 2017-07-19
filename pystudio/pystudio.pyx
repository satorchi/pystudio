from libdispatcheraccess cimport (
    MAX_NB_REQUEST_PER_CLIENT as cMAX_NB_REQUEST_PER_CLIENT,
    TF_FLAG as cTF_FLAG)
cdef int cMETA_FLAG = cTF_FLAG * 2
_TF_FLAG = cTF_FLAG
_META_FLAG = cMETA_FLAG
_MAX_NB_REQUEST_PER_CLIENT = cMAX_NB_REQUEST_PER_CLIENT

include "parameters.pyx"
include "paramscomputer.pyx"
include "dispatcheraccess.pyx"
include "requests.pyx"
