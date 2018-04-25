#ifndef TPROJECTSUBSYSTEMSCOMMUNICATION_H
#define TPROJECTSUBSYSTEMSCOMMUNICATION_H

#include "tabstractsubsystemscommunication.h"
#include "customdispatcher.h"
class TProjectSubsystemsCommunication :public TAbstractSubSystemsCommunication
{
public:
    TProjectSubsystemsCommunication(TRawDataEmitter* rawDataEmitter);
    virtual ~TProjectSubsystemsCommunication();
    TVirtualDevice* device(int subsystemId);

protected:
    int nbSubsystems(){return NB_SUB_SYSTEMS;}
    void allocateVars();
    void buildDevices(TRawDataEmitter* rawDataEmitter);
};
#endif // TPROJECTSUBSYSTEMSCOMMUNICATION_H