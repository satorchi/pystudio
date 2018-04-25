#ifndef TKERNELPARAMSTOSTRING_H
#define TKERNELPARAMSTOSTRING_H
#include <QString>

class TKernelParamsToString
{
public:
    TKernelParamsToString();
    static QString toString(int parameterTf, double value);
};

#endif // TKERNELPARAMSTOSTRING_H
