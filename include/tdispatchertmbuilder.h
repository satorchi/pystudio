//---------------------------------------------------------------------------

#ifndef TDispatcherTMBuilderH
#define TDispatcherTMBuilderH
//---------------------------------------------------------------------------

#include "tdispatcherrequest.h"
#include "tabstractparameterstable.h"
#include "qdispatcherbytearray.h"

class TDispatcherTMBuilder
{
public :

    /** @brief Class constructor.
 *
 * Initialize all class variable.
 */
    TDispatcherTMBuilder(int tmMaxSize);

    /** @brief Class destructor.
 */
    ~TDispatcherTMBuilder();

    void initTMBuilder();
    void buildACKTM(quint8 tcID, quint16 tcCN, quint8 error = 0, const quint8 *errorStatus=NULL, int nbErrorStatus=0);
    void buildStatusTM(TAbstractParametersTable* Parameters);
    void buildDispatchTM(TDispatcherRequest* dispatcherRequest, TAbstractParametersTable *Parameters);

    QDispatcherByteArray  *tmBuffer;

private :
    quint16    m_ackCN;
    quint16    m_reqCN;
};

#endif
