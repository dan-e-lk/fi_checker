### This script is for testing only!!
checker_version = '2.4b'

def test_all(parameters):
	import traceback
	print('importing arcpy...')
	from Modules.CheckAll import Check
	
	num_of_tests = len(parameters)
	fails = []

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
			fails.append(k)

	if len(fails) > 0:
		print('\nFailed to run the following tests:\n%s'%fails)

	num_of_success = num_of_tests - len(fails)
	print('\n\n%s out of %s ran successfully'%(num_of_success, num_of_tests))


if __name__ == '__main__':
	parameters = {
	'AR_NEW_GDB': 	['ar',	'Martel', 				2011, 	2017, 	r'C:\testers\AR_NEW_GDB\MU509_17AR_testers.gdb', 							'feature classes', 	'2017', 	50, 	checker_version, 	'test_Oct5'],
	'FMP_NEW_GDB_AE':['fmp','Dog_River_Matawin', 	2020, 	2020, 	r'C:\testers\FMP_NEW_GDB_AllError\mu999_2020.gdb', 							'feature classes', 	'2017', 	50, 	checker_version, 	'test_Oct5'],
	'FMP_NEW_GDB_BMI':['fmp','Gordon_Cosens', 		2020, 	2020, 	r'C:\testers\FMP_NEW_GDB_BMI_PCI\Gordon_Cosens_BMI_PCI.gdb', 				'feature classes', 	'2017', 	50, 	checker_version, 	'test_Oct5'],
	'FMP_NEW_GDB_noBMI':['fmp','Romeo_Malette',		2019, 	2019, 	r'C:\testers\FMP_NEW_GDB_Except_BMI_PCI\Romeo_DraftPlan2019_Shortened.gdb',	'feature classes', 	'2017', 	50, 	checker_version, 	'test_Oct5'],	
	'FMP_NEW_SHP':	['fmp','Hearst',				2019, 	2019, 	r'C:\testers\FMP_NEW_SHP\Hearst_DraftPlan_2019_shortened',					'shapefile', 	'2017', 	50, 	checker_version, 		'test_Oct5'],
	'AWS_NEW_COV':	['aws','Algoma',				2018, 	2009, 	r'C:\testers\AWS_NEW_COV\Algoma_AWS_2018',									'coverage', 	'2017', 	50, 	checker_version, 		'test_Oct5'],
	'AWS_NEW_GDB':	['aws','Hearst',				2018, 	2009, 	r'C:\testers\AWS_NEW_GDB\Hearst_AWS2018.gdb',								'feature classes', 	'2017', 	50, 	checker_version, 	'test_Oct5'],

	}



	test_all(parameters)