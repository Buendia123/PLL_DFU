#!/bin/bash

function usage() {
echo "Usage:"
echo "-p port (1,2,3,4)"

exit $1
}

PORT=0
opt_string="p:h"
while getopts ${opt_string} flag; do
    case "${flag}" in
    p) PORT=${OPTARG} ;;
    h) usage 0 ;;
    *) echo "UNDECODED ${flag} ${OPTARG}"
       usage 1
       ;;
    esac
done

if [ 0 -eq ${PORT} ]; then
    echo "Need -p PORT_NUM"
    exit 1
fi

if [ ${PORT} -gt 4 ] || [ ${PORT} -lt 1 ]; then
    echo "Port ${PORT} out of range [1,2,3,4]"
    exit 1
fi

#  BUS number for UTP is 3,4,5,6 for ports 1,2,3,4
BUS=$(( PORT + 2 ))

FW_V1="firmware/EM200QDX.0.52.0"
FW_V2="firmware/EM200QDX.0.52.0"

time_epoch_0=`/bin/date +%s`
#################### step 1
echo "MCU image change to 0.52.0 (v2)"
python ALdfu.py -d linux -port ${BUS} -component MCU -b ${FW_V2}
rc=$?
time_epoch_1=`/bin/date +%s`
runtime1=$(( time_epoch_1 - time_epoch_0 ))
echo "x.x.x  -> 0.52.0 (v2)  ${runtime1} seconds"

if [ 0 -ne $rc ]; then
    echo "***************************************"
    echo "* ERROR: Change to 0.52.0 failed (v2) *"
    echo "***************************************"
    exit 1
fi

#################### step 2
echo "DSP image change to 227.0.36 (v2)"
python ALdfu.py -d linux -port ${BUS} -component DSP -b ${FW_V2}
rc=$?
time_epoch_2=`/bin/date +%s`
runtime2=$(( time_epoch_2 - time_epoch_1 ))
echo "x.x.x  -> 227.0.36 (v2) ${runtime2} seconds"

if [ 0 -ne $rc ]; then
    echo "***************************************"
    echo "* ERROR: Change to 227.0.36 failed (v2) *"
    echo "***************************************"
    exit 1
fi

#################### step 3
echo "MCU image change to 0.52.0 (v1)"
python ALdfu.py -d linux -port ${BUS} -component MCU -b ${FW_V2}
rc=$?
time_epoch_3=`/bin/date +%s`
runtime3=$(( time_epoch_3 - time_epoch_2 ))
echo "x.x.x  -> 0.52.0 (v1)  ${runtime3} seconds"

if [ 0 -ne $rc ]; then
    echo "***************************************"
    echo "* ERROR: Change to 0.52.0 failed (v1) *"
    echo "***************************************"
    exit 1
fi

#################### step 4
echo "DSP image change to 227.0.36 (v1)"
python ALdfu.py -d linux -port ${BUS} -component DSP -b ${FW_V2}
rc=$?
time_epoch_4=`/bin/date +%s`
runtime4=$(( time_epoch_4 - time_epoch_3 ))
echo "x.x.x  -> 227.0.36 (v1) ${runtime4} seconds"

if [ 0 -ne $rc ]; then
    echo "***************************************"
    echo "* ERROR: Change to 227.0.36 failed (v1) *"
    echo "***************************************"
    exit 1
fi

echo "**************************************************"
echo "* x.x.x -> 0.52.0   (v2) -> 0.52.0   (v1) PASSED *"
echo "* x.x.x -> 227.0.36 (v2) -> 227.0.36 (v1) PASSED *"
echo "**************************************************"

runtime5=$(( time_epoch_4 - time_epoch_0 ))


echo "Run times:"
echo "    x.x.x         -> 0.52.0   (v2) ${runtime1} seconds"
echo "    x.x.x         -> 227.0.36 (v2) ${runtime2} seconds"
echo "    0.52.0 (v2)   -> 0.52.0   (v1) ${runtime3} seconds"
echo "    227.0.36 (v2) -> 227.0.36 (v1) ${runtime4} seconds"
echo "Total time: ${runtime5} seconds"
