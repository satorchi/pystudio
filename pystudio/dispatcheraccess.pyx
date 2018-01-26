from libcpp cimport bool
from libhelpers cimport connect_request, slot_request
from libqt cimport (
    QApplication, QByteArray, QList, QString, fromRawData, qint16)
from libdispatcheraccess cimport TDispatcherAccess, TParamsComputer
from collections import OrderedDict
cimport cython
cimport numpy as np
import numpy as np
import re
import types

__all__ = ['DispatcherAccess']

cdef QApplication *_app = NULL
_last_client = None
DEFAULT_TIMEOUT = 5000  # ms

cdef class Parameter
# cdef class ParameterTable
cdef class RequestOneTime
cdef class RequestPersistent

cdef class DispatcherAccess:
    """
    Dispatcher access class.

    Return a client that can send commands and requests to the data server,
    aka the dispatcher.

    """

    # these two variables must be declared here
    # otherwise we get the cython error "cannot convert to python object"
    cdef TDispatcherAccess *_da
    cdef TParamsComputer *_pc

    def __cinit__(self, str dispatcherAddress=None, int dispatcherPort=-1):
        global _app, _last_client
        cdef int argc = 0
        cdef QByteArray dispatcherAddress_
        cdef QString dispatcherAddress__
        
        if _app is NULL:
            _app = new QApplication(argc, <char**>NULL)
        if dispatcherAddress is None:
            self._da = new TDispatcherAccess()
        else:
            dispatcherAddress_ = QByteArray(dispatcherAddress.encode('utf-8'),
                                            len(dispatcherAddress))
            dispatcherAddress__ = QString(dispatcherAddress_)
            self._da = new TDispatcherAccess(dispatcherAddress__,
                                             dispatcherPort)
        self.waitingForAckMode = False
        self.autoUpdateWithRequest = True
        self._da.start()

        ### cannot assign self.parameters because we get the runtime error
        ### "objects is not writable"
        ### this assignment is commented out,
        ### but somehow, the parameters get assigned somewhere along the line... not sure where.
        # self.parameters = get_parameters(self)
        self._pc = new TParamsComputer()
        cdef slot_request slot = &requestArrived
        connect_request(self._da, slot)
        _last_client = self

    def __dealloc__(self):
        del self._da
        del self._pc
        # del self.parameters

    
    property parameters:
        def __get__(self):
            return get_parameters(self)
    
    property connected:
        def __get__(self):
            return self._da.isConnected()

    property lastError:
        def __get__(self):
            cdef string out = self._da.lastError().toStdString()
            return out.decode('UTF-8')

    property state:
        def __get__(self):
            cdef string out = self._da.state().toStdString()
            return out.decode('UTF-8')

    def configure(self, str address, int port):
        """
        Used to (re)configure the Dispatcher communication parameters.

        Parameters
        ----------
        address : str
            Dispatcher IP address
        port : int
            Dispatcher IP port

        """
        cdef QByteArray address_
        cdef QString address__
        address_ = QByteArray(address, len(address))
        address__ = QString(address_)
        self._da.configure(address__, port)

    def resizeTMBuffer(self, int bufferSize):
        """
        Définit la taille du buffer de télémétrie de la librairie.
        À ne modifier que si cela est nécessaire dans le cas où un nombre
        très important de requêtes doit être fait.

        Parameters
        ----------
        bufferSize : int
            New buffer size.

        """
        self._da.resizeTMBuffer(bufferSize)

    property waitingForAckMode:
        """
        The command mode (True: waiting for acknowlegment, False otherwise).

        """
        def __get__(self):
            return self._da.waitingForAckMode()
        def __set__(self, bool value):
            self._da.setWaitingForAckMode(value)

    property waitingForAckTimeOut:
        """
        Timeout in milliseconds when waiting for command acknowlegement.

        """
        def __get__(self):
            return self._da.waitingForAckTimeOut()
        def __set__(self, int value):
            self._da.setWaitingForAckTimeOut(value)

    property subSystemsCommandsLocked:
        def __get__(self):
            return self._da.subSystemsCommandsLocked()
        def __set__(self, bool value):
            self._da.setSubSystemsCommandsLocked(value)

    property fullCommandsLocked:
        def __get__(self):
            return self._da.fullCommandsLocked()
        def __set__(self, bool value):
            self._da.setFullCommandsLocked(value)

    property autoUpdateWithRequest:
        """
        The auto-update mode (True: process request when it arrives and emit
        signal, False: push request into FIFO).

        """
        def __set__(self, bool value):
            self._da.setAutoUpdateWithRequest(value)

    def startSubsystemAccess(self):
        return self._da.startSubsystemAccess()

    def stopSubsystemAccess(self):
        return self._da.stopSubsystemAccess()

    def stopDispatcher(self, int stopCode):
        """ Stop code is parameterCRC() """
        return self._da.stopDispatcher(stopCode)

    '''
    vvvvvvvvvvv
    removed in v3

    def setDebug(self):
        self._da.setDebug()

    removed in v3
    ^^^^^^^^^^^^^
    '''

    def waitMs(self, int milliseconds):
        self._da.waitMs(milliseconds)

    def sendReloadTF(self):
        return self._da.sendReloadTF()

    property dispatcherTFVersionLoaded:
        def __get__(self):
            return self._da.dispatcherTFVersionLoaded()

    def run(self):
        self._da.run()

    property dispatcherAddress:
        def __get__(self):
            cdef string out = self._da.dispatcherAddress().toStdString()
            return out

    property dispatcherPort:
        def __get__(self):
            return self._da.dispatcherPort()

    property stackSize:
        def __get__(self):
            return self._da.stackSize()

    property stackOccupation:
        def __get__(self):
            return self._da.stackOccupation()

    property requestRate:
        def __get__(self):
            return self._da.requestRate()

    property dataRate:
        def __get__(self):
            return self._da.dataRate()

    property nbOverlap:
        def __get__(self):
            return self._da.nbOverlap()

    '''
    vvvvvvvvvvvvv
    removed in V3

    def _emit_request_arrived(self, int num):
        """
        For testing purposes: emit signal that a request has arrived.

        """
        self._da.requestArrived(num)
    
    removed in V3
    ^^^^^^^^^^^^^
    '''

    def abort_requests(self):
        """ Abort all pending persistent requests. """
        self._da.disableAllRequestedParameters()

    def fetch(self, parameters, object trigger=0, int timeout=DEFAULT_TIMEOUT):
        """
        Fetch a parameter or a list of parameters by sending a request
        to the dispatcher and waiting its completion.

        Parameters
        ----------
        parameters : str or sequence of str
            The requested parameters.
        trigger : int or str, optional
            If the trigger is integer, it specifies the delay in ms after which
            the parameters will be returned. Otherwise, it specifies the
            watched parameter whose update will trigger the acquisition of
            the requested parameters.
        timeout : int, optional
            The request timeout in ms, after which the fetch is aborted through
            a TimeoutException.

        Examples
        --------
        To fetch a parameter immediately:
        >>> value = client.fetch(parameter)

        To fetch a parameter after 100 ms:
        >>> value = client.fetch(parameter, 100)

        To fetch a parameter only after the parameter
        'QUBIC_AllPixelsScientificData_0' has changed:
        >>> value = client.fetch(parameter, 'QUBIC_AllPixelsScientificData_0')

        """
        if isinstance(parameters, str):
            parameters = [_.strip() for _ in parameters.split(',')]
        request = RequestOneTime(self, parameters, timeout, trigger)
        return request.next()

    def request(self, parameters, object trigger=None, int every=1,
                int timeout=DEFAULT_TIMEOUT):
        """
        Send a persistent request to the dispatcher.

        Parameters
        ----------
        parameters : str or sequence of str
            The requested parameters.
        trigger : int or str, optional
            If the trigger is integer, it specifies the period in ms at which
            the parameters will be sampled. Otherwise, it specifies the watched
            parameter whose update will trigger the acquisition of the
            requested parameters. If the trigger is not specified, the watched
            parameter will be the first requested parameter, i.e. the request
            will arrive every time the requested parameter changes.
        timeout : int, optional
            The request timeout in ms. It controls the duration after which
            calls to the wait method are aborted through a TimeoutException.

        Examples
        --------
        To send the parameters every 100ms:
        >>> req = client.request(parameters, 100)

        To send the parameter 'QUBIC_AllPixelsScientificData_0' every time it
        changes:
        >>> req = client.request('QUBIC_AllPixelsScientificData_0')

        To send the parameters every time the parameter
        'QUBIC_AllPixelsScientificData_0' changes:
        >>> req = client.request(parameters, 'QUBIC_AllPixelsScientificData_0')

        """
        if isinstance(parameters, str):
            parameters = [_.strip() for _ in parameters.split(',')]
        return RequestPersistent(self, parameters, timeout, trigger, every)

    @cython.boundscheck(False)
    def convertADU2Value(self, parameter, object x not None):
        cdef int i, parameter_id
        cdef double[::1] x__, out_
        if isinstance(parameter, int):
            parameter_id = parameter
        else:
            parameter_id = self.parameters[parameter].id
        x = np.asarray(x, np.float64, 'C')
        x_ = x.ravel()
        out = np.empty_like(x)
        out_ = out.ravel()
        for i in range(x_.size):
            out_[i] = self._pc.calculate(parameter_id, x_[i])
        if x.ndim == 0:
            return out[()]
        return out

    @cython.boundscheck(False)
    def convertValue2ADU(self, parameter, object x not None):
        cdef int i, parameter_id
        cdef double[::1] x__, out_
        parameter_ = self.parameters[parameter]
        parameter_id = parameter_.id
        x = np.asarray(x, np.float64, 'C')
        x_ = x.ravel()
        out = np.empty_like(x)
        out_ = out.ravel()
        for i in range(x_.size):
            out_[i] = self._pc.invCalculate(parameter_id, x_[i])
        out = np.array(out, dtype=parameter_.value.dtype, copy=False)
        if x.ndim == 0:
            return out[()]
        return out

    def sendCustomCommand(self, int asicNum, int id, int cn, corps not None):
        """
        sendCustomCommand(int asicNum, int id, int cn, uint8[:] corps)

        commande customisable

        """
        corps = np.ascontiguousarray(corps)
        if corps.dtype != np.uint8:
            raise TypeError(
                "The command body data type is not uint8.")
        cdef char[::1] corps_ = corps
        cdef QByteArray corps__ = fromRawData(&corps_[0], corps.size)
        cdef bool out = self._da.sendCustomCommand(asicNum, id, cn, corps__)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicParam(self, int asicNum, int address, int value):
        """
        sendSetAsicParam(int asicNum, int address, int value)

        configure l'asic (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicParam(asicNum, address, value)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetTESDAC(self, int asicNum, int shape, int frequency, int amplitude, int offset):
       """

        Specifie le signal de calib a injecter sur les TES mode:0 pas de signal, 1 envoi du signal, shape: 0 sinus, 1 triangle, 2 continu  (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
       cdef bool out = self._da.sendSetTESDAC(asicNum, shape, frequency, amplitude, offset)
       if not out:
           raise RuntimeError(self.lastError)

        
    def sendSetAsicApol(self, int asicNum, int value):
        """
        sendSetAsicApol(int asicNum, int value)

        polarisation des blocs analogiques (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicApol(asicNum, value)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicSpol(self, int asicNum, int value):
        """
        sendSetAsicSpol(int asicNum, int value)

        polarisation des squids (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicSpol(asicNum, value)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicVicm(self, int asicNum, int value):
        """
        sendSetAsicVicm(int asicNum, int value)

        tension de mode commun Vicm (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicVicm(asicNum, value)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicVocm(self, int asicNum, int value):
        """
        sendSetAsicVocm(int asicNum, int value)

        tension de mode commun Vocm (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicVocm(asicNum, value)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicSetColumn(self, int asicNum, int startStopCol):
        """
        sendSetAsicSetColumn(int asicNum, int startStopCol)

        circuit d'adressage: position initiale et finale colonne (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicSetColumn(asicNum, startStopCol)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicSelStartRow(self, int asicNum, int value):
        """
        sendSetAsicSelStartRow(int asicNum, int value)

        circuit d'adressage: position initiale ligne (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicSelStartRow(asicNum, value)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicSelLastRow(self, int asicNum, int value):
        """
        sendSetAsicSelLastRow(int asicNum, int value)

        circuit d'adressage: position finale ligne (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicSelLastRow(asicNum, value)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicRazb(self, int asicNum):
        """
        sendSetAsicRazb(int asicNum)

        Envoi une pulse RAZb (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicRazb(asicNum)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicInib(self, int asicNum):
        """
        sendSetAsicInib(int asicNum)

        Envoi une pulse INIb (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetAsicInib(asicNum)
        if not out:
            raise RuntimeError(self.lastError)


    def sendSetFeedbackTable(self, int asicNum, feedbackTable not None):
        """
        sendSetFeedbackTable(int asicNum, int16[128] feedbackTable)

        configure la table de feedback (128*16bits) pour l'asic asicNum (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        feedbackTable_ = np.ascontiguousarray(feedbackTable, np.int16)
        if feedbackTable_.size != 128:
            raise ValueError("Expected array size of argument 'feedbackTable' is '128'.")
        cdef qint16[::1] feedbackTable__ = feedbackTable_
        cdef bool out = self._da.sendSetFeedbackTable(asicNum, <quint16*>&feedbackTable__[0])
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetOffsetTable(self, int asicNum, offsetTable not None):
        """
        sendSetOffsetTable(int asicNum, int16[128] offsetTable)

        configure la table d'offsets (128*16bits) pour l'asic asicNum (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        offsetTable_ = np.ascontiguousarray(offsetTable, np.int16)
        if offsetTable_.size != 128:
            raise ValueError("Expected array size of argument 'offsetTable' is '128'.")
        cdef qint16[::1] offsetTable__ = offsetTable_
        cdef bool out = self._da.sendSetOffsetTable(asicNum, <quint16*>&offsetTable__[0])
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetMask(self, int asicNum, mask not None):
        """
        sendSetMask(int asicNum, uint8[125] mask)

        configure le masque avec la table mask(128*8bits) pour l'asic asicNum (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        mask_ = np.ascontiguousarray(mask, np.uint8)
        if mask_.size != 125:
            raise ValueError("Expected array size of argument 'mask' is '125'.")
        cdef quint8[::1] mask__ = mask_
        cdef bool out = self._da.sendSetMask(asicNum, &mask__[0])
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetNSample(self, int Nsample):
        """
        sendSetNSample(int Nsample)

        configure le Nsample pour tous les ASICs

        """
        cdef bool out = self._da.sendSetNSample(Nsample)
        if not out:
            raise RuntimeError(self.lastError)

    def sendStartAcq(self, int asicNum):
        """
        sendStartAcq(int asicNum)

        demarrage de l'acquisition de la carte NetQuic (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendStartAcq(asicNum)
        if not out:
            raise RuntimeError(self.lastError)

    def sendStopAcq(self, int asicNum):
        """
        sendStopAcq(int asicNum)

        arret de l'acquisition de la carte NetQuic (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendStopAcq(asicNum)
        if not out:
            raise RuntimeError(self.lastError)

    def sendResetNetquic(self, int asicNum):
        """
        sendResetNetquic(int asicNum)

        reset de la carte NetQuic (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendResetNetquic(asicNum)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetCycleRawMode(self, int asicNum, int undersampling):
        """
        sendSetCycleRawMode(int asicNum, int undersampling)

        bascule en mode raw signal cycle (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetCycleRawMode(asicNum, undersampling)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetAsicConf(self, int asicNum, int signalId, int state):
        """
        sendSetAsicConf(int asicNum, int signalId, int state)

        configure un signal a 1 ou 0

        """
        cdef bool out = self._da.sendSetAsicConf(asicNum, signalId, state)
        if not out:
            raise RuntimeError(self.lastError)

    def sendGetStatus(self, int asicNum):
        """
        sendGetStatus(int asicNum)

        demande le paquet status de la carte NetQuic (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendGetStatus(asicNum)
        if not out:
            raise RuntimeError(self.lastError)


    def sendSetASICSerialLinkFrequency(self, int serialFreq):
        """

        change la frequence du lien serie pour les commandes ASIC 0-200=> 0=>2kHz (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetASICSerialLinkFrequency(serialFreq)
        if not out:
            raise RuntimeError(self.lastError)

    def sendConfigurePID(self, int asicNum, int P, int I, int D):
        """
        sendConfigurePID(int asicNum, int P, int I, int D)

        configure les parametres de la regul (si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendConfigurePID(asicNum, P, I, D)
        if not out:
            raise RuntimeError(self.lastError)

    def sendActivatePID(self, int asicNum, int onOff):
        """
        sendActivatePID(int asicNum, int onOff)

        active la regulation onOff = 1, desactive la regulation onOff = 0(si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendActivatePID(asicNum, onOff)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetRelay(self, int asicNum , int bitmask):
        """
        sendSetRelay(int asicNum , int bitmask)

        choose the relay resistance: 100kOhm, 10kOhm
        """
        cdef bool out = self._da.sendSetRelay(asicNum, bitmask)
        if not out:
            raise RuntimeError(self.lastError)
        

        
    def sendResetVOffset(self, int asicNum):
        """
        sendResetVOffset(int asicNum)

        reset des valeurs VOffset (mise a 0) de l'asic specifie(si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendResetVOffset(asicNum)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetVOffset(self, int asicNum, int pixelNum, float voffset):
        """
        sendSetVOffset(int asicNum, int pixelNum, float32 voffset)

        configure la valeur VOffset pour le pixel (ou tous les pixels si pixelNum = 0xFF) de l'asic specifie(si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetVOffset(asicNum, pixelNum, voffset)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetVOffsets(self, int asicNum, voffset not None):
        """
        sendSetVOffsets(int asicNum, float32[128] voffset)

        configure la valeur VOffset pour tous les pixels de l'asic specifie(si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        voffset_ = np.ascontiguousarray(voffset, np.float32)
        if voffset_.size != 128:
            raise ValueError("Expected array size of argument 'voffset' is '128'.")
        cdef float[::1] voffset__ = voffset_
        cdef bool out = self._da.sendSetVOffsets(asicNum, &voffset__[0])
        if not out:
            raise RuntimeError(self.lastError)

    def sendResetVout2IinCoeffs(self, int asicNum):
        """
        sendResetVout2IinCoeffs(int asicNum)

        reset des valeurs Vout2Iin (mise a 1) de l'asic specifie(si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendResetVout2IinCoeffs(asicNum)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetVout2IinCoeffs(self, int asicNum, float MinMfb, float Rfb):
        """
        sendSetVout2IinCoeffs(int asicNum, float32 MinMfb, float32 Rfb)

        configure la valeur Vout2Iin =  Min/Mfb* Rfb pour l'asic specifie(si asicNum = 0xFF, la commande est envoyée a tous les ASIC, si asic num < 16, la commande est envoyée a l'ASIC asicNum, pour envoyer à une liste d'ASICs utiliser les bits 8 à 23 pour specifier la liste, ex asicNum = 0x00FF00 configurera les asic 0 à 7)

        """
        cdef bool out = self._da.sendSetVout2IinCoeffs(asicNum, MinMfb, Rfb)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetVout2IinsCoeffs(self, MinMfb not None, Rfb not None):
        """
        sendSetVout2IinsCoeffs(float32[16] MinMfb, float32[16] Rfb)

        configure les valeurs out2Iin =  Min/Mfb* Rfb de tous les asics

        """
        MinMfb_ = np.ascontiguousarray(MinMfb, np.float32)
        if MinMfb_.size != 16:
            raise ValueError("Expected array size of argument 'MinMfb' is '16'.")
        cdef float[::1] MinMfb__ = MinMfb_
        Rfb_ = np.ascontiguousarray(Rfb, np.float32)
        if Rfb_.size != 16:
            raise ValueError("Expected array size of argument 'Rfb' is '16'.")
        cdef float[::1] Rfb__ = Rfb_
        cdef bool out = self._da.sendSetVout2IinsCoeffs(&MinMfb__[0], &Rfb__[0])
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetScientificDataTfUsed(self, int tfused):
        """
        sendSetScientificDataTfUsed(int tfused)

        applique la fonction de transfert : 0 => signal brut, 1 => Vout, 2 => Iin

        """
        cdef bool out = self._da.sendSetScientificDataTfUsed(tfused)
        if not out:
            raise RuntimeError(self.lastError)

    '''
    vvvvvvvvvvvvv
    REMOVED IN V3    

    def sendStartBackup(self, str sessionName, str comment):
        """
        sendStartBackup(str sessionName, str comment)

        start backup

        """
        cdef QByteArray sessionName_ = QByteArray(sessionName, len(sessionName))
        cdef QString sessionName__ = QString(sessionName_)
        cdef QByteArray comment_ = QByteArray(comment, len(comment))
        cdef QString comment__ = QString(comment_)
        cdef bool out = self._da.sendStartBackup(sessionName__, comment__)
        if not out:
            raise RuntimeError(self.lastError)


    def sendStopBackup(self):
        """
        sendStopBackup()

        stop backup

        """
        cdef bool out = self._da.sendStopBackup()
        if not out:
            raise RuntimeError(self.lastError)

    def sendStartRawBackup(self, str sessionName):
        """
        sendStartRawBackup(str sessionName)

        start raw backup

        """
        cdef QByteArray sessionName_ = QByteArray(sessionName, len(sessionName))
        cdef QString sessionName__ = QString(sessionName_)
        cdef bool out = self._da.sendStartRawBackup(sessionName__)
        if not out:
            raise RuntimeError(self.lastError)

    def sendStopRawBackup(self):
        """
        sendStopRawBackup()

        stop raw backup

        """
        cdef bool out = self._da.sendStopRawBackup()
        if not out:
            raise RuntimeError(self.lastError)

    
    def sendStartHKBackup(self, str sessionName, str comment):
        """
        sendStartHKBackup(str sessionName, str comment)

        start HK backup (hk displayed in HKPlot tool)

        """
        cdef QByteArray sessionName_ = QByteArray(sessionName, len(sessionName))
        cdef QString sessionName__ = QString(sessionName_)
        cdef QByteArray comment_ = QByteArray(comment, len(comment))
        cdef QString comment__ = QString(comment_)
        cdef bool out = self._da.sendStartHKBackup(sessionName__, comment__)
        if not out:
            raise RuntimeError(self.lastError)

    def sendStopHKBackup(self):
        """
        sendStopHKBackup()

        stop HK backup

        """
        cdef bool out = self._da.sendStopHKBackup()
        if not out:
            raise RuntimeError(self.lastError)


    REMOVED IN V3
    ^^^^^^^^^^^^^
    '''

    def sendSetBackupDir(self, str directory):
        """
        sendSetBackupDir(str directory)

        define the base backup directory

        """
        cdef QByteArray directory_ = QByteArray(directory, len(directory))
        cdef QString directory__ = QString(directory_)
        cdef bool out = self._da.sendSetBackupDir(directory__)
        if not out:
            raise RuntimeError(self.lastError)

    def sendResetSubsystem(self, int subsystemId):
        """
        sendResetSubsystem(int subsystemId)

        reset the subsystem

        """
        cdef bool out = self._da.sendResetSubsystem(subsystemId)
        if not out:
            raise RuntimeError(self.lastError)

    def sendResetDecommutationFlags(self, int subsytemId):
        """
        sendResetDecommutationFlags(int subsytemId)

        reset the decommutation flags for the subsytem, if subsytemId = 0xFF reset all subsystems flags (DISP_DecommuteLastErrorCode, DISP_Decommute...)

        """
        cdef bool out = self._da.sendResetDecommutationFlags(subsytemId)
        if not out:
            raise RuntimeError(self.lastError)

    def sendAddToLogbook(self, str key, str comment):
        """
        sendAddToLogbook(str key, str comment)

        add a line into the logbook file (line is : YYYYMMDD hhmmss: key => comment)

        """
        cdef QByteArray key_ = QByteArray(key, len(key))
        cdef QString key__ = QString(key_)
        cdef QByteArray comment_ = QByteArray(comment, len(comment))
        cdef QString comment__ = QString(comment_)
        cdef bool out = self._da.sendAddToLogbook(key__, comment__)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetLogBookFilename(self, str filename):
        """
        sendSetLogBookFilename(str filename)

        Set the logbook file, if filename is empty, a new logbook file is opened according to the automatic logbook filename strategy

        """
        cdef QByteArray filename_ = QByteArray(filename, len(filename))
        cdef QString filename__ = QString(filename_)
        cdef bool out = self._da.sendSetLogBookFilename(filename__)
        if not out:
            raise RuntimeError(self.lastError)

    def sendSetLogBookBaseDirectory(self, str directory):
        """
        sendSetLogBookBaseDirectory(str directory)

        Change the logbook base directory

        """
        cdef QByteArray directory_ = QByteArray(directory, len(directory))
        cdef QString directory__ = QString(directory_)
        cdef bool out = self._da.sendSetLogBookBaseDirectory(directory__)
        if not out:
            raise RuntimeError(self.lastError)
