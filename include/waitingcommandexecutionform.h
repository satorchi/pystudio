#ifndef WAITINGCOMMANDEXECUTIONFORM_H
#define WAITINGCOMMANDEXECUTIONFORM_H

#include <QWidget>
#include <QTimer>

namespace Ui {
class WaitingCommandExecutionForm;
}

class WaitingCommandExecutionForm : public QWidget
{
    Q_OBJECT

public:
    explicit WaitingCommandExecutionForm(QWidget *parent = 0);
    ~WaitingCommandExecutionForm();

    void startWaitingFor(QString commandName, bool showOnlyOnError =false);
    void setFailureMessage(QString msg);
    void setSuccessMessage(QString msg);

private:
    Ui::WaitingCommandExecutionForm *ui;
    QTimer* m_showHideTimer;

    bool m_wantShowForm;
protected slots:
    void showHideForm();

};

#endif // WAITINGCOMMANDEXECUTIONFORM_H
