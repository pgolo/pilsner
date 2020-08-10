cd `dirname $0`
MYDIR=`pwd`
ROOT=${MYDIR}/../..
ENV=.env.36
cd -
mkdir -p ${ROOT}/.vscode
echo '{'>${ROOT}/.vscode/settings.json
echo '    "python.pythonPath": "${workspaceFolder}/'${ENV}'/bin/python3",'>>${ROOT}/.vscode/settings.json
echo '    "code-runner.executorMap": {"python": "./'${ENV}'/bin/python3"}'>>${ROOT}/.vscode/settings.json
echo '}'>>${ROOT}/.vscode/settings.json
echo '{'>${ROOT}/.markdownlint.json
echo '    "MD024": {"siblings_only": true},'>>${ROOT}/.markdownlint.json
echo '    "MD013": {"line_length": 1000}'>>${ROOT}/.markdownlint.json
echo '}'>>${ROOT}/.markdownlint.json
