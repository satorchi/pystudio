cimport numpy as np
from libcpp cimport bool
from libcpp.string cimport string
from libdispatcheraccess cimport TParametersTable
from libqt cimport quint8, quint16, quint32
from .parameters import read_all_params, ParameterEntry


cdef class DispatcherAccess


class ParameterTable(object):
    """
    Store a table of parameters.

    Except for the QString case, the parameter value is a view of
    the parameter member of TParametersTable class (i.e.: there is not copy).

    """
    #cdef object _params
    #cdef quint32 NETQUIC_rate
    NETQUIC_rate=None
    
    def __init__(self, params):
        self._params = params
        for param in params:
            setattr(self, param.name, param)

    def __getitem__(self, value):
        if isinstance(value, str):
            if not hasattr(self, value):
                raise ValueError("Invalid parameter name: '{}'.".format(value))
            return getattr(self, value)
        value = int(value)
        for param in self._params:
            if param.id == value:
                return param
        raise ValueError("Invalid parameter value: '{}'.".format(value))

    def __len__(self):
        return len(self._params)

    def __iter__(self):
        return iter(self._params)
            

cdef class Parameter:
    cdef void *_ptr
    cdef void *_ptr_bound
    cdef public str name
    cdef public int id
    cdef public int type
    cdef int ubound
    cdef int s1

    def __cinit__(self, str name, int id, int ubound, int s1, *args):
        if s1 < 0:
            raise ValueError('Invalid parameter shape.')
        self.name = name
        self.id = id
        self.ubound = ubound
        self.s1 = s1

    def __str__(self):
        out = '<{0} {1}'.format(type(self).__name__, self.name, self.value)
        if len(self.shape) == 0:
            out += ' = {0}'.format(self.value[()])
        else:
            value = self.value.ravel()
            out += ' = [{0}... {1}]'.format(value[0], value[-1])
        out += '>'
        return out

    __repr__ = __str__

    property shape:
        def __get__(self):
            if self.s1 == 0:
                return ()
            return (self.get_bound(),)

    cdef int get_bound(self):
        cdef int bound
        if self.ubound == -1:
            return max(1, self.s1)
        if self.ubound == 0:
            bound = (<quint8*>self._ptr_bound)[0]
        elif self.ubound == 1:
            bound = (<quint16*>self._ptr_bound)[0]
        else:
            raise ValueError("Invalid bound type: '{}'.".format(self.ubound))
        return max(0, min(self.s1, bound))


cdef class Parameter2d(Parameter):
    cdef int s2
    def __cinit__(self, str name, int id, int ubound, int s1, int s2, *args):
        self.s2 = s2
    property shape:
        def __get__(self):
            return (self.s2, self.get_bound())


cdef class Parameter3d(Parameter2d):
    cdef int s3
    def __cinit__(self, str name, int id, int ubound, int s1, int s2, int s3):
        self.s3 = s3
    property shape:
        def __get__(self):
            return (self.s3, self.s2, self.get_bound())


cdef class ParameterUInt8(Parameter):
    def __cinit__(self, *args):
        self.type = 0x00
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.uint8_t[::1] view = <np.uint8_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterUInt16(Parameter):
    def __cinit__(self, *args):
        self.type = 0x01
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.uint16_t[::1] view = <np.uint16_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterUInt32(Parameter):
    def __cinit__(self, *args):
        self.type = 0x03
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.uint32_t[::1] view = <np.uint32_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterUInt64(Parameter):
    def __cinit__(self, *args):
        self.type = 0x07
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.uint64_t[::1] view = <np.uint64_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterInt8(Parameter):
    def __cinit__(self, *args):
        self.type = 0x08
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.int8_t[::1] view = <np.int8_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterInt16(Parameter):
    def __cinit__(self, *args):
        self.type = 0x09
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.int16_t[::1] view = <np.int16_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterInt32(Parameter):
    def __cinit__(self, *args):
        self.type = 0x0B
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.int32_t[::1] view = <np.int32_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterInt64(Parameter):
    def __cinit__(self, *args):
        self.type = 0x0F
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.int64_t[::1] view = <np.int64_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterFloat32(Parameter):
    def __cinit__(self, *args):
        self.type = 0x13
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.float32_t[::1] view = <np.float32_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterFloat64(Parameter):
    def __cinit__(self, *args):
        self.type = 0x27
    property value:
        def __get__(self):
            cdef int bound = self.get_bound()
            cdef np.float64_t[::1] view = <np.float64_t[:bound]> self._ptr
            out = np.asarray(view)
            if self.s1 == 0:
                out.shape = ()
            return out


cdef class ParameterString(Parameter):
    def __cinit__(self, *args):
        self.type = 0x80
    property value:
        def __get__(self):
            cdef QString *p = <QString *> self._ptr
            cdef string s = p.toStdString()
            return s.decode('UTF-8')


cdef class Parameter2dUInt8(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x00
    property value:
        def __get__(self):
            cdef np.uint8_t[:, ::1] view = <np.uint8_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dUInt16(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x01
    property value:
        def __get__(self):
            cdef np.uint16_t[:, ::1] view = <np.uint16_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dUInt32(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x03
    property value:
        def __get__(self):
            cdef np.uint32_t[:, ::1] view = <np.uint32_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dUInt64(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x07
    property value:
        def __get__(self):
            cdef np.uint64_t[:, ::1] view = <np.uint64_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dInt8(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x08
    property value:
        def __get__(self):
            cdef np.int8_t[:, ::1] view = <np.int8_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dInt16(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x09
    property value:
        def __get__(self):
            cdef np.int16_t[:, ::1] view = <np.int16_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dInt32(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x0B
    property value:
        def __get__(self):
            cdef np.int32_t[:, ::1] view = <np.int32_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dInt64(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x0F
    property value:
        def __get__(self):
            cdef np.int64_t[:, ::1] view = <np.int64_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dFloat32(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x13
    property value:
        def __get__(self):
            cdef np.float32_t[:, ::1] view = <np.float32_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter2dFloat64(Parameter2d):
    def __cinit__(self, *args):
        self.type = 0x27
    property value:
        def __get__(self):
            cdef np.float64_t[:, ::1] view = <np.float64_t[:self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :self.get_bound()]


cdef class Parameter3dUInt8(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x00
    property value:
        def __get__(self):
            cdef np.uint8_t[:, :, ::1] view = <np.uint8_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dUInt16(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x01
    property value:
        def __get__(self):
            cdef np.uint16_t[:, :, ::1] view = <np.uint16_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dUInt32(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x03
    property value:
        def __get__(self):
            cdef np.uint32_t[:, :, ::1] view = <np.uint32_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dUInt64(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x07
    property value:
        def __get__(self):
            cdef np.uint64_t[:, :, ::1] view = <np.uint64_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dInt8(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x08
    property value:
        def __get__(self):
            cdef np.int8_t[:, :, ::1] view = <np.int8_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dInt16(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x09
    property value:
        def __get__(self):
            cdef np.int16_t[:, :, ::1] view = <np.int16_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dInt32(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x0B
    property value:
        def __get__(self):
            cdef np.int32_t[:, :, ::1] view = <np.int32_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dInt64(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x0F
    property value:
        def __get__(self):
            cdef np.int64_t[:, :, ::1] view = <np.int64_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dFloat32(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x13
    property value:
        def __get__(self):
            cdef np.float32_t[:, :, ::1] view = <np.float32_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class Parameter3dFloat64(Parameter3d):
    def __cinit__(self, *args):
        self.type = 0x27
    property value:
        def __get__(self):
            cdef np.float64_t[:, :, ::1] view = <np.float64_t[:self.s3, :self.s2, :self.s1]> self._ptr
            a = np.asarray(view)
            if self.ubound == -1:
                return a
            return a[:, :, :self.get_bound()]


cdef class ParameterUnhandled(Parameter):
    def __cinit__(self, *args):
        self.type = -1


def convert_parameter(rparam, int iparam, params, bparams, use_tf,
                      DispatcherAccess da not None):
    cdef int s1
    cdef int s2
    cdef int s3
    cdef int id = iparam
    cdef TParametersTable *pt = da._da.parameters()

    if use_tf:
        id |= cTF_FLAG
    name = rparam.name
    ptype = rparam.type
    if rparam.ubound is not None:
        try:
            pbound = bparams[rparam.ubound]
        except KeyError:
            try:
                pbound = next(_ for _ in params if _.name == rparam.ubound)
                bparams[pbound.name] = pbound
            except ValueError:
                raise ValueError("Undefined parameter '{}'.".
                                 format(rparam.ubound))
        ubound = pbound.type
    else:
        ubound = -1
    ndim = len(rparam.shape)
    if ndim == 0:
        s1 = 0
    else:
        s1 = rparam.shape[-1]
    if ndim <= 1:
        if ptype == 0x00:
            param = ParameterUInt8(name, id, ubound, s1)
        elif ptype == 0x01:
            param = ParameterUInt16(name, id, ubound, s1)
        elif ptype == 0x02:
            # ASIC_RowColumnRange stored as quint32
            param = ParameterUInt32(name, id, ubound, s1)
        elif ptype == 0x03:
            param = ParameterUInt32(name, id, ubound, s1)
        elif ptype == 0x07:
            param = ParameterUInt64(name, id, ubound, s1)
        elif ptype == 0x08:
            param = ParameterInt8(name, id, ubound, s1)
        elif ptype == 0x09:
            param = ParameterInt16(name, id, ubound, s1)
        elif ptype == 0x0A:
            param = ParameterInt32(name, id, ubound, s1)
        elif ptype == 0x0B:
            param = ParameterInt32(name, id, ubound, s1)
        elif ptype == 0x0F:
            param = ParameterInt64(name, id, ubound, s1)
        elif ptype == 0x13:
            param = ParameterFloat32(name, id, ubound, s1)
        elif ptype == 0x27:
            param = ParameterFloat64(name, id, ubound, s1)
        elif ptype == 0x80:
            param = ParameterString(name, id, -1, 0)
        else:
            param = ParameterUnhandled(name, id, ubound, s1)
            print("Parameter '{}' of type '{}' is not handled.".
                  format(name, ptype))
    elif ndim == 2:
        s2 = rparam.shape[0]
        if ptype == 0x00:
            param = Parameter2dUInt8(name, id, ubound, s1, s2)
        elif ptype == 0x01:
            param = Parameter2dUInt16(name, id, ubound, s1, s2)
        elif ptype == 0x02:
            param = Parameter2dUInt32(name, id, ubound, s1, s2)
        elif ptype == 0x03:
            param = Parameter2dUInt32(name, id, ubound, s1, s2)
        elif ptype == 0x07:
            param = Parameter2dUInt64(name, id, ubound, s1, s2)
        elif ptype == 0x08:
            param = Parameter2dInt8(name, id, ubound, s1, s2)
        elif ptype == 0x09:
            param = Parameter2dInt16(name, id, ubound, s1, s2)
        elif ptype == 0x0A:
            param = Parameter2dInt32(name, id, ubound, s1, s2)
        elif ptype == 0x0B:
            param = Parameter2dInt32(name, id, ubound, s1, s2)
        elif ptype == 0x0F:
            param = Parameter2dInt64(name, id, ubound, s1, s2)
        elif ptype == 0x13:
            param = Parameter2dFloat32(name, id, ubound, s1, s2)
        elif ptype == 0x27:
            param = Parameter2dFloat64(name, id, ubound, s1, s2)
        else:
            param = ParameterUnhandled(name, id, ubound, s1)
            print("Parameter '{}' of type '{}' is not handled.".
                  format(name, ptype))
    elif ndim == 3:
        s2 = rparam.shape[1]
        s3 = rparam.shape[0]
        if ptype == 0x00:
            param = Parameter3dUInt8(name, id, ubound, s1, s2, s3)
        elif ptype == 0x01:
            param = Parameter3dUInt16(name, id, ubound, s1, s2, s3)
        elif ptype == 0x02:
            param = Parameter3dUInt32(name, id, ubound, s1, s2, s3)
        elif ptype == 0x03:
            param = Parameter3dUInt32(name, id, ubound, s1, s2, s3)
        elif ptype == 0x07:
            param = Parameter3dUInt64(name, id, ubound, s1, s2, s3)
        elif ptype == 0x08:
            param = Parameter3dInt8(name, id, ubound, s1, s2, s3)
        elif ptype == 0x09:
            param = Parameter3dInt16(name, id, ubound, s1, s2, s3)
        elif ptype == 0x0A:
            param = Parameter3dInt32(name, id, ubound, s1, s2, s3)
        elif ptype == 0x0B:
            param = Parameter3dInt32(name, id, ubound, s1, s2, s3)
        elif ptype == 0x0F:
            param = Parameter3dInt64(name, id, ubound, s1, s2, s3)
        elif ptype == 0x13:
            param = Parameter3dFloat32(name, id, ubound, s1, s2, s3)
        elif ptype == 0x27:
            param = Parameter3dFloat64(name, id, ubound, s1, s2, s3)
        else:
            param = ParameterUnhandled(name, id, ubound, s1)
            print("Parameter '{}' of type '{}' is not handled.".
                  format(name, ptype))

    if use_tf:
        param._ptr = pt.paramAddressTF[iparam]
    else:
        param._ptr = pt.paramAddress[iparam]

    if rparam.ubound is not None:
        param._ptr_bound = pt.paramAddress[pbound.id]
    return param


def get_parameters(DispatcherAccess da):
    cdef int i, j
    # cdef TParametersTable _params

    rparams = read_all_params()
    params = []
    paramsTF = []
    bparams = {}
    for i, rparam in enumerate(rparams):
        param = convert_parameter(rparam, i, params, bparams, False, da)
        params.append(param)
        if rparam.use_tf:
            rparam_tf = ParameterEntry(
                rparam.name+'_TF', rparam.description, 0x27, rparam.shape,
                rparam.ubound, False)
            param = convert_parameter(rparam_tf, i, params, bparams, True, da)
            params.append(param)
   
    # As of 28/09/2015, parameter access to 3-dimensional arrays through
    # the Dispatcher Client is limited to either the whole array or each of
    # the last dimension. We provide a transparent access to the last two
    # dimensions by adding new parameters with the flag META.
    # Example: 'QUBIC_WorkingRawData' accesses the whole array and
    # 'QUBIC_WorkingRawData_0_0' accesses the timeline of the first TES
    # of the first ASIC. Here we add 'QUBIC_WorkingRawData_0' to access
    # the timelines of all the TES of the first ASIC.
    for i, rparam in enumerate(rparams):
        shape = rparam.shape
        if len(shape) < 3:
            continue
        if rparam.use_tf:
            import warnings
            warnings.warn('Code should be updated to make meta-parameters han'
                          'dle TF parameters.')
            continue
        for j in range(shape[0]):
            iparam = i + j * shape[1] + 1
            rparam_ = ParameterEntry(
                '{0}_{1}'.format(rparam.name, j), rparam.description,
                rparam.type, rparam.shape[1:], rparam.ubound, False)
            param = convert_parameter(
                rparam_, iparam, None, bparams, False, da)
            param.id |= cMETA_FLAG
            params.append(param)
            # _params=params
    return ParameterTable(params)
    # return params
