@echo off
rem This script runs the script and passes all arguments to it

rem Remember the current working directory
set original_directory=%cd%

rem Change the path to your Python executable (if needed)
set python_executable=python

rem Set the path to the directory of the Python script 
set script_directory=%~dp0

rem Join the path with the script name to create an abspath
set python_script=%script_directory%\m1_changelogger.py

rem Pass all arguments to the Python script
%python_executable% %python_script% %*