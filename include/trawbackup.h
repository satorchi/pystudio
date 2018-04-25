//---------------------------------------------------------------------------
#ifndef TRAWBACKUP_H
#define TRAWBACKUP_H
//---------------------------------------------------------------------------
#include <stdio.h>
#include <QString>
#include <QHash>
#include "tsinglebackup.h"

/** @brief Used to backup the data in a raw format.
 *
 * This class manages the backup of raw data in segmented files.
 */
class TRawBackup: public TSingleBackup
{
public :


/** @brief Class constructor.
 *
 * Initialize all class variable, create the backup directory if it doesn't exist.
 * @param [in] directory the backup directory.
 * @param [in] fileSize the maximal file size.
 */
    TRawBackup(quint64 fileSize);

/** @brief Class destructor.
 *
 * close the current file if it's open.
 */
    virtual ~TRawBackup();

/** @brief save the buffer in the current file.
 *
 * open a new file if needed, save the data and close the file if the maximal size is reached.
 * @param [in] subsystem subsytem ID to read.
 * @param [in] buffer the data to save.
 * @param [in] size the data size.
 * @return void.
 */
    void save(quint8 subsystem, const quint8 *buffer, unsigned int size);
    void saveDatation();
    bool startNewSession(QString directory, QString sessionName, QString comment);
    void closeCurrentSession();
    QString currentFile(){ return m_currentFileStr;}
    void flush();
    void setSubsystemName(quint8 id, QString name);

private :
    QString m_currentFileStr;
    quint64 m_maxFileSize;       /**< Maximal file size. */
    FILE* m_currentFile;     /**< Handle of the current opened file. */
    quint64 m_currentFileSize;   /**< Size of the current open file. */

    QHash<quint8 ,QString> m_subsystemsNames;

/** @brief Create and open a new file if needed.
 *
 * If the backup is ON and the no file is open, a new file is created.
 * The filename format is disp_file-YYMMDD-HHMMSS.dat.
 * The m_currentFile variable will contain the new file handle.
 */
    void openNewFileIfNeeded();

/** @brief close the current file if maximal file size is reached.*/

    void closeFileIfNeeded();

/** @brief close the current open file.*/

    void closeFile();

};

#endif
