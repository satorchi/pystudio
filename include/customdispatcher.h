//---------------------------------------------------------------------------
#ifndef CustomDispatcherH
#define CustomDispatcherH
//---------------------------------------------------------------------------

#include <QString>

/** \def DISPATCHER_CUSTOM_VERSION
  *  @brief User Dispatcher version. */
#define DISPATCHER_CUSTOM_VERSION   0x0100
/******************************************************************************/
// limites des requetes, connexions, configuration du port.

/** \def NB_SUB_SYSTEMS
  *  @brief Number of sub systems to manage. */
#define NB_SUB_SYSTEMS 12

/** \def DISPATCHER_RAWEMITTER_PORT
  *  @brief Dispatcher TCP/IP raw emitter port.  Default 9946*/
#define DISPATCHER_RAW_EMITTER_PORT 9946

/******************************************************************************/

/** \def DEFAULT_BACKUP_FILE_SIZE
  *  @brief Raw backup file size. Default 52428800 (50Mo)*/
#define DEFAULT_BACKUP_FILE_SIZE 52428800

/******************************************************************************/
/** \def MAX_SUBSYS_TM_SIZE
  *  @brief Maximal TM message field size. */
#define MAX_SUBSYS_TM_SIZE 2500

/******************************************************************************/
/** \def MAX_SUBSYSTEM_RATE
  *  @brief Maximal TM message field size. */
#define MAX_SUBSYSTEM_RATE 20000000ULL

/** \def DISPATCHER_KERNEL_LOOP_PER_SECOND
  *  @brief Nombre d'execution de la boucle principale par sec Default = 100*/
#define DISPATCHER_KERNEL_LOOP_PER_SECOND 100


// start includes dispatcher Wizard DON'T TOUCH
#define INDEX_OF_MULTINETQUICMANAGER 0
#define MULTINETQUICMANAGER_ID 2
#define INDEX_OF_SWITCHES 1
#define SWITCHES_ID 3
#define INDEX_OF_CFIBERS 2
#define CFIBERS_ID 8
#define INDEX_OF_IMACRT1 3
#define IMACRT1_ID 4
#define INDEX_OF_IMACRT2 4
#define IMACRT2_ID 5
#define INDEX_OF_IMACRT3 5
#define IMACRT3_ID 6
#define INDEX_OF_IMACRT4 6
#define IMACRT4_ID 7
#define INDEX_OF_HWP 7
#define HWP_ID 9
#define INDEX_OF_CALIBSOURCES 8
#define CALIBSOURCES_ID 10
#define INDEX_OF_PLATFORMCONTROLER 9
#define PLATFORMCONTROLER_ID 11
#define INDEX_OF_PLATFORMMOTORS 10
#define PLATFORMMOTORS_ID 12
#define INDEX_OF_GPS 11
#define GPS_ID 13
const unsigned char subsystemIds[NB_SUB_SYSTEMS] = {MULTINETQUICMANAGER_ID ,SWITCHES_ID ,CFIBERS_ID ,IMACRT1_ID ,IMACRT2_ID ,IMACRT3_ID ,IMACRT4_ID ,HWP_ID ,CALIBSOURCES_ID ,PLATFORMCONTROLER_ID ,PLATFORMMOTORS_ID ,GPS_ID };
#define SUBSYSTEM_NAMES_STR  QString("MultiNetQuicManager,Switches,CFibers,IMACRT1,IMACRT2,IMACRT3,IMACRT4,HWP,CalibSources,PlatformControler,PlatformMotors,GPS")
#define SUBSYSTEM_NAME_BY_ID(id) (id == MULTINETQUICMANAGER_ID)?QString("MultiNetQuicManager"):(id == SWITCHES_ID)?QString("Switches"):(id == CFIBERS_ID)?QString("CFibers"):(id == IMACRT1_ID)?QString("IMACRT1"):(id == IMACRT2_ID)?QString("IMACRT2"):(id == IMACRT3_ID)?QString("IMACRT3"):(id == IMACRT4_ID)?QString("IMACRT4"):(id == HWP_ID)?QString("HWP"):(id == CALIBSOURCES_ID)?QString("CalibSources"):(id == PLATFORMCONTROLER_ID)?QString("PlatformControler"):(id == PLATFORMMOTORS_ID)?QString("PlatformMotors"):(id == GPS_ID)?QString("GPS"):QString("unknown subsytem")
// stop includes dispatcher Wizard DON'T TOUCH

#define NUM_CLIENT_CONNECT 15

#define MAX_NB_REQUEST_PER_CLIENT 10

#define DISPATCHER_SERVER_PORT 3002

#endif




