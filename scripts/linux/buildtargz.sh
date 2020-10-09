# Usage:
# buildtargz.sh path/to/python
#
# The package will be placed in dist/ directory.

RUNDIR=`pwd`
cd `dirname $0`
MYDIR=`pwd`
ROOT=${MYDIR}/../..
ENV=${ROOT}/.env.build
SHIPPING=${ROOT}/shipping

if [ $# -eq 0 ]
then
    cd ${RUNDIR}
    exit
fi

if [ ! -f $1 ]
then
    echo $1: Python not found
    cd ${RUNDIR}
    exit
fi

cd ${ROOT}

virtualenv -p $1 ${ENV}
${ENV}/bin/python3 ${SHIPPING}/make_setup.py sdist
${ENV}/bin/python3 ${ROOT}/setup.py sdist

rm -r ${ENV}
rm -r ${ROOT}/pilsner.egg-info
rm ${ROOT}/setup.py

cd ${RUNDIR}
