from libdispatcheraccess cimport TDispatcherAccess

ctypedef void (*slot_request)(int)

cdef extern from "helpers.h":
    void connect_request(TDispatcherAccess*, slot_request)
 
