@echo off
set RUNDIR=%cd%
set ROOT=%~dp0..\..
set ENV=.env.37
set TEST=%ROOT%\test
set FILES=ut_model.py ut_utility.py functional.py performance.py
cd %ROOT%
(for %%f in (%FILES%) do (
    echo Running %%f
    call %ROOT%\%ENV%\Scripts\python.exe %TEST%\%%f -b
))
cd %RUNDIR%
