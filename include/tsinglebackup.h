#ifndef TSINGLEBACKUP_H
#define TSINGLEBACKUP_H

#include <QtGlobal>
#include <QString>

class TSingleBackup
{
public:
    TSingleBackup(quint16 backupId);

    void setBaseDirectory(QString baseDirectory);
    /*
     * bool startNewSession(QString directory, QString sessionName, QString comment);
     * return true if directory is valid or directory can be created
*/
    virtual bool startNewSession(QString directory, QString sessionName, QString comment);
    virtual void closeCurrentSession();
    quint16 backupId();

    QString backupDirectory();
    QString baseDirectory();
    QString comment();
    QString sessionName();
    bool isSaving();
    quint64 sessionFileSize();
    virtual void flush();

protected :

    quint64 m_maxFileSize;
    quint64 m_sessionFilesSize;
    QString m_backupDir;
    QString m_baseDirectory;
    QString m_sessionName;
    QString m_comment;
    quint16 m_backupId;
    bool    m_saving;
};

#endif // TBACKUP_H
