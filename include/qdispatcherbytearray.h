#ifndef QDISPATCHERBYTEARRAY_H
#define QDISPATCHERBYTEARRAY_H

#include <QtGlobal>
#include <string.h> // memcpy

class QDispatcherByteArray
{
public:
    QDispatcherByteArray(quint32 capacity = 0);
    ~QDispatcherByteArray();
    void reserve(quint32 size,bool resizeToLessSize = false);
    void resize(quint32 size,bool resizeToLessSize = false);
    int capacity();
    int size();
    void clear();

    inline void append(quint8 byte){
        if (m_size == m_capacity)
            increaseArray();
        m_byteArray[m_size++] = byte;
    }

    inline void append(const void* buffer, quint32 bufferSize){
        prepareIncSize(bufferSize);
        memcpy(endOfCurrentData(),buffer,bufferSize);
        incSize(bufferSize);
    }


    inline const quint8* constData(){
        return m_byteArray;
    }
    inline quint8* endOfCurrentData(){
        return &m_byteArray[m_size];
    }

    inline quint8* data(){
        return m_byteArray;
    }
    inline quint8 at(quint32 index){
        if (index < m_size)
            return m_byteArray[index];
        else
            return 0;
    }
    inline void replace(quint32 index, quint8 value){
        if ((m_byteArray != NULL) && (index < m_size))
            m_byteArray[index] = value;
    }

private:
    void increaseArray(quint32 minimumNewSize = 0);
    void incSize(quint32 deltaSize);
    void prepareIncSize(quint32 deltaSize);

    quint8* m_byteArray;
    quint32 m_capacity;
    quint32 m_size;
};

#endif // QDISPATCHERBYTEARRAY_H
