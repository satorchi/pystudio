#ifndef TLOGBOOK_H
#define TLOGBOOK_H

#include <QTextStream>
#include <QDir>
#include <QHash>

class TLogBook
{
public:
    enum DisplayFlag {
        Hexadecimal         = 0x00000001,
        text                = 0x00000002
    };

    TLogBook();

    virtual void addCustomCommand(quint32 id, const quint8* command, quint32 size,const DisplayFlag &flag = Hexadecimal);
    virtual void addInternCommand(quint32 id,quint8* command, quint32 size,const DisplayFlag &flag = Hexadecimal);
    virtual void addSubsysCommand(quint8 subsystemID,quint16 id,quint8* command, quint32 size,const DisplayFlag &flag = Hexadecimal);
    virtual void addSubsysTelemetry(quint8 subsystemID, quint32 id,const quint8* tm, quint32 size,const DisplayFlag &flag = Hexadecimal);
    virtual void addComment(QString comment); // add an entry like yyyyMMdd-hhmmss.zzz: Comment => errorStr
    virtual void addError(QString errorStr); // add an entry like yyyyMMdd-hhmmss.zzz: Error => errorStr
    virtual void addCustom(QString key, QString comment); // add an entry like yyyyMMdd-hhmmss.zzz: Key => comment
    void setTcDataDisplaySize(int size); // -1 display all else display only size bytes
    void setTmDataDisplaySize(int size); // -1 display all else display only size bytes
    void setMaxLinePerFile(quint32 nbLines);
    void closeCurrentFile();
    bool setBaseDirectory(QString baseDirectory);
    bool setNewFilename(QString filename);
    void setUTCDatationEnabled(bool enabled);
    QString baseDirectory();
    QString currentFileName();

protected :
    virtual void addNewEntry(QString logEntry);
    virtual QString getNewAutomaticLogbookFile() = 0;
    QHash<quint64, QString> commandDescriptionHash;
    QHash<quint64, QString> telemetryDescriptionHash;
    QHash<quint16, QString> subsystemsDescriptionHash;
    quint32 m_currentNumberLines;

private:
    bool setNewFile(QString file);
    void buildDataEntry(bool isCommand,QString description, const quint8* command, quint32 size,const DisplayFlag flag = Hexadecimal);
    QTextStream m_logStream;
    QString m_baseDirectory;
    QString m_fileName;
    QFile m_logFile;
    quint32 m_tcDataSize;
    quint32 m_tmDataSize;
    quint32 m_maxNumberLines;
    bool m_utcDatation;
    QString m_char2Hex[256];
};

#endif // TLOGBOOK_H
