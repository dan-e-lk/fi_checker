print("Importing Arcpy...")
import arcpy
import sys
import Modules.Reference as R



# # user inputs:
plan  = sys.argv[1] ## Must be one from aws, ar and fmp. not case-sensitive.
fmu = sys.argv[2] ## case-sensitive. can't have spaces - ie Big_Pic
year = int(sys.argv[3]) ## Submission year - eg. 2020
fmpStartYear = int(sys.argv[4]) ## must be an integer
workspace = sys.argv[5] ## gdb/folder where the submission feature classes are stored.


dataformat = sys.argv[6] # has to be 'shp','fc','cov'.
dataformat_dict = {'shp':'shapefile', 'fc':'feature classes', 'cov':'coverage'}
dataformat = dataformat_dict[dataformat]


tech_spec_version = sys.argv[7] # 'old' or 'new'
if tech_spec_version == 'old':
	tech_spec_version = "2009"
else:
	tech_spec_version = "2017"

error_limit = sys.argv[8] # 'limit' or 'nolimit'
if error_limit == 'nolimit':
	error_limit = 999999
else:
	error_limit = 50


SubID = sys.argv[9] # cant have special character since the filename will include submission id. Also, the Reference.findSubID will try to find the submission ID in fmu/plan/year/ folder.


from Modules.CheckAll import Check
class_check = Check(plan,fmu,year,fmpStartYear,workspace, dataformat, tech_spec_version, error_limit, SubID)

class_check.run()