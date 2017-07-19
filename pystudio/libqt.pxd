from libcpp.string cimport string

cdef extern from "<QtCore>":
    ctypedef int qint8
    ctypedef int qint16
    ctypedef int qint32
    ctypedef int qint64
    ctypedef int quint8
    ctypedef int quint16
    ctypedef int quint32
    ctypedef int quint64

cdef extern from "<QApplication>" nogil:
    cdef cppclass QApplication:
        QApplication(int argc, char **argv) except +
        QString applicationDirPath()

cdef extern from "<QCoreApplication>" namespace "QCoreApplication::QCoreApplication" nogil:
   cdef void processEvents()

cdef extern from "<QByteArray>" nogil:
    cdef cppclass QByteArray:
        QByteArray() except +
        QByteArray(const char*, int size) except +

cdef extern from "<QByteArray>" namespace "QByteArray::QByteArray" nogil:
    cdef QByteArray fromRawData(const char*, int size)

cdef extern from "<QList>" nogil:
    cdef cppclass QList[T]:
        QList() except +
        void append(const T)
        T at(int)
        int count()
        T first()
        T last()

cdef extern from "<QMutex>" nogil:
    cdef cppclass QMutex:
        QMutex() except +
    cdef cppclass QMutexLocker:
        QMutexLocker(QMutex*) except +

cdef extern from "<QString>" nogil:
    cdef cppclass QString:
        QString() except +
        QString(QByteArray) except +
        string toStdString()
