@echo off
rem Usage:
rem buildtargz.bat path\to\python
rem
rem The package will be placed in dist\ directory.

set RUNDIR=%cd%
set MYDIR=%~dp0
set ROOT=%MYDIR%\..\..
set ENV=%ROOT%\.env.build
set SHIPPING=%ROOT%\shipping

if (%1)==() (cd %RUNDIR% && exit)
if not exist "%1" (echo "%1": Python not found && cd %RUNDIR% && exit)
cd "%ROOT%"
virtualenv -p "%1" "%ENV%"
"%ENV%"\Scripts\python "%SHIPPING%"\make_setup.py sdist
"%ENV%"\Scripts\python "%ROOT%"\setup.py sdist
rmdir /S /Q "%ENV%"

del /Q "%ROOT%"\setup.py

cd %RUNDIR%
