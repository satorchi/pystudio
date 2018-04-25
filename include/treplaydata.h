//---------------------------------------------------------------------------

#ifndef TReplayDataH
#define TReplayDataH
//---------------------------------------------------------------------------

#include <stdio.h>
#include <QDir>

/** \def PLAY_ONE_FILE
  *  @brief Used to set the replay mode(m_playMode) to "one file replay". */
#define PLAY_ONE_FILE   1
/** \def PLAY_DIRECTORY
  *  @brief Used to set the replay mode(m_playMode) to "directory replay". */
#define PLAY_DIRECTORY  2
/** \def PLAY_OFF
  *  @brief Used to set the replay mode(m_playMode) to "OFF". */
#define PLAY_OFF        3


/** @brief Class used to replay data.

 */
class TReplayData
{
public :
    /** @brief Constructor.
 *
 * Initialize the class parameter. Try to open the file or directory, if this
 * operation failed, the replay mode is set to OFF.
 * @param [in] fileOrDirectory file or directory to replay
 */
    TReplayData(int nbSubsystems);
    /** @brief Destructor.
 *
 * If a file is open, close it.
 */
    ~TReplayData();

    void startReadFileOrDirectory(QString fileOrDirectory);

    /** @brief Implementation of the virtual read function.
 *
 * If the replay mode is ON, read a part of the current file. If the file is finished
 * try to open an other file if the m_fileOrDirectory is a directory.
 * @param [in] subsystem subsytem ID to read.
 * @param [out] buffer pointer of pointer to be updated with the data buffer read.
 * @param [out] bufferSize number of quint8 read.
 * @return True if some data has been read, false else.
 */
    int read(quint8 subsystem, quint8* buffer, int bufferSize);

private :

    bool close();

    /** @brief open the next file to replay.
 *
 * If mode is PLAY_ONE_FILE, open the file during the first function call, else close it.
 * If mode is PLAY_DIRECTORY, open the next file found inside the directory, if a file was open, close it.
 * Else nothing to do.
 */
    void openNextFile();  /**< TParameter dispatcher object pointer. */

    int m_playMode;  /**< Contains the replay mode (PLAY_ONE_FILE, PLAY_DIRECTORY or PLAY_OFF). */
    FILE* m_currentFile; /**< Handle of the current opened file. */
    QString m_fileOrDirectory;/**< filename or directory to read. */
    quint8* m_header; /**< Used to read temporary headers*/

    QFileInfoList m_directoryFileList;
    int m_fileListIndex;
    int m_nbSubsystems;
};
#endif
