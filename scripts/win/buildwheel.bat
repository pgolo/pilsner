@echo off
rem Usage:
rem buildwheel.bat path\to\python36 path\to\python37 path\to\python38
rem
rem The package will be placed in dist\ directory.

set RUNDIR=%cd%
set MYDIR=%~dp0
set ROOT=%MYDIR%\..\..
set REQUIREMENTS=%ROOT%\requirements-build.txt
set ENV=%ROOT%\.env.build
set SHIPPING=%ROOT%\shipping

:BUILD
if (%1)==() (goto FINISH)
if not exist "%1" (echo "%1": Python not found && shift && goto BUILD)
cd %ROOT%
virtualenv -p %1 %ENV%
%ENV%\Scripts\python -m pip install --no-cache-dir -r %REQUIREMENTS%
%ENV%\Scripts\python %SHIPPING%\make_setup.py bdist_wheel
%ENV%\Scripts\python %ROOT%\setup.py bdist_wheel
rmdir /S /Q %ENV%
rmdir /S /Q %ROOT%\pilsner.egg-info
rmdir /S /Q %ROOT%\build
del /Q %ROOT%\pilsner\model.c
del /Q %ROOT%\pilsner\utility.c
shift
goto BUILD

:FINISH
del /Q %ROOT%\setup.py
cd %RUNDIR%
