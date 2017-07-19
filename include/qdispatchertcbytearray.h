#ifndef QDISPATCHERTCBYTEARRAY_H
#define QDISPATCHERTCBYTEARRAY_H

#include "qdispatcherbytearray.h"


class QDispatcherTCByteArray: public QDispatcherByteArray
{

public:
    explicit QDispatcherTCByteArray();

    void startNewTC(quint16 tcCN);
    void closeTC();
    void startNewDispatcherKernelTC(quint16 tcCN, quint8 dispatcherTcId);
    void startNewCustomTC(quint16 tcCN, quint16 customTcNum);
    void startNewInternTC(quint16 tcCN, quint16 customTcNum);
    void startNewSubsystemTC(quint16 tcCN, quint8 subsysID, quint16 tcID);
    const quint8* subsystemTCBuffer();
    quint32 subsystemTCBufferSize();

private:
    int m_subsytemTCStartIndex;

};

#endif // QDISPATCHERTCBYTEARRAY_H
