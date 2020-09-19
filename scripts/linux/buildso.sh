RUNDIR=`pwd`
cd `dirname $0`
MYDIR=`pwd`
ROOT=${MYDIR}/../..
ENV=.env.36
SRC=${ROOT}/pilsner
DIST=${ROOT}/bin
TEST=${ROOT}/test
cd ${ROOT}
rm -r ${ROOT}/build
rm -r ${ROOT}/cythonized
mkdir -p ${DIST}
${ROOT}/${ENV}/bin/python3 ${TEST}/compile.py build_ext --inplace
mv ${SRC}/*.so ${DIST}
cd ${RUNDIR}
