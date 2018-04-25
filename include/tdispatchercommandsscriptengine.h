#ifndef QDISPATCHERCOMMANDSSCRIPTENGINE_H
#define QDISPATCHERCOMMANDSSCRIPTENGINE_H

#include "tdispatcherkernelscriptengine.h"
#include "tdispatcheraccess.h"

extern TDispatcherAccess* _dispatcherAccess;

class TDispatcherCommandsScriptEngine : public TDispatcherKernelScriptEngine
{
public:
    TDispatcherCommandsScriptEngine(QObject *parent ,TDispatcherAccess * dispatcherAccess,QPlainTextEdit* fileTextEdit);
};
#endif // QDISPATCHERCOMMANDSSCRIPTENGINE_H