#ifndef TPARAMSTOSTRING_H
#define TPARAMSTOSTRING_H
#include <QString>
#include "tkernelparamstostring.h"

class TParamsToString : public TKernelParamsToString
{
public:
    TParamsToString();

    static QString toString(int parameterTf, double value);
};

#endif // TPARAMSTOSTRING_H
