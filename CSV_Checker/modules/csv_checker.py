# this is the main script that runs csv check.

# I need to add a script that creates a log file as well as either print or ArcpyAddMessage as the script progresses

import os, shutil, csv
import FMP_techspec_4_5_v202408 as techspec


def main(input_list):

	input_folder = input_list[0]
	submission_year = input_list[1]
	mu_no = input_list[2]

	# check if input mu_no is 3 digits OR give drop down in the GUI
	# check if submission_year is 4 digits OR give drop down in the GUI

	# grabbing all the csv files, full-path and all caps
	csv_fullpath_list = grab_all_csv(input_folder)
	# print("CSV file list:\n%s"%csv_fullpath_list)

	# looking for csv files with the right format: MU<MUNO>_<SUB_YEAR>_<INFO_PROD>_TBL_<DESC>.csv  eg. MU123_2022_FMPDP_TBL_SGRList.csv
	print("\nChecking file names...")
	check_filename_summary, fmp_file_list, duplicate_filetype_list = check_filename(csv_fullpath_list, submission_year, mu_no)
	# !!!! need to also add missing file types

	# checking fieldnames
	print("\nChecking field names...")
	check_fieldname_summary = {}	
	for file in fmp_file_list:
		desc = check_filename_summary[file][2] # eg. SGRLIST
		check_fieldname_summary[file] = check_fieldname(file, desc) # input is the fullpath of the csv file and the description (type) of the csv file
	print("\nFieldname Summary:")
	for k,v in check_fieldname_summary.items():
		print("%s\n%s\n"%(k,v)) # v = ["ERROR", "Why this is error",[correct_fields,missing_fields,extra_fields]]

	# checking values
	print("\nChecking all values...")
	check_value_sum, num_of_rec = check_value(check_fieldname_summary)

	# printing out the results
	print("\ncheck_value_sum:")
	for k,v in check_value_sum.items():
		print(k)
		for flags in v:
			print("\t%s"%flags)
		print("")


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

def check_filename(csv_fullpath_list, submission_year, mu_no):
	""" FMP Techspec 4.5.2 - Naming Convention CHECK
		which csv files are FMP tables? (and which files aren't)
		Do those files have the correct MUNO, SUB_YEAR and DESC?
		Are there more than one csv file of the same kind? That's no good.
		example input:
		csv_fullpath_list = ['T:\\TESTDATA\\T2\\MU123_2022_TBL_PROJECTEDFOREST.CSV', 'T:\\TESTDATA\\T2\\MU123_2022_TBL_PROJECTEDHARVESTAREA.CSV', 'T:\\TESTDATA\\T2\\MU123_2022_TBL_SGRLIST.CSV']
	"""
	# looking for csv files with the right format: MU<MUNO>_<SUB_YEAR>_<INFO_PROD>_TBL_<DESC>.csv  eg. MU123_2022_FMPDP_TBL_SGRList.csv
	naming_conv = "MU<MUNO>_<SUB_YEAR>_<INFO_PROD>_TBL_<DESC>.csv"
	check_filename_summary = {i:None for i in csv_fullpath_list} # this summary will tell you which files are either ERROR, WARNING, or PASS. eg. {"T:\TESTDATA\4507_MU123_2022_FMP_TBL_SGRLIST.CSV": ['PASS', 'SGRLIST'], ...}
	not_fmp_file_list = [] # fullpath - if the file has nothing to do with fmp tables
	fmp_file_list = [] # fullpath - fmp table with correct naming convention
	duplicate_filetype_list = [] # can't have two or more of the same kind (can't have more than one SGRList.csv) unless it has different info product
	duplicate_checker = []
	for csv_file in csv_fullpath_list:
		orig_filename_full = os.path.split(csv_file)[1]
		if 'MU' in orig_filename_full and 'TBL' in orig_filename_full:
			orig_filename = orig_filename_full[orig_filename_full.find('MU'):-4] # this gets rid of prefix and extension. eg. MU123_2022_FMPDP_TBL_SGRLIST
			# but really the file should start with the word MU
			if orig_filename_full.find('MU') != 0:
				check_filename_summary[csv_file] = ["WARNING", "Filename should begin with 'MU'."]
		else:
			not_fmp_file_list.append(csv_file)
			check_filename_summary[csv_file] = ["ERROR", "Filename does not follow the naming convention: %s"%naming_conv]
			continue #move on to the next file

		parts = orig_filename.split('_')
		if len(parts) < 5:
			not_fmp_file_list.append(csv_file)
			check_filename_summary[csv_file] = ["ERROR", "Filename does not follow the naming convention: %s"%naming_conv]
			continue #move on to the next file
		elif len(parts) > 5:
			check_filename_summary[csv_file] = ["WARNING", "Filename shouldn't have prefix or suffix. (Filename does not follow the naming convention)"]
		MUNO = parts[0][2:] # eg '123'
		SUB_YEAR = parts[1]
		INFO_PROD = parts[2]
		TBL = parts[3]
		DESC = parts[4]
		parts_list = [MUNO,SUB_YEAR,INFO_PROD,TBL,DESC]

		# checking each part of the filename
		if MUNO != mu_no:
			not_fmp_file_list.append(csv_file)
			check_filename_summary[csv_file] = ["ERROR", "Filename's MU number does not match with the input MU number"]
			continue
		if SUB_YEAR != submission_year:
			not_fmp_file_list.append(csv_file)
			check_filename_summary[csv_file] = ["ERROR", "Filename's submission year does not match with that of the input"]
			continue
		if INFO_PROD not in ['FMPDP','FMP','FMPDPC','FMPC','MD','FMPEX']:
			not_fmp_file_list.append(csv_file)
			check_filename_summary[csv_file] = ["ERROR", "Filename's info product must be 'FMPDP','FMP','FMPDPC','FMPC','MD', or 'FMPEX'"]
			continue
		if TBL != 'TBL':
			not_fmp_file_list.append(csv_file)
			check_filename_summary[csv_file] = ["ERROR", "Filename does not follow the naming convention (missing _TBL_): %s"%naming_conv]
			continue
		if DESC not in techspec.filename_fieldname.keys():
			not_fmp_file_list.append(csv_file)
			check_filename_summary[csv_file] = ["ERROR", "Filename's description (%s) is invalid."%DESC]
			continue
		if parts_list in duplicate_checker:
			duplicate_filetype_list.append(csv_file)
			# check_filename_summary[csv_file] = ["WARNING", "Cannot have multiple csv tables of the same type. %s already exists"%parts_list]

		# all other files pass
		fmp_file_list.append(csv_file)
		duplicate_checker.append(parts_list)
		if check_filename_summary[csv_file] == None:
			check_filename_summary[csv_file] = ["PASS", "The file type is %s"%DESC ,DESC]
		else: # cases for WARNING
			val = check_filename_summary[csv_file]
			val.append(DESC)
			check_filename_summary[csv_file] = val

	print("\n")
	for k,v in check_filename_summary.items():
		print("%s\n\t%s"%(k,v))

	# debugging only
	# print("not fmp: %s"%not_fmp_file_list)
	# print("fmp files: %s"%fmp_file_list)
	# print("duplicate files: %s"%duplicate_filetype_list)

	# This script still passes filenames with extra prefixes and suffixes separated by underscore.
	return [check_filename_summary, fmp_file_list, duplicate_filetype_list]

def check_fieldname(file, desc):
	filename = os.path.split(file)[1]
	print("\t%s"%filename)
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		row_counter = 0
		field_list = None # eg. ['forest unit', 'age class', 'year', 'area'], if csv file is empty this will remain None
		for row in reader:
			if row_counter > 0:
				break  # just looping through the first row
			else:
				field_list = list(row.keys())
			row_counter += 1
		print(field_list)

	# we have field list now. check it against the tech spec field list
	if field_list == None: # if the file is empty:
		return ['ERROR', "This is an empty csv file", None]

	field_list_set = set([i.upper().strip() for i in field_list]) # makeing them all cap and into a set
	techspec_fieldnames = set(techspec.filename_fieldname[desc])

	correct_fields = list(field_list_set & techspec_fieldnames) # union (common elements of both))
	missing_fields = list(techspec_fieldnames - field_list_set)
	extra_fields = list(field_list_set - techspec_fieldnames)
	summary = [correct_fields,missing_fields,extra_fields]

	if len(missing_fields) > 0:
		return ['ERROR', "Missing Fields: %s"%missing_fields, summary]
		# example output: ['ERROR', "Missing Fields: ['REGENERATION', 'TENDING']", [['TARGET FU', 'SILVICULTURAL SYSTEM', 'SGR CODE', 'SITE PREPARATION', 'TARGET YIELD'], ['REGENERATION', 'TENDING'], ['DANIELS COMMENTS FIELD']]]
	elif len(extra_fields) > 0:
		return ['WARNING', "Extra Fields: %s"%extra_fields, summary]
	else:
		return ['PASS', "", summary]

def check_value(fname_sum):
	"""
	Loops through the csv files then loop through each rows to check if the values are populated correctly.
	example of input fname_sum:
	{"T:\03_VALUES\4508_MU123_2022_FMP_TBL_PROJECTEDFOREST.CSV": ['PASS', '', [['AGE CLASS', 'TERM', 'FOREST UNIT', 'AREA'], [], []]]}
	"""
	# create a new dictionary that will summarize what we do in this function
	check_value_summary = {k:[] for k,v in fname_sum.items()}
	num_of_rec = {k:0 for k,v in fname_sum.items()}
	for k,v in fname_sum.items():
		# unpacking
		filename = k
		justname = os.path.split(k)[1] # eg. 4508_MU123_2022_FMP_TBL_PROJECTEDFOREST.CSV
		validity = v[0] # 'ERROR','WARNING', or 'PASS'
		field_summary = v[2]
		if field_summary != None: existing_fields = field_summary[0]

		# if there are no valid fields to check
		print("\tChecking values of %s"%justname)
		if field_summary is None or len(field_summary[0]) == 0:
			err = [["ERROR", None, "Fieldname Error", "There's not one valid field to check"]]
			check_value_summary[k] = err
			print("\t\t%s: %s. %s"%(err[0][0],err[0][2],err[0][3]))
			continue # move on to next file
		
		# find out what type of csv file this is
		DESC = None
		for description in techspec.filename_fieldname.keys():
			if description in justname:
				DESC = description
				continue
		if DESC == None: # this shouldn't happen
			err = [["ERROR", None, "Filename Error", "Can't identify what type of csv file this is."]]
			check_value_summary[k] = err
			print("\t\t%s: %s. %s"%(err[0][0],err[0][2],err[0][3]))
			continue # move on to next file			

		# save csv file in memory as a dictionary
		file_in_memory = []
		with open(filename) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				new_dict = {k.upper():v for k,v in row.items()}
				file_in_memory.append(new_dict)
		num_of_rec[k] = len(file_in_memory)
		print("\t\t%s records found"%len(file_in_memory))
		
		# print(file_in_memory) # for debug

		#####################       validation       #####################

		error_warning_list = [] # eg.[ ["ERROR", 5 (number of records flagged), 'SGR CODE' (fieldname), "SGR CODE must be populated", [3,5,6,8,9]], ...]
		
		if DESC == 'SGRLIST':
			# checking SGR CODE
			field = 'SGR CODE'
			if field in existing_fields:
				# Population of this column is mandatory
				flags = techspec.c_mandatory_population(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)
			# checking SILVICULTURAL SYSTEM
			field = 'SILVICULTURAL SYSTEM'
			if field in existing_fields:
				# Population of SILVICULTURAL SYSTEM must follow the coding scheme
				flags = techspec.c_coding_scheme(file_in_memory, field, techspec.cs_silvsys)
				if flags != None:
					error_warning_list.append(flags)
			# checking TARGET_FU
			field = 'TARGET FU'
			if field in existing_fields:
				# Population of this column is mandatory
				flags = techspec.c_mandatory_population(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)
				# the only acceptable values are those from PLANFU... we can't check this here because this varies from one FMU to another
			# checking TARGET_YIELD
			field = 'TARGET YIELD'
			if field in existing_fields:
				# Population of this column is mandatory
				flags = techspec.c_mandatory_population(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)
				# the only acceptable values are those from FMP... we can't check this here because this varies from one FMU to another	
			# checking REGENERATION
			field = 'REGENERATION'
			if field in existing_fields:
				# Population of REGENERATION must follow the coding scheme
				flags = techspec.c_coding_scheme(file_in_memory, field, techspec.cs_regen)
				if flags != None:
					error_warning_list.append(flags)
			# checking SITE_PREPARATION
			field = 'SITE PREPARATION'
			if field in existing_fields:
				# Population of SITE_PREPARATION must follow the coding scheme
				flags = techspec.c_coding_scheme(file_in_memory, field, techspec.cs_siteprep)
				if flags != None:
					error_warning_list.append(flags)
			# checking TENDING
			field = 'TENDING'
			if field in existing_fields:
				# Population of TENDING must follow the coding scheme
				flags = techspec.c_coding_scheme(file_in_memory, field, techspec.cs_tending)
				if flags != None:
					error_warning_list.append(flags)

		# PROJECTEDFOREST
		if DESC == 'PROJECTEDFOREST':
			# checking next field
			field = 'FOREST UNIT'
			if field in existing_fields:
				# Population of this column is mandatory
				flags = techspec.c_mandatory_population(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)
			# checking next field
			field = 'AGE CLASS'
			if field in existing_fields:
				# Population of this column is mandatory and must follow appendix 3 of FMP tech spec
				flags = techspec.c_age_class(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)
			# checking next field
			field = 'TERM'
			if field in existing_fields:
				# Population of this column is mandatory
				flags = techspec.c_mandatory_population(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)			
				# the formal must be YYYY
				flags = techspec.c_year(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)
			# checking next field
			field = 'AREA'
			if field in existing_fields:
				# Population of this column is mandatory
				flags = techspec.c_mandatory_population(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)
				# the format must be integer with no decimal places
				flags = techspec.c_isnumeric(file_in_memory, field)
				if flags != None:
					error_warning_list.append(flags)













		check_value_summary[k] = error_warning_list

	return [check_value_summary, num_of_rec]

		








# testing each function
if __name__ == '__main__':
	# d = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\CheckerToolAgain\csv_checker\script\test_data\t1'
	# grab_all_csv(d)
	
	csv_fullpath_list = ['T:\\TESTDATA\\T2\\MU123_2022_TBL_PROJECTEDFOREST.CSV', 'T:\\TESTDATA\\T2\\MU123_2022_TBL_PROJECTEDHARVESTAREA.CSV', 'T:\\TESTDATA\\T2\\MU123_2022_TBL_SGRLIST.CSV']
	check_filename(csv_fullpath_list)



