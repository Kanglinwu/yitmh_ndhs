from tkinter import N
from flask import Blueprint, jsonify, request
from models import db, get_jsm_field_sets, get_jsm_field_sets_sortOut, get_jsm_mapping, get_jsm_mapping_prod, get_jsm_ops, get_jsm_ops_prod, get_jsm_ops_comments, get_jsm_net, get_jsm_net_prod, get_jsm_net_comments, get_jsm_sys, get_jsm_sys_comments, get_jsm_sys_prod, get_jsm_dba, get_jsm_dba_comments, get_jsm_dba_prod
from sqlalchemy import or_, and_

import datetime
import json
import requests
import asyncio
import time
import markdownify
import redis

import urllib3

urllib3.disable_warnings()

app_mainRoutine = Blueprint('app_mainRoutine', __name__)

qatHeaders = {
    "Accept":
    "application/json",
    "Content-Type":
    "application/json",
    'Authorization':
    'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
    'Cookie':
    'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_0163a28143f3879bcfd9f567a0d8c7dffe9c798b_lin'
}

prodHeaders = {
    'Accept':
    'application/json',
    'Content-Type':
    'application/json',
    'Authorization':
    'Basic c3J2Lm9wc2FwaUB5aXRtaC5jb206bzhWc2M0ZTBWdWFaTjNsdTY2dzVBNDUy',
    'Cookie':
    'atlassian.xsrf.token=06ef7867-f85e-4f6f-9b1f-33a446f98474_0012fa1428e8508be4216e59a2b1d11fa06a777f_lin'
}

convertHeaders = {
    'Authorization':
    'Basic c3J2Lm9wc0B5aXRtaC5jb206MFdxeFRMeUZySFdzbXRmZE9QZmJGMkJB',
    'charset':
    'utf-8',
    'Content-Type':
    'application/json',
    'Cookie':
    'atlassian.xsrf.token=06ef7867-f85e-4f6f-9b1f-33a446f98474_c3177274581f5c6da7eae2245f92f75123bf59c2_lin'
}


# # Get JSM Field Flow
# ~ 1
# https://okta.opsware.xyz:9486/bpRoutine/jsm/findTheContextId
# https://okta.opsware.xyz:9487/bpRoutine/jsm/findTheContextId
@app_mainRoutine.route('/jsm/findTheContextId')
def jsmRoutineFindTheContextId():
    # Jira OPS QAT Header
    headers = {
        "Accept":
        "application/json",
        "Content-Type":
        "application/json",
        'Authorization':
        'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
        'Cookie':
        'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_0163a28143f3879bcfd9f567a0d8c7dffe9c798b_lin'
    }

    # using this async function to call Jira API then get context id
    async def send_req(url, optionName, fieldId, headers):
        print(f'start to query - {url}')
        res = await loop.run_in_executor(
            None, lambda: requests.request("GET", url, headers=headers))
        print(f'end to query - {url}')
        tmpDict = {}
        tmpDict.setdefault("optionName", optionName)
        tmpDict.setdefault('fieldId', fieldId)
        tmpDict.setdefault('value', res.json())
        tmpDict.setdefault('timestamp', datetime.datetime.now())
        container.append(tmpDict)

    # current can't use this
    # netOptionList = ['Infra', 'Request Handler', 'Participant(s)', 'Category NET', 'Facilities', 'Start Time', 'End Time', 'Vendor support']
    # sysOptionList = ['Biz Units', 'Start Time', 'End Time', 'Category SYS', 'Request Handler', 'Participant(s)']
    # dbaOptionList = ['Biz Units', 'Request Handler', 'Participant(s)', 'Category DB', 'Service impact', 'Work Hour']
    # result = list(netOptionList)
    # result.extend(x for x in sysOptionList if x not in result)
    # result.extend(x for x in dbaOptionList if x not in result)

    optionNameList = [
        'Infra', 'Request Handler', 'Participant(s)', 'Category NET',
        'Facilities', 'Start Time', 'End Time', 'Vendor support', 'Biz Units',
        'Category SYS', 'Category DB', 'Work Hour', 'User impact',
        'Category OPS'
    ]
    fieldIdList = [
        'customfield_10071', 'customfield_10075', 'customfield_10077',
        'customfield_10088', 'customfield_10089', 'customfield_10067',
        'customfield_10068', 'customfield_10090', 'customfield_10070',
        'customfield_10087', 'customfield_10092', 'customfield_10091',
        'customfield_10093', 'customfield_10065'
    ]
    tasks = []  # async / await task list
    container = []  # jira api result container

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()

    for option, fieldId in zip(optionNameList, fieldIdList):
        url = f'https://anyhow-test4u.atlassian.net/rest/api/3/field/{fieldId}/context'
        task = loop.create_task(send_req(url, option, fieldId, headers))
        tasks.append(task)
        # print(option, '--', f'https://anyhow-test4u.atlassian.net/rest/api/3/field/{fieldId}/context')

    loop.run_until_complete(asyncio.wait(tasks))
    print('finish query JSM option')
    print('start to insert api result to DB table - JSM_field_sets')

    checkDbdata = [
        x.optionName for x in get_jsm_field_sets.query.filter(
            get_jsm_field_sets.env == 'anyhow-test4u.atlassian.net').all()
    ]  # query db and store all optionName on this list

    for i in container:
        if i['optionName'] in checkDbdata:
            # means db already has the column
            # print(f'hit update current data to table for {i}')
            for key, value in i.items():
                if key != 'value':
                    get_jsm_field_sets.query.filter(
                        get_jsm_field_sets.optionName ==
                        i['optionName']).update({key: value})
                db.session.commit()
        else:
            # means new column for this option
            # print(f'hit add new data to table for {i}')
            insertDb = get_jsm_field_sets(
                env='anyhow-test4u.atlassian.net',
                optionName=i['optionName'],
                fieldId=i['fieldId'],
                contextId=i['value']['values'][0]['id'])
            db.session.add(insertDb)
            db.session.commit()
    db.session.close()
    db.session.remove()

    print('finish to insert api result to DB table - JSM_field_sets')
    return 'ok'


# ~ 2
@app_mainRoutine.route('/jsm/updateTheFieldOptions')
def jsmRoutineupdateTheFieldOptions():
    # get local DB data
    resultSet = get_jsm_field_sets.query.filter(
        get_jsm_field_sets.env == 'anyhow-test4u.atlassian.net').all()
    # store the URL
    targetUrlSets = []
    for i in resultSet:
        # https://anyhow-test4u.atlassian.net/rest/api/3/field/customfield_10087/context/10189/option
        targetUrlSets.append((
            i.sn,
            f'https://{i.env}/rest/api/3/field/{i.fieldId}/context/{i.contextId}/option'
        ))

    # Jira OPS QAT Header
    headers = {
        "Accept":
        "application/json",
        "Content-Type":
        "application/json",
        'Authorization':
        'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
        'Cookie':
        'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_0163a28143f3879bcfd9f567a0d8c7dffe9c798b_lin'
    }

    tasks = []  # async / await task list
    container = []  # jira api result container

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()

    # using this async function to call Jira API then get context id
    async def send_req(url, sn, headers):
        print(f'start to query - {url}')
        try:
            res = await loop.run_in_executor(
                None, lambda: requests.request("GET", url, headers=headers))
            print(f'end to query - {url}')
            tmpDict = {}
            tmpDict.setdefault("sn", sn)
            tmpDict.setdefault('value', json.dumps(res.json()['values']))
            tmpDict.setdefault('timestamp', datetime.datetime.now())
            container.append(tmpDict)
        except Exception as e:
            print('###')
            print(e)
            print(sn)
            print('###')

    for (sn, url) in targetUrlSets:
        task = loop.create_task(send_req(url, sn, headers))
        tasks.append(task)

    loop.run_until_complete(asyncio.wait(tasks))

    for i in container:
        for key, value in i.items():
            get_jsm_field_sets.query.filter(
                get_jsm_field_sets.sn == i['sn']).update({key: value})
            db.session.commit()
    db.session.close()
    db.session.remove()
    return 'ok'


# ~ 3
@app_mainRoutine.route('/jsm/sortOutOption')
def jsmRoutineSortOutOption():
    resultList = get_jsm_field_sets.query.filter(
        get_jsm_field_sets.env == "anyhow-test4u.atlassian.net").all()
    containerList = []

    for i in resultList:
        if i.value:
            for ii in json.loads(i.value):
                tmpDict = {}
                tmpDict.setdefault('env', i.env)
                tmpDict.setdefault('optionName', i.optionName)
                tmpDict.setdefault('fieldId', i.fieldId)
                tmpDict.setdefault('contextId', i.contextId)
                tmpDict.setdefault('_id', ii['id'])
                tmpDict.setdefault('_value', ii['value'])
                containerList.append(tmpDict)

    # drop all
    db.session.query(get_jsm_field_sets_sortOut).filter(
        get_jsm_field_sets_sortOut.env ==
        "anyhow-test4u.atlassian.net").delete()
    db.session.commit()

    for x in containerList:
        insertDb = get_jsm_field_sets_sortOut(**x)
        db.session.add(insertDb)
        db.session.commit()
    db.session.close()
    db.session.remove()

    return 'ok'


def check_pull_status(_pattern, which_team):
    r = redis.StrictRedis(host='127.0.0.1', port=6379,
                          db=0, charset="utf-8", decode_responses=True)
    target_string_key = f'define_pull_{which_team}_request_status_is_ongoing'
    target_team = which_team.upper()
    if _pattern == 'ongoing':
        r.set(target_string_key, 'yes')
        print(
            f'[routine][{target_team}][Pull] - set the pull {which_team} request status to ongoing ( yes )')
    elif _pattern == 'stop':
        r.set(target_string_key, 'no')
        print(
            f'[routine][{target_team}][Pull] - set the pull {which_team} request status to stop ( no )')
    else:
        if r.get(target_string_key) == 'yes':
            # user can't access it, need to wait
            return True
        else:
            # user access it
            return False

# Worklog server query JSM service desk each team (OPS, NET, SYS, DBA) queue, and insert new ticket (created by customer), or update the reopen ticket
# https://okta.opsware.xyz:9486/bpRoutine/jsm/pull/ops
# https://okta.opsware.xyz:9487/bpRoutine/jsm/pull/ops


@app_mainRoutine.route('/jsm/pull/ops')
def jsmRoutinePullOps():
    # check the status
    if check_pull_status('check', 'ops') == False:
        check_pull_status('ongoing', 'ops')
        resultContainer = []
        # init the request start 0 and limit 20
        cLimit = 20
        cStart = 0
        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/573/issue?limit={cLimit}&start={cStart}"

        # 1 - query JSM Queue
        try:
            defineDone = True
            reTryCounter = 1
            while defineDone:
                curTime = datetime.datetime.now()
                print(f'[routine][OPS] - Pull {url} at {curTime}')
                response = requests.request("GET", url, headers=prodHeaders)
                if response.status_code == 200:
                    dict_response = response.json()
                    # update
                    for oneJsm in dict_response['values']:
                        resultContainer.append(oneJsm)
                    if dict_response['isLastPage'] == True:
                        defineDone = False
                    else:
                        cStart = cLimit + cStart
                        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/573/issue?limit={cLimit}&start={cStart}"
                else:
                    print(response.status_code)
                    if reTryCounter > 5:
                        defineDone = False
                    else:
                        reTryCounter += 1
                        time.sleep(2)
        except Exception as e:
            print(e)
            return 'Get ERROR when pull JSM OPS Ticket on while loop', 500

        if reTryCounter > 5:
            return 'Get Unexcept http status code when pull JSM OPS Ticket on while loop', 500

        # 2 - get all mapping db for ops - export issueId list and Dict
        allOpsMappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod._group == 'OPS').all()
        allOpsMappingResultIssueIdList = []
        allOpsMappingSortOutDict = {}
        for item in allOpsMappingResult:
            allOpsMappingResultIssueIdList.append(item.issueId)
            allOpsMappingSortOutDict.setdefault(item.issueId, item.sn)

        # which jsm ticket need to insert to mapping db
        addNewItemList = []
        # which jsm ticket need to check local db status
        checkItemList = []

        # 3 - local check
        for i in resultContainer:
            # customer send the mail to us, then create new ticket
            if i['id'] not in allOpsMappingResultIssueIdList:
                jsmKey = i['key']
                content_convert = convert_markdown(i['key'])
                tmpDict = {}
                tmpDict.setdefault('issueId', i['id'])
                tmpDict.setdefault('issueKey', i['key'])
                tmpDict.setdefault(
                    'issueUrl', f'https://ict888.atlassian.net/browse/{jsmKey}')
                tmpDict.setdefault('_group', 'OPS')
                tmpDict.setdefault('title', i['fields']['summary'])
                tmpDict.setdefault(
                    'description', 'AUTO PULL BY WORKLOG SERVER')
                tmpDict.setdefault('createdTime', i['fields']['created'])
                tmpDict.setdefault('startTime',
                                   datetime.datetime.fromtimestamp(626572800))
                tmpDict.setdefault('jiraStatus', i['fields']['status']['id'])
                tmpDict.setdefault('ticketStatus', 2)
                tmpDict.setdefault('custom_infra', json.dumps([]))
                tmpDict.setdefault('custom_category', '')
                tmpDict.setdefault('custom_bizUnit', json.dumps([]))
                tmpDict.setdefault('custom_handler', json.dumps([]))
                tmpDict.setdefault('content_raw', content_convert[0])
                tmpDict.setdefault('content_html', content_convert[1])
                addNewItemList.append(tmpDict)
            else:  # check if this ticket status is closed on local db
                # (mapping sn, issueId, issueKey, jsmStatus)
                tmpIssueId = i['id']
                tmpIssueKey = i['key']
                checkItemList.append(
                    (allOpsMappingSortOutDict[tmpIssueId], tmpIssueId, tmpIssueKey,
                     i['fields']['status']['id']))

        # 3-1 need to insert mapping db and comments db and local db
        if len(addNewItemList) != 0:
            for x in addNewItemList:
                curTime = datetime.datetime.now()
                targetIssueKey = x['issueKey']
                print(
                    f'[routine][OPS] - Add NEW JSM ticket - {targetIssueKey}')
                # insert mapping db
                insertMappingDb = get_jsm_mapping_prod(issueId=x['issueId'],
                                                       issueKey=x['issueKey'],
                                                       issueUrl=x['issueUrl'],
                                                       _group=x['_group'])
                db.session.add(insertMappingDb)
                db.session.commit()
                db.session.refresh(insertMappingDb)
                x.setdefault('mappingSn', insertMappingDb.sn)
            db.session.close()
            db.session.remove()

            for i in addNewItemList:
                # add new comment to record
                addOneRow = get_jsm_ops_comments(
                    issueKey=i['issueKey'],
                    handler='Bot',
                    commentType=2,
                    content='AUTO PULL BY WORKLOG SERVER')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                # insert local db
                insertLocalDb = get_jsm_ops_prod(
                    title=i['title'],
                    description=i['description'],
                    content_raw=i['content_raw'],
                    content_html=i['content_html'],
                    mapping=i['mappingSn'],
                    comments=json.dumps([commentDbSn]),
                    createdTime=datetime.datetime.strptime(
                        i['createdTime'], "%Y-%m-%dT%H:%M:%S.%f%z"),
                    startTime=i['startTime'],
                    jiraStatus=int(i['jiraStatus']),
                    ticketStatus=i['ticketStatus'],
                    custom_infra=i['custom_infra'],
                    custom_bizUnit=i['custom_bizUnit'],
                    custom_category=i['custom_category'],
                    custom_handler=i['custom_handler'])
                db.session.add(insertLocalDb)
                db.session.commit()
            db.session.close()
            db.session.remove()
        else:
            curTime = datetime.datetime.now()
            print(
                f'[routine][OPS] - Pull result: does not exist any new ticket at {curTime}'
            )

        # 3-2 need to check if ticket has been closed on local db
        if len(checkItemList) != 0:
            for i in checkItemList:
                # (mapping sn, issueId, issueKey, jsmStatus)
                checkJSMstatus = get_jsm_ops_prod.query.filter(
                    get_jsm_ops_prod.mapping == int(i[0])).first()
                # means ticket has been closed, but now status change
                if checkJSMstatus.jiraStatus == 71 or checkJSMstatus.jiraStatus == 121 or checkJSMstatus.jiraStatus == 6:
                    curTime = datetime.datetime.now()
                    targetIssueKey = i[2]
                    print(
                        f'[routine][OPS] - CLOSE JSM ticket Reopen - {targetIssueKey} at {curTime}'
                    )
                    # add new comment
                    addOneRow = get_jsm_ops_comments(
                        issueKey=i[2],
                        handler='Bot',
                        content=f'CLOSE TICKET STATUS CHANGE')
                    db.session.add(addOneRow)
                    db.session.commit()
                    db.session.refresh(addOneRow)
                    commentDbSn = addOneRow.sn  # get comment sn
                    # update the jsm ticket status and comment list
                    # # update comments
                    tmpCommentsList = json.loads(checkJSMstatus.comments)
                    tmpCommentsList.append(commentDbSn)
                    checkJSMstatus.comments = json.dumps(tmpCommentsList)
                    # # update status
                    checkJSMstatus.jiraStatus = int(i[3])
                    checkJSMstatus.ticketStatus = 2
                    db.session.commit()
            db.session.close()
            db.session.remove()
        check_pull_status('stop', 'ops')
        return 'ok'
    else:
        print('[Pull][OPS] - Wait for other ppl ongoing the request, wait 3 second')
        # local counter, avoid check key due to some issue cause value is 'yes'
        local_counter = 1
        while check_pull_status('check', 'ops') == True:
            if local_counter > 3:
                check_pull_status('stop', 'ops')
                break
            else:
                local_counter += 1
                time.sleep(3)
        return jsmRoutinePullOps()


@app_mainRoutine.route('/jsm/pull/net')
def jsmProdRoutinePullNet():
    resultContainer = []
    if check_pull_status('check', 'net') == False:
        check_pull_status('ongoing', 'net')

        # init the request start 0 and limit 20
        cLimit = 20
        cStart = 0
        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/576/issue?limit={cLimit}&start={cStart}"
        # url = f"https://anyhow-test4u.atlassian.net/rest/servicedeskapi/servicedesk/1/queue/23/issue?limit={cLimit}&start={cStart}"

        # 1 - query JSM Queue
        try:
            defineDone = True
            reTryCounter = 1
            while defineDone:
                curTime = datetime.datetime.now()
                print(f'[routine][NET] - Pull {url} at {curTime}')
                response = requests.request("GET", url, headers=prodHeaders)
                if response.status_code == 200:
                    dict_response = response.json()
                    # update
                    for oneJsm in dict_response['values']:
                        resultContainer.append(oneJsm)
                    if dict_response['isLastPage'] == True:
                        defineDone = False
                    else:
                        cStart = cLimit + cStart
                        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/576/issue?limit={cLimit}&start={cStart}"
                        # url = f"https://anyhow-test4u.atlassian.net/rest/servicedeskapi/servicedesk/1/queue/23/issue?limit={cLimit}&start={cStart}"
                else:
                    print(response.status_code)
                    if reTryCounter > 5:
                        defineDone = False
                    else:
                        reTryCounter += 1
                        time.sleep(2)
        except Exception as e:
            print(e)
            return 'Get ERROR when query JSM on while loop', 500

        if reTryCounter > 5:
            return 'Get Unexcept http status code when query JSM on while loop', 500

        # 2 - get all mapping db for net - export issueId list and Dict
        allNetMappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod._group == 'NET').all()
        allNetMappingResultIssueIdList = []
        allNetMappingSortOutDict = {}
        for item in allNetMappingResult:
            allNetMappingResultIssueIdList.append(item.issueId)
            allNetMappingSortOutDict.setdefault(item.issueId, item.sn)

        # which jsm ticket need to insert to mapping db
        addNewItemList = []
        # which jsm ticket need to check local db status
        checkItemList = []

        # 3 - local check
        for i in resultContainer:
            # customer send the mail to us, then create new ticket
            if i['id'] not in allNetMappingResultIssueIdList:
                jsmKey = i['key']
                content_convert = convert_markdown(i['key'])
                tmpDict = {}
                tmpDict.setdefault('issueId', i['id'])
                tmpDict.setdefault('issueKey', i['key'])
                tmpDict.setdefault(
                    'issueUrl', f'https://ict888.atlassian.net/browse/{jsmKey}')
                tmpDict.setdefault('_group', 'NET')
                tmpDict.setdefault('title', i['fields']['summary'])
                tmpDict.setdefault(
                    'description', 'AUTO PULL BY WORKLOG SERVER')
                tmpDict.setdefault('createdTime', i['fields']['created'])
                # tmpDict.setdefault('startTime', datetime.datetime.now()) # avoid start time not match
                tmpDict.setdefault('jiraStatus', i['fields']['status']['id'])
                tmpDict.setdefault('ticketStatus', 2)
                tmpDict.setdefault('custom_infra', json.dumps([]))
                tmpDict.setdefault('custom_category', '')
                tmpDict.setdefault('custom_facilities', json.dumps([]))
                tmpDict.setdefault('custom_facilities', json.dumps([]))
                tmpDict.setdefault('custom_handler', json.dumps([]))
                tmpDict.setdefault('content_raw', content_convert[0])
                tmpDict.setdefault('content_html', content_convert[1])
                addNewItemList.append(tmpDict)
            else:  # check if this ticket status is closed on local db
                # (mapping sn, issueId, issueKey, jsmStatus)
                tmpIssueId = i['id']
                tmpIssueKey = i['key']
                checkItemList.append(
                    (allNetMappingSortOutDict[tmpIssueId], tmpIssueId, tmpIssueKey,
                     i['fields']['status']['id']))

        # 3-1 need to insert mapping db and comments db and local db
        if len(addNewItemList) != 0:
            for x in addNewItemList:
                curTime = datetime.datetime.now()
                targetIssueKey = x['issueKey']
                print(
                    f'[routine][NET] - Add NEW JSM ticket - {targetIssueKey}')
                # insert mapping db
                insertMappingDb = get_jsm_mapping_prod(issueId=x['issueId'],
                                                       issueKey=x['issueKey'],
                                                       issueUrl=x['issueUrl'],
                                                       _group=x['_group'])
                db.session.add(insertMappingDb)
                db.session.commit()
                db.session.refresh(insertMappingDb)
                x.setdefault('mappingSn', insertMappingDb.sn)
            db.session.close()
            db.session.remove()

            for i in addNewItemList:
                # add new comment to record
                addOneRow = get_jsm_net_comments(
                    issueKey=i['issueKey'],
                    handler='Bot',
                    content='AUTO PULL BY WORKLOG SERVER')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                # insert local db
                insertLocalDb = get_jsm_net_prod(
                    title=i['title'],
                    description=i['description'],
                    mapping=i['mappingSn'],
                    comments=json.dumps([commentDbSn]),
                    createdTime=datetime.datetime.strptime(
                        i['createdTime'], "%Y-%m-%dT%H:%M:%S.%f%z"),
                    # startTime=i['startTime'],
                    jiraStatus=int(i['jiraStatus']),
                    ticketStatus=i['ticketStatus'],
                    custom_infra=i['custom_infra'],
                    custom_category=i['custom_category'],
                    custom_facilities=i['custom_facilities'],
                    custom_handler=i['custom_handler'])
                db.session.add(insertLocalDb)
                db.session.commit()
            db.session.close()
            db.session.remove()
        else:
            curTime = datetime.datetime.now()
            print(
                f'[routine][NET] - Pull result: does not exist any new ticket at {curTime}'
            )

        # 3-2 need to check if ticket has been closed on local db
        if len(checkItemList) != 0:
            for i in checkItemList:
                # (mapping sn, issueId, issueKey, jsmStatus)
                checkJSMstatus = get_jsm_net_prod.query.filter(
                    get_jsm_net_prod.mapping == int(i[0])).first()
                # means ticket has been closed, but now status change
                if checkJSMstatus.jiraStatus == 71 or checkJSMstatus.jiraStatus == 121 or checkJSMstatus.jiraStatus == 6:
                    curTime = datetime.datetime.now()
                    targetIssueKey = i[2]
                    print(
                        f'[routine][NET] - CLOSE NET JSM ticket Reopen - {targetIssueKey} at {curTime}'
                    )
                    # add new comment
                    addOneRow = get_jsm_net_comments(
                        issueKey=i[2],
                        handler='Bot',
                        content=f'CLOSE TICKET STATUS CHANGE')
                    db.session.add(addOneRow)
                    db.session.commit()
                    db.session.refresh(addOneRow)
                    commentDbSn = addOneRow.sn  # get comment sn
                    # update the jsm ticket status and comment list
                    # # update comments
                    tmpCommentsList = json.loads(checkJSMstatus.comments)
                    tmpCommentsList.append(commentDbSn)
                    checkJSMstatus.comments = json.dumps(tmpCommentsList)
                    # # update jira status
                    checkJSMstatus.jiraStatus = int(i[3])
                    # # update ticket status to 2
                    checkJSMstatus.ticketStatus = 2
                    db.session.commit()
            db.session.close()
            db.session.remove()
        check_pull_status('stop', 'net')
        return 'ok'
    else:
        print('[Pull][NET] - Wait for other ppl ongoing the request, wait 3 second')
        # local counter, avoid check key due to some issue cause value is 'yes'
        local_counter = 1
        while check_pull_status('check', 'net') == True:
            if local_counter > 3:
                check_pull_status('stop', 'net')
                break
            else:
                local_counter += 1
                time.sleep(3)
        return jsmProdRoutinePullNet()

# https://okta.opsware.xyz:9486/bpRoutine/jsm/pull/sys


@app_mainRoutine.route('/jsm/pull/sys')
def jsmRoutinePullSys():
    resultContainer = []
    if check_pull_status('check', 'sys') == False:
        check_pull_status('ongoing', 'sys')

        # init the request start 0 and limit 20
        cLimit = 20
        cStart = 0
        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/574/issue?limit={cLimit}&start={cStart}"

        # 1 - query JSM Queue
        try:
            defineDone = True
            reTryCounter = 1
            while defineDone:
                curTime = datetime.datetime.now()
                print(f'[routine][SYS] - Pull {url} at {curTime}')
                response = requests.request("GET", url, headers=prodHeaders)
                if response.status_code == 200:
                    dict_response = response.json()
                    # update
                    for oneJsm in dict_response['values']:
                        resultContainer.append(oneJsm)
                    if dict_response['isLastPage'] == True:
                        defineDone = False
                    else:
                        cStart = cLimit + cStart
                        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/574/issue?limit={cLimit}&start={cStart}"
                else:
                    print(response.status_code)
                    if reTryCounter > 5:
                        defineDone = False
                    else:
                        reTryCounter += 1
                        time.sleep(2)
        except Exception as e:
            print(e)
            return 'Get ERROR when pull JSM SYS Ticket on while loop', 500

        if reTryCounter > 5:
            return 'Get Unexcept http status code when pull JSM SYS Ticket on while loop', 500

        # 2 - get all mapping db for sys - export issueId list and Dict
        allSysMappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod._group == 'SYS').all()
        allSysMappingResultIssueIdList = []
        allSysMappingSortOutDict = {}
        for item in allSysMappingResult:
            allSysMappingResultIssueIdList.append(item.issueId)
            allSysMappingSortOutDict.setdefault(item.issueId, item.sn)

        # which jsm ticket need to insert to mapping db
        addNewItemList = []
        # which jsm ticket need to check local db status
        checkItemList = []

        # 3 - local check
        for i in resultContainer:
            # customer send the mail to us, then create new ticket
            if i['id'] not in allSysMappingResultIssueIdList:
                jsmKey = i['key']
                content_convert = convert_markdown(i['key'])
                tmpDict = {}
                tmpDict.setdefault('issueId', i['id'])
                tmpDict.setdefault('issueKey', i['key'])
                tmpDict.setdefault(
                    'issueUrl',
                    f'https://anyhow-test4u.atlassian.net/browse/{jsmKey}')
                tmpDict.setdefault('_group', 'SYS')
                tmpDict.setdefault('title', i['fields']['summary'])
                tmpDict.setdefault(
                    'description', 'AUTO PULL BY WORKLOG SERVER')
                tmpDict.setdefault('createdTime', i['fields']['created'])
                # tmpDict.setdefault('startTime', datetime.datetime.now())
                tmpDict.setdefault('jiraStatus', i['fields']['status']['id'])
                tmpDict.setdefault('ticketStatus', 2)
                tmpDict.setdefault('custom_bizUnit', json.dumps([]))
                tmpDict.setdefault('custom_category', json.dumps([]))
                tmpDict.setdefault('custom_priority', '')
                tmpDict.setdefault('custom_handler', json.dumps([]))
                tmpDict.setdefault('content_raw', content_convert[0])
                tmpDict.setdefault('content_html', content_convert[1])
                addNewItemList.append(tmpDict)
            else:  # check if this ticket status is closed on local db
                # (mapping sn, issueId, issueKey, jsmStatus)
                tmpIssueId = i['id']
                tmpIssueKey = i['key']
                checkItemList.append(
                    (allSysMappingSortOutDict[tmpIssueId], tmpIssueId, tmpIssueKey,
                     i['fields']['status']['id']))

        # 3-1 need to insert mapping db and comments db and local db
        if len(addNewItemList) != 0:
            for x in addNewItemList:
                curTime = datetime.datetime.now()
                targetIssueKey = x['issueKey']
                print(
                    f'[routine][SYS] - Add NEW JSM ticket - {targetIssueKey}')
                # insert mapping db
                insertMappingDb = get_jsm_mapping_prod(issueId=x['issueId'],
                                                       issueKey=x['issueKey'],
                                                       issueUrl=x['issueUrl'],
                                                       _group=x['_group'])
                db.session.add(insertMappingDb)
                db.session.commit()
                db.session.refresh(insertMappingDb)
                x.setdefault('mappingSn', insertMappingDb.sn)
            db.session.close()
            db.session.remove()

            for i in addNewItemList:
                # add new comment to record
                addOneRow = get_jsm_sys_comments(
                    issueKey=i['issueKey'],
                    handler='Bot',
                    content='AUTO PULL BY WORKLOG SERVER')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                # insert local db
                insertLocalDb = get_jsm_sys_prod(
                    title=i['title'],
                    description=i['description'],
                    mapping=i['mappingSn'],
                    comments=json.dumps([commentDbSn]),
                    createdTime=datetime.datetime.strptime(
                        i['createdTime'], "%Y-%m-%dT%H:%M:%S.%f%z"),
                    # startTime=i['startTime'],
                    jiraStatus=int(i['jiraStatus']),
                    ticketStatus=i['ticketStatus'],
                    custom_category=i['custom_category'],
                    custom_bizUnit=i['custom_bizUnit'],
                    custom_priority=i['custom_priority'],
                    custom_handler=i['custom_handler'])
                db.session.add(insertLocalDb)
                db.session.commit()
            db.session.close()
            db.session.remove()
        else:
            curTime = datetime.datetime.now()
            print(
                f'[routine][SYS] - Pull result: does not exist any new ticket at {curTime}'
            )

        # 3-2 need to check if ticket has been closed on local db
        if len(checkItemList) != 0:
            for i in checkItemList:
                print(i)
                # (mapping sn, issueId, issueKey, jsmStatus)
                checkJSMstatus = get_jsm_sys_prod.query.filter(
                    get_jsm_sys_prod.mapping == int(i[0])).first()
                # means ticket has been closed, but now status change
                if checkJSMstatus.jiraStatus == 71 or checkJSMstatus.jiraStatus == 121 or checkJSMstatus.jiraStatus == 6:
                    curTime = datetime.datetime.now()
                    targetIssueKey = i[2]
                    print(
                        f'[routine][SYS] - CLOSE SYS JSM ticket Reopen - {targetIssueKey} at {curTime}'
                    )
                    # add new comment
                    addOneRow = get_jsm_sys_comments(
                        issueKey=i[2],
                        handler='Bot',
                        content=f'CLOSE TICKET STATUS CHANGE')
                    db.session.add(addOneRow)
                    db.session.commit()
                    db.session.refresh(addOneRow)
                    commentDbSn = addOneRow.sn  # get comment sn
                    # update the jsm ticket status and comment list
                    # # update comments
                    tmpCommentsList = json.loads(checkJSMstatus.comments)
                    tmpCommentsList.append(commentDbSn)
                    checkJSMstatus.comments = json.dumps(tmpCommentsList)
                    # # update status
                    checkJSMstatus.jiraStatus = int(i[3])
                    checkJSMstatus.ticketStatus = 2
                    db.session.commit()
            db.session.close()
            db.session.remove()
        check_pull_status('stop', 'sys')
        return 'ok'
    else:
        print('[Pull][SYS] - Wait for other ppl ongoing the request, wait 3 second')
        # local counter, avoid check key due to some issue cause value is 'yes'
        local_counter = 1
        while check_pull_status('check', 'sys') == True:
            if local_counter > 3:
                check_pull_status('stop', 'sys')
                break
            else:
                local_counter += 1
                time.sleep(3)
        return jsmRoutinePullSys()


@app_mainRoutine.route('/jsm/pull/dba')
def jsmRoutinePullDba():
    resultContainer = []
    if check_pull_status('check', 'dba') == False:
        check_pull_status('ongoing', 'dba')

        # init the request start 0 and limit 20
        cLimit = 20
        cStart = 0
        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/575/issue?limit={cLimit}&start={cStart}"

        # 1 - query JSM Queue
        try:
            defineDone = True
            reTryCounter = 1
            while defineDone:
                curTime = datetime.datetime.now()
                print(f'[routine][DBA] - Pull {url} at {curTime}')
                response = requests.request("GET", url, headers=prodHeaders)
                if response.status_code == 200:
                    dict_response = response.json()
                    # update
                    for oneJsm in dict_response['values']:
                        resultContainer.append(oneJsm)
                    if dict_response['isLastPage'] == True:
                        defineDone = False
                    else:
                        cStart = cLimit + cStart
                        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/21/queue/575/issue?limit={cLimit}&start={cStart}"
                else:
                    print(response.status_code)
                    if reTryCounter > 5:
                        defineDone = False
                    else:
                        reTryCounter += 1
                        time.sleep(2)
        except Exception as e:
            print(e)
            return 'Get ERROR when pull JSM DBA Ticket on while loop', 500

        if reTryCounter > 5:
            return 'Get Unexcept http status code when pull JSM DBA Ticket on while loop', 500

        # 2 - get all mapping db for sys - export issueId list and Dict
        allDbaMappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod._group == 'DBA').all()
        allDbaMappingResultIssueIdList = []
        allDbaMappingSortOutDict = {}
        for item in allDbaMappingResult:
            allDbaMappingResultIssueIdList.append(item.issueId)
            allDbaMappingSortOutDict.setdefault(item.issueId, item.sn)

        # which jsm ticket need to insert to mapping db
        addNewItemList = []
        # which jsm ticket need to check local db status
        checkItemList = []

        # 3 - local check
        for i in resultContainer:
            # customer send the mail to us, then create new ticket
            if i['id'] not in allDbaMappingResultIssueIdList:
                jsmKey = i['key']
                content_convert = convert_markdown(i['key'])
                tmpDict = {}
                tmpDict.setdefault('issueId', i['id'])
                tmpDict.setdefault('issueKey', i['key'])
                tmpDict.setdefault(
                    'issueUrl', f'https://ict888.atlassian.net/browse/{jsmKey}')
                tmpDict.setdefault('_group', 'DBA')
                tmpDict.setdefault('title', i['fields']['summary'])
                tmpDict.setdefault(
                    'description', 'AUTO PULL BY WORKLOG SERVER')
                tmpDict.setdefault('createdTime', i['fields']['created'])
                tmpDict.setdefault('startTime',
                                   datetime.datetime.fromtimestamp(626572800))
                tmpDict.setdefault('endTime',
                                   datetime.datetime.fromtimestamp(626572800))
                tmpDict.setdefault('jiraStatus', i['fields']['status']['id'])
                tmpDict.setdefault('ticketStatus', 2)
                tmpDict.setdefault('custom_bizUnit', json.dumps([]))
                tmpDict.setdefault('custom_category', json.dumps([]))
                tmpDict.setdefault('custom_handler', json.dumps([]))
                tmpDict.setdefault('custom_priority', '')
                tmpDict.setdefault('custom_isImpact', 0)
                tmpDict.setdefault('content_raw', content_convert[0])
                tmpDict.setdefault('content_html', content_convert[1])
                addNewItemList.append(tmpDict)
            else:  # check if this ticket status is closed on local db
                # (mapping sn, issueId, issueKey, jsmStatus)
                tmpIssueId = i['id']
                tmpIssueKey = i['key']
                checkItemList.append(
                    (allDbaMappingSortOutDict[tmpIssueId], tmpIssueId, tmpIssueKey,
                     i['fields']['status']['id']))

        # 3-1 need to insert mapping db and comments db and local db
        if len(addNewItemList) != 0:
            for x in addNewItemList:
                curTime = datetime.datetime.now()
                targetIssueKey = x['issueKey']
                print(
                    f'[routine][DBA] - Add NEW JSM ticket - {targetIssueKey}')
                # insert mapping db
                insertMappingDb = get_jsm_mapping_prod(issueId=x['issueId'],
                                                       issueKey=x['issueKey'],
                                                       issueUrl=x['issueUrl'],
                                                       _group=x['_group'])
                db.session.add(insertMappingDb)
                db.session.commit()
                db.session.refresh(insertMappingDb)
                x.setdefault('mappingSn', insertMappingDb.sn)
            db.session.close()
            db.session.remove()

            for i in addNewItemList:
                # add new comment to record
                addOneRow = get_jsm_dba_comments(
                    issueKey=i['issueKey'],
                    handler='Bot',
                    content='AUTO PULL BY WORKLOG SERVER')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                # insert local db
                insertLocalDb = get_jsm_dba_prod(
                    title=i['title'],
                    description=i['description'],
                    mapping=i['mappingSn'],
                    comments=json.dumps([commentDbSn]),
                    createdTime=datetime.datetime.strptime(
                        i['createdTime'], "%Y-%m-%dT%H:%M:%S.%f%z"),
                    startTime=i['startTime'],
                    endTime=i['endTime'],
                    jiraStatus=int(i['jiraStatus']),
                    ticketStatus=i['ticketStatus'],
                    custom_category=i['custom_category'],
                    custom_bizUnit=i['custom_bizUnit'],
                    custom_priority=i['custom_priority'],
                    custom_isImpact=i['custom_isImpact'],
                    custom_handler=i['custom_handler'])
                db.session.add(insertLocalDb)
                db.session.commit()
            db.session.close()
            db.session.remove()
        else:
            curTime = datetime.datetime.now()
            print(
                f'[routine][DBA] - Pull result: does not exist any new ticket at {curTime}'
            )

        # 3-2 need to check if ticket has been closed on local db
        if len(checkItemList) != 0:
            for i in checkItemList:
                # (mapping sn, issueId, issueKey, jsmStatus)
                checkJSMstatus = get_jsm_dba_prod.query.filter(
                    get_jsm_dba_prod.mapping == int(i[0])).first()
                # means ticket has been closed, but now status change
                if checkJSMstatus.jiraStatus == 71 or checkJSMstatus.jiraStatus == 121 or checkJSMstatus.jiraStatus == 6:
                    curTime = datetime.datetime.now()
                    targetIssueKey = i[2]
                    print(
                        f'[routine][DBA] - CLOSE JSM ticket Reopen - {targetIssueKey} at {curTime}'
                    )
                    # add new comment
                    addOneRow = get_jsm_dba_comments(
                        issueKey=i[2],
                        handler='Bot',
                        content=f'CLOSE TICKET STATUS CHANGE')
                    db.session.add(addOneRow)
                    db.session.commit()
                    db.session.refresh(addOneRow)
                    commentDbSn = addOneRow.sn  # get comment sn
                    # update the jsm ticket status and comment list
                    # # update comments
                    tmpCommentsList = json.loads(checkJSMstatus.comments)
                    tmpCommentsList.append(commentDbSn)
                    checkJSMstatus.comments = json.dumps(tmpCommentsList)
                    # # update status
                    checkJSMstatus.jiraStatus = int(i[3])
                    checkJSMstatus.ticketStatus = 2
                    db.session.commit()
            db.session.close()
            db.session.remove()
        check_pull_status('stop', 'dba')
        return 'ok'
    else:
        print('[Pull][DBA] - Wait for other ppl ongoing the request, wait 3 second')
        # local counter, avoid check key due to some issue cause value is 'yes'
        local_counter = 1
        while check_pull_status('check', 'dba') == True:
            if local_counter > 3:
                check_pull_status('stop', 'dba')
                break
            else:
                local_counter += 1
                time.sleep(3)
        return jsmRoutinePullDba()


# https://okta.opsware.xyz:9486/bpRoutine/jsm/statusOption
@app_mainRoutine.route('/jsm/statusOption', methods=['GET', 'POST'])
def jsmStatusOption():
    # # frontend data
    # { "curStatus": 4, "issueId": 11815, "issueKey": "YTS-1796", "action": "query" }
    # # return - when action is query
    # itemOption.value = [{ label: 'Completed', value: 61, color: 'secondary' }, { label: 'Canceled', value: 211, color: 'secondary' }]
    front_data = request.get_json(silent=True)
    issueId = front_data['issueId']
    issueKey = front_data['issueKey']
    localDnSn = front_data['localDbSn']
    whichTeam = front_data['whichTeam']
    returnList = []
    nextStatusNameurl = f'https://ict888.atlassian.net/rest/api/3/issue/{issueId}/transitions'
    defineDone = True
    reTryTime = 1
    try:
        while defineDone:
            nextStatusNameRes = requests.request("GET",
                                                 nextStatusNameurl,
                                                 headers=prodHeaders)
            if nextStatusNameRes.status_code == 200:
                resultDict = nextStatusNameRes.json()
                defineDone = False
                print(
                    f'[{issueKey}][Routine] - Query transitions from JSM Successful'
                )
            else:
                if reTryTime > 5:
                    defineDone = False
                else:
                    print(
                        f'[{issueKey}][Routine] - Query transitions from JSM Failed (x{reTryTime}) - Get unexpected http code ({nextStatusNameRes.status_code})'
                    )
                    reTryTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return f'[{issueKey}][Routine] - Query transitions from JSM Failed during query JSM status option [Exception]', 500

    if reTryTime > 5:
        return f'[{issueKey}][Routine] - Query transitions from JSM Failed during query JSM status option [Unexpected Http code]', 500
    else:
        if whichTeam == 'NET':
            print(resultDict)
            for i in resultDict['transitions']:
                if i['to']['id'] == '10114':  # custom cancel reason
                    returnList.append(
                        dict(label='Canceled - Declined',
                             value=[
                                 i['id'], i['to']['id'], 'Canceled - Declined'
                             ],
                             color='secondary'))
                    returnList.append(
                        dict(label='Canceled - Duplicate',
                             value=[
                                 i['id'], i['to']['id'], 'Canceled - Duplicate'
                             ],
                             color='secondary'))
                elif i['to'][
                        'id'] == '10129':  # check if user miss any columns
                    resultDb = get_jsm_net_prod.query.filter(
                        get_jsm_net_prod.sn == localDnSn).first()
                    missList = []
                    if len(json.loads(resultDb.custom_infra)) == 0:
                        missList.append('infra')
                    if resultDb.custom_category == '':
                        missList.append('category')
                    if len(json.loads(resultDb.custom_facilities)) == 0:
                        missList.append('facilities')
                    if len(json.loads(resultDb.custom_handler)) == 0:
                        missList.append('handler')
                    if len(missList) == 0:
                        returnList.append(
                            dict(label=i['to']['name'],
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                            ],
                                color='secondary'))
                    else:
                        tmpName = i['to']['name']
                        missString = ', '.join(missList)
                        newLabel = f'{tmpName} - Miss {missString}'
                        returnList.append(
                            dict(label=newLabel,
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                                 ],
                                 color='secondary',
                                 disable=True))
                else:
                    returnList.append(
                        dict(label=i['to']['name'],
                             value=[i['id'], i['to']['id'], i['to']['name']],
                             color='secondary'))
        elif whichTeam == 'SYS':
            for i in resultDict['transitions']:
                if i['to']['id'] == '10129':
                    resultDb = get_jsm_sys_prod.query.filter(
                        get_jsm_sys_prod.sn == localDnSn).first()
                    missList = []
                    if len(json.loads(resultDb.custom_bizUnit)) == 0:
                        missList.append('bizUnit')
                    if len(json.loads(resultDb.custom_category)) == 0:
                        missList.append('category')
                    if len(json.loads(resultDb.custom_handler)) == 0:
                        missList.append('handler')
                    if resultDb.custom_priority == '':
                        missList.append('priority')

                    if len(missList) == 0:
                        returnList.append(
                            dict(label=i['to']['name'],
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                            ],
                                color='secondary'))
                    else:
                        tmpName = i['to']['name']
                        missString = ', '.join(missList)
                        newLabel = f'{tmpName} - Miss {missString}'
                        returnList.append(
                            dict(label=newLabel,
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                                 ],
                                 color='secondary',
                                 disable=True))
                else:
                    returnList.append(
                        dict(label=i['to']['name'],
                             value=[i['id'], i['to']['id'], i['to']['name']],
                             color='secondary'))
        elif whichTeam == 'DBA':
            for i in resultDict['transitions']:
                if i['to']['id'] == '10129':
                    resultDb = get_jsm_dba_prod.query.filter(
                        get_jsm_dba_prod.sn == localDnSn).first()
                    missList = []
                    if len(json.loads(resultDb.custom_bizUnit)) == 0:
                        missList.append('bizUnit')
                    if len(json.loads(resultDb.custom_category)) == 0:
                        missList.append('category')
                    if len(json.loads(resultDb.custom_handler)) == 0:
                        missList.append('handler')
                    if resultDb.custom_priority == '':
                        missList.append('priority')
                    if resultDb.custom_workLogValue == None:
                        missList.append('Working Minutes')

                    if len(missList) == 0:
                        returnList.append(
                            dict(label=i['to']['name'],
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                            ],
                                color='secondary'))
                    else:
                        tmpName = i['to']['name']
                        missString = ', '.join(missList)
                        newLabel = f'{tmpName} - Miss {missString}'
                        returnList.append(
                            dict(label=newLabel,
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                                 ],
                                 color='secondary',
                                 disable=True))
                else:
                    returnList.append(
                        dict(label=i['to']['name'],
                             value=[i['id'], i['to']['id'], i['to']['name']],
                             color='secondary'))
        elif whichTeam == 'OPS':
            for i in resultDict['transitions']:
                if i['to']['id'] == '10129':
                    resultDb = get_jsm_ops_prod.query.filter(
                        get_jsm_ops_prod.sn == localDnSn).first()
                    missList = []
                    if resultDb.custom_category == '':
                        missList.append('category')
                    if len(json.loads(resultDb.custom_bizUnit)) == 0:
                        missList.append('bizUnit')
                    if len(json.loads(resultDb.custom_infra)) == 0:
                        missList.append('infra')
                    if len(json.loads(resultDb.custom_handler)) == 0:
                        missList.append('handler')
                    if len(missList) == 0:
                        returnList.append(
                            dict(label=i['to']['name'],
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                            ],
                                color='secondary'))
                    else:
                        tmpName = i['to']['name']
                        missString = ', '.join(missList)
                        newLabel = f'{tmpName} - Miss {missString}'
                        returnList.append(
                            dict(label=newLabel,
                                 value=[
                                     i['id'], i['to']['id'], i['to']['name']
                                 ],
                                 color='secondary',
                                 disable=True))
                else:
                    returnList.append(
                        dict(label=i['to']['name'],
                             value=[i['id'], i['to']['id'], i['to']['name']],
                             color='secondary'))
        return jsonify(returnList)


@app_mainRoutine.route('/jsm/reopen', methods=['GET', 'POST'])
def jsmReopenTicket():
    # {'group': 'SYS', 'issueKey': 'YTS-1992', 'editor': 'Paul.Chen', 'localDbSn': 107}
    front_data = request.get_json(silent=True)
    print(front_data)
    whichTeam = front_data['group']
    issueKey = front_data['issueKey']
    issueId = front_data['issueId']
    editor = front_data['editor']
    localDbSn = front_data['localDbSn']

    # 1 - check the next transitions id
    nextStatusNameurl = f'https://ict888.atlassian.net/rest/api/3/issue/{issueKey}/transitions'
    defineDone = True
    reTryTime = 1
    try:
        while defineDone:
            nextStatusNameRes = requests.request("GET",
                                                 nextStatusNameurl,
                                                 headers=prodHeaders)
            if nextStatusNameRes.status_code == 200:
                resultDict = nextStatusNameRes.json()
                defineDone = False
                print(
                    f'[{issueKey}][Reopen] - Query transitions from JSM Successful'
                )
            else:
                if reTryTime > 5:
                    defineDone = False
                else:
                    print(
                        f'[{issueKey}][Reopen] - Query transitions from JSM Failed (x{reTryTime}) - Get unexpected http code ({nextStatusNameRes.status_code})'
                    )
                    reTryTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return f'[{issueKey}][Routine] - Query transitions from JSM Failed during query JSM status option [Exception]', 500

    if reTryTime > 5:
        return f'[{issueKey}][Routine] - Query transitions from JSM Failed during query JSM status option [Unexpected Http code]', 500
    else:
        nextTransitionsId = resultDict['transitions'][0]['id']
        newStatusId = resultDict['transitions'][0]['to']['id']
        newStatusName = resultDict['transitions'][0]['to']['name']

    # prepare the payload to change the status
    try:
        payloadDict = {}
        payloadDict.setdefault('targetJSMSn', localDbSn)
        payloadDict.setdefault('jsmIssueId', issueId)
        payloadDict.setdefault('jsmIssueKey', issueKey)
        payloadDict.setdefault('toWhichStatus',
                               [nextTransitionsId, newStatusId, newStatusName])
        payloadDict.setdefault('editor', editor)
        payload = json.dumps(payloadDict)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        if whichTeam == 'NET':
            targetUrl = 'https://okta.opsware.xyz:9487/bpCowork/jsm/net/update/status'
        elif whichTeam == 'DBA':
            targetUrl = 'https://okta.opsware.xyz:9487/bpCowork/jsm/dba/update/status'
        elif whichTeam == 'SYS':
            targetUrl = 'https://okta.opsware.xyz:9487/bpCowork/jsm/sys/update/status'
        elif whichTeam == 'OPS':
            targetUrl = 'https://okta.opsware.xyz:9487/bpCowork/jsm/ops/update/status'

        callInternalUrl = requests.request("POST",
                                           targetUrl,
                                           data=payload,
                                           headers=prodHeaders,
                                           verify=False)
        if callInternalUrl.text == 'ok':
            return 'ok'
        else:
            return callInternalUrl.text, 500
    except Exception as e:
        print(e)
        return f'[{issueKey}][Reopen] - Get issue when change the jsm status', 500

# https://okta.opsware.xyz:9486/bpRoutine/prod/create/field/all
# KEVEN
# fixed field by manually, update the fixed field sets on db, if need to update, need to drop all, maybe use the filter
@app_mainRoutine.route('/prod/create/field/<whichTeam>')
def prod_create_field_net(whichTeam=False):
    url = 'ict888.atlassian.net'
    customFieldslist = []

    if whichTeam == 'all':
        prod_create_field_net('net')
        prod_create_field_net('sys')
        prod_create_field_net('dba')
        prod_create_field_net('ops')
        # requests.get("https://okta.opsware.xyz:9486/bpRoutine/prod/create/field/net")
        # requests.get("https://okta.opsware.xyz:9486/bpRoutine/prod/create/field/sys")
        # requests.get("https://okta.opsware.xyz:9486/bpRoutine/prod/create/field/dba")
        # requests.get("https://okta.opsware.xyz:9486/bpRoutine/prod/create/field/ops")
        return 'all ok'

    defineDB = False  # if whichTeam user does not provide it, then backend should not udpate db
    if whichTeam == 'net':
        print('== update jsm NET prod field ==')
        defineDB = True
        curContextId = 1
        customFieldslist.append(
            dict(customFieldName='Infra',
                 customFieldId='customfield_10264',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Category NET',
                 customFieldId='customfield_10286',
                 optionType='single'))
        customFieldslist.append(
            dict(customFieldName='Facilities',
                 customFieldId='customfield_10287',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Vendor Support',
                 customFieldId='customfield_10288',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Request Handler',
                 customFieldId='customfield_10274',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Participants',
                 customFieldId='customfield_10206',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Start Date Time',
                 customFieldId='customfield_10282',
                 optionType='timeString'))
        customFieldslist.append(
            dict(customFieldName='End Date Time',
                 customFieldId='customfield_10283',
                 optionType='timeString'))

        tmp_list = []
        tmp_list.append(('10812', 'FRI'))
        tmp_list.append(('10951', 'SAT'))
        tmp_list.append(('10813', 'SUN'))
        tmp_list.append(('10814', 'Highway'))
        tmp_list.append(('10815', 'MPLS'))
        tmp_list.append(('10816', 'UAT'))
        tmp_list.append(('10817', 'LBT'))
        tmp_list.append(('10818', 'RTX'))
        tmp_list.append(('10819', 'SSS'))
        tmp_list.append(('10952', 'DEV/QAT'))
        tmp_list.append(('11014', 'Haven'))
        tmp_list.append(('10820', 'Others'))
        customFieldslist[0]['values'] = tmp_list

        tmp_list2 = []
        tmp_list2.append(('10953', 'Architecture'))
        tmp_list2.append(('10954', 'Replacement'))
        tmp_list2.append(('10955', 'Upgrade'))
        tmp_list2.append(('10956', 'Project'))
        tmp_list2.append(('10957', 'Migration'))
        tmp_list2.append(('10958', 'Routine'))
        tmp_list2.append(('10959', 'Decommission'))
        tmp_list2.append(('10960', 'Regular Procurement'))
        tmp_list2.append(('10961', 'Troubleshooting'))
        tmp_list2.append(('10962', 'Other'))
        customFieldslist[1]['values'] = tmp_list2

        tmp_list3 = []
        tmp_list3.append(('10963', 'BR'))
        tmp_list3.append(('10964', 'FW'))
        tmp_list3.append(('10965', 'Switch'))
        tmp_list3.append(('10966', 'LTM'))
        tmp_list3.append(('10967', 'APS'))
        tmp_list3.append(('10968', 'WAF'))
        tmp_list3.append(('10969', 'Domain'))
        tmp_list3.append(('10970', 'DNS'))
        tmp_list3.append(('11108', 'K8S'))
        tmp_list3.append(('10971', 'Certificate'))
        tmp_list3.append(('11428', 'Cloud'))
        tmp_list3.append(('11110', 'Other'))
        customFieldslist[2]['values'] = tmp_list3

        tmp_list4 = []
        tmp_list4.append(('10972', 'Sanfran'))
        tmp_list4.append(('10973', 'Lantro'))
        tmp_list4.append(('10974', 'eASPNet'))
        customFieldslist[3]['values'] = tmp_list4

        tmp_list5 = []
        tmp_list5.append(('61237809fc55090071e40617', 'Justin Yeh'))
        tmp_list5.append(('6123807fec0a83006a1e72ce', 'Josh Liu'))
        tmp_list5.append(('612380814f29230069223aae', 'Ryo Bing'))
        tmp_list5.append(('612380810511d6006a0e12eb', 'Ray Hong'))
        tmp_list5.append(('612389351827d100682d0079', 'Chris Yen'))
        tmp_list5.append(('612389380511d6006a0e7db7', 'Shane Tzou'))
        customFieldslist[4]['values'] = tmp_list5
        customFieldslist[5]['values'] = tmp_list5

    elif whichTeam == 'sys':
        print('== update jsm SYS prod field ==')
        defineDB = True
        curContextId = 2
        customFieldslist.append(
            dict(customFieldName='BUs/Dept',
                 customFieldId='customfield_10281',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Request Handler',
                 customFieldId='customfield_10274',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Participants',
                 customFieldId='customfield_10206',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Category SYS',
                 customFieldId='customfield_10285',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Start Date Time',
                 customFieldId='customfield_10282',
                 optionType='timeString'))
        customFieldslist.append(
            dict(customFieldName='End Date Time',
                 customFieldId='customfield_10283',
                 optionType='timeString'))
        customFieldslist.append(
            dict(customFieldName='priority',
                 customFieldId='priority',
                 optionType='default'))

        tmp_list = []
        tmp_list.append(('10886', 'XN-188Asia'))
        tmp_list.append(('10887', 'XN-SBK'))
        tmp_list.append(('10888', 'XN-NBG'))
        tmp_list.append(('10889', 'XN-LDR'))
        tmp_list.append(('10890', 'XN-CAS'))
        tmp_list.append(('10891', 'XN-BI'))
        tmp_list.append(('10892', 'XN-IL'))
        tmp_list.append(('10893', 'XN-RTX'))
        tmp_list.append(('10894', 'XN-EA'))
        tmp_list.append(('10895', 'XN-OFC'))
        tmp_list.append(('10896', 'XN-TRS'))
        tmp_list.append(('11109', 'XN-TRS_TW'))
        tmp_list.append(('11512', '188 App Support'))
        tmp_list.append(('11513', 'SBK App Support'))
        tmp_list.append(('11514', 'CSN App Support LDR'))
        tmp_list.append(('11515', 'CSN App Support NBG'))
        tmp_list.append(('11527', 'CSP-TA'))
        # tmp_list.append(('10897', 'Infra-APP'))
        tmp_list.append(('10898', 'Infra-CEM'))
        tmp_list.append(('10899', 'Infra-CWD'))
        tmp_list.append(('10900', 'Infra-DBA'))
        tmp_list.append(('10901', 'Infra-NET'))
        tmp_list.append(('10902', 'Infra-SYS'))
        tmp_list.append(('10903', 'Infra-OPS'))
        tmp_list.append(('10904', 'Infra-TS'))
        tmp_list.append(('11018', 'Office'))
        tmp_list.append(('11019', 'Others'))
        customFieldslist[0]['values'] = tmp_list

        tmp_list2 = []
        tmp_list2.append(('61236ff4db2b4e006afb50a2', 'Gary Tseng'))
        tmp_list2.append(('612373a11827d100682bfcdb', 'Paul Chen'))
        tmp_list2.append(('612373a21827d100682bfced', 'Sun Sun'))
        tmp_list2.append(('6123780a3fe26c00692fe2ed', 'Ran Shih'))
        tmp_list2.append(('61237dee0952180069c827bd', 'Ian Hsu'))
        tmp_list2.append(('612380801827d100682c9765', 'Noel Huang'))
        tmp_list2.append(('6123871945f753006910bf8f', 'Wesley Hung'))
        tmp_list2.append(('6123871724912a0069d2539e', 'Ralf Wu'))
        customFieldslist[1]['values'] = tmp_list2
        customFieldslist[2]['values'] = tmp_list2

        tmp_list3 = []
        tmp_list3.append(('10929', 'Server-Provision'))
        tmp_list3.append(('10930', 'Server-Decommission'))
        tmp_list3.append(('11015', 'Server-Specification Adjust'))
        tmp_list3.append(('11016', 'Server-Software Installation'))
        tmp_list3.append(('11020', 'Server-Setting Modification'))
        tmp_list3.append(('10931', 'Hardware-Installation'))
        tmp_list3.append(('10932', 'Hardware-Replacment'))
        tmp_list3.append(('10933', 'Hardware-Decommission'))
        tmp_list3.append(('10934', 'Account-Creation'))
        tmp_list3.append(('10935', 'Account-Disable'))
        tmp_list3.append(('10936', 'Account-Privilege Modification'))
        tmp_list3.append(('10937', 'Platform-Anti-Virus Related'))
        tmp_list3.append(('10938', 'Platform-ELK Related'))
        tmp_list3.append(('10939', 'Platform-Kubernetes Related'))
        tmp_list3.append(('11017', 'Platform-Mail Related'))
        tmp_list3.append(('10940', 'Platform-RabbitMQ Related'))
        tmp_list3.append(('10941', 'Platform-NAS Related'))
        tmp_list3.append(('10942', 'Platform-Nutanix Related'))
        tmp_list3.append(('10943', 'Platform-Proxy Related'))
        tmp_list3.append(('10944', 'Platform-Redis Related'))
        tmp_list3.append(('10945', 'Monitor-HostMonitor Related'))
        tmp_list3.append(('10946', 'Monitor-Prometheus/Grafana Related'))
        tmp_list3.append(('10947', 'Security Related'))
        tmp_list3.append(('10948', 'Trouble Shooting'))
        tmp_list3.append(
            ('10949', 'Advanced Trouble Shooting (Generate SOP/KB)'))
        tmp_list3.append(('10950', 'Others'))
        customFieldslist[3]['values'] = tmp_list3

    elif whichTeam == 'dba':
        print('== update jsm DBA prod field ==')
        defineDB = True
        curContextId = 3
        customFieldslist = []
        customFieldslist.append(
            dict(customFieldName='BUs/Dept',
                 customFieldId='customfield_10281',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Request Handler',
                 customFieldId='customfield_10274',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Participants',
                 customFieldId='customfield_10206',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Category DB',
                 customFieldId='customfield_10289',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='User Impact',
                 customFieldId='customfield_10244',
                 optionType='single'))
        customFieldslist.append(
            dict(customFieldName='Start Date Time',
                 customFieldId='customfield_10282',
                 optionType='timeString'))
        customFieldslist.append(
            dict(customFieldName='End Date Time',
                 customFieldId='customfield_10283',
                 optionType='timeString'))
        customFieldslist.append(
            dict(customFieldName='priority',
                 customFieldId='priority',
                 optionType='default'))

        tmp_list = []
        tmp_list.append(('10886', 'XN-188Asia'))
        tmp_list.append(('10887', 'XN-SBK'))
        tmp_list.append(('10888', 'XN-NBG'))
        tmp_list.append(('10889', 'XN-LDR'))
        tmp_list.append(('10890', 'XN-CAS'))
        tmp_list.append(('10891', 'XN-BI'))
        tmp_list.append(('10892', 'XN-IL'))
        tmp_list.append(('10893', 'XN-RTX'))
        tmp_list.append(('10894', 'XN-EA'))
        tmp_list.append(('10895', 'XN-OFC'))
        tmp_list.append(('10896', 'XN-TRS'))
        tmp_list.append(('11109', 'XN-TRS_TW'))
        tmp_list.append(('11512', '188 App Support'))
        tmp_list.append(('11513', 'SBK App Support'))
        tmp_list.append(('11514', 'CSN App Support LDR'))
        tmp_list.append(('11515', 'CSN App Support NBG'))
        tmp_list.append(('11527', 'CSP-TA'))
        # tmp_list.append(('10897', 'Infra-APP'))
        tmp_list.append(('10898', 'Infra-CEM'))
        tmp_list.append(('10899', 'Infra-CWD'))
        tmp_list.append(('10900', 'Infra-DBA'))
        tmp_list.append(('10901', 'Infra-NET'))
        tmp_list.append(('10902', 'Infra-SYS'))
        tmp_list.append(('10903', 'Infra-OPS'))
        tmp_list.append(('10904', 'Infra-TS'))
        tmp_list.append(('11018', 'Office'))
        tmp_list.append(('11019', 'Others'))
        customFieldslist[0]['values'] = tmp_list

        tmp_list2 = []
        tmp_list2.append(('61236ff3db2b4e006afb5099', 'David Tung'))
        tmp_list2.append(('61236ff61827d100682bd084', 'Tony Wu'))
        tmp_list2.append(('61236ff3fc55090071e3a3cb', 'Albert Huang'))
        tmp_list2.append(('612373a2d7cac600694b28a9', 'Robert Lin'))
        tmp_list2.append(('6123780bd7cac600694b5cf6', 'Stanley Chen'))
        tmp_list2.append(('61238a643ef46a007049b7c6', 'Demon Wu'))
        tmp_list2.append(('612389350952180069c8b27f', 'Carny Chou'))
        tmp_list2.append(('61238a2c0bbbf90071d9c4fb', 'Austin Chang'))
        tmp_list2.append(('612389380952180069c8b2a3', 'William Liu'))
        customFieldslist[1]['values'] = tmp_list2
        customFieldslist[2]['values'] = tmp_list2

        tmp_list3 = []
        tmp_list3.append(('10975', 'Deployment'))
        tmp_list3.append(('10976', 'DB-Request(Instance/DB/Schema)'))
        tmp_list3.append(('10977', 'DB-Decom'))
        tmp_list3.append(('10978', 'DB-Security'))
        tmp_list3.append(('10979', 'DB-Config'))
        tmp_list3.append(('10980', 'DB-Add/Resize file'))
        tmp_list3.append(('10981', 'DB-Monitor System'))
        tmp_list3.append(('10982', 'DB-Others'))
        tmp_list3.append(('10983', 'Disk Extend'))
        tmp_list3.append(('10984', 'Storage-Upgrade'))
        tmp_list3.append(('10985', 'Storage-Volume move'))
        tmp_list3.append(('10986', 'Storage-Cabling'))
        tmp_list3.append(('10987', 'Storage-Hardware replacement'))
        tmp_list3.append(('10988', 'Storage-Others'))
        tmp_list3.append(('10989', 'On Call-Urgent/Deployment'))
        tmp_list3.append(('10990', 'Vault'))
        tmp_list3.append(('10991', 'DB Automation'))
        tmp_list3.append(('10992', 'SOP document'))
        tmp_list3.append(('10993', 'Troubleshooting/Performance Tunning'))
        tmp_list3.append(('10994', 'JIRA Related'))
        tmp_list3.append(('10995', 'Others-DB Relaetd'))
        tmp_list3.append(('10996', 'Others-No DB Related'))
        customFieldslist[3]['values'] = tmp_list3

        tmp_list4 = []
        tmp_list4.append(('10773', 'No'))
        tmp_list4.append(('10772', 'Yes'))
        customFieldslist[4]['values'] = tmp_list4

    elif whichTeam == 'ops':
        print('== update jsm OPS prod field ==')
        defineDB = True
        curContextId = 4
        customFieldslist = []
        customFieldslist.append(
            dict(customFieldName='BUs/Dept',
                 customFieldId='customfield_10281',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Request Handler',
                 customFieldId='customfield_10274',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Participants',
                 customFieldId='customfield_10206',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Infra',
                 customFieldId='customfield_10264',
                 optionType='multiple'))
        customFieldslist.append(
            dict(customFieldName='Category OPS',
                 customFieldId='customfield_10290',
                 optionType='single'))
        customFieldslist.append(
            dict(customFieldName='Start Date Time',
                 customFieldId='customfield_10282',
                 optionType='timeString'))
        customFieldslist.append(
            dict(customFieldName='End Date Time',
                 customFieldId='customfield_10283',
                 optionType='timeString'))

        tmp_list = []
        tmp_list.append(('10886', 'XN-188Asia'))
        tmp_list.append(('10887', 'XN-SBK'))
        tmp_list.append(('10888', 'XN-NBG'))
        tmp_list.append(('10889', 'XN-LDR'))
        tmp_list.append(('10890', 'XN-CAS'))
        tmp_list.append(('10891', 'XN-BI'))
        tmp_list.append(('10892', 'XN-IL'))
        tmp_list.append(('10893', 'XN-RTX'))
        tmp_list.append(('10894', 'XN-EA'))
        tmp_list.append(('10895', 'XN-OFC'))
        tmp_list.append(('10896', 'XN-TRS'))
        tmp_list.append(('11109', 'XN-TRS_TW'))
        tmp_list.append(('11512', '188 App Support'))
        tmp_list.append(('11513', 'SBK App Support'))
        tmp_list.append(('11514', 'CSN App Support LDR'))
        tmp_list.append(('11515', 'CSN App Support NBG'))
        tmp_list.append(('11527', 'CSP-TA'))
        # tmp_list.append(('10897', 'Infra-APP'))
        tmp_list.append(('10898', 'Infra-CEM'))
        tmp_list.append(('10899', 'Infra-CWD'))
        tmp_list.append(('10900', 'Infra-DBA'))
        tmp_list.append(('10901', 'Infra-NET'))
        tmp_list.append(('10902', 'Infra-SYS'))
        tmp_list.append(('10903', 'Infra-OPS'))
        tmp_list.append(('10904', 'Infra-TS'))
        tmp_list.append(('11018', 'Office'))
        tmp_list.append(('11019', 'Others'))
        customFieldslist[0]['values'] = tmp_list

        tmp_list1 = []
        tmp_list1.append(
            ('70121:a2077655-0362-4506-8963-79807a4468bf', 'Aiden Tan'))
        tmp_list1.append(('60080adec224770068948323', 'Albert Liu'))
        tmp_list1.append(('61238bd50952180069c8d381', 'Alex lin'))
        tmp_list1.append(('605b0e68572e59006966fb1b', 'Allen Yu'))
        tmp_list1.append(('60080b1674c3e2007163d85a', 'Asky Huang'))
        tmp_list1.append(('60067a9ecc7af1006f3c6306', 'Bayu Winursito'))
        tmp_list1.append(('6123807e45f7530069106eb8', 'Bob Lin'))
        tmp_list1.append(('5b99034ef58aee2b8d674693', 'Cadalora Lin'))
        tmp_list1.append(('60080adfbe0f980076d6dc78', 'Cyril Rejas'))
        tmp_list1.append(
            ('70121:08a34230-d1a5-4be7-ae28-2b22008e10f8', 'Daniel Liu'))
        tmp_list1.append(('5f8d494c40588b0077d97269', 'Danny Wu'))
        tmp_list1.append(('612389360bbbf90071d9ba2d', 'Eric Kao'))
        tmp_list1.append(('60080adfee80bd006f7a14ee', 'Gary Wu'))
        tmp_list1.append(('60080b16bb4eb50078940592', 'Huck Chen'))
        tmp_list1.append(
            ('70121:9113383e-ef02-4534-bce3-5fd070c95b26', 'Ivan Chu'))
        tmp_list1.append(('60042988dfb0c700690943f8', 'Keven Chang'))
        tmp_list1.append(
            ('70121:e315fa09-5350-4453-89aa-2ed2a6fb7a3f', 'Larry Tsou'))
        tmp_list1.append(('613eed22805a97006a90e2ce', 'Rorschach Ye'))
        tmp_list1.append(('60080b370d83ff007662e69d', 'Thurston Chao'))
        customFieldslist[1]['values'] = tmp_list1
        customFieldslist[2]['values'] = tmp_list1

        tmp_list2 = []
        tmp_list2.append(('10812', 'FRI'))
        tmp_list2.append(('10951', 'SAT'))
        tmp_list2.append(('10813', 'SUN'))
        tmp_list2.append(('10814', 'Highway'))
        tmp_list2.append(('10815', 'MPLS'))
        tmp_list2.append(('10816', 'UAT'))
        tmp_list2.append(('10817', 'LBT'))
        tmp_list2.append(('10818', 'RTX'))
        tmp_list2.append(('10819', 'SSS'))
        tmp_list2.append(('10952', 'DEV/QAT'))
        tmp_list2.append(('11014', 'Haven'))
        tmp_list2.append(('10820', 'Others'))
        customFieldslist[3]['values'] = tmp_list2

        tmp_list3 = []
        tmp_list3.append(('10997', 'Request-CDN'))
        tmp_list3.append(('10998', 'Request-Domain Redirection'))
        tmp_list3.append(('10999', 'Request-Firewall'))
        tmp_list3.append(('11000', 'Request-LTM'))
        tmp_list3.append(('11001', 'Request-Monitoring Related'))
        tmp_list3.append(('11002', 'Request-K8S Related'))
        tmp_list3.append(('11003', 'Incident-Application issue'))
        tmp_list3.append(('11004', 'Incident-CDN issue'))
        tmp_list3.append(('11005', 'Incident-Hardware DB'))
        tmp_list3.append(('11006', 'Incident-Hardware Network'))
        tmp_list3.append(('11007', 'Incident-Hardware Server'))
        tmp_list3.append(('11008', 'Incident-Hardware Power Outage'))
        tmp_list3.append(('11009', 'Incident-Network DDoS'))
        tmp_list3.append(('11010', 'Incident-Network DNS Poison/ Gov Block'))
        tmp_list3.append(
            ('11011', 'Incident-Network ISP / Service Provider Issue'))
        tmp_list3.append(
            ('11012', 'Incident-Service Providers / 3rd Party Issue'))
        tmp_list3.append(('11013', 'Incident-Undefined Issues'))
        tmp_list3.append(('11111', 'Request-Coding Related'))
        tmp_list3.append(('11504', 'OPS-KB'))
        tmp_list3.append(('11414', 'Others'))
        tmp_list3.append(
            ('11413', 'Request-Network ISP / Service Provider Maintenance'))
        customFieldslist[4]['values'] = tmp_list3

    if defineDB:
        # drop
        print('start to delete old data per env and current team')
        db.session.query(get_jsm_field_sets).filter(
            get_jsm_field_sets.env == "ict888.atlassian.net",
            get_jsm_field_sets.contextId == curContextId).delete()
        db.session.commit()
        print('end to delete old data per env and current team')

        # insert
        print('start update jsm_field_sets loop')
        for i in customFieldslist:
            print(i['customFieldName'], i['customFieldId'])
            tmp_values_list = []
            if 'values' in i.keys():
                for ii in i['values']:
                    tmp_values_list.append(
                        dict(id=ii[0], value=ii[1], disabled=False))
            insertDb = get_jsm_field_sets(env=url,
                                          optionName=i['customFieldName'],
                                          fieldId=i['customFieldId'],
                                          contextId=curContextId,
                                          value=json.dumps(tmp_values_list))
            db.session.add(insertDb)
        db.session.commit()
        db.session.close()
        db.session.remove()
        print('end update jsm_field_sets loop')
        return 'ok'
    else:
        return 'Wrong anwser!', 403


# https://okta.opsware.xyz:9486/bpRoutine/prod/sortout/field
@app_mainRoutine.route('/prod/sortout/field')
def prod_sort_out_field():
    resultList = get_jsm_field_sets.query.filter(
        get_jsm_field_sets.env == "ict888.atlassian.net").all()

    containerList = []

    for i in resultList:
        if len(json.loads(i.value)) != 0:
            for ii in json.loads(i.value):
                tmpDict = {}
                tmpDict.setdefault('env', i.env)
                tmpDict.setdefault('optionName', i.optionName)
                tmpDict.setdefault('fieldId', i.fieldId)
                tmpDict.setdefault('contextId', i.contextId)
                tmpDict.setdefault('_id', ii['id'])
                tmpDict.setdefault('_value', ii['value'])
                containerList.append(tmpDict)

    # drop all
    db.session.query(get_jsm_field_sets_sortOut).filter(
        get_jsm_field_sets_sortOut.env == "ict888.atlassian.net").delete()
    db.session.commit()

    for x in containerList:
        insertDb = get_jsm_field_sets_sortOut(**x)
        db.session.add(insertDb)
        db.session.commit()
    db.session.close()
    db.session.remove()

    return 'ok'


# for NET
# https://okta.opsware.xyz:9486/bpRoutine/tmp/update/qat/prod/net
@app_mainRoutine.route('/tmp/update/qat/prod/net')
def tmp_update_get_prod_net():
    def jsmCreateIssue(payload, url, targetTeam):
        defineDone = True
        reTryCreateJSMIssue = 1
        while defineDone:
            try:
                res = requests.request("POST",
                                       url,
                                       data=payload,
                                       headers=prodHeaders)
                if res.status_code == 201:
                    defineDone = False
                    print(
                        f'create {targetTeam} new ticket with title & description'
                    )
                else:
                    print(res.status_code)
                    reTryCreateJSMIssue += 1
                    if reTryCreateJSMIssue > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)

        if reTryCreateJSMIssue > 5:
            print(f'bad, get error when create new ticket for {targetTeam}')
            return False
        else:
            return res.json()['issueId']

    def jsmUpdateNetIssue(table_object):
        # get all fields about NET
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.contextId == 1).all()

        option_infra = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10264']
        option_infra_dict = {}
        for itemKey, itemValue in option_infra:
            option_infra_dict.setdefault(itemKey, itemValue)

        option_handler = [(x._value, {
            "accountId": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10274']
        option_handler_dict = {}
        for itemKey, itemValue in option_handler:
            option_handler_dict.setdefault(itemKey, itemValue)

        option_participant = [(x._value, {
            "accountId": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10206']
        option_participant_dict = {}
        for itemKey, itemValue in option_participant:
            option_participant_dict.setdefault(itemKey, itemValue)

        option_category = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10286']
        option_category_dict = {}
        for itemKey, itemValue in option_category:
            option_category_dict.setdefault(itemKey, itemValue)

        option_facilities = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10287']
        option_facilities_dict = {}
        for itemKey, itemValue in option_facilities:
            option_facilities_dict.setdefault(itemKey, itemValue)

        option_vendor = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10288']
        option_vendor_dict = {}
        for itemKey, itemValue in option_vendor:
            option_vendor_dict.setdefault(itemKey, itemValue)

        payloadDict = {'fields': {}}

        for k, v in table_object.serialize.items():
            if k == 'custom_infra':
                _valueList = []
                for item in v:
                    _valueList.append(option_infra_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10264',
                                                 _valueList)
            if k == 'custom_handler':
                _valueList = []
                for item in v:
                    _valueList.append(option_handler_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10274',
                                                 _valueList)
            if k == 'custom_participant':  # optional
                if v:
                    _valueList = []
                    for item in v:
                        _valueList.append(option_participant_dict[f'{item}'])
                    payloadDict['fields'].setdefault('customfield_10206',
                                                     _valueList)
            if k == 'custom_category':  # string
                print(v)
                payloadDict['fields'].setdefault('customfield_10286',
                                                 option_category_dict[f'{v}'])

            if k == 'custom_facilities':
                _valueList = []
                for item in v:
                    _valueList.append(option_facilities_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10287',
                                                 _valueList)

            if k == 'custom_vendor':  # optional
                if v:
                    _valueList = []
                    for item in v:
                        _valueList.append(option_vendor_dict[f'{item}'])
                    payloadDict['fields'].setdefault('customfield_10288',
                                                     _valueList)

            if k == 'startTime':
                # customfield_10067, 2022-03-29T03:30:00.000+0800
                payloadDict['fields'].setdefault(
                    'customfield_10282',
                    v.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            if k == 'endTime':
                if v:
                    payloadDict['fields'].setdefault(
                        'customfield_10283',
                        v.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))

        print(f'payloadDict = {payloadDict}')

        payload = json.dumps(payloadDict)
        url = f"https://ict888.atlassian.net/rest/api/3/issue/{table_object.mapping}"
        headers = {
            'Accept':
            'application/json',
            'Content-Type':
            'application/json',
            'Authorization':
            'Basic c3J2Lm9wc0B5aXRtaC5jb206MFdxeFRMeUZySFdzbXRmZE9QZmJGMkJB',
            'Cookie':
            'atlassian.xsrf.token=06ef7867-f85e-4f6f-9b1f-33a446f98474_724c56f3252bc2032cc55a889c5eee923d113ff6_lin'
        }

        defineDone = True
        counter = 1
        returnStatus = 'Success'

        while defineDone:
            try:
                response = requests.request("PUT",
                                            url,
                                            headers=prodHeaders,
                                            data=payload)
                if response.status_code == 204:
                    defineDone = False
                else:
                    print(response.status_code)
                    if counter > 5:
                        returnStatus = 'Fail'
                        defineDone = False
                    else:
                        counter += 1
                        time.sleep(2)
            except Exception as e:
                print(e)
        print(f'Update Ticket - {table_object.title}, status: {returnStatus}')
        return returnStatus

    def jsmUpdateComment(result):
        commentInjectList = []  # use this to update the Jira
        commentLists = json.loads(result.comments)
        for i in commentLists:
            tmpItem = get_jsm_net_comments.query.filter(
                get_jsm_net_comments.sn == i).first()
            newValue = markdownify.markdownify(tmpItem.content,
                                               heading_style="ATX")
            commentInjectList.append(
                f'(update by {tmpItem.handler} at {tmpItem.timestamp}), {newValue}'
            )

        url = f"https://ict888.atlassian.net/rest/api/2/issue/{result.mapping}/comment"

        for eachComment in commentInjectList:
            try:
                payload = json.dumps({
                    "visibility": {
                        "type": "role",
                        "value": "Service Desk Team"
                    },
                    "body": f'{eachComment}'
                })

                defineDone = True
                reTry = 0

                while defineDone:
                    response = requests.request("POST",
                                                url,
                                                headers=prodHeaders,
                                                data=payload)
                    if response.status_code == 201:
                        print(
                            f'[{result.mapping}] Done for update - {eachComment}'
                        )
                        defineDone = False
                    else:
                        print(response.status_code)
                        reTry += 1
                        if reTry > 5:
                            defineDone = False
                        else:
                            time.sleep(2)

                if reTry > 5:
                    print(
                        'failed during update the all comments to Jira, over 5 times'
                    )
            except Exception as e:
                print(
                    'failed during update the all comments to Jira, exception detail - '
                )
                print(e)

        if defineDone == True:
            return False
        else:
            return True

    udpateToJiraList = []

    # result = get_jsm_net_prod.query.all()
    # # result = get_jsm_net_prod.query.filter(
    # #     or_(get_jsm_net_prod.jiraStatus == 3,
    # #          get_jsm_net_prod.jiraStatus == 10011)).all()
    # print(len(result))

    for customSn in udpateToJiraList:
        # curtime = datetime.datetime.now()
        v = get_jsm_net_prod.query.filter(
            get_jsm_net_prod.sn == customSn).first()
        print(f'* sn: {v.sn}, mapping: {v.mapping}')
        # print(f'* start {k} - sn: {v.sn}, title: {v.title}, mapping: {v.mapping}')
        # # @@@1@@@
        print('create jira ticket - title and description')
        # tmp_playload
        payload_create_ticket = json.dumps({
            "serviceDeskId": "21",
            "requestTypeId": "492",
            "requestFieldValues": {
                "summary":
                v.title,
                "description":
                markdownify.markdownify(v.description, heading_style="ATX")
            }
        })
        url_create_ticket = "https://ict888.atlassian.net/rest/servicedeskapi/request"

        # 1. create jira ticket - only for title and descrption
        tmp_jsm_issue_id = jsmCreateIssue(payload_create_ticket,
                                          url_create_ticket, 'NET')
        v.mapping = tmp_jsm_issue_id
        db.session.commit()

        # 2. update db table detail to jira prod
        status_update_detail_to_jira = jsmUpdateNetIssue(v)
        if status_update_detail_to_jira == 'Fail':
            print(v.title, ' - get issue at part 2')
            continue
        # else:
        #     status_update_comments = jsmUpdateComment(v)
        #     if status_update_comments:
        #         print(f'* sn: {v.sn}, title: {v.title}')
        #     else:
        #         print(f'* sn: {v.sn}, title: {v.title}, fail!')
        #     lasttime = datetime.datetime.now()
        #     totalcost = lasttime - curtime
        #     print(f'* --end {k} - sn: {v.sn}, title: {v.title} -- cost: {totalcost}')

        # # @@@2@@@@  update status
        # flowList = [{
        #     "transition": {
        #         "id": "11"
        #     }
        # }, {
        #     "transition": {
        #         "id": "41"
        #     }
        # }, {
        #     "transition": {
        #         "id": "51"
        #     }
        # }]
        # url_change_status = f'https://ict888.atlassian.net/rest/api/3/issue/{v.mapping}/transitions'

        # for kk, ii in enumerate(flowList):
        #     payload = json.dumps(ii)
        #     defineDone = True
        #     counter = 1
        #     while defineDone:
        #         try:
        #             response = requests.request("POST",
        #                                         url_change_status,
        #                                         data=payload,
        #                                         headers=prodHeaders)
        #             if response.status_code == 204:
        #                 defineDone = False
        #             else:
        #                 print(response.status_code)
        #         except Exception as e:
        #             print(e)
        #             counter += 1
        #             if counter > 5:
        #                 defineDone = False
        #             else:
        #                 time.sleep(2)

        #     if counter > 5:
        #         print(f'updateNewIssueStatus-{kk}, get issue')
        #     else:
        #         print(f'updateNewIssueStatus-{kk}, ok')

        # lasttime = datetime.datetime.now()
        # totalcost = lasttime - curtime
        # print(f'* --end {k} - sn: {v.sn}, title: {v.title} -- cost: {totalcost}')

        # ## @@ query the jira prod api, and update the mapping table
        url_to_query_jira = f'https://ict888.atlassian.net/rest/api/2/issue/{v.mapping}'

        defineDone = True
        reTryCreateJSMIssue = 1

        while defineDone:
            try:
                res = requests.request("GET",
                                       url_to_query_jira,
                                       headers=prodHeaders)
                if res.status_code == 200:
                    defineDone = False
                    print('ok for query')
                else:
                    print(res.status_code)
                    reTryCreateJSMIssue += 1
                    if reTryCreateJSMIssue > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)

        insertDb = get_jsm_mapping_prod(
            issueId=res.json()['id'],
            issueKey=res.json()['key'],
            issueUrl=res.json()['fields']['customfield_10010']['_links']
            ['agent'],
            _group='NET')
        db.session.add(insertDb)
        db.session.commit()
        db.session.refresh(insertDb)
        returnSn = insertDb.sn
        v.mapping = returnSn
        db.session.commit()

    return 'ok'


# for SYS
# https://okta.opsware.xyz:9486/bpRoutine/tmp/update/qat/prod/sys
@app_mainRoutine.route('/tmp/update/qat/prod/sys')
def tmp_update_get_prod_sys():
    def jsmCreateIssue(payload, url, targetTeam):
        defineDone = True
        reTryCreateJSMIssue = 1
        while defineDone:
            try:
                res = requests.request("POST",
                                       url,
                                       data=payload,
                                       headers=prodHeaders)
                if res.status_code == 201:
                    defineDone = False
                    print(
                        f'create {targetTeam} new ticket with title & description'
                    )
                else:
                    print(res.status_code)
                    reTryCreateJSMIssue += 1
                    if reTryCreateJSMIssue > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)

        if reTryCreateJSMIssue > 5:
            print(f'bad, get error when create new ticket for {targetTeam}')
            return False
        else:
            return res.json()['issueId']

    def jsmUpdateIssue(table_object):
        # get all fields about SYS
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.contextId == 2).all()

        option_bu = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10281']
        option_bu_dict = {}
        for itemKey, itemValue in option_bu:
            option_bu_dict.setdefault(itemKey, itemValue)

        option_handler = [(x._value, {
            "accountId": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10274']
        option_handler_dict = {}
        for itemKey, itemValue in option_handler:
            option_handler_dict.setdefault(itemKey, itemValue)

        option_participant = [(x._value, {
            "accountId": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10206']
        option_participant_dict = {}
        for itemKey, itemValue in option_participant:
            option_participant_dict.setdefault(itemKey, itemValue)

        option_category = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10285']
        option_category_dict = {}
        for itemKey, itemValue in option_category:
            option_category_dict.setdefault(itemKey, itemValue)

        payloadDict = {'fields': {}}

        for k, v in table_object.serialize.items():
            if k == 'custom_bizUnit':
                _valueList = []
                for item in v:
                    if item == 'TRS':
                        _valueList.append(dict(id='10896'))
                    else:
                        _valueList.append(option_bu_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10281',
                                                 _valueList)
            if k == 'custom_handler':
                _valueList = []
                for item in v:
                    _valueList.append(option_handler_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10274',
                                                 _valueList)
            if k == 'custom_participant':  # optional
                if v:
                    _valueList = []
                    for item in v:
                        _valueList.append(option_participant_dict[f'{item}'])
                    payloadDict['fields'].setdefault('customfield_10206',
                                                     _valueList)

            if k == 'custom_category':
                _valueList = []
                for item in v:
                    _valueList.append(option_category_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10285',
                                                 _valueList)

            if k == 'startTime':
                payloadDict['fields'].setdefault(
                    'customfield_10282',
                    v.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            if k == 'endTime':
                if v:
                    payloadDict['fields'].setdefault(
                        'customfield_10283',
                        v.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))

            if k == 'custom_priority':
                priorityName = ['Highest', 'High', 'Medium', 'Low', 'Lowest']
                priorityId = [{
                    "id": '1'
                }, {
                    "id": '2'
                }, {
                    "id": '3'
                }, {
                    "id": '4'
                }, {
                    "id": '10000'
                }]
                priorityDict = {}
                for n, i in zip(priorityName, priorityId):
                    priorityDict.setdefault(n, i)
                payloadDict['fields'].setdefault('priority', priorityDict[v])

        print(f'payloadDict = {payloadDict}')

        payload = json.dumps(payloadDict)
        url = f"https://ict888.atlassian.net/rest/api/3/issue/{table_object.mapping}"

        defineDone = True
        counter = 1
        returnStatus = 'Success'

        while defineDone:
            try:
                response = requests.request("PUT",
                                            url,
                                            headers=prodHeaders,
                                            data=payload)
                if response.status_code == 204:
                    defineDone = False
                else:
                    print(response.status_code)
                    if counter > 5:
                        returnStatus = 'Fail'
                        defineDone = False
                    else:
                        counter += 1
                        time.sleep(2)
            except Exception as e:
                print(e)
        print(f'Update Ticket - {table_object.title}, status: {returnStatus}')
        return returnStatus

    def jsmUpdateComment(result):
        commentInjectList = []  # use this to update the Jira
        commentLists = json.loads(result.comments)
        for i in commentLists:
            tmpItem = get_jsm_sys_comments.query.filter(
                get_jsm_sys_comments.sn == i).first()
            newValue = markdownify.markdownify(tmpItem.content,
                                               heading_style="ATX")
            commentInjectList.append(
                f'(update by {tmpItem.handler} at {tmpItem.timestamp}), {newValue}'
            )

        url = f"https://ict888.atlassian.net/rest/api/2/issue/{result.mapping}/comment"

        for eachComment in commentInjectList:
            try:
                payload = json.dumps({
                    "visibility": {
                        "type": "role",
                        "value": "Service Desk Team"
                    },
                    "body": f'{eachComment}'
                })

                defineDone = True
                reTry = 0

                while defineDone:
                    response = requests.request("POST",
                                                url,
                                                headers=prodHeaders,
                                                data=payload)
                    if response.status_code == 201:
                        print(
                            f'[{result.mapping}] Done for update - {eachComment}'
                        )
                        defineDone = False
                    else:
                        print(response.status_code)
                        reTry += 1
                        if reTry > 5:
                            defineDone = False
                        else:
                            time.sleep(2)

                if reTry > 5:
                    print(
                        'failed during update the all comments to Jira, over 5 times'
                    )
            except Exception as e:
                print(
                    'failed during update the all comments to Jira, exception detail - '
                )
                print(e)

        if defineDone == True:
            return False
        else:
            return True

    # result = get_jsm_sys_prod.query.filter(get_jsm_sys_prod.ticketStatus != 99).all()
    # print(len(result))

    sys_close_ticket_sn = [
        780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 777, 778, 779, 769,
        770, 771, 772, 773, 774, 775, 776, 768, 767
    ]

    for targetSn in sys_close_ticket_sn:
        v = get_jsm_sys_prod.query.filter(
            get_jsm_sys_prod.sn == targetSn).first()
        # curtime = datetime.datetime.now()
        print(f'* sn: {v.sn}, title: {v.title}')

        # @@@1@@@
        print('create jira ticket - title and description')
        # # tmp_playload
        payload_create_ticket = json.dumps({
            "serviceDeskId": "21",
            "requestTypeId": "491",
            "requestFieldValues": {
                "summary":
                v.title,
                "description":
                markdownify.markdownify(v.description, heading_style="ATX")
            }
        })
        url_create_ticket = "https://ict888.atlassian.net/rest/servicedeskapi/request"

        # 1. create jira ticket - only for title and descrption
        tmp_jsm_issue_id = jsmCreateIssue(payload_create_ticket,
                                          url_create_ticket, 'SYS')
        v.mapping = tmp_jsm_issue_id
        db.session.commit()

        # 2. update db table detail to jira prod
        status_update_detail_to_jira = jsmUpdateIssue(v)
        if status_update_detail_to_jira == 'Fail':
            print(v.title, ' - get issue at part 2 - update detail')
            continue
        # else:
        #     status_update_comments = jsmUpdateComment(v)
        #     if status_update_comments:
        #         print('update comment success')
        #     else:
        #         print(v.title,
        #               ' - get issue at part 3 - update comment failed')

        # # @@@2@@@@  update status
        flowList = [{"transition": {"id": "11"}}]
        # flowList = [{
        #     "transition": {
        #         "id": "11"
        #     }
        # }, {
        #     "transition": {
        #         "id": "41"
        #     }
        # }, {
        #     "transition": {
        #         "id": "51"
        #     }
        # }]
        url_for_change_status = f'https://ict888.atlassian.net/rest/api/3/issue/{v.mapping}/transitions'

        for kk, ii in enumerate(flowList):
            payload = json.dumps(ii)
            defineDone = True
            counter = 1
            while defineDone:
                try:
                    response = requests.request("POST",
                                                url_for_change_status,
                                                data=payload,
                                                headers=prodHeaders)
                    if response.status_code == 204:
                        defineDone = False
                    else:
                        print(response.status_code)
                except Exception as e:
                    print(e)
                    counter += 1
                    if counter > 5:
                        defineDone = False
                    else:
                        time.sleep(2)

            if counter > 5:
                print(f'updateNewIssueStatus-{kk}, get issue')
            else:
                print(f'updateNewIssueStatus-{kk}, ok')

        db.session.commit()

        # # ## @@ query the jira prod api, and update the mapping table
        url_to_query_jira = f'https://ict888.atlassian.net/rest/api/2/issue/{v.mapping}'

        defineDone = True
        reTryCreateJSMIssue = 1

        while defineDone:
            try:
                res = requests.request("GET",
                                       url_to_query_jira,
                                       headers=prodHeaders)
                if res.status_code == 200:
                    defineDone = False
                    print('ok for query')
                else:
                    print(res.status_code)
                    reTryCreateJSMIssue += 1
                    if reTryCreateJSMIssue > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)

        insertDb = get_jsm_mapping_prod(
            issueId=res.json()['id'],
            issueKey=res.json()['key'],
            issueUrl=res.json()['fields']['customfield_10010']['_links']
            ['agent'],
            _group='SYS')
        db.session.add(insertDb)
        db.session.commit()
        db.session.refresh(insertDb)
        returnSn = insertDb.sn
        v.mapping = returnSn
        db.session.commit()

    return 'ok'


# for DBA
# https://okta.opsware.xyz:9486/bpRoutine/tmp/update/qat/prod/dba
@app_mainRoutine.route('/tmp/update/qat/prod/dba')
def tmp_update_get_prod_dba():
    def jsmCreateIssue(payload, url, targetTeam):
        defineDone = True
        reTryCreateJSMIssue = 1
        while defineDone:
            try:
                res = requests.request("POST",
                                       url,
                                       data=payload,
                                       headers=prodHeaders)
                if res.status_code == 201:
                    defineDone = False
                    print(
                        f'create {targetTeam} new ticket with title & description'
                    )
                else:
                    print(res.status_code)
                    reTryCreateJSMIssue += 1
                    if reTryCreateJSMIssue > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)

        if reTryCreateJSMIssue > 5:
            print(f'bad, get error when create new ticket for {targetTeam}')
            return False
        else:
            return res.json()['issueId']

    def jsmUpdateIssue(table_object):
        # get all fields about SYS
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.contextId == 3).all()

        # Biz Unit
        option_bu = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10281']
        option_bu_dict = {}
        for itemKey, itemValue in option_bu:
            option_bu_dict.setdefault(itemKey, itemValue)

        option_handler = [(x._value, {
            "accountId": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10274']
        option_handler_dict = {}
        for itemKey, itemValue in option_handler:
            option_handler_dict.setdefault(itemKey, itemValue)

        option_participant = [(x._value, {
            "accountId": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10206']
        option_participant_dict = {}
        for itemKey, itemValue in option_participant:
            option_participant_dict.setdefault(itemKey, itemValue)

        # custom_category DBA
        option_category = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10289']

        option_category_dict = {}
        for itemKey, itemValue in option_category:
            option_category_dict.setdefault(itemKey, itemValue)

        # custom_isImpact
        option_isImpact = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10244']

        option_isImpact_dict = {}
        for itemKey, itemValue in option_isImpact:
            option_isImpact_dict.setdefault(itemKey, itemValue)

        payloadDict = {'fields': {}}

        for k, v in table_object.serialize.items():
            if k == 'custom_bizUnit':
                _valueList = []
                for item in v:
                    _valueList.append(option_bu_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10281',
                                                 _valueList)

            if k == 'custom_handler':
                _valueList = []
                for item in v:
                    _valueList.append(option_handler_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10274',
                                                 _valueList)

            if k == 'custom_participant':  # optional
                if v:
                    _valueList = []
                    for item in v:
                        _valueList.append(option_participant_dict[f'{item}'])
                    payloadDict['fields'].setdefault('customfield_10206',
                                                     _valueList)

            if k == 'custom_category':
                _valueList = []
                for item in v:
                    _valueList.append(option_category_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10289',
                                                 _valueList)

            if k == 'startTime':
                # customfield_10067, 2022-03-29T03:30:00.000+0800
                tmpTimeObject = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M")
                payloadDict['fields'].setdefault(
                    'customfield_10282',
                    tmpTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            if k == 'endTime':
                tmpTimeObject = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M")
                payloadDict['fields'].setdefault(
                    'customfield_10283',
                    tmpTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            if k == 'custom_priority':
                priorityName = ['Highest', 'High', 'Medium', 'Low', 'Lowest']
                priorityId = [{
                    "id": '1'
                }, {
                    "id": '2'
                }, {
                    "id": '3'
                }, {
                    "id": '4'
                }, {
                    "id": '10000'
                }]
                priorityDict = {}
                for n, i in zip(priorityName, priorityId):
                    priorityDict.setdefault(n, i)
                payloadDict['fields'].setdefault('priority', priorityDict[v])
            if k == 'custom_isImpact':
                if v == 1:
                    payloadDict['fields'].setdefault(
                        'customfield_10244', option_isImpact_dict['Yes'])
                else:
                    payloadDict['fields'].setdefault(
                        'customfield_10244', option_isImpact_dict['No'])

        print(f'payloadDict = {payloadDict}')

        payload = json.dumps(payloadDict)
        url = f"https://ict888.atlassian.net/rest/api/3/issue/{table_object.mapping}"

        defineDone = True
        counter = 1
        returnStatus = 'Success'

        while defineDone:
            try:
                response = requests.request("PUT",
                                            url,
                                            headers=prodHeaders,
                                            data=payload)
                if response.status_code == 204:
                    defineDone = False
                else:
                    print(response.status_code)
                    if counter > 5:
                        returnStatus = 'Fail'
                        defineDone = False
                    else:
                        counter += 1
                        time.sleep(2)
            except Exception as e:
                print(e)
        print(f'Update Ticket - {table_object.title}, status: {returnStatus}')
        return returnStatus

    def jsmUpdateComment(result):
        commentInjectList = []  # use this to update the Jira
        commentLists = json.loads(result.comments)
        for i in commentLists:
            tmpItem = get_jsm_sys_comments.query.filter(
                get_jsm_sys_comments.sn == i).first()
            newValue = markdownify.markdownify(tmpItem.content,
                                               heading_style="ATX")
            commentInjectList.append(
                f'(update by {tmpItem.handler} at {tmpItem.timestamp}), {newValue}'
            )

        url = f"https://ict888.atlassian.net/rest/api/2/issue/{result.mapping}/comment"

        for eachComment in commentInjectList:
            try:
                payload = json.dumps({
                    "visibility": {
                        "type": "role",
                        "value": "Service Desk Team"
                    },
                    "body": f'{eachComment}'
                })

                defineDone = True
                reTry = 0

                while defineDone:
                    response = requests.request("POST",
                                                url,
                                                headers=prodHeaders,
                                                data=payload)
                    if response.status_code == 201:
                        print(
                            f'[{result.mapping}] Done for update - {eachComment}'
                        )
                        defineDone = False
                    else:
                        print(response.status_code)
                        reTry += 1
                        if reTry > 5:
                            defineDone = False
                        else:
                            time.sleep(2)

                if reTry > 5:
                    print(
                        'failed during update the all comments to Jira, over 5 times'
                    )
            except Exception as e:
                print(
                    'failed during update the all comments to Jira, exception detail - '
                )
                print(e)

        if defineDone == True:
            return False
        else:
            return True

    result = get_jsm_dba_prod.query.filter(
        get_jsm_dba_prod.ticketStatus != 99).all()
    print(len(result))

    for k, v in enumerate(result):
        # curtime = datetime.datetime.now()
        print(f'* start {k} - sn: {v.sn}, title: {v.title}')
        # # # ## @@ query the jira prod api, and update the mapping table ( mapping change to table )
        url_to_query_jira = f'https://ict888.atlassian.net/rest/api/2/issue/{v.mapping}'

        defineDone = True
        reTryCreateJSMIssue = 1

        while defineDone:
            try:
                res = requests.request("GET",
                                       url_to_query_jira,
                                       headers=prodHeaders)
                if res.status_code == 200:
                    defineDone = False
                    print('ok for query')
                else:
                    print(res.status_code)
                    reTryCreateJSMIssue += 1
                    if reTryCreateJSMIssue > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)

        insertDb = get_jsm_mapping_prod(
            issueId=res.json()['id'],
            issueKey=res.json()['key'],
            issueUrl=res.json()['fields']['customfield_10010']['_links']
            ['agent'],
            _group='DBA')
        db.session.add(insertDb)
        db.session.commit()
        db.session.refresh(insertDb)
        returnSn = insertDb.sn
        v.mapping = returnSn
        db.session.commit()

        # # @@@1@@@
        # print('create jira ticket - title and description')
        # # # tmp_playload
        # payload_create_ticket = json.dumps({
        #     "serviceDeskId": "21",
        #     "requestTypeId": "493",
        #     "requestFieldValues": {
        #         "summary":
        #         v.title,
        #         "description":
        #         markdownify.markdownify(v.description, heading_style="ATX")
        #     }
        # })
        # url_create_ticket = "https://ict888.atlassian.net/rest/servicedeskapi/request"

        # # 1. create jira ticket - only for title and descrption
        # tmp_jsm_issue_id = jsmCreateIssue(payload_create_ticket,
        #                                   url_create_ticket, 'DBA')
        # v.mapping = tmp_jsm_issue_id
        # db.session.commit()

        # # 2. update db table detail to jira prod
        # status_update_detail_to_jira = jsmUpdateIssue(v)
        # if status_update_detail_to_jira == 'Fail':
        #     print(k, ' - get issue at part 2 - update detail')
        #     continue
        # else:
        #     lasttime = datetime.datetime.now()
        #     totalcost = lasttime - curtime
        #     print(f'* --end {k} - sn: {v.sn}, title: {v.title} -- cost: {totalcost}')
        # status_update_comments = jsmUpdateComment(v)
        # if status_update_comments:
        #     print('update comment success')
        # else:
        #     print(k, ' - get issue at part 3 - update comment failed')
        #     continue

        # lasttime = datetime.datetime.now()
        # totalcost = lasttime - curtime
        # if status_update_comments:
        #     print(
        #         f'* --end {k} - sn: {v.sn}, title: {v.title} -- cost: {totalcost}'
        #     )
        # else:
        #     print(
        #         f'* --end {k} - sn: {v.sn}, title: {v.title} -- cost: {totalcost}, fail!'
        #     )

        # # # @@@2@@@@  update status
        # flowList = [{"transition": {"id": "11"}}, {"transition": {"id": "41"}}, {"transition": {"id": "51"}}]
        # url_for_change_status = f'https://ict888.atlassian.net/rest/api/3/issue/{v.mapping}/transitions'

        # for kk, ii in enumerate(flowList):
        #     payload = json.dumps(ii)
        #     defineDone = True
        #     counter = 1
        #     while defineDone:
        #         try:
        #             response = requests.request("POST",
        #                                         url_for_change_status,
        #                                         data=payload,
        #                                         headers=headers)
        #             if response.status_code == 204:
        #                 defineDone = False
        #             else:
        #                 print(response.status_code)
        #         except Exception as e:
        #             print(e)
        #             counter += 1
        #             if counter > 5:
        #                 defineDone = False
        #             else:
        #                 time.sleep(2)

        #     if counter > 5:
        #         print(f'updateNewIssueStatus-{kk}, get issue')
        #     else:
        #         print(f'updateNewIssueStatus-{kk}, ok')

        # v.ticketStatus = 99
        # db.session.commit()
        # lasttime = datetime.datetime.now()
        # totalcost = lasttime - curtime
        # print(f'* --end {k} - sn: {v.sn}, title: {v.title} -- cost: {totalcost}')

    return 'ok'


@app_mainRoutine.route('/jira/convert_markdown/<issueKey>')
def convert_markdown(issueKey):
    try:
        url = f"https://ict888.atlassian.net/rest/api/2/issue/{issueKey}"
        response = requests.request("GET", url, headers=prodHeaders)
        raw_content = response.json()['fields']['description']

        convert_url = "https://ict888.atlassian.net/rest/api/1.0/render"
        convert_payload = json.dumps({
            "rendererType": "atlassian-wiki-renderer",
            "unrenderedMarkup": raw_content
        })

        response = requests.request("POST",
                                    convert_url,
                                    data=convert_payload,
                                    headers=convertHeaders)
    except Exception as e:
        print(e)
        return (None, None)

    return (raw_content, response.text)
