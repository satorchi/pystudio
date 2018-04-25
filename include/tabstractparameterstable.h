#ifndef TABSTRACTPARAMETERSTABLE_H
#define TABSTRACTPARAMETERSTABLE_H

#include <QtGlobal>
#include <QString>
#include <QMutex>
#include "tabstractparamscomputer.h"
#include "definitions.h"


template <typename T>
T *AllocateDynamicArray( int dim1)
{
    T *dynamicArray = new T [dim1];

    return dynamicArray;
}

template <typename T>
T **AllocateDynamicArray( int dim1, int dim2)
{
    T **dynamicArray;

    dynamicArray = new T*[dim1];
    for( int i = 0 ; i < dim1 ; i++ )
        dynamicArray[i] = new T [dim2];

    return dynamicArray;
}

template <typename T>
T ***AllocateDynamicArray( int dim1, int dim2,  int dim3)
{
    T ***dynamicArray;

    dynamicArray = new T**[dim1];
    for( int i = 0 ; i < dim1 ; i++ )
    {
        dynamicArray[i] = new T*[dim2];
        for( int j = 0 ; j < dim2 ; j++ )
            dynamicArray[i][j] = new T[dim3];
    }
    return dynamicArray;
}

template <typename T>
void FreeDynamicArray(T* dArray)
{
    delete [] dArray;
}

template <typename T>
void FreeDynamicArray(T** dArray)
{
    delete [] *dArray;
    delete [] dArray;
}

template <typename T>
void FreeDynamicArray(T*** dArray)
{
    delete [] **dArray;
    delete [] *dArray;
    delete [] dArray;
}


class TAbstractParametersTable
{
public :
    /** \@brief Constructor.
 *
 * Initialize the class parameters.
 */
    TAbstractParametersTable();

    virtual quint32 nbParameters() = 0;
    virtual quint32 parametersCRC() = 0;
    virtual quint32 tfLibVersion() = 0;
    virtual quint32 indexedArraySize(quint32 parameterId) = 0;
    virtual void resetDecommutationParameters(quint8 subsytemId) = 0;
    virtual void resetToDefaultValues() = 0;
    virtual void setSessionName(QString sessionName) = 0;
    virtual void reloadTF() = 0;
    QString stringValue(quint32 parameterId);
    int setStringValue(quint32 parameterId, const char* string);
    QByteArray byteArrayValue(quint32 parameterId);
    int setByteArrayValue(quint32 parameterId, const char* buffer, int size);

    quint32* paramCodage; /**< Size of each parameters (8, 16, 32, 64 bits). */
    quint32* tfParamArraySize; /**< Size of each parameters (8, 16, 32, 64 bits). */
    void** paramAddress;/**< pointer array. */
    double** paramAddressTF;/**< pointer array. */
    quint8*  paramOptions;/**< Indicate parameter option (0 = no option, 1 = use tab indexed by parameter).*/
    quint32*  paramOptionsInformations;/**< Indicate parameter option information.*/
    quint16*  tabParamReceived;/**< Indicate how many time each parameters has been received. */
    bool isRunning;

private:
    QMutex m_stringOrByteArrMutex;
};
#endif // TABSTRACTPARAMETERSTABLE_H
