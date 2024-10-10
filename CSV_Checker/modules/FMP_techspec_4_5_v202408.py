

filename_fieldname = {
	
	"SGRLIST": 				['SGR CODE', 'SILVICULTURAL SYSTEM', 'TARGET FU', 'TARGET YIELD', 'SITE PREPARATION', 'REGENERATION', 'TENDING'],
	"PROJECTEDFOREST": 		['FOREST UNIT', 'AGE CLASS', 'TERM', 'AREA'],
	"PROJECTEDHARVESTAREA":	['FOREST UNIT', 'TERM', 'AREA'],
	"PROJECTEDHARVESTVOLUME":['SPECIES', 'PRODUCT', 'TERM', 'VOLUME'],
	"PROJECTEDSTRUCTURE": 	['LANDSCAPE GUIDE INDICATOR', 'TERM', 'AREA'],
	"PROJECTEDSILVICULTURE":['FOREST UNIT', 'TREATMENT', 'TERM', 'AREA'],
	"PROJECTEDWILDLIFE":	['WILDLIFE', 'TERM', 'AREA'],
	"HARVESTAREAS":			['HARVEST CATEGORY', 'FOREST UNIT', 'AGE CLASS', 'AREA'],
	"HARVESTVOLUME":		['HARVEST CATEGORY', 'VOLUME TYPE', 'FOREST UNIT', 'SPECIES', 'VOLUME'],
	"VOLUMESWOODUTILIZATION":['HARVEST CATEGORY', 'UTILIZATION', 'VOLUME TYPE', 'LICENSEE', 'MILL', 'PRODUCT', 'SPECIES', 'VOLUME'],
	"WOODSUPPLYMECHANISM":	['MILL', 'WOOD SUPPLY MECHANISM', 'PRODUCT', 'VOLUME'],
	"PLANNEDRENEWAL":		['DISTURBANCE TYPE', 'ACTIVITY', 'TREATMENT'],
	"PLANNEDEXPENDITURES":	['ACCOUNT','ACTIVITY','EXPENDITURES'],
	"PLANNEDASSESSMENT":	['DISTURBANCE TYPE', 'FOREST UNIT', 'SGR CODE', 'TARGET FU', 'AREA']
}

############################      CODING SCHEMES     ###############################

cs_silvsys = ['CLEARCUT','SELECTION','SELTERWOOD']
cs_regen = ['CLAAG','NATURAL','HARP','PLANT','SEED','SEED SITE PREP','SCARIFICATION','SEED TREE','STRIP CUT']
cs_siteprep = ['MECHANICAL','CHEMICAL AERIAL','CHEMICAL GROUND','PRESCRIBED BURN','NONE']
cs_tending = ['CHEMICAL AERIAL','CHEMICAL GROUND','MANUAL','MECHANICAL','PRESCRIBED BURN','IMPROVEMENT','PRE-COMMERCIAL THIN',
				'CULTIVATION','PRUNING','NONE']





############################   VALIDATION FUNCTIONS  ###############################

# "c" stands for "check".  c_year = check year function

def c_mandatory_population(file_in_memory, field, min_char_len = 1, error_or_warning = 'ERROR', count_special_char = False):
	""" Use this function whenever the validation says a certain field must be populated.
	loop through the file_in_memory (list of dictionary) and check if values under the input field is populated
	output will be None if there's no error.
	output example: ["ERROR", 5 (number of records flagged), 'SGR CODE' (fieldname), "SGR CODE must be populated", [3,5,6,8,9]]
	"""
	rec_no = 2 # assuming people open it with Excel - first data starts on row 2.
	err_list = []
	for record in file_in_memory:
		val = record[field].strip()
		# special characters shouldn't count (some field values may be something like '--' which doesn't count)
		if not count_special_char: val = ''.join(filter(str.isalnum,val))
		if len(val)<1:
			err_list.append(rec_no)
		rec_no += 1

	err_count = len(err_list)
	if err_count == 0:
		return None
	else:
		return [error_or_warning, err_count, field, "%s must be populated"%field, err_list]



def c_coding_scheme(file_in_memory, field, coding_scheme, error_or_warning = 'ERROR'):
	""" Use this function whenever the validation says "the population must follow the correct coding scheme" (and population is mandatory)
	output will be None if there's no error.
	output example: ["ERROR", 3 (number of records flagged), 'REGENERATION' (fieldname), "Population of REGENERATION must follow the coding scheme", [3,5]]	
	"""
	rec_no = 2 # assuming people open it with Excel - first data starts on row 2.
	err_list = []
	for record in file_in_memory:
		val = record[field].strip().upper()
		if val not in coding_scheme:
			err_list.append(rec_no)
		rec_no += 1

	err_count = len(err_list)
	if err_count == 0:
		return None
	else:
		return [error_or_warning, err_count, field, "Population of %s field must follow the coding scheme: %s"%(field, coding_scheme), err_list]


def c_age_class(file_in_memory, field, error_or_warning = 'ERROR'):
	""" Use this function whenever the validation says "the only acceptable values are the age class values in Appendix 3"
	output will be None if there's no error.
	output example: ["ERROR", 3 (number of records flagged), 'AGE CLASS' (fieldname), "the only acceptable values are the age class values in Appendix 3", [3,5]]	
	"""
	# load age class table
	import csv
	csvfile = open('age_class_table.csv')
	reader = csv.DictReader(csvfile)
	csv_table = [i for i in reader]
	ac5 = set([i['AC5'] for i in csv_table])
	ac10 = set([i['AC10'] for i in csv_table])
	ac20 = set([i['AC20'] for i in csv_table])

	# check the first few records first
	# need at least few records to start this checking process
	total_rec_no = len(file_in_memory)
	if total_rec_no < 10:
		return ['ERROR', 1, field, "There are not enough records to check %s field"%field, []]

	# find out whether this field value is using AC5, AC10 or AC20.
	ac_type = None
	for i in range(9):
		val = file_in_memory[i][field].strip().upper() # eg. '000-005'
		if val in ['251+','ALLAGED']:
			continue
		if val in ac20:
			ac_type = ac20
			break		
		elif val in ac10:
			ac_type = ac10
			break
		elif val in ac5:
			ac_type = ac5
			break
	if ac_type == None:
		return ['ERROR', 1, field, "Cannot determine whether the values are using AC5, AC10 or AC20 system.", []]

	# now we know which AC type the data is using, validate all the data.
	# the following code is very similar to the c_coding_scheme function
	rec_no = 2 # assuming people open it with Excel - first data starts on row 2.
	err_list = []
	for record in file_in_memory:
		val = record[field].strip().upper()
		if val not in ac_type:
			err_list.append(rec_no)
		rec_no += 1

	err_count = len(err_list)
	if err_count == 0:
		return None
	else:
		return [error_or_warning, err_count, field, "Population of %s field is mandatory and must follow the the Appendix 3 of FMP Tech Spec."%field, err_list]


def c_year(file_in_memory, field, error_or_warning = 'ERROR', minyear=2000, maxyear=2200):
	""" Use this to check year fields such as "TERM" field
	Good for validating "The format must be YYYY"
	"""
	rec_no = 2 # assuming people open it with Excel - first data starts on row 2.
	err_list = []
	for record in file_in_memory:
		val = record[field].strip().upper()
		if len(val) != 4:
			err_list.append(rec_no)
		else:
			try:
				year = int(val)
				if year < minyear or year > maxyear:
					err_list.append(rec_no)
			except ValueError:
				err_list.append(rec_no)
		rec_no += 1

	err_count = len(err_list)
	if err_count == 0:
		return None
	else:
		return [error_or_warning, err_count, field, "The format of %s field must be YYYY (eg. 2032)."%field, err_list]

def c_isnumeric(file_in_memory, field, error_or_warning = 'ERROR'): # this function allows zero as a valid value
	""" Use this function whenever the validation says "the value must be whole numbers and no decimal places"
	Negative numbers will also result in error.
	For now, leading zeros are allowed in this function, but I doubt that anyone would put leading zeros here anyways...
	"""
	rec_no = 2 # assuming people open it with Excel - first data starts on row 2.
	err_list = []
	for record in file_in_memory:
		val = record[field].strip()
		if not val.isnumeric():
			err_list.append(rec_no)
		rec_no += 1

	err_count = len(err_list)
	if err_count == 0:
		return None
	else:
		return [error_or_warning, err_count, field, "The value of %s field must be a whole number and have no decimal places."%field, err_list]









if __name__ == '__main__':
	# for k,v in filename_fieldname.items():
	# 	print("\t%s"%k)
	# 	new_v = [i.replace(' ','_') for i in v]
	# 	print("%s"%new_v)

	# c_age_class('a','a')
	pass


