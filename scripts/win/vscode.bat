@echo off
set ROOT=%~dp0..\..
set ENV=.env.37
if not exist %ROOT%\.vscode\nul mkdir %ROOT%\.vscode
echo {>%ROOT%\.vscode\settings.json
echo     "python.pythonPath": "${workspaceFolder}\\%ENV%\\Scripts\\python.exe",>>%ROOT%\.vscode\settings.json
echo     "code-runner.executorMap": {"python": "call .\\%ENV%\\Scripts\\python"}>>%ROOT%\.vscode\settings.json
echo }>>%ROOT%\.vscode\settings.json
echo {>%ROOT%\.markdownlint.json
echo     "MD024": {"siblings_only": true},>>%ROOT%\.markdownlint.json
echo     "MD013": {"line_length": 1000}>>%ROOT%\.markdownlint.json
echo }>>%ROOT%\.markdownlint.json
