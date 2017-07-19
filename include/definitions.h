#ifndef _DEFINES_H_
#define _DEFINES_H_
#include <QtGlobal>


/** \def DISPATCHER_KERNEL_V
  *  @brief Dispatcher Kernel version. */
#define DISPATCHER_KERNEL_V   0x0205


typedef union
{
    quint8  b[8]; // b[0] poids faible --> b[1] ... b[7] poids forts
    quint16  w;
    quint32 dw;
    quint64 qw;
    double d;
    float f;
    int i;
} CONVERSION_TYPE;


typedef union
{
    quint8  b[4]; // b[0] poids faible --> b[1] ... b[3] poids forts
    float f;

} CONVERSION_FLOAT;

typedef union
{
    quint8  b[8]; // b[0] poids faible --> b[1] ... b[7] poids forts
    double d;

} CONVERSION_DOUBLE;

typedef union
{
    quint8  b[8]; // b[0] poids faible --> b[1] ... b[7] poids forts
    quint64 q;
} CONVERSION_64;

/******************************************************************************/
// Dispatcher general defines

/** \def DISPATCHER_BACKUP_ON
  *  @brief Dispatcher mode is backup ON. */
#define DISPATCHER_BACKUP_ON               1


/** \def DISPATCHER_BACKUP_OFF
  *  @brief Dispatcher mode is backup OFF. */
#define DISPATCHER_BACKUP_OFF              2


/** \def CODAGE_STRING
  *  @brief Tag used to reconize string parameter. */
#define CODAGE_STRING           0x80
#define CODAGE_BYTEARR          0x40
#define CODAGE_DOUBLE           0x27
#define CODAGE_FLOAT            0x13
#define CODAGE_SIGNED           0x08
#define IS_SIGNED(paramCodage)                ((paramCodage)  & CODAGE_SIGNED)
#define IS_STRING(paramCodage)                ((paramCodage & 0xFF) == CODAGE_STRING)
#define IS_STRING_OR_BYTEARR(paramCodage)     ((paramCodage & 0xC0))
#define IS_BYTEARR(paramCodage)               ((paramCodage & 0xFF) == CODAGE_BYTEARR)
#define IS_FLOAT(paramCodage)                 ((paramCodage & 0xFF) == CODAGE_FLOAT)
#define IS_DOUBLE(paramCodage)                ((paramCodage & 0xFF) == CODAGE_DOUBLE)
#define IS_INT(paramCodage)                   (((paramCodage) & 0xF0) == 0)
#define SIZE_OF_PARAMETER(paramCodage)        ((((paramCodage) & 0x7) + 1) * 8)
#define ARRAY_SIZE_OF_PARAMETER(paramCodage)  ((paramCodage) >> 8)
#define PARAMETER_TYPE(paramCodage)  ((paramCodage) &0xFF)

/******************************************************************************/

/** \def TF_FLAG
  *  @brief define the TF parameter flag. */
#define TF_FLAG 0x800000

/** \def REQUEST_TF
  *  @brief Macro to build a TF ID. */
#define REQUEST_TF(p) ((p)|TF_FLAG)

/** \def IS_TF_REQUEST */
#define IS_TF_REQUEST(p) ((p)&TF_FLAG)

/** \def TF_MASK */
#define TF_MASK     0x7FFFFF


/******************************************************************************/
/** Dispatcher Decommutation Errors codes.
   */
/** \def DECOMM_NO_ERROR
  *  @brief Error status : no error. */
#define DECOMM_NO_ERROR             0

/** \def DECOMM_HEADER_ERROR
  *  @brief Error status : bad header field. */
#define DECOMM_HEADER_ERROR          1

/** \def DECOMM_SIZE_ERROR
  *  @brief Error status : size overflow. */
#define DECOMM_SIZE_ERROR            2

/** \def DECOMM_EOP_ERROR
  *  @brief Error status : bad EOP field. */
#define DECOMM_EOP_ERROR             4

/** \def DECOMM_CHECKSUM_ERROR
  *  @brief Error status : bad checksum */
#define DECOMM_CHECKSUM_ERROR        8

/** \def DECOMM_ID_ERROR
  *  @brief Error status : bad Id */
#define DECOMM_ID_ERROR             16


/******************************************************************************/
/** Dispatcher ACK Errors codes.
   */
/** \def ACK_NO_ERROR
  *  @brief Error status : no error. */
#define ACK_NO_ERROR            0

/** \def ACK_INVALID_COMMAND
  *  @brief Error status : The command format is not correct. */
#define ACK_INVALID_COMMAND     1

/** \def ACK_COMMAND_REJECTED
  *  @brief Error status : The command can't be executed. */
#define ACK_COMMAND_REJECTED    2

/** \def ACK_UNKNOW_ID
  *  @brief Error status : The command ID is unknow. */
#define ACK_UNKNOW_ID           3

/** \def ACK_COMMAND_NOT_SENT
  *  @brief Error status : The command is not sent. */
#define ACK_COMMAND_NOT_SENT    4

/** \def ACK_TIMEOUT
  *  @brief Error status :Ack timeout. */
#define ACK_TIMEOUT         5


/** \def ACK_FROM_SUBSYS
  *  @brief Error status : The ACK comes from Subsystem. See Errors reports field. */
#define ACK_FROM_SUBSYS           0xFF


/******************************************************************************/
/* flag DISP_BackupsState
 *****************************************************************************/

/** \def BACKUP_RAW_ACTIVATED_MASK
  *  @brief mask for the raw backup. */
#define BACKUP_RAW_ACTIVATED_MASK   0x0001

/** \def BACKUP_RAW_DESACTIVATED_MASK
  *  @brief mask for the raw backup. */
#define BACKUP_RAW_DESACTIVATED_MASK   0xFFFE

/** \def BACKUP_HK_ACTIVATED_MASK
  *  @brief mask for the raw backup. */
#define BACKUP_HK_ACTIVATED_MASK    0x0002

/** \def BACKUP_HK_DESACTIVATED_MASK
  *  @brief mask for the raw backup. */
#define BACKUP_HK_DESACTIVATED_MASK    0xFFFD


/******************************************************************************/

#endif
