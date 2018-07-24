#-------------------------------------------------------------------------------
# Name:        CheckAll
# Purpose:
#
# Author:      Ministry of Natural Resources and Forestry (MNRF)
#
# Created:     24/02/2017
# Copyright:   MNRF
# 
# Updates:  2018 05 28: #U001 Added warning if no layer found with correct naming convention
#           Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#-------------------------------------------------------------------------------

import Reference, htmlstyle
import os, datetime, pprint, inspect, webbrowser
import arcpy
# import importlib

test_mode = False

class Check():
    def __init__(self,plan,fmu,year,fmpStartYear,workspace,dataformat,tech_spec_version,error_limit,checker_version,subID = None):
        self.plan = plan.upper()
        self.fmu = fmu
        self.year = year
        self.fmpStartYear = fmpStartYear
        self.workspace = workspace ## N:\WORK-DATA\FMPDS\Abitibi_River\AWS\2017\_data\FMP_Schema.gdb
        self.dataformat = dataformat # eg. 'shapefile','feature classes' or 'coverage'
        self.tech_spec_version = tech_spec_version
        self.old_or_new = 'NEW' if tech_spec_version == '2017' else 'OLD'
        self.subID = subID
        self.error_limit = error_limit
        self.checker_version = checker_version

    # this method calls all other functions and methods. This method is the backbone of the checker program.
    def run(self):
        importstr = "import TechSpec_" + self.plan + "_" + self.old_or_new + " as TechSpec" ## for example "import TechSpec_FMP_NEW as TechSpec"
        exec(importstr)
        self.TechSpec = TechSpec

        self.today = datetime.date.today()

        print("\nWorking on " + self.workspace)
        arcpy.AddMessage("\nWorking on " + self.workspace)

        if self.dataformat == 'feature classes':
            self.mainFolder = os.path.split(self.workspace)[0] ## The report will be saved in this folder: N:\WORK-DATA\FMPDS\Abitibi_River\AWS\2017\_data
        else:
            self.mainFolder = self.workspace ## The report will be saved in this folder: N:\WORK-DATA\FMPDS\Abitibi_River\AWS\2017\shp

        # creating the html report file.
        if self.subID in [None, '']:
            self.subID = Reference.findSubID(os.path.split(self.mainFolder)[0]) # looking for the submission ID from fi_Submission txt file located in, for example, ...\Abitibi_River\AWS\2017 folder
        self.MUNumber = Reference.FMUCodeConverter(self.fmu)
        self.htmlfile = '%s\\MU%s_%s_%s_Report_%s.html'%(self.mainFolder,self.MUNumber,self.year,self.plan,self.subID) #eg. ..2017\AWS_Report_20987.html

        print("\nWriting the html file: " + self.htmlfile)
        arcpy.AddMessage("\nWriting the html file: " + self.htmlfile)

        rep = open(self.htmlfile,'w')
        # Add Style
        rep.write(htmlstyle.htmlStyle)
        # Start Body
        rep.write('<body>')
        # Add Header
        rep.write('<h1>%s Tech Spec Validation Report on %s</h1>'%(self.plan,self.workspace))
        # Add Report Summary info
        rep.write(self.htmlReportSummary1())

        # creating an empty summary dictionary
        self.summarytbl = {}

        #Running validations...
        if self.dataformat == 'coverage':
            self.layerPresent_4Coverage() ## after this module, self.summarytbl = {'C:\Algoma_AWS_e00\E00\mu615_18agp00\point': ['AGP','Existing forestry aggregate pits'], ...}
        else:
            arcpy.env.workspace = self.workspace
            self.layerPresent() ## after this module, self.summarytbl = {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern'], 'MU110_17SAC11': ['SAC', 'Scheduled Area Of Concern'],

        ## adding projection to the summary tbl - eg. {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N'], 'MU110_17SAC11': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N'],...}
        self.projection() 

        ## adding mandatory and non mandatory field lists to the summary tbl {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'MU110_17SAC10_', 'MU110_17SAC10_ID']], ...}
        self.fieldValidation() 

        ## This runs the record-based validations using arcpy.da.SearchCursor.
        self.recordValidation()
        
        self.attachFimRef()

        # Add Report Summary Table
        rep.write(self.htmlReportSummary2())

        # Add error deatil
        rep.write(self.htmlErrorDetail())

        # *Used to add watchfile summary (if available) right here* 

        # Add footnote
        rep.write(self.htmlFootnote())
        rep.write('</body></html>')
        rep.close()

        print("Time: :" + self.timeEnd)
        print("The report can be found here:\n" + self.htmlfile)
        print("*************       Script Complete!        ******************\n")
        arcpy.AddMessage("\nThe report can be found here:\n" + self.htmlfile)
        webbrowser.open(self.htmlfile,new=2)


    def htmlReportSummary1(self):
        htmlstring ='<h2>Report Summary</h2>'
        htmlstring += '''
            <table id="t01">
              <tr><td>Submission Type:</td> <td>%s</td>             </tr>
              <tr><td>Submission Year:</td> <td>%s</td>             </tr>
              <tr><td>MU Name:</td>         <td>%s</td>             </tr> 
              <tr><td>Submission ID:</td>   <td>%s</td>             </tr>             
              <tr><td>Plan Start Year:</td> <td>%s</td>             </tr>
              <tr><td>MU Number:</td>       <td>%s</td>             </tr>
              <tr><td>Date Reviewed:</td>   <td>%s</td>             </tr>
              <tr><td>Tech Spec Used:</td>  <td>%s version</td>     </tr>
              <tr><td>Data Format:</td>     <td>%s</td>             </tr>              
            </table> <br>
            '''%(self.plan,self.year,self.fmu,self.subID,self.fmpStartYear, self.MUNumber,self.today,self.tech_spec_version, self.dataformat)
        return htmlstring


    def layerPresent(self):
        print("\nChecking which layers are present...")
        arcpy.AddMessage("\nChecking which layers are present...")

        # grabbing the list of layer acronyms from the techspec module.
        self.LyrAcronyms = list(self.TechSpec.lyrInfo.keys()) ## eg.['SRC', 'SHR', 'SRA', 'SRG', 'SAG', 'SWC', 'STT', 'SRP', 'AGP', 'SAC', 'SPT', 'SSP', 'SNW', 'SOR']
        
        # List of the actual layers found in the user input.
        self.lyrs = [str(f).upper() for f in arcpy.ListFeatureClasses()] ##eg. ['MU110_17AGP00', 'MU110_17SAC01', 'MU11019SAC001'...] This will be used as keys for the dictionary self.summarytbl.

        # checking additional layers
        additionalLayers = [lyr for lyr in self.lyrs if lyr[8:11] not in self.LyrAcronyms and lyr[7:10] not in self.LyrAcronyms] ##eg. ['mu509_17nat00']  #v2017 edited for cases such as MU96518SAC003 and MU965_18SAC003
        self.strAdditionalLayers = ''
        if len(additionalLayers) > 0 :
            self.strAdditionalLayers = 'Additional layer(s) found: ' + str(additionalLayers)
        self.lyrs = sorted([i for i in self.lyrs if i not in additionalLayers]) # removing the additional files, such as NAT, or any other misnamed layers from the list.

        #U001 Warning if all we found are additional layers (i.e. no layer found with correct naming convention)
        if len(self.lyrs) == 0:
            arcpy.AddError("!!!!!! Could not find any %s spatial data. \nMake sure your spatial data follows the correct naming convention (i.e. MU123_99LYR00)."%self.plan)
        # letting the users know which spatial layers are found and will be checking.
        else:
            arcpy.AddMessage("\tThe following layers have been found:")
            for lyr in self.lyrs:
                arcpy.AddMessage("\t\t" + str(lyr))      

        # checking missing layers.
        lyrsMissing = []
        for lyr in self.LyrAcronyms:
            if len([f for f in self.lyrs if f[8:11] == lyr or f[7:10] == lyr]) == 0:  # if there's zero layer that has, for example, 'SRP' word in it... #v2017 edited for cases such as MU96518SAC003 and MU965_18SAC003
                lyrsMissing.append(self.TechSpec.lyrInfo[lyr][0])  # list of missing layers such as ["Scheduled Residual Patches", "Scheduled Protection Treatment"]
        self.strLyrsMissing = ''
        if len(lyrsMissing) > 0:
            self.strLyrsMissing = 'Missing layer(s): ' + str(lyrsMissing)

        # Feb 2018 edit: catching layers that did not follow the naming convention
        self.misnamed_lyrs = []
        self.str_misnamed_lyrs = ''
        for lyr in self.lyrs:
            if lyr[6:8] != str(self.year)[-2:] and lyr[5:7] != str(self.year)[-2:]:
                self.misnamed_lyrs.append(lyr + ' - layer name does not match the submission year (%s).'%str(self.year)[-2:])
            elif lyr[2:5] != self.MUNumber:
                self.misnamed_lyrs.append(lyr + ' - layer name should contain correct FMU code (%s).'%self.MUNumber)
        if len(self.misnamed_lyrs) > 0:
            self.str_misnamed_lyrs += "Misnamed layer(s) found:"
            for item in self.misnamed_lyrs:
                self.str_misnamed_lyrs += '<br>%s'%item


        # updating the summary dictionary table.
        # self.lyrs is a list of all the spatial layers that the tool will be checking.
        self.summarytbl.update(dict(zip(self.lyrs,[[] for i in self.lyrs]))) ## eg. {'MU110_17SAC10': [], 'MU110_17SAC11': [],..}
        for key in list(self.summarytbl.keys()):
            for i in self.LyrAcronyms:
                if i in key: # for example, if 'SAC' in 'MU96518SAC003'
                    self.summarytbl[key].append(i)
                    self.summarytbl[key].append(self.TechSpec.lyrInfo[i][0]) ## eg. {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern'], 'MU110_17SAC11': ['SAC', 'Scheduled Area Of Concern'],



    def layerPresent_4Coverage(self):
        """ after this module is run, self.summarytbl becomes {'C:\Algoma_AWS_e00\E00\mu615_18agp00\point': ['Yes'], 'C:\Algoma_AWS_e00\E00\mu615_18shr00\polygon': ['Yes'], ...}
        """
        arcpy.AddMessage("\nChecking which layers are present...")

        # grabbing the list of layer acronyms from the techspec module.
        self.LyrAcronyms = list(self.TechSpec.lyrInfo.keys()) ## eg.['SRC', 'SHR', 'SRA', 'SRG', 'SAG', 'SWC', 'STT', 'SRP', 'AGP', 'SAC', 'SPT', 'SSP', 'SNW', 'SOR']
        
        # List of all the folders inside the workspace
        self.lyrs = [os.path.join(self.workspace,i).upper() for i in os.listdir(self.workspace) if os.path.isdir(os.path.join(self.workspace,i))] ##eg. ['C:\Algoma_AWS_e00\E00\info','C:\Algoma_AWS_e00\E00\mu615_18agp00',...]

        # Make sure there is an 'info' folder in the workspace.
        info_folder_finder = ['y' for i in self.lyrs if os.path.split(i)[1] == 'INFO']
        if len(info_folder_finder) < 1:
            arcpy.AddError("\n****** Checker Tool was not able to locate 'info' folder in the workspace specified.")
            arcpy.AddError("Make sure to specify the PARENT folder of where all your coverage folders are located.")

        # checking additional layers
        additionalLayers = [lyr for lyr in self.lyrs if lyr[-5:-2] not in self.LyrAcronyms and lyr[-6:-3] not in self.LyrAcronyms]
        self.strAdditionalLayers = ''
        ### commenting out the following since there will always be additional folders in workspace folder.
        # if len(additionalLayers) > 0 :
        #     self.strAdditionalLayers = 'Additional layer(s) found: ' + str(additionalLayers)

        self.lyrs = sorted([i for i in self.lyrs if i not in additionalLayers]) # At this point, any folders that doesn't carry the layer acronym such as SRC have been removed.
        # At this point, self.lyrs looks like this (all caps): ['C:\ALGOMA_AWS_E00\E00\MU615_18AGP00','C:\ALGOMA_AWS_E00\E00\MU615_18SAC01','C:\ALGOMA_AWS_E00\E00\MU615_18SAC02'...]

        #U001 Warning if all we found are additional layers (i.e. no layer found with correct naming convention)
        if len(self.lyrs) == 0:
            arcpy.AddError("!!!!!! Could not find any %s spatial data. \nMake sure your spatial data follows the correct naming convention (i.e. MU123_99LYR00)."%self.plan)
        else:
            # letting the users know which coverages have been found and will be checked.
            arcpy.AddMessage("\tThe following coverages have been found:")
            for lyr in self.lyrs:
                arcpy.AddMessage("\t\t%s"%os.path.split(lyr)[1])

        # checking missing layers.
        lyrsMissing = []
        for lyr in self.LyrAcronyms:
            if len([f for f in self.lyrs if f[-5:-2] == lyr or f[-6:-3] == lyr]) == 0:  # if there's zero layer that has, for example, 'SRP' word in it... #v2017 edited for cases such as MU96518SAC003 and MU965_18SAC003
                lyrsMissing.append(self.TechSpec.lyrInfo[lyr][0])  # list of missing layers such as ["Scheduled Residual Patches", "Scheduled Protection Treatment"]
        self.strLyrsMissing = ''
        if len(lyrsMissing) > 0:
            self.strLyrsMissing = 'Missing layer(s): ' + str(lyrsMissing)

        # Feb 2018 edit: catching layers that did not follow the naming convention
        self.misnamed_lyrs = []
        self.str_misnamed_lyrs = ''
        for lyr in self.lyrs:
            if lyr[-7:-5] != str(self.year)[-2:] and lyr[-8:-6] != str(self.year)[-2:]:
                self.misnamed_lyrs.append(os.path.split(lyr)[1] + ' - layer name does not match the submission year (%s).'%str(self.year)[-2:])
            elif lyr[-11:-8] != self.MUNumber:
                self.misnamed_lyrs.append(os.path.split(lyr)[1] + ' - layer name should contain correct FMU code (%s).'%self.MUNumber)
        if len(self.misnamed_lyrs) > 0:
            self.str_misnamed_lyrs += "Misnamed layer(s) found:"
            for item in self.misnamed_lyrs:
                self.str_misnamed_lyrs += '<br>%s'%item

        # For Coverage, we need to add 'polygon','arc', or 'point' to each item in self.lyrs.
        lyrs_with_fullpath = []
        for lyr in self.lyrs:
            for acro in self.LyrAcronyms:
                if acro in os.path.split(lyr)[1]:
                    fullpath = os.path.join(lyr,self.TechSpec.lyrInfo[acro][2]) # joining 'C:\ALGOMA_AWS_E00\E00\MU615_18AGP00' and 'point'
                    if arcpy.Exists(fullpath):
                        lyrs_with_fullpath.append(fullpath.upper())
                    else:
                        arcpy.AddWarning('Unable to locate "%s"'%fullpath) # this could mean that 
        self.lyrs = lyrs_with_fullpath
        # At this point, self.lyrs looks like this: ['C:\ALGOMA_AWS_E00\E00\MU615_18AGP00\POINT','C:\ALGOMA_AWS_E00\E00\MU615_18SAC01\POLYGON','C:\ALGOMA_AWS_E00\E00\MU615_18SAC02\POLYGON'...]


        # updating the summary dictionary table.
        # self.lyrs is a list of all the spatial layers that the tool will be checking.
        self.summarytbl.update(dict(zip(self.lyrs,[[] for i in self.lyrs]))) ## eg. {'C:\ALGOMA_AWS_E00\E00\MU615_18AGP00\POINT': [], 'C:\ALGOMA_AWS_E00\E00\MU615_18SAC01\POLYGON': [],..}
        for key in list(self.summarytbl.keys()):
            for i in self.LyrAcronyms:
                if i in key: # for example, if 'SAC' in 'MU96518SAC003'
                    self.summarytbl[key].append(i)
                    self.summarytbl[key].append(self.TechSpec.lyrInfo[i][0]) ## eg. {'C:\ALGOMA_AWS_E00\E00\MU615_18AGP00\POINT': ['AGP', 'Existing Forestry Aggregate Pits'], 'C:\ALGOMA_AWS_E00\E00\MU615_18SAC01\POLYGON': ['SAC', 'Scheduled Area Of Concern'],


    def projection(self):
        print("\nChecking projection...")
        arcpy.AddMessage("\nChecking projection...")

        projection_list = []
        for lyr in self.lyrs:
            desc = arcpy.Describe(lyr)
            SRName = desc.spatialReference.name.replace('_',' ') ## eg.NAD 1938 UTM Zone 17N
            self.summarytbl[lyr].append(str(SRName)) ##eg. {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N'], 'MU110_17SAC11': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N'],...}
            projection_list.append(SRName)

        self.num_of_proj_used = len(set(projection_list))
        self.strProjectionCheck = ''

        if self.num_of_proj_used == 1:
            self.strProjectionCheck += 'All layers are using the same projection: %s'%projection_list[0]
            arcpy.AddMessage("\t" + self.strProjectionCheck)
        elif self.num_of_proj_used > 1:
            self.strProjectionCheck += 'Not all layers are using the same projection!!'
            arcpy.AddMessage("\t" + self.strProjectionCheck)

    def fieldValidation(self):
        """
        Checks missing field and additional fields. 
        """
        print("\nChecking field names...")
        arcpy.AddMessage("\nChecking field names...")

        removeList = ['Shape', 'AREA','PERIMETER','FNODE_','TNODE_', 'LPOLY_', 'RPOLY_', 'LENGTH','Shape_Length', 'Shape_Area', 'POLYGONID', 'SCALE', 'ANGLE']
        self.fieldValidation = dict(zip(self.lyrs,['Invalid' for i in self.lyrs])) ## eg. {'MU110_17SAC10': 'Invalid', 'MU110_17SAC11': 'Invalid',...}
        self.fieldDefComments = dict(zip(self.lyrs,[[] for i in self.lyrs])) ## eg. {'MU110_17SAC10': [], 'MU110_17SAC11': [],...}
        for i in self.LyrAcronyms:
            for lyr in self.lyrs: # self.lyrs is a list of all the spatial layers that the tool will be checking.
                if i in lyr:
                    manFields = self.TechSpec.lyrInfo[i][1] ##eg. ['PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP']
                    self.testingFields = [str(f.name).upper() for f in arcpy.ListFields(lyr)] ##eg. ['OBJECTID', 'Shape', 'AREA', 'PERIMETER', 'MU110_17AGP00_', 'MU110_17AGP00_ID', 'PIT_ID', 'PIT_NAME', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP', 'POLYGONID', 'SCALE', 'ANGLE']
                    self.testingFields = [f for f in self.testingFields if f not in removeList] ##eg. ['OBJECTID', 'MU110_17AGP00_', 'MU110_17AGP00_ID', 'PIT_ID', 'PIT_NAME', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP']
                    self.existingManFields = [f for f in self.testingFields if f in manFields] ##eg. ['PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP']
                    self.additionalFields = [f for f in self.testingFields if f not in manFields] ## eg. ['OBJECTID', 'MU110_17AGP00_', 'MU110_17AGP00_ID', 'PIT_NAME']
                    self.summarytbl[lyr].append(self.existingManFields)
                    self.summarytbl[lyr].append(self.additionalFields)
                    if len(self.existingManFields) == len(manFields):
                        self.fieldValidation[lyr] = 'Valid'
                    else:
                        missingFields = [f for f in manFields if f not in self.existingManFields]
                        self.fieldDefComments[lyr].append('Field(s) missing: ' + str(missingFields))

    def recordValidation(self):
        print("\nChecking each record...")
        arcpy.AddMessage("\nChecking each record...")
        result = self.TechSpec.run(self.workspace, self.summarytbl, self.year, self.fmpStartYear)

        self.errorDetail = result[0] #eg. {'MU110_17AGP00': [['Error on OBJECTID 1: The population of PIT_OPEN is mandatory and the attribute must follow the correct coding scheme.', 'Error on OBJECTID 2:...]]}

        self.recordVal = result[1] #eg. {'MU110_17AGP00': 'Invalid-Critical', 'MU110_17SAC01': 'Invalid-Critical',...}

        self.recordValCom = result[2] #eg. {'MU110_17AGP00': ['Total number of records checked: 250', 'Error on 2 record(s): The population of PIT_OPEN is mandatory and the attribute must follow the correct coding scheme (A1.14.2).',...}

        self.fieldValUpdate = result[3] #fieldValUpdate is any updates to existing fieldValidation variable. eg. {'MU110_17SPT00': 'Invalid',...}. For instance, if MGMTCON2 is missing while MGMTCON3 is present, even though both fields are non-mandatory fields, this will flag an error.

        self.fieldValComUpdate = result[4] #fieldValComUpdate is any updates to existing fieldDefComments variable. eg. {'MU110_17SPT00': ['TRTMTHD2 is mandatory when TRTMTHD3 is present.'],...}

        # Updating the self.summarytbl...
        for lyr in self.lyrs: 
            if len(self.fieldValUpdate[lyr]) != 0: # checking if there are any updates to Field Validation column.
                self.fieldValidation[lyr] = self.fieldValUpdate[lyr]
            if len(self.fieldValComUpdate[lyr]) != 0: # checking if there are any updates to Field Definition Comments column.
                self.fieldDefComments[lyr] =  self.fieldDefComments[lyr] + self.fieldValComUpdate[lyr]
            self.summarytbl[lyr].append(self.fieldValidation[lyr])
            self.summarytbl[lyr].append(self.fieldDefComments[lyr])
            self.summarytbl[lyr].append(self.recordVal[lyr])
            self.summarytbl[lyr].append(self.recordValCom[lyr])


    def attachFimRef(self):
        """Searchs for the tech spec url and section number in the TechSpec_XYZ_ABC.py"""
        for lyr in self.lyrs: # self.lyrs is a list of all the spatial layers that the tool just checked.
            try:
                techspec_url = self.TechSpec.lyrInfo[self.summarytbl[lyr][0]][4]  # 20180603 changed to 4 from 3 to add Data Type
                techspec_section = self.TechSpec.lyrInfo[self.summarytbl[lyr][0]][3] # 20180603 changed to 3 from 2 to add Data Type
                html = '<a href="' + techspec_url + '" target="_blank">' + techspec_section + '</a>'
                self.summarytbl[lyr].append(html)
            except:
                self.summarytbl[lyr].append(str(techspec_section))



    def htmlReportSummary2(self):
        print("\nFilling out the HTML report")
        arcpy.AddMessage("\nFilling out the HTML report")
        htmlstring = ''
        if len(self.str_misnamed_lyrs) > 0:
            htmlstring += '<p id="p03">' + self.str_misnamed_lyrs +  '</p>'
        if len(self.strLyrsMissing) > 0: 
            htmlstring += '<p id="p02">' + self.strLyrsMissing +  '</p>'
        htmlstring += '''
            <table id="t02">
              <tr>
                <th>Layer File Name</th>
                <th>Layer Name</th>
                <th>Existing Mandatory Fields</th>
                <th>Additional Fields</th>
                <th>Field Validation</th>
                <th>Field Comments</th>
                <th>Record Validation</th>
                <th>Record Validation Comments</th>
                <th><small>Reference</small></th>
              </tr>'''
        for lyr in self.lyrs:
            htmlstring += '<tr>'

            # Layer File Name
            if self.dataformat == 'coverage':
                filename = os.path.split(os.path.split(lyr)[0])[1]
                htmlstring += '<td><div class="tooltip">' + filename + '<span class="tooltiptext">Projection: ' + self.summarytbl[lyr][2] + '</span></div></td>' # Layer File Name + projection when hovering over.
            else:
                htmlstring += '<td><div class="tooltip">' + lyr + '<span class="tooltiptext">Projection: ' + self.summarytbl[lyr][2] + '</span></div></td>'

            htmlstring += '<td><small>' + self.summarytbl[lyr][1] + '</small></td>' # Layer Name
            # htmlstring += '<td><small>' + self.summarytbl[lyr][2] + '</small></td>' # Projection # now the projection is viewed by hovering over the file name.
            htmlstring += '<td><small>' + Reference.shortenList(self.summarytbl[lyr][3]) + '</small></td>' # Existing Mandatory Fields
            htmlstring += '<td><small>' + Reference.shortenList(self.summarytbl[lyr][4]) + '</small></td>' # Additional Fields
            if self.summarytbl[lyr][5] == 'Invalid':
                htmlstring += '<td><p id="p03">' +self.summarytbl[lyr][5] + '</p></td>' # Field Validation - red if invalid
            else:
                htmlstring += '<td><p id="p01">' +self.summarytbl[lyr][5] + '</p></td>' # Field Validation - green if invalid
            if len(self.summarytbl[lyr][6]) == 0:
                htmlstring += '<td>N/A</td>' # Field Definition Comments - N/A if there isn't any.
            else:
                htmlstring += '<td><small>'
                for line in self.summarytbl[lyr][6]: # Field Definition Comments - if there's one or more, write each line separately
                    htmlstring += '- ' + line + '<br>'
                htmlstring += '</small></td>'
            if self.summarytbl[lyr][7] == 'Invalid-Critical':
                htmlstring += '<td><p id="p03">' +self.summarytbl[lyr][7] + '</p></td>' # Field Validation - red if invalid critical
            elif self.summarytbl[lyr][7] == 'Invalid-Minor':
                htmlstring += '<td><p id="p02">' +self.summarytbl[lyr][7] + '</p></td>' # Field Validation - orange if invalid minor
            elif self.summarytbl[lyr][7] == 'Valid':
                htmlstring += '<td><p id="p01">' +self.summarytbl[lyr][7] + '</p></td>' # Field Validation - green if valid
            else:
                htmlstring += '<td>' + self.summarytbl[lyr][7] + '</td>' # Field Validation - regular font if anything else

            htmlstring += '<td><small>'
            # Record Validation Comment - first line (Total 99 records with 9 artifacts)
            htmlstring += '<div class="tooltip">- ' + self.summarytbl[lyr][8][0] + '<span class="tooltiptext">Artifacts are empty polygons populated in coverages to fill up the holes in polygons.</span></div><br>'
            if len(self.summarytbl[lyr][8]) > 1:
                for line in self.summarytbl[lyr][8][1:]: # Record Validation Comments - write each line separately
                    htmlstring += '- ' + line + '<br>'
            htmlstring += '</small></td>'
            htmlstring += '<td>' + self.summarytbl[lyr][9] + '</td>' # FIM Reference
            htmlstring += '</tr>' # End of line

        htmlstring += '</table>'
        if len(self.strLyrsMissing) > 0: htmlstring += '<p id="p02">' + self.strLyrsMissing +  '</p>' # Missing layers
        if len(self.strAdditionalLayers ) > 0: htmlstring += '<br>' + self.strAdditionalLayers + '<br>'

        if self.num_of_proj_used == 1:
            htmlstring += '<br>' + self.strProjectionCheck + '<br>' # All layers are using the same projection
        elif self.num_of_proj_used > 1:
            htmlstring += '<br><p id="p03">' + self.strProjectionCheck + ' - Hover over each layer name to check the projection.</p>' # Not all layers are using the same projection.

        htmlstring += '<br>'
        return htmlstring

    def htmlErrorDetail(self):
        htmlstring = '''<h2>Error Detail</h2>'''
        errors = 0
        for lyr in self.lyrs:
            if len(self.errorDetail[lyr]) > 0: ## if there are errors...
                errorDetailListList = Reference.sortError(self.errorDetail[lyr],self.error_limit) # *************************** This is where you change the number of same errors appear on error detail section.
                errors += 1
                htmlstring += '<h3>' + lyr + '</h3>'
                htmlstring += '<p><small>'

                for errorType in errorDetailListList:
                    for line in errorType:
                        htmlstring += line + '<br>'
                    htmlstring += '<br>'

                htmlstring += '</small></p>'
        if errors == 0:
            htmlstring += '<p>None found.<p>'
        return htmlstring

    def htmlFootnote(self):
        htmlstring = '''<h2>Footnote</h2>'''
        self.timeEnd = str(datetime.datetime.now())
        htmlstring += '<p>'
        htmlstring += 'This report has been saved as: ' + self.htmlfile + '<br>'
        htmlstring += 'Time created: ' + self.timeEnd + '<br>'
        htmlstring += 'Python script used: ' + inspect.getfile(inspect.currentframe())  + '<br>'        
        htmlstring += 'Checker version used: v' + self.checker_version  + '<br>'
        htmlstring += '</p>'
        return htmlstring


# Tester:
if __name__ == '__main__':
    pass