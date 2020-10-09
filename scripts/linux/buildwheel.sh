# Usage:
# buildwheel.sh path/to/python3.6 path/to/python3.7 path/to/python3.8
#
# The wheels will be placed in dist/ directory.

RUNDIR=`pwd`
cd `dirname $0`
MYDIR=`pwd`
ROOT=${MYDIR}/../..
REQUIREMENTS=${ROOT}/requirements-build.txt
ENV=${ROOT}/.env.build
SHIPPING=${ROOT}/shipping

cd ${ROOT}

for PY in "$@"
do
    if [ ! -f ${PY} ]
    then
        echo ${PY}: Python not found
    else
        virtualenv -p ${PY} ${ENV}
        ${ENV}/bin/python3 -m pip install --no-cache-dir -r ${REQUIREMENTS}
        ${ENV}/bin/python3 ${SHIPPING}/make_setup.py bdist_wheel
        ${ENV}/bin/python3 ${ROOT}/setup.py bdist_wheel
        rm -r ${ENV}
        rm -r ${ROOT}/pilsner.egg-info
        rm -r ${ROOT}/build
        rm ${ROOT}/pilsner/model.c
        rm ${ROOT}/pilsner/utility.c
        rm ${ROOT}/setup.py
    fi
done

cd ${RUNDIR}
