import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob

def speHumi2RelHum(speHum, temp, press):
    w = speHum/(1-speHum)
    es = 611*np.exp(17.27*(temp - 273.16)/(237.3 + (temp - 273.16)))
    ws = 0.622*(es/(press-es))      
    relHum = 100 *(w/ws)
    
    return relHum

def relHum2specHum(datasel,rhi=False,offset=False):
    if rhi==True:
        relHum = calc_rh_from_rhi(datasel)    
    else:
        if offset == True:
            relHum = datasel['rh_offset']
        else:
            relHum = datasel['Humidity']
    es = 611*np.exp(17.27*(datasel['Temperature'] - 273.16)/(237.3 + (datasel['Temperature'] - 273.16)))
    e = relHum/100*es
    Rv = 461.5; Rl = 287.05 #specific gas constant for water vapour and dry air (in J/kg/K)
    rho_w = e/(Rv*datasel['Temperature']); rho_l = (datasel['Pressure']-e)/(Rl*datasel['Temperature'])# density of wet and dry air
    qv = rho_w/(rho_l+rho_w)
    
    return qv
def psatw(atmo): #PURE ELEMENTAL FUNCTION psat_water( T ) result ( psatw ) in mo_atmo.f90
    '''
    calculate relative humidity with respect to water from temperature
    INPUT: atmo: dictionary which must contain numpy arrays including the key T
    '''
    constants = dict() #collection of coefficients from McSnow
    constants["T_3"] =  273.15 #! [K]     melting temperature of ice/snow #from mo_atmotypes
    constants["A_w"]  = 1.72693882e1 #, &  !..constant in saturation pressure - liquid #from mo_atmotypes
    constants["B_w"]  = 3.58600000e1  #!..constant in saturation pressure - liquid #from mo_atmotypes
    constants["e_3"]  = 6.10780000e2  #!..saturation pressure at T = T_3#from mo_atmotypes
    return constants["e_3"] * np.exp(constants["A_w"] * (atmo["Temperature"]-constants["T_3"]) / (atmo["Temperature"]-constants["B_w"]))

def psati(atmo): #PURE ELEMENTAL FUNCTION psat_water( T ) result ( psatw ) in mo_atmo.f90
    '''
    calculate relative humidity with respect to ice from temperature
    INPUT: atmo: dictionary which must contain numpy arrays including the key T
    '''
    constants = dict() #collection of coefficients from McSnow
    constants["T_3"] =  273.15 #! [K]     melting temperature of ice/snow #from mo_atmotypes
    constants["A_i"]  = 2.18745584e1 #, &  !..constant in saturation pressure - ice #from mo_atmotypes
    constants["B_i"]  = 7.66000000e0  #!..constant in saturation pressure - ice #from mo_atmotypes
    constants["e_3"]  = 6.10780000e2  #!..saturation pressure at T = T_3#from mo_atmotypes
    return constants["e_3"] * np.exp(constants["A_i"] * (atmo["Temperature"]-constants["T_3"]) / (atmo["Temperature"]-constants["B_i"]))

def calc_rhi(atmo,double=False, offset=False): #calculate rh over ice from rh over water and saturation pressure equation in SB
    '''
    calculate the relative humidity with respect to ice from the relative humidity with respect to water and temperature
    INPUT:  atmo: dictionary which must contain numpy arrays including the keys rh and T
    '''

    psat_w = psatw(atmo)
    psat_i = psati(atmo)
    rhi = psat_w/psat_i*atmo["Humidity"]
    return rhi

def calc_rh_from_rhi(atmo):
    '''
    calculate the relative humidity with respect to water from the relative humidity with respect to ice and temperature
    INPUT:  atmo: dictionary which must contain numpy arrays including the keys rh and T
    '''
    psat_w = psatw(atmo)
    psat_i = psati(atmo)
    rh = psat_i/psat_w*atmo['rhi_offset']
    return rh

# path to radiosondes:    
pathRadio = '/data/obs/site/jue/radiosondes/Vaisala/' 
files = sorted(glob.glob(pathRadio+'*.nc'))

for f in files:
  print(f)
  f_name = f.split('.nc')[0]
  data = xr.open_dataset(f)# open file
  print(data)
  
  data['Pressure'] = data.Pressure *100
  data['Temperature'] = data.Temperature#-273.15
  data['Temperature_cel'] = data.Temperature-273.15 # temperature in celsius. need in Kelvin too for calculation of RHi
  data['Humidity'] = data.Humidity
  data['specific_humidity'] = relHum2specHum(data)
  data['Humidity_ice'] = calc_rhi(data)
  data['WindSpeed'] = data.WindSpeed
  data['Height'] = data.Height
  #data['Height'] = data.Height - data.Height.min()
  print(data.Temperature)

  fig,ax = plt.subplots(figsize=(15,5),ncols=3,sharey=True)
  ax[0].plot(data.Temperature_cel,data.Height)
  ax[0].set_ylabel('Altitude [m]')
  ax[0].set_xlabel('Temperature [°C]')
  ax[0].grid()
  ax[1].plot(data.Humidity,data.Height,label='RHw')
  ax[1].plot(data.Humidity_ice,data.Height,label='RHi')
  ax[1].set_xlabel('Humidity %')
  ax[1].legend()
  ax[1].grid()
  ax[2].plot(data.WindSpeed,data.Height)
  ax[2].set_xlabel('WindSpeed [m/s]')
  ax[2].grid()
  fig.suptitle('Radiosonde measurements ')#+data.Time[0].dt.strftime('%Y%m%d %H%M%S').values)
  plt.tight_layout()
  #plt.savefig(data.Time[0].dt.strftime('%Y%m%d_%H%M%S').values+'.png')
  plt.savefig(f_name+'.png')
  print(f_name)
  plt.show()
  
  fig,ax = plt.subplots(figsize=(10,5),ncols=2,sharey=True)
  ax[0].plot(data.Humidity,data.Temperature_cel,label='RHw')
  ax[0].plot(data.Humidity_ice,data.Temperature_cel,label='RHi')
  ax[0].set_xlabel('Humidity %')
  ax[0].set_ylabel('Temperature [°C]')
  ax[0].legend()
  ax[0].grid()
  ax[0].set_ylim([10,data.Temperature.min()-5])
  ax[1].plot(data.specific_humidity,data.Temperature)
  ax[1].set_xlabel('specific_humidity')
  ax[1].grid()
  fig.suptitle('Radiosonde measurements ')#+data.Time[0].dt.strftime('%Y%m%d %H%M%S').values)
  plt.tight_layout()
  #plt.savefig(data.Time[0].dt.strftime('%Y%m%d_%H%M%S').values+'T_coord.png')
  plt.savefig(f_name+'_T_coord.png')
  plt.close()

