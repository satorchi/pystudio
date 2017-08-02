Assignment methods are intended to assign valid values to various
parameters.  It's good practice to use these methods rather than
assigning through a back-door (knowing that Python does not have
"private" variables).

## assign_defaults()
assign default values to parameters
 
## assign_asic(asic)
assign which ASIC is in communication (which half of the 256 TES array)
 
## assign_integration_time(tinteg)
integration time for data gathering
 
## assign_pausetime(pausetime)
wait time between subsequent commands to QubicStudio
 
## assign_ip(ip)
IP address of the QUBIC Local Control Computer (running QubicStudio)
