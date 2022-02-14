'''
This skript reads in the Vaisala Radiosonde xml file (SynchronizedSoundingData.xml) and outputs a netcdf.

Author: Leonie von Terzi
last edit: 10.2.22
'''

import xml.etree.ElementTree as ET
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from sys import argv

def globalAttr(data,serialNumber):
    '''
    define the global attributes, data: the xarray dataset, serialNumber: serial number of the radiosonde
    '''
    data.attrs['Experiment']= 'TRIPEX-POL, Forschungszentrum Juelich'
    data.attrs['Instrument']= 'Vaisala Radiosonde RS41-SGP, serial number: '+serialNumber
    data.attrs['Data']= 'Produced by Leonie von Terzi, lterzi@uni-koeln.de'
    data.attrs['Institution']= 'Institute for Geophysics and Meteorology, University of Cologne, Germany'
    data.attrs['Latitude']= '50.908547 N'
    data.attrs['Longitude']= '6.413536 E'
    data.attrs['Altitude']= 'Altitude of the JOYCE (www.joyce.cloud) platform: 111m asl'
    data.attrs['process_date'] = str(date.today())
    return data

def varAttr(data,var_info):
    '''
    define the variable attributes, var_info must be a dictionary containing the variable info such as standard_name, units
    e.g.: var_info= {'Height':{'standard_name':'height','units':'m'}}
    '''
    for var in var_info.keys():
      print(var)
      for key in var_info[var].keys():
        data[var].attrs[key] = var_info[var][key]
    
    return data 

# input give by the bash skript, otherwise comment this line and give the pathFile, outPath and date_time yourself. 
#outPath: path where to save the nc file, pathFile: path to xml files, date_time: date and time where the radiosonde was launched, used in naming the nc-file.
pathFile, outPath, date_time = argv[1].split(',') # I need to pass day_number:0:CEL for reprocessing the CEL measurements today    

# sounding data:
tree = ET.parse(pathFile+'/SynchronizedSoundingData.xml') # parse the xml file
root = tree.getroot()
n_rows = len(root)

# meta data:
tree_meta = ET.parse(pathFile+'/SoundingMetadata.xml')
root_meta = tree_meta.getroot()
# now get the serial number of the sonde:
for child in root_meta:
  if child.attrib['MetadataKeyPk'] == 'SONDE_SERIAL_NUMBER':
    sonde_serial_number = child.attrib['MetadataValue']

# define dataframe and variable infos.
df = pd.DataFrame(index=range(n_rows),columns=['Height','Humidity','Temperature','Pressure','WindSpeed','WindDir','Time','Latitude','Longitude','PtuStatus','Altitude']) # Time: DataSrvTime 
var_info = {'Height':{'long_name':'Height above roof platform','standard_name':'Height','units':'m'},
            'Humidity':{'long_name':'relative humidity','standard_name':'humidity','units':'%'},
            'Temperature':{'long_name':'air temperature','standar_name':'temperature','units':'K'},
            'Pressure':{'standard_name':'pressure','long_name':'air pressure','units':'hPa'},
            'WindSpeed':{'standard_name':'wind speed','units':'m/s'},
            'WindDir':{'standard_name':'wind direction','units':'deg'},
            'Time':{'standard_name':'time','units':'UTC'},
            'Latitude':{'standard_name':'latitude','units':'deg'},
            'Longitude':{'standard_name':'longitude','units':'deg'},
            'PtuStatus':{'standard_name':'ptu status','meaning':''},
            'Altitude':{'standard_name':'Altitude','long_name':'height above mean sea level','units':'m'},
            }
# parse each row and save into dataframe            
for var in df.columns:
  print(var)
  for i,child in enumerate(root):
    if var == 'Time':
      varxml = 'DataSrvTime'
      df[var].loc[i] = child.attrib[varxml]
    else:
      varxml = var
      df[var].loc[i] = float(child.attrib[varxml])
    soundingID = child.attrib['SoundingIdPk']
# now set time as the index variable:
df = df.set_index('Time')
# now convert to xarray to save as netcdf
df_xr = df.to_xarray()

# now define all the attributes of the variables used in the dataset:
df_xr = globalAttr(df_xr,sonde_serial_number)
df_xr = varAttr(df_xr,var_info)
# now save into netcdf with predefined outputFolder. Name will be date_launchtime.nc
df_xr.to_netcdf(outPath+date_time+'.nc')
print(df_xr)
print('saved in '+outPath+date_time+'.nc')
