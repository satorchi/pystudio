#ifndef TDispatcherAccess_H
#define TDispatcherAccess_H

#include "tparameterstable.h"
#include "tcommandencode.h"
#include "tdispatcheraccesskernel.h"
#include "definitions.h"


/** @brief Manage the dispatcher connection for clients.
 */
class TDispatcherAccess :  public TDispatcherAccessKernel, public TCommandEncode
{
Q_OBJECT
public :

/** @brief Constructor.
 *
 * Initialize the class parameters.
 * @param [in] dispatcherAddress Dispatcher IP address.
 * @param [in] dispatcherPort Dispatcher IP port.
 */
    TDispatcherAccess(QString dispatcherAddress = "", int dispatcherPort = -1);

    inline TParametersTable* parameters(){
        return (TParametersTable*)TDispatcherAccessKernel::parameters();
    }

    bool isValidSubsystemAck(quint8 subsysId, quint16 ackReportSize, const quint8* ackReport, QString& errorStr);


signals:
    void requestArrived(int requestNum, TParametersTable* parametersTable);

private slots:
    void requestIsArrived(int requestNum);

protected:
    bool sendCustomTC(QString tcName){return TDispatcherAccessKernel::sendCustomTC(tcName);}
    bool sendInternTC(QString tcName){return TDispatcherAccessKernel::sendInternTC(tcName);}
    bool sendSubsystemTC(QString tcName, quint8 subsysID,quint16 tcID);
    QDispatcherTCByteArray* startNewCustomTC(quint16 customTcNum) { return TDispatcherAccessKernel::startNewCustomTC(customTcNum);}
    QDispatcherTCByteArray* startNewInternTC(quint16 internTcNum) { return TDispatcherAccessKernel::startNewInternTC(internTcNum);}
    QDispatcherTCByteArray* startNewSubsystemTC(quint8 subsysID, quint16 tcID){ return TDispatcherAccessKernel::startNewSubsystemTC(subsysID,tcID);}
};


#endif // TDispatcherAccess_H
