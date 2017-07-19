#ifndef _TCOMMANDENCODE_H_
#define _TCOMMANDENCODE_H_

#include "definitions.h"
#include "tvirtualcommandencode.h"
#include "qdispatchertcbytearray.h"


class TCommandEncode : public TVirtualCommandEncode
{
public :
TCommandEncode();
virtual  ~TCommandEncode();

void buildSubsystemTcEOP(QDispatcherTCByteArray *currentTC, quint8 subsystemID, quint16 commandNum);
void buildSubsystemTcHeader(QDispatcherTCByteArray *currentTC, quint8 subsystemID, quint16 commandNum, quint32 dataFieldSize);

bool sendSwitchesMsg(QString txtMsg);
bool sendToIMARCTR1(QString txtMsg);
bool sendToIMARCTR2(QString txtMsg);
bool sendToIMARCTR3(QString txtMsg);
bool sendToIMARCTR4(QString txtMsg);


protected :
virtual bool sendSubsystemTC(quint8 subsysID,quint16 tcID) = 0;

private :

};

#endif
