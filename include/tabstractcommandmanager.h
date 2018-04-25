//---------------------------------------------------------------------------
#ifndef TAbstractCommandManagerH
#define TAbstractCommandManagerH
//---------------------------------------------------------------------------

#include "tabstractparameterstable.h"
#include "tlogbook.h"
#include "tabstractsubsystemscommunication.h"
#include "qdispatcherbytearray.h"
#include "tinterncommanddecode.h"
#include "tdispbackups.h"

class TClientsManager;
class TClient;

/** @brief Clients commands manager.
 *
 * This class manages the clients commands (decoding level, execution level).
 */
class TAbstractCommandManager{

  public :
/** @brief Class constructor.
 *
 * Initialize all class variables.
 * @param [in] clients pointer to the clients manager.
 * @param [in] client pointer to the corresponding client.
 * @param [in] clientNum command manager number.
 * @param [in] Parameters pointer to TParameters object.
 * @param [in] DispatcherTMBuilder pointer to TDispatcherTMBuilder object.
 */
    TAbstractCommandManager(TLogBook *m_commandLogBook, TClientsManager* clientsManager, TAbstractParametersTable *Parameters, TAbstractSubSystemsCommunication* subsystemsCommunication, TDispBackups *backups);


/** @brief Class destructor.
 */
   virtual ~TAbstractCommandManager();

/** @brief Initialize the class variables.
 *
 */
    void init();

/** @brief Decode a client command.
 *
 * Decode the client commands (State machine), launch the command execution.
 * @param [in] tcBuff pointer to the command buffer.
 * @param [in] tcBuffSize size of the command buffer.
 */
    void decodeAndExecuteCommands(quint8 *tcBuff, int tcBuffSize);

    void setClient(TClient* client);

    quint16  lastTcCN() {return m_lastTcCN;}


  protected :


/** @brief Launch the command execution according to the command ID.
 */
    void executeCommand();

    /** @brief Virtual method used to execute a custom command.
     */
        virtual quint8 executeCustomCommand(quint16 commandID,quint8* command,quint32 commandSize) = 0;

    /** @brief Virtual method used before sending a command to a subsystem.
     */
    virtual bool checkSubsytemCommandBeforeSendingIt(quint8 subsystemID, quint16 tcID,quint8* command,quint32 commandSize) = 0;

    TClientsManager* _clientManager;            /**< Pointer to the TClients object*/
    TClient* _currentClient;              /**< Pointer to the associated client*/
    TAbstractSubSystemsCommunication* _subsystemsCommunication;    
    TDispBackups* _backups;
    TLogBook* _logBook;

private :
    QDispatcherByteArray *m_currentTC; /**< Current decoding TC buffer*/
    TInternCommandDecode m_interCommandDecode;
    TAbstractParametersTable* m_parameters;      /**< Pointer to the TParameters object of the program. */

    int m_currentState;             /**< Decoding state of the state machine*/
    int m_currentIndex;
    quint32  m_currentTCNW;            /**< NW field of the current command*/
    quint32 m_currentDecodingNB;
    quint16  m_lastTcCN;                 /**< Last TC CN field read*/

};
#endif

