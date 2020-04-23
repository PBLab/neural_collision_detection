#!/usr/bin/bash

#~/ncd_n -V ~/vascular/vascular.0.999.obj -N cube400.obj -o test_dense -m batch -f test_dense.txt -i dense_centers.csv -c 10 -z -q -n

set -x

ID=$1
REVERSE_FLAG=$2

if [ -z ${ID} ]; then
	echo "ID must be set"
	exit
fi

CREATE_CUBE="create_cube.py"
if [ ${REVERSE_FLAG} ] && [ ${REVERSE_FLAG} == "-r" ]; then
	CREATE_CUBE="create_horizontal_cube.py"
fi

RADIUS=4
HEIGHT=400
CUBE_NAME=cube_${ID}.obj
TMP_DIR=just_some_dir
TMP_RES=test_temp_res_${ID}.txt
CENTERS_NAME=centers_${ID}.csv
OUTPUT_NAME=heatmap_${ID}.png

rm -rf ${TMP_DIR} ${TMP_RES}

python ${CREATE_CUBE} ${CUBE_NAME} ${RADIUS} ${HEIGHT}
python create_centers.py ${CENTERS_NAME} ${HEIGHT} ${REVERSE_FLAG}
~/ncd_n -V ~/vascular/vascular.0.999.obj -N ${CUBE_NAME} -o ${TMP_DIR} -m batch -f ${TMP_RES} -i ${CENTERS_NAME} -c 10 -z -q -n
python parse_results.py ${TMP_RES} ${RADIUS} ${OUTPUT_NAME} ${REVERSE_FLAG}
#wc -l ${OUTPUT_NAME}
