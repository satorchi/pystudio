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

protected:
    bool sendCustomTC(){return TDispatcherAccessKernel::sendCustomTC();}
    bool sendInternTC(){return TDispatcherAccessKernel::sendInternTC();}
    bool sendSubsystemTC(quint8 subsysID,quint16 tcID);
    QDispatcherTCByteArray* startNewCustomTC(quint16 customTcNum) { return TDispatcherAccessKernel::startNewCustomTC(customTcNum);}
    QDispatcherTCByteArray* startNewInternTC(quint16 internTcNum) { return TDispatcherAccessKernel::startNewInternTC(internTcNum);}
    QDispatcherTCByteArray* startNewSubsystemTC(quint8 subsysID, quint16 tcID){ return TDispatcherAccessKernel::startNewSubsystemTC(subsysID,tcID);}
};


#endif // TDispatcherAccess_H
