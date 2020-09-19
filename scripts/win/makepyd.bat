@echo off
set RUNDIR=%cd%
set ROOT=%~dp0..\..
set ENV=.env.37
set SRC=%ROOT%\pilsner
set DIST=%ROOT%\bin
set TEST=%ROOT%\test
cd %ROOT%
rmdir /S /Q %ROOT%\build
rmdir /S /Q %ROOT%\cythonized
rmdir /S /Q %DIST%
if not exist %DIST%\nul mkdir %DIST%
call %ROOT%\%ENV%\Scripts\python %TEST%\compile.py build_ext --inplace
move /Y %SRC%\*.pyd %DIST%\
copy /Y %SRC%\__init__.py %DIST%\
copy /Y %SRC%\*.xml %DIST%\
cd %RUNDIR%
