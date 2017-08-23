#include "helpers.h"

void connect_request(TDispatcherAccess* object, slot_request slot) {
  QObject::connect(object, &TDispatcherAccess::requestArrived, slot);
}
