#Version 1.0
#Initial version, only supports FCT/SFG/FG

#Version 1.1
#Add features for ICT and USB charger station.

#2019-08-06
#Version 1.2
#Add the samples' known standard information mapping.

#2019-08-08
#Version 1.3
#Check if the good sample quantity is same as the bad sample.

#2019-08-08
# Version=1.4;
#Only check the bad unit fails, and good unit passes.

#2019-08-08
Version=1.5;
#Sort the overall test result by test time.
#Only read the map file for the specified station.

import os;
import sys;
from collections import defaultdict;
import csv;
from datetime import datetime;

print "Script version", Version;
RequestTestTime=3;

VerifyErrorCode=False;

SummaryFolder=r"C:\temp";
if not os.path.exists(SummaryFolder):
    os.makedirs(SummaryFolder);

RootFolder=raw_input("Enter the root folder where the logs are:");
print "What kind of tester you want to analyze?";
print "1. ICT";
print "2. USB charger FT";
print "3. FCT/SFG/FG00/FG24 --> Default";
stationCategory=raw_input("Please select one of them.");
if stationCategory == "":
    stationCategory="3";
if int(stationCategory)<1 or int(stationCategory)>3:
    print "The station is unsupported, the script exits.";
    quit();
print;
class KeysInFile:
    def __init__(self):
        self.SN="";
        self.Result="";
        self.ExecID="";
        self.Time="";
        self.ECList=[];

def ParseECList(fileFullPath):
    errorCodeList=[];
    filereader=open(fileFullPath, 'r');
    lines = filereader.readlines();
    for oneline in lines:
        measurementName,result,value,lsl,usl,ec=oneline.strip().split(',');
        if result=="0":
            errorCodeList.append(ec);
    return errorCodeList;

def ParseLogFile(fileFullPath,station):
    keys=KeysInFile();
    filename=os.path.basename(fileFullPath);
    if "MB" in station or "FCT" in station:
        segs=filename.split("_");
        keys.SN=segs[0];
        keys.Result=segs[1].split('[')[0];
#         keys.Result=segs[1];
        keys.ExecID=segs[5]+"_"+segs[6]+"_"+segs[7];
        keys.Time=segs[9];
        keys.ECList=ParseECList(fileFullPath);
    if "SFG" in station:
        segs=filename.split("_");
        keys.SN=segs[0];
        keys.Result=segs[2].split('[')[0];
#         keys.Result=segs[2];
        keys.ExecID=segs[6]+"_"+segs[7];
        keys.Time=segs[9];
        keys.ECList=ParseECList(fileFullPath);
    if "ICP" in station:
        segs=filename.split("_");
        keys.SN=segs[0];
        keys.Result=segs[1].split('[')[0];
#         keys.Result=segs[1];
        keys.ExecID=segs[5]+"_"+segs[6];
        keys.Time=segs[8];
    if "FG00" in station:
        segs=filename.split("_");
        keys.SN=segs[0];
        keys.Result=segs[1].split('[')[0];
#         keys.Result=segs[1];
        keys.ExecID=segs[5]+"_"+segs[6];
        keys.Time=segs[8];
        keys.ECList=ParseECList(fileFullPath);
    if  "FG24" in station:
        segs=filename.split("_");
        keys.SN=segs[0];
        keys.Result=segs[1].split('[')[0];
#         keys.Result=segs[1];
        keys.ExecID=segs[5]+"_"+segs[6];
        keys.Time=segs[8];
        keys.ECList=ParseECList(fileFullPath);
    return keys;

def ParseUSBChargerFile(fileFullPath):
    keys=KeysInFile();
    logFileReader=open(fileFullPath);
    lines=logFileReader.readlines();
    testDateTime=lines[1].split(':')[-1].strip();
    testDate,testTime=testDateTime.split('_');
    keys.Time=testDate+testTime;
    keys.SN=lines[2].split(':')[-1].strip();
    keys.Result=lines[3].split(':')[-1].strip();
    if keys.Result=="FAIL":
        keys.Result="BAD";
    else:
        keys.Result="GOOD";
    testerSlot=lines[4].split(' ')[-1].strip();
#     testerID=lines[6].split(':')[-1].strip();
    testerID=lines[6].split('-')[-1].strip();
    keys.ExecID="UF"+testerID[:-2]+"-"+testerID[-2:]+"_"+testerSlot;
    return keys;

def ParseICTFile(fileFullPath):
    keys=KeysInFile();
    filename=os.path.basename(fileFullPath).split('.')[0];
    keys.SN,keys.Time=filename.split('_');
    logFileReader=open(fileFullPath);
    lines=logFileReader.readlines();
#     testerID=lines[2].split(':')[-1].strip();
    testerID=fileFullPath.split('\\')[-2];
    testerSlot=lines[8].split('-')[-1].strip();
    keys.ExecID=testerID+"_"+testerSlot;
    keys.Result=lines[10].split('=')[-1].strip();
    if keys.Result=="FAIL":
        keys.Result="BAD";
    else:
        keys.Result="GOOD";
    return keys;

#Read the device map information
if stationCategory=="1":
    ICTMapFile="ICTMap.csv";
    ICTPanelMap=dict();
    with open(ICTMapFile, 'r') as f:
        reader = csv.reader(f,delimiter=",");
        for sn,panel,trueValue in reader:
            ICTPanelMap[sn]=[panel,trueValue];

if stationCategory=="2":
    ChargerMapFile="ChargerMap.csv";
    ChargerMap=dict();
    with open(ChargerMapFile, 'r') as f:
        reader = csv.reader(f,delimiter=",");
        for sn,trueValue in reader:
            ChargerMap[sn]=trueValue;

if stationCategory=="3":
    FCTMapFile="FCTMap.csv";
    FCTPanelMap=dict();        
    with open(FCTMapFile, 'r') as f:
        reader = csv.reader(f,delimiter=",");
        for sn,panel,trueValue,ExpectedEC in reader:
            FCTPanelMap[sn]=[panel,trueValue,ExpectedEC];
    
    SFGMapFile="SFGMap.csv";
    SFGMap=dict();
    with open(SFGMapFile, 'r') as f:
        reader = csv.reader(f,delimiter=",");
        for sn,trueValue,ExpectedEC in reader:
            SFGMap[sn]=[trueValue,ExpectedEC];
    
    FG00MapFile="FG00Map.csv";
    FG00Map=dict();
    with open(FG00MapFile, 'r') as f:
        reader = csv.reader(f,delimiter=",");
        for sn,trueValue,ExpectedEC in reader:
            FG00Map[sn]=[trueValue,ExpectedEC];
    
    FG24MapFile="FG24Map.csv";
    FG24Map=dict();
    with open(FG24MapFile, 'r') as f:
        reader = csv.reader(f,delimiter=",");
        for sn,trueValue,ExpectedEC in reader:
            FG24Map[sn]=[trueValue,ExpectedEC];

UnitPool=defaultdict(list);
stationName="";

if stationCategory=="1":    #ICT station
    stationName="ICT";
    for path,dirs,files in os.walk(RootFolder,False):
        for logfilename in files:
            if ".TXT" not in logfilename.upper():
                continue;
            else:
                logFullPath= os.path.join(path,logfilename);
                keys=ParseICTFile(logFullPath);
                UnitPool[keys.SN+"$"+keys.ExecID].append([keys.Result,keys.Time]);

if stationCategory=="2":    #USB charger station
    stationName="USBCharger";
    for path,dirs,files in os.walk(RootFolder,False):
        for logfilename in files:
            if ".TXT" not in logfilename.upper():
                continue;
            else:
                logFullPath= os.path.join(path,logfilename);
                keys=ParseUSBChargerFile(logFullPath);
                UnitPool[keys.SN+"$"+keys.ExecID].append([keys.Result,keys.Time]);

if stationCategory=="3":    #FCT/SFG/FG00/FG24 station
    for path,dirs,files in os.walk(RootFolder,False):
        for logfilename in files:
            if ".TXT" not in logfilename.upper():
                continue;
            else:
                if "_FCT_" in logfilename or "_MB_" in logfilename:
                    stationName="FCT";
                    keys=ParseLogFile(os.path.join(path,logfilename),stationName);
                    if VerifyErrorCode==True:
                        if FCTPanelMap[keys.SN][1]=="BAD":     #Bad sample
                            if FCTPanelMap[keys.SN][2] in keys.ECList:
                                keys.Result="BAD";
                            else:
                                keys.Result="GOOD";
                        else:   #Good sample
                            if keys.Result=="PASS":
                                keys.Result="GOOD";
                            else:
                                keys.Result="BAD";
                else:
                    if "_SFG_" in logfilename:
                        stationName="SFG";
                        keys=ParseLogFile(os.path.join(path,logfilename),stationName);
                        if VerifyErrorCode==True:
                            if SFGMap[keys.SN][0]=="BAD":     #Expected bad sample
                                if SFGMap[keys.SN][1] in keys.ECList:
                                    keys.Result="BAD";
                                else:
                                    keys.Result="GOOD";
                            else:   #Expected good sample
                                if keys.Result=="PASS":
                                    keys.Result="GOOD";
                                else:
                                    keys.Result="BAD";
                    else:
                        if "_FG00_" in logfilename:
                            stationName="FG00";
                            keys=ParseLogFile(os.path.join(path,logfilename),stationName);
                            if VerifyErrorCode==True:
                                if FG00Map[keys.SN][0]=="BAD":     #Bad sample
                                    if FG00Map[keys.SN][1] in keys.ECList:
                                        keys.Result="BAD";
                                    else:
                                        keys.Result="GOOD";
                                else:   #Good sample
                                    if keys.Result=="PASS":
                                        keys.Result="GOOD";
                                    else:
                                        keys.Result="BAD";
                        else:
                            if "_FG24_" in logfilename:
                                stationName="FG24";
                                keys=ParseLogFile(os.path.join(path,logfilename),stationName);
                                if VerifyErrorCode==True:
                                    if FG24Map[keys.SN][0]=="BAD":     #Bad sample
                                        if FG24Map[keys.SN][1] in keys.ECList:
                                            keys.Result="BAD";
                                        else:
                                            keys.Result="GOOD";
                                    else:   #Good sample
                                        if keys.Result=="PASS":
                                            keys.Result="GOOD";
                                        else:
                                            keys.Result="BAD";
                            else:
                                print "Can't find keyword in log file name. It could be MB, SFG, FG00 or FG24.";
                                quit();
                if VerifyErrorCode==False:
                    if keys.Result=="FAIL":
                        keys.Result="BAD";
                    if keys.Result=="PASS":
                        keys.Result="GOOD";
                UnitPool[keys.SN+"$"+keys.ExecID].append([keys.Result,keys.Time]);
if UnitPool.__len__() ==0:
    print "There is no .txt file found in path: "+RootFolder;
    quit();

testsBalanced=True;

### Check if the trial time is balanced.
AllResults=[];
SortedResults=[];
for record in UnitPool:
    if len(UnitPool[record])!=RequestTestTime:
        sn,execid=record.split('$');
        print sn,"is tested in",execid,"unbalanced, only test",len(UnitPool[record]),"times";
        testsBalanced=False;
    else:
        for singleResult in UnitPool[record]:
            oneresult=KeysInFile();
            oneresult.SN, oneresult.ExecID=record.split('$');
            oneresult.Result,oneresult.Time=singleResult[:];
            AllResults.append(oneresult);
if testsBalanced is False:
    sys.exit();
SortedResults=sorted(AllResults,key=lambda (KeysInFile): KeysInFile.Time,reverse=False);


summaryFile=os.path.join(SummaryFolder,stationName+"_TMV_summary_"+datetime.now().strftime("%Y%m%d%H%M%S")+".csv");
summaryFileHandle=open(summaryFile,"w");
summaryFileWriter=csv.writer(summaryFileHandle,lineterminator='\n');
row=["Samples","Appraiser","True_Value","Test_Value","TestTime"];
summaryFileWriter.writerow(row);

### Check if the good sample quantity is same as bad sample.
goodDeviceCount=0;
badDeviceCount=0;
for oneRecord in SortedResults:
    sn=oneRecord.SN;
    try:
        if stationName=="USBCharger":
            expectedResult=ChargerMap[sn];
        if stationName=="ICT":
            panelID,expectedResult=ICTPanelMap[sn];
        if stationName=="FCT":
            panelID,expectedResult,expectedEC=FCTPanelMap[sn];
        if stationName=="SFG":
            expectedResult,expectedEC=SFGMap[sn];
        if stationName=="FG00":
            expectedResult,expectedEC=FG00Map[sn];
        if stationName == "FG24":
            expectedResult,expectedEC=FG24Map[sn];
    except:
        print "Something goes wrong in",sn,"mapping.";
        sys.exit();
    if stationName =="ICT" or stationName=="FCT":
        row=[panelID,sn,oneRecord.ExecID,expectedResult,oneRecord.Result,"'"+oneRecord.Time];
    else:
        row=[sn,oneRecord.ExecID,expectedResult,oneRecord.Result,"'"+oneRecord.Time];
    summaryFileWriter.writerow(row);
    if expectedResult=="BAD":
        badDeviceCount+=1;
    else:
        goodDeviceCount+=1;
summaryFileHandle.close();
# print summaryFile,"is generated.";
if badDeviceCount!=goodDeviceCount:
    os.remove(summaryFile);
    print "The good samples are tested {} times, but the bad samples are tested {} times, they should be same.".format(goodDeviceCount,badDeviceCount);
#     print summaryFile,"is deleted.";
    sys.exit();
print "The analysis finishes.";
print "The summary file is", summaryFile;