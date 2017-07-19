#ifndef TAbstractParamsComputer_H
#define TAbstractParamsComputer_H

#include <QString>
#include <limits>
#include <QList>

class TAbstractParametersTable;
const double dMax = std::numeric_limits<double>::max();

class TAverage
{
public :
        TAverage(int size);
        ~TAverage();
        void reset();
        double addValueAndGetAverage(double value);
private:
        double* m_tabValues;
        int m_currentIndex;
        int m_size;
        int m_nbValues;
        double m_sum;

};

class ParamDescription
{
public :
        enum TFType {
            noTF,
            linear,
            script,
            compiled
        };

    ParamDescription(){
        typeOfTf = ParamDescription::noTF;
        minWarning = -dMax;
        minAlert = -dMax;
        maxWarning = dMax;
        maxAlert = dMax;
        a = 1;
        b = 0;
        function="";
        unit ="";
        rawUnit = "";
        autoCalculateTF = false;
    }

    TFType typeOfTf;
    double a;
    double b;
    QString function;
    QString unit;
    QString rawUnit;
    QString realName;
    QString dispName;
    QString description;
    int precision;
    double minWarning;
    double minAlert;
    double maxWarning;
    double maxAlert;
    double value;
    bool autoCalculateTF;
};

class TAbstractParamsComputer
{
public:
    enum TFAlert {
        inTheRange,
        warning,
        alert
    };
    TAbstractParamsComputer();
    virtual ~TAbstractParamsComputer() {}

    void updateTfParameter(TAbstractParametersTable* parameters, unsigned int parameterId);
    double calculate(int parameterId, double value, QList<double>* listOfExtraParameters = NULL);
    double calculate(TAbstractParametersTable *parameters, int parameterId, double value, QList<double>* listOfExtraParameters = NULL);
    void autoCalculateIfNeeded(TAbstractParametersTable* parameters,QList<unsigned int>* listOfDecodedParameters);
    double invCalculate(int parameterId, double value);

    void updateTF();
    int fileVersion();
    QString unit(int parameterId);
    QString rawUnit(int parameterId);
    int precision(int parameterId);
    bool hasTf(int parameterId);
    bool canInvCalculate(int parameterId);
    QString realName(int parameterId);
    QString dispName(int parameterId);
    QString description(int parameterId);
    TFAlert checkAlert(int parameterId, double value);
    ParamDescription* getParamDescription(int parameterId);

protected :
        virtual double customProcess(int parameterTf, double value, QList<double>* listOfExtraParameters = NULL)=0;
        virtual double customProcess(TAbstractParametersTable* parameters, int parameterTf, double value, QList<double>* listOfExtraParameters = NULL)=0;


private :
    QList<ParamDescription*> m_paramsDescriptions;
    int m_currentFileVersion;
};

#endif // TAbstractParamsComputer_H
