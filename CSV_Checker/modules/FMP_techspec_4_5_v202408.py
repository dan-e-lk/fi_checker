

filename_fieldname = {
	
	"SGRLIST": 				['SGR_CODE', 'SILVICULTURAL_SYSTEM', 'TARGET_FU', 'TARGET_YIELD', 'SITE_PREPARATION', 'REGENERATION', 'TENDING'],
	"PROJECTEDFOREST": 		['FOREST_UNIT', 'AGE_CLASS', 'TERM', 'AREA'],
	"PROJECTEDHARVESTAREA":	['FOREST_UNIT', 'TERM', 'AREA'],
	"PROJECTEDHARVESTVOLUME":['SPECIES', 'PRODUCT', 'TERM', 'VOLUME'],
	"PROJECTEDSTRUCTURE": 	['LANDSCAPE_GUIDE_INDICATOR', 'TERM', 'AREA'],
	"PROJECTEDSILVICULTURE":['FOREST_UNIT', 'TREATMENT', 'TERM', 'AREA'],
	"PROJECTEDWILDLIFE":	['WILDLIFE', 'TERM', 'AREA'],
	"HARVESTAREAS":			['HARVEST_CATEGORY', 'FOREST_UNIT', 'AGE_CLASS', 'AREA'],
	"HARVESTVOLUME":		['HARVEST_CATEGORY', 'VOLUME_TYPE', 'FOREST_UNIT', 'SPECIES', 'VOLUME'],
	"VOLUMESWOODUTILIZATION":['HARVEST_CATEGORY', 'UTILIZATION', 'VOLUME_TYPE', 'LICENSEE', 'MILL', 'PRODUCT', 'SPECIES', 'VOLUME'],
	"WOODSUPPLYMECHANISM":	['MILL', 'WOOD_SUPPLY_MECHANISM', 'PRODUCT', 'VOLUME'],
	"PLANNEDRENEWAL":		['DISTURBANCE_TYPE', 'ACTIVITY', 'TREATMENT'],
	"PLANNEDEXPENDITURES":	['ACCOUNT','ACTIVITY','EXPENDITURES'],
	"PLANNEDASSESSMENT":	['DISTURBANCE_TYPE', 'FOREST_UNIT', 'SGR_CODE', 'TARGET_FU', 'AREA']
}

############################      CODING SCHEMES     ###############################

cs_silvsys = ['CLEARCUT','SELECTION','SELTERWOOD']
cs_regen = ['CLAAG','NATURAL','HARP','PLANT','SEED','SEED SITE PREP','SCARIFICATION','SEED TREE','STRIP CUT']






############################   VALIDATION FUNCTIONS  ###############################

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
	""" Use this function whenever the validation says "the population must follow the correct coding scheme"
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
		return [error_or_warning, err_count, field, "Population of %s must follow the coding scheme: %s"%(field, coding_scheme), err_list]



if __name__ == '__main__':
	for k,v in filename_fieldname.items():
		print("\t%s"%k)
		new_v = [i.replace(' ','_') for i in v]
		print("%s"%new_v)