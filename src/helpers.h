#include "tdispatcheraccess.h"

typedef void (* slot_request)(int);

void connect_request(TDispatcherAccess*, slot_request);
