#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# author:    zhangpeng
# reference: myself
# purpose:   filter the car's family log
# date:      2018-03-16
# version:   1.0.5
# improve:   functionalize and decoratelize

import sys
import os
import commands
import re
import time
import datetime

sVG01LogPath = '/record/ftpfiles/xyvg01/L/'
sVG02LogPath = '/record/ftpfiles/xyvg02/L/'
sLocalLogPath = '/home/zhangpeng/signalStatistics/data/dataAll/'
sScriptPath = '/home/zhangpeng/carFamilyLog/'
dErrorCode = {"20": "被叫不应答", "16": "被叫不应答", "17": "用户忙", "18": "用户无响应", "19": "用户无应答"}
linput = sys.argv[1:]

sRegexDate = ur'2018-\d{2}-\d{2}'
sRegexTime = ur'[0-2][0-9]:[0-5][0-9]:[0-5][0-9]'
sRegexAni = ur'[01]\d{10}'
for eachInput in linput:
    matchDate = re.search(sRegexDate, eachInput)
    matchTime = re.search(sRegexTime, eachInput)
    matchAni = re.search(sRegexAni, eachInput)
    if matchDate:
        sDateOri = matchDate.group()
        sDate = sDateOri.replace("-", "")
    if matchTime:
        sTime = matchTime.group()
    if matchAni:
        sAni = matchAni.group()
# print sDateOri
# improve:   jude the time to search from VG01 or VG02(1.0.3)
sNowHour = time.strftime('%H', time.localtime(time.time()))
today = datetime.date.today()

if sDateOri == today.isoformat() and sTime[:2] == sNowHour:
    lLogPath = [sVG01LogPath, sVG02LogPath]
elif sDateOri == today.isoformat() and (int(sNowHour) == int(sTime[:2]) + 1 or int(sNowHour) == int(sTime[:2]) + 2):
    lLogPath = [sLocalLogPath, sVG01LogPath, sVG02LogPath]
else:
    lLogPath = [sLocalLogPath]
print(lLogPath)

sDatePlus1H = (datetime.datetime.strptime(sTime, '%H:%M:%S') + datetime.timedelta(hours=1)).strftime('%H:%M:%S')[:2]

for sEachLogPath in lLogPath:
    if sEachLogPath == sLocalLogPath:
        sCpLog = "cp -f /%s/%s%s*.log /%s/%s%s*.log /%s/" % (
            sEachLogPath, sDate, sTime[:2], sEachLogPath, sDate, sDatePlus1H, sScriptPath)
        tShellCpLog = commands.getstatusoutput(sCpLog)
    elif sEachLogPath == sVG01LogPath:
        sCpLog = "cp -f /%s/%s%s*.log /%s/%s%s*.log /%s/" % (
            sEachLogPath, sDate, sTime[:2], sEachLogPath, sDate, sDatePlus1H, sScriptPath)
        tShellCpLog = commands.getstatusoutput(sCpLog)
        tRename = commands.getstatusoutput('rename  ".log" "_xyvg01.log" /%s/%s??.log' % (sScriptPath, sDate))
    else:
        sCpLog = "cp -f /%s/%s%s*.log /%s/%s%s*.log /%s/" % (
            sEachLogPath, sDate, sTime[:2], sEachLogPath, sDate, sDatePlus1H, sScriptPath)
        tShellCpLog = commands.getstatusoutput(sCpLog)
        tRename = commands.getstatusoutput('rename  ".log" "_xyvg02.log" /%s/%s??.log' % (sScriptPath, sDate))
    # print(tShellCpLog[1].decode('UTF-8','ignore'))

    # tlsName = commands.getstatusoutput('ls /%s/'%sScriptPath)
    # print(tlsName[1])

sFindSsionid = "cat /%s/%s*.log |grep %s |grep %s |awk 'END {print $6}'" % (sScriptPath, sDate, sAni, sTime)
tShellFindSsionid = commands.getstatusoutput(sFindSsionid)
print(tShellFindSsionid)
if tShellFindSsionid[1] != '':
    sSsionid = tShellFindSsionid[1].replace("[", "").replace("]", "")
    sGetRecordLog = "cat /%s/%s*.log |grep %s" % (sScriptPath, sDate, sSsionid)
    lRecordLogOri = commands.getstatusoutput(sGetRecordLog)
    # print(lRecordLogOri[1])

# print(sRecordLogOri[1].encode('UTF-8').decode('UTF-8','ignore'))
tmp = sys.stdout  # print stream redirection
sys.stdout = open('logTmp.txt', 'w')
print(lRecordLogOri[1])  # warning do not comment this statement
sys.stdout.close()  # must close the opened file
sys.stdout = tmp

sRmLog = "rm -f /%s/%s*.log" % (sScriptPath, sDate)
lRmLog = commands.getstatusoutput(sRmLog)

sColor = '32'
print '\033[1;%s;40m=\033[0m' % (sColor) * 75
print 're:'
print unicode(' '.join(sys.argv[1:]), 'utf-8')
print '\033[1;%s;40m=\033[0m' % (sColor) * 75

dRegexLog = {
    'sRegexPlayWhiteWav': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Menu.*play.*whitelistin' % (sDateOri), \
    'sRegexPlayWav': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Menu.*play.*welcome' % (sDateOri), \
    'sRegexPressKey': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Menu.*dtmf.*pszDtmf:(\d)' % (sDateOri), \
    'sRegexDestNumLock': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Flow.*Tellock\sverify\sdestnum.*exist:tellock:(\d+)' % (
        sDateOri), \
    'sRegexStartCallFull': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Dial.*\xd6\xf7\xbd\xd0:(%s),.*\xb1\xbb\xbd\xd0:(\d+),\xb1\xbb\xbd\xd0\xc7\xf8\xba\xc5:(\d+),\xd4\xad\xb1\xbb\xbd\xd0:\d+' % (
        sDateOri, sAni), \
    'sRegexDnisRing': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Tran.*\xcd\xe2\xba\xf4\xb6\xd4\xb6\xcb\xd5\xf1\xc1\xe5\xa1\xa3' % (
        sDateOri), \
    'sRegexFailTrans': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Tran.*\xd7\xaa\xbd\xd3\xca\xa7\xb0\xdc.*\xb1\xbb\xbd\xd0:(\d+).*\xd0\xc5\xc1\xee:(\d+)' % (
        sDateOri), \
    'sRegexStartCallTerm': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Dial.*\xd6\xf7\xbd\xd0:(\d+),.*\xb1\xbb\xbd\xd0:(\d+),\xb1\xbb\xbd\xd0\xc7\xf8\xba\xc5:(\d+),\xd4\xad\xb1\xbb\xbd\xd0:(?!\d)' % (
        sDateOri), \
    'sRegexTransSucc': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Tran.*\xd7\xaa\xbd\xd3\xb3\xc9\xb9\xa6\xb4\xee\xbd\xd3' % (
        sDateOri), \
    'sRegexDisconnect': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Reco.*Stop record.*Success' % (sDateOri), \
    'sRegexAniHungUp': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Tran.*EVTDISCONNECTED' % (sDateOri), \
    'sRegexRecordOver': ur'^(%s\s[0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*Bill.*WriteSDR' % (sDateOri), \
    'sRegexCallIn': ur'^(%s\s%s).*Call.*Incoming Call.*(%s)' % (sDateOri, sTime, sAni), \
    }
with open('/%s/logTmp.txt' % (sScriptPath)) as logFile:
    for eachline in logFile:
        mRegexCallIn = re.search(dRegexLog['sRegexCallIn'], eachline)
        mRegexPlayWav = re.search(dRegexLog['sRegexPlayWav'], eachline)
        mRegexPlayWhiteWav = re.search(dRegexLog['sRegexPlayWhiteWav'], eachline)
        mRegexPressKey = re.search(dRegexLog['sRegexPressKey'], eachline)
        mRegexStartCallFull = re.search(dRegexLog['sRegexStartCallFull'], eachline)
        mRegexDnisRing = re.search(dRegexLog['sRegexDnisRing'], eachline)
        mRegexFailTrans = re.search(dRegexLog['sRegexFailTrans'], eachline)
        mRegexStartCallTerm = re.search(dRegexLog['sRegexStartCallTerm'], eachline)
        mRegexTransSucc = re.search(dRegexLog['sRegexTransSucc'], eachline)
        mRegexAniHungUp = re.search(dRegexLog['sRegexAniHungUp'], eachline)
        mRegexRecordOver = re.search(dRegexLog['sRegexRecordOver'], eachline)
        mRegexDestNumLock = re.search(dRegexLog['sRegexDestNumLock'], eachline)
        if mRegexCallIn:
            print("%s -主叫%s呼入。" % (mRegexCallIn.group(1), mRegexCallIn.group(2)))
        if mRegexPlayWav:
            print("%s -播放欢迎语。" % (mRegexPlayWav.group(1)))
        if mRegexPlayWhiteWav:
            print("%s -播放白名单提示语。" % (mRegexPlayWhiteWav.group(1)))
        if mRegexPressKey:
            print("%s -开始菜单按键，按了菜单%s键。" % (mRegexPressKey.group(1), mRegexPressKey.group(2)))
        if mRegexStartCallFull:
            print("%s -开始全透传转接%s。" % (mRegexStartCallFull.group(1), mRegexStartCallFull.group(3)))
        if mRegexDnisRing:
            print("%s -外呼对端振铃。" % (mRegexDnisRing.group(1)))
        if mRegexFailTrans:
            print("%s -转接失败。%s%s" % (
                mRegexFailTrans.group(1), mRegexFailTrans.group(2), dErrorCode[mRegexFailTrans.group(3)]))
        if mRegexStartCallTerm:
            print("%s -开始计费号转接%s" % (mRegexStartCallTerm.group(1), mRegexStartCallTerm.group(3)))
        if mRegexTransSucc:
            print("%s -转接成功开始通话。" % (mRegexTransSucc.group(1)))
        if mRegexAniHungUp:
            print("%s -主叫挂断。" % (mRegexAniHungUp.group(1)))
        if mRegexRecordOver:
            print("%s -通话结束。" % (mRegexRecordOver.group(1)))
        if mRegexDestNumLock:
            print("%s -目的码%s被锁。" % (mRegexDestNumLock.group(1), mRegexDestNumLock.group(2)))
print '\033[1;%s;40m=\033[0m' % (sColor) * 75
