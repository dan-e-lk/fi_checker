#-------------------------------------------------------------------------------
# Name:         TechSpec_FMP.py
# Purpose:      This module checkes every validation statements in FMP Tech Spec 2017
#
# Author:       RIAU, Ministry of Natural Resources and Forestry
#
#
# Created:      JUL 31 2017
# Updates:      MAR 28 2018 - DAN - The script now checks BMI, PCI and OPI
#               May 30 2018 - DAN - Now the script looks for FID if it cant find OBJECTID to accomodate shp and coverage
#           Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#-------------------------------------------------------------------------------

###########################     VALIDATION UPDATES  ############################
##      Search the script using *UD for validation changes from origianl tech spec
##    *UD1:
##    Old:
##      DEVSTAGE attribute must be DEPHARV or DEPNAT if POLYTYPE = FOR and the stocking attributes equal 0.00 (OSTKG + USTKG + STKG = 0)
##    New:
##      DEVSTAGE attribute must be DEP* or NEW* if POLYTYPE = FOR and the stocking attributes equal 0.00 (OSTKG + USTKG + STKG = 0)
##
##    *UD2:
##    Old:
##        The value (UHT) must be at least 3 less than OHT.
##    New:
##        Where VERT is equal to TO, TU, MO or MU, the OHT - UHT must be >= 3 OR OAGE - UAGE must be >= 20.
##
########################   END OF VALIDATION UPDATES  ##########################

import arcpy
import os, sys
import Reference as R
import pprint

verbose = True

lyrInfo = {
# Lyr acronym            name                           mandatory fields                                            Data type   Tech Spec       Tech Spec URL

    "AOC":  ["Area of Concern",                         ["AOCID","AOCTYPE"],                                        'polygon',  '4.2.8',        R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=114')],

    "BMI":  ["Base Model Inventory",                    ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                       'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                       'OYRORG', 'OSPCOMP', 'OLEADSPC', 'OAGE', 'OHT', 'OCCLO',
                                                       'OSTKG', 'OSC', 'UYRORG', 'USPCOMP', 'ULEADSPC', 'UAGE',
                                                       'UHT', 'UCCLO', 'USTKG', 'USC', 'INCIDSPC', 'VERT', 'HORIZ',
                                                       'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'ACCESS2', 'MGMTCON1',
                                                       'MGMTCON2', 'MGMTCON3', 'YRORG', 'SPCOMP', 'LEADSPC',
                                                       'AGE', 'HT', 'CCLO', 'STKG', 'SC', 'MANAGED', 'SMZ',
                                                       'PLANFU', 'AU', 'AVAIL', 'SILVSYS', 'NEXTSTG', 'YIELD'],     'polygon',  '4.1.4',        R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=15')],

    "ERU":  ["Existing Road Use Management Strategies", ['ROADID','ROADCLAS','TRANS','ACYEAR','ACCESS','DECOM',
                                                        'INTENT','MAINTAIN','MONITOR','RESPONS','CONTROL1'],        'arc',      '4.2.12',       R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=132')],

    "FDP":  ["Forecast Depletions",                     ['FSOURCE','FYRDEP','FDEVSTAGE'],                           'polygon',  '4.1.8',        R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=98')],

    "IMP":  ["Tree Improvement",                        ['IMPROVE'],                                                'polygon',  '4.2.15',       R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=148')],

    "OPI":  ["Operational Planning Inventory",          ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                       'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                       'INCIDSPC', 'VERT', 'HORIZ',
                                                       'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'ACCESS2', 'MGMTCON1',
                                                       'MGMTCON2', 'MGMTCON3', 'YRORG', 'SPCOMP', 'LEADSPC',
                                                       'AGE', 'HT', 'CCLO', 'STKG', 'SC', 'MANAGED', 'SMZ',
                                                       'PLANFU', 'AU', 'AVAIL', 'SILVSYS', 'NEXTSTG', 'YIELD',
                                                        'OMZ', 'SGR'],                                              'polygon',  '4.1.4',        R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=15')],

    "ORB":  ["Operational Road Boundaries",             ['ORBID'],                                                  'polygon',  '4.2.11',       R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=129')],

    "PAG":  ["Planned Aggregate Extraction Areas",      ['AGAREAID'],                                               'polygon',  '4.2.14',       R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=146')],

    "PCI":  ["Planning Composite",                      ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                        'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                        'OYRORG', 'OSPCOMP', 'OLEADSPC', 'OAGE', 'OHT', 'OCCLO',
                                                        'OSTKG', 'OSC', 'UYRORG', 'USPCOMP', 'ULEADSPC', 'UAGE',
                                                        'UHT', 'UCCLO', 'USTKG', 'USC', 'INCIDSPC', 'VERT', 
                                                        'HORIZ', 'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'MGMTCON1'],      'polygon',  '4.1.4',        R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=15')],

    "PHR":  ["Planned Harvest",                         ['BLOCKID','SILVSYS','HARVCAT'],                            'polygon',  '4.2.7',        R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=109')],

    "PRC":  ["Planned Road Corridors",                  ['ROADID','ROADCLAS','TRANS','ACYEAR','ACCESS','DECOM',
                                                        'INTENT','MAINTAIN','MONITOR','CONTROL1','CONTROL2'],       'polygon',  '4.2.10',       R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=120')], # revisit this. there were a number of errors in the tech spec itself.

    "PRP":  ["Planned Residual Patches",                ['RESID'],                                                  'polygon',  '4.2.9',        R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=118')],

    "WXI":  ["Existing Road Water Crossing Inventory",  ['WATXID','WATXTYPE','RESPONS','ROADID'],                   'point',    '4.2.13',       R.findPDF('FIM_FMP_TechSpec_2017.pdf#page=142')],
        }


# vnull is used to check if an item is NULL or blank.
vnull = [None,'',' ']

def run(gdb, summarytbl, year, fmpStartYear):  ## eg. summarytbl = {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'MU110_17SAC10_', 'MU110_17SAC10_ID']], 'MU110_17SAC11':...}

    if verbose: print("%s\n%s\n%s\n%s"%(gdb, summarytbl, year, fmpStartYear))

    lyrList = summarytbl.keys()
    fieldValUpdate = dict(zip(lyrList,['' for i in lyrList]))  ## if we find a record-value-based mandatory field, field validation status should be updated.
    fieldValComUpdate = dict(zip(lyrList,[[] for i in lyrList])) ## if we find a record-value-based mandatory field, field validation comments should be updated.
    recordVal = dict(zip(lyrList,['' for i in lyrList]))  ## recordVal should be either Valid or Invalid for each layer.
    recordValCom = dict(zip(lyrList,[[] for i in lyrList]))  ## recordValCom should be in the form, "1 record(s) where AWS_YR = 2016".
    errorDetail = dict(zip(lyrList,[[] for i in lyrList])) ## this will be used to populate "Error Detail" section of the report.

    for lyr in summarytbl.keys(): # for each layer such as MU110_17SAC10...
        lyrAcro = summarytbl[lyr][0] ## eg. "AGP"
        criticalError = 0
        minorError = 0
        systemError = False
        # summarytbl[lry][3] is a list of existing mandatory fields and summarytbl[lry][4] is a list of existing other fields
        f = summarytbl[lyr][4] + summarytbl[lyr][3]  ## f is the list of all fields found in lyr. eg. ['FID', 'SHAPE','PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP', ...]
        
        # feature classes have ObjectID, shapefiles and coverages have FID. Search for ObjectID's index value in f, if not possible, search for FID's index value in f. else use whatever field comes first as the ID field.
        try:
            OBJECTID = f.index('OBJECTID')
        except:
            try:
                OBJECTID = f.index('FID')
            except:
                OBJECTID = 0

        cursor = arcpy.da.SearchCursor(lyr,f)
        recordCount = len(list(cursor))
        cursor.reset()
        recordValCom[lyr].append("Total number of records checked: " + str(recordCount))



#       ######### Going through each layer type. Starts with PCI BMI OPI FDP, then in alphabetical order ##########

        arcpy.AddMessage("  Checking each record in %s (%s records)..."%(lyr,recordCount))


        ##############################################################################
        #                                                                            #
        ########################  Checking PCI, OPI and BMI   ########################
        #                                                                            #
        ##############################################################################


        if lyrAcro in ["PCI","BMI","OPI"]:
            try: # need try and except block here for cases such as not having mandatory fields. 
            # POLYID
                errorList = ["Error on OBJECTID %s: The population of POLYID is mandatory."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of POLYID is mandatory."%len(errorList))

                polyIDList = [cursor[f.index('POLYID')] for row in cursor if cursor[f.index('POLYID')] not in vnull ]
                cursor.reset()
                numDuplicates = len(polyIDList) - len(set(polyIDList))
                if numDuplicates > 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The POLYID attribute must contain a unique value."%numDuplicates)

            # POLYTYPE
                errorList = ["Error on OBJECTID %s: The population of POLYTYPE is mandatory and must follow the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] not in ['WAT','DAL','GRS','ISL','UCL','BSH','RCK','TMS','OMS','FOR']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of POLYTYPE is mandatory and must follow the correct coding scheme."%len(errorList))

                ## "If POLYTYPE attribute does not equal FOR, then FORMOD,DEVSTAGE, OYRORG, OSPCOMP..." can be checked on other fields.

            # OWNER
                errorList = ["Error on OBJECTID %s: The population of OWNER is mandatory and must follow the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if str(cursor[f.index('OWNER')]) not in ['0','1','2','3','4','5','6','7','8','9']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of OWNER is mandatory and must follow the correct coding scheme."%len(errorList))

            # YRSOURCE
                errorList = ["Error on OBJECTID %s: The YRSOURCE must be populated with the correct format (YYYY)."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('YRSOURCE')] in vnull or cursor[f.index('YRSOURCE')] < 1000 or cursor[f.index('YRSOURCE')] > 9999 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The YRSOURCE must be populated with the correct format (YYYY)."%len(errorList))

                errorList = ["Error on OBJECTID %s: The YRSOURCE must be at least a year less than the plan period start year."%cursor[OBJECTID] for row in cursor
                                if int(cursor[f.index('YRSOURCE')] or 0) > fmpStartYear - 1]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The YRSOURCE must be at least a year less than the plan period start year."%len(errorList))

            # SOURCE
                errorList = ["Error on OBJECTID %s: The population of SOURCE must follow the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('SOURCE')] not in ['BASECOVR','DIGITALA','DIGITALP','ESTIMATE','FOC','FORECAST','FRICNVRT','INFRARED','MARKING','OCULARA','OCULARG','OPC','PHOTO','PHOTOLS','PHOTOSS','LOTFIXD','PLOTVAR','RADAR','REGENASS','SEMEXTEN','SEMINTEN','SPECTRAL','SUPINFO']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of SOURCE is mandatory and must follow the correct coding scheme."%len(errorList))

                if lyrAcro in ["PCI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: SOURCE must not have the value FORECAST in PCI or OPI."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('SOURCE')] == 'FORECAST']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SOURCE must not have the value 'FORECAST' in PCI or OPI."%len(errorList))

                errorList = ["Error on OBJECTID %s: SOURCE must not equal ESTIMATE if the DEVSTAGE is NAT or starts with EST."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('DEVSTAGE')] not in vnull
                                if cursor[f.index('DEVSTAGE')][:3] == 'EST' or cursor[f.index('DEVSTAGE')] == 'NAT'
                                if cursor[f.index('SOURCE')] == 'ESTIMATE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SOURCE must not equal ESTIMATE if the DEVSTAGE is NAT or starts with EST."%len(errorList))

            # FORMOD
                errorList = ["Error on OBJECTID %s: FORMOD must be null when POLYTYPE is not equal to FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('FORMOD')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FORMOD must be null when POLYTYPE is not equal to FOR."%len(errorList))

                errorList = ["Error on OBJECTID %s: FORMOD must not be blank or null, and must follow the correct coding scheme when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('FORMOD')] not in ['RP','MR','PF']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FORMOD must not be blank or null, and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

                if "SC" in f:
                    errorList = ["Warning on OBJECTID %s: FORMOD attribute should be PF when SC equals 4."%cursor[OBJECTID] for row in cursor
                                    if str(cursor[f.index('SC')]) == '4'
                                    if cursor[f.index('FORMOD')] != 'PF']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1                     
                        recordValCom[lyr].append("Warning on %s record(s): FORMOD attribute should be PF when SC equals 4."%len(errorList))

            # DEVSTAGE
                errorList = ["Error on OBJECTID %s: DEVSTAGE must be null when POLYTYPE is not equal to FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('DEVSTAGE')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEVSTAGE must be null when POLYTYPE is not equal to FOR."%len(errorList))

                errorList = ["Error on OBJECTID %s: The population of DEVSTAGE is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('DEVSTAGE')] not in ['DEPHARV', 'DEPNAT','LOWMGMT','LOWNAT','NEWPLANT','NEWSEED','NEWNAT','ESTPLANT','ESTSEED','ESTNAT','NAT','THINPRE','THINCOM','BLKSTRIP','SEEDTREE','FRSTPASS','PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT','THINCOM','IMPROVE','SELECT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of DEVSTAGE is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))


                optField = ['OSTKG','USTKG','STKG']
                matchingField = list(set(optField) & set(f))
                command = """errorList = ["Error on OBJECTID %s: DEVSTAGE attribute must be DEP* or NEW* if POLYTYPE = FOR and the stocking attributes equal 0.00 (OSTKG + USTKG + STKG = 0)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('DEVSTAGE')] not in ['DEPHARV','DEPNAT','NEWPLANT','NEWSEED','NEWNAT']
                                    if float(cursor[f.index('""" + matchingField[0] + """')] or 0)"""    # float(x or 0) will give 0.0 if x is None. *UD1: Added NEWPLANT, NEWSEED and NEWNAT on Dec 2017
                if len(matchingField) > 1:
                    for i in range(1,len(matchingField)):
                        command += """ + float(cursor[f.index('""" + matchingField[i] + """')] or 0)"""
                command += """ == 0]"""
                exec(command) ## executing the command built above...
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEVSTAGE attribute must be DEP* or NEW* if POLYTYPE = FOR and the stocking attributes equal 0.00 (OSTKG + USTKG + STKG = 0)."%len(errorList))

                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Warning on OBJECTID %s: DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if int(cursor[f.index('UCCLO')] or 0) + int(cursor[f.index('OCCLO')] or 0) < 25
                                    if cursor[f.index('DEVSTAGE')] not in ['LOWMGMT','LOWNAT','DEPHARV','DEPNAT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1                      # minor error!!!!
                        recordValCom[lyr].append("Warning on %s record(s): DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25."%len(errorList))

            # YRDEP
                errorList = ["Error on OBJECTID %s: YRDEP must equal zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('YRDEP')] <> 0] 
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must equal zero when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on OBJECTID %s: YRDEP must be at least a year less than the plan start year."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('YRDEP')] > fmpStartYear - 1 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must be at least a year less than the plan start year."%len(errorList))

                errorList = ["Warning on OBJECTID %s: YRDEP should be greater than or equal to 1900 where POLYTYPE = FOR (4.1.4 YRDEP)."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('YRDEP')] != None and cursor[f.index('YRDEP')] < 1900 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be greater than or equal to 1900 where POLYTYPE = FOR (4.1.4 YRDEP)."%len(errorList))

                errorList = ["Warning on OBJECTID %s: YRDEP should be greater than or equal to 1900 where DEPTYPE is not null (4.1.4 YRDEP)."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('DEPTYPE')] not in vnull
                                if cursor[f.index('YRDEP')] < 1900 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be greater than or equal to 1900 where DEPTYPE is not null (4.1.4 YRDEP)."%len(errorList))

            # DEPTYPE
                errorList = ["Error on OBJECTID %s: DEPTYPE must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('DEPTYPE')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEPTYPE must be null when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on OBJECTID %s: DEPTYPE must follow the correct coding scheme where YRDEP is not 0."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('YRDEP')] not in [0] + vnull
                                if cursor[f.index('DEPTYPE')] not in ['BLOWDOWN','DISEASE','DROUGHT','FIRE','FLOOD','HARVEST','ICE','INSECTS','SNOW','UNKNOWN']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEPTYPE must follow the correct coding scheme where YRDEP is not 0."%len(errorList))

                errorList = ["Warning on OBJECTID %s: DEPTYPE should not be UNKNOWN if DEVSTAGE starts with DEP, NEW or EST."%cursor[OBJECTID] for row in cursor
                                if str(cursor[f.index('DEVSTAGE')] or '')[:3] in ['DEP','NEW','EST']  # str(b or '') will give '' if b is None.
                                if cursor[f.index('DEPTYPE')] == 'UNKNOWN' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): DEPTYPE should not be UNKNOWN if DEVSTAGE starts with DEP, NEW or EST."%len(errorList))

                ## The following has been included in YRDEP validation: If the disturbance type is not null (DEPTYPE ? null) then disturbance year should be greater than or equal nineteen hundred (YRDEP >= 1900)

            # OYRORG (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OYRORG must equal zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OYRORG')] <> 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OYRORG must equal zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OYRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OYRORG')] in vnull or int(cursor[f.index('OYRORG')]) < 1600 or int(cursor[f.index('OYRORG')]) > fmpStartYear - 1 ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OYRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: OYRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OYRORG')] > cursor[f.index('YRSOURCE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OYRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%len(errorList))

            # OSPCOMP (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OSPCOMP must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OSPCOMP')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSPCOMP must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OSPCOMP must be populated when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSPCOMP')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSPCOMP must be populated when POLYTYPE is FOR."%len(errorList))

                    # code to check spcomp
                    fieldname = "OSPCOMP"
                    errorList = []
                    warningList = []
                    for row in cursor:
                        if cursor[f.index(fieldname)] not in vnull:
                            check = R.spcVal(cursor[f.index(fieldname)],fieldname)
                            if check is None: ## when no error found
                                pass
                            elif check[0] == "Error":
                                errorList.append("%s on OBJECTID %s: %s"%(check[0],cursor[OBJECTID],check[1]))
                            elif check[0] == "Warning":
                                warningList.append("%s on OBJECTID %s: %s"%(check[0],cursor[OBJECTID],check[1]))
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): %s value error. For more info, search for '%s' in the Error Detail section."%(len(errorList),fieldname,fieldname))
                    if len(warningList) > 0:
                        errorDetail[lyr].append(warningList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): %s value warning. For more info, search for '%s' in the Error Detail section."%(len(warningList),fieldname,fieldname))

            # OLEADSPC (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OLEADSPC must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OLEADSPC')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OLEADSPC must be populated when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OLEADSPC')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be populated when POLYTYPE = FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OLEADSPC must be a species listed in the OSPCOMP when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OLEADSPC')] not in vnull and cursor[f.index('OSPCOMP')] not in vnull
                                    if cursor[f.index('OLEADSPC')].upper() not in cursor[f.index('OSPCOMP')].upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be a species listed in the OSPCOMP when POLYTYPE = FOR."%len(errorList))

                    # this check works only if the spcomp is in descending order.
                    errorList = ["Error on OBJECTID %s: OLEADSPC must be the species with the greatest percent composition."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('OLEADSPC')] not in vnull
                                    if cursor[f.index('OSPCOMP')] not in vnull and len(cursor[f.index('OSPCOMP')]) > 3
                                    if cursor[f.index('OLEADSPC')].strip().upper() <> cursor[f.index('OSPCOMP')][:3].strip().upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be the species with the greatest percent composition."%len(errorList))

            # OAGE (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OAGE must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OAGE')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OAGE must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OAGE must be populated and follow the correct format when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if not isinstance(cursor[f.index('OAGE')],int) or cursor[f.index('OAGE')] < 0] ## testing if OAGE is always a positive integer or zero.
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OAGE must be populated and follow the correct format when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OAGE can be zero only when DEVSTAGE is DEPHARV or DEPNAT (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OAGE')] == 0
                                    if cursor[f.index('DEVSTAGE')] not in ['DEPHARV','DEPNAT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OAGE can be zero only when DEVSTAGE is DEPHARV or DEPNAT (when POLYTYPE = FOR)."%len(errorList))

            # OHT (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OHT must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OHT')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OHT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OHT')] < 0 or cursor[f.index('OHT')] > 40] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OHT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OHT')] <= 0
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] not in ['DEP','NEW','LOW']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%len(errorList))

            # OCCLO (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OCCLO must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OCCLO')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OCCLO must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OCCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OCCLO')] < 0 or cursor[f.index('OCCLO')] > 100] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OCCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%len(errorList))

            # OSTKG (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OSTKG must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OSTKG')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSTKG must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OSTKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSTKG')] < 0 or cursor[f.index('OSTKG')] > 4] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSTKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OSTKG must be greater than zero if the DEVSTAGE does not start with DEP or NEW (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSTKG')] != None # this has already been checked.
                                    if cursor[f.index('OSTKG')] <= 0
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] not in ['DEP','NEW']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSTKG must be greater than zero if the DEVSTAGE does not start with DEP or NEW (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: OSTKG should be greater than 0.4 for certain DEVSTAGE values (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSTKG')] != None # this has already been checked.
                                    if cursor[f.index('OSTKG')] < 0.4
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')] in ['NAT','ESTNAT','ESTPLANT','ESTSEED','IMPROVE','SELECT','SNGLTREE','THINCOM','FIRSTCUT','SEEDCUT','PREPCUT','FIRSTPASS','BLKSTRIP','THINPRE']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OSTKG should be greater than 0.4 for certain DEVSTAGE values (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: OSTKG and USTKG should be zero when DEVSTAGE starts with DEP."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] == 'DEP'
                                    if cursor[f.index('OSTKG')] != 0 or cursor[f.index('USTKG')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OSTKG and USTKG should be zero when DEVSTAGE starts with DEP."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: OSTKG should be less than 2.5."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('OSTKG')] > 2.5]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OSTKG should be less than 2.5."%len(errorList))

            # OSC (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: OSC must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OSC')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSC must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OSC must be between 0 and 4 when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSC')] < 0 or cursor[f.index('OSC')] > 4] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSC must be between 0 and 4 when POLYTYPE = FOR."%len(errorList))

            # UYRORG (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: UYRORG must equal zero when POLYTYPE is not FOR or if DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('UYRORG')] <> 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UYRORG must equal zero when POLYTYPE is not FOR or if DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: UYRORG must be greater than OYRORG, greater than 1800, but less than the plan start year when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UYRORG')] < 1800 or cursor[f.index('UYRORG')] < cursor[f.index('OYRORG')] or cursor[f.index('UYRORG')] >= fmpStartYear ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UYRORG must be greater than OYRORG, greater than 1800, but less than the plan start year when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: UYRORG should not be greater than YRSOURCE when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UYRORG')] > cursor[f.index('YRSOURCE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): UYRORG should not be greater than YRSOURCE when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))

            # USPCOMP (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: USPCOMP must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('USPCOMP')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USPCOMP must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: USPCOMP must be entered when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('USPCOMP')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USPCOMP must be entered when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))

                    # code to check spcomp
                    fieldname = "USPCOMP"
                    errorList = []
                    warningList = []
                    for row in cursor:
                        if cursor[f.index(fieldname)] not in vnull:
                            check = R.spcVal(cursor[f.index(fieldname)],fieldname)
                            if check is None: ## when no error found
                                pass
                            elif check[0] == "Error":
                                errorList.append("%s on OBJECTID %s: %s"%(check[0],cursor[OBJECTID],check[1]))
                            elif check[0] == "Warning":
                                warningList.append("%s on OBJECTID %s: %s"%(check[0],cursor[OBJECTID],check[1]))
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): %s value error. For more info, search for '%s' in the Error Detail section."%(len(errorList),fieldname,fieldname))
                    if len(warningList) > 0:
                        errorDetail[lyr].append(warningList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): %s value warning. For more info, search for '%s' in the Error Detail section."%(len(warningList),fieldname,fieldname))

            # ULEADSPC (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: ULEADSPC must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('ULEADSPC')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: ULEADSPC must be populated when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('ULEADSPC')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be populated when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on OBJECTID %s: ULEADSPC must be a species listed in the USPCOMP."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('ULEADSPC')] not in vnull and cursor[f.index('USPCOMP')] != None
                                    if cursor[f.index('ULEADSPC')].upper() not in cursor[f.index('USPCOMP')].upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be a species listed in the USPCOMP."%len(errorList))

                    # this check works only if the spcomp is in descending order.
                    errorList = ["Error on OBJECTID %s: ULEADSPC must be the species with the greatest percent composition."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('ULEADSPC')] not in vnull
                                    if cursor[f.index('USPCOMP')] not in vnull and len(cursor[f.index('USPCOMP')]) > 3
                                    if cursor[f.index('ULEADSPC')].strip().upper() <> cursor[f.index('USPCOMP')][:3].strip().upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be the species with the greatest percent composition."%len(errorList))

            # UAGE (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: UAGE must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('UAGE')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UAGE must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: UAGE must be populated and follow the correct format when POLYTYPE is FOR and when VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if not isinstance(cursor[f.index('UAGE')],int) or cursor[f.index('UAGE')] <= 0] ## testing if UAGE is always a positive integer.
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UAGE must be populated and follow the correct format when POLYTYPE is FOR and when VERT is TO, TU, MO or MU."%len(errorList))

            # UHT (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: UHT must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('UHT')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UHT must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: UHT must be greater than 0 when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UHT')] <= 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UHT must be greater than 0 when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on OBJECTID %s: UHT must be between 0 and 40 when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('UHT')] < 0 or cursor[f.index('UHT')] > 40]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UHT must be between 0 and 40 when POLYTYPE = FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: OHT minus UHT must be >= 3 OR OAGE minus UAGE must be >= 20, when VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('UHT')] != 0 and cursor[f.index('UAGE')] != 0
                                    if isinstance(cursor[f.index('UHT')],(int,float)) and isinstance(cursor[f.index('OHT')],(int,float)) and isinstance(cursor[f.index('OAGE')],(int,float)) and isinstance(cursor[f.index('UAGE')],(int,float))
                                    if (cursor[f.index('UHT')] > cursor[f.index('OHT')] - 3) and (cursor[f.index('UAGE')] > cursor[f.index('OAGE')] - 20)]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT minus UHT must be >= 3 OR OAGE minus UAGE must be >= 20, when VERT is TO, TU, MO or MU."%len(errorList))      # *UD2 update on Dec 2017

            # UCCLO (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: UCCLO must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('UCCLO')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UCCLO must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: UCCLO cannot be zero when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UCCLO')] == 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UCCLO cannot be zero when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on OBJECTID %s: UCCLO must be between 0 and 100 when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('UCCLO')] < 0 or cursor[f.index('UCCLO')] > 100] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UCCLO must be between 0 and 100 when POLYTYPE = FOR."%len(errorList))

            # USTKG (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: USTKG must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('USTKG')] != 0] # SQL version: (POLYTYPE <> 'FOR' OR DEVSTAGE in('DEPHARV','DEPNAT')) AND (USTKG <> 0 OR USTKG is Null)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USTKG must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: USTKG must be between 0 and 4.0 (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('USTKG')] < 0 or cursor[f.index('USTKG')] > 4] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USTKG must be between 0 and 4.0 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: USTKG should not be 0 when VERT is TO, TU, MO or MU."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('USTKG')] <= 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): USTKG should not be 0 when VERT is TO, TU, MO or MU."%len(errorList))

                    ## The following validation is being checked in the OSTKG section: "If DEVSTAGE attribute starts with DEP, then OSTKG + USTKG = 0"

                    errorList = ["Warning on OBJECTID %s: USTKG should be less than 2.5."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('USTKG')] > 2.5]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): USTKG should be less than 2.5."%len(errorList))

            # USC (PCI and BMI only)
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on OBJECTID %s: USC must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('USC')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USC must be zero when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on OBJECTID %s: USC must be between 0 and 4 when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('USC')] < 0 or cursor[f.index('USC')] > 4] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USC must be between 0 and 4 when POLYTYPE = FOR."%len(errorList))

            # INCIDSPC (applies to PCI BMI and OPI)
                errorList = ["Error on OBJECTID %s: INCIDSPC must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('INCIDSPC')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INCIDSPC must be null when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on OBJECTID %s: INCIDSPC must be populated when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('INCIDSPC')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INCIDSPC must be populated when POLYTYPE = FOR."%len(errorList))

                errorList = ["Error on OBJECTID %s: INCIDSPC must follow the correct species code (or NON) if populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('INCIDSPC')] not in vnull
                                if cursor[f.index('INCIDSPC')].upper() != 'NON'
                                if cursor[f.index('INCIDSPC')].upper() not in R.SpcListInterp + R.SpcListOther ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INCIDSPC must follow the correct species code (or NON) if populated."%len(errorList))

                if lyrAcro == 'PCI':
# possibility of value error
                    errorList = ["Warning on OBJECTID %s: INCIDSPC should not represent over 10 percent in OSPCOMP."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('INCIDSPC')] not in [None,'',' ','NON','Non'] and cursor[f.index('OSPCOMP')] != None  # if INCIDSPC is None, '' or ' ', then the next statement wouldn't work.
                                    if cursor[f.index('INCIDSPC')].upper() in cursor[f.index('OSPCOMP')].upper()
                                    if int(cursor[f.index('OSPCOMP')][cursor[f.index('OSPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+3:cursor[f.index('OSPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+6] > 10)] # int(sp[sp.find(incidspc)+3:sp.find(incidspc)+6])
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): INCIDSPC should not represent over 10 percent in OSPCOMP."%len(errorList))

                if lyrAcro in ["BMI", "OPI"]:
# possibility of value error
                    errorList = ["Warning on OBJECTID %s: INCIDSPC should not represent over 10 percent in SPCOMP."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('INCIDSPC')] not in [None,'',' ','NON','Non'] and cursor[f.index('SPCOMP')] != None  # if INCIDSPC is None, '' or ' ', then the next statement wouldn't work.
                                    if cursor[f.index('INCIDSPC')].upper() in cursor[f.index('SPCOMP')].upper()
                                    if int(cursor[f.index('SPCOMP')][cursor[f.index('SPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+3:cursor[f.index('SPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+6] > 10)]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): INCIDSPC should not represent over 10 percent in SPCOMP."%len(errorList))                                      

            # VERT
                errorList = ["Error on OBJECTID %s: VERT must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('VERT')] not in ['SI','SV','TO','TU','MO','MU','CX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): VERT must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

            # HORIZ
                errorList = ["Error on OBJECTID %s: HORIZ must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('HORIZ')] not in ['SS','SP','FP','MP','OC','OU']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HORIZ must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

            # PRI_ECO and SEC_ECO

                errorList = ["Error on OBJECTID %s: PRI_ECO must be populated when POLYTYPE is FOR or when SEC_ECO is not null."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR' or cursor[f.index('SEC_ECO')] not in vnull
                                if cursor[f.index('PRI_ECO')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PRI_ECO must be populated when POLYTYPE is FOR or when SEC_ECO is not null."%len(errorList))


                ## code to check PRI_ECO and SEC_ECO
                for fname in ["PRI_ECO", "SEC_ECO"]:
                    errorList = []
                    for row in cursor:
                        if cursor[f.index(fname)] not in vnull:
                            check = R.ecoVal(cursor[f.index(fname)],fname)
                            if check is None: ## when no error found
                                pass
                            else:
                                errorList.append("%s on OBJECTID %s: %s"%(check[0],cursor[OBJECTID],check[1]))

                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): %s value error. For more info, search for '%s' in the Error Detail section."%(len(errorList),fname,fname))

            # ACCESS1
                errorList = ["Error on OBJECTID %s: ACCESS1 must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('ACCESS1')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS1 must be null when POLYTYPE is not FOR."%len(errorList))


                errorList = ["Error on OBJECTID %s: ACCESS1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('ACCESS1')] not in ['GEO','LUD','NON','OWN','PRC','STO']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

            # ACCESS2
                if 'ACCESS2' in f:
                    errorList = ["Error on OBJECTID %s: ACCESS2 must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('ACCESS2')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS2 must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: ACCESS2 must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('ACCESS2')] not in vnull
                                    if cursor[f.index('ACCESS2')] not in ['GEO','LUD','NON','OWN','PRC','STO']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS2 must follow the correct coding scheme if populated."%len(errorList))

                    errorList = ["Error on OBJECTID %s: ACCESS1 must not be NON if ACCESS2 is not equal to NON."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('ACCESS2')] != 'NON'
                                    if cursor[f.index('ACCESS1')] == 'NON']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS1 must not be NON if ACCESS2 is not equal to NON."%len(errorList))

                    errorList = ["Error on OBJECTID %s: ACCESS1 must not be the same as ACCESS2 unless both are NON."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('ACCESS1')] in ['GEO','LUD','OWN','PRC','STO'] ## if ACCESS1 is populated with correct coding scheme except 'NON'.
                                    if cursor[f.index('ACCESS1')] == cursor[f.index('ACCESS2')]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS1 must not be the same as ACCESS2 unless both are NON."%len(errorList))

            # MGMTCON1
                try:
                    errorList = ["Error on OBJECTID %s: MGMTCON1, MGMTCON2 and MGMTCON3 must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('MGMTCON1')] and cursor[f.index('MGMTCON2')] and cursor[f.index('MGMTCON3')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1, MGMTCON2 and MGMTCON3 must be null when POLYTYPE is not FOR."%len(errorList))
                except:
                    # in the case where MGMTCON2 or MGMTCON3 field does not exist, the above try statement will fail
                    try:
                        errorList = ["Error on OBJECTID %s: MGMTCON1 and MGMTCON2 must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                        if cursor[f.index('POLYTYPE')] != 'FOR'
                                        if cursor[f.index('MGMTCON1')] and cursor[f.index('MGMTCON2')] not in vnull]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): MGMTCON1 and MGMTCON2 must be null when POLYTYPE is not FOR."%len(errorList))
                    except:
                        # in the case where MGMTCON2 field does not exist, the above try statement will fail
                        errorList = ["Error on OBJECTID %s: MGMTCON1 must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                        if cursor[f.index('POLYTYPE')] != 'FOR'
                                        if cursor[f.index('MGMTCON1')] not in vnull]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must be null when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on OBJECTID %s: MGMTCON1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('MGMTCON1')] not in ['COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

                try:
                    errorList = ["Error on OBJECTID %s: MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('ACCESS1')] == 'GEO' or cursor[f.index('ACCESS2')] == 'GEO'
                                    if cursor[f.index('MGMTCON1')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%len(errorList))
                except:
                    # in the case where ACCESS2 field does not exist, the above try statement will fail
                    errorList = ["Error on OBJECTID %s: MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('ACCESS1')] == 'GEO'
                                    if cursor[f.index('MGMTCON1')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%len(errorList))

                errorList = ["Error on OBJECTID %s: MGMTCON1 must not equal 'NONE' when FORMOD = 'PF'."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('FORMOD')] == 'PF'
                                if cursor[f.index('MGMTCON1')] == 'NONE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not equal 'NONE' when FORMOD = 'PF'."%len(errorList))

            # MGMTCON2, MGMTCON3
                if "MGMTCON2" in f:
                    errorList = ["Error on OBJECTID %s: MGMTCON1 must not be 'NONE' if MGMTCON2 is not 'NONE'."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON2')] != 'NONE'
                                    if cursor[f.index('MGMTCON1')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if MGMTCON2 is not 'NONE'."%len(errorList))

                    errorList = ["Error on OBJECTID %s: MGMTCON2 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON2')] not in [None,'',' ','COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON2 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%len(errorList))

                if "MGMTCON3" in f:
                    errorList = ["Error on OBJECTID %s: MGMTCON3 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON3')] not in [None,'',' ','COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON3 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%len(errorList))

                if "MGMTCON2" and "MGMTCON3" in f:
                    errorList = ["Error on OBJECTID %s: MGMTCON1 and MGMTCON2 must not be 'NONE' if MGMTCON3 is not 'NONE'."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON3')] != 'NONE'
                                    if cursor[f.index('MGMTCON1')] == 'NONE' or cursor[f.index('MGMTCON2')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 and MGMTCON2 must not be 'NONE' if MGMTCON3 is not 'NONE'."%len(errorList))

                try:
                    # using try and except here because most of the times, MGMTCON2 and 3 exists
                    errorList = ["Error on OBJECTID %s: MGMTCON1 must not have the same value as MGMTCON2 or MGMTCON3 unless they are all NONE."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON1')] != 'NONE'
                                    if cursor[f.index('MGMTCON1')] == cursor[f.index('MGMTCON2')] or cursor[f.index('MGMTCON1')] == cursor[f.index('MGMTCON3')]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not have the same value as MGMTCON2 or MGMTCON3 unless they are all NONE."%len(errorList))
                except:
                    try:
                        errorList = ["Error on OBJECTID %s: MGMTCON1 must not have the same value as MGMTCON2 unless they are both NONE."%cursor[OBJECTID] for row in cursor
                                        if cursor[f.index('POLYTYPE')] == 'FOR'
                                        if cursor[f.index('MGMTCON1')] != 'NONE'
                                        if cursor[f.index('MGMTCON1')] == cursor[f.index('MGMTCON2')]]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not have the same value as MGMTCON2 unless they are both NONE."%len(errorList))
                    except:
                        pass

                if 'SC' in f:
                    errorList = ["Warning on OBJECTID %s: MGMTCON1 should not equal 'NONE' when SC = 'PF'."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('SC')] == 'PF'
                                    if cursor[f.index('MGMTCON1')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): MGMTCON1 should not equal 'NONE' when SC = 'PF'."%len(errorList))

                if 'MGMTCON2' not in f and 'MGMTCON3' in f:
                   fieldValComUpdate[lyr].append("Missing MGMTCON2: If MGMTCON3 field exists, then MGMTCON2 field should also exist.")
                   fieldValUpdate[lyr] = 'Invalid'




            ################################     BMI and OPI ONLY     ##################################

            # YRORG (BMI and OPI only)
                if lyrAcro in ["BMI","OPI"]:
                    errorList = ["Error on OBJECTID %s: YRORG must equal zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('YRORG')] <> 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YRORG must equal zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: YRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YRORG')] in vnull or int(cursor[f.index('YRORG')]) < 1600 or int(cursor[f.index('YRORG')]) > fmpStartYear - 1 ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: YRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YRORG')] > cursor[f.index('YRSOURCE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): YRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%len(errorList))

                if lyrAcro in ["BMI"]:
                    errorList = ["Warning on OBJECTID %s: YRORG should be greater than or equal to OYRORG."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YRORG')] < cursor[f.index('OYRORG')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): YRORG should be greater than or equal to OYRORG."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: YRORG should be less than or equal to UYRORG if UYRORG is not 0."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('UYRORG')] > 0
                                    if cursor[f.index('YRORG')] > cursor[f.index('UYRORG')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): YRORG should be less than or equal to UYRORG if UYRORG is not 0."%len(errorList))

            # SPCOMP (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: SPCOMP must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SPCOMP')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SPCOMP must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: SPCOMP must be populated when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('SPCOMP')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SPCOMP must be populated when POLYTYPE is FOR."%len(errorList))

                    # code to check spcomp
                    fieldname = "SPCOMP"
                    errorList = []
                    warningList = []
                    for row in cursor:
                        if cursor[f.index(fieldname)] not in vnull:
                            check = R.spcVal(cursor[f.index(fieldname)],fieldname)
                            if check is None: ## when no error found
                                pass
                            elif check[0] == "Error":
                                errorList.append("%s on OBJECTID %s: %s"%(check[0],cursor[OBJECTID],check[1]))
                            elif check[0] == "Warning":
                                warningList.append("%s on OBJECTID %s: %s"%(check[0],cursor[OBJECTID],check[1]))
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): %s value error. For more info, search for '%s' in the Error Detail section."%(len(errorList),fieldname,fieldname))
                    if len(warningList) > 0:
                        errorDetail[lyr].append(warningList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): %s value warning. For more info, search for '%s' in the Error Detail section."%(len(warningList),fieldname,fieldname))

            # LEADSPC (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: LEADSPC must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('LEADSPC')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: LEADSPC must be populated when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('LEADSPC')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be populated when POLYTYPE = FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: LEADSPC must be species listed in the SPCOMP when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('LEADSPC')] not in vnull and cursor[f.index('SPCOMP')] not in vnull
                                    if cursor[f.index('LEADSPC')].upper() not in cursor[f.index('SPCOMP')].upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be species listed in the SPCOMP when POLYTYPE = FOR."%len(errorList))

                    # this check works only if the spcomp is in descending order.
                    errorList = ["Error on OBJECTID %s: LEADSPC must be the species with the greatest percent composition."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('LEADSPC')] not in vnull
                                    if cursor[f.index('SPCOMP')] not in vnull and cursor[f.index('LEADSPC')] not in vnull
                                    if cursor[f.index('LEADSPC')].strip().upper() <> cursor[f.index('SPCOMP')][:3].strip().upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be the species with the greatest percent composition."%len(errorList))

            # AGE (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: AGE must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('AGE')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: AGE must be populated and follow the correct format when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if not isinstance(cursor[f.index('AGE')],int) or cursor[f.index('AGE')] < 0] ## testing if AGE is always a positive integer or zero.
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE must be populated and follow the correct format when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: AGE can be zero only when DEVSTAGE is DEPHARV or DEPNAT (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AGE')] == 0
                                    if cursor[f.index('DEVSTAGE')] not in ['DEPHARV','DEPNAT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE can be zero only when DEVSTAGE is DEPHARV or DEPNAT (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Error on OBJECTID %s: AGE must be equal to the plan start year minus the YRORG."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AGE')] > 0 and cursor[f.index('YRORG')] > 0
                                    if fmpStartYear - cursor[f.index('YRORG')] != cursor[f.index('AGE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE must be equal to the plan start year minus the YRORG."%len(errorList))

            # HT (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: HT must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('HT')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: HT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('HT')] < 0 or cursor[f.index('HT')] > 40] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Error on OBJECTID %s: HT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('HT')] <= 0
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] not in ['DEP','NEW','LOW']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%len(errorList))

                    # only applied to BMI
                    if lyrAcro == 'BMI':
                        errorList = ["Warning on OBJECTID %s: HT should be greater than or equal to UHT and less than or equal to OHT."%cursor[OBJECTID] for row in cursor
                                        if cursor[f.index('POLYTYPE')] == 'FOR'
                                        if cursor[f.index('HT')] >= 0 and cursor[f.index('OHT')] >= 0 and cursor[f.index('UHT')] >= 0
                                        if cursor[f.index('HT')] < cursor[f.index('UHT')] or cursor[f.index('HT')] > cursor[f.index('OHT')] ]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            minorError += 1
                            recordValCom[lyr].append("Warning on %s record(s): HT should be greater than or equal to UHT and less than or equal to OHT."%len(errorList))

            # CCLO (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: CCLO must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('CCLO')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CCLO must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: CCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('CCLO')] < 0 or cursor[f.index('CCLO')] > 100] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%len(errorList))

            # STKG (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: STKG must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('STKG')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be zero when POLYTYPE is not FOR."%len(errorList))


                    errorList = ["Error on OBJECTID %s: STKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('STKG')] < 0 or cursor[f.index('STKG')] > 4] # surprisingly this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%len(errorList))


                    errorList = ["Error on OBJECTID %s: STKG must be greater than zero if the DEVSTAGE starts with NAT or EST (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('STKG')] <= 0
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] in ['NAT','EST']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be greater than zero if the DEVSTAGE starts with NAT or EST (when POLYTYPE = FOR)."%len(errorList))


                    errorList = ["Warning on OBJECTID %s: STKG should be greater than 0.4 if DEVSTAGE is NAT or starts with EST (when POLYTYPE = FOR)."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('STKG')] < 0.4
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] in ['NAT','EST']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): STKG should be greater than 0.4 if DEVSTAGE is NAT or starts with EST (when POLYTYPE = FOR)."%len(errorList))


                    errorList = ["Warning on OBJECTID %s: STKG should be zero when DEVSTAGE starts with DEP."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] == 'DEP'
                                    if cursor[f.index('STKG')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): STKG should be zero when DEVSTAGE starts with DEP."%len(errorList))


                    errorList = ["Warning on OBJECTID %s: STKG should be less than 2.5."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('STKG')] > 2.5]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): STKG should be less than 2.5."%len(errorList))

            # SC (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: SC must be zero when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SC')] != 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SC must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: SC must be between 0 and 4 when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('SC')] < 0 or cursor[f.index('SC')] > 4] # this will also catch nulls and empty spaces
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SC must be between 0 and 4 when POLYTYPE = FOR."%len(errorList))

            # MANAGED (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: MANAGED must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('MANAGED')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MANAGED must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: MANAGED must be M or U when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MANAGED')] not in ['M','U']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MANAGED must be M or U when POLYTYPE = FOR."%len(errorList))

            # SMZ (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: SMZ must be populated."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('SMZ')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SMZ must be populated."%len(errorList))

            # PLANFU (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: PLANFU must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('PLANFU')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PLANFU must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: PLANFU must be populated when POLYTYPE = FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('PLANFU')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PLANFU must be populated when POLYTYPE = FOR."%len(errorList))

            # AU (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: AU must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('AU')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AU must be null when POLYTYPE is not FOR."%len(errorList))

            # AVAIL (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: AVAIL must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('AVAIL')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AVAIL must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: AVAIL must be A or U when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AVAIL')] not in ['A','U']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AVAIL must be A or U when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: AVAIL must be U when MANAGED = U."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MANAGED')] == 'U'
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AVAIL must be U when MANAGED = U."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: AVAIL should be U when FORMOD = PF and OWNER = 1."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if str(cursor[f.index('OWNER')]) == '1'
                                    if cursor[f.index('FORMOD')] == 'PF'
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): AVAIL should be U when FORMOD = PF and OWNER = 1."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: AVAIL should be U when SC = 4 and OWNER = 1."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if str(cursor[f.index('OWNER')]) == '1'
                                    if str(cursor[f.index('SC')]) == '4'
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): AVAIL should be U when SC = 4 and OWNER = 1."%len(errorList))

                    errorList = ["Warning on OBJECTID %s: AVAIL should be U when ACCESS1 is GEO, LUD, OWN, PRC or STO."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if str(cursor[f.index('OWNER')]) == '1'
                                    if cursor[f.index('ACCESS1')] in ['GEO','LUD','OWN','PRC','STO']
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): AVAIL should be U when ACCESS1 is GEO, LUD, OWN, PRC or STO."%len(errorList))

            # SILVSYS (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: SILVSYS must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SILVSYS')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SILVSYS must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: SILVSYS must be CC, SE or SH when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('SILVSYS')] not in ['CC','SE','SH']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SILVSYS must be CC, SE or SH when POLYTYPE is FOR."%len(errorList))

            # NEXTSTG (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: NEXTSTG must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('NEXTSTG')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): NEXTSTG must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: NEXTSTG must follow the coding scheme when POLYTYPE is FOR and AVAIL = A."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AVAIL')] == 'A'
                                    if cursor[f.index('NEXTSTG')] not in ['THINPRE','THINCOM','CONVENT','BLKSTRIP','SEEDTREE','SCNDPASS','PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT','IMPROVE','SELECT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): NEXTSTG must follow the coding scheme when POLYTYPE is FOR and AVAIL = A."%len(errorList))

            # YIELD (BMI and OPI only)
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on OBJECTID %s: YIELD must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('YIELD')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YIELD must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: YIELD must be populated when POLYTYPE is FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YIELD')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YIELD must be populated when POLYTYPE is FOR."%len(errorList))


            ################################     OPI ONLY     ##################################

            # OMZ (OPI only)
                # There's nothing to validate.

            # SGR (OPI only)
                if lyrAcro == "OPI":
                    errorList = ["Error on OBJECTID %s: SGR must be null when POLYTYPE is not FOR."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SGR')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SGR must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on OBJECTID %s: SGR must not be null when POLYTYPE is FOR, AVAIL = A, and AGE >= 30."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AVAIL')] == 'A' 
                                    if int(cursor[f.index('AGE')] or 0) >= 30 # because a blank string is greater than any number in python world.
                                    if cursor[f.index('SGR')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SGR must not be null when POLYTYPE is FOR, AVAIL = A, and AGE >= 30."%len(errorList))


            # that's all for BMI, PCI and OPI!!!!!

            except ValueError: # This try statement begins way up - "if lyrAcro in ["PCI","BMI","OPI"]:""
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1




        ########################         Checking FDP        ########################

        if lyrAcro == "FDP":
            try: # need try and except block here for cases such as not having mandatory fields.

            # FSOURCE
                errorList = ["Error on OBJECTID %s: FSOURCE must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('FSOURCE')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FSOURCE must be populated."%len(errorList))
                # Not checking for valid coding scheme because the tech spec says FSOURCE attribute may be populated with other codes when it's being used for natural disturbances.

            # FYRDEP
                errorList = ["Error on OBJECTID %s: FYRDEP must be populated and zero is not a valid code."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('FYRDEP')] in [0, None, '',' ']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FYRDEP must be populated and zero is not a valid code."%len(errorList))

                errorList = ["Warning on OBJECTID %s: FYRDEP should not be less than plan start year minus 4."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('FYRDEP')] not in [0, None, '',' ']
                                if cursor[f.index('FYRDEP')] < fmpStartYear - 4]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): FYRDEP should not be less than plan start year minus 4."%len(errorList))

            # FDEVSTAGE
                errorList = ["Error on OBJECTID %s: FDEVSTAGE must be populated with the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('FDEVSTAGE')] not in ['DEPHARV', 'DEPNAT','LOWMGMT','LOWNAT','NEWPLANT','NEWSEED','NEWNAT','ESTPLANT','ESTSEED','ESTNAT','NAT','THINPRE','THINCOM','BLKSTRIP','SEEDTREE','FRSTPASS','PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT','THINCOM','IMPROVE','SELECT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FDEVSTAGE must be populated with the correct coding scheme."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking AOC        ########################

        if lyrAcro == "AOC":
            try: # need try and except block here for cases such as not having mandatory fields.

            # AOCID
                errorList = ["Error on OBJECTID %s: AOCID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('AOCID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AOCID must be populated."%len(errorList))

            # AOCTYPE
                errorList = ["Error on OBJECTID %s: AOCTYPE must be populated with M or R."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('AOCTYPE')] not in ['M','R']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AOCTYPE must be populated with M or R."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking ERU        ########################

        if lyrAcro == "ERU":
            try: # need try and except block here for cases such as not having mandatory fields.

            # ROADID
                errorList = ["Error on OBJECTID %s: ROADID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))

            # ROADCLAS
                errorList = ["Error on OBJECTID %s: ROADCLAS must be populated with P, B or O."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ROADCLAS')] not in ['P','B','O']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated with P, B or O."%len(errorList))

            # TRANS
                errorList = ["Error on OBJECTID %s: TRANS, if populated, must be greater than or equal to the plan start year."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('TRANS')] not in [0, None, '', ' ']
                                if cursor[f.index('TRANS')] < fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS, if populated, must be greater than or equal to the plan start year."%len(errorList))

                # The following is a validation for INTENT: "If TRANS value does not equal zero (TRANS is not 0) then INTENT must be populated"

                errorList = ["Warning on OBJECTID %s: TRANS, if populated, should not be greater than plan start year plus 20."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('TRANS')] not in vnull
                                if cursor[f.index('TRANS')] > fmpStartYear + 20]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): TRANS, if populated, should not be greater than plan start year plus 20."%len(errorList))

            # ACYEAR
                errorList = ["Error on OBJECTID %s: ACYEAR, if populated, must be greater than or equal to the plan start year when ACCESS is not EXISTING or REMOVE."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACCESS')] not in ['EXISTING','REMOVE']
                                if cursor[f.index('ACYEAR')] < fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACYEAR, if populated, must be greater than or equal to the plan start year when ACCESS is not EXISTING or REMOVE."%len(errorList))

                # Below is checking ACCESS...
                errorList = ["Error on OBJECTID %s: ACCESS must not be null if ACYEAR is populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACCESS')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must not be null if ACYEAR is populated."%len(errorList))

            # ACCESS
                errorList = ["Error on OBJECTID %s: ACCESS must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACCESS')] not in vnull + ['APPLY','REMOVE','ADD','EXISTING','BOTH','ADDREMOVE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must follow the correct coding scheme if populated."%len(errorList))

                # this is checking CONTROL1
                errorList = ["Error on OBJECTID %s: CONTROL1 must not be null if ACCESS = APPLY, ADD, BOTH OR ADDREMOVE."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACCESS')] in ['APPLY','ADD','BOTH','ADDREMOVE']
                                if cursor[f.index('CONTROL1')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must not be null if ACCESS = APPLY, ADD, BOTH OR ADDREMOVE."%len(errorList))

                # this is checking CONTROL1
                errorList = ["Warning on OBJECTID %s: CONTROL1 should be null if ACCESS = REMOVE."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACCESS')] == 'REMOVE'
                                if cursor[f.index('CONTROL1')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): CONTROL1 should be null if ACCESS = REMOVE."%len(errorList))

                # this is checking CONTROL2
                if "CONTROL2" in f:
                    errorList = ["Warning on OBJECTID %s: CONTROL2 should be null if ACCESS = REMOVE."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('ACCESS')] == 'REMOVE'
                                    if cursor[f.index('CONTROL2')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): CONTROL2 should be null if ACCESS = REMOVE."%len(errorList))

            # DECOM, MAINTAIN, MONITOR, ACCESS
                errorList = ["Error on OBJECTID %s: At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('DECOM')] in vnull
                                if cursor[f.index('MAINTAIN')] != 'Y'
                                if cursor[f.index('MONITOR')] != 'Y'
                                if cursor[f.index('ACCESS')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%len(errorList))

            # DECOM
                errorList = ["Error on OBJECTID %s: DECOM must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('DECOM')] not in vnull + ['BERM','SCAR','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DECOM must follow the correct coding scheme if populated."%len(errorList))

            # INTENT
                errorList = ["Error on OBJECTID %s: INTENT must be populated if TRANS is not 0."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('TRANS')] != 0
                                if cursor[f.index('INTENT')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INTENT must be populated if TRANS is not 0."%len(errorList))

            # MAINTAIN
                errorList = ["Error on OBJECTID %s: MAINTAIN must be populated with Y or N."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('MAINTAIN')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated with Y or N."%len(errorList))

            # MONITOR
                errorList = ["Error on OBJECTID %s: MONITOR must be populated with Y or N."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('MONITOR')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated with Y or N."%len(errorList))

            # RESPONS
                errorList = ["Error on OBJECTID %s: RESPONS must be populated with the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('RESPONS')] not in ['SFL','MNR','OTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): RESPONS must be populated with the correct coding scheme."%len(errorList))

                respons_sfl_list = ["" for row in cursor if cursor[f.index('RESPONS')] == "SFL"]
                cursor.reset()
                if len(respons_sfl_list) == 0:
                    minorError += 1
                    recordValCom[lyr].append("Warning: At least one record should have RESPONS = SFL (except for Crown managed units).")                

            # CONTROL1 and 2
                errorList = ["Error on OBJECTID %s: CONTROL1 must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if populated."%len(errorList))

                if "CONTROL2" in f:
                    errorList = ["Error on OBJECTID %s: CONTROL2 must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking ORB        ########################

        if lyrAcro == "ORB":
            try:

            # ORBID
                errorList = ["Error on OBJECTID %s: ORBID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ORBID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ORBID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking IMP        ########################

        if lyrAcro == "IMP":
            try:

            # IMPROVE
                errorList = ["Error on OBJECTID %s: IMPROVE must be populated with Y or N."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('IMPROVE')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): IMPROVE must be populated with Y or N."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking PAG        ########################

        if lyrAcro == "PAG":
            try:

            # AGAREAID
                errorList = ["Error on OBJECTID %s: AGAREAID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('AGAREAID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AGAREAID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking PHR        ########################

        if lyrAcro == "PHR":
            try:

            # BLOCKID
                errorList = ["Error on OBJECTID %s: BLOCKID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('BLOCKID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): BLOCKID must be populated."%len(errorList))

            # SILVSYS
                errorList = ["Error on OBJECTID %s: SILVSYS must be populated with CC, SE or SH."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('SILVSYS')] not in ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated with CC, SE or SH."%len(errorList))

                errorList = ["Error on OBJECTID %s: SILVSYS must be CC if HARVCAT = SCNDPASS."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('HARVCAT')] == 'SCNDPASS'
                                if cursor[f.index('SILVSYS')] != 'CC']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be CC if HARVCAT = SCNDPASS."%len(errorList))

            # HARVCAT
                errorList = ["Error on OBJECTID %s: HARVCAT must be populated with the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('HARVCAT')] not in ['BRIDGING','CONTNGNT','REGULAR','SALVAGE','REDIRECT','ACCELER','SCNDPASS']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVCAT must be populated with the correct coding scheme."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking PRC        ########################

        if lyrAcro == "PRC":
            try: # need try and except block here for cases such as not having mandatory fields.

            # ROADID
                errorList = ["Error on OBJECTID %s: ROADID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))

            # ROADCLAS
                errorList = ["Error on OBJECTID %s: ROADCLAS must be populated with P or B."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ROADCLAS')] not in ['P','B']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated with P or B."%len(errorList))

            # TRANS
                errorList = ["Error on OBJECTID %s: TRANS, if populated, must be greater than or equal to the plan start year."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('TRANS')] not in [0, None, '', ' ']
                                if cursor[f.index('TRANS')] < fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS, if populated, must be greater than or equal to the plan start year."%len(errorList))

                # The following is a validation for INTENT: "If TRANS value does not equal zero (TRANS is not 0) then INTENT must be populated"

            # ACYEAR
                errorList = ["Error on OBJECTID %s: ACYEAR, if populated, must be between plan start year and plan end year."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACYEAR')] < fmpStartYear or cursor[f.index('ACYEAR')] > fmpStartYear + 10]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACYEAR, if populated, must be between plan start year and plan end year."%len(errorList))

                # Below is checking ACCESS...
                errorList = ["Error on OBJECTID %s: ACCESS must be APPLY, REMOVE or BOTH if ACYEAR is populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACCESS')] not in ['APPLY','REMOVE','BOTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must be APPLY, REMOVE or BOTH if ACYEAR is populated."%len(errorList))

            # ACCESS
                errorList = ["Error on OBJECTID %s: ACCESS must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ACCESS')] not in vnull + ['APPLY','REMOVE','BOTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must follow the correct coding scheme if populated."%len(errorList))


                # Ignoring the following validations due to validation conflicts:
                # # this is checking CONTROL1
                # errorList = ["Warning on OBJECTID %s: CONTROL1 should be null if ACCESS = REMOVE."%cursor[OBJECTID] for row in cursor
                #                 if cursor[f.index('ACCESS')] == 'REMOVE'
                #                 if cursor[f.index('CONTROL1')] not in vnull]
                # cursor.reset()
                # if len(errorList) > 0:
                #     errorDetail[lyr].append(errorList)
                #     minorError += 1
                #     recordValCom[lyr].append("Warning on %s record(s): CONTROL1 should be null if ACCESS = REMOVE."%len(errorList))

                # # this is checking CONTROL2
                # if "CONTROL2" in f:
                #     errorList = ["Warning on OBJECTID %s: CONTROL2 should be null if ACCESS = REMOVE."%cursor[OBJECTID] for row in cursor
                #                     if cursor[f.index('ACCESS')] == 'REMOVE'
                #                     if cursor[f.index('CONTROL2')] not in vnull]
                #     cursor.reset()
                #     if len(errorList) > 0:
                #         errorDetail[lyr].append(errorList)
                #         minorError += 1
                #         recordValCom[lyr].append("Warning on %s record(s): CONTROL2 should be null if ACCESS = REMOVE."%len(errorList))

            # DECOM, MAINTAIN, MONITOR, ACCESS
                errorList = ["Error on OBJECTID %s: At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('DECOM')] in vnull
                                if cursor[f.index('MAINTAIN')] != 'Y'
                                if cursor[f.index('MONITOR')] != 'Y'
                                if cursor[f.index('ACCESS')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%len(errorList))

                # Not checking the following validation statement because CONSTRCT field does not exist:
                #   At a minimum, one of Construction, Decommissioning, Maintenance, Monitoring or Access Control must occur for each record (CONSTRCT = Y or DECOM IS NOT NULL or MAINTAIN = Y or MONITOR = Y or [ACCESS = APPLY or ACCESS = REMOVE OR ACCESS = BOTH])

            # DECOM
                errorList = ["Error on OBJECTID %s: DECOM must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('DECOM')] not in vnull + ['BERM','SCAR','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DECOM must follow the correct coding scheme if populated."%len(errorList))

            # INTENT
                errorList = ["Error on OBJECTID %s: INTENT must be populated if TRANS is populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('TRANS')] not in [0, None]
                                if cursor[f.index('INTENT')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INTENT must be populated if TRANS is populated."%len(errorList))

            # MAINTAIN
                errorList = ["Error on OBJECTID %s: MAINTAIN must be populated with Y or N."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('MAINTAIN')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated with Y or N."%len(errorList))

            # MONITOR
                errorList = ["Error on OBJECTID %s: MONITOR must be populated with Y or N."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('MONITOR')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated with Y or N."%len(errorList))
            

            # CONTROL1 and 2
                errorList = ["Error on OBJECTID %s: CONTROL1 must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if populated."%len(errorList))

                if "CONTROL2" in f:
                    errorList = ["Error on OBJECTID %s: CONTROL2 must follow the correct coding scheme if populated."%cursor[OBJECTID] for row in cursor
                                    if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if populated."%len(errorList))

                # Ignoring the following validation due to tech spec conflicts:
                # errorList = ["Error on OBJECTID %s: CONTROL1 must be populated with the correct coding scheme where ACCESS = BOTH or APPLY."%cursor[OBJECTID] for row in cursor
                #                 if cursor[f.index('ACCESS')] in ['BOTH','APPLY']
                #                 if cursor[f.index('CONTROL1')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                # cursor.reset()
                # if len(errorList) > 0:
                #     errorDetail[lyr].append(errorList)
                #     criticalError += 1
                #     recordValCom[lyr].append("Error on %s record(s): CONTROL1 must be populated with the correct coding scheme where ACCESS = BOTH or APPLY."%len(errorList))


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking PRP        ########################

        if lyrAcro == "PRP":
            try:

            # RESID
                errorList = ["Error on OBJECTID %s: RESID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('RESID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): RESID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking WXI        ########################

        if lyrAcro == "WXI":
            try:

            # WATXID
                errorList = ["Error on OBJECTID %s: WATXID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('WATXID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WATXID must be populated."%len(errorList))

            # WATXTYPE
                errorList = ["Error on OBJECTID %s: WATXTYPE must be populated with the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('WATXTYPE')] not in ['BRID','TEMP','CULV','MULTI','FORD','ICE','BOX','ARCH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WATXTYPE must be populated with the correct coding scheme."%len(errorList))

            # RESPONS
                errorList = ["Error on OBJECTID %s: RESPONS must be populated with the correct coding scheme."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('RESPONS')] not in ['SFL','MNR','OTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): RESPONS must be populated with the correct coding scheme."%len(errorList))

                respons_sfl_list = ["" for row in cursor if cursor[f.index('RESPONS')] == "SFL"]
                cursor.reset()
                if len(respons_sfl_list) == 0:
                    minorError += 1
                    recordValCom[lyr].append("Warning: At least one record should have RESPONS = SFL (except for Crown managed units).")       

            # ROADID
                errorList = ["Error on OBJECTID %s: ROADID must be populated."%cursor[OBJECTID] for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to value error - most likely due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1







#    Still in the for loop: "for lyr in summarytbl.keys():"

        if criticalError > 0:
            recordVal[lyr] = "Invalid-Critical"
        elif systemError:
            recordVal[lyr] = "N/A"
        elif minorError > 0:
            recordVal[lyr] = "Invalid-Minor"
        else:
            recordVal[lyr] = "Valid"

        del cursor # kill cursor

        if verbose:
            for errors_flagged in recordValCom[lyr]:
                arcpy.AddMessage('  - ' + errors_flagged)
            arcpy.AddMessage('') # just to add a new line.

    return [errorDetail, recordVal, recordValCom, fieldValUpdate, fieldValComUpdate]



if __name__ == "__main__":
    pass