# this is the main script that runs csv check.

# I need to add a script that creates a log file as well as either print or ArcpyAddMessage as the script progresses

import os, shutil
import FMP_techspec_4_5_v202408 as techspec


def main(input_list):

	input_folder = input_list[0]
	submission_year = input_list[1]
	mu_no = input_list[2]

	# grabbing all the csv files, full-path and all caps
	csv_fullpath_list = grab_all_csv(input_folder)
	
	print("CSV file list:\n%s"%csv_fullpath_list)


	# no no, filter only those files that has the right format first!!
	# right format: 


	# filter only those files that contains the keyword <description> such as "SGRList"
	keyword_list = techspec.filename_fieldname.keys()
	missing_tab_list = []
	matching_tab_list = []
	for csv_fullpath in csv_fullpath_list:
		for keyword in keyword_list: # eg. keyword = SGRLIST
			if keyword in os.path.split(csv_fullpath)[1]:
				matching_tab_list.append(keyword)
				break












def grab_all_csv(input_folder):
	""" grabs and outputs all csv files.
		does not go into subfolder
	"""
	file_fullpath_list = []
	endswith_this = 'CSV'
	d = input_folder

	for file in os.listdir(d):
		if file.upper().endswith(endswith_this):
			fullpath = os.path.join(d.upper(),file.upper())
			file_fullpath_list.append(fullpath)
			# print(fullpath)

	return file_fullpath_list	




# testing
if __name__ == '__main__':
	d = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\CheckerToolAgain\csv_checker\script\test_data\t1'
	grab_all_csv(d)