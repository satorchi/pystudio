//---------------------------------------------------------------------------

#ifndef TVirtualDeviceH
#define TVirtualDeviceH
//---------------------------------------------------------------------------
#include <stdlib.h>
#include <QString>
#include "trawdataemitter.h"

/** \def SEND
  *  @brief ERREUR lors de l'envoi d'une TC
 */
#define SEND_FAILED                 0
#define SEND_SUCCESS_WAITING_ACK    1
#define SEND_SUCCESS_NO_WAITING     2
#define SEND_NOT_ALLOWED            3


/** @brief Virtual class, define the OBSW communication interface.
 */
class TVirtualDevice
{
public :
    /** @brief Constructor.
 *
 * Initialize the class parameter.
 */
    TVirtualDevice(QString name, int deviceID, bool returnAck, TRawDataEmitter *rawDataEmitter):m_name(name),m_connectionState(0), m_rawDataEmitter(rawDataEmitter), m_deviceID(deviceID),m_deviceReturnAck(returnAck)
    {
    }

    /** @brief Destructor.
 */
    virtual ~TVirtualDevice()
    {
    }
    QString name(){return m_name;}
    int id(){return m_deviceID;}
    bool returnAck(){return m_deviceReturnAck;}
    quint64 connectionState(){return m_connectionState;}
    void setReturnAck(bool returnAck){m_deviceReturnAck = returnAck;}

    /** @brief Virtual definition of open link function.
         *
         * try to open the link.
         * @return open result
         */
    virtual bool open()=0;

    /** @brief Virtual definition of close link function.
         *
         * close the link.
         * @return close result.
         */
    virtual bool close()=0;


    /** @brief Virtual definition of link read function.
         *
         * read data.
         * @param [in] buffer to fill with data read.
         * @param [in/out] readDataSize max read size, return number of quint8 read.
         * @return number of quint8 read.
         */

    virtual int read(quint8* buffer,int readDataSize)=0;


    /** @brief Virtual definition of link read function.
         *
         * reset link.
         */

    virtual bool reset()=0;


    /** @brief Virtual definition of write function.
 *
 * send data.
 *  utiliser m_rawDataEmitter->send(0x80 | m_deviceID,tcBuff, tcBuffSize);
 * @param [in] buffer data buffer to send.
 * @param [in] bufferSize size of data buffer.
 * @return number of quint8 written.
 */
    virtual int write(quint8* buffer,int bufferSize)=0;
protected:
    QString m_name;
    quint64 m_connectionState; /** etat de la connection (code d'erreur ou autre)*/
    TRawDataEmitter* m_rawDataEmitter; /** permet de transmettre les commandes au rawDataAnalyser*/

private :
    int m_deviceID;
    bool m_deviceReturnAck;
};


class TInactiveDevice : public TVirtualDevice
{
public:
    TInactiveDevice(QString name, int deviceID, bool returnAck):TVirtualDevice(name,deviceID,returnAck,NULL){m_connectionState = 0xFF;}

    bool open(){return true;}
    bool close(){return true;}
    bool reset(){return true;}
    int read(quint8* ,int){return 0;}
    int write(quint8* ,int ) {return 0;}
};

#endif
