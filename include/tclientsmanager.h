//---------------------------------------------------------------------------
#ifndef _TAbstractTClientsManager_H
#define _TAbstractTClientsManager_H
//---------------------------------------------------------------------------

#include "tclient.h"
#include "tabstractparameterstable.h"
#include "tabstractsubsystemscommunication.h"
#include "tabstractcommandmanager.h"

#include <QTcpServer>
#include <QObject>


/** \def SUBSYS_ACCESS_OFF
  *  @brief Used to configure OnOff parameter of subystemsAccess function.
 */
#define SUBSYS_ACCESS_OFF 0

/** \def SUBSYS_ACCESS_ON
  *  @brief Used to configure OnOff parameter of subystemsAccess function.
  */
#define SUBSYS_ACCESS_ON  1

/** \def CLIENT_LIST_FULL
  *  @brief Result of insertClient function if the client list is full.
 */
#define CLIENT_LIST_FULL    -1



/** @brief Clients connection manager.
 *
 * This class manages the client connection with a socket server.
 */
class TClientsManager : public QObject
{
    Q_OBJECT
public:
    /** @brief Constructor.
 *
 * Initialize all class variable, create the TClients object and the socket server.
 * @param [in] Parameters pointer to TParameters object.
 * @param [in] port server port.
 * @param [in] DataReceiver pointer to the Subystems communication layer.
 */
    TClientsManager(TAbstractParametersTable* parameters, int port, TAbstractSubSystemsCommunication* subsysComm);

    /** @brief Destructor.
 *
 * release all created instances in constructor.
 */
    virtual ~TClientsManager();

    /** @brief Get commands from clients and execute them.
 *
 */
    void getAndExecuteCommands();

    /** @brief Activate or not the commands exclusion mode. (default = false)
     *  if the command exclusion mode is active, only one client can send command and the client must
     *  request and release the command access with commands startSubsystemAccess and stopSubsystemAccess
     */
    void setFreeModeCommand(bool enabled);

    /** @brief Build dispatch TM.
 *
 * For each Subystem TM received, the function is called to build dispatcher TM
 * for clients who requested them.
 * @param [in] receiveACK the TM received is an ACK.
 * @param [in] ACKStatus if the TM is an ACK, ACKStatus contains the TM ACK status.
 * @param [in] ACKStatusSize if the TM is an ACK, ACKStatusSize contains the TM ACK status size.
 * @param [in] ACKClientNum if the client number to send the ACK, to be used when the ACK<->Client is managed by user.
 */
    void buildDispatchTM(bool receiveACK, const quint8 *ACKStatus, quint8 ACKStatusSize, int ACKClientNum = -1);

    /** @brief Build dispatch TM for requests with timeout.
 *
 */
    void buildDispatchTMWithTimeOut();

    quint8 sendTCToSubystems(int clientIndex,quint8 subsystemID, quint8 *tcBuff,int tcBuffSize);
    bool subystemsAccess(int clientIndex, quint8 OnOff, char* name);

    int dataSentToClients(bool resetValue);
    int nbActiveRequests();
    int nbClients();
    char* getMasterClientName();
    void assignClients(TClient**clients, quint8 nbClientsAllowed);

private:

    int insertClient(QTcpSocket *clntSocket);
    void releaseClient(int indexClient);

    QTcpServer *m_tcpServer; /**< Pointer to the socket server. */
    TAbstractParametersTable*    m_parameters; /**< Pointer to the TParameters object of the program.*/
    TClient** m_pClients; /**< TClient pointer list. */
    int m_nbClientsConnected;
    TAbstractSubSystemsCommunication* m_pSubystemsCommunication; /**< Pointer to Subystems communication layer. */
    int m_sentDataSize;
    char m_masterClientName[255 + 1/* '/0' */]; /**< Name of the master client (client with TC access ON). */
    int m_masterClientIndex; /**< Master client number. */
    int m_freeModeCommand;
    quint8 *m_tcReadBuffer;   /**< Buffer used to build temporary TC. */
    quint8 m_nbClientsAllowed;

public slots:
    /** @brief Detect the clients connections.
     *
     * Accept the clients connections, insert them in the client list if it's not full.
     */
    void detectNewClient();

};
#endif
