#ifndef TDISPBACKUPS_H
#define TDISPBACKUPS_H

#include "tabstractparamscomputer.h"
#include "thkbackup.h"
#include "trawbackup.h"


class TDispBackups
{
public:
    TDispBackups(TAbstractParamsComputer *tfComputer, quint64 maxRawFileSize);
    ~TDispBackups();

    virtual bool startNewSession(quint16 backupMask, QString sessionName, QString comment) = 0;
    virtual void closeCurrentSession(quint16 backupMask) = 0;

    THKBackup* hkBackup();
    TRawBackup* rawBackup();

protected:
    THKBackup* m_hkBackup;
    TRawBackup* m_rawBackup;
};

#endif // TABSTRACTBACKUPS_H
