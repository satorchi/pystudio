from libcpp cimport bool
from libdispatcheraccess cimport TDispatcherAccess
from libqt cimport processEvents, QList, QMutex, QMutexLocker, quint8, quint16, quint32
import time

cdef QMutex _mutex
cdef bool *_requestsArrived = 256 * [False]
MAX_UINT16 = 65535


class TimeoutError(Exception):
    pass


cdef class DispatcherAccess


cdef void requestArrived(int num) nogil:
    cdef QMutexLocker *locker = new QMutexLocker(&_mutex)
    _requestsArrived[num] = True
    del locker


cdef int convert_requested_parameters(DispatcherAccess da, object parameters,
                                      QList[quint32] *meta_ids,
                                      QList[quint32] *out) except 1:
    cdef quint32 paramId
    for parameter in parameters:
        if not isinstance(parameter, str):
            raise TypeError('Invalid parameter type.')
        param = da.parameters[parameter.strip()]
        meta_ids.append(<quint32>param.id)
        if param.id & cMETA_FLAG:
            paramId = param.id & ~cMETA_FLAG
            for i in range(param.shape[0]):
                out.append(<quint32>paramId)
                paramId += 1
        else:
            out.append(<quint32>param.id)
    return 0


cdef class AbstractRequest:
    cdef public int id
    cdef public int timeout
    cdef DispatcherAccess da
    cdef QList[quint32] paramMetaIds
    cdef str error_msg

    def __cinit__(self, DispatcherAccess da not None, object parameters,
                  int timeout, *args):
        self.da = da
        self.timeout = timeout

    def __dealloc__(self):
        if self.id >= 0:
            self.da._da.disableOneRequestedParameters(<quint8>self.id)

    def _check(self, bool isValid, str watched=None):
        if self.id < 0:
            raise RuntimeError(
                'Rejected request (size too big, too many sent requests...)')
        if not isValid:
            raise RuntimeError('Request failure.')
        if watched is None:
            self.error_msg = 'The request timed out.'
        else:
            self.error_msg = (
                "The request timed out because the watched parameter '{0}' did"
                " not change.".format(watched))

    def abort(self):
        """
        Abort request.

        """
        self.da._da.disableOneRequestedParameters(<quint8>self.id)

    def next(self):
        """
        Wait until request completion and return the requested parameters.

        A copy of the requested parameter values is returned. Here we precisely
        do what TDispatcherKernelScriptEngine's ValueForId does, in the sense
        that there is no guarantee that the returned parameter value is what
        the dispatcher transferred when it sent a "request arrived" signal,
        because the unprotected buffer held by TParametersTable may have been
        overwritten in the meantime by the following transfers, in the case of
        persistent or concurrent requests.
        For the same reason, there is also no guarantee that the parameter
        values returned in the output tuple do originate from the same
        transfer.
        At least, the copy which is performed insures that the returned values
        won't be modified between two calls to this method.

        """
        self.wait()
        out = tuple(self.da.parameters[self.paramMetaIds.at(i)].value.copy()
                    for i in range(self.paramMetaIds.count()))
        if len(out) == 1:
            out = out[0]
        return out

    def test(self):
        """
        Return True if the request has arrived.

        """
        cdef QMutexLocker *locker = new QMutexLocker(&_mutex)
        out = _requestsArrived[self.id]
        if out:
            _requestsArrived[self.id] = False
        del locker
        return out

    def wait(self):
        """
        Wait until request arrives.

        On timeout, raise a TimeoutError exception.

        """
        time0 = time.time()
        while not self.test():
            time.sleep(0.001)
            processEvents()
            if 1000 * (time.time() - time0) > self.timeout:
                self.abort()
                raise TimeoutError(self.error_msg)


cdef class RequestOneTime(AbstractRequest):
    def __cinit__(self, DispatcherAccess da not None, object parameters,
                  int timeout, object trigger=0):
        cdef QList[quint32] paramIds
        convert_requested_parameters(da, parameters, &self.paramMetaIds, &paramIds)
        cdef quint32 watchedId
        cdef bool isValid = False
        cdef QMutexLocker *locker = new QMutexLocker(&_mutex)
        if isinstance(trigger, str):
            watchedId = da.parameters[trigger].id & ~cMETA_FLAG
            self.id = da._da.requestOneTimeSynchroParameters(paramIds, watchedId, &isValid)
            self._check(isValid, trigger)
        else:
            trigger = max(int(trigger), 0)
            if trigger > MAX_UINT16:
                raise ValueError('Delay cannot exceed {0} ms.'.
                                 format(MAX_UINT16))
            self.id = da._da.requestOneTimeTimeoutParameters(paramIds, <quint16>trigger, &isValid)
            self.timeout = max(timeout, trigger + trigger // 2)
            self._check(isValid)
        _requestsArrived[self.id] = False
        del locker


cdef class RequestPersistent(AbstractRequest):
    def __cinit__(self, DispatcherAccess da not None, object parameters,
                  int timeout, object trigger, int every=1):
        cdef QList[quint32] paramIds
        convert_requested_parameters(da, parameters, &self.paramMetaIds,
                                     &paramIds)
        cdef quint32 watchedId
        cdef bool isValid = False
        cdef QMutexLocker *locker = new QMutexLocker(&_mutex)
        if trigger is None:
            trigger = parameters[0]
        if isinstance(trigger, str):
            watchedId = da.parameters[trigger].id & ~cMETA_FLAG
            if every > MAX_UINT16:
                raise ValueError(
                    'Argument every cannot exceed {0}.'.format(MAX_UINT16))
            every = max(every, 1)
            self.id =  da._da.requestSynchroParameters(
                paramIds, watchedId, <quint16>every, &isValid)
            self._check(isValid, trigger)
        else:
            if every != 1:
                raise ValueError(
                    'Argument every can be specified only if the trigger is a '
                    'parameter.')
            trigger = max(int(trigger), 1)
            if trigger > MAX_UINT16:
                raise ValueError('Period cannot exceed {0} ms.'.
                                 format(MAX_UINT16))
            self.id = da._da.requestTimeoutParameters(
                paramIds, <quint16>trigger, &isValid)
            self.timeout = max(timeout, trigger + trigger // 2)
            self._check(isValid)
        _requestsArrived[self.id] = False
        del locker
