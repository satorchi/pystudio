#ifndef TRAWDATAEMITTER_H
#define TRAWDATAEMITTER_H

#include <QtNetwork>
#define DEFAULT_UDP_PACKET_SIZE 1500

class TRawDataEmitter
{
public:
    TRawDataEmitter();
    void checkForNewConnection();
    void resetConnection();
    void send(quint8 subsystem, quint8* buffer, quint32 bufferSize);
    void sendCommand(quint8 subsystem, quint8* buffer, quint32 bufferSize);

private:
  /**< Socket UDP made in Qt*/
  QUdpSocket* m_udpSocket;
  QHostAddress m_remoteAddress;
  quint16 m_remotePort;
  quint16 m_localPort;
  quint32 m_nbPacketsToSend;
  bool m_subsystemsIsEnabled[64];
  unsigned char m_bufferTemp[DEFAULT_UDP_PACKET_SIZE];
};

#endif // TRAWDATAEMITTER_H
