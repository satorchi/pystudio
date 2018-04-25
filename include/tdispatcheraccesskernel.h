#ifndef TDispatcherAccessKernel_H
#define TDispatcherAccessKernel_H

#include "tabstractparameterstable.h"
#include "qdispatchertcbytearray.h"
#include "waitingcommandexecutionform.h"
#include <QMutex>
#include <QThread>
#include <QSemaphore>
#include <QTime>
#include <QCoreApplication>

#include <QTcpSocket>

#define USING_DISPATCHER_ACCESS_LIB 1
/**
 * \enum freqtype
 * @brief Constantes de type de requetes.
 *
 * freqtype est une série de constantes prédéfinie pour définir le type de requête.
 */
typedef enum _freqtype {
    TimeOutMode   /*!<  requete de type timeout*/
    , SynchronisedMode /*!<  requete de type synchronisation avec la réception d'un parametre*/
} freqtype;
/**
 * @brief Special locker
 *
 */
class MutexTryLocker {
  QMutex *m_;
public:
  MutexTryLocker(QMutex *m) : m_(m) {while (m_->tryLock(10) == false)QCoreApplication::processEvents();}
  ~MutexTryLocker() { m_->unlock(); }
};

/**
 * @brief Manage the dispatcher TCP connection
 *
 */
class QMyTcpSocket:public QTcpSocket
{
    Q_OBJECT
public:
    QMyTcpSocket();
    /**
     * @brief return the dispatcher connection state
     *
     * @return true if dispatcher connection is established
     */
    bool isConnected();
    void setConnected();

private :
    bool m_connected;

private slots:
    void disconnected();
};


/** @brief Manage the dispatcher connection for clients.
 */
class TDispatcherAccessKernel :  public QThread
{
    Q_OBJECT
public :

    enum waitingForAckModes{
        NotWaitingForAck
        ,WaitingForAck
        ,WaitingForAckWithPopup
    };

    /** @brief Constructor.
 *
 * Initialize the class parameters.
 * @param [in] bufferSize Size of the Data receiver buffer.
 * @param [in] clientName Name of the current client.
 * @param [in] dispatcherAddress Dispatcher IP address.
 * @param [in] dispatcherPort Dispatcher IP port.
 */
    TDispatcherAccessKernel(quint16 maxTCSize=10000);

    void initDispatcherAccess(TAbstractParametersTable* parameters, quint16 bufferSize, QString dispatcherAddress, int dispatcherPort);
    /** @brief Destructor.
 */
    virtual  ~TDispatcherAccessKernel();

    /** @brief Used to (re)configure the Dispatcher communication parameters.
 *
 * Initialize Dispatcher communication parameters (address, port...).
 * @param [in] dispatcherAddress Dispatcher IP address.
 * @param [in] dispatcherPort Dispatcher IP port (optionnal default port used).
 */
    void configure(QString dispatcherAddress, int dispatcherPort);

    /** @brief Get the number of available data in the buffer.
 *
 * @param [out]  bufferOverlapped Return true if the circular buffer has been full.
 * @return Return the number of available data in the buffer.
 */
    quint16 getNbDataAvailable(bool &bufferOverlapped);

    /** @brief Update the TParametersTable object.
 * Pop the first available data in the buffer, extract values and update the TParametersTable object.
 * @return The TParametersTable object updated
 */
    TAbstractParametersTable* update(int *requestNum = NULL);

    /** @brief update the TParametersTable object.
 * Pop all available data in the buffer, extract values and update the TParametersTable object.
 * @return The TParametersTable object updated.
 */
    TAbstractParametersTable* updateAll();


    /** @brief Défini la taille du buffer de télémétrie de la librairie.
     *A ne modifier que si cela est nécessaire dans le cas ou un nombre
     *Trés important de requettes doit etre fait.
     * @param [in] bufferSize Nouvelle taille du buffer.
     */

    void resizeTMBuffer(quint16 bufferSize);

    /** @brief Define the command mode (waiting for ACK or not).
 * @param [in] waitingForACK activate/desactivate the command blocking.
 */
    void setWaitingForAckMode(waitingForAckModes waitingForACK, bool showPopupOnlyOnError = true);
    void setWaitingForAckMode(bool waitingForACK){if (waitingForACK) setWaitingForAckMode(WaitingForAck); else setWaitingForAckMode(NotWaitingForAck);}
    void setWaitingForAckTimeOut(int ackTimeOut = 5000);

    waitingForAckModes waitingForAckMode() { return m_waitingForACK;}
    int waitingForAckTimeOut(){return m_ackTimeOut;}

    bool subSystemsCommandsLocked();
    void setSubSystemsCommandsLocked(bool commandMode);

    bool fullCommandsLocked();
    void setFullCommandsLocked(bool commandMode);


    /** @brief Define the autoUpdate mode (process request when arrive and emit signal or push request into FIFO).
     * @param [in] autoUpdate activate/desactivate autoUpdate
     */
    void setAutoUpdateWithRequest(bool autoUpdate);
    bool startSubsystemAccess();
    bool stopSubsystemAccess();
    bool stopDispatcher(quint32 stopCode); // stop code is parameterCRC()

    void setDebugEnable(bool enabled);
    void waitMs(qint64 milliseconds);

    virtual bool isValidSubsystemAck(quint8 subsysId, quint16 ackReportSize, const quint8* ackReport, QString& errorStr) = 0;



    /** @brief Définie une requete synchronisée. Dans ce mode les parametres sont envoyés à chaque fois (ou 1 fois sur X) que le parametre parameterIdToSynchronize est acquis.
 * @param [in] parameterList Liste des parametres à envoyer.
 * @param [in] parameterIdToSynchronize Parametre utilisé pour la synchronisation.
 * @param [in] everyXParameters Defini la frequence d'envoi.
 *              Si <= 1, les parametres sont envoyés chaque fois que parameterIdToSynchronize est acquis.
 *              Sinon les parametres sont envoyés 1 fois sur 2,3,4...
  * @return Le numero de requete attribué ou -1 si la requete n'est pas valide (trop de parametres) ou si le nombre max de requetes est atteint (voir MAX_NB_REQUEST_PER_CLIENT).
 */

    int requestSynchroParameters(QList<quint32> parameterList,quint32 parameterIdToSynchronize, quint16 everyXParameters = 0, bool *isValidRequest=NULL);

    /** @brief Définie une requete avec timeout. Dans ce mode les parametres sont envoyés toutes les X ms.
    * @param [in] parameterList Liste des parametres à envoyer.
    * @param [in] timeout timeout en ms (defaut = 1000).
     * @return Le numero de requete attribué ou -1 si la requete n'est pas valide (trop de parametres) ou si le nombre max de requetes est atteint (voir MAX_NB_REQUEST_PER_CLIENT).
    */
    int requestTimeoutParameters(QList<quint32> parameterList,quint16 timeout = 1000, bool *isValidRequest=NULL);

    /** @brief Définie une requete synchronisée.
    * Dans ce mode les parametres sont envoyés une seule fois, des que le parametre parameterIdToSynchronize sera acquis.
    * @param [in] parameterList Liste des parametres à envoyer.
    * @param [in] parameterIdToSynchronize Parametre utilisé pour la synchronisation.
    * @return Le numero de requete attribué ou -1 si la requete n'est pas valide (trop de parametres) ou si le nombre max de requetes est atteint (voir MAX_NB_REQUEST_PER_CLIENT).
    */
    int requestOneTimeSynchroParameters(QList<quint32> parameterList,quint32 parameterIdToSynchronize, bool *isValidRequest=NULL);

    /** @brief Définie une requete avec timeout.
    * Dans ce mode les parametres seront envoyé une seule fois immediatement ou dans X ms.
    * @param [in] parameterList Liste des parametres à envoyer.
    * @param [in] timeout timeout en ms (defaut = 0 <=> immediatement).
     * @return Le numero de requete attribué ou -1 si la requete n'est pas valide (trop de parametres) ou si le nombre max de requetes est atteint (voir MAX_NB_REQUEST_PER_CLIENT).
    */
    int requestOneTimeTimeoutParameters(QList<quint32> parameterList,quint16 timeout = 0, bool *isValidRequest=NULL);

    bool disableOneRequestedParameters(quint8 reqNum);
    bool disableAllRequestedParameters();

    QString lastError();
    bool isConnected();
    QString state();
    int dispatcherTFVersionLoaded();

    int getSubSystemStatusReports(quint8 *statusReports);
    quint8 getCommandStatus();

    void run();
    quint8 _ACKStatusReports[255];

    inline QString dispatcherAddress(){
        return m_dispatcherAddress;
    }

    inline int dispatcherPort(){
        return m_dispatcherPort;
    }

    inline int stackSize(){
        return m_bufferSize;
    }

    inline int stackOccupation(){
        return m_nbElements;
    }
    inline double requestRate(){
        return m_requestRate;
    }
    inline double dataRate(){
        return m_dataRate;
    }

    inline quint32 nbOverlap(){
        return m_nbOverlap;
    }

    /**
     * @brief beginReadParameters
     * To be used to access to parameters asynchroniously
     */

    inline void beginReadParameters(){
        while (m_parametersMutex.tryLock(10) == false)QCoreApplication::processEvents();
    }

    /** @brief Get the pointer to tparameters.
 */
    inline TAbstractParametersTable* parameters(){
        return m_parameters;
    }

    inline void endReadParameters(){
        m_parametersMutex.unlock();
    }


signals:
    void requestArrived(int requestNum);
    void connected();
    void disconnected();
    void connectionStateChanged(bool connected);
    void errorOccurs(QString errorStr);

protected :
    bool sendSubsystemTC(QString tcName,quint8 subsysID,quint16 tcID);
    bool sendCustomTC(QString tcName);
    bool sendInternTC(QString tcName);
    QDispatcherTCByteArray* startNewCustomTC(quint16 customTcNum);
    QDispatcherTCByteArray* startNewInternTC(quint16 internTcNum);
    QDispatcherTCByteArray* startNewSubsystemTC(quint8 subsysID, quint16 tcID);
    TAbstractParametersTable* m_parameters;
    bool m_subsystemControledAccessMode;
    quint8 m_lastSubsystemTCSent;

private :

    typedef struct _request{
        bool oneShot;
        freqtype freqType;
        quint32 parameterNum;
        quint16 frequency;
        quint16 nbParameters;
        QList<quint32> parameterList;
        quint16 futureRequestsSize;
        quint32 requestsCN;
        quint16 requestsSize; /**< List of request size.*/
    } oneRequest;


    /** @brief Define a request.
     * @param [in] reqNum Request number (from 0 to MAX_NB_REQUEST_PER_CLIENT-1).
     * @param [in] oneShot The request must be executed only one time.
     * @param [in] freqType Request frequency type : timeout mode or synchronised mode.
     * @param [in] parameterNum Define the parameter to used if the freqType is synchronised mode, else not used.
     * @param [in] frequency Define the frequency.
     * @param [in] parameterList List of parameters to send.
     */

    bool requestParameters(quint8 reqNum, bool oneShot, freqtype freqType,quint32 parameterNum,quint16 frequency,QList<quint32> parameterList);


    quint8 m_lastRequestNum;

    /** @brief Erase all data from the buffer.
 */
    void clearDataBuffer();
    /**
     * @brief
     *
     * @param dataMessageFieldSize
     * @return bool
     */
    bool sendTC();
    void decodeTM(quint8* tmBuff, int tmBuffSize);
    int getNextEmptyRequest();
    bool isActivated();
    bool processTM(); // return true if TM is a request and autoUpdate is activated
    void deleteRequestsFromBuffer(quint16 reqNum);
    void optimizeBufferRequests();
    void sendRequestsAfterConnection();
    void setAckStatus(quint8 ACKStatus);
    quint8 ackStatus();
    void setErrorMsg(QString msg);
    QString errorMsg();

    bool m_debug;
    int m_dispatcherTFVersionLoaded;
    bool m_incompatibleLibrary;
    bool m_subSystemsCommandsLocked;
    bool m_statusTMReceived;
    bool m_fullCommandsLocked;

    QMyTcpSocket* m_socketClient;       /**< Client TCP socket. */
    QString m_clientName;              /**< Name of the Client. */
    QDispatcherTCByteArray m_currentTC;     /**< Buffer used to build an order. */
    QString m_errorMsg;
    quint16 m_tcCN;
    QMap<quint8, oneRequest*> m_requests;

    quint8 m_ACKStatus;
    quint16 m_ACKStatusReportsSize;

    /************ circular buffer variables ************/
    QDispatcherByteArray** m_dataBuffer;         /**< Circular buffer used to bufferize the data received. */
    quint16 m_bufferSize;           /**< Size of the circular buffer. */
    quint16 m_popIndex;             /**< Read index of the buffer. */
    quint16 m_pushIndex;            /**< Write index of the buffer. */
    quint16 m_nbElements;           /**< Nb elements in the buffer. */
    bool m_bufferOverlapped;     /**< Flag indicates if the buffer has been full. */
    bool m_running;

    QMutex m_socketMutex;
    QMutex m_internVarMutex;
    QMutex m_parametersMutex;

    QSemaphore m_ackSem;

    waitingForAckModes m_waitingForACK;
    bool m_showWaitingForACKPopupOnlyOnError;
    quint16 m_waitingForACKCN;
    bool m_autoUpdate;

    QString m_dispatcherAddress;
    int m_dispatcherPort;
    double m_requestRate;
    int m_requestNumber;
    double m_dataRate;
    int m_dataNumber;
    int m_ackTimeOut;
    QTime m_benchTime;
    quint32 m_currentState;
    quint32 m_nbOverlap;
    quint32 m_currentDecodingNB;
    WaitingCommandExecutionForm* m_waitingForCommandExecutionForm;

};


#endif // TDispatcherAccessKernelKERNEL_H
