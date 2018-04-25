#ifndef QTIMEOUT_H
#define QTIMEOUT_H

#include <QThread>
#include <QElapsedTimer>

class SleeperThread : public QThread
{
public:
    static void msleep(unsigned long msecs)
    {
        QThread::msleep(msecs);
    }
    static void  usleep ( unsigned long usecs )
    {
        QThread::usleep(usecs);
    }
};

class QTimeout
{
public:
    QTimeout();
    void restart(double msTimeout);
    bool hasElapse(qint64* nSecondsToTimout = NULL);
    qint64 goToTimeOut();

private:
    qint64 m_timeoutTime;
    QElapsedTimer m_elapseTimer;
    qint64 delayToTimeout();
    qint64 m_timeOutDelay;

};


#endif // QTIMEOUT_H
