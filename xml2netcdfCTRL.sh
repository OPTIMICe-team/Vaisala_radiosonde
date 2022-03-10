# control of the xml2netcdf.py python skript to convert vaisala xml files to netcdf. 
# Input: date and launch time
# if you want to save in the same folder as it is stored currently, you need to be logged into hatpro, otherwise the nc file can not be saved
# here this is done automatically in the sshpass line
# dependency: python3, xarray, pandas, numpy, 
# you need the createNC.sh file
# output: netcdf file 
# Author: Leonie von Terzi
# date: 20220210
echo "type USERNAME"
read USERNAME

echo "type password"
read -s PASS

echo "type PC name"
read PCNAME

pathPro=/home/lvonterz/radiosondes/ #/work/lvonterz/radiosond_tests/ #/home/lvonterz/radiosondes/ # path to processing skripts
pathRadiosonde=/data/obs/site/jue/radiosondes/Vaisala/ # path to vaisala radiosone mwx folder

cd $pathPro
# this will soon be updated to process all files on a certain day
date=20220108 # date to process
time=134904 # time of start
fileID=JOYCE # fileID in the beginning of mwx file name

files2process=${pathRadiosonde}${fileID}_${date}*.mwx
echo $files2process

for filename in $files2process; do
  echo ${filename%.*}
# if not logged in as hatpro:
  sshpass -p "${PASS}" ssh -X ${USERNAME}@${PCNAME} 'bash -s' < createNC.sh $filename $pathPro $pathRadiosonde # ${date}_${time} $fileID $pathPro $filesRadiosonde
# if logged in as hatpro
#bash createNC.sh ${date}_${time} $fileID $pathPro $filesRadiosonde
done
