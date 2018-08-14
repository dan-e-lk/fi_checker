### This script is for testing only!!
checker_version = '2.3.4'

def test_all(parameters):
	import traceback
	print('importing arcpy...')
	from Modules.CheckAll import Check
	for k,v in parameters.items():
		try:
			print('\n**********************   Running test %s   ************************\n'%k)
			class_check = Check(v[0],v[1],v[2],v[3],v[4], v[5], v[6], v[7], v[8], v[9])
			class_check.run()
			print('\n**************   Successfully completed test %s   *****************\n'%k)
		except:
			var = traceback.format_exc()
			print(var)
			print('\n!!!!!!!!   Failed to run test %s   !!!!!!!!!*\n'%k)



if __name__ == '__main__':
	parameters = {
	'FMP_NEW_COV': 	['fmp',	'Dog_River_Matawin', 	2019, 	2019, 	r'C:\testers\FMP_NEW_COV\Dog_River_Mat_DraftPlan_2019_no_inventories', 		'coverage', 		'2017', 	"Limit to 50 errors per error type", 	checker_version, 	'test'],
	'FMP_NEW_GDB_AE':['fmp','Dog_River_Matawin', 	2020, 	2020, 	r'C:\testers\FMP_NEW_GDB_AllError\mu999_2020.gdb', 							'feature classes', 	'2017', 	"Limit to 50 errors per error type", 	checker_version, 	'test'],
	'FMP_NEW_GDB_BMI':['fmp','Gordon_Cosens', 		2020, 	2020, 	r'C:\testers\FMP_NEW_GDB_BMI_PCI\Gordon_Cosens_BMI_PCI.gdb', 				'feature classes', 	'2017', 	"Limit to 50 errors per error type", 	checker_version, 	'test'],
	'FMP_NEW_GDB_noBMI':['fmp','Romeo_Malette',		2019, 	2019, 	r'C:\testers\FMP_NEW_GDB_Except_BMI_PCI\Romeo_DraftPlan2019_Shortened.gdb',	'feature classes', 	'2017', 	"Limit to 50 errors per error type", 	checker_version, 	'test'],	
	'FMP_NEW_SHP':	['fmp','Hearst',				2019, 	2019, 	r'C:\testers\FMP_NEW_SHP\Hearst_DraftPlan_2019_shortened',					'shapefile', 	'2017', 	"Limit to 50 errors per error type", 	checker_version, 	'test'],
	'AWS_NEW_COV':	['aws','Algoma',				2018, 	2009, 	r'C:\testers\AWS_NEW_COV\Algoma_AWS_2018',									'coverage', 	'2017', 	"Limit to 50 errors per error type", 	checker_version, 	'test'],
	'AWS_NEW_GDB':	['aws','Hearst',				2018, 	2009, 	r'C:\testers\AWS_NEW_GDB\Hearst_AWS2018.gdb',								'feature classes', 	'2017', 	"Limit to 50 errors per error type", 	checker_version, 	'test'],
	}



	test_all(parameters)