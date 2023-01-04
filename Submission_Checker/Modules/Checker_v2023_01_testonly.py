#-------------------------------------------------------------------------------
# Name:        	FI Checker

checker_version = '2023.01'

# Purpose:	   	This tool checks the FMP, AR or AWS submission (according to the 
#				FIM Technical Specifications 2009 or 2017) and outputs a validation report 
#				in html format.The report will be saved at the same folder level where your 
#				geodatabase is saved. This validation report is equivalent to stage 1 and 
#				stage 2 checks of the current (2017) FI portal.
#
#			   
# Author:      Ministry of Natural Resources and Forestry (MNRF)
#
# Created:     24/02/2017
# Copyright:   MNRF 2017
#
# Updates:	May 24, 2018
#			Added error_limit variable to give the user an option to create a full or shortened error detail section.
#			Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#			
#-------------------------------------------------------------------------------
print("Importing Arcpy...")
import arcpy
# import Modules.Reference as R
import Reference as R

# python version used by the user
import sys
arcpy.AddMessage("Python version: v%s"%sys.version) # eg. 3.9.11 [MSC v.1931 64 bit (AMD64)]



# # user inputs:
# plan  = 'FMP'
# fmu = 'Gordon_Cosens' ## case-sensitive. can't have spaces - ie Big_Pic
# year = 2020 ## must be an integer
# fmpStartYear = 2020 ## must be an integer
# workspace = r'C:\DanielK_Workspace\_TestData\Gordon_Cosens\BMI_sample\MU438_20BMI00_sample.gdb' ## gdb where the submission feature classes are stored.
# dataformat = 'feature class' # eg. 'shapefile','feature class' or 'coverage'
# tech_spec_version = "Latest" # "Old (2009)" or "Latest"
# tech_spec_version = "2020" if tech_spec_version == "Latest" else "2009"
# SubID = 'test02' # optional. cant have special character since the filename will include submission id. Also, the Reference.findSubID will try to find the submission ID in fmu/plan/year/ folder.
# error_limit = "Limit to 50 errors per error type" # "Limit to 50 errors per error type" or "Full Report"

# user inputs:
plan  = 'AWS'
fmu = 'Temagami' ## case-sensitive. can't have spaces - ie Big_Pic
year = 2022 ## must be an integer
fmpStartYear = 2019 ## must be an integer
workspace = r'C:\DanielK_Workspace\_TestData\Temagami\AWS\2022\FM-898-2019-AWS-1712\Layers\shp_short' ## gdb where the submission feature classes are stored.
dataformat = 'shapefile' # eg. 'shapefile','feature class' or 'coverage'
tech_spec_version = "Latest" # "Old (2009)" or "Latest"
tech_spec_version = "2020" if tech_spec_version == "Latest" else "2009"
SubID = 'arcpro' # optional. cant have special character since the filename will include submission id. Also, the Reference.findSubID will try to find the submission ID in fmu/plan/year/ folder.
error_limit = "Limit to 50 errors per error type" # "Limit to 50 errors per error type" or "Full Report"


if error_limit == 'Limit to 50 errors per error type':
	error_limit = 50
else:
	error_limit = 999999 # need to have some upper limit due to the html file size limitation.

from CheckAll import Check
try:
	class_check = Check(plan,fmu,year,fmpStartYear,workspace, dataformat, tech_spec_version, error_limit, checker_version, SubID)
	class_check.run()
finally:
	arcpy.AddMessage("\nTool version: v%s"%checker_version)




