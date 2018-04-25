//---------------------------------------------------------------------------
#ifndef TDispatcherRequestH
#define TDispatcherRequestH
//---------------------------------------------------------------------------

#include "qtimeout.h"
#include <QTime>

/** @brief Dispatcher parameter request definition.
 *
 * This class is used to define a client parameters request.
 */
class TDispatcherRequest
{
public :
    /** @brief Constructor.
 *
 * Initialize all class variable.
 */
    TDispatcherRequest(quint32 idOfLastParameter);

    /** @brief Destructor.
 */
    ~TDispatcherRequest();

    /** @brief configure a parameters request.
 *
 * Check the parameters validity, if the parameters are correct, configure the
 * class variables with the request.
 * @param [in] mode request mode.
 * @param [in] frequency request frequency parameter.
 * @param [in] nbParameters parameters number.
 * @return True if the parameters are valid, false else.
 */
    bool startRequest(quint8 reqNum, quint32 mode, quint16 frequency, quint16 *paramReceivedCount);

    /** @brief Return if the request is active, the production mode is "synchronized" and it's time to send parameters.
 *
 * @param [in] paramReceivedCount Parameters reception counters list.
 * @return Return true if the request is active, the production mode is "synchronized" and it's time to send parameters.
 */
    bool synchronizedModeActive(quint16* paramReceivedCount, bool &oneShot);
    bool timeout(bool &oneShot);

    /** @brief reset the request.
 *
 * Initialize the parameters of the request. The request is not activated.
 */
    void reset();

    quint16 parametersCount();
    quint32 parameterId(int index);
    quint8 reqNum() {return m_requestNum;}
    bool append(quint32 parameterId);

private :
    QList<quint32> m_tabParamRequested; /**< List of parameters to send. */
    bool m_waitingForParameter; /**< True => synchronized frequency, false => Hz frequency . */
    bool m_oneShot;     /**< True if it is a single request. */
    bool m_firstTimeOut;
    quint16 m_frequency;    /**< Parameters production frequency. */
    quint16 m_awaitedParamReceivedCount;    /**< Value of Parameters->tabParamReceived to wait to send parameters (use for synchronized emission). */
    quint32 m_parameterNum;    /**< Parameter ID used in synchronized mode. */
    quint8 m_requestNum;
    quint32 m_idOfLastParameter;
    QTimeout m_timeOut; /**< date of the last send. */
};
#endif
