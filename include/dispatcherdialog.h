#ifndef DISPATCHERDIALOG_H
#define DISPATCHERDIALOG_H

#include <QDialog>
#include <QAbstractButton>
#include "tdispatcheraccesskernel.h"

namespace Ui {
    class DispatcherDialog;
}

class DispatcherDialog : public QDialog
{
    Q_OBJECT

public:
    explicit DispatcherDialog(QWidget *parent = 0);
    ~DispatcherDialog();

    void open(TDispatcherAccessKernel* dispatcher);

private:
    Ui::DispatcherDialog *ui;



private slots:

};

#endif // DISPATCHERDIALOG_H
