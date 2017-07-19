from libdispatcheraccess cimport TParamsComputer


cdef class ParamsComputer:
    cdef TParamsComputer* _pc
    def __cinit__(self):
        self._pc = new TParamsComputer()
        

    def __dealloc__(self):
        del self._pc

    def calculate(self, int parameter_id, double value):
        return self._pc.calculate(parameter_id, value)

    def invCalculate(self, int parameter_id, double value):
        return self._pc.invCalculate(parameter_id, value)

    def updateTF(self):
        self._pc.updateTF()

    def fileVersion(self):
        return self._pc.fileVersion()

    def unit(self, int parameter_id):
        cdef string out = self._pc.unit(parameter_id).toStdString()
        return out.decode('UTF-8')

    def rawUnit(self, int parameter_id):
        cdef string out = self._pc.rawUnit(parameter_id).toStdString()
        return out.decode('UTF-8')

    def precision(self, int parameter_id):
        return self._pc.precision(parameter_id)

    def hasTf(self, int parameter_id):
        return self._pc.hasTf(parameter_id)

    def canInvCalculate(self, int parameter_id):
        return self._pc.canInvCalculate(parameter_id)

    def realName(self, int parameter_id):
        cdef string out = self._pc.realName(parameter_id).toStdString()
        return out.decode('UTF-8')

    def dispName(self, int parameter_id):
        cdef string out = self._pc.dispName(parameter_id).toStdString()
        return out.decode('UTF-8')

    def description(self, int parameter_id):
        cdef string out = self._pc.description(parameter_id).toStdString()
        return out.decode('UTF-8')
