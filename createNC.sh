# this file accesses the python3 skript which produces the nc files from Vaisala radiosonde xml files. 
#Input needed: date_time: date and time when the radiosonde was launched (used in finding the correct file)
#              fileID: ID at the beginning of the file (JOYCE)
#              pathPro: path where the python skript is
#              pathRadiosonde: path to the radiosonde data (which is also currently where we save the data, 
#              if you want to change that, adjust ${pathRadiosonde} in line 22 (python3 xml2netcdf.py ...) to the outputPath you want 
#              if you want to save in /data/obs you need to be logged in as hatpro, the file xml2netcdfCTRL.sh does that part and needs to be executed first
# Author: Leonie von Terzi
# Date: 2022-02-10

#date_time=$1
#fileID=$2
filemwx=$1
pathPro=$2
pathRadiosonde=$3
fileID=${filemwx%.*}
echo $fileID
# make mwx into zip file so we can open it
cp $filemwx ${fileID}.zip #${pathRadiosonde}${fileID}_${date_time}.mwx  ${pathRadiosonde}${fileID}_${date_time}.zip

#if [[ "${pathRadiosonde}${fileID}_${date_time}" == * ]]; then
#    echo ${pathRadiosonde}${fileID}_${date_time} already there, now removing the file
    
#else
# remove potential old file unzipped files
rm -r ${fileID} #${pathRadiosonde}${fileID}_${date_time}
echo now unzipping ${fileID}.zip
#unzip the zip file
unzip ${fileID}.zip -d ${fileID}/
#fi
cd $pathPro
# now execute the python skript
python3 xml2netcdf.py ${fileID},${pathRadiosonde} #,${date_time}

#remove the zip file and the file in which the zip was unzipped.
rm -r ${fileID}
rm -r ${fileID}.zip
