#ifndef QDISPATCHERWIDGET_H
#define QDISPATCHERWIDGET_H

#include <QWidget>
#include <QTimer>
#include "tdispatcheraccesskernel.h"

namespace Ui {
    class QDispatcherWidget;
}

class QDispatcherWidget : public QWidget
{
    Q_OBJECT

public:
    explicit QDispatcherWidget(QWidget *parent = 0);
    ~QDispatcherWidget();

    void init(TDispatcherAccessKernel* dispatcherAccess);

private:
    Ui::QDispatcherWidget *ui;

    TDispatcherAccessKernel* m_dispatcherAccess;
    QTimer m_timerRefresh;

private slots:
    void updateLabels();
    void on_pushButton_clicked();
};

#endif // QDISPATCHERWIDGET_H
