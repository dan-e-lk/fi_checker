
:: HOW TO RUN THIS BATCH FILE
:: <path to ArcGIS python exe> <path to Checker_v2_command_line.py file> <aws, ar or fmp> 
::		<fmu name eg.gordon_cosens> <submission year> <plan start year> 
::		<path to the gdb or to the parent folder of shpfiles/coverage files> 
::		<fc/shp/cov depending on your file type> <old or new (tech spec version)> <limit or nolimit> 
::		<suffix - don't use special characters>

REM Here's an example:
C:\Python27\ArcGIS10.3\python.exe S:\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\InDevelopment\Submission_Checker\Checker_v2_command_line.py aws Hearst 2018 2009 C:\TEMP\testers\AWS_NEW_GDB\Hearst_AWS2018.gdb fc new limit 98765
