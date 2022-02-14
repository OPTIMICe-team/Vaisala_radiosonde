Codes to convert vaisala MW41 xml output into netcdf
The conversion is done with python3, you need xarray, pandas and numpy installed on you computer
xml2netcdfCTRL.sh controls the conversion, you need to give the path to the python and shell skripts in pathPro; the location of the Radiosonde mwx folder
For simplicity this needs to be run as hatpro user, you can either directly log in as hatpro or use the sshpass I implemented (you need to add the pwd yourself). If you are anyways logged in as hatpro then you need to uncomment line 23 and comment line 21
Author: Leonie von Terzi, lterzi@uni-koeln.de
