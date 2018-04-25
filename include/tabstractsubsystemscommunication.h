//---------------------------------------------------------------------------

#ifndef TAbstractSubSystemsCommunicationH
#define TAbstractSubSystemsCommunicationH
//---------------------------------------------------------------------------
#include "tvirtualdevice.h"
#include "treplaydata.h"
#include <QHash>

/** @brief Implement the communication interface.
 * Class to be written by user.
 */
class TAbstractSubSystemsCommunication
{
public :
    /** @brief Constructor.
 *
 * Initialize the class parameter.
 */
    TAbstractSubSystemsCommunication();

    /** @brief Destructor.
 */
    ~TAbstractSubSystemsCommunication();

    bool isInReplayMode();
    void setReplayMode(bool activate);
    void setReplayFile(QString filename);
    QString name(quint8 subsystem);

    quint64 connectionState(quint8 subsystem);

   /** \brief Implementation of isActive function.
 *
 * Used to check if the subsystem is active
 */
    bool isActive(quint8 subsystem);

    /** @brief Implementation of open function.
 *
 * Used to open the communication with Subystems
 */
    bool open(quint8 subsystem);

    /** @brief Implementation of close function.
 *
 * Used to close the communication with Subystems
 */
    bool close(quint8 subsystem);

    /** @brief Implementation of read function.
 *
 * read Subystems data.
 * @param [in] subsystem subsytem ID to read.
 * @param [out] buffer pointer of pointer to be updated with the data buffer read.
 * @param [out] bufferSize number of quint8 read.
 * @return True if the read function acquire data from Subystems with success, false else.
 */
    unsigned int read(quint8 subsystem, quint8* buffer,unsigned int bufferSize);

    /** @brief Implementation of write function.
 *
 * Send data to Subystems.
 * @param [in] subsystemID ID of the subsystem.
 * @param [in] buffer data buffer to send.
 * @param [in] bufferSize size of data buffer.
 * @return True if the write function send all data to Subystems with success, false else.
 */
    quint8 write(quint8 subsystemID,quint8* buffer,int bufferSize);

    /** @brief Implementation of reset function.
 *
 * Send data to Subystems.
 * @param [in] subsystemID ID of the subsystem.
 * @return True if the reset success, false else.
 */
    bool reset(quint8 subsystemId);
protected:
    virtual int nbSubsystems() = 0;
    virtual void allocateVars() = 0;
    TVirtualDevice** m_deviceList;
    bool  *m_deviceIsActive;
    TReplayData* m_replayDevices;
    bool m_replayMode;
    QHash<int, int > m_devicesIDs;
};
#endif
