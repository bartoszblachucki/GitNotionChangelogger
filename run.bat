rem author: Bartosz Błachucki, GameDevTube
rem This script runs the script m1_changelogger.py script using python and passes all arguments to it
rem Use it to quickly iterate during development or if you don't want to/can't use a built exe
@echo off

rem Change the path to your Python executable (if needed)
set python_executable=python

rem Set the path to the directory of the Python script 
set script_directory=%~dp0

rem Join the path with the script name to create an abspath
set python_script=%script_directory%\m1_changelogger.py

rem Pass all arguments to the Python script
%python_executable% %python_script% %*