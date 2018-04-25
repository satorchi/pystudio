#ifndef QAUTOCONNECTSOCKET_H
#define QAUTOCONNECTSOCKET_H

#include <QTcpSocket>
#include "qtimeout.h"

class QAutoConnectSocket:public QObject
{
    Q_OBJECT
public:
    QAutoConnectSocket(QString ip, int port, int connectionTimeOut = 0);
    int read(char* buffer, int bufferSize);
    int write(char* buffer,int bufferSize);
    bool isConnected();
    void reconfigure(QString ip, int port);
    void connect(int timeout = 0);
    void disconnect();
    QString tcpError();
    qint64 bytesToWrite();

private :
    QTcpSocket* m_internSocket;
    QString m_remoteIP;
    int m_remotePort;
    int m_connectionTimeOut;
    void tryToConnectIfNeeded(bool firstConnection = false);


    QTimeout m_timeOut;

private slots:

     void disconnection();
};

#endif // QAUTOCONNECTSOCKET_H
