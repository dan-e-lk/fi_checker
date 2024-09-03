# main_arcpy.py only works with arcgis toolbox and requires arcpy
# this script is only a brdige between ArcGIS GUI and the csv_checker module

import arcpy
import csv_checker as cc


def main_arcpy(input_list):

	

	arcpy.AddMessage("Checking the following folder...\n%s"%input_folder)

	# running the csv_checker module:
	cc.main(input_list)
	



if __name__ == '__main__':
	# input_folder is the path to the folder where you stored all your FMP csv files (not checking the subfolders)
	input_folder = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\CheckerToolAgain\csv_checker\script\test_data\t1'
	submission_year = 2022
	mu_no = '123'

	input_list = [input_folder,submission_year,mu_no]
	main_arcpy(input_list)