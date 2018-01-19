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
bool sendConfigureCFibers(quint16 periode , quint8 broche3State , quint8 broche4State , quint8 broche5State , quint16 ampFiber1 , quint16 offsetFiber1 , quint16 durationFiber1 , quint16 ampFiber2 , quint16 offsetFiber2 , quint16 durationFiber2 , quint16 ampFiber3 , quint16 offsetFiber3 , quint16 durationFiber3 , quint16 ampFiber4 , quint16 offsetFiber4 , quint16 durationFiber4);
bool sendConfigureHighFrequencySource(double frequency);
bool sendConfigureLowFrequencySource(double frequency);


protected :
virtual bool sendSubsystemTC(QString tcName, quint8 subsysID,quint16 tcID) = 0;

void loadCalibSourceFactors();

private :

double m_hfFactor;
double m_lfFactor;
};

#endif
