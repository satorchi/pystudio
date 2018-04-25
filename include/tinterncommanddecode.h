
#ifndef _TINTERNCOMMANDDECODE_H_
#define _TINTERNCOMMANDDECODE_H_

#define 		DISP_RESETALLPARAMETERS_ID 14

#define 		DISP_SETLOGBOOKBASEDIRECTORY_ID 13
#define 		DISP_SETLOGBOOKFILENAME_ID 12
#define 		DISP_ADDCOMMENTTOLOGBOOK_ID 11
#define 		DISP_RESETDECOMMUTATIONFLAGS_ID 10
#define 		DISP_RESETSUBSYSTEM_ID 9
#define 		DISP_SETBACKUPDIR_ID 8
#define 		DISP_RELOADTF_ID 7
#define 		DISP_REQUESTDISPATCHERSTATUS_ID 6

#define 		DISP_STOPBACKUP_ID 5
#define 		DISP_STARTBACKUP_ID 4
#include "definitions.h"
#include <QString>

class TInternCommandDecode
{
public :
TInternCommandDecode();
~TInternCommandDecode();

/** \@brief Decode the StartBackup command's fields.
 *
 * Extract all custom fields of the StartBackup command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] backupsId TBWTBWTBWTBWTBWTBWTBW
 * \@param [out] sessionName TBWTBWTBWTBWTBWTBWTBW
 * \@param [out] comment TBWTBWTBWTBWTBWTBWTBW
 */
void decodeStartBackup(quint8* pbTC , /*@out@*/quint16 *backupsId , /*@out@*/QString *sessionName , /*@out@*/QString *comment);

/** \@brief Decode the StopBackup command's fields.
 *
 * Extract all custom fields of the StopBackup command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] backupsId TBWTBWTBWTBWTBWTBWTBW
 */
void decodeStopBackup(quint8* pbTC , /*@out@*/quint16 *backupsId);

/** \@brief Decode the SetBackupDir command's fields.
 *
 * Extract all custom fields of the SetBackupDir command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] directory TBWTBWTBWTBWTBWTBWTBW
 */
void decodeSetBackupDir(quint8* pbTC , /*@out@*/QString *directory);

/** \@brief Decode the ResetSubsystem command's fields.
 *
 * Extract all custom fields of the ResetSubsystem command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] subsystemId TBWTBWTBWTBWTBWTBWTBW
 */
void decodeResetSubsystem(quint8* pbTC , /*@out@*/quint8 *subsystemId);

/** \@brief Decode the ResetDecommutationFlags command's fields.
 *
 * Extract all custom fields of the ResetDecommutationFlags command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] subsytemId TBWTBWTBWTBWTBWTBWTBW
 */
void decodeResetDecommutationFlags(quint8* pbTC , /*@out@*/quint8 *subsytemId);

/** \@brief Decode the AddCommentToLogbook command's fields.
 *
 * Extract all custom fields of the AddCommentToLogbook command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] key TBWTBWTBWTBWTBWTBWTBW
 ** \@param [out] comment TBWTBWTBWTBWTBWTBWTBW
 */
void decodeAddToLogbook(quint8* pbTC , /*@out@*/QString *key , /*@out@*/QString *comment);

/** \@brief Decode the SetLogBookFilename command's fields.
 *
 * Extract all custom fields of the SetLogBookFilename command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] filename TBWTBWTBWTBWTBWTBWTBW
 */
void decodeSetLogBookFilename(quint8* pbTC , /*@out@*/QString *filename);

/** \@brief Decode the SetLogBookBaseDirectory command's fields.
 *
 * Extract all custom fields of the SetLogBookBaseDirectory command.
 * \@param [in] pbTC Command buffer.
 * \@param [out] directory TBWTBWTBWTBWTBWTBWTBW
 */
void decodeSetLogBookBaseDirectory(quint8* pbTC , /*@out@*/QString *directory);


};

#endif
