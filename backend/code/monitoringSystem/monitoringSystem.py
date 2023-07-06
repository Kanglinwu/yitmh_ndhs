from flask import Blueprint, jsonify, render_template, request, Response
from bs4 import BeautifulSoup
from collections import defaultdict

from models import db, get_handover_customer_status, get_handover_health_map, get_customer_status_note

import requests
import datetime
import json

## connect windows server
from smb.SMBConnection import SMBConnection

app_monitoringSystem = Blueprint('app_monitoringSystem', __name__)


@app_monitoringSystem.route('/test')
def get_backup_test():
    return 'test the blueprint'


@app_monitoringSystem.route('/check/wug', methods=['GET', 'POST'])
def checkerWug():
    # assign front end data
    front_data = request.get_json(silent=True)
    currentDate = front_data['curDate']
    currentShift = front_data['curShift']
    lastCheckTime = front_data['timeStamp']
    checker = front_data['newEditor']

    # get result from 3rd partner
    curTime = datetime.datetime.now()
    cur_time_u = curTime.timestamp()
    postTimeStamp = int(cur_time_u) * 1000
    with requests.Session() as s:
        url = "http://10.99.25.64/NmConsole/user/login"
        payload = "ReturnUrl=%2FNmConsole%2F&UserName=admin&Password=!QAZ2wsx&RememberMe=false&X-Requested-With=XMLHttpRequest"
        headers = {
            'Content-Type':
            'application/x-www-form-urlencoded',
            'Authorization':
            'Basic YWRtaW46IVFBWjJ3c3g=',
            'Cookie':
            'ASPSESSIONIDSQARTATT=CLBLECABEPBAHOAHBFMCPNJH; ASP.NET_SessionId=; .ASPXAUTH=1CF46A1C5CBC97470447D776166DD20226639F13C20B1E71739D55A69CE5D010231606DC9A2183355D1BFC53B9DE7B04FF8872CAD559260BCE735DB134B5443E3B876FD021EECADCE704699F402FFE97D4AB85081FDC506371ACF02452F5D36C460F246001C23970E411443E3709A1DD5E7BB510F8958F9BD4842B377EB20D7E; langid=1033'
        }

        loginPage = s.post(url, headers=headers, data=payload)

        if loginPage.status_code == 200:
            summaryTable = s.get(
                f'http://10.99.25.64/NmConsole/Reports/Workspace/Universal/ProblemAreas/WrSummaryCounts/WrSummaryCounts.asp?nDeviceGroupID=-1&sUniqueID=71A57C78-E66A-41B1-AE1D-6CE9700F2ADD&nWorkspaceType=4&nTimestamp={postTimeStamp}'
            )
            readHtmlbyBs4 = BeautifulSoup(summaryTable.text, 'lxml')
            selectAllitemBytr = readHtmlbyBs4.select('tr')
            multi_dict = defaultdict(list)
            for i in selectAllitemBytr:
                if i.find('span', {'style': 'background-color:#FF5050;'}):
                    multi_dict[i.select('a')[0].get_text()] = int(
                        i.select('td')[0].get_text())

    # generate dict to frontend
    insertDict = {}
    insertDict['auditor'] = checker
    insertDict['lastCheckTime'] = lastCheckTime
    if len(dict(multi_dict).keys()) != 0:
        insertDict['status'] = 'Error'
        insertDict['detail'] = dict(multi_dict)
    else:
        insertDict['status'] = 'Good'
        insertDict['detail'] = 'null'

    # check db exist the data or not
    queryDb = get_handover_health_map.query.filter(
        get_handover_health_map.date == currentDate,
        get_handover_health_map.shift == currentShift).first()

    if queryDb:
        # means update only
        queryDb.WhatsUpGold = json.dumps(insertDict)
        insertDict['verion'] = queryDb.Ver + 1
        queryDb.Ver += 1
        db.session.commit()
        db.session.close()
    else:
        # means new row for this date & shift
        insertDb = get_handover_health_map(date=currentDate,
                                           shift=currentShift,
                                           WhatsUpGold=json.dumps(insertDict),
                                           Ver=1)
        insertDict['verion'] = 1
        db.session.add(insertDb)
        db.session.commit()
        db.session.close()
    db.session.remove()
    return jsonify(insertDict)


@app_monitoringSystem.route('/check/prtg/fri', methods=['GET', 'POST'])
def checkerPrtgFri():
    # assign front end data
    front_data = request.get_json(silent=True)
    currentDate = front_data['curDate']
    currentShift = front_data['curShift']
    lastCheckTime = front_data['timeStamp']
    checker = front_data['newEditor']
    # get result from 3rd partner
    result = requests.get(
        'http://10.99.25.212/api/table.json?content=sensors&columns=objid,downtimesince,device,sensor,lastvalue,status,message,priority&filter_status=5&filter_status=4&filter_status=13&filter_status=14&sortby=priority&username=prtgadmin&passhash=1754565467'
    )
    hashtable = defaultdict(list)
    if result.json()['treesize'] != 0:
        for i in result.json()['sensors']:
            if i['status'] in hashtable.keys():
                hashtable[i['status']] = hashtable[i['status']] + 1
            else:
                hashtable[i['status']] = 1
    # generate dict to frontend
    insertDict = {}
    insertDict['auditor'] = checker
    insertDict['lastCheckTime'] = lastCheckTime
    if len(dict(hashtable).keys()) != 0:
        insertDict['status'] = 'Error'
        insertDict['detail'] = dict(hashtable)
    else:
        insertDict['status'] = 'Good'
        insertDict['detail'] = 'null'

    # check db exist the data or not
    queryDb = get_handover_health_map.query.filter(
        get_handover_health_map.date == currentDate,
        get_handover_health_map.shift == currentShift).first()

    if queryDb:
        # means update only
        queryDb.PRTG_FRI = json.dumps(insertDict)
        insertDict['verion'] = queryDb.Ver + 1
        queryDb.Ver += 1
        db.session.commit()
        db.session.close()
    else:
        # means new row for this date & shift
        insertDb = get_handover_health_map(date=currentDate,
                                           shift=currentShift,
                                           PRTG_FRI=json.dumps(insertDict),
                                           Ver=1)
        insertDict['verion'] = 1
        db.session.add(insertDb)
        db.session.commit()
        db.session.close()

    db.session.remove()
    # return auditor, detail, lastCheckTime, status only
    return jsonify(insertDict)


@app_monitoringSystem.route('/check/prtg/sun', methods=['GET', 'POST'])
def checkerPrtgSun():
    # assign front end data
    front_data = request.get_json(silent=True)
    currentDate = front_data['curDate']
    currentShift = front_data['curShift']
    lastCheckTime = front_data['timeStamp']
    checker = front_data['newEditor']
    # get result from 3rd partner
    result = requests.get(
        'http://10.99.25.209/api/table.json?content=sensors&columns=objid,downtimesince,device,sensor,lastvalue,status,message,priority&filter_status=5&filter_status=4&filter_status=13&filter_status=14&sortby=priority&username=prtgadmin&passhash=4220464942'
    )
    hashtable = defaultdict(list)
    if result.json()['treesize'] != 0:
        for i in result.json()['sensors']:
            if i['status'] in hashtable.keys():
                hashtable[i['status']] = hashtable[i['status']] + 1
            else:
                hashtable[i['status']] = 1
    # generate dict to frontend
    insertDict = {}
    insertDict['auditor'] = checker
    insertDict['lastCheckTime'] = lastCheckTime
    if len(dict(hashtable).keys()) != 0:
        insertDict['status'] = 'Error'
        insertDict['detail'] = dict(hashtable)
    else:
        insertDict['status'] = 'Good'
        insertDict['detail'] = 'null'

    # check db exist the data or not
    queryDb = get_handover_health_map.query.filter(
        get_handover_health_map.date == currentDate,
        get_handover_health_map.shift == currentShift).first()

    if queryDb:
        # means update only
        queryDb.PRTG_SUN = json.dumps(insertDict)
        insertDict['verion'] = queryDb.Ver + 1
        queryDb.Ver += 1
        db.session.commit()
        db.session.close()
    else:
        # means new row for this date & shift
        insertDb = get_handover_health_map(date=currentDate,
                                           shift=currentShift,
                                           PRTG_SUN=json.dumps(insertDict),
                                           Ver=1)
        insertDict['verion'] = 1
        db.session.add(insertDb)
        db.session.commit()
        db.session.close()
    db.session.remove()
    # return auditor, detail, lastCheckTime, status only
    return jsonify(insertDict)


@app_monitoringSystem.route('/check/pagerduty', methods=['GET', 'POST'])
def checkerPagerDuty():
    # assign front end data
    front_data = request.get_json(silent=True)
    currentDate = front_data['curDate']
    currentShift = front_data['curShift']
    lastCheckTime = front_data['timeStamp']
    checker = front_data['newEditor']
    # get result from 3rd partner
    result = requests.get('http://10.7.6.221:6001/query_db_alert/all')
    # generate dict to frontend
    insertDict = {}
    insertDict['auditor'] = checker
    if len(result.json().keys()) != 0:
        insertDict['status'] = 'Error'
        insertDict['detail'] = result.json()
    else:
        insertDict['status'] = 'Good'
        insertDict['detail'] = 'null'
    insertDict['lastCheckTime'] = lastCheckTime
    # check db exist the data or not
    queryDb = get_handover_health_map.query.filter(
        get_handover_health_map.date == currentDate,
        get_handover_health_map.shift == currentShift).first()

    if queryDb:
        # means update only
        queryDb.PageDuty = json.dumps(insertDict)
        insertDict['verion'] = queryDb.Ver + 1
        queryDb.Ver += 1
        db.session.commit()
        db.session.close()
    else:
        # means new row for this date & shift
        insertDb = get_handover_health_map(date=currentDate,
                                           shift=currentShift,
                                           PageDuty=json.dumps(insertDict),
                                           Ver=1)
        insertDict['verion'] = 1
        db.session.add(insertDb)
        db.session.commit()
        db.session.close()
    db.session.remove()
    # return auditor, detail, lastCheckTime, status only
    return jsonify(insertDict)


@app_monitoringSystem.route('/check/jkb', methods=['GET', 'POST'])
def checkerJkb():
    # assign front end data
    front_data = request.get_json(silent=True)
    currentDate = front_data['curDate']
    currentShift = front_data['curShift']
    lastCheckTime = front_data['timeStamp']
    checker = front_data['newEditor']
    # get result from 3rd partner
    # result = requests.get('http://192.168.37.16:5001/for_gary_handover_check_if_any_alert/')
    result = requests.get('http://10.7.6.186:5055/for_gary_handover_check_if_any_alert')
    insertDict = {}
    insertDict['auditor'] = checker
    if int(result.text) != 0:
        insertDict['status'] = 'Error'
        insertDict['detail'] = {'alert': result.text}
    else:
        insertDict['status'] = 'Good'
        insertDict['detail'] = 'null'
    insertDict['lastCheckTime'] = lastCheckTime

    # check db exist the data or not
    queryDb = get_handover_health_map.query.filter(
        get_handover_health_map.date == currentDate,
        get_handover_health_map.shift == currentShift).first()

    if queryDb:
        # means update only
        queryDb.JKB = json.dumps(insertDict)
        insertDict['verion'] = queryDb.Ver + 1
        queryDb.Ver += 1
        db.session.commit()
        db.session.close()
    else:
        # means new row for this date & shift
        insertDb = get_handover_health_map(date=currentDate,
                                           shift=currentShift,
                                           JKB=json.dumps(insertDict),
                                           Ver=1)
        insertDict['verion'] = 1
        db.session.add(insertDb)
        db.session.commit()
        db.session.close()
    # return auditor, detail, lastCheckTime, status only
    return jsonify(insertDict)


@app_monitoringSystem.route('/healthMap/query/<date>/<shift>')
def healthMapQuery(date, shift):
    result = get_handover_health_map.query.filter(
        get_handover_health_map.date == date,
        get_handover_health_map.shift == shift).first()
    db.session.remove()
    if result:
        rebuildList = []
        serviceNameList = list(
            result.serialize.keys())  # list all keys on result
        serviceNameList = [
            e for e in serviceNameList
            if e not in ('sn', 'date', 'shift', 'Ver')
        ]  # drop unnecessary keys

        for i in serviceNameList:
            if result.serialize[i] != None:
                # result.serialize[i] -> str
                tmpDict = json.loads(
                    result.serialize[i]
                )  # {'auditor': 'Gary.Wu', 'status': 'Good', 'detail': 'null', 'lastCheckTime': '2022/01/06 23:47'}
            else:
                tmpDict = {
                    'auditor': 'Null',
                    'status': 'Unknown',
                    'detail': 'Null',
                    'lastCheckTime': 'Null'
                }
            tmpDict['service'] = i
            rebuildList.append({i: tmpDict})
        rebuildList.append({'verion': result.serialize['Ver']})
        return jsonify(rebuildList)
    else:
        return f'{date}-{shift} row does not exist', 202


@app_monitoringSystem.route('/healthMap/autoQuery')
def healthMapAutoQuery():
    result = get_handover_customer_status.query.order_by(
        get_handover_customer_status.sn.desc()).first()
    return_dict = dict(date=result.date.strftime("%Y%m%d"), shift=result.shift)
    date = return_dict['date']
    shift = return_dict['shift']

    result = get_handover_health_map.query.filter(
        get_handover_health_map.date == date,
        get_handover_health_map.shift == shift).first()
    db.session.remove()
    if result:
        rebuildList = []
        serviceNameList = list(
            result.serialize.keys())  # list all keys on result
        serviceNameList = [
            e for e in serviceNameList
            if e not in ('sn', 'date', 'shift', 'Ver')
        ]  # drop unnecessary keys

        for i in serviceNameList:
            if result.serialize[i] != None:
                # result.serialize[i] -> str
                tmpDict = json.loads(
                    result.serialize[i]
                )  # {'auditor': 'Gary.Wu', 'status': 'Good', 'detail': 'null', 'lastCheckTime': '2022/01/06 23:47'}
            else:
                tmpDict = {
                    'auditor': 'Null',
                    'status': 'Unknown',
                    'detail': 'Null',
                    'lastCheckTime': 'Null'
                }
            tmpDict['service'] = i
            rebuildList.append({i: tmpDict})
        rebuildList.append({'verion': result.serialize['Ver']})
        return jsonify(rebuildList)
    else:
        return f'{date}-{shift} row does not exist', 202


@app_monitoringSystem.route('/healthMap/verion/<date>/<shift>')
def healthMapVersion(date, shift):
    result = get_handover_health_map.query.filter(
        get_handover_health_map.date == date,
        get_handover_health_map.shift == shift).first()
    db.session.remove()
    db.session.close()
    if result:
        return str(result.serialize['Ver'])
    else:
        return str(0)


@app_monitoringSystem.route('/healthMap/autoVerion')
def healthMapAutoVersion():
    result = get_handover_customer_status.query.order_by(
        get_handover_customer_status.sn.desc()).first()
    return_dict = dict(date=result.date.strftime("%Y%m%d"), shift=result.shift)
    date = return_dict['date']
    shift = return_dict['shift']
    result = get_handover_health_map.query.filter(
        get_handover_health_map.date == date,
        get_handover_health_map.shift == shift).first()
    db.session.remove()
    db.session.close()
    if result:
        return str(result.serialize['Ver'])
    else:
        return str(0)


@app_monitoringSystem.route('/check/hm/<target>', methods=['GET', 'POST'])
def checkerHm(target):
    # assign front end data
    front_data = request.get_json(silent=True)
    currentDate = front_data['curDate']
    currentShift = front_data['curShift']
    lastCheckTime = front_data['timeStamp']
    checker = front_data['newEditor']

    ## update the file by HM report only for 93 and 94
    if (target == 'pauseList93') or (target == 'pauseList94'):
        userID = 'ops'
        password = '!QAZ2wsx'
        client_machine_name = 'DHSChecker'
        server_name = 'A-EZ-111'
        server_ip = '10.7.6.93'
        # domain_name = 'sso'
        conn = SMBConnection(userID,
                             password,
                             client_machine_name,
                             server_name,
                             use_ntlm_v2=True,
                             is_direct_tcp=True)

        conn.connect(server_ip, 445)

        sharefiles = conn.listPath('Share', '/DHS')

        for i in sharefiles:
            if i.filename == f'{target}.htm':
                with open(f'monitoringSystem/static/{i.filename}', 'wb') as fp:
                    conn.retrieveFile('Share', f'/DHS/{i.filename}', fp)
        with open(f'monitoringSystem/static/{target}.htm',
                  'r',
                  errors='ignore') as file_object:
            bsObj = BeautifulSoup(file_object, 'lxml')
            nameList = bsObj.findAll("td", {"class": "TFc"})

        if len(nameList) != 0:
            returnDict = {'pause': len(nameList)}
        else:
            returnDict = {}
    else:
        userID = 'yt0060'
        password = '4rfv%TGB6yhn`'
        client_machine_name = 'DHSChecker'
        if target == 'pauseList81':
            server_name = 'A-noc-hm081'
            server_ip = '10.99.25.81'
        elif target == 'pauseList82':
            server_name = 'A-noc-hm082'
            server_ip = '10.99.25.82'
        domain_name = 'sso'
        conn = SMBConnection(userID,
                             password,
                             client_machine_name,
                             server_name,
                             domain=domain_name,
                             use_ntlm_v2=True,
                             is_direct_tcp=True)
        conn.connect(server_ip, 445)
        sharefiles = conn.listPath('x', '/DHS')

        for i in sharefiles:
            if i.filename == f'{target}.htm':
                with open(f'monitoringSystem/static/{i.filename}', 'wb') as fp:
                    conn.retrieveFile('x', f'/DHS/{i.filename}', fp)
        with open(f'monitoringSystem/static/{target}.htm',
                  'r',
                  errors='ignore') as file_object:
            bsObj = BeautifulSoup(file_object, 'lxml')
            nameList = bsObj.findAll("td", {"class": "TFc"})

        if len(nameList) != 0:
            returnDict = {'pause': len(nameList)}
        else:
            returnDict = {}

    insertDict = {}
    insertDict['auditor'] = checker
    if len(returnDict.keys()) != 0:
        insertDict['status'] = 'Error'
        insertDict['detail'] = returnDict
    else:
        insertDict['status'] = 'Good'
        insertDict['detail'] = 'null'
    insertDict['lastCheckTime'] = lastCheckTime

    # check db exist the data or not
    queryDb = get_handover_health_map.query.filter(
        get_handover_health_map.date == currentDate,
        get_handover_health_map.shift == currentShift).first()

    if queryDb:
        # means update only
        if target == 'pauseList93':
            queryDb.HM93 = json.dumps(insertDict)
        elif target == 'pauseList94':
            queryDb.HM94 = json.dumps(insertDict)
        elif target == 'pauseList81':
            queryDb.HM81 = json.dumps(insertDict)
        elif target == 'pauseList82':
            queryDb.HM82 = json.dumps(insertDict)
        insertDict['verion'] = queryDb.Ver + 1
        queryDb.Ver += 1
        db.session.commit()
        db.session.close()
    else:
        # means new row for this date & shift
        if target == 'pauseList93':
            insertDb = get_handover_health_map(date=currentDate,
                                               shift=currentShift,
                                               HM93=json.dumps(insertDict),
                                               Ver=1)
        elif target == 'pauseList94':
            insertDb = get_handover_health_map(date=currentDate,
                                               shift=currentShift,
                                               HM94=json.dumps(insertDict),
                                               Ver=1)
        elif target == 'pauseList81':
            insertDb = get_handover_health_map(date=currentDate,
                                               shift=currentShift,
                                               HM81=json.dumps(insertDict),
                                               Ver=1)
        elif target == 'pauseList82':
            insertDb = get_handover_health_map(date=currentDate,
                                               shift=currentShift,
                                               HM82=json.dumps(insertDict),
                                               Ver=1)
        insertDict['verion'] = 1
        db.session.add(insertDb)
        db.session.commit()
        db.session.close()
        db.session.remove()
    # return auditor, detail, lastCheckTime, status only
    return jsonify(insertDict)


@app_monitoringSystem.route('/return/hm/<target>')
def returnHmPage(target):
    with open(f'monitoringSystem/static/{target}.htm', 'r',
              errors='ignore') as file_object:
        bsObj = BeautifulSoup(file_object, 'lxml')
        returnList = []
        nameList = bsObj.findAll("td", {"class": "TFl"})
        # print(nameList)
        for i in nameList:
            returnList.append(i.get_text())
        # print(returnList)
    return render_template('pauseList.html', data=returnList)


@app_monitoringSystem.route('/Incident/query')
def incidentQuery():
    returnList = []
    result = get_customer_status_note.query.filter(
        get_customer_status_note.date.between(
            '2022-04-01',
            '2025-03-31')).order_by(get_customer_status_note.sn.desc()).all()
    for i in result:
        tmpDict = i.serialize
        tmpDict['customer'] = json.loads(tmpDict['customer'])
        tmpDict['jira_ticket'] = json.loads(tmpDict['jira_ticket'])
        tmpDict['date'] = f'{i.date}'
        tmpDict['event_start_time'] = f'{i.event_start_time}'
        tmpDict['event_end_time'] = f'{i.event_end_time}'
        returnList.append(tmpDict)
    return jsonify(returnList)
