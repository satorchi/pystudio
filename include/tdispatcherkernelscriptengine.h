#ifndef QDISPATCHERKERNELSCRIPTENGINE_H
#define QDISPATCHERKERNELSCRIPTENGINE_H

#include <QScriptEngine>
#include <QPlainTextEdit>
#include <QLabel>
#include "tdispatcheraccesskernel.h"
#include "tabstractparamscomputer.h"

#define MAX_FILE_CONTEXT    5

extern TAbstractParamsComputer*   _paramComputer;
extern QLabel *_imageLabel;
extern QPlainTextEdit* _logTextEdit;
extern bool _wantAbortScript;

void newRequestArrived(quint8 requestNum);
void writeErrorToLog(QString errorMessage);


class TDispatcherKernelScriptEngine : public QScriptEngine
{
    Q_OBJECT
public:
    explicit TDispatcherKernelScriptEngine(QObject *parent,
                                           TDispatcherAccessKernel * dispatcherAccess,
                                           QPlainTextEdit* fileTextEdit = NULL);

    QScriptValue	evaluate ( const QString & program, const QString & fileName = QString(), int lineNumber = 1 );
    QScriptValue	evaluate ( const QScriptProgram & program );

    QStringList functionsList;
    QStringList kernelFunctionsList;
    void setFileTextEdit(QPlainTextEdit* fileTextEdit);
    void setToggleButton(QAction* toggleButton);
    QPlainTextEdit* fileTextEdit(quint8 fileContext);
protected:
    void addParameterGetter(const QString &name);


private :
    void loadDescrFile();
signals:

public slots:
    void requestArrived(int requestNum);

};

#endif // QDISPATCHERKERNELSCRIPTENGINE_H
