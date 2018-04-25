//---------------------------------------------------------------------------

#ifndef TClientH
#define TClientH
//---------------------------------------------------------------------------

#include "tabstractparameterstable.h"
#include "tdispatcherrequest.h"
#include "tdispatchertmbuilder.h"
#include "tabstractcommandmanager.h"
#include <QTcpSocket>
#include <QList>


/** \def CLIENT_DISCONNECTED
  *  @brief Used for the getAndExecuteCommands() return when the client deconnection
  * is detected.
 */
#define CLIENT_DISCONNECTED  -1

/** @brief Client manager.
 *
 * This class manages one client.
 */
class TClient : public QObject
{
    Q_OBJECT

  public :

/** @brief Class constructor.
 *
 * Initialize all class variable and create instances of TCommandManager and tdispatcherrequest.
 * @param [in] clients the clients manager.
 * @param [in] clientNum the client number.
 * @param [in] Parameters pointer to TParameters object.
 */
    TClient(quint8 clientNum,quint8 nbRequestsAllowedPerClient,  TAbstractParametersTable* Parameters, TAbstractCommandManager* commandManager);
/** @brief Class destructor.
 *
 * release all created instances in constructor.
 */
   virtual  ~TClient();


/** @brief Called to initialize the client.
 *
 * Called when a new client is connected. Initialize all variables (CommandManager, dispatcherRequest list...).
 * @param [in] newClientSocket client socket pointer.
 */
    void setNewClient(QTcpSocket *newClientSocket);

/** @brief Called to release the client.
 *
 * close the client socket and reset all associated variables.
 */
    void releaseClient();

/** @brief Called to configure a parameters request with a client command.
 *
 * Extract data from the command to configure a parameters request.
 * @param [in] pCommandBuffer dispatcher request command.
 * @param [in] size command size.
 * @return The validity of the command.
 */
    bool buildRequest(quint8* pCommandBuffer, int size);

/** @brief Build Dispatcher TM.
 *
 * Check the dispatcherRequest list and build a dispatcher TM when it's needed.
 * If the last TM received from subsystem is an ACK TM, build the ACK TM for the client.
 * @param [in] receiveACK the subsystem TM received is an ACK.
 * @param [in] ACKStatus if the subsystem TM is an ACK, ACKStatus contains the subsystem TM ACK status.
 * @param [in] ACKStatusSize if the subsystem TM is an ACK, ACKStatusSize contains the subsystem TM ACK status size.
 */
    void buildDispatchTM(bool receiveACK,  const quint8 *ACKStatus, quint8 ACKStatusSize);

/** @brief Build dispatch TM for requests with timeout.
 *
 */
    void buildDispatchTMWithTimeOut();


/** @brief Return is the client is connected.
 *
 * @return The client connection status.
 */
    bool isAlive();

/** @brief Get client commands from socket and execute it.
 *
 * Get the commands from socket, configure CommandManager to decode and execute the command.
 * Detect the client deconnection and return it.
 * @return The client connection status.
 */
    int getAndExecuteCommands(quint8* tcBuff, int tcBuffSize);

/** @brief Send TM to client.
 *
 * If the client is connected, send data to the socket.
 * @return Return true if the TM has been sent succesfully, else return false.
 */
    int dataSentToClient();

    int clientNumber();
    void sendAckTelemetry(quint8 tcID, quint16 tcCN, quint8 error = 0, const quint8 *errorStatus=NULL, int nbErrorStatus=0);
    void sendStatusTelemetry();

    int nbActiveRequests();

  protected :
/** @brief Initialize class variable.
 *
 */
    void init();
    /** @brief Send built TM to client or if requested, send raw data to client.
    *
    */
    bool sendTMToClient();


private slots:
    void disconnected();

private :
    QAbstractSocket *m_clientSocket; /**< Socket pointer.*/
    bool m_isDisconnected;
    quint8 m_clientNum;/**< client number.*/
    TAbstractParametersTable* m_parameters; /**< Pointer to the TParameters object of the program. */
    void disableAllRequests();
    int isInActiveList(quint8 reqNum);
    QList<TDispatcherRequest*> m_inactivesRequests;
    QList<TDispatcherRequest*> m_activesRequests;
    int m_dataSentSize;
    quint8 m_nbRequestsAllowedPerClient;
    TDispatcherTMBuilder* m_dispatcherTMBuilder;
    TAbstractCommandManager* m_commandManager;
};
#endif
