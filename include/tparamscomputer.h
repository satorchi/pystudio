#ifndef TPARAMSCOMPUTER_H
#define TPARAMSCOMPUTER_H

#include "tabstractparamscomputer.h"



class TParamsComputer : public TAbstractParamsComputer
{
public:
    TParamsComputer();
    ~TParamsComputer();

protected :
        double customProcess(int parameterTf, double value, QList<double>* listOfExtraParameters = NULL);
        double customProcess(TAbstractParametersTable* parameters,int parameterTf, double value, QList<double>* listOfExtraParameters = NULL);

};

#endif // TPARAMSCOMPUTER_H
