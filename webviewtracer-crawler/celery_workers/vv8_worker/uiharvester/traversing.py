#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import itertools
import random
import string
import copy
import re
import datetime
import datetime as dt
import itertools
import hashlib
import time
import shutil
from collections import deque
import datetime as dt
import getopt
import pickle
from enum import Enum
import fcntl
import base64
import argparse
import math
import xml.etree.ElementTree as ET 
import xmltodict
from PIL import Image
import imagehash
import contextlib

import signal

device=""
apk=""
shellCommand="adb -s "+device+" shell "
adbCommand="adb -s "+device+" "
logcatTag="UIHarvester"
weblogcatTag="UIWebHarvester"
global logcatRandomTag
global countSleepTime


global ldate
global lwebviewdate
lwebviewdate=""
ldate=""
GMSQueue=[]
activitiesQueue=[]
BFSQueue=[]
DFSQueue=[]
monkeyQueue=[]
global display
display=(0,0)

global runBFS
global acceptColor
global rejectColor
global isAppOpened
global timesReopened

#Initialize default variables
runBFS = 1;isAppOpened=1;timesReopened=0;

apk="";traversal=""; path="."; device=""; sleepTime=0.5; sleepXforMainActivity=1;timeout=60;countSleepTime=0;eventsFired=0;screenshots=1;webviewswait=0;
grant_consent_dialogue=0;

record_replay="";record_file="";replay_file="";RECORD_REPLAY_PATH="./Utilities/RecordReplay/bin/";

fridaScripts="";FRIDA_SCRIPTS_PATH="./frida-scripts/";

activities=0;google_sso=0;google_sso_error_counter=0;googleLoggedIn=0;

setPriorities=0;
activity_dict = {};
activity_counter=0;

facebookLoggedIn=0;apkPath="";

priorityList = set([" agree", "continue", " allow", "accept", "next", " yes", "consent", "confirm", 
                 "understand", " begin", " informed", "acceptance", "okay", "support", "experience",
                 "disagree", "reject", "dont allow", "not allow", "dont accept", "not accept", "not now", 
                 "cancel", "not agree", "dont agree", "not consent", "dont consent", "only required", 
                 "deny", "decline", "no, ", "exit app", "refuse", "dismiss", "skip"])
priorityEqList=["go", "ok", "start", "get started"]

consentList = ["agree", "allow", "accept", "consent", "confirm", "begin", "informed",
                  "acceptance", "okay", "grant" , "continue", "next", "yes", "support", "understand",
                  "go", "ok", "start", "started", "save"]
dialogueList = ["privacy", "collect", "cookie", "policy", "advertis", "unique identifier","terms ", "agreement", "use of service", "use of data", "protect your", "your experience", "you agree", "personali", "cookies"]


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def handler(signum, frame):
    print("Ctrl + c is pressed!!!")
    os.system("kill -9 $! > /dev/null 2>&1")
    os.system("pkill -f \""+adbCommand+"\"")
    #kill frida process
    os.system('pkill -f "frida -U -f '+apk+' -l '+FRIDA_SCRIPTS_PATH+'UIHarvester.js"')
    exit(1) 
 
signal.signal(signal.SIGINT, handler)
    
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def getLogcatDate():
    global ldate
    proc  = subprocess.Popen(["echo $ldate"], stdout=subprocess.PIPE, shell=True)
    (ldate, err) = proc.communicate()
    ldate= ldate.decode('ascii').replace("\n", "")
#End

def setLogcatDate():
    global ldate
    command=shellCommand+" \"(date +'%m-%d %H:%M:%S.000')\""
    proc  = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (ldate, err) = proc.communicate()
    ldate= ldate.decode('ascii').replace("\n", "")
    os.environ["ldate"] = ldate
#End

def getWebviewLogcatDate():
    global lwebviewdate
    proc  = subprocess.Popen(["echo $lwebviewdate"], stdout=subprocess.PIPE, shell=True)
    (lwebviewdate, err) = proc.communicate()
    lwebviewdate= lwebviewdate.decode('ascii').replace("\n", "")
#End

def setWebviewLogcatDate():
    global lwebviewdate
    command=shellCommand+" \"(date +'%m-%d %H:%M:%S.000')\""
    proc  = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (lwebviewdate, err) = proc.communicate()
    lwebviewdate= lwebviewdate.decode('ascii').replace("\n", "")
    os.environ["lwebviewdate"] = lwebviewdate
#End

def printFeatures(queueFile):
    fieldSeperator="--"
    # load additional module
    import pickle
    try:
        with open(queueFile, 'rb') as filehandle:  
            # read the data as binary data stream
            queueFile = pickle.load(filehandle)
            #Get all keys
            all_keys = list(set().union(*(list(d[4].keys()) for d in queueFile)))
            i=0
            print("#", end=' ')
            for i in range(len(all_keys)):
                if i==len(all_keys)-1:
                    print(all_keys[i])
                else:
                    print(all_keys[i]+fieldSeperator, end=' ')
                    
            for item in queueFile:
                for i in range(len(all_keys)):
                    if i==len(all_keys)-1:
                        if all_keys[i] in item[4]:
                            print(item[4][all_keys[i]])
                        else:
                            print("N/A")
                    else:
                        if all_keys[i] in item[4]:
                            print(str(item[4][all_keys[i]])+fieldSeperator, end=' ')
                        else:
                            print("N/A"+fieldSeperator, end=' ')
                                        
        return queueFile 
    except IOError as e:
        print(e)
#End

def loadQueue(queueFile):
    # load additional module
    import pickle
    
    print(bcolors.OKBLUE + "File: "+bcolors.ENDC + queueFile)
    try:
        with open(queueFile, 'rb') as filehandle:  
            # read the data as binary data stream
            try:
                queueFile = pickle.load(filehandle)
                printTmpList(queueFile)
            except:
                print(bcolors.FAIL + "Wrong or corrupted file: "+bcolors.ENDC + queueFile)
            
        return queueFile 
    except IOError as e:
        print(e)
#End
        
def printOutput(currentTime,FullPathfile):
    global countSleepTime
    global traversal
    name = ""
    Queue=[]
    if traversal=="BFS":
        Queue = BFSQueue
        name=traversal
    elif traversal=="DFS":
        Queue = DFSQueue
        name=traversal
    else:
        Queue = monkeyQueue
        name=traversal
    
    printTmpList(Queue)
    #Save results to file
    f = open(FullPathfile+"_"+name+'.txt', 'w')
    print("# ActualTime TimeWithoutSleep eventsFired elementsFound, googleLoggedIn", file=f)
    print(currentTime , currentTime-countSleepTime, eventsFired, str(len(Queue)) , facebookLoggedIn, file=f)
    print(bcolors.OKBLUE + "ActualTime: "+ bcolors.ENDC+ str(currentTime) +\
          bcolors.OKBLUE + " TimeWithoutSleep: "+ bcolors.ENDC +str(currentTime-countSleepTime) +\
          bcolors.OKBLUE + " eventsFired: "+bcolors.ENDC + str(eventsFired) +\
          bcolors.OKBLUE + " elementsFound: "+bcolors.ENDC + str(len(Queue)) +\
          bcolors.OKBLUE + " googleLoggedIn: "+bcolors.ENDC + str(googleLoggedIn))
    f.close()
    
    #Save the Queue independent of traversal 
    with open(path+"/"+"Queue_"+name+".data", "wb") as filehandle:  
            # store the data as binary data stream
            pickle.dump(Queue, filehandle)
    
#End

def printGraph():
    tmpdict={}
    for item in BFSQueue:
        if len(item[3]) not in tmpdict:
            tmpdict[len(item[3])]=[]
            tmpdict[len(item[3])].append((item[0]))
    
    f = open('./data/'+apk+'/'+apk+'graph.txt', 'w')
    print(tmpdict, file=f)
    f.close()
#End

def zipFiles():
    shutil.make_archive("./data/"+apk, 'tar', "./data/"+apk+"/")
    os.system("rm -rf ./data/"+apk+"/")
#End  
  
def createFolder():
    if not os.path.exists(path+"/"+apk):    
        os.system("mkdir "+path+"/"+apk)
#End    

def screenshot(name):
    os.system(shellCommand+" screencap -p > "+path+"/"+name+".png")
#End

def removeFromQueue(T, T2):
    global traversal

    print("Remove from Queue...")
    remove_list=[]
    if traversal=="BFS":
        for UIelement in BFSQueue:
            if UIelement[4]['TimeStampWithClicksTime']==T2 and UIelement[4]['TimeStamp']==T:
                remove_list.append(UIelement)

        for elem in remove_list:
            BFSQueue.remove(elem)

    elif traversal=="DFS":
        for UIelement in DFSQueue:
            if UIelement[4]['TimeStampWithClicksTime']==T2 and UIelement[4]['TimeStamp']==T:
                remove_list.append(UIelement)

        for elem in remove_list:
            DFSQueue.remove(elem)

    time.sleep(1)

def readAndAdd(start_time):
    global traversal

    setLogcatDate()
    time.sleep(5)

    print("Read and Add")
    powerOffOn()

    remove_list=[]
    if activities==1:
        ElementsList=readLogfile(apk, "-"+str(activity_counter))
    else:
        ElementsList=readLogfile(apk)
    #Fix the timeStamp 
    timeStamp=time.time() - start_time - countSleepTime
    ElementsList=addTimestamptoElements(ElementsList,timeStamp)

    if traversal=="BFS":
        print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
        addToQueue(ElementsList,[])
        printTmpList(BFSQueue)
    elif traversal=="DFS":
        print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
        addToDFSQueue(ElementsList,[])
        printTmpList(DFSQueue)

def doStuffScroll():
    os.system(shellCommand+"input touchscreen swipe "+str(300)+" "+str(int(display[1])-300)+" "+str(300)+" "+str(300)+" 1200 > /dev/null 2>&1")

def doStuff(UIelement, elemDict, start_time, hasContext):
    global GMSQueue
    os.system(shellCommand + f" \"su -c 'echo com.google.android.gms >> /data/data/reaper.UIHarvester/current_app'\"")

    time.sleep(2)

    setLogcatDate()

    click(UIelement[1], UIelement[2], UIelement[4])

    powerOffOn()

    time.sleep(1)

    ElementsList=readLogfile("com.google.android.gms")
    timeStamp=time.time() - start_time - countSleepTime
    ElementsList=addTimestamptoElements(ElementsList,timeStamp)

    os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

    if not ElementsList:
        os.system(shellCommand + f" \"su -c 'echo android >> /data/data/reaper.UIHarvester/current_app'\"")

        powerOffOn()

        time.sleep(3)

        ElementsList=readLogfile("android")
        timeStamp=time.time() - start_time - countSleepTime
        ElementsList=addTimestamptoElements(ElementsList,timeStamp)

        os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

        if not ElementsList:
            bringToFront(start_time, elemDict)
            if not elemDict == None:
                removeFromQueue(elemDict['TimeStamp'], elemDict['TimeStampWithClicksTime'])
            readAndAdd(start_time)
            return 1

    print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
    addToGMSQueue(ElementsList,[])
    printTmpList(GMSQueue)

    signIn = 0

    for UIelement in GMSQueue:
        Class = UIelement[4]["Object getClass"].strip().replace('\n','')
        text = UIelement[4]["Text"].strip().replace('\n','')
        resource_id = UIelement[4]["ResourceId"].strip().replace('\n','')

        if text == "null":
            text = UIelement[4]["getChildText"].strip().replace('\n','')

        if Class=="android.widget.Button" and text=="Continue":
            click(UIelement[1], UIelement[2], UIelement[4])
            signIn=1
            break

        if resource_id=="agree_and_share_button" and text=="Agree and share":
            click(UIelement[1], UIelement[2], UIelement[4])
            signIn=1
            break

    ############# 2 webview round of sso ##############

    time.sleep(2)

    doStuffScroll()

    os.system(shellCommand + f" \"su -c 'echo com.google.android.gms >> /data/data/reaper.UIHarvester/current_app'\"")

    time.sleep(2)

    powerOffOn()

    time.sleep(1)

    ElementsList=readLogfile("com.google.android.gms")
    timeStamp=time.time() - start_time - countSleepTime
    ElementsList=addTimestamptoElements(ElementsList,timeStamp)

    os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

    if not ElementsList:
        bringToFront(start_time, elemDict)
        if not elemDict == None:
            removeFromQueue(elemDict['TimeStamp'], elemDict['TimeStampWithClicksTime'])
        readAndAdd(start_time)
        return 1

    GMSQueue = []
    print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
    addToGMSQueue(ElementsList,[])
    printTmpList(GMSQueue)

    signIn = 0

    for UIelement in GMSQueue: 
        Class = UIelement[4]["Object getClass"].strip().replace('\n','')
        text = UIelement[4]["Text"].strip().replace('\n','')

        if text == "null":
            text = UIelement[4]["getChildText"].strip().replace('\n','')

        if Class=="android.widget.Button" and text=="Allow":
            click(UIelement[1], UIelement[2], UIelement[4])
            signIn=1
            break

        if Class=="android.widget.Button" and text=="Continue":
            click(UIelement[1], UIelement[2], UIelement[4])
            signIn=1
            break

    if not elemDict == None:
        removeFromQueue(elemDict['TimeStamp'], elemDict['TimeStampWithClicksTime'])

    readAndAdd(start_time)

    return signIn

def googleSSOrandom(start_time):
    global countSleepTime
    global google_sso_error_counter

    os.system(shellCommand + f" \"su -c 'echo com.google.android.gms >> /data/data/reaper.UIHarvester/current_app'\"")

    powerOffOn()

    time.sleep(3)

    ElementsList=readLogfile("com.google.android.gms")
    timeStamp=time.time() - start_time - countSleepTime
    ElementsList=addTimestamptoElements(ElementsList,timeStamp)

    os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

    if not ElementsList:
        os.system(shellCommand + f" \"su -c 'echo android >> /data/data/reaper.UIHarvester/current_app'\"")

        powerOffOn()

        time.sleep(3)

        ElementsList=readLogfile("android")
        timeStamp=time.time() - start_time - countSleepTime
        ElementsList=addTimestamptoElements(ElementsList,timeStamp)

        os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

        if not ElementsList:
            return 0

    print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
    addToGMSQueue(ElementsList,[])
    printTmpList(GMSQueue)

    time.sleep(1)

    OK_Element = None;
    radio_is_clicked = False;

    for UIelement in GMSQueue:
        resource_id = UIelement[4]["ResourceId"].strip().replace('\n','')
        Class = UIelement[4]["Object getClass"].strip().replace('\n','')
        text = UIelement[4]["Text"].strip().replace('\n','')

        if text == "null":
            text = UIelement[4]["getChildText"].strip().replace('\n','')

        if (resource_id=="button1" or resource_id=="button2") and text=="OK":
            OK_Element = UIelement
            if radio_is_clicked:
                return doStuff(OK_Element, None, start_time, 1)

        if resource_id=="account_name" or (resource_id=="container" and not text=="Add another account"):
            name_element = UIelement#click(UIelement[1], UIelement[2], UIelement[4])
            doStuff(name_element, None, start_time, 1)

            return 1

        if Class=="android.widget.Button" and text=="Continue":
            click(UIelement[1], UIelement[2], UIelement[4])
            # removeFromQueue(elemDict['TimeStamp'], elemDict['TimeStampWithClicksTime'])
            readAndAdd(start_time)
            
            return 1

        if Class=="android.widget.Button" and resource_id=="continue_as_button":
            click(UIelement[1], UIelement[2], UIelement[4])
            # removeFromQueue(elemDict['TimeStamp'], elemDict['TimeStampWithClicksTime'])
            readAndAdd(start_time)
            
            return 1

        if Class=="android.widget.TextView" and (resource_id=="credential_primary_label" or resource_id=="credential_secondary_label"):
            name_element = UIelement
            doStuff(name_element, None, start_time, 1)
            
            return 1

        if resource_id=="text1" and not text=="Add account":
            click(UIelement[1], UIelement[2], UIelement[4])
            radio_is_clicked = True

            if OK_Element != None:
                return doStuff(OK_Element, None, start_time, 1)

    if google_sso_error_counter >= 2:
        return 0
    google_sso_error_counter+=1
    return 0

def googleSSO(Queue, start_time, instant_click=0):
    global countSleepTime
    global google_sso_error_counter

    for UIelement in Queue:
        x               = UIelement[1]#X coord
        y               = UIelement[2]#Y coord
        elemreplaypath  = UIelement[3]#replay path
        elemDict        = UIelement[4]#dictionary of element
    
        pretty_text = elemDict['Text'].lower().strip().replace('\n','')
        if pretty_text=="null" or pretty_text=="":
            pretty_text = elemDict['getContentDescription'].lower().strip().replace('\n','')

        if ("sign up with google" in pretty_text or "continue with google" in pretty_text or \
            "sign in with google" in pretty_text or "log in with google" in pretty_text or \
            "login with google" in pretty_text or "connect with google" in pretty_text):

            os.system(shellCommand + f" \"su -c 'echo com.google.android.gms >> /data/data/reaper.UIHarvester/current_app'\"")

            time.sleep(1)

            if not elemreplaypath or instant_click:
                click(x,y,elemDict)
            else:               
                replay(elemreplaypath)
                click(x,y,elemDict)

            time.sleep(1)

            ElementsList=readLogfile("com.google.android.gms")
            timeStamp=time.time() - start_time - countSleepTime
            ElementsList=addTimestamptoElements(ElementsList,timeStamp)

            os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

            if not ElementsList:
                os.system(shellCommand + f" \"su -c 'echo android >> /data/data/reaper.UIHarvester/current_app'\"")

                powerOffOn()

                time.sleep(3)

                ElementsList2=readLogfile("android")
                timeStamp=time.time() - start_time - countSleepTime
                ElementsList2=addTimestamptoElements(ElementsList2,timeStamp)

                os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

                if not ElementsList2:
                    # Maybe use other functionality for google sso (2 attempts)
                    if google_sso_error_counter >= 2:
                        return -1
                    google_sso_error_counter+=1
                    bringToFront(start_time, elemDict)
                    return 0

                ElementsList = ElementsList2

            print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
            addToGMSQueue(ElementsList,[])
            printTmpList(GMSQueue)

            time.sleep(1)

            OK_Element = None;
            radio_is_clicked = False;

            for UIelement in GMSQueue:
                resource_id = UIelement[4]["ResourceId"].strip().replace('\n','')
                Class = UIelement[4]["Object getClass"].strip().replace('\n','')
                text = UIelement[4]["Text"].strip().replace('\n','')

                if text == "null":
                    text = UIelement[4]["getChildText"].strip().replace('\n','')

                if resource_id=="button1" and text=="OK":
                    OK_Element = UIelement
                    if radio_is_clicked:
                        return doStuff(OK_Element, elemDict, start_time, 1)

                if resource_id=="account_name" or (resource_id=="container" and not text=="Add another account"):
                    name_element = UIelement#click(UIelement[1], UIelement[2], UIelement[4])
                    doStuff(name_element, elemDict, start_time, 1)

                    return 1

                if Class=="android.widget.Button" and text=="Continue":
                    click(UIelement[1], UIelement[2], UIelement[4])
                    removeFromQueue(elemDict['TimeStamp'], elemDict['TimeStampWithClicksTime'])
                    readAndAdd(start_time)
                    
                    return 1

                if Class=="android.widget.Button" and resource_id=="continue_as_button":
                    click(UIelement[1], UIelement[2], UIelement[4])
                    removeFromQueue(elemDict['TimeStamp'], elemDict['TimeStampWithClicksTime'])
                    readAndAdd(start_time)

                    return 1

                if Class=="android.widget.TextView" and (resource_id=="credential_primary_label" or resource_id=="credential_secondary_label"):
                    name_element = UIelement
                    doStuff(name_element, elemDict, start_time, 1)
                    
                    return 1

                if resource_id=="text1" and not text=="Add account":
                    click(UIelement[1], UIelement[2], UIelement[4])
                    radio_is_clicked = True

                    if OK_Element != None:
                        return doStuff(OK_Element, elemDict, start_time, 1)

            if google_sso_error_counter >= 2:
                return -1
            google_sso_error_counter+=1
            return 0

    return 0

def grantRunTimeConsentDialogue(Queue):
    hasRunTimeConsentDialogue=0
    hasAgreeButton = 0
    isChildTexts = []
    isClicked = {}
    maxRunTimeConsentDialogueButtonLen = 37
    escapeWords = ["continue with", "not", "dont", "don't", "doesnt", "your", "you", "Do I have to consent to everything?", "Continue as guest"]
    agreeButtons = []

    for element in Queue:

        if (element["Text"] == "null" or element["Text"].strip() == "") and (element["getChildText"] == "null" or element["getChildText"].strip() == ""):
            continue

        tmp = 0
        text = element["Text"]

        if (element["Text"] == "null" or element["Text"].strip() == ""):
            text = element["getChildText"]
            tmp = 1

        pretty_text = text.lower().strip().replace('\n','').replace('\'','').replace('\"','').replace('.','').replace(',','').replace('!','').replace('?','').replace(':','').replace(';','')
        pretty_text_arr=pretty_text.split()

        if any(word in dialogueList for word in pretty_text_arr):
            hasRunTimeConsentDialogue = 1

        if any(word in consentList for word in pretty_text_arr) and checkIfClickable(element)==1 and \
            len(pretty_text)<maxRunTimeConsentDialogueButtonLen and not any(word in pretty_text for word in escapeWords):
            hasAgreeButton = 1
            agreeButtons.append(element)

            if tmp:
                isChildTexts.append(1)
            else:
                isChildTexts.append(0)

    if hasRunTimeConsentDialogue and hasAgreeButton:
        print("Consent Click_________________________________________________________")
        jj=0
        for agreeButton in agreeButtons:
            if isChildTexts[jj]:
                click(agreeButton["childX"], agreeButton["childY"], agreeButton)
            else:
                click(int(agreeButton['Coords'].split()[0]), int(agreeButton['Coords'].split()[1]), agreeButton)
            jj+=1


def dowebviewswait():
    global webviewswait
    if webviewswait == 0:
        return

    print("Waiting for webviews to load...")
    command=adbCommand+"logcat -d -T '"+lwebviewdate.replace("\r", "")+"' | grep 'UI-LoadedWebviews'"
    count = 0
    badcount = 0
    start_time = time.time()
    while True:
        proc  = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        try:
            (res, err) = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            print("Timeout")
            badcount += 1
            count += 1
            if count > 100 or badcount > 6:
                print("Come on!")
                break
        lst = res.decode('ascii').split("\n")
        #Removes the last one element -> ''
        lst.pop()

        if (time.time() - start_time) > 60:
            break

        count += 1
        if count > 100 or badcount > 6:
            print("Come on!")
            break
        if len(lst) == 0:
            continue

        if len(lst) == 1:
            if lst[0].split("UI-LoadedWebviews: ")[1] == "Init":
                break

        if len(lst) == 2:
            if lst[0].split("UI-LoadedWebviews: ")[1] == "Init" and lst[1].split("UI-LoadedWebviews: ")[1] == "Init":
                break

        if lst[-1].split("UI-LoadedWebviews: ")[1] == "0":
            continue

def getCustomTabElements(default_browser, start_time, elemDict, replayPath, ViewCounter):
    os.system(shellCommand + f" \"su -c 'echo {default_browser} >> /data/data/reaper.UIHarvester/current_app'\"")

    powerOffOn()

    time.sleep(3)

    if activities==1:
        ElementsList=readLogfile(default_browser, "-"+str(activity_counter))
    else:
        ElementsList=readLogfile(default_browser)
    timeStamp=time.time() - start_time - countSleepTime
    ElementsList=addTimestamptoElements(ElementsList,timeStamp)

    os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")

    #Remove the extra one that was pressed
    for item in ElementsList:
        if item['isPressed']=="1" and item['ResourceId']==elemDict['ResourceId'] and item['Object getClass']==elemDict['Object getClass']:
            #Remove all the same occurances from the list
            ElementsList= [a for a in ElementsList if a != item]
    
    #Remove the ones that have been already found
    for item in ElementsList:
        if existsInQueue(item['Hash'])==1:
            #Remove all the same occurances from the list
            ElementsList= [a for a in ElementsList if a != item]
    
    #Add the number of ***ONLY*** new UIelements to Elements-Yield feature
    k = set(list([i['Hash'] for i in ElementsList]))
    elemDict['Elements-Yield']=len(k)
    
    
    #If click did not produce new elements the ElementsList is empty
    if not ElementsList:
        print(bcolors.WARNING + "ElementsList is empty." + bcolors.ENDC+ '.')
    else:
        ViewCounter+=1
        addToQueue(ElementsList,replayPath)

    printTmpList(BFSQueue)

def bringToFront(start_time, elemDict, replayPath=[], ViewCounter=0):
    global logcatRandomTag
    global countSleepTime
    global googleLoggedIn
    #Check if package is in foreground else goBack
    
    #I remove the 'windows' argument after window
    proc = subprocess.Popen([shellCommand+" dumpsys activity activities | grep -E 'mFocusedApp'"], stdout=subprocess.PIPE, shell=True)
    (foreground, err) = proc.communicate()
    foreground = foreground.decode('utf-8').replace("\n", "")
    if(apk not in foreground):
        if googleLoggedIn==0 and google_sso==1:
            googleLoggedIn = googleSSOrandom(start_time)

        if "org.chromium.chrome/.browser.customtabs.CustomTabActivity" in foreground:
            getCustomTabElements("org.chromium.chrome", start_time, elemDict, replayPath, ViewCounter)
        elif "com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabActivity" in foreground:
            getCustomTabElements("com.android.chrome", start_time, elemDict, replayPath, ViewCounter)
        
        print(bcolors.OKGREEN + "Bring to front / Clear logcat" + bcolors.ENDC + '.')
        #goBack()
        os.system(shellCommand+"logcat -c")
        setLogcatDate()
        logcatRandomTag="Frida-Bridge"+id_generator()
        #Print logcatRandomTag to logcat
        os.system(shellCommand+"log -p v -t Frida-Bridge"+logcatTag+" "+logcatRandomTag+"")
        os.system(shellCommand+'log -p d -t UI-LoadedWebviews "Init"')
        time.sleep(sleepTime)
        countSleepTime+=sleepTime
    ###############################################
#End

def click(x,y,elemDict):
    global countSleepTime
    global eventsFired

    # Crop to activity na exei mono to package_name kai des an einai idio me auto -> /data/data/reaper.UIHarvester/current_app, an oxi tote to
    # app den anoikse kai ftiakse ena arxeio noSpawn px sto folder kai termatise to

    dowebviewswait()
    setWebviewLogcatDate()

    os.system(shellCommand+'log -p d -t UI-LoadedWebviews "Init"')

    txt = elemDict['Text']

    if elemDict['Text'] == "null" and elemDict['getChildText'] != "null" and elemDict['getChildText'] != "":
        txt = elemDict['getChildText']
        x = elemDict['childX']
        y = elemDict['childY']

    if int(x)>int(display[0]) or int(y)>int(display[1]) or int(y)<0 or int(x)<0:#perform scroll
        (x,y,elemDict)=scroll(int(x),int(y),int(display[0]),int(display[1]),elemDict)
    
    print(bcolors.HEADER + "Click: " + bcolors.OKBLUE + str(x)+" "+str(y) +","+bcolors.HEADER+" Text:"+ bcolors.ENDC+"["+str(txt)+"]"+ bcolors.ENDC)
    os.system(shellCommand+"input tap "+str(x)+" "+str(y)+" > /dev/null 2>&1")
    
    time.sleep(sleepTime)
    countSleepTime+=sleepTime
    eventsFired+=1
#End

def clickNoTime(x,y,elemDict,verbose):
    global countSleepTime
    global eventsFired
    if int(x)>int(display[0]) or int(y)>int(display[1]) :#perform scroll
                (x,y,elemDict)=scroll(int(x),int(y),int(display[0]),int(display[1]),elemDict)
    
    if verbose==1:
        print(bcolors.HEADER + "Click: " + bcolors.OKBLUE + str(x)+" "+str(y) +","+bcolors.HEADER+" Text:"+ bcolors.ENDC+"["+str(elemDict['Text'])+"]"+ bcolors.ENDC)
    os.system(shellCommand+"input tap "+str(x)+" "+str(y)+" > /dev/null 2>&1")
    time.sleep(sleepTime)
    eventsFired+=1
#End

def powerOffOn():
    pass
    # global countSleepTime
    #Power off and on the display and read logcat again to get the new coords of the item
    # time.sleep(0.2)
    # os.system(shellCommand+"input keyevent 26> /dev/null 2>&1");
    # time.sleep(1)
    # os.system(shellCommand+"input keyevent 26> /dev/null 2>&1");
    # time.sleep(1.8)
    #countSleepTime+=3
#End

def powerOffOnNoTime():
    pass
    #Power off and on the display and read logcat again to get the new coords of the item
    # time.sleep(0.2)
    # os.system(shellCommand+"input keyevent 26> /dev/null 2>&1");
    # time.sleep(0.2)
    # os.system(shellCommand+"input keyevent 26> /dev/null 2>&1");
    # time.sleep(0.2)
#End

def scroll(x,y,displayX,displayY,elemDict):
    global countSleepTime
    global eventsFired
    corner=230
    verticalCorner = 130
    print(bcolors.HEADER + "Scrolling: [" + bcolors.ENDC, end=' ')
    if x < 0:
        verticalSwipes=math.floor((x)/displayX);i=1
    else:
        verticalSwipes=int((x)/displayX);i=1
    if y < 0:
        horizontalSwipes=math.floor((y)/displayY);i=1
    else:
        horizontalSwipes=int((y)/displayY);i=1
    print("Vertical * "+str(verticalSwipes)+" and ", end=' ')
    print("Horizontal * "+str(horizontalSwipes)+"]", end=' ')

    dowebviewswait()
    setWebviewLogcatDate()
    os.system(shellCommand+'log -p d -t UI-LoadedWebviews "Init"')

    constantX = x+3
    if constantX>displayX:
        constantX = displayX-10
    elif constantX<0:
        constantX = 10

    constantY = y+3
    if constantY>displayY:
        constantY = displayY-10
    elif constantY<0:
        constantY = 10

    if horizontalSwipes<0:
        horizontalSwipes=horizontalSwipes*(-1)
        while i<=horizontalSwipes:
            os.system(shellCommand+"input touchscreen swipe "+str(constantX)+" "+str(corner)+" "+str(constantX)+" "+str(displayY-corner)+" 1200 > /dev/null 2>&1")
            i=i+1
            eventsFired+=1
    else:
        #Scroll horizontal
        while i<=horizontalSwipes:
            os.system(shellCommand+"input touchscreen swipe "+str(constantX)+" "+str(displayY-corner)+" "+str(constantX)+" "+str(corner)+" 1200 > /dev/null 2>&1")
            i=i+1
            eventsFired+=1
    
    i=1

    if verticalSwipes<0:
        verticalSwipes=verticalSwipes*(-1)
        while i<=verticalSwipes:
            os.system(shellCommand+"input touchscreen swipe "+str((verticalCorner))+" "+str(constantY)+" "+str(displayX-verticalCorner)+" "+str(constantY)+" 1200 > /dev/null 2>&1")
            i=i+1
            eventsFired+=1
    else:
        #Scroll Vertical
        while i<=verticalSwipes:
            os.system(shellCommand+"input touchscreen swipe "+str((displayX-verticalCorner))+" "+str(constantY)+" "+str(verticalCorner)+" "+str(constantY)+" 1200 > /dev/null 2>&1")
            i=i+1
            eventsFired+=1

    time.sleep(1.5)
    powerOffOn()
    
    setLogcatDate()
    global logcatRandomTag
    #Create new logcatRandomTag
    logcatRandomTag=logcatRandomTag="Frida-Bridge"+id_generator()
    #Print logcatRandomTag to logcat
    os.system(shellCommand+"log -p v -t Frida-Bridge"+logcatTag+" "+logcatRandomTag+"")

    #Power off and on the display and read logcat again to get the new coords of the item
    

    time.sleep(1.5)
    
    #Read Logfile
    if activities==1:
        tmpList=readLogfile(apk, "-"+str(activity_counter))
    else:
        tmpList=readLogfile(apk)

    for item in tmpList:
        try:
            if not "Object getClass" in item:
                print("Is Web Element")
                continue

            if  item['Object getClass']==elemDict['Object getClass'] and \
                item['ResourceId']==elemDict['ResourceId'] and \
                item['Text']==elemDict['Text'] and \
                item['getContentDescription']==elemDict['getContentDescription'] and \
                item['getChildText']==elemDict['getChildText'] and \
                item['getTag']==elemDict['getTag']:

                if item['Coords'].split()[0] < 0:
                    x=item['Coords'].split()[0]
                if item['Coords'].split()[1] < 0:
                    y=item['Coords'].split()[1]
                break;
        except:
            pass
    return (x,y,elemDict)
#End

def goBack():
    global countSleepTime
    print(bcolors.HEADER + "GoBack"+ bcolors.ENDC + '.')
    os.system(shellCommand+"input keyevent KEYCODE_BACK > /dev/null 2>&1")
    time.sleep(sleepTime)
    countSleepTime+=sleepTime
    print(bcolors.HEADER + "Done" + bcolors.ENDC)
#End

def clickSettings():
    global countSleepTime
    print(bcolors.HEADER + "click Settings"+ bcolors.ENDC + '.')
    os.system(shellCommand+"input keyevent KEYCODE_MENU > /dev/null 2>&1")
    time.sleep(sleepTime)
    countSleepTime+=sleepTime
    print(bcolors.HEADER + "Done" + bcolors.ENDC)
#End

def image_to_hash(image_path):
    image = Image.open(image_path)

    # Convert to grayscale
    image = image.convert('L')

    # Resize to a standard size
    image = image.resize((8, 8))

    # Generate perceptual hashes
    hash1 = imagehash.dhash(image)

    return str(hash1)

def screenshot_activity(name):
    time.sleep(2)
    os.system(shellCommand+" screencap -p > "+path+"/"+name+".png")
    time.sleep(4)

def delete_screenshot_activity(name):
    os.system("rm -rf "+path+"/"+name+".png")

def addtoDict(activity, action="", data=""):
    if not activity in activity_dict:
        activity_dict[activity] = {}

    if not action in activity_dict[activity]:
        activity_dict[activity][action] = []

    if not data in activity_dict[activity][action]:
        activity_dict[activity][action].append(data)

def makeUrl(scheme="", host="", path=""):
    url=""
    if scheme!="" and host!="":
        url=scheme+"://"+host
    elif scheme!="":
        url=scheme
    else:
        url=host

    url+=path

    return url


def checkData(dataItem, HOST, SCHEME, TAG):
    if '@'+TAG+':pathPattern' in dataItem:
        path="";scheme=SCHEME;host=HOST;
        if '@'+TAG+':scheme' in dataItem:

            scheme=dataItem['@'+TAG+':scheme']
        if '@'+TAG+':host' in dataItem:

            host=dataItem['@'+TAG+':host']
        

        return makeUrl(scheme=ref_to_string(scheme), host=ref_to_string(host), path=ref_to_string(dataItem['@'+TAG+':pathPattern']))
    if '@'+TAG+':pathPrefix' in dataItem:
        path="";scheme=SCHEME;host=HOST;
        if '@'+TAG+':scheme' in dataItem:

            scheme=dataItem['@'+TAG+':scheme']
        if '@'+TAG+':host' in dataItem:

            host=dataItem['@'+TAG+':host']
        

        return makeUrl(scheme=ref_to_string(scheme), host=ref_to_string(host), path=ref_to_string(dataItem['@'+TAG+':pathPrefix']))
    if '@'+TAG+':path' in dataItem:
        path="";scheme=SCHEME;host=HOST;
        if '@'+TAG+':scheme' in dataItem:

            scheme=dataItem['@'+TAG+':scheme']
        if '@'+TAG+':host' in dataItem:

            host=dataItem['@'+TAG+':host']
        

        return makeUrl(scheme=ref_to_string(scheme), host=ref_to_string(host), path=ref_to_string(dataItem['@'+TAG+':path']))

def ref_to_bool(item):
    if "@bool/" in item and os.path.exists("./BASE/res/values/bools.xml"):
        item=item.split("@bool/")[1]
        with open("./BASE/res/values/bools.xml") as f:
            bool_dict = xmltodict.parse(f.read())

        for xml_item in bool_dict['resources']['bool']:
            if xml_item['@name'] == item:
                return xml_item['#text']

    return item

def ref_to_string(item):
    if "@string/" in item and os.path.exists("./BASE/res/values/strings.xml"):
        item=item.split("@string/")[1]
        with open("./BASE/res/values/strings.xml") as f:
            string_dict = xmltodict.parse(f.read())

        for xml_item in string_dict['resources']['string']:
            if xml_item['@name'] == item:
                return xml_item['#text']

    return item

def getActivityList():
    if not os.path.exists("./BASE/AndroidManifest.xml"):
        return []

    with open("./BASE/AndroidManifest.xml") as f:
        xml_dict = xmltodict.parse(f.read())

    for item in xml_dict['manifest']['application']['activity']:
        r = re.compile("@.*exported")
        exported_name=""
        newlist = list(filter(r.match, item))
        if len(newlist)>0:
            exported_name=newlist[0]
            TAG = exported_name.replace("@","").replace(":exported","")

        if exported_name!="" and ref_to_bool(item[exported_name]) == "true":
            addtoDict(item['@'+TAG+':name'])
            if 'intent-filter' in item:
                if isinstance(item['intent-filter'], list):
                    for intentItem in item['intent-filter']:
                        HOST=""
                        SCHEME=""
                        ACTIONS=[]
                        if 'action' in intentItem:
                            if isinstance(intentItem['action'], list):
                                for actionItem in intentItem['action']:
                                    addtoDict(item['@'+TAG+':name'], actionItem['@'+TAG+':name'])
                                    ACTIONS.append(actionItem['@'+TAG+':name'])
                            else:
                                addtoDict(item['@'+TAG+':name'], intentItem['action']['@'+TAG+':name'])
                                ACTIONS.append(intentItem['action']['@'+TAG+':name'])
                        
                        if 'data' in intentItem:
                            if isinstance(intentItem['data'], list):
                                for dataItem in intentItem['data']:
                                    if '@'+TAG+':host' in dataItem and not ('@'+TAG+':pathPattern' in dataItem or '@'+TAG+':pathPrefix' in dataItem or '@'+TAG+':path' in dataItem) and HOST=="":
                                        HOST=dataItem['@'+TAG+':host']
                                    if "@'+TAG+':scheme" in dataItem and not ('@'+TAG+':pathPattern' in dataItem or '@'+TAG+':pathPrefix' in dataItem or '@'+TAG+':path' in dataItem) and SCHEME=="":
                                        SCHEME=dataItem['@'+TAG+':scheme']
                                    url = checkData(dataItem, HOST, SCHEME, TAG)
                                    for ACTION in ACTIONS:
                                        addtoDict(item['@'+TAG+':name'], ACTION, url)
                            else:
                                url = checkData(intentItem['data'], HOST, SCHEME, TAG)
                                for ACTION in ACTIONS:
                                    addtoDict(item['@'+TAG+':name'], ACTION, url)
                else:
                    HOST=""
                    SCHEME=""
                    ACTIONS=[]
                    if 'action' in item['intent-filter']:
                        if isinstance(item['intent-filter']['action'], list):
                            for actionItem in item['intent-filter']['action']:
                                addtoDict(item['@'+TAG+':name'], actionItem['@'+TAG+':name'])
                        else:
                            addtoDict(item['@'+TAG+':name'], item['intent-filter']['action']['@'+TAG+':name'])
                    
                    if 'data' in item['intent-filter']:
                        if isinstance(item['intent-filter']['data'], list):
                            for dataItem in item['intent-filter']['data']:
                                if '@'+TAG+':host' in dataItem and not ('@'+TAG+':pathPattern' in dataItem or '@'+TAG+':pathPrefix' in dataItem or '@'+TAG+':path' in dataItem) and HOST=="":
                                    HOST=dataItem['@'+TAG+':host']
                                if "@'+TAG+':scheme" in dataItem and not ('@'+TAG+':pathPattern' in dataItem or '@'+TAG+':pathPrefix' in dataItem or '@'+TAG+':path' in dataItem) and SCHEME=="":
                                    SCHEME=dataItem['@'+TAG+':scheme']
                                url = checkData(dataItem, HOST, SCHEME, TAG)
                                for ACTION in ACTIONS:
                                    addtoDict(item['@'+TAG+':name'], ACTION, url)
                        else:
                            url = checkData(item['intent-filter']['data'], HOST, SCHEME, TAG)
                            for ACTION in ACTIONS:
                                addtoDict(item['@'+TAG+':name'], ACTION, url)



    lst=[]
    for k,v in activity_dict.items():
        cmd=""
        for k2,v2 in v.items():
            for v3 in v2:
                if v3!='' and v3!=None:
                    cmd=k+","+k2+","+v3
                else:
                    cmd=k+","+k2
                if cmd.endswith("/"):
                    cmd = cmd[:-1]
                if not cmd in lst:
                    if not (k+"," in lst and k2=='android.intent.action.VIEW' and (v3==None or v3=='')):
                        lst.append(cmd)

    return lst

def initActivities():
    global countSleepTime
    global activity_counter

    start_time = time.time()
    
    ActivityAlreadyOnForegroundMessage="Warning: Activity not started, intent has been delivered to currently running top-most instance."
    WARNING=0
    os.system("rm -rf BASE")
    os.system("rm -rf BASE.apk")

    activities_map = {}
    activities_hashes=[]

    print(bcolors.OKGREEN+"Analyzing apk..."+bcolors.ENDC)
    proc  = subprocess.Popen([shellCommand+f"pm path {apk}"], stdout=subprocess.PIPE, shell=True)
    (paths, err) = proc.communicate()
    paths = paths.decode('utf-8').replace("package:", "").split("\n")
    os.system(adbCommand+f"pull {paths[0]} ./BASE.apk")

    apktool  = subprocess.Popen(["apktool d -o BASE BASE.apk"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) #--no-src -s, is faster but some references of strings are from other lib sources
    (info, apktool_err) = apktool.communicate()

    if apktool_err!=None and apktool_err.decode('utf-8').strip().replace("\n","")!="":
        os.system("echo \"Analysis of this app with option --activities may be limited.\" > "+path+"/Activities/warning")
        with open(path+"/Activities/warning", "a+") as activities_folder_file:
            activities_folder_file.write(apktool_err.decode('utf-8'))
        WARNING=1

    activity_list = getActivityList()

    os.system("touch "+path+"/Activities/all_activities")
    with open(path+"/Activities/all_activities", "a+") as activities_folder_file:
        for tmp in activity_list:
            activities_folder_file.write(tmp+"\n")
    
    os.system("rm -rf BASE")
    os.system("rm -rf BASE.apk")

    print(bcolors.OKGREEN+"Done"+bcolors.ENDC+".")

    activity_list.insert(0, "MainActivity,")

    counter=-1

    for activity_action_data in activity_list:
        counter+=1
        activity_counter = counter

        tmp=activity_action_data.split(",")
        activity = tmp[0]
        action = ""
        data=""
        currentTime=0

        if len(tmp)>1:
            action = tmp[1] 
        if len(tmp)>2:
            data = tmp[2]

        activity = activity.replace("$","\\$")
        if apk in activity:
            activity = activity.replace(apk,apk+"/")
        else:
            activity = apk+"/"+activity

        data_cmd=""
        action_cmd=""

        if action!="":
            action_cmd = f"-a {action}"
        if data!="":
            data_cmd = f"-d '{data}'"

        startAppandWaitforMainActivity(apk)

        if counter>0:
            proc  = subprocess.Popen([shellCommand+f"am start -n '{activity}' {action_cmd} {data_cmd}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (running_activity, err) = proc.communicate()

            time.sleep(2)

        ####
        os.system(shellCommand + " \"su -c 'touch /data/data/reaper.UIHarvester/current_app'\"")
        os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")
        ####  

        activity_folder_name = path+"/Activities/Activity-"+str(counter)
        os.system(f"mkdir {activity_folder_name}")

        proc = subprocess.Popen([shellCommand+" dumpsys activity activities | grep -E 'mFocusedApp' | cut -d ' ' -f 2- | awk '{print $3}' | sed 's\\}\\\\'"], stdout=subprocess.PIPE, shell=True)
        (foreground, err2) = proc.communicate()
        foreground = foreground.decode('utf-8').replace("\n", "")

        accessed_activity = foreground

        os.system("touch "+activity_folder_name+"/details")
        with open(activity_folder_name+"/details", "w") as activity_folder_file:
            activity_folder_file.write(f"Activity Requested: {activity} {action} {data}\n")
            activity_folder_file.write(f"Activity Accessed: {accessed_activity}")

        if counter>0 and err!=None and err.decode('utf-8').replace("\n","")!="" and err.decode('utf-8').replace("\n","")!=ActivityAlreadyOnForegroundMessage:
            print(bcolors.WARNING+"Error activity: "+bcolors.ENDC+activity+bcolors.WARNING+" can't open."+bcolors.ENDC)
            os.system("touch "+activity_folder_name+"/error")
            with open(activity_folder_name+"/error", "w") as activity_folder_file:
                activity_folder_file.write(err.decode('utf-8'))
            killApp()
            continue
        
        if(apk not in foreground and not "org.chromium.chrome/.browser.customtabs.CustomTabActivity" in foreground and \
            not "com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabActivity" in foreground):
            print(bcolors.WARNING+"Error activity: "+bcolors.ENDC+activity+bcolors.WARNING+" can't open."+bcolors.ENDC)
            os.system("touch "+activity_folder_name+"/error")
            with open(activity_folder_name+"/error", "w") as activity_folder_file:
                activity_folder_file.write("Error: Activity doesn't open")
            killApp()
            continue

        screenshot_activity("image1")

        if not os.path.exists(path+"/image1.png") or not os.path.getsize(path+"/image1.png")>0:
            with open(activity_folder_name+"/error", "a+") as activity_folder_file:
                activity_folder_file.write("Error: Can't take a screenshot")
            delete_screenshot_activity("image1")
            continue

        imgHash = image_to_hash(path+"/image1.png")

        is_been_traversed=False

        if len(activities_hashes)==0:
            activities_hashes.append(imgHash)
        else:
            for activity_hash in activities_hashes:
                if abs(imagehash.hex_to_hash(activity_hash) - imagehash.hex_to_hash(imgHash)) < 10:
                    is_been_traversed=True
                    break

        if not is_been_traversed:
            activities_hashes.append(imgHash)
            countSleepTime=0
            if traversal=="BFS":
                #Begin BFS
                print("Begin BFS")
                if counter>0:
                    currentTime=beginBFS([activity,action_cmd,data_cmd,"-"+str(counter)])
                else:
                    currentTime=beginBFS()
                BFSQueue=[]
            elif traversal=="DFS":
                #Begin DFS
                if counter>0:
                    currentTime=beginDFS([activity,action_cmd,data_cmd,"-"+str(counter)])
                else:
                    currentTime=beginDFS()
                DFSQueue=[]
            elif traversal=="monkey" or traversal=="MONKEY":
                if counter>0:
                    currentTime=beginMonkey([activity,action_cmd,data_cmd,"-"+str(counter)])
                else:
                    currentTime=beginMonkey()
                monkeyQueue=[]
        else:
            with open(activity_folder_name+"/details", "a+") as activity_folder_file:
                activity_folder_file.write("\n[Already been traversed]")
            print(activity+bcolors.WARNING+" has already been traversed"+bcolors.ENDC)
        

        killApp()
        delete_screenshot_activity("image1")

    return time.time() - start_time

def startActivity():
    activitiesQueue.append()


def startAppandWaitforMainActivity(apk):
    global countSleepTime
    global ldate
    global isAppOpened
    global timesReopened
    global activities

    setLogcatDate()
    setWebviewLogcatDate()
    print(bcolors.HEADER + "Starting  App: "+ bcolors.ENDC +apk + bcolors.HEADER +" Activity: "+bcolors.ENDC, end=' ', flush=True)
    
    if activities==0:
        ####
        os.system(shellCommand + " \"su -c 'touch /data/data/reaper.UIHarvester/current_app'\"")
        os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")
        time.sleep(1)
        ####  

    print("Frida starting... ", end=' ', flush=True)
    #get main activity
    os.system("frida -U -f "+apk+" -l "+FRIDA_SCRIPTS_PATH+"UIHarvester.js "+fridaScripts+" >> "+path+"/frida/logfile 2>&1 &")

    #Wait for activity to launch dont wait for 10 secs
    returnCode=666
    command=adbCommand+"logcat -d -T '"+ldate.replace("\r", "")+"' |  grep -ic 'Displayed "+apk+"'"
    counter = 0 
    start_time = time.time()
    print("Waiting for app to start... ", end=' ', flush=True)
    while(returnCode!=str(1)):
        proc  = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        (returnCode, err) = proc.communicate()
        returnCode = returnCode.decode('ascii').replace("\n", "")
        counter+=1
        end_time = time.time()
        if end_time-start_time>7:
            break

    command=adbCommand+"logcat -d -T '"+ldate.replace("\r", "")+"' |  grep -ic 'Splash Screen "+apk+"'"
    counter = 0
    start_time = time.time()
    while(returnCode!=str(1)):
        proc  = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        (returnCode, err) = proc.communicate()
        returnCode = returnCode.decode('ascii').replace("\n", "")
        counter+=1
        end_time = time.time()
        if end_time-start_time>7 and returnCode!=str(1):
            isAppOpened = 1
            break

    proc  = subprocess.Popen([shellCommand+"dumpsys activity activities | grep mFocusedApp | cut -d ' ' -f 2- | awk '{print $3}' | sed 's\\}\\\\'"], stdout=subprocess.PIPE, shell=True)
    (activity, err) = proc.communicate()
    activity = activity.decode('utf-8').replace("\n", "")
    print("["+activity+"] .", end=' ')  

    #sleep sleepXforMainActivity seconds  in order to fetch dynamic contnent
    time.sleep(sleepXforMainActivity)
    countSleepTime+=sleepXforMainActivity
    print(bcolors.OKGREEN + "Done" + bcolors.ENDC)  

#End

def killApp():
  print(bcolors.HEADER + "Killing App: "+bcolors.ENDC +apk) 
  dowebviewswait()

  os.system(shellCommand + f" \"su -c 'echo 0 > /data/data/reaper.UIHarvester/current_app'\"")

  proc  = subprocess.Popen([shellCommand+"dumpsys activity activities | grep mFocusedApp | awk '{print $3}' | cut -d '/' -f 1"], stdout=subprocess.PIPE, shell=True)
  (top_app, err) = proc.communicate()
  top_app = top_app.decode('utf-8').replace("\n", "")

  os.system(shellCommand+"am force-stop "+top_app+" > /dev/null 2>&1")
  os.system(shellCommand+"am force-stop "+apk+" > /dev/null 2>&1")

  os.system('pkill -f "frida -U -f '+apk+' -l '+FRIDA_SCRIPTS_PATH+'UIHarvester.js"')
#End

def parseBase64forWeb(encodedElement):
    elementDict={}
    try:
        element=base64.b64decode(encodedElement).decode('utf-8').split('\n')
    except:
        print(encodedElement)
        print(bcolors.FAIL + "Didn't got all the data for this element from logcat" + bcolors.ENDC + '.')
        return elementDict
    
    for item in element:
        if len(item)<=1:
            continue
        tmp=item.split(":",1)

        if tmp[0] not in elementDict:
            if not "End of Node" in tmp[0] and len(tmp[0])<50:
                if tmp[0]=="class":
                    elementDict[tmp[0]]=tmp[1][1:].replace("","")
                else:
                    try:
                        elementDict[tmp[0]]=tmp[1][1:]
                    except:
                        pass
    
    
    if (len(list(elementDict.keys()))<17):
        return {}

    md5String=elementDict["class"]+\
    elementDict["getViewIdResourceName"]+\
    elementDict["Text"]+\
    elementDict["getContentDescription"]

    elementDict["Hash"]=hashlib.md5(md5String.encode('utf-8')).hexdigest()
    
    elementDict["Elements-Yield"]=0
    elementDict["ViewNumber"]="-"
    #the time that has passed in order to find the element
    elementDict["TimeStamp"]=0.0
    elementDict["TimeStampWithClicksTime"]=0.0
    return elementDict
#End

def parseBase64(encodedElement):
    elementDict={}
    try:
        element=base64.b64decode(encodedElement).decode('utf-8').split('\n')
    except:
        print(bcolors.FAIL + "Didn't got all the data for this element from logcat" + bcolors.ENDC + '.')
        return elementDict
    
    for item in element:
        if len(item)<=1:
            continue
        tmp=item.split(":",1)
    
        if tmp[0] not in elementDict:
            if tmp[0]=="Object getClass":
                elementDict[tmp[0]]=tmp[1][1:].replace("class ","")
            else:
                try:
                    elementDict[tmp[0]]=tmp[1][1:]
                except:
                    pass
    
    
    if (len(list(elementDict.keys()))<17):
        return {}
    
    if "ResourceId" in elementDict or "Text" in elementDict or "getChildText" in elementDict or "getContentDescription" in elementDict:
        getChild=""
        if "getChildText" in elementDict:
            getChild = elementDict["getChildText"]
        else:
            elementDict["getChildText"] = ""
        getContent=""
        if "getContentDescription" in elementDict:
            getContent = elementDict["getContentDescription"]
        else:
            elementDict["getContentDescription"] = ""

        if "id/" in elementDict["ResourceId"]:
            elementDict["ResourceId"] = elementDict["ResourceId"].split("id/")[1]

        md5String=elementDict["Object getClass"]+elementDict["ResourceId"]+elementDict["Text"]+getChild+getContent+elementDict["getTag"]
    else:
        elementDict["getContentDescription"] = ""
        elementDict["getChildText"] = ""
        elementDict["ResourceId"] = ""
        elementDict["Text"] = ""  
        md5String=elementDict["Object getClass"]+elementDict["getTag"]

    elementDict["Hash"]=hashlib.md5(md5String.encode('utf-8')).hexdigest()
    
    elementDict["Elements-Yield"]=0
    elementDict["ViewNumber"]="-"
    #the time that has passed in order to find the element
    elementDict["TimeStamp"]=0.0
    elementDict["TimeStampWithClicksTime"]=0.0
    return elementDict
#End

def readAfterlogcatRandomTag(activity_num=""):
    global logcatRandomTag 
    
    #Read logfile 
    command=shellCommand+"logcat -d | grep -i 'Frida-Bridge.*"+logcatTag+"' > "+path+"/UIHarvester/UIHarvesterLog"+activity_num+".tmp"
    proc  = subprocess.Popen([ command ],  stdout=subprocess.PIPE, shell=True);proc.communicate()
    
    #Create the list
    logfile=open(""+path+"/UIHarvester/UIHarvesterLog"+activity_num+".tmp","r")
    tmpList=[]
    tmp=0
    for line in logfile:
        if logcatRandomTag not in line and tmp==0:
            continue
        else:
            tmp=1

        if tmp==1:
            if " "+logcatTag in line:
                line=line.strip()
                
                ##Read after logcatTag and get the base64 part
                line=(line.split(logcatTag))[1]

                ##Remove empty lines
                if len(line)!=0:
                    tmpList.append(line)
                
                tmpList=list(set(tmpList))
                ##Remove duplicate lines    
    logfile.close()
    
    logfile=open(""+path+"/UIHarvester/UIHarvesterLog"+activity_num+"","w")
    for line in tmpList:
        print(line, file=logfile)
    logfile.close()
    
    #Create new logcatRandomTag
    logcatRandomTag=logcatRandomTag="Frida-Bridge"+id_generator()
    #Print logcatRandomTag to logcat
    os.system(shellCommand+"log -p v -t Frida-Bridge"+logcatTag+" "+logcatRandomTag+"")
#End

def readLogfile(apk, activity_num=""):
    global display
    #Reads the logcat and return a list of Dictionary elements elements
    ElementsList=[];

    ##Open logfile and read it 
    readAfterlogcatRandomTag(activity_num)


    with contextlib.redirect_stdout(None):
        print(apk+"_________________________________________________________________")

    #Create the list
    logfile=open(""+path+"/UIHarvester/UIHarvesterLog"+activity_num+"","r")
    for line in logfile:
        line=line.strip()
        
        #Parse the elements
        element=parseBase64(line)
        with contextlib.redirect_stdout(None):
            print(element)

        if len(element)>0 :
            #Only add the elements from the apk we want
            if element['currentPackageName']==apk:
                ElementsList.append(element)

    #Close the file
    logfile.close()
    
    if (display[0]==0 and display[1]==0 and ElementsList):
        #Initialize Display size
        display=(ElementsList[0]['DisplaySize'].split()[0],ElementsList[0]['DisplaySize'].split()[1])
        if int(display[0])<700 or int(display[1])<700:
            # tmp_display = os.popen(shellCommand+" dumpsys window | grep mDisplayInfo | grep -oE 'real [0-9]+ x [0-9]+' | sed 's\\real \\\\'").read() #android 11
            tmp_display = os.popen(shellCommand+"wm size | grep -oE '[0-9]+x[0-9]+'").read() 
            display=(tmp_display.split("x")[0], tmp_display.split("x")[1].replace("\n", ""))

    return ElementsList    
#End 

def printElementList(ElementsList):
    for element in ElementsList:
        print("----------------------")
        for key in element:            
            print(key+": |"+str(element[key])+"|")
        print("----------------------")
#End

def printTmpList(tmp):
    counter=0
    for i in tmp:
        print("[Hash: "+str(i[0])+"]"\
            + " [isClickable: "+ str(checkIfClickable(i[4]))+"]"\
            + " [T: "+str( "%.2f" % (i[4]['TimeStamp']))+"]"\
            + " [T2: "+str("%.2f" % (i[4]['TimeStampWithClicksTime']))+"]"\
            + " [View: "+str(i[4]['ViewNumber'])+"]"\
            + " [Elements-Yield:"+str(i[4]['Elements-Yield'])+"]"\
            + " [X:"+str(i[1])+" Y:"+str(i[2])+"]"\
            + " ChildText:["+str(i[4]['getChildText'])+"]"\
            + " Text:["+str(i[4]['Text'])+"]", end=' ')
        replaypath= i[3]
        path=[ (i[0],i[1]) for i in replaypath]
        print("Path: ",path)
        counter=counter+1
    print("Items "+str(counter))
#End

#TODO +str(" CLASS:"+i[4]["Object getClass"]+" ID:"+i[4]["ResourceId"]+" TAG:"+i[4]["getTag"])

def replay(replayPathList):  
    global countSleepTime
    time.sleep(0.5)
    countSleepTime+=0.5

    print(bcolors.OKGREEN + "[Replaying Path" + bcolors.ENDC)
  
    print(bcolors.OKGREEN + "|" + bcolors.ENDC, end=' ')
    
    for item in replayPathList:
        print(bcolors.OKGREEN + "|" + bcolors.ENDC, end=' ')
        click(item[0],item[1],item[2])
    print(bcolors.OKGREEN + "[Replaying Path Finished" + bcolors.ENDC)
    time.sleep(sleepTime)
    countSleepTime+=sleepTime
#End

def existsInGMSQueue(hashObject):
  found=0
  for item in GMSQueue:
    if item[0]==hashObject:
            found=1
  return found
#End

def existsInQueue(hashObject):
  found=0
  for item in BFSQueue:
    if item[0]==hashObject:
            found=1
  return found
#End

def existsInMonkeyQueue(hashObject):
  found=0
  for item in monkeyQueue:
    if item[0]==hashObject:
            found=1
  return found
#End

def existsInDFSQueue(hashObject):
  found=0
  for item in DFSQueue:
    if item[0]==hashObject:
            found=1
  return found
#End

def addToGMSQueue(ElementsList,replayPathtmp):
    clicksList=[]
    #Traverse the ElementsList
    for element in ElementsList:
        #Get Hash
        hashObject=element['Hash']
        clickX=element['Coords'].split()[0]
        clickY=element['Coords'].split()[1]
        
        clicksList.append((hashObject,clickX,clickY,element))
  
    #Sort the items that we will traverse in descending order based on Y axis
    clicksList.sort(key=lambda tup: ( int(tup[2]),int(tup[1]) ) )
    
    for item in clicksList:
        #Check if the  object exists in our Queue
        if existsInGMSQueue(item[0])!=1:
            GMSQueue.append((item[0],item[1],item[2],replayPathtmp,item[3]))
#End

def addToQueue(ElementsList,replayPathtmp):
    clicksList=[]
    #Traverse the ElementsList
    for element in ElementsList:
        #Get Hash
        hashObject=element['Hash']
        clickX=element['Coords'].split()[0]
        clickY=element['Coords'].split()[1]
        
        clicksList.append((hashObject,clickX,clickY,element))
  
    #Sort the items that we will traverse in descending order based on Y axis
    clicksList.sort(key=lambda tup: ( int(tup[2]),int(tup[1]) ) )
    
    for item in clicksList:
        #Check if the object exists in our Queue
        if existsInQueue(item[0])!=1:
            BFSQueue.append((item[0],item[1],item[2],replayPathtmp,item[3]))
#End

def addToDFSQueue(ElementsList,replayPathtmp,position):
    clicksList=[]
    #Traverse the ElementsList
    for element in ElementsList:
        #Get Hash
        hashObject=element['Hash']
        clickX=element['Coords'].split()[0]
        clickY=element['Coords'].split()[1]
        
        clicksList.append((hashObject,clickX,clickY,element))
  
    #Sort the items that we will traverse in descending order based on Y axis
    clicksList.sort(key=lambda tup: ( int(tup[2]),int(tup[1]) ) )
    
    for item in clicksList:
        #Check if the  object exists in our Queue
        if existsInDFSQueue(item[0])!=1:
            if position>=0:
                DFSQueue.insert( position , (item[0],item[1],item[2],replayPathtmp,item[3]))
                position+=1
            else:
                DFSQueue.append((item[0],item[1],item[2],replayPathtmp,item[3]))
#End

def addToMonkeyQueue(ElementsList,replayPathtmp):
    clicksList=[]
    #Traverse the ElementsList
    for element in ElementsList:
        #Get Hash
        hashObject=element['Hash']
        clickX=element['Coords'].split()[0]
        clickY=element['Coords'].split()[1]
        clicksList.append((hashObject,clickX,clickY,element))
  
    #Sort the items that we will traverse in descending order based on Y axis
    clicksList.sort(key=lambda tup: ( int(tup[2]),int(tup[1]) ) )
    
    for item in clicksList:
        #Check if the  object exists in our Queue
        if existsInMonkeyQueue(item[0])!=1:
            monkeyQueue.append((item[0],item[1],item[2],replayPathtmp,item[3]))
#End


def checkIfClickable(elemDict):
    if 'noClickable' in elemDict:
        if elemDict['noClickable']==str(1):
            return 0
    if 'isCheckable' in elemDict:
        if elemDict['isCheckable']==str(1):
            return 1
    if  elemDict['isClickable']==str(1) or \
        elemDict['isLongClickable']==str(1) or \
        elemDict['isContextClickable']==str(1):
        return 1
    # elif 'parentClickable' in elemDict and elemDict['parentClickable']==str(1):
    #     return 1
    elif 'hasOnClickListeners' in elemDict:
        if elemDict['hasOnClickListeners']==str(1) or \
           elemDict['isPressed']==str(1):
            return 1

    return 0
#End

def beginMonkey(lst=[]):
    #Create logcatRandomTag in order to get logcat output after this value
    global logcatRandomTag
    global countSleepTime
    global eventsFired
    global path
    
    sleepTime=0.2
    monkeyEvents=3
    countSleepTime+=sleepXforMainActivity
    setLogcatDate()
    setWebviewLogcatDate()
    logcatRandomTag="Frida-Bridge"+id_generator()
    #Print logcatRandomTag to logcat
    os.system(shellCommand+"log -p v -t Frida-Bridge"+logcatTag+" "+logcatRandomTag+"")

    proc = subprocess.Popen(["frida -U -f "+apk+" -l "+FRIDA_SCRIPTS_PATH+"UIHarvester.js "+fridaScripts+" >> "+path+"/frida/logfile 2>&1 &"], shell=True)
    proc.communicate()

    if len(lst)>0 and activities==1:
        proc  = subprocess.Popen([shellCommand+f"am start -n '{lst[0]}' {lst[1]} {lst[2]}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (running_activity, err) = proc.communicate()
        time.sleep(1)
        ####
        os.system(shellCommand + " \"su -c 'touch /data/data/reaper.UIHarvester/current_app'\"")
        os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")
        ####  
    
    #Start traversing 
    msg=""
    start_time = time.time()
    sys.stdout.write("\n")

    while(1):
        currentTime= time.time() - start_time
        
        msg = bcolors.OKBLUE+ "Exercising with Space Monkeys : "+bcolors.ENDC+"[%i of %i]" % (currentTime, int(timeout))
        sys.stdout.write(msg + chr(8) * len(msg))
        sys.stdout.flush()
        if (currentTime)>=timeout:
            print("\n")
            print(bcolors.OKGREEN +"TimeOut excited" + bcolors.ENDC)
            break
        else:

            dowebviewswait()
            setWebviewLogcatDate()
            os.system(shellCommand+'log -p d -t UI-LoadedWebviews "Init"')
            
            os.system(shellCommand+"monkey -v --throttle 500 -p "+apk+" --pct-touch 90 --pct-nav 10 "+str(monkeyEvents)+" > /dev/null 2>&1")
            eventsFired+=monkeyEvents

            time.sleep(sleepTime)
            countSleepTime+=sleepTime
            if len(lst)>0 and activities==1:
                ElementsList=readLogfile(apk, lst[3])
            else:
                ElementsList=readLogfile(apk)  
            
            ElementsList=addTimestamptoElements(ElementsList,currentTime)

            addToMonkeyQueue(ElementsList,[])


    os.system("pkill frida")
    
    return currentTime
#End

def addTimestamptoElements(ElementsList,timeStamp):
    for item in ElementsList:
        if timeStamp <=0 or timeStamp+countSleepTime <=0:
            item['TimeStamp']=0.0
            item['TimeStampWithClicksTime']=0.0
        else:
            item['TimeStamp']=timeStamp
            item['TimeStampWithClicksTime']=timeStamp+countSleepTime
    return ElementsList
#End

def clearAppData(apk):
    print(bcolors.OKGREEN+"Clearing data..."+bcolors.ENDC)
    proc = subprocess.Popen([shellCommand+"pm clear "+apk+" > /dev/null 2>&1"], stdout=subprocess.PIPE, shell=True)
    proc.communicate()

def recordRR():
    start_time = time.time()

    os.system(adbCommand + " push "+RECORD_REPLAY_PATH+"replay /data/local/tmp/")

    os.system(shellCommand+" \"su -c 'chmod +x /data/local/tmp/replay'\"")

    os.system(shellCommand+" getevent -tt > "+record_file.replace("\n","")+" &")

    print(bcolors.OKGREEN + "\nRecording is starting..." + bcolors.ENDC)

    input(bcolors.WARNING + "\nPress any button on keyboard to stop Recording..." + bcolors.ENDC)

    os.system("pkill -f '"+shellCommand+" getevent -tt'")

    os.system("echo 'total "+str(time.time() - start_time)+"' >> "+record_file)

    os.system(shellCommand+'log -p d -t UI-LoadedWebviews "Init"')

    killApp()

    return time.time() - start_time

def replayRR():

    waitForWebviewsTag="--no-wait______"
    if webviewswait == 1:
        waitForWebviewsTag="--wait-webviews"

    start_time = time.time()

    os.system("java -cp "+RECORD_REPLAY_PATH+" Translate "+replay_file.replace("\n","")+" "+path+"/RecordReplay/translatedEvents.txt")
    os.system(adbCommand+" push "+path+"/RecordReplay/translatedEvents.txt /data/local/tmp/")

    os.system(shellCommand+" \"su -c './data/local/tmp/replay ./data/local/tmp/translatedEvents.txt "+waitForWebviewsTag+"'\"")

    os.system(shellCommand+'log -p d -t UI-LoadedWebviews "Init"')

    with open(replay_file) as f:
        record_time = f.readlines()[-1].split(" ")[1].replace("\n", "")

    while(time.time() - start_time < float(record_time)):
        continue

    return time.time() - start_time

def recordAndReplay():
    
    recordRR()

    os.system(shellCommand+"am force-stop "+apk+" > /dev/null 2>&1")

    os.system('pkill -f "frida -U -f '+apk+' -l '+FRIDA_SCRIPTS_PATH+'UIHarvester.js"')

    startAppandWaitforMainActivity(apk)

    currentTime = replayRR()

    os.system(shellCommand+"am force-stop "+apk+" > /dev/null 2>&1")

    os.system('pkill -f "frida -U -f '+apk+' -l '+FRIDA_SCRIPTS_PATH+'UIHarvester.js"')

    return currentTime

def isAppSpawned():
    proc = subprocess.Popen([shellCommand+" dumpsys activity activities | grep -E 'mFocusedApp'"], stdout=subprocess.PIPE, shell=True)
    (foreground, err) = proc.communicate()
    foreground = foreground.decode('utf-8').replace("\n", "")
    if (not apk in foreground and not "org.chromium.chrome/.browser.customtabs.CustomTabActivity" in foreground and \
            not "com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabActivity" in foreground and \
            not "com.google.android.gms" in foreground):

        return 0

    return 1


def beginBFS(lst=[]):
    start_time = time.time()
    currentTime=0
    global display
    global countSleepTime
    global google_sso
    global googleLoggedIn
    global eventsFired

    print(bcolors.OKGREEN + "Creating logfile List" + bcolors.ENDC + '.', end=' ', flush=True)
    powerOffOn()
    time.sleep(2)
    if len(lst)>0 and activities==1:
        ElementsList=readLogfile(apk, lst[3])
    else:
        ElementsList=readLogfile(apk)
    #Fix the timeStamp 
    timeStamp=time.time() - start_time - countSleepTime
    ElementsList=addTimestamptoElements(ElementsList,timeStamp)

    has_clickable_elements = 0
    for element in ElementsList:
        has_clickable_elements+=checkIfClickable(element)
    
    print(bcolors.OKGREEN + "Done" + bcolors.ENDC)
    if not ElementsList or has_clickable_elements==0:
        print(bcolors.WARNING + "ElementsList is empty at start time." + bcolors.ENDC+ '.', flush=True)
        googleSSOrandom(start_time) #If starts with google sso
        powerOffOn()
        time.sleep(2)
        if len(lst)>0 and activities==1:
            ElementsList=readLogfile(apk, lst[3])
        else:
            ElementsList=readLogfile(apk)
        #Fix the timeStamp 
        timeStamp=time.time() - start_time - countSleepTime
        ElementsList=addTimestamptoElements(ElementsList,timeStamp)
        
        if not ElementsList:
            print(bcolors.WARNING + "ElementsList is empty at start time." + bcolors.ENDC+ '.')
            return time.time() - start_time
    
    print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
    addToQueue(ElementsList,[])
    printTmpList(BFSQueue)
    
    if (screenshots==1):
        screenshot("start")    
        screenshotCounter=1 
        
    i=1
    ViewCounter=1
    isSignIn=0
    stop_trying_sso=0
    appSpawnedPrevIter=1

    if grant_consent_dialogue:
        grantRunTimeConsentDialogue(ElementsList)

    for UIelement in BFSQueue:

        currentTime= time.time() - start_time
        #Check the TimeOut
        if (currentTime)>=timeout:
            print(bcolors.OKGREEN +"TimeOut excited" + bcolors.ENDC)
            
            #Fix the ViewCounter for the elements 
            for element in ElementsList:
                if element['ViewNumber']=="-":
                    element['ViewNumber']=ViewCounter
            break
        
        currentPath=[]
        elemHASH        = UIelement[0]#hash
        elemXcoord      = UIelement[1]#X coord
        elemYcoord      = UIelement[2]#Y coord
        elemreplaypath  = UIelement[3]#replaypath
        elemDict        = UIelement[4]#dictionary of element
        
        #Fix the ViewCounter
        for element in ElementsList:
            element['ViewNumber']=ViewCounter

        if not isAppSpawned() and appSpawnedPrevIter==1:
            appSpawnedPrevIter=0
            startAppandWaitforMainActivity(apk)
            if len(lst)>0 and activities==1:
                proc  = subprocess.Popen([shellCommand+f"am start -n '{lst[0]}' {lst[1]} {lst[2]}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (running_activity, err) = proc.communicate()
                time.sleep(1)
                ####
                os.system(shellCommand + " \"su -c 'touch /data/data/reaper.UIHarvester/current_app'\"")
                os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")
                ####

            if not isAppSpawned():
                print(bcolors.FAIL+"App is not spawned..."+bcolors.ENDC)
                os.system("touch "+path+"/appStopSpawning")

                if isSignIn == 1:
                    googleLoggedIn=1
                else:
                    googleLoggedIn=0

                return currentTime

        if google_sso == 1 and not isSignIn and not stop_trying_sso and googleLoggedIn==0:
            isSignIn = googleSSO(BFSQueue, start_time)
            if isSignIn == -1:
                stop_trying_sso = 1

        if setPriorities:
            pretty_text=elemDict['Text'].lower().strip().replace('\n','')
            if pretty_text == "null" or pretty_text=="":
                pretty_text=elemDict['getChildText'].lower().strip().replace('\n','')
            if pretty_text == "null" or pretty_text=="":
                pretty_text=elemDict['getContentDescription'].lower().strip().replace('\n','')

            if any(word in " "+pretty_text for word in priorityList) or pretty_text in priorityEqList:
                print("priority")

        #Check if it is interactable
        if (elemDict['isShown'] == str(1)): # elemDict['getImportantForAccessibility'] == str(1) and

            #Check if clickable
            if checkIfClickable(elemDict)!=1:
                continue
            print("###################################################")
            
            currentPath=elemreplaypath
        
            #Set the logcat date
            setLogcatDate()

            #Perform click
            if not elemreplaypath:#If the item does not have a replay path then click it
                click(elemXcoord,elemYcoord,elemDict)
                    
            else:# If the item has a replay path. traverse the replay path first
                replay(elemreplaypath)
                click(elemXcoord,elemYcoord,elemDict)
            
            if (screenshots==1):
                #Get screeshot
                screenshot("view-"+str(screenshotCounter))
                screenshotCounter+=1
            
            #Add the path so far
            replayPath=[]
            replayPath=list(elemreplaypath)
            replayPath.append((elemXcoord,elemYcoord,elemDict))

            #Check if we are still on the app
            bringToFront(start_time, elemDict, replayPath, ViewCounter)

            #Read the new logcat list
            powerOffOn()
            time.sleep(2)
            if len(lst)>0 and activities==1:
                ElementsList=readLogfile(apk, lst[3])
            else:
                ElementsList=readLogfile(apk)
            #Fix the timeStamp
            timeStamp=time.time() - start_time - countSleepTime
            ElementsList=addTimestamptoElements(ElementsList,timeStamp)
            
            #Remove the extra one that was pressed
            for item in ElementsList:
                if item['isPressed']=="1" and item['ResourceId']==elemDict['ResourceId'] and item['Object getClass']==elemDict['Object getClass']:
                    #Remove all the same occurances from the list
                    ElementsList= [a for a in ElementsList if a != item]
            
            #Remove the ones that have been already found
            for item in ElementsList:
                if existsInQueue(item['Hash'])==1:
                    #Remove all the same occurances from the list
                    ElementsList= [a for a in ElementsList if a != item]
            
            #Add the number of ***ONLY*** new UIelements to Elements-Yield feature
            k = set(list([i['Hash'] for i in ElementsList]))
            elemDict['Elements-Yield']=len(k)
            
            
            #If click did not produce new elements the ElementsList is empty
            if not ElementsList:
                print(bcolors.WARNING + "ElementsList is empty." + bcolors.ENDC+ '.')
            else:
                ViewCounter+=1
                addToQueue(ElementsList,replayPath)

            if grant_consent_dialogue:
                grantRunTimeConsentDialogue(ElementsList)

            if google_sso == 1 and not isSignIn and not stop_trying_sso and googleLoggedIn==0:
                isSignIn = googleSSO(BFSQueue, start_time, 1)
                if isSignIn == -1:
                    stop_trying_sso = 1

            printTmpList(BFSQueue)
            ##Kill the app and replay the path
            killApp()
            startAppandWaitforMainActivity(apk)
            if len(lst)>0 and activities==1:
                proc  = subprocess.Popen([shellCommand+f"am start -n '{lst[0]}' {lst[1]} {lst[2]}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (running_activity, err) = proc.communicate()
                time.sleep(1)
                ####
                os.system(shellCommand + " \"su -c 'touch /data/data/reaper.UIHarvester/current_app'\"")
                os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")
                ####  

        if isSignIn == 1:
            googleLoggedIn=1
        else:
            googleLoggedIn=0

    #If traversing has finished or the timeout is reached return the currentTime
    return currentTime
#End

def beginDFS(lst=[]):
    start_time = time.time()
    currentTime=0
    global display
    global countSleepTime
    global google_sso
    global googleLoggedIn
    global eventsFired
    
    print(bcolors.OKGREEN + "Creating logfile List" + bcolors.ENDC + '.', end=' ')
    powerOffOn()
    time.sleep(2)
    if len(lst)>0 and activities==1:
        ElementsList=readLogfile(apk, lst[3])
    else:
        ElementsList=readLogfile(apk)  
    print(bcolors.OKGREEN + "Done" + bcolors.ENDC)
    #Fix the timeStamp 
    timeStamp=time.time() - start_time - countSleepTime
    ElementsList=addTimestamptoElements(ElementsList,timeStamp)
    
    has_clickable_elements = 0
    for element in ElementsList:
        has_clickable_elements+=checkIfClickable(element)
    
    print(bcolors.OKGREEN + "Done" + bcolors.ENDC)
    if not ElementsList or has_clickable_elements==0:
        print(bcolors.WARNING + "ElementsList is empty at start time." + bcolors.ENDC+ '.')
        googleSSOrandom(start_time)
        powerOffOn()
        time.sleep(2)
        if len(lst)>0 and activities==1:
            ElementsList=readLogfile(apk, lst[3])
        else:
            ElementsList=readLogfile(apk)
        #Fix the timeStamp 
        timeStamp=time.time() - start_time - countSleepTime
        ElementsList=addTimestamptoElements(ElementsList,timeStamp)
        
        if not ElementsList:
            return time.time() - start_time

    print(bcolors.OKGREEN + "Adding to Queue" + bcolors.ENDC+ '.')
    addToDFSQueue(ElementsList,[], -1)
    printTmpList(DFSQueue)
    
    if (screenshots==1):
        screenshot("start")    
        screenshotCounter=1
    
    i=1
    ViewCounter=1
    isSignIn=0
    stop_trying_sso=0
    appSpawnedPrevIter=1

    if grant_consent_dialogue:
        grantRunTimeConsentDialogue(DFSQueue)

    for UIelement in DFSQueue:
        currentTime= time.time() - start_time

        #Check the TimeOut
        if (currentTime)>=timeout:
            print(bcolors.OKGREEN +"TimeOut excited" + bcolors.ENDC)
            #Fix the ViewCounter for the elements 
            for element in ElementsList:
                if element['ViewNumber']=="-":
                    element['ViewNumber']=ViewCounter
            break
        
        currentPath=[]
        elemHASH        = UIelement[0]#hash
        elemXcoord      = UIelement[1]#X coord
        elemYcoord      = UIelement[2]#Y coord
        elemreplaypath  = UIelement[3]#replaypath
        elemDict        = UIelement[4]#dictionary of element
        
        #Fix the ViewCounter
        for element in ElementsList:
            element['ViewNumber']=ViewCounter

        if not isAppSpawned() and appSpawnedPrevIter==1:
            appSpawnedPrevIter=0
            startAppandWaitforMainActivity(apk)
            if len(lst)>0 and activities==1:
                proc  = subprocess.Popen([shellCommand+f"am start -n '{lst[0]}' {lst[1]} {lst[2]}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (running_activity, err) = proc.communicate()
                time.sleep(1)
                ####
                os.system(shellCommand + " \"su -c 'touch /data/data/reaper.UIHarvester/current_app'\"")
                os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")
                ####

            if not isAppSpawned():
                print(bcolors.FAIL+"App is not spawned..."+bcolors.ENDC)
                os.system("touch "+path+"/appStopSpawning")

                if isSignIn == 1:
                    googleLoggedIn=1
                else:
                    googleLoggedIn=0

                return currentTime

        if google_sso == 1 and not isSignIn and not stop_trying_sso and googleLoggedIn==0:
            isSignIn = googleSSO(DFSQueue, start_time)
            if isSignIn == -1:
                stop_trying_sso = 1
        
        #Check if it is interactable
        if (elemDict['isShown'] == str(1)): #elemDict['getImportantForAccessibility'] == str(1) and 

            #Check if clickable
            if checkIfClickable(elemDict)!=1:
                continue
            print("###################################################")
            
            currentPath=elemreplaypath
        
            #Set the logcat date
            setLogcatDate()

            #Perform click
            if not elemreplaypath:#If the item does not have a replay path then click it
                    click(elemXcoord,elemYcoord,elemDict)
                    
            else:# If the item has a replay path. traverse the replay path first                
                replay(elemreplaypath)
                click(elemXcoord,elemYcoord,elemDict)
                

            if (screenshots==1):
                #Get screeshot
                screenshot("view-"+str(screenshotCounter))
                screenshotCounter+=1
            
            #Add the path so far
            replayPath=[]
            replayPath=list(elemreplaypath)
            replayPath.append((elemXcoord,elemYcoord,elemDict))

            #Check if we are still on the app
            bringToFront(start_time, elemDict, replayPath, ViewCounter)

            #Read the new logcat list
            powerOffOn()
            time.sleep(2)
            if len(lst)>0 and activities==1:
                ElementsList=readLogfile(apk, lst[3])
            else:
                ElementsList=readLogfile(apk)
            #Fix the timeStamp 
            timeStamp=time.time() - start_time - countSleepTime
            ElementsList=addTimestamptoElements(ElementsList,timeStamp)
            
            #Remove the extra one that was pressed
            for item in ElementsList:
                if item['isPressed']=="1" and  item['ResourceId']==elemDict['ResourceId'] and item['Object getClass']==elemDict['Object getClass']:
                    #Remove all the same occurances from the list
                    ElementsList= [a for a in ElementsList if a != item]
                    
            
            #Remove the ones that have been already found
            for item in ElementsList:
                if existsInDFSQueue(item['Hash'])==1:
                    #Remove all the same occurances from the list
                    ElementsList= [a for a in ElementsList if a != item]
            
            #Add the number of ***ONLY*** new UIelements to Elements-Yield feature
            k = set(list([i['Hash'] for i in ElementsList]))
            elemDict['Elements-Yield']=len(k)
            
            #If click did not produce new elements the ElementsList is empty
            if not ElementsList:
                print(bcolors.WARNING + "ElementsList is empty." + bcolors.ENDC+ '.')
            else:
                ViewCounter+=1
                #Get the position of the element in the list
                position=DFSQueue.index( (elemHASH,elemXcoord ,elemYcoord, elemreplaypath, elemDict) )
                addToDFSQueue(ElementsList,replayPath, (DFSQueue.index( (elemHASH,elemXcoord ,elemYcoord, elemreplaypath, elemDict) )+1) )

            if google_sso == 1 and not isSignIn and not stop_trying_sso and googleLoggedIn==0:
                isSignIn = googleSSO(DFSQueue, start_time, 1)
                if isSignIn == -1:
                    stop_trying_sso = 1

            printTmpList(DFSQueue)
            ##Kill the app and replay the path
            killApp()
            startAppandWaitforMainActivity(apk)
            if len(lst)>0 and activities==1:
                proc  = subprocess.Popen([shellCommand+f"am start -n '{lst[0]}' {lst[1]} {lst[2]}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (running_activity, err) = proc.communicate()
                time.sleep(1)
                ####
                os.system(shellCommand + " \"su -c 'touch /data/data/reaper.UIHarvester/current_app'\"")
                os.system(shellCommand + f" \"su -c 'echo {apk} > /data/data/reaper.UIHarvester/current_app'\"")
                ####  

    if isSignIn == 1:
        googleLoggedIn=1
    else:
        googleLoggedIn=0

    #If traversing has finished or the timeout is reached return the currentTime
    return currentTime
#End

def drawProgressBar(percent, barLen):
    # percent float from 0 to 1. 
    sys.stdout.write("\r")
    sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(barLen * percent), barLen, percent * 100))
    sys.stdout.flush()

def findLogin():
  print(bcolors.OKGREEN + "Gathering Login Activities: "+ bcolors.ENDC, end=' ')
  aapt="aapt dump xmltree "+apkPath+"/"+apk+".apk AndroidManifest.xml"
  tmp='"'
  proc  = subprocess.Popen([aapt+" | grep  -iE '.*oauth.*|.*sign.*in|.*signin.*|.*login.*|.*facebook.*' |  awk -F'"+tmp+"' '$0=$2'"], stdout=subprocess.PIPE, shell=True)
  listLoginActivities=list(proc.stdout)
  listLoginActivities = [w.replace('\n', '') for w in listLoginActivities]  
  print(bcolors.HEADER + "Done" + bcolors.ENDC)
  return listLoginActivities
#End

def checkForPopUpError():
    proc = subprocess.Popen([shellCommand+"dumpsys window windows | grep -E 'mCurrentFocus'"], stdout=subprocess.PIPE, shell=True)
    (foreground, err) = proc.communicate()
    foreground = foreground.decode('ascii').replace("\n", "")
    if re.search('(.*)Application Error:(.*)', foreground ,re.IGNORECASE):
    
        #Power off and on the display
        powerOffOnNoTime()
        
        #Read logfile
        ElementsList=readLogfile("android")
        
        for element in ElementsList:
            if re.search('(.*)Unfortunately,(.*) has stopped.', element['Text'],re.IGNORECASE):
                #Check for "ok" element
                elementTMP=next((tmp for tmp in ElementsList if tmp["Text"].lower() == "OK".lower()))
                #Click "ok" element
                if elementTMP:
                    clickNoTime(elementTMP['Coords'].split()[0],elementTMP['Coords'].split()[1],elementTMP,verbose=1)        
            if re.search('(.*)Close app(.*)', element['Text'],re.IGNORECASE):
                #Check for "Close app" element
                elementTMP=next((tmp for tmp in ElementsList if tmp["Text"].lower() == "Close app".lower()))
                #Click "ok" element
                if elementTMP:
                    clickNoTime(elementTMP['Coords'].split()[0],elementTMP['Coords'].split()[1],elementTMP,verbose=1)        
            if re.search('(.*)has stopped(.*)', element['Text'],re.IGNORECASE):
                #Check for "Close app" element
                elementTMP=next((tmp for tmp in ElementsList if tmp["Text"].lower() == "Open app again".lower()))
                #Click "ok" element
                if elementTMP:
                    clickNoTime(elementTMP['Coords'].split()[0],elementTMP['Coords'].split()[1],elementTMP,verbose=1)        
#End

def clickApproximately(display):
    X= int(int(display[0])/2)
    Y= int(0.8*int(display[1]))
    os.system(shellCommand+"input tap "+str(X)+" "+str(Y)+" > /dev/null 2>&1")
    time.sleep(sleepTime+10)
#End

def swipeUpApp():
    os.system(shellCommand+"input keyevent KEYCODE_APP_SWITCH > /dev/null 2>&1")
    time.sleep(0.5)
    os.system(shellCommand+"input swipe 522 1647 522 90 > /dev/null 2>&1")
    time.sleep(0.5)

def grantAllPermissions():
    proc  = subprocess.Popen([shellCommand+"dumpsys package " + apk + " | awk -F: '/: granted=false/ {print $1}'"], stdout=subprocess.PIPE, shell=True)
    permList = proc.stdout.readlines()
    for perm in permList:
        os.system(shellCommand+"pm grant " + apk + " " + str(perm.decode('ascii')).strip().replace("\n","")+" > /dev/null 2>&1")
        os.system(shellCommand+"appops set --uid "+apk+" "+str(perm.decode('ascii')).strip().replace("\n","").split(".")[-1]+" allow"+" > /dev/null 2>&1")

    print("Perms: "+str(permList).replace(" ", "").replace("\\n","")+" are granted for package "+apk)

#End 

#################################################
###################Main##########################
#################################################
def main(argv):
    ################Get the arguments
    global apk
    global traversal
    global path
    global device
    global sleepTime
    global sleepXforMainActivity
    global timeout
    global screenshots
    global webviewswait
    global record_replay
    global activities
    global google_sso
    global grant_consent_dialogue
    global record_file
    global replay_file
    global apkPath
    global facebookLoggedIn
    global shellCommand
    global adbCommand
    global runBFS
    global countSleepTime
    global fridaScripts
    facebooklog=0
    apkPath=""

    parser = argparse.ArgumentParser(description='Usage: traversing.py [args]', usage=argparse.SUPPRESS, formatter_class=argparse.RawTextHelpFormatter, epilog='Example:\n  Description:\n    Traverse imdb using BFS with a 2 seconds delay between clicks, 4 seconds sleep time to launch the main activity,\n    135 seconds traverse\'s timeout. Also load 2 frida scripts\n  Command:\n    python3 traversing.py -p com.imdb.mobile -d 16091JEC203869 -e BFS -o com.imdb.mobile -s 3 -a 4 -t 135 -fl script1.js script2.js\n\nTroubleshooting:\n  1) Solve the error of not getting all the items from logcat by setting the logcat buffer to 4M or 16M.', add_help=False)
    
    parser._optionals.title = 'Arguments'
    parser.add_argument('-p', '--package', metavar='', help='<Package name>')
    parser.add_argument('-d', '--device', metavar='', help='<Device\'s name>')
    parser.add_argument('-e', '--explore', metavar='', help='<BFS|DFS|monkey>')
    parser.add_argument('-t', '--timeout', metavar='', help='<Timeout for exploration in seconds | Default \'60\'>')
    parser.add_argument('-o', '--output', metavar='', help='<Path to output stuff | Default \'pwd/results\'>')
    parser.add_argument('-s', '--sleepTime', metavar='', help='<Time sleeping between clicks (in seconds) | Default \''+str(sleepTime)+'\'>')    
    parser.add_argument('-a', '--activitywait', metavar='', help='<Sleep time to launch main activity (in seconds) | Default \''+str(sleepXforMainActivity)+'\'>')
    parser.add_argument('-S', '--screenshots', metavar='', help='<Take screenshots at every step | Value <0|1> | Default \''+str(screenshots)+'\'>')
    parser.add_argument('-w', '--webviewswait', metavar='', help='<Wait until all webviews have been rendered before any action | Value <0|1>| Default \''+str(webviewswait)+'\'>')
    parser.add_argument('-c', '--grant-consent-dialogue', metavar='', help='<Grant Run-Time Consent Dialogue (GDPR, DPA, PIPA, PIPEDA, etc.) | Value <0|1>| Default \''+str(grant_consent_dialogue)+'\'>')
    parser.add_argument('-rd', '--record', metavar='', help='<Record user events | save \'path-to-file\' >')
    parser.add_argument('-ry', '--replay', metavar='', help='<Replay user events | save \'path-to-file\' >')
    parser.add_argument('-A', '--activities', metavar='', help='<Explore all activities | Value <0|1> | Default \''+str(activities)+'\'>')
    parser.add_argument('-G', '--google-sso', metavar='', help='<Sign up with google | Value <0|1> | Default \''+str(google_sso)+'\'>')
    parser.add_argument('-D', '--data', metavar='', help='<Print the data file and exit | \'path-to-file\' >')
    parser.add_argument('-F', '--features', metavar='', help='<Print the elements\'s features from a file and exit | \'path-to-file\'>')
    parser.add_argument('-i', '--input', metavar='', help='<Path to original apk file>')
    parser.add_argument('-fl', '--frida-load', metavar='', nargs='+', help='<List of frida scripts separated by space>')
    parser.add_argument('-h', '--help', action='help', help='<Shows this message>')

    args = parser.parse_args()

    print(bcolors.HEADER + "UIHarvester Traversing Module" + bcolors.ENDC)

    mandatory_args = 0

    if args.package!=None:
        apk = args.package
        mandatory_args+=1
    if args.device!=None:
        device = args.device
        if os.environ.get( 'ADB_SETUP' ) == 'virtual':
            shellCommand="adb shell "
            adbCommand="adb "
        else:
            shellCommand="adb -s "+device+" shell "
            adbCommand="adb -s "+device+" "
        mandatory_args+=1
    if args.explore!=None:
        traversal = args.explore
        mandatory_args+=1
    if args.timeout!=None:
        timeout = args.timeout
    if args.output!=None:
        path = args.output
    if args.sleepTime!=None:
        sleepTime = float(args.sleepTime)
    if args.activitywait!=None:
        sleepXforMainActivity = float(args.activitywait)
    if args.screenshots!=None:
        screenshots = int(args.screenshots)
    if args.webviewswait!=None:
        webviewswait = int(args.webviewswait)
    if args.grant_consent_dialogue!=None:
        grant_consent_dialogue = int(args.grant_consent_dialogue)
    if args.activities!=None:
        activities = int(args.activities)
    if args.google_sso!=None:
        google_sso = int(args.google_sso)
    if args.record!=None:
        record_replay = "record"
        record_file = args.record
        mandatory_args+=1
    if args.replay!=None:
        record_replay = "replay"
        replay_file = args.replay
        mandatory_args+=1
    if args.data!=None:
        loadQueue(str(args.data))
        return
    if args.features!=None:
        printFeatures(str(args.features))
        return
    if args.input!=None:
        apkPath=str(args.input)
    if args.frida_load!=None:
        fridaScripts+= "-l "+" -l ".join(args.frida_load)

    if mandatory_args == 3:
        pass
    else:
        print("Wrong arguments. Check traversing.py --help")
        sys.exit()

    print("Mandatory arguments: ", "apk: ["+str(apk)+"] device: ["+str(device)+"] traversal: ["+str(traversal)+"]")
    print("Shell command: ", shellCommand)
    has_path = os.popen(shellCommand + f" pm path {apk}").read()
    if has_path.strip().replace("\n", "") == "":
        print("Wrong package name.")
        sys.exit()
    
    if traversal=="BFS" or traversal=="DFS" or traversal=="monkey" or traversal=="MONKEY" or record_replay.lower()=="record" or record_replay.lower()=="replay":
        pass
    else:
        print("Wrong argument(--explore). Check traversing.py --help")
        sys.exit()
    print("Arguments: ","apk: ["+str(apk)+"] device: ["+str(device)+"] traversal: ["+str(traversal)+"] timeout: ["+str(timeout)+
        "] path: ["+str(path)+"] sleepTime: ["+str(sleepTime)+"] sleepXforMainActivity: ["+str(sleepXforMainActivity)+"] waitForWebviews: ["+str(webviewswait)+
        "] exploreAllActivities: ["+str(activities)+"] googleSSO: ["+str(google_sso)+"] DataPrivacyConsentDialogue: ["+str(grant_consent_dialogue)+"]")

    sleepTime=float(sleepTime)
    sleepXforMainActivity= float(sleepXforMainActivity)
    timeout=float(timeout)
    ###############

    isAccessibilityRunning = os.popen(shellCommand+'dumpsys activity services | grep -c "reaper.UIHarvester/.WebAccessibility"').read()
    if int(isAccessibilityRunning) == 0:
        os.system(shellCommand+"settings put secure enabled_accessibility_services reaper.UIHarvester/.WebAccessibility")

    #if webviewswait == 1:
    fridaScripts+=" -l "+FRIDA_SCRIPTS_PATH+"identify_webviews.js "

    os.system(shellCommand + "\"su -c 'echo false > /data/data/reaper.UIHarvester/is_plaintext'\"")

    #kill frida process
    os.system('pkill -f "frida -U -f '+apk+' -l '+FRIDA_SCRIPTS_PATH+'UIHarvester.js"')

    #Set logcat buffer = 4M
    os.system(adbCommand+" logcat -G 8M")

    #Create logcatRandomTag in order to get logcat output after this value
    global logcatRandomTag
    setLogcatDate()
    setWebviewLogcatDate()
    logcatRandomTag="Frida-Bridge"+id_generator()
    #Print logcatRandomTag to logcat
    os.system(shellCommand+"log -p v -t Frida-Bridge"+logcatTag+" "+logcatRandomTag+"")

    #Get full logcat
    path = "./vv8uiharvester/"+apk
    if path == "." :
        path="./results/"+apk
        if os.path.exists(path):
            os.system("rm -rf "+path)
        
        os.system("mkdir -p "+path)
        os.system("mkdir "+path+"/UIHarvester")
        os.system("mkdir "+path+"/frida")
        os.system("mkdir "+path+"/logcat")
    else:
        os.system("rm -rf "+path)

        os.system("mkdir -p "+path)
        os.system("mkdir "+path+"/UIHarvester")
        os.system("mkdir "+path+"/frida")
        os.system("mkdir "+path+"/logcat")

    print(bcolors.OKGREEN + "Begin Traversing" + bcolors.ENDC + '.')

    os.system(adbCommand+"logcat > "+path+"/logcat/full_logcat &")

    grantAllPermissions()
    
    #Begin traversing
    if activities==1:
        print("Init Activity Traversing...")
        os.system("mkdir "+path+"/Activities")
        currentTime=initActivities()
    elif record_replay.lower()=="record":
        print(bcolors.WARNING + "Wait before Recording..." + bcolors.ENDC)
        os.system("mkdir "+path+"/RecordReplay")
        #Start Apps's main activity
        startAppandWaitforMainActivity(apk)
        #Record and Replay
        currentTime=recordRR()
    elif record_replay.lower()=="replay":
        print(bcolors.WARNING + "Wait for Replaying..." + bcolors.ENDC)
        os.system("mkdir "+path+"/RecordReplay")
        #Start Apps's main activity
        startAppandWaitforMainActivity(apk)
        #Record and Replay
        currentTime=replayRR()
    elif traversal=="BFS":
        #Start Apps's main activity
        startAppandWaitforMainActivity(apk)
        #Begin BFS
        print(bcolors.WARNING + "Wait before BFS..." + bcolors.ENDC, flush=True)
        currentTime=beginBFS()
    elif traversal=="DFS":
        #Start Apps's main activity
        startAppandWaitforMainActivity(apk)
        #Begin DFS
        currentTime=beginDFS()
    elif traversal=="monkey" or traversal=="MONKEY":
        currentTime=beginMonkey()
    
    print(bcolors.OKGREEN + "Traversing Finished" + bcolors.ENDC + '.')
    #KIll the app
    killApp()
    time.sleep(5) 
    #Output all the info to the specified path and file
    printOutput(currentTime, path+"/traversingResults")
    
    #kill logcat that is on the background
    os.system("kill -9 $! > /dev/null 2>&1")
    os.system("pkill -f \""+adbCommand+"\"")
    os.makedirs(path+"/logz", exist_ok=True)
    os.system(adbCommand+"pull /sdcard/Documents/ "+path+"/logz")
    os.system(adbCommand+"shell su -c 'pm clear com.google.android.webview'")
    os.system(adbCommand+"shell su -c 'rm -rf /sdcard/Documents/*'")
    open(path + "/fileList.txt", "w").write(subprocess.run(["adb", "shell", "ls", "/sdcard/Documents/"], capture_output=True, text=True).stdout)
    os.system(shellCommand + f" \"su -c 'echo 0 > /data/data/reaper.UIHarvester/current_app'\"")

#End

if __name__ == "__main__":
   print("Starting traversing.py")
   main(sys.argv[1:])
