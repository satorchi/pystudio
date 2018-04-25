#ifndef QDISPATCHERPARAMETERSSCRIPTENGINE_H
#define QDISPATCHERPARAMETERSSCRIPTENGINE_H

#include "tdispatchercommandsscriptengine.h"
#include <tdispatcheraccess.h>

class TDispatcherParametersScriptEngine : public TDispatcherCommandsScriptEngine
{
public:
    explicit TDispatcherParametersScriptEngine(QObject *parent ,TDispatcherAccess * dispatcherAccess,QPlainTextEdit* fileTextEdit);
};
#endif // QDISPATCHERPARAMETERSSCRIPTENGINE_H