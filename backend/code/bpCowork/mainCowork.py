from ast import Not
from cProfile import label
from dataclasses import field
from doctest import Example
from enum import Flag
from operator import contains
from re import template

from sqlalchemy import false, null, true, or_, and_, func
from models import db, get_jsm_dba_prod, get_jsm_mapping_prod, get_jsm_net, get_jsm_net_prod, get_jsm_field_sets, get_jsm_mapping, get_jsm_field_sets_sortOut, get_jsm_net_comments, get_jsm_sys, get_jsm_sys_comments, get_jsm_sys_prod, get_jsm_dba, get_jsm_dba_comments, get_jsm_ops, get_jsm_ops_comments, get_jsm_ops_prod, get_otrs_dba_ticket, get_otrs_dba_ticket_comments, get_handover_customer_status
from flask import Blueprint, jsonify, request
import json
import collections
import requests
import datetime
import asyncio
import markdownify
import time

# Skype
from skpy import Skype, SkypeChats

app_mainCowork = Blueprint('app_mainCowork', __name__)

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

# front end create ticket
@app_mainCowork.route('/update/db', methods=['GET', 'POST'])
def updateDb():
    front_data = request.get_json(silent=True)
    targetTeam = front_data['targetTeam']
    dictData = front_data['result']
    whoCreate = front_data['editor']
    containerList = []
    tmpDict = {}

    # create issue, and update jsm mapping, return jsm mapping sn
    def jsmCreateIssue(payload, targetTeam):
        url = "https://ict888.atlassian.net/rest/servicedeskapi/request"

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
            insertDb = get_jsm_mapping_prod(
                issueId=res.json()['issueId'],
                issueKey=res.json()['issueKey'],
                issueUrl=res.json()['_links']['agent'],
                _group=targetTeam)
            db.session.add(insertDb)
            db.session.commit()
            db.session.refresh(insertDb)
            returnSn = insertDb.sn
            db.session.close()
            db.session.remove()

            return returnSn

    # update SYS issue, and return status string
    def jsmUpdateSysIssue(sn):
        jsmInfo = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == sn).first()
        targetSys = get_jsm_sys_prod.query.filter(
            get_jsm_sys_prod.mapping == sn).first()
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

        for k, v in targetSys.serialize.items():
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
        url = f"https://ict888.atlassian.net/rest/api/3/issue/{jsmInfo.issueId}"

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
        print(f'Update Ticket - {targetSys.title}, status: {returnStatus}')
        return returnStatus

    # update OPS issue, and return status string
    def jsmUpdateOpsIssue(sn):
        jsmInfo = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == sn).first()
        targetOps = get_jsm_ops_prod.query.filter(
            get_jsm_ops_prod.mapping == sn).first()
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.contextId == 4).all()

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

        # custom_category OPS
        option_category = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10290']
        option_category_dict = {}
        for itemKey, itemValue in option_category:
            option_category_dict.setdefault(itemKey, itemValue)

        # Infra
        option_infra = [(x._value, {
            "id": x._id
        }) for x in optionsSet if x.fieldId == 'customfield_10264']
        option_infra_dict = {}
        for itemKey, itemValue in option_infra:
            option_infra_dict.setdefault(itemKey, itemValue)

        payloadDict = {'fields': {}}

        for k, v in targetOps.serialize.items():
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

            if k == 'custom_infra':
                _valueList = []
                for item in v:
                    _valueList.append(option_infra_dict[f'{item}'])
                payloadDict['fields'].setdefault('customfield_10264',
                                                 _valueList)

            if k == 'custom_category':
                payloadDict['fields'].setdefault('customfield_10290',
                                                 option_category_dict[v])

            if k == 'startTime':
                payloadDict['fields'].setdefault(
                    'customfield_10282',
                    v.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))

            if k == 'endTime':
                if v:
                    payloadDict['fields'].setdefault(
                        'customfield_10283',
                        v.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))

        payload = json.dumps(payloadDict)
        print(payloadDict)

        url = f"https://ict888.atlassian.net/rest/api/3/issue/{jsmInfo.issueId}"

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

        print(
            f'Update Ticket {jsmInfo.issueKey} - {targetOps.title}, status: {returnStatus}'
        )
        return returnStatus

    # update DBA issue, and return status string
    def jsmUpdateDbaIssue(sn):
        jsmInfo = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == sn).first()
        targetDba = get_jsm_dba_prod.query.filter(
            get_jsm_dba_prod.mapping == sn).first()

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

        for k, v in targetDba.serialize.items():
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

        payload = json.dumps(payloadDict)

        url = f"https://ict888.atlassian.net/rest/api/3/issue/{jsmInfo.issueId}"

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
                if counter > 5:
                    returnStatus = 'Fail'
                    defineDone = False
                else:
                    counter += 1
                    time.sleep(2)

        print(f'Update Ticket {jsmInfo.issueKey} - {targetDba.title}, status: {returnStatus}')

        return returnStatus

    # update NET issue, and return status string
    def jsmUpdateNetIssue(sn):
        jsmInfo = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == sn).first()
        targetNet = get_jsm_net_prod.query.filter(
            get_jsm_net_prod.mapping == sn).first()

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

        for k, v in targetNet.serialize.items():
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
        url = f"https://ict888.atlassian.net/rest/api/3/issue/{jsmInfo.issueId}"

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

        print(
            f'Update Ticket {jsmInfo.issueKey} - {targetNet.title}, status: {returnStatus}'
        )

        return returnStatus

    # update issue status
    def updateNewIssueStatusToOnProgess(mappingSn, _group):
        target = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == mappingSn).first()
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{target.issueKey}/transitions'

        payload = json.dumps({"transition": {"id": "11"}})

        defineDone = True
        counter = 1

        while defineDone:
            try:
                response = requests.request("POST",
                                            url,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    defineDone = False
                else:
                    counter += 1
                    print(response.status_code)
            except Exception as e:
                print(e)
                counter += 1
                if counter > 5:
                    defineDone = False
                else:
                    time.sleep(2)

        if counter > 5:
            print('updateNewIssueStatusToOnProgess, get issue')
            return False
        else:
            print('updateNewIssueStatusToOnProgess, ok')
            if _group == 'NET':
                adjustStatus = get_jsm_net_prod.query.filter(
                    get_jsm_net_prod.mapping == mappingSn).first()
            elif _group == 'SYS':
                adjustStatus = get_jsm_sys_prod.query.filter(
                    get_jsm_sys_prod.mapping == mappingSn).first()
            elif _group == 'DBA':
                adjustStatus = get_jsm_dba_prod.query.filter(
                    get_jsm_dba_prod.mapping == mappingSn).first()
            elif _group == 'OPS':
                adjustStatus = get_jsm_ops_prod.query.filter(
                    get_jsm_ops_prod.mapping == mappingSn).first()
            adjustStatus.jiraStatus = 3
            db.session.commit()
            db.session.close()
            db.session.remove()
            return True

    # only for DBA
    def jsmCreateWorkLog(mappingSn, cost):
        getIssueIdByMappingSn = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == mappingSn).first()
        createWorkLogUrl = f'https://ict888.atlassian.net/rest/api/2/issue/{getIssueIdByMappingSn.issueId}/worklog'
        payload = json.dumps({
            "timeSpentSeconds": cost * 60,
            "visibility": {
                "type": "role",
                "value": "Service Desk Team"
            },
            "comment": 'Auto generate by API'
        })

        defineStatus = True
        reTryAddWorkLog = 1
        newWorkLogid = False

        while defineStatus:
            try:
                response = requests.request("POST",
                                            createWorkLogUrl,
                                            headers=prodHeaders,
                                            data=payload)
                if response.status_code == 201:
                    newWorkLogid = response.json()['id']
                    defineStatus = False
                    print(
                        f'[{getIssueIdByMappingSn.issueKey}] - Create the Worklog record on JSM'
                    )
                else:
                    reTryAddWorkLog += 1
                    print(
                        f'[{getIssueIdByMappingSn.issueKey}] - Get unexcept http code {response.status_code}, retry - {reTryAddWorkLog}'
                    )
                    if reTryAddWorkLog > 5:
                        defineStatus = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)
                print(
                    f'[{getIssueIdByMappingSn.issueKey}] - Get Exception issue when create the Worklog record on JSM'
                )
                reTryAddWorkLog = 6
                defineStatus = False

        if newWorkLogid:
            # update the jsm dba local db
            searchByMappingSn = get_jsm_dba_prod.query.filter(
                get_jsm_dba_prod.mapping == mappingSn).first()
            searchByMappingSn.custom_workLogId = newWorkLogid
            searchByMappingSn.custom_workLogValue = cost * 60
            print(
                f'[{getIssueIdByMappingSn.issueKey}] - Done for update - Add the worklog id and value to local db'
            )
            db.session.commit()
            db.session.close()
            db.session.remove()
            return 'good'
        else:
            print(
                f'[{getIssueIdByMappingSn.issueKey}] - Get issue when getting worklog ID'
            )
            return 'bad'

    def addNewComment(editor, mappingSn, whichTeam):
        queryMappingDb = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == mappingSn).first()
        tmpTargetIssueKey = queryMappingDb.issueKey
        # 1 - add new comment on local comment db
        # 2 - adjust the comment list on local db
        try:
            if whichTeam == 'NET':
                # 1
                addOneRow = get_jsm_net_comments(issueKey=tmpTargetIssueKey,
                                                 handler=editor,
                                                 content='Create JSM Ticket')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(
                    f'[{tmpTargetIssueKey}] - Done for add create log the local comment db'
                )
                # 2
                queryLocalDb = get_jsm_net_prod.query.filter(
                    get_jsm_net_prod.mapping == mappingSn).first()
                queryLocalDb.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(
                    f'[{tmpTargetIssueKey}] - Done for adjust the comment list on local db'
                )
                return True
            elif whichTeam == 'SYS':
                # 1
                addOneRow = get_jsm_sys_comments(issueKey=tmpTargetIssueKey,
                                                 handler=editor,
                                                 content='Create JSM Ticket')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(
                    f'[{tmpTargetIssueKey}] - Done for add create log the local comment db'
                )
                # 2
                queryLocalDb = get_jsm_sys_prod.query.filter(
                    get_jsm_sys_prod.mapping == mappingSn).first()
                queryLocalDb.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(
                    f'[{tmpTargetIssueKey}] - Done for adjust the comment list on local db'
                )
                return True
            elif whichTeam == 'DBA':
                # 1
                addOneRow = get_jsm_dba_comments(issueKey=tmpTargetIssueKey,
                                                 handler=editor,
                                                 content='Create JSM Ticket')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(
                    f'[{tmpTargetIssueKey}] - Done for add create log the local comment db'
                )
                # 2
                queryLocalDb = get_jsm_dba_prod.query.filter(
                    get_jsm_dba_prod.mapping == mappingSn).first()
                queryLocalDb.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(
                    f'[{tmpTargetIssueKey}] - Done for adjust the comment list on local db'
                )
                return True
            elif whichTeam == 'OPS':
                # 1
                addOneRow = get_jsm_ops_comments(issueKey=tmpTargetIssueKey,
                                                 handler=editor,
                                                 commentType=2,
                                                 content='Create JSM Ticket')
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(
                    f'[{tmpTargetIssueKey}] - Done for add create log the local comment db'
                )
                # 2
                queryLocalDb = get_jsm_ops_prod.query.filter(
                    get_jsm_ops_prod.mapping == mappingSn).first()
                queryLocalDb.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(
                    f'[{tmpTargetIssueKey}] - Done for adjust the comment list on local db'
                )
                return True
            else:
                return False
        except Exception as e:
            print(e)
            print(
                f'[{tmpTargetIssueKey}] - Get error when creating log the comment db'
            )
            return False

    # update to Local db
    if targetTeam == 'NET':
        # payload for create new JSM ticket with title and description
        payload_create_ticket = json.dumps({
            "serviceDeskId": "21",
            "requestTypeId": "492",
            "requestFieldValues": {
                "summary":
                dictData['title'],
                "description":
                markdownify.markdownify(dictData['description'],
                                        heading_style="ATX")
            }
        })

        # 1 - create JSM ticket, return mapping sn ( int )
        mappingSn = jsmCreateIssue(payload_create_ticket, 'NET')

        # 2 - update custom info to local db
        tmpDict["startTime"] = datetime.datetime.strptime(
            dictData['startTime'], "%Y-%m-%d %H:%M")
        if dictData['endTime'] != '':
            try:
                tmpDict["endTime"] = datetime.datetime.strptime(
                    dictData['endTime'], "%Y-%m-%d %H:%M")
            except Exception as e:
                print(e)
                errorFormat = tmpDict["endTime"]
                print(
                    f'Net user {whoCreate} fill the uncorrect endTime - {errorFormat}'
                )
        tmpDict["ticketStatus"] = 1  # new ticket
        tmpDict["jiraStatus"] = 1  # fixed, Open = 1, In Progress = 3
        tmpDict["mapping"] = mappingSn
        tmpDict["custom_infra"] = json.dumps(dictData['infra'])
        tmpDict["custom_category"] = dictData['category']
        tmpDict["custom_facilities"] = json.dumps(dictData['facilities'])
        tmpDict["custom_vendor"] = json.dumps(dictData['vendorSupport'])
        tmpDict["custom_handler"] = json.dumps(dictData['handler'])
        if dictData['participant']:
            tmpDict["custom_participant"] = json.dumps(dictData['participant'])
        tmpDict["title"] = dictData['title']
        tmpDict["description"] = dictData['description']

        containerList.append(tmpDict)

        for x in containerList:
            insertDb = get_jsm_net_prod(**x)
            db.session.add(insertDb)
            db.session.commit()
        db.session.close()
        db.session.remove()

        # 3 - add one comment to record who create this ticket
        addNewCommentResult = addNewComment(whoCreate, mappingSn, targetTeam)
        if addNewCommentResult != True:
            return 'failed due to addNewCommentResult', 500

        # 4 - update option to Jira ticket
        status = jsmUpdateNetIssue(mappingSn)

        # 5 - update ticket status
        updateNewIssueStatusToOnProgess(mappingSn, targetTeam)

        if status == 'Success':
            return 'ok', 200
        else:
            return 'failed', 500
    elif targetTeam == 'SYS':
        f = open('spider_sys.txt', 'a')
        f.write(f'[Start] - {dictData} \n')
        # 1 - Prepare the payload to create the JSM SYS ticket
        payload = json.dumps({
            "serviceDeskId": "21",
            "requestTypeId": "491",
            "requestFieldValues": {
                "summary":
                dictData['title'],
                "description":
                markdownify.markdownify(dictData['description'],
                                        heading_style="ATX")
            }
        })

        # 2 - create JSM ticket and add record on mapping db, and return mapping db SN
        mappingSn = jsmCreateIssue(payload, 'SYS')

        print(f'create the new SYS JSM ticket, and the mapping db has beeen insert new row, SN is {mappingSn}')
        f.write(f'#2 - create the new SYS JSM ticket, and the mapping db has beeen insert new row, SN is {mappingSn} \n')

        # 3 - add record on local db (jsm_sys)
        f.write('#3 - start add record on local db \n')
        if mappingSn:
            try:
                tmpDict["startTime"] = datetime.datetime.strptime(
                    dictData['startTime'], "%Y-%m-%d %H:%M")
                if dictData['endTime'] != '':
                    try:
                        tmpDict["endTime"] = datetime.datetime.strptime(
                            dictData['endTime'], "%Y-%m-%d %H:%M")
                    except Exception as e:
                        print(e)
                        f.write(f'#3 - {e} \n')
                        errorFormat = tmpDict["endTime"]
                        print(f'Sys user {whoCreate} fill the uncorrect endTime - {errorFormat}')
                        f.write(f'#3 - SYS user {whoCreate} fill the uncorrect endTime - {errorFormat} \n')
                        f.close()
                        return 'bad, get issue during add new row on jsm_sys_prod local db', 500 
                tmpDict["ticketStatus"] = 1  # new ticket
                tmpDict["jiraStatus"] = 1  # fixed, Open = 1, In Progress = 3
                tmpDict["custom_bizUnit"] = json.dumps(dictData['bizUnit'])
                tmpDict["custom_category"] = json.dumps(dictData['category'])
                tmpDict["custom_handler"] = json.dumps(dictData['handler'])
                if dictData['participant']:
                    tmpDict["custom_participant"] = json.dumps(
                        dictData['participant'])
                tmpDict["custom_priority"] = dictData['priority']
                tmpDict["title"] = dictData['title']
                tmpDict["description"] = dictData['description']
                tmpDict["mapping"] = mappingSn

                containerList.append(tmpDict)

                for x in containerList:
                    insertDb = get_jsm_sys_prod(**x)
                    db.session.add(insertDb)
                    db.session.commit()
                db.session.close()
                db.session.remove()
                print(f'add new row on jsm_sys local db')
                f.write('#3 - add new row on jsm_sys local db \n')
            except Exception as e:
                print(e)
                f.write(f'#3 - {e} \n')
                f.write('#3 - bad, get issue during add new row on jsm_sys local db \n')
                f.close()
                return 'bad, get issue during add new row on jsm_sys local db', 500
        else:
            f.write('#2 - bad, get issue during create the JSM ticket \n')
            f.close()
            return 'bad, get issue during create the JSM ticket', 500

        # 4 - add one comment to record who create this ticket
        addNewCommentResult = addNewComment(whoCreate, mappingSn, targetTeam)
        if addNewCommentResult != True:
            f.write('#4 - failed, add one comment to record who create this ticket \n')
            f.close()
            return 'failed due to addNewCommentResult', 500
        else:
            f.write('#4 - success, add one comment to record who create this ticket \n')

        # 5 - update option to Jira ticket
        status = jsmUpdateSysIssue(mappingSn)
        if status == 'Success':
            f.write(f'#5 - {status} - update option to Jira ticket \n')
        else:
            f.write(f'#5 - {status} - update option to Jira ticket \n')
            f.close()
            return 'failed due to update option to Jira ticket', 500

        # 6 - update ticket status
        updateNewIssueStatusToOnProgess(mappingSn, targetTeam)
        if updateNewIssueStatusToOnProgess:
            f.write('#6 - success for updateNewIssueStatusToOnProgess \n')
        else:
            f.write('#6 - failed for updateNewIssueStatusToOnProgess \n')
            f.close()
            return 'failed due to updateNewIssueStatusToOnProgess', 500

        if status == 'Success':
            f.write('[Stop] - return 200 \n')
            f.close()
            return 'ok', 200
        else:
            f.write('[Stop] - return 500 \n')
            f.close()
            return 'failed', 500
    elif targetTeam == 'DBA':
        f = open('spider_dba.txt', 'a')
        f.write(f'[Start] - {dictData} \n')
        # 1 - Prepare the payload to create the JSM SYS ticket
        payload = json.dumps({
            "serviceDeskId": "21",
            "requestTypeId": "493",
            "requestFieldValues": {
                "summary":
                dictData['title'],
                "description":
                markdownify.markdownify(dictData['description'],
                                        heading_style="ATX")
            }
        })

        # 2 - create JSM ticket and add record on mapping db, and return mapping db SN
        mappingSn = jsmCreateIssue(payload, 'DBA')

        print(f'create the new DBA JSM ticket, and the mapping db has beeen insert new row, SN is {mappingSn}')
        f.write(f'#2 - create the new DBA JSM ticket, and the mapping db has beeen insert new row, SN is {mappingSn} \n')

        # 3 - add record on local db (jsm_dba)
        f.write('#3 - start add record on local db \n')
        if mappingSn:
            try:
                tmpDict["startTime"] = datetime.datetime.strptime(
                    dictData['startTime'], "%Y-%m-%d %H:%M")
                if dictData['endTime']:
                    try:
                        tmpDict["endTime"] = datetime.datetime.strptime(
                            dictData['endTime'], "%Y-%m-%d %H:%M")
                    except Exception as e:
                        print(e)
                        f.write(f'#3 - {e} \n')
                        errorFormat = tmpDict["endTime"]
                        print(f'DBA user {whoCreate} fill the uncorrect endTime - {errorFormat}')
                        f.write(f'#3 - DBA user {whoCreate} fill the uncorrect endTime - {errorFormat} \n')
                        f.close()
                        return 'bad, get issue during add new row on jsm_dba_prod local db', 500 
                tmpDict["ticketStatus"] = 1  # new ticket
                tmpDict["jiraStatus"] = 1  # fixed, Open = 1, In Progress = 3
                tmpDict["custom_bizUnit"] = json.dumps(dictData['bizUnit'])
                tmpDict["custom_category"] = json.dumps(dictData['category'])
                tmpDict["custom_handler"] = json.dumps(dictData['handler'])
                if dictData['participant']:
                    tmpDict["custom_participant"] = json.dumps(
                        dictData['participant'])
                tmpDict["custom_priority"] = dictData['priority']
                tmpDict["custom_isImpact"] = dictData['isImpact']
                tmpDict["title"] = dictData['title']
                tmpDict["description"] = dictData['description']
                tmpDict["mapping"] = mappingSn

                containerList.append(tmpDict)

                for x in containerList:
                    insertDb = get_jsm_dba_prod(**x)
                    db.session.add(insertDb)
                    db.session.commit()
                db.session.close()
                db.session.remove()
                print('add new row on jsm_dba local db')
                f.write('#3 - add new row on jsm_dba local db \n')
            except Exception as e:
                print(e)
                f.write(f'#3 - {e} \n')
                f.write('#3 - bad, get issue during add new row on jsm_dba_prod local db \n')
                f.close()
                return 'bad, get issue during add new row on jsm_dba_prod local db', 500
        else:
            f.write('#2 - bad, get issue during create the JSM ticket \n')
            f.close()
            return 'bad, get issue during create the JSM ticket', 500

        # 4 - add one comment to record who create this ticket
        addNewCommentResult = addNewComment(whoCreate, mappingSn, targetTeam)
        if addNewCommentResult != True:
            f.write('#4 - failed, add one comment to record who create this ticket \n')
            f.close()
            return 'failed due to addNewCommentResult', 500
        else:
            f.write('#4 - success, add one comment to record who create this ticket \n')

        # 5 - update option to Jira ticket
        status = jsmUpdateDbaIssue(mappingSn)
        if status == 'Success':
            f.write(f'#5 - {status} - update option to Jira ticket \n')
        else:
            f.write(f'#5 - {status} - update option to Jira ticket \n')
            f.close()
            return 'failed due to update option to Jira ticket', 500

        # 6 - create new worklog to store the work hours and store to the local DB jsm_dba custom_workLogId and custom_workLogValue
        updateWorkLogStatus = jsmCreateWorkLog(mappingSn,
                                               dictData['duration'][1])
        if updateWorkLogStatus == 'bad':
            f.write('#6 - failed due to update the worklog part \n')
            f.close()
            return 'failed due to update the worklog part', 500
        else:
            f.write('#6 - success for update the worklog part \n')

        # 7 - update ticket status
        updateNewIssueStatusToOnProgess(mappingSn, targetTeam)
        if updateNewIssueStatusToOnProgess:
            f.write('#7 - success for updateNewIssueStatusToOnProgess \n')
        else:
            f.write('#7 - failed for updateNewIssueStatusToOnProgess \n')
            f.close()
            return 'failed due to updateNewIssueStatusToOnProgess', 500

        if status == 'Success':
            f.write('[Stop] - return 200 \n')
            f.close()
            return 'ok', 200
        else:
            f.write('[Stop] - return 500 \n')
            f.close()
            return 'failed', 500
    elif targetTeam == 'OPS':
        # 1 - Prepare the payload to create the JSM OPS ticket
        payload = json.dumps({
            "serviceDeskId": "21",
            "requestTypeId": "497",
            "requestFieldValues": {
                "summary":
                dictData['title'],
                "description":
                markdownify.markdownify(dictData['description'],
                                        heading_style="ATX")
            }
        })

        # 2 - create JSM ticket and add record on mapping db, and return mapping db SN
        mappingSn = jsmCreateIssue(payload, 'OPS')

        # 3 - add record on local db (jsm_ops)
        if mappingSn:
            try:
                tmpDict["startTime"] = datetime.datetime.strptime(
                    dictData['startTime'], "%Y-%m-%d %H:%M")
                if dictData['endTime'] != '':
                    try:
                        tmpDict["endTime"] = datetime.datetime.strptime(
                            dictData['endTime'], "%Y-%m-%d %H:%M")
                    except Exception as e:
                        print(e)
                        errorFormat = tmpDict["endTime"]
                        print(
                            f'OPS user {whoCreate} fill the uncorrect endTime - {errorFormat}'
                        )
                tmpDict["ticketStatus"] = 1  # new ticket
                tmpDict["jiraStatus"] = 1  # fixed, Open = 1, In Progress = 3
                tmpDict["custom_bizUnit"] = json.dumps(dictData['bizUnit'])
                tmpDict["custom_infra"] = json.dumps(dictData['infra'])
                tmpDict["custom_category"] = dictData['category']
                tmpDict["custom_handler"] = json.dumps(dictData['handler'])
                if dictData['participant']:
                    tmpDict["custom_participant"] = json.dumps(
                        dictData['participant'])
                tmpDict["title"] = dictData['title']
                tmpDict["description"] = dictData['description']
                tmpDict["mapping"] = mappingSn

                containerList.append(tmpDict)

                for x in containerList:
                    insertDb = get_jsm_ops_prod(**x)
                    db.session.add(insertDb)
                    db.session.commit()
                db.session.close()
                db.session.remove()
                print(f'add new row on jsm_ops local db')
            except Exception as e:
                print(e)
                return 'bad, get issue during add new row on jsm_ops local db', 500
        else:
            return 'bad, get issue during create the JSM ticket', 500

        # 4 - add one comment to record who create this ticket
        addNewCommentResult = addNewComment(whoCreate, mappingSn, targetTeam)
        if addNewCommentResult != True:
            return 'failed due to addNewCommentResult', 500

        # 5 - update option to Jira ticket
        status = jsmUpdateOpsIssue(mappingSn)

        # 6 - update ticket status
        updateNewIssueStatusToOnProgess(mappingSn, targetTeam)

        if status == 'Success':
            return 'ok', 200
        else:
            return 'failed', 500


@app_mainCowork.route('/jsm/query/field')
@app_mainCowork.route('/jsm/query/field/<fieldId>/<contextId>')
def jsmQueryField(fieldId=None, contextId=None):
    if fieldId:
        resultList = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == fieldId,
            get_jsm_field_sets_sortOut.contextId == contextId).order_by(
                get_jsm_field_sets_sortOut.sn).all()
        returnList = []
        for i in resultList:
            returnList.append(dict(label=i._value, value=i._value))
    else:
        resultList = get_jsm_field_sets.query.all()
        returnList = []
        for i in resultList:
            returnList.append(i.serialize)
    return jsonify(returnList)


# return the jira option by team
@app_mainCowork.route('/jsm/createTicket/field/<whichTeam>')
def jsmCreateTicketField(whichTeam):
    tmpDict = {}
    if whichTeam == 'SYS':
        categoryOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10285',
            get_jsm_field_sets_sortOut.contextId == 2).all()
        categoryList = [x._value for x in categoryOptions]
        bizUnitOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10281',
            get_jsm_field_sets_sortOut.contextId == 2).all()
        bizUnitList = [x._value for x in bizUnitOptions]
        tmpDict.setdefault('categoryOptions', categoryList)
        tmpDict.setdefault('bizUnitOptions', bizUnitList)
    elif whichTeam == 'NET':
        infraOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10264',
            get_jsm_field_sets_sortOut.contextId == 1).order_by(
                get_jsm_field_sets_sortOut.sn).all()
        infraList = [x._value for x in infraOptions]
        categoryOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10286',
            get_jsm_field_sets_sortOut.contextId == 1).order_by(
                get_jsm_field_sets_sortOut.sn).all()
        categoryList = [x._value for x in categoryOptions]
        facilitiesOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10287',
            get_jsm_field_sets_sortOut.contextId == 1).order_by(
                get_jsm_field_sets_sortOut.sn).all()
        facilitiesList = [x._value for x in facilitiesOptions]
        vendorOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10288',
            get_jsm_field_sets_sortOut.contextId == 1).order_by(
                get_jsm_field_sets_sortOut.sn).all()
        vendorList = [x._value for x in vendorOptions]
        tmpDict.setdefault('infraOptions', infraList)
        tmpDict.setdefault('categoryOptions', categoryList)
        tmpDict.setdefault('facilitiesOptions', facilitiesList)
        tmpDict.setdefault('vendorOptions', vendorList)
    elif whichTeam == 'DBA':
        bizUnitOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10281',
            get_jsm_field_sets_sortOut.contextId == 3).all()
        bizUnitList = [x._value for x in bizUnitOptions]
        categoryOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10289',
            get_jsm_field_sets_sortOut.contextId == 3).all()
        categoryList = [x._value for x in categoryOptions]
        tmpDict.setdefault('bizUnitOptions', bizUnitList)
        tmpDict.setdefault('categoryOptions', categoryList)
    elif whichTeam == 'OPS':
        infraOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10264',
            get_jsm_field_sets_sortOut.contextId == 4).all()
        infraList = [x._value for x in infraOptions]
        categoryOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10290',
            get_jsm_field_sets_sortOut.contextId == 4).all()
        categoryList = [x._value for x in categoryOptions]
        bizUnitOptions = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10281',
            get_jsm_field_sets_sortOut.contextId == 4).all()
        bizUnitList = [x._value for x in bizUnitOptions]
        tmpDict.setdefault('infraOptions', infraList)
        tmpDict.setdefault('categoryOptions', categoryList)
        tmpDict.setdefault('bizUnitOptions', bizUnitList)
    return jsonify(tmpDict)


@app_mainCowork.route('/query/netdb')
@app_mainCowork.route('/query/netdb/<jsmSn>')
def queryNetDB(jsmSn=None):
    if jsmSn == 'closedTicket':
        resultSet = get_jsm_net_prod.query.filter(
            or_(get_jsm_net_prod.jiraStatus == 121,
                get_jsm_net_prod.jiraStatus == 71,
                get_jsm_net_prod.jiraStatus == 6)).order_by(
                    get_jsm_net_prod.mapping.desc()).limit(100)
        returnList = []
        for i in resultSet:
            tmpDict = {}
            tmpDict.setdefault('sn', i.sn)
            tmpDict.setdefault('handler', json.loads(i.custom_handler))
            tmpDict.setdefault('category', [i.custom_category])
            if i.custom_participant:
                tmpDict.setdefault('participant',
                                   json.loads(i.custom_participant))
            else:
                tmpDict.setdefault('participant', '')
            mappingResult = get_jsm_mapping_prod.query.filter(
                get_jsm_mapping_prod.sn == i.mapping).first()
            print(i)
            try:
                tmpDict.setdefault('issueKey', mappingResult.issueKey)
                tmpDict.setdefault('issueId', mappingResult.issueId)
                tmpDict.setdefault('issueUrl', mappingResult.issueUrl)
                tmpDict.setdefault('jsm', f'{mappingResult.issueKey} - {i.title}')
            except Exception as e:
                print(i.serialize)
            # get last comment time and sort out the time list
            # check if start time and end time has data
            if i.endTime:
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                endTime = i.endTime.strftime('%Y-%m-%d %H:%M')
                tmpDict.setdefault(
                    'timestamp',
                    [startTime, endTime,
                     str(i.endTime - i.startTime)])
            else:
                lastCommentSn = json.loads(i.comments)[-1]
                lastCommentResult = get_jsm_net_comments.query.filter(
                    get_jsm_net_comments.sn == lastCommentSn).first()
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                closeTime = lastCommentResult.timestamp.strftime(
                    '%Y-%m-%d %H:%M')
                tmpDict.setdefault('timestamp', [
                    startTime, closeTime,
                    str(lastCommentResult.timestamp - i.createdTime)
                ])
            returnList.append(tmpDict)
        return jsonify(returnList)
    elif jsmSn:
        resultSet = get_jsm_net_prod.query.filter(
            get_jsm_net_prod.sn == jsmSn).first()
        tmpDict = resultSet.serialize
        mappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == resultSet.mapping).first()
        tmpDict.setdefault('issueId', mappingResult.issueId)
        tmpDict.setdefault('issueKey', mappingResult.issueKey)
        tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

        # change the time format
        tmpDict['startTime'] = tmpDict['startTime'].strftime(
            '%Y-%m-%d %H:%M:%S')
        if tmpDict['endTime']:
            tmpDict['endTime'] = tmpDict['endTime'].strftime(
                '%Y-%m-%d %H:%M:%S')

        if resultSet.comments:
            tmpCommentList = []
            for eachComment in reversed(json.loads(resultSet.comments)):
                queryByCommentsSn = get_jsm_net_comments.query.filter(
                    get_jsm_net_comments.sn == eachComment).first()
                tmpCommentList.append(queryByCommentsSn.serialize)
            tmpDict['comments'] = tmpCommentList
        else:
            tmpDict['comments'] = None
        return jsonify(tmpDict)
    else:
        resultSet = get_jsm_net_prod.query.filter(
            and_(get_jsm_net_prod.jiraStatus != 121,
                 get_jsm_net_prod.jiraStatus != 71,
                 get_jsm_net_prod.jiraStatus != 6)).all()
        returnList = []

        if resultSet:
            for i in resultSet:
                tmpDict = i.serialize
                mappingResult = get_jsm_mapping_prod.query.filter(
                    get_jsm_mapping_prod.sn == i.mapping).first()
                tmpDict.setdefault('issueId', mappingResult.issueId)
                tmpDict.setdefault('issueKey', mappingResult.issueKey)
                tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

                # change the time format
                if tmpDict['startTime']:
                    tmpDict['startTime'] = tmpDict['startTime'].strftime(
                        '%Y-%m-%d %H:%M:%S')
                if tmpDict['endTime']:
                    tmpDict['endTime'] = tmpDict['endTime'].strftime(
                        '%Y-%m-%d %H:%M:%S')

                # check the comments
                if i.comments:
                    tmpCommentList = []
                    # reversed
                    for eachComment in reversed(json.loads(i.comments)):
                        queryByCommentsSn = get_jsm_net_comments.query.filter(
                            get_jsm_net_comments.sn == eachComment).first()
                        tmpCommentList.append(queryByCommentsSn.serialize)
                    tmpDict['comments'] = tmpCommentList
                returnList.append(tmpDict)
            return jsonify(returnList)
        else:
            return jsonify({})


@app_mainCowork.route('/query/sysdb')
@app_mainCowork.route('/query/sysdb/<jsmSn>')
def querySysDB(jsmSn=None):
    if jsmSn == 'closedTicket':
        resultSet = get_jsm_sys_prod.query.filter(
            or_(get_jsm_sys_prod.jiraStatus == 121,
                get_jsm_sys_prod.jiraStatus == 71,
                get_jsm_sys_prod.jiraStatus == 6)).order_by(
                    get_jsm_sys_prod.mapping.desc()).limit(100)
        returnList = []
        for i in resultSet:
            tmpDict = {}
            tmpDict.setdefault('sn', i.sn)
            tmpDict.setdefault('handler', json.loads(i.custom_handler))
            tmpDict.setdefault('category', json.loads(i.custom_category))
            if i.custom_participant:
                tmpDict.setdefault('participant',
                                   json.loads(i.custom_participant))
            else:
                tmpDict.setdefault('participant', '')
            mappingResult = get_jsm_mapping_prod.query.filter(
                get_jsm_mapping_prod.sn == i.mapping).first()
            tmpDict.setdefault('issueKey', mappingResult.issueKey)
            tmpDict.setdefault('issueId', mappingResult.issueId)
            tmpDict.setdefault('issueUrl', mappingResult.issueUrl)
            tmpDict.setdefault('jsm', f'{mappingResult.issueKey} - {i.title}')
            # get last comment time and sort out the time list
            # check if start time and end time has data
            if i.endTime:
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                endTime = i.endTime.strftime('%Y-%m-%d %H:%M')
                tmpDict.setdefault(
                    'timestamp',
                    [startTime, endTime,
                     str(i.endTime - i.startTime)])
            else:
                lastCommentSn = json.loads(i.comments)[-1]
                lastCommentResult = get_jsm_sys_comments.query.filter(
                    get_jsm_sys_comments.sn == lastCommentSn).first()
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                closeTime = lastCommentResult.timestamp.strftime(
                    '%Y-%m-%d %H:%M')
                tmpDict.setdefault('timestamp', [
                    startTime, closeTime,
                    str(lastCommentResult.timestamp - i.createdTime)
                ])
            returnList.append(tmpDict)
        return jsonify(returnList)
    elif jsmSn:
        resultSet = get_jsm_sys_prod.query.filter(
            get_jsm_sys_prod.sn == jsmSn).first()
        tmpDict = resultSet.serialize
        mappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == resultSet.mapping).first()
        tmpDict.setdefault('issueId', mappingResult.issueId)
        tmpDict.setdefault('issueKey', mappingResult.issueKey)
        tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

        # change the time format
        tmpDict['startTime'] = tmpDict['startTime'].strftime('%Y-%m-%d %H:%M')
        if tmpDict['endTime']:
            tmpDict['endTime'] = tmpDict['endTime'].strftime('%Y-%m-%d %H:%M')

        if resultSet.comments:
            tmpCommentList = []
            for eachComment in reversed(json.loads(resultSet.comments)):
                queryByCommentsSn = get_jsm_sys_comments.query.filter(
                    get_jsm_sys_comments.sn == eachComment).first()
                tmpCommentList.append(queryByCommentsSn.serialize)
            tmpDict['comments'] = tmpCommentList
        else:
            tmpDict['comments'] = None
        return jsonify(tmpDict)
    else:
        resultSet = get_jsm_sys_prod.query.filter(
            and_(get_jsm_sys_prod.jiraStatus != 121,
                 get_jsm_sys_prod.jiraStatus != 71,
                 get_jsm_sys_prod.jiraStatus != 6)).all()
        returnList = []
        if resultSet:
            for i in resultSet:
                try:
                    tmpDict = i.serialize
                    mappingResult = get_jsm_mapping_prod.query.filter(
                        get_jsm_mapping_prod.sn == i.mapping).first()
                    tmpDict.setdefault('issueId', mappingResult.issueId)
                    tmpDict.setdefault('issueKey', mappingResult.issueKey)
                    tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

                    # change the time format
                    if tmpDict['startTime']:
                        tmpDict['startTime'] = tmpDict['startTime'].strftime(
                            '%Y-%m-%d %H:%M')
                    if tmpDict['endTime']:
                        tmpDict['endTime'] = tmpDict['endTime'].strftime(
                            '%Y-%m-%d %H:%M')

                    # check the comments
                    if i.comments:
                        tmpCommentList = []
                        # reversed
                        for eachComment in reversed(json.loads(i.comments)):
                            queryByCommentsSn = get_jsm_sys_comments.query.filter(
                                get_jsm_sys_comments.sn ==
                                eachComment).first()
                            tmpCommentList.append(queryByCommentsSn.serialize)
                        tmpDict['comments'] = tmpCommentList
                    returnList.append(tmpDict)
                except Exception as e:
                    print(e)
                    print(f'sys sn get issue - ${i.sn}')
            return jsonify(returnList)
        else:
            return jsonify([])


@app_mainCowork.route('/query/opsdb')
@app_mainCowork.route('/query/opsdb/<jsmSn>')
def queryOpsDB(jsmSn=None):
    if jsmSn == 'closedTicket':
        resultSet = get_jsm_ops_prod.query.filter(
            or_(get_jsm_ops_prod.jiraStatus == 121,
                get_jsm_ops_prod.jiraStatus == 71,
                get_jsm_ops_prod.jiraStatus == 6)).order_by(
                    get_jsm_ops_prod.mapping.desc()).limit(100)
        returnList = []
        for i in resultSet:
            tmpDict = {}
            tmpDict.setdefault('sn', i.sn)
            tmpDict.setdefault('handler', json.loads(i.custom_handler))
            tmpDict.setdefault('category', [i.custom_category])
            if i.custom_participant:
                tmpDict.setdefault('participant',
                                   json.loads(i.custom_participant))
            else:
                tmpDict.setdefault('participant', '')
            mappingResult = get_jsm_mapping_prod.query.filter(
                get_jsm_mapping_prod.sn == i.mapping).first()
            tmpDict.setdefault('issueKey', mappingResult.issueKey)
            tmpDict.setdefault('issueId', mappingResult.issueId)
            tmpDict.setdefault('issueUrl', mappingResult.issueUrl)
            tmpDict.setdefault('jsm', f'{mappingResult.issueKey} - {i.title}')
            # get last comment time and sort out the time list
            # check if start time and end time has data
            if i.endTime:
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                endTime = i.endTime.strftime('%Y-%m-%d %H:%M')
                tmpDict.setdefault(
                    'timestamp',
                    [startTime, endTime,
                     str(i.endTime - i.startTime)])
            else:
                lastCommentSn = json.loads(i.comments)[-1]
                lastCommentResult = get_jsm_ops_comments.query.filter(
                    get_jsm_ops_comments.sn == lastCommentSn).first()
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                closeTime = lastCommentResult.timestamp.strftime(
                    '%Y-%m-%d %H:%M')
                tmpDict.setdefault('timestamp', [
                    startTime, closeTime,
                    str(lastCommentResult.timestamp - i.createdTime)
                ])
            returnList.append(tmpDict)
        return jsonify(returnList)
    elif jsmSn:
        resultSet = get_jsm_ops_prod.query.filter(
            get_jsm_ops_prod.sn == jsmSn).first()
        tmpDict = resultSet.serialize
        mappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == resultSet.mapping).first()
        tmpDict.setdefault('issueId', mappingResult.issueId)
        tmpDict.setdefault('issueKey', mappingResult.issueKey)
        tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

        # default add the highlight to true
        tmpDict['highlight'] = True

        # change the time format
        tmpDict['startTime'] = tmpDict['startTime'].strftime('%Y-%m-%d %H:%M')
        if tmpDict['endTime']:
            tmpDict['endTime'] = tmpDict['endTime'].strftime('%Y-%m-%d %H:%M')

        if resultSet.comments:
            tmpCommentList = []
            updateonce = True # to resolve the comment will not high light when user update it
            for eachComment in reversed(json.loads(resultSet.comments)):
                queryByCommentsSn = get_jsm_ops_comments.query.filter(
                    get_jsm_ops_comments.sn == eachComment).first()
                tmpCommentList.append(queryByCommentsSn.serialize)
                if updateonce:
                    tmpCommentList[-1].setdefault('display', True)
                    updateonce = False
            tmpDict['comments'] = tmpCommentList
        else:
            tmpDict['comments'] = None
        return jsonify(tmpDict)
    else:
        lastRow = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        date = lastRow.date
        shift = lastRow.shift
        shiftTimeMapping = {'M': '07:00', 'A': '15:30', 'N': '22:30'}
        stime_time = shiftTimeMapping[shift]
        shift_stime = f'{date} {stime_time}'
        shift_stime_obj = datetime.datetime.strptime(shift_stime, "%Y-%m-%d %H:%M")
        checker_comment = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.timestamp > shift_stime_obj).first()

        if checker_comment:
            mark_comment_start_number = checker_comment.sn
        else:
            mark_comment_start_number = 999999

        resultSet = get_jsm_ops_prod.query.filter(
            and_(get_jsm_ops_prod.jiraStatus != 121,
                 get_jsm_ops_prod.jiraStatus != 71,
                 get_jsm_ops_prod.jiraStatus != 6,
                 get_jsm_ops_prod.ticketStatus != 99)).all()
        returnList = []
        for i in resultSet:
            tmpDict = i.serialize
            define_highlight = False
            tmpDict.setdefault('highlight', False)
            mappingResult = get_jsm_mapping_prod.query.filter(
                get_jsm_mapping_prod.sn == i.mapping).first()
            tmpDict.setdefault('issueId', mappingResult.issueId)
            tmpDict.setdefault('issueKey', mappingResult.issueKey)
            tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

            # change the time format
            tmpDict['startTime'] = tmpDict['startTime'].strftime(
                '%Y-%m-%d %H:%M')
            if tmpDict['endTime']:
                tmpDict['endTime'] = tmpDict['endTime'].strftime(
                    '%Y-%m-%d %H:%M')

            # check the comments
            if i.comments:
                tmpCommentList = []
                # reversed
                for eachComment in reversed(json.loads(i.comments)):
                    queryByCommentsSn = get_jsm_ops_comments.query.filter(
                        get_jsm_ops_comments.sn == eachComment).first()
                    tmpCommentList.append(queryByCommentsSn.serialize)
                    if queryByCommentsSn.sn >= mark_comment_start_number:
                        define_highlight = True
                        tmpCommentList[-1].setdefault('display', True)
                    else:
                        tmpCommentList[-1].setdefault('display', False)
                tmpDict['comments'] = tmpCommentList
            
            if define_highlight:
                tmpDict['highlight'] = True
            returnList.append(tmpDict)

        return jsonify(returnList)


@app_mainCowork.route('/query/dbadb')
@app_mainCowork.route('/query/dbadb/<jsmSn>')
def queryDbaDB(jsmSn=None):
    if jsmSn == 'closedTicket':
        resultSet = get_jsm_dba_prod.query.filter(
            or_(get_jsm_dba_prod.jiraStatus == 121,
                get_jsm_dba_prod.jiraStatus == 71,
                get_jsm_dba_prod.jiraStatus == 6)).order_by(
                    get_jsm_dba_prod.mapping.desc()).limit(100)
        returnList = []
        for i in resultSet:
            tmpDict = {}
            tmpDict.setdefault('sn', i.sn)
            tmpDict.setdefault('handler', json.loads(i.custom_handler))
            tmpDict.setdefault('category', json.loads(i.custom_category))
            if i.custom_participant:
                tmpDict.setdefault('participant',
                                   json.loads(i.custom_participant))
            else:
                tmpDict.setdefault('participant', '')
            mappingResult = get_jsm_mapping_prod.query.filter(
                get_jsm_mapping_prod.sn == i.mapping).first()
            tmpDict.setdefault('issueKey', mappingResult.issueKey)
            tmpDict.setdefault('issueId', mappingResult.issueId)
            tmpDict.setdefault('issueUrl', mappingResult.issueUrl)
            tmpDict.setdefault('jsm', f'{mappingResult.issueKey} - {i.title}')
            # get last comment time and sort out the time list
            # check if start time and end time has data
            if i.endTime:
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                endTime = i.endTime.strftime('%Y-%m-%d %H:%M')
                tmpDict.setdefault(
                    'timestamp',
                    [startTime, endTime,
                     str(i.endTime - i.startTime)])
            else:
                lastCommentSn = json.loads(i.comments)[-1]
                lastCommentResult = get_jsm_dba_comments.query.filter(
                    get_jsm_dba_comments.sn == lastCommentSn).first()
                startTime = i.startTime.strftime('%Y-%m-%d %H:%M')
                closeTime = lastCommentResult.timestamp.strftime(
                    '%Y-%m-%d %H:%M')
                tmpDict.setdefault('timestamp', [
                    startTime, closeTime,
                    str(lastCommentResult.timestamp - i.createdTime)
                ])
            returnList.append(tmpDict)
        return jsonify(returnList)
    elif jsmSn:
        resultSet = get_jsm_dba_prod.query.filter(
            get_jsm_dba_prod.sn == jsmSn).first()
        tmpDict = resultSet.serialize
        mappingResult = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == resultSet.mapping).first()
        tmpDict.setdefault('issueId', mappingResult.issueId)
        tmpDict.setdefault('issueKey', mappingResult.issueKey)
        tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

        # # change the time format
        # tmpDict['startTime'] = tmpDict['startTime'].strftime(
        #     '%Y-%m-%d %H:%M:%S')
        # if tmpDict['endTime'] != '':
        #     tmpDict['endTime'] = tmpDict['endTime'].strftime(
        #         '%Y-%m-%d %H:%M:%S')

        if resultSet.comments:
            tmpCommentList = []
            for eachComment in reversed(json.loads(resultSet.comments)):
                queryByCommentsSn = get_jsm_dba_comments.query.filter(
                    get_jsm_dba_comments.sn == eachComment).first()
                tmpCommentList.append(queryByCommentsSn.serialize)
            tmpDict['comments'] = tmpCommentList
        else:
            tmpDict['comments'] = None
        return jsonify(tmpDict)
    else:
        resultSet = get_jsm_dba_prod.query.filter(
            and_(get_jsm_dba_prod.jiraStatus != 121,
                 get_jsm_dba_prod.jiraStatus != 71,
                 get_jsm_dba_prod.jiraStatus != 6)).all()
        returnList = []
        for i in resultSet:
            tmpDict = i.serialize
            mappingResult = get_jsm_mapping_prod.query.filter(
                get_jsm_mapping_prod.sn == i.mapping).first()
            tmpDict.setdefault('issueId', mappingResult.issueId)
            tmpDict.setdefault('issueKey', mappingResult.issueKey)
            tmpDict.setdefault('issueUrl', mappingResult.issueUrl)

            # change the time format
            # tmpDict['startTime'] = datetime.datetime.strptime(tmpDict['startTime'], "%Y-%m-%d %H:%M")
            # if tmpDict['endTime'] != '':
            #     tmpDict['endTime'] = datetime.datetime.strptime(tmpDict['endTime'], "%Y-%m-%d %H:%M")

            # check the comments
            if i.comments:
                tmpCommentList = []
                # reversed
                for eachComment in reversed(json.loads(i.comments)):
                    queryByCommentsSn = get_jsm_dba_comments.query.filter(
                        get_jsm_dba_comments.sn == eachComment).first()
                    tmpCommentList.append(queryByCommentsSn.serialize)
                tmpDict['comments'] = tmpCommentList
            returnList.append(tmpDict)

        return jsonify(returnList)


@app_mainCowork.route('/update/comment', methods=['GET', 'POST'])
def updateComment():
    front_data = request.get_json(silent=True)
    newEditor = front_data['newEditor']
    targetJsmSn = front_data['targetJsmSn']
    targetJsmIssueKey = front_data['targetJsmIssueKey']
    comment = front_data['comment']
    group = front_data['group']

    if group == 'NET':
        try:
            # update comment
            addOneRow = get_jsm_net_comments(issueKey=targetJsmIssueKey,
                                             handler=newEditor,
                                             content=comment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{targetJsmIssueKey}] - Update the comment db ( success )')
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update the comment db'
            )
            return 'Bad, get issue when update the comment db', 500

        try:
            # update JSM local db comment list
            jsmResult = get_jsm_net_prod.query.filter(
                get_jsm_net_prod.sn == targetJsmSn).first()
            if jsmResult.comments:
                tmpList = json.loads(jsmResult.comments)
                tmpList.append(commentDbSn)
                jsmResult.comments = json.dumps(tmpList)
            else:
                jsmResult.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(
                f'[{targetJsmIssueKey}] - Update local db for comment column ( success )'
            )
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update local db for comment column'
            )
            return 'Bad, get issue when update local db for comment column', 500

    if group == 'SYS':
        try:
            # update comment
            addOneRow = get_jsm_sys_comments(issueKey=targetJsmIssueKey,
                                             handler=newEditor,
                                             content=comment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{targetJsmIssueKey}] - Update the comment db ( success )')
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update the comment db'
            )
            return 'BAD, get issue when update the comment db', 500

        try:
            # update JSM local db comment list
            jsmResult = get_jsm_sys_prod.query.filter(
                get_jsm_sys_prod.sn == targetJsmSn).first()
            if jsmResult.comments:
                tmpList = json.loads(jsmResult.comments)
                tmpList.append(commentDbSn)
                jsmResult.comments = json.dumps(tmpList)
            else:
                jsmResult.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(
                f'[{targetJsmIssueKey}] - Update local db for comment column ( success )'
            )
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update local db for comment column'
            )
            return 'Bad, get issue when update local db for comment column', 500

    if group == 'OPS':
        updateToDesc = front_data['updateToDesc']
        try:
            # update comment
            addOneRow = get_jsm_ops_comments(issueKey=targetJsmIssueKey,
                                             handler=newEditor,
                                             commentType=2,
                                             content=comment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{targetJsmIssueKey}] - Update the comment db ( success )')
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update the comment db'
            )
            return 'BAD, get issue when update the comment db', 500

        try:
            # update JSM local db comment list
            jsmResult = get_jsm_ops_prod.query.filter(
                get_jsm_ops_prod.sn == targetJsmSn).first()

            # Merge desc and comment if option is true
            if updateToDesc == True:
                jsmResult.description = jsmResult.description + '<br>' + comment

            if jsmResult.comments:
                tmpList = json.loads(jsmResult.comments)
                tmpList.append(commentDbSn)
                jsmResult.comments = json.dumps(tmpList)
            else:
                jsmResult.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(
                f'[{targetJsmIssueKey}] - Update local db for comment column ( success )'
            )
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update local db for comment column'
            )
            return 'Bad, get issue when update local db for comment column', 500

    if group == 'DBA':
        try:
            # update comment
            addOneRow = get_jsm_dba_comments(issueKey=targetJsmIssueKey,
                                             handler=newEditor,
                                             content=comment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{targetJsmIssueKey}] - Update the comment db ( success )')
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update the comment db'
            )
            return 'BAD, get issue when update the comment db', 500

        try:
            # update JSM local db comment list
            jsmResult = get_jsm_dba_prod.query.filter(
                get_jsm_dba_prod.sn == targetJsmSn).first()
            if jsmResult.comments:
                tmpList = json.loads(jsmResult.comments)
                tmpList.append(commentDbSn)
                jsmResult.comments = json.dumps(tmpList)
            else:
                jsmResult.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(
                f'[{targetJsmIssueKey}] - Update local db for comment column ( success )'
            )
        except Exception as e:
            print(e)
            print(
                f'[{targetJsmIssueKey}] - Get issue when update local db for comment column'
            )
            return 'Bad, get issue when update local db for comment column', 500

    return 'ok', 200


# to which status control by frontend postData
@app_mainCowork.route('/jsm/net/update/status', methods=['GET', 'POST'])
def jsmNetUpdateStatus():

    front_data = request.get_json(silent=True)
    targetJSMSn = front_data['targetJSMSn']
    jsmIssueId = front_data['jsmIssueId']
    jsmIssueKey = front_data['jsmIssueKey']
    toWhichStatus = front_data[
        'toWhichStatus']  # ['transitions id', 'next jsm status id', 'next jsm status name']
    curStatusNameurl = f'https://ict888.atlassian.net/rest/servicedeskapi/request/{jsmIssueId}'
    try:
        defineCurNameCatchDone = True
        reTryCurNameCatchTime = 1
        while defineCurNameCatchDone:
            curStatusNameRes = requests.request("GET",
                                                curStatusNameurl,
                                                headers=prodHeaders)
            if curStatusNameRes.status_code == 200:
                curStatusName = curStatusNameRes.json(
                )['currentStatus']['status']
                defineCurNameCatchDone = False
            else:
                print(curStatusNameRes.status_code)
                if reTryCurNameCatchTime > 5:
                    defineCurNameCatchDone = False
                else:
                    reTryCurNameCatchTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return f'[{jsmIssueKey}] - GET Exception ERROR DURING GET CURRENT STATUS NAME FROM JSM', 500

    if reTryCurNameCatchTime > 5:
        return f'[{jsmIssueKey}] - GET Unexpected HTTP Response Code from JSM DURING GET CURRENT STATUS NAME FROM JSM', 500

    editor = front_data['editor']
    oldStatus = curStatusName
    newStatus = toWhichStatus[2]
    transitionsId = toWhichStatus[0]
    newStatusId = toWhichStatus[1]
    newComment = f'Change ticket status from "{oldStatus}" to "{newStatus}"'

    if newStatus == 'Closed':
        #1 - sort out list for all comments
        queryCommentBySn = get_jsm_net_prod.query.filter(
            get_jsm_net_prod.sn == targetJSMSn).first()
        commentInjectList = []  # use this to update the Jira
        curTime = datetime.datetime.now()
        formatTime = curTime.strftime("%Y-%m-%d %H:%M:%S")
        if queryCommentBySn.comments:
            commentLists = json.loads(queryCommentBySn.comments)
            for i in commentLists:
                tmpItem = get_jsm_net_comments.query.filter(
                    get_jsm_net_comments.sn == i).first()
                newValue = markdownify.markdownify(tmpItem.content,
                                                   heading_style="ATX")
                commentInjectList.append(
                    f'(update by {tmpItem.handler} at {tmpItem.timestamp}), {newValue}'
                )

        # append final comment let jira know who close this ticket
        commentInjectList.append(
            f'(update by {editor} at {formatTime}), Change ticket status to "Closed"'
        )

        #2 - update to Jira comment for all commments
        url = f"https://ict888.atlassian.net/rest/api/2/issue/{jsmIssueId}/comment"

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
                            f'[{jsmIssueKey}] Done for update - {eachComment}')
                        defineDone = False
                    else:
                        print(response.status_code)
                        reTry += 1
                        if reTry > 5:
                            defineDone = False
                        else:
                            time.sleep(2)

                if reTry > 5:
                    return 'failed during update the all comments to Jira', 500
            except Exception as e:
                print(e)
                return 'failed during update the all comments to Jira', 500

        #3  adjust the Jira status
        urlUpdateStatus = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'
        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})
        defineUpdateStatus = True
        reTryUpdateStatus = 1
        try:
            while defineUpdateStatus:
                response = requests.request("POST",
                                            urlUpdateStatus,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                    defineUpdateStatus = False
                    break
                else:
                    print(response.status_code)
                    reTryUpdateStatus += 1
                    if reTryUpdateStatus > 5:
                        defineUpdateStatus = False
                    else:
                        time.sleep(2)

            if reTryUpdateStatus > 5:
                return 'failed when udpate the JSM status (try 5 times)', 500
        except Exception as e:
            print(e)
            return 'failed when udpate the JSM status, go to backend see the Exception', 500

        # 4 update comments db - jsm_net_comments, get comments db sn
        try:
            addOneRow = get_jsm_net_comments(issueKey=jsmIssueKey,
                                             handler=editor,
                                             content=newComment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{jsmIssueKey}] Done for udpate comments DB')
        except Exception as e:
            print(e)
            return 'bad - due to update jsm net comments db', 500

        # 5 update local db - jsm_net, update jirastatus and append comments
        try:
            adjustStatus = get_jsm_net_prod.query.filter(
                get_jsm_net_prod.sn == targetJSMSn).first()
            adjustStatus.jiraStatus = newStatusId
            if adjustStatus.comments:
                tmpList = json.loads(adjustStatus.comments)
                tmpList.append(commentDbSn)
                adjustStatus.comments = json.dumps(tmpList)
            else:
                adjustStatus.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(f'[{jsmIssueKey}] Done for udpate local DB')
            return 'ok'
        except Exception as e:
            print(e)
            return 'bad - due to update jsm net db', 500

    # 1. adjust jira ticket status
    def adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor, newComment,
                               targetJSMSn):
        transitionsId = toWhichStatus[0]
        newStatusId = toWhichStatus[1]
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'
        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})

        defineDone = True
        counter = 1

        while defineDone:
            try:
                response = requests.request("POST",
                                            url,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    defineDone = False
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                else:
                    print(response.status_code)
                    counter += 1
                    if counter > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)
                return 'bad - due to Jira update issue, detail please see the backend log'

        if counter > 5:
            print('updateNewIssueStatusToOnProgess, get issue')
            return 'bad - due to Jira update issue (try 5 times)'
        else:
            # 2. update comments db - jsm_net_comments, get comments db sn
            try:
                addOneRow = get_jsm_net_comments(issueKey=jsmIssueKey,
                                                 handler=editor,
                                                 content=newComment)
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(f'[{jsmIssueKey}] Done for udpate comments DB')
            except Exception as e:
                print(e)
                return 'bad - due to update jsm net comments db'
            # 3. update local db - jsm_net, update jirastatus and append comments
            try:
                adjustStatus = get_jsm_net_prod.query.filter(
                    get_jsm_net_prod.sn == targetJSMSn).first()
                adjustStatus.jiraStatus = newStatusId
                if adjustStatus.comments:
                    tmpList = json.loads(adjustStatus.comments)
                    tmpList.append(commentDbSn)
                    adjustStatus.comments = json.dumps(tmpList)
                else:
                    adjustStatus.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(f'[{jsmIssueKey}] Done for udpate local DB')
                return 'ok'
            except Exception as e:
                print(e)
                return 'bad - due to update jsm net db'

    updateResult = adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor,
                                          newComment, targetJSMSn)

    if updateResult != 'ok':
        return updateResult, 500
    else:
        return 'ok', 200


# to which status control by frontend postData
@app_mainCowork.route('/jsm/sys/update/status', methods=['GET', 'POST'])
def jsmSysUpdateStatus():
    front_data = request.get_json(silent=True)
    targetJSMSn = front_data['targetJSMSn']
    jsmIssueId = front_data['jsmIssueId']
    jsmIssueKey = front_data['jsmIssueKey']
    toWhichStatus = front_data[
        'toWhichStatus']  # ['transitions id', 'next jsm status id', 'next jsm status name']
    curStatusNameurl = f'https://ict888.atlassian.net/rest/servicedeskapi/request/{jsmIssueId}'
    try:
        defineCurNameCatchDone = True
        reTryCurNameCatchTime = 1
        while defineCurNameCatchDone:
            curStatusNameRes = requests.request("GET",
                                                curStatusNameurl,
                                                headers=prodHeaders)
            if curStatusNameRes.status_code == 200:
                curStatusName = curStatusNameRes.json(
                )['currentStatus']['status']
                defineCurNameCatchDone = False
            else:
                print(curStatusNameRes.status_code)
                if reTryCurNameCatchTime > 5:
                    defineCurNameCatchDone = False
                else:
                    reTryCurNameCatchTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return f'[{jsmIssueKey}] - GET Exception ERROR DURING GET CURRENT STATUS NAME FROM JSM', 500

    if reTryCurNameCatchTime > 5:
        return f'[{jsmIssueKey}] - GET Unexpected HTTP Response Code from JSM DURING GET CURRENT STATUS NAME FROM JSM', 500

    editor = front_data['editor']
    oldStatus = curStatusName
    newStatus = toWhichStatus[2]
    transitionsId = toWhichStatus[0]
    newStatusId = toWhichStatus[1]
    newComment = f'Change ticket status from "{oldStatus}" to "{newStatus}"'

    if newStatus == 'Closed':
        #1 - sort out list for all comments
        queryCommentBySn = get_jsm_sys_prod.query.filter(
            get_jsm_sys_prod.sn == targetJSMSn).first()
        commentInjectList = []  # use this to update the Jira
        curTime = datetime.datetime.now()
        formatTime = curTime.strftime("%Y-%m-%d %H:%M:%S")
        if queryCommentBySn.comments:
            commentLists = json.loads(queryCommentBySn.comments)
            for i in commentLists:
                tmpItem = get_jsm_sys_comments.query.filter(
                    get_jsm_sys_comments.sn == i).first()
                newValue = markdownify.markdownify(tmpItem.content,
                                                   heading_style="ATX")
                commentInjectList.append(
                    f'(update by {tmpItem.handler} at {tmpItem.timestamp}), {newValue}'
                )

        # append final comment let jira know who close this ticket
        commentInjectList.append(
            f'(update by {editor} at {formatTime}), Change ticket status to "Closed"'
        )

        #2 - update to Jira comment for all commments
        url = f"https://ict888.atlassian.net/rest/api/2/issue/{jsmIssueId}/comment"

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
                            f'[{jsmIssueKey}] Done for update - {eachComment}')
                        defineDone = False
                    else:
                        print(response.status_code)
                        reTry += 1
                        if reTry > 5:
                            defineDone = False
                        else:
                            time.sleep(2)

                if reTry > 5:
                    return 'failed during update the all comments to Jira', 500
            except Exception as e:
                print(e)
                return 'failed during update the all comments to Jira', 500

        #3  adjust the Jira status
        urlUpdateStatus = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'
        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})
        # print(f'update status payload = {payload}')
        defineUpdateStatus = True
        reTryUpdateStatus = 1
        try:
            while defineUpdateStatus:
                response = requests.request("POST",
                                            urlUpdateStatus,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                    defineUpdateStatus = False
                    break
                else:
                    print(response.status_code)
                    reTryUpdateStatus += 1
                    if reTryUpdateStatus > 5:
                        defineUpdateStatus = False
                    else:
                        time.sleep(2)

            if reTryUpdateStatus > 5:
                return 'failed when udpate the JSM status (try 5 times)', 500
        except Exception as e:
            print(e)
            return 'failed when udpate the JSM status, go to backend see the Exception', 500

        # 4 update comments db - jsm_net_comments, get comments db sn
        try:
            addOneRow = get_jsm_sys_comments(issueKey=jsmIssueKey,
                                             handler=editor,
                                             content=newComment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{jsmIssueKey}] Done for udpate comments DB')
        except Exception as e:
            print(e)
            return 'bad - due to update jsm sys comments db', 500

        # 5 update local db - jsm_net, update jirastatus and append comments
        try:
            adjustStatus = get_jsm_sys_prod.query.filter(
                get_jsm_sys_prod.sn == targetJSMSn).first()
            adjustStatus.jiraStatus = newStatusId
            if adjustStatus.comments:
                tmpList = json.loads(adjustStatus.comments)
                tmpList.append(commentDbSn)
                adjustStatus.comments = json.dumps(tmpList)
            else:
                adjustStatus.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(f'[{jsmIssueKey}] Done for udpate local DB')
            return 'ok'
        except Exception as e:
            print(e)
            return 'bad - due to update jsm sys db', 500

    # 1. adjust jira ticket status
    def adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor, newComment,
                               targetJSMSn):
        transitionsId = toWhichStatus[0]
        newStatusId = toWhichStatus[1]
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'
        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})

        defineDone = True
        counter = 1

        while defineDone:
            try:
                response = requests.request("POST",
                                            url,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    defineDone = False
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                else:
                    print(response.status_code)
                    counter += 1
                    if counter > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)
                return 'bad - due to Jira update issue, detail please see the backend log'

        if counter > 5:
            print('updateNewIssueStatusToOnProgess, get issue')
            return 'bad - due to Jira update issue (try 5 times)'
        else:
            # 2. update comments db - jsm_net_comments, get comments db sn
            try:
                addOneRow = get_jsm_sys_comments(issueKey=jsmIssueKey,
                                                 handler=editor,
                                                 content=newComment)
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(f'[{jsmIssueKey}] Done for udpate comments DB')
            except Exception as e:
                print(e)
                return 'bad - due to update jsm sys comments db'
            # 3. update local db - jsm_net, update jirastatus and append comments
            try:
                adjustStatus = get_jsm_sys_prod.query.filter(
                    get_jsm_sys_prod.sn == targetJSMSn).first()
                adjustStatus.jiraStatus = newStatusId
                if adjustStatus.comments:
                    tmpList = json.loads(adjustStatus.comments)
                    tmpList.append(commentDbSn)
                    adjustStatus.comments = json.dumps(tmpList)
                else:
                    adjustStatus.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(f'[{jsmIssueKey}] Done for udpate local DB')
                return 'ok'
            except Exception as e:
                print(e)
                return 'bad - due to update jsm sys db'

    updateResult = adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor,
                                          newComment, targetJSMSn)

    if updateResult != 'ok':
        return updateResult, 500
    else:
        return 'ok', 200


# to which status control by frontend postData
@app_mainCowork.route('/jsm/ops/update/status', methods=['GET', 'POST'])
def jsmOpsUpdateStatus():

    front_data = request.get_json(silent=True)
    targetJSMSn = front_data['targetJSMSn']
    jsmIssueId = front_data['jsmIssueId']
    jsmIssueKey = front_data['jsmIssueKey']
    toWhichStatus = front_data[
        'toWhichStatus']  # ['transitions id', 'next jsm status id', 'next jsm status name']
    curStatusNameurl = f'https://ict888.atlassian.net/rest/servicedeskapi/request/{jsmIssueId}'
    try:
        defineCurNameCatchDone = True
        reTryCurNameCatchTime = 1
        while defineCurNameCatchDone:
            curStatusNameRes = requests.request("GET",
                                                curStatusNameurl,
                                                headers=prodHeaders)
            if curStatusNameRes.status_code == 200:
                curStatusName = curStatusNameRes.json(
                )['currentStatus']['status']
                defineCurNameCatchDone = False
            else:
                print(curStatusNameRes.status_code)
                if reTryCurNameCatchTime > 5:
                    defineCurNameCatchDone = False
                else:
                    reTryCurNameCatchTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return f'[{jsmIssueKey}] - GET Exception ERROR DURING GET CURRENT STATUS NAME FROM JSM', 500

    if reTryCurNameCatchTime > 5:
        return f'[{jsmIssueKey}] - GET Unexpected HTTP Response Code from JSM DURING GET CURRENT STATUS NAME FROM JSM', 500

    editor = front_data['editor']
    oldStatus = curStatusName
    newStatus = toWhichStatus[2]
    transitionsId = toWhichStatus[0]
    newStatusId = toWhichStatus[1]
    newComment = f'Change ticket status from "{oldStatus}" to "{newStatus}"'

    if newStatus == 'Closed':
        #1 - sort out list for all comments
        queryCommentBySn = get_jsm_ops_prod.query.filter(
            get_jsm_ops_prod.sn == targetJSMSn).first()
        commentInjectList = []  # use this to update the Jira
        curTime = datetime.datetime.now()
        formatTime = curTime.strftime("%Y-%m-%d %H:%M:%S")
        if queryCommentBySn.comments:
            commentLists = json.loads(queryCommentBySn.comments)
            for i in commentLists:
                tmpItem = get_jsm_ops_comments.query.filter(
                    get_jsm_ops_comments.sn == i).first()
                newValue = markdownify.markdownify(tmpItem.content,
                                                   heading_style="ATX")
                commentInjectList.append(
                    f'(update by {tmpItem.handler} at {tmpItem.timestamp}), {newValue}'
                )

        # append final comment let jira know who close this ticket
        commentInjectList.append(
            f'(update by {editor} at {formatTime}), Change ticket status to "Closed"'
        )

        #2 - update to Jira comment for all commments
        url = f"https://ict888.atlassian.net/rest/api/2/issue/{jsmIssueId}/comment"

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
                            f'[{jsmIssueKey}] Done for update - {eachComment}')
                        defineDone = False
                    else:
                        print(response.status_code)
                        reTry += 1
                        if reTry > 5:
                            defineDone = False
                        else:
                            time.sleep(2)

                if reTry > 5:
                    return 'failed during update the all comments to Jira', 500
            except Exception as e:
                print(e)
                return 'failed during update the all comments to Jira', 500

        #2.5 rollback the desc to jira
        # get the raw html first
        origin_result = get_jsm_ops_prod.query.filter(get_jsm_ops_prod.sn == targetJSMSn).first()
        if origin_result.content_raw:
            rollback_desc_url = f'https://ict888.atlassian.net/rest/api/2/issue/{jsmIssueId}'
            rollback_desc_payload = json.dumps({"fields": {"description": origin_result.content_raw}})
            rollback_desc_defineDone = True
            rollback_counter = 1
            while rollback_desc_defineDone:
                try:
                    response = requests.request("PUT",
                                                rollback_desc_url,
                                                data=rollback_desc_payload,
                                                headers=prodHeaders)
                    if response.status_code == 204:
                        rollback_desc_defineDone = False
                    else:
                        print(f'targetUrl={rollback_desc_url}, JSM return status code={response.status_code}')
                        rollback_counter += 1
                        if rollback_counter > 5:
                            time.sleep(1)
                            rollback_desc_defineDone = False
                        else:
                            time.sleep(2)
                except Exception as e:
                    print(e)
                    if rollback_counter > 5:
                        rollback_desc_defineDone = False
                    else:
                        rollback_counter += 1


        #3  adjust the Jira status
        urlUpdateStatus = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'
        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})
        # print(f'update status payload = {payload}')
        defineUpdateStatus = True
        reTryUpdateStatus = 1
        try:
            while defineUpdateStatus:
                response = requests.request("POST",
                                            urlUpdateStatus,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                    defineUpdateStatus = False
                    break
                else:
                    print(response.status_code)
                    reTryUpdateStatus += 1
                    if reTryUpdateStatus > 5:
                        defineUpdateStatus = False
                    else:
                        time.sleep(2)

            if reTryUpdateStatus > 5:
                return 'failed when udpate the JSM status (try 5 times)', 500
        except Exception as e:
            print(e)
            return 'failed when udpate the JSM status, go to backend see the Exception', 500

        # 4 update comments db - jsm_net_comments, get comments db sn
        try:
            addOneRow = get_jsm_ops_comments(issueKey=jsmIssueKey,
                                             handler=editor,
                                             commentType=2,
                                             content=newComment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{jsmIssueKey}] Done for udpate comments DB')
        except Exception as e:
            print(e)
            return 'bad - due to update jsm ops comments db', 500

        # 5 update local db - jsm_net, update jirastatus and append comments
        try:
            adjustStatus = get_jsm_ops_prod.query.filter(
                get_jsm_ops_prod.sn == targetJSMSn).first()
            adjustStatus.jiraStatus = newStatusId
            if adjustStatus.comments:
                tmpList = json.loads(adjustStatus.comments)
                tmpList.append(commentDbSn)
                adjustStatus.comments = json.dumps(tmpList)
            else:
                adjustStatus.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(f'[{jsmIssueKey}] Done for udpate local DB')
            return 'ok'
        except Exception as e:
            print(e)
            return 'bad - due to update jsm ops db', 500

    # 1. adjust jira ticket status
    def adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor, newComment,
                               targetJSMSn):
        transitionsId = toWhichStatus[0]
        newStatusId = toWhichStatus[1]
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'

        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})

        defineDone = True
        counter = 1

        while defineDone:
            try:
                response = requests.request("POST",
                                            url,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    defineDone = False
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                else:
                    print(response.status_code)
                    counter += 1
                    if counter > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)
                return 'bad - due to Jira update issue, detail please see the backend log'

        if counter > 5:
            print('updateNewIssueStatusToOnProgess, get issue')
            return 'bad - due to Jira update issue (try 5 times)'
        else:
            # 2. update comments db - jsm_net_comments, get comments db sn
            try:
                addOneRow = get_jsm_ops_comments(issueKey=jsmIssueKey,
                                                 handler=editor,
                                                 commentType=2,
                                                 content=newComment)
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(f'[{jsmIssueKey}] Done for udpate comments DB')
            except Exception as e:
                print(e)
                return 'bad - due to update jsm ops comments db'
            # 3. update local db - jsm_net, update jirastatus and append comments
            try:
                adjustStatus = get_jsm_ops_prod.query.filter(
                    get_jsm_ops_prod.sn == targetJSMSn).first()
                adjustStatus.jiraStatus = newStatusId
                if adjustStatus.comments:
                    tmpList = json.loads(adjustStatus.comments)
                    tmpList.append(commentDbSn)
                    adjustStatus.comments = json.dumps(tmpList)
                else:
                    adjustStatus.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(f'[{jsmIssueKey}] Done for udpate local DB')
                return 'ok'
            except Exception as e:
                print(e)
                return 'bad - due to update jsm ops db'

    updateResult = adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor,
                                          newComment, targetJSMSn)

    if updateResult != 'ok':
        return updateResult, 500
    else:
        return 'ok', 200


# to which status control by frontend postData
@app_mainCowork.route('/jsm/dba/update/status', methods=['GET', 'POST'])
def jsmDbaUpdateStatus():
    # JSM header

    front_data = request.get_json(silent=True)
    targetJSMSn = front_data['targetJSMSn']
    jsmIssueId = front_data['jsmIssueId']
    jsmIssueKey = front_data['jsmIssueKey']
    toWhichStatus = front_data[
        'toWhichStatus']  # ['transitions id', 'next jsm status id', 'next jsm status name']
    curStatusNameurl = f'https://ict888.atlassian.net/rest/servicedeskapi/request/{jsmIssueId}'
    try:
        defineCurNameCatchDone = True
        reTryCurNameCatchTime = 1
        while defineCurNameCatchDone:
            curStatusNameRes = requests.request("GET",
                                                curStatusNameurl,
                                                headers=prodHeaders)
            if curStatusNameRes.status_code == 200:
                curStatusName = curStatusNameRes.json(
                )['currentStatus']['status']
                defineCurNameCatchDone = False
            else:
                print(curStatusNameRes.status_code)
                if reTryCurNameCatchTime > 5:
                    defineCurNameCatchDone = False
                else:
                    reTryCurNameCatchTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return f'[{jsmIssueKey}] - GET Exception ERROR DURING GET CURRENT STATUS NAME FROM JSM', 500

    if reTryCurNameCatchTime > 5:
        return f'[{jsmIssueKey}] - GET Unexpected HTTP Response Code from JSM DURING GET CURRENT STATUS NAME FROM JSM', 500

    editor = front_data['editor']
    oldStatus = curStatusName
    newStatus = toWhichStatus[2]
    transitionsId = toWhichStatus[0]
    newStatusId = toWhichStatus[1]
    newComment = f'Change ticket status from "{oldStatus}" to "{newStatus}"'

    if newStatus == 'Closed':
        #1 - sort out list for all comments
        queryCommentBySn = get_jsm_dba_prod.query.filter(
            get_jsm_dba_prod.sn == targetJSMSn).first()
        commentInjectList = []  # use this to update the Jira
        curTime = datetime.datetime.now()
        formatTime = curTime.strftime("%Y-%m-%d %H:%M:%S")
        if queryCommentBySn.comments:
            commentLists = json.loads(queryCommentBySn.comments)
            for i in commentLists:
                tmpItem = get_jsm_dba_comments.query.filter(
                    get_jsm_dba_comments.sn == i).first()
                newValue = markdownify.markdownify(tmpItem.content,
                                                   heading_style="ATX")
                commentInjectList.append(
                    f'(update by {tmpItem.handler} at {tmpItem.timestamp}), {newValue}'
                )

        # append final comment let jira know who close this ticket
        commentInjectList.append(
            f'(update by {editor} at {formatTime}), Change ticket status to "Closed"'
        )

        #2 - update to Jira comment for all commments
        url = f"https://ict888.atlassian.net/rest/api/2/issue/{jsmIssueId}/comment"

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
                            f'[{jsmIssueKey}] Done for update - {eachComment}')
                        defineDone = False
                    else:
                        print(response.status_code)
                        reTry += 1
                        if reTry > 5:
                            defineDone = False
                        else:
                            time.sleep(2)

                if reTry > 5:
                    return 'failed during update the all comments to Jira', 500
            except Exception as e:
                print(e)
                return 'failed during update the all comments to Jira', 500

        #3  adjust the Jira status
        urlUpdateStatus = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'
        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})
        # print(f'update status payload = {payload}')
        defineUpdateStatus = True
        reTryUpdateStatus = 1
        try:
            while defineUpdateStatus:
                response = requests.request("POST",
                                            urlUpdateStatus,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                    defineUpdateStatus = False
                    break
                else:
                    print(response.status_code)
                    reTryUpdateStatus += 1
                    if reTryUpdateStatus > 5:
                        defineUpdateStatus = False
                    else:
                        time.sleep(2)

            if reTryUpdateStatus > 5:
                return 'failed when udpate the JSM status (try 5 times)', 500
        except Exception as e:
            print(e)
            return 'failed when udpate the JSM status, go to backend see the Exception', 500

        # 4 update comments db - jsm_net_comments, get comments db sn
        try:
            addOneRow = get_jsm_dba_comments(issueKey=jsmIssueKey,
                                             handler=editor,
                                             content=newComment)
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            db.session.close()
            print(f'[{jsmIssueKey}] Done for udpate comments DB')
        except Exception as e:
            print(e)
            return 'bad - due to update jsm dba comments db', 500

        # 5 update local db - jsm_net, update jirastatus and append comments
        try:
            adjustStatus = get_jsm_dba_prod.query.filter(
                get_jsm_dba_prod.sn == targetJSMSn).first()
            adjustStatus.jiraStatus = newStatusId
            if adjustStatus.comments:
                tmpList = json.loads(adjustStatus.comments)
                tmpList.append(commentDbSn)
                adjustStatus.comments = json.dumps(tmpList)
            else:
                adjustStatus.comments = json.dumps([commentDbSn])
            db.session.commit()
            db.session.close()
            db.session.remove()
            print(f'[{jsmIssueKey}] Done for udpate local DB')
            return 'ok'
        except Exception as e:
            print(e)
            return 'bad - due to update jsm dba db', 500

    # 1. adjust jira ticket status
    def adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor, newComment,
                               targetJSMSn):
        transitionsId = toWhichStatus[0]
        newStatusId = toWhichStatus[1]
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{jsmIssueKey}/transitions'

        payload = json.dumps({"transition": {"id": f'{transitionsId}'}})

        defineDone = True
        counter = 1

        while defineDone:
            try:
                response = requests.request("POST",
                                            url,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    defineDone = False
                    print(f'[{jsmIssueKey}] Done for udpate JSM status')
                else:
                    print(response.status_code)
                    counter += 1
                    if counter > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)
                return 'bad - due to Jira update issue, detail please see the backend log'

        if counter > 5:
            print('updateNewIssueStatusToOnProgess, get issue')
            return 'bad - due to Jira update issue (try 5 times)'
        else:
            # 2. update comments db - jsm_net_comments, get comments db sn
            try:
                addOneRow = get_jsm_dba_comments(issueKey=jsmIssueKey,
                                                 handler=editor,
                                                 content=newComment)
                db.session.add(addOneRow)
                db.session.commit()
                db.session.refresh(addOneRow)
                commentDbSn = addOneRow.sn
                db.session.close()
                print(f'[{jsmIssueKey}] Done for udpate comments DB')
            except Exception as e:
                print(e)
                return 'bad - due to update jsm dba comments db'
            # 3. update local db - jsm_net, update jirastatus and append comments
            try:
                adjustStatus = get_jsm_dba_prod.query.filter(
                    get_jsm_dba_prod.sn == targetJSMSn).first()
                adjustStatus.jiraStatus = newStatusId
                if adjustStatus.comments:
                    tmpList = json.loads(adjustStatus.comments)
                    tmpList.append(commentDbSn)
                    adjustStatus.comments = json.dumps(tmpList)
                else:
                    adjustStatus.comments = json.dumps([commentDbSn])
                db.session.commit()
                db.session.close()
                db.session.remove()
                print(f'[{jsmIssueKey}] Done for udpate local DB')
                return 'ok'
            except Exception as e:
                print(e)
                return 'bad - due to update jsm dba db'

    updateResult = adjustJiraTicketstatus(jsmIssueKey, toWhichStatus, editor,
                                          newComment, targetJSMSn)

    if updateResult != 'ok':
        return updateResult, 500
    else:
        return 'ok', 200


# to update the JSM option ( include title and description) by api
@app_mainCowork.route('/jsm/net/update/option', methods=['GET', 'POST'])
def jsmUpdateNetOption():
    #1 list default option
    front_data = request.get_json(silent=True)
    editor = front_data['editor']
    target = front_data['target']
    issueId = front_data['jsmIssueId']
    issuekey = front_data['jsmIssueKey']
    localSn = front_data['targetJSMSn']
    _value = front_data['newValue']

    #2 check the target, and sort out the url and payload
    # url = f'https://anyhow-test4u.atlassian.net/rest/api/3/issue/{issueId}'
    url = f'https://ict888.atlassian.net/rest/api/3/issue/{issueId}'
    if target == 'title':
        payload = json.dumps({"fields": {"summary": f'{_value}'}})
        newComment = f'Change ticket title to "{_value}"'
    elif target == 'description':
        url = f'https://ict888.atlassian.net/rest/api/2/issue/{issueId}'
        newValue = markdownify.markdownify(_value, heading_style="ATX")
        payload = json.dumps({"fields": {"description": newValue}})
        newComment = f'Update ticket description'
    elif target == 'handler':
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10274',
            get_jsm_field_sets_sortOut.contextId == 1).all()
        option_handler = [{
            "accountId": x._id
        } for x in optionsSet if x._value in _value]
        payloadDict = {'fields': {}}
        payloadDict['fields'].setdefault('customfield_10274', option_handler)
        payload = json.dumps(payloadDict)
        newComment = f'Update ticket handler to {", ".join(_value)}'
    elif target == 'participant':
        payloadDict = {'fields': {}}
        if len(_value) == 0:
            print('change to 0')
            payloadDict['fields'].setdefault('customfield_10206', None)
            payload = json.dumps(payloadDict)
            newComment = f'Remove all participants'
        else:
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10206',
                get_jsm_field_sets_sortOut.contextId == 1).all()
            option_participants = [{
                "accountId": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict['fields'].setdefault('customfield_10206',
                                             option_participants)
            payload = json.dumps(payloadDict)
            newComment = f'Update participant to {", ".join(_value)}'
    elif target == 'category':
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10286',
            get_jsm_field_sets_sortOut._value == _value,
            get_jsm_field_sets_sortOut.contextId == 1).first()
        option_category = {"id": optionsSet._id}
        payloadDict = {'fields': {}}
        payloadDict['fields'].setdefault('customfield_10286', option_category)
        payload = json.dumps(payloadDict)
        newComment = f'Update category to {_value}'
    elif target == 'facilities':
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10287',
            get_jsm_field_sets_sortOut.contextId == 1).all()
        option_facilities = [{
            "id": x._id
        } for x in optionsSet if x._value in _value]
        payloadDict = {'fields': {}}
        payloadDict['fields'].setdefault('customfield_10287',
                                         option_facilities)
        payload = json.dumps(payloadDict)
        newComment = f'Update facilities to {", ".join(_value)}'
    elif target == 'infra':
        optionsSet = get_jsm_field_sets_sortOut.query.filter(
            get_jsm_field_sets_sortOut.fieldId == 'customfield_10264',
            get_jsm_field_sets_sortOut.contextId == 1).all()
        option_infra = [{
            "id": x._id
        } for x in optionsSet if x._value in _value]
        payloadDict = {'fields': {}}
        payloadDict['fields'].setdefault('customfield_10264', option_infra)
        payload = json.dumps(payloadDict)
        newComment = f'Update infra to {", ".join(_value)}'
    elif target == 'vendor':
        payloadDict = {'fields': {}}
        if len(_value) == 0:
            payloadDict['fields'].setdefault('customfield_10288', None)
            payload = json.dumps(payloadDict)
            newComment = f'Remove all vendors'
        else:
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10288',
                get_jsm_field_sets_sortOut.contextId == 1).all()
            option_vendor = [{
                "id": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict['fields'].setdefault('customfield_10288',
                                             option_vendor)
            payload = json.dumps(payloadDict)
            newComment = f'Update vendors to {", ".join(_value)}'
    elif target == 'time':
        # print(_value) [startTime, endTime]
        print(_value)
        payloadDict = {'fields': {}}
        sTimeObject = datetime.datetime.strptime(_value[0],
                                                 "%Y-%m-%d %H:%M:%S")
        eTimeObject = datetime.datetime.strptime(_value[1],
                                                 "%Y-%m-%d %H:%M:%S")
        payloadDict['fields'].setdefault(
            'customfield_10282',
            sTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
        payloadDict['fields'].setdefault(
            'customfield_10283',
            eTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
        payload = json.dumps(payloadDict)
        newComment = f'Update time attribute'

    #3 update JSM
    defineDone = True
    counter = 1
    while defineDone:
        try:
            response = requests.request("PUT",
                                        url,
                                        data=payload,
                                        headers=prodHeaders)
            if response.status_code == 204:
                defineDone = False
            else:
                print(
                    f'targetUrl={url}, JSM return status code={response.status_code}'
                )
                counter += 1
                if counter > 5:
                    defineDone = False
                else:
                    time.sleep(2)
        except Exception as e:
            print(e)
            counter += 1
            if counter > 5:
                defineDone = False
            else:
                time.sleep(2)

    if counter > 5:
        return 'failed due to update JSM by API', 500

    #4 update the commentDb by this action
    try:
        addOneRow = get_jsm_net_comments(issueKey=issuekey,
                                         handler=editor,
                                         content=newComment)
        db.session.add(addOneRow)
        db.session.commit()
        db.session.refresh(addOneRow)
        commentDbSn = addOneRow.sn
        db.session.close()
    except Exception as e:
        print(e)
        return 'failed due to update comments on local', 500

    #5 update localDb
    try:
        # default
        queryByLocalSn = get_jsm_net_prod.query.filter(
            get_jsm_net_prod.sn == localSn).first()
        # update comment
        if queryByLocalSn.comments:
            tmpList = json.loads(queryByLocalSn.comments)
            tmpList.append(commentDbSn)
            queryByLocalSn.comments = json.dumps(tmpList)
        else:
            queryByLocalSn.comments = json.dumps([commentDbSn])

        # update by target
        if target == 'title':
            queryByLocalSn.title = _value
        elif target == 'description':
            queryByLocalSn.description = _value
        elif target == 'handler':
            queryByLocalSn.custom_handler = json.dumps(_value)
        elif target == 'participant':
            if len(_value) == 0:
                queryByLocalSn.custom_participant = None
            else:
                queryByLocalSn.custom_participant = json.dumps(_value)
        elif target == 'category':
            queryByLocalSn.custom_category = _value
        elif target == 'facilities':
            queryByLocalSn.custom_facilities = json.dumps(_value)
        elif target == 'infra':
            queryByLocalSn.custom_infra = json.dumps(_value)
        elif target == 'vendor':
            if len(_value) == 0:
                queryByLocalSn.custom_vendor = None
            else:
                queryByLocalSn.custom_vendor = json.dumps(_value)
        elif target == 'time':
            queryByLocalSn.startTime = sTimeObject
            queryByLocalSn.endTime = eTimeObject

        db.session.commit()
        db.session.close()
        db.session.remove()
        return 'ok', 200
    except Exception as e:
        print(e)
        return f'failed due to update JSM {localSn} on local', 500


@app_mainCowork.route('/jsm/sys/update/option', methods=['GET', 'POST'])
def jsmUpdateSysOption():
    # 1 list default option
    front_data = request.get_json(silent=True)
    editor = front_data['editor']
    target = front_data['target']
    issueId = front_data['jsmIssueId']
    issuekey = front_data['jsmIssueKey']
    localSn = front_data['targetJSMSn']
    _value = front_data['newValue']

    # 2 check the target, and sort out the url and payload
    try:
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{issueId}'
        if target == 'title':
            payload = json.dumps({"fields": {"summary": f'{_value}'}})
            newComment = f'Change ticket title to "{_value}"'
        elif target == 'description':
            url = f'https://ict888.atlassian.net/rest/api/2/issue/{issueId}'
            newValue = markdownify.markdownify(_value, heading_style="ATX")
            payload = json.dumps({"fields": {"description": newValue}})
            newComment = f'Update ticket description'

        elif target == 'handler':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10274',
                get_jsm_field_sets_sortOut.contextId == 2).all()
            option_handler = [{
                "accountId": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10274',
                                             option_handler)
            payload = json.dumps(payloadDict)
            newComment = f'Update ticket handler to {", ".join(_value)}'
        elif target == 'participant':
            payloadDict = {'fields': {}}
            if len(_value) == 0:
                print('change to 0')
                payloadDict['fields'].setdefault('customfield_10206', None)
                payload = json.dumps(payloadDict)
                newComment = f'Remove all participants'
            else:
                optionsSet = get_jsm_field_sets_sortOut.query.filter(
                    get_jsm_field_sets_sortOut.fieldId == 'customfield_10206',
                    get_jsm_field_sets_sortOut.contextId == 2).all()
                option_participants = [{
                    "accountId": x._id
                } for x in optionsSet if x._value in _value]
                payloadDict['fields'].setdefault('customfield_10206',
                                                 option_participants)
                payload = json.dumps(payloadDict)
                newComment = f'Update participant to {", ".join(_value)}'

        elif target == 'bizUnit':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10281',
                get_jsm_field_sets_sortOut.contextId == 2).all()
            option_bizUnit = [{
                "id": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10281',
                                             option_bizUnit)
            payload = json.dumps(payloadDict)
            newComment = f'Update bizUnit to {", ".join(_value)}'

        elif target == 'category':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10285',
                get_jsm_field_sets_sortOut.contextId == 2).all()
            option_category = [{
                "id": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10285',
                                             option_category)
            payload = json.dumps(payloadDict)
            newComment = f'Update category to {", ".join(_value)}'
        elif target == 'priority':
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
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('priority', priorityDict[_value])
            payload = json.dumps(payloadDict)
            newComment = f'Update priority to {_value}'
        elif target == 'time':
            # print(_value) [startTime, endTime]
            print(_value)
            payloadDict = {'fields': {}}
            sTimeObject = datetime.datetime.strptime(_value[0],
                                                     "%Y-%m-%d %H:%M")
            eTimeObject = datetime.datetime.strptime(_value[1],
                                                     "%Y-%m-%d %H:%M")
            payloadDict['fields'].setdefault(
                'customfield_10282',
                sTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            payloadDict['fields'].setdefault(
                'customfield_10283',
                eTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            payload = json.dumps(payloadDict)
            newComment = f'Update time attribute'
        print(f'[{issuekey}] Done for export the {target} PAYLOAD')
    except Exception as e:
        print(e)
        print(f'[{issuekey}] Get ERROR when export the {target} PAYLOAD')
        return f'[{issuekey}] Get ERROR when export the {target} PAYLOAD', 500

    # 3 update JSM
    defineDone = True
    counter = 1
    while defineDone:
        try:
            response = requests.request("PUT",
                                        url,
                                        data=payload,
                                        headers=prodHeaders)
            if response.status_code == 204:
                print(f'[{issuekey}] Done for update {target} to JSM')
                defineDone = False
            else:
                print(
                    f'targetUrl={url}, JSM return status code={response.status_code}'
                )
                counter += 1
                if counter > 5:
                    defineDone = False
                else:
                    time.sleep(2)
        except Exception as e:
            print(e)
            counter += 1
            if counter > 5:
                defineDone = False
            else:
                time.sleep(2)

    if counter > 5:
        print(f'[{issuekey}] Get ERROR when update {target} to JSM (x5)')
        return f'[{issuekey}] Get ERROR when update {target} to JSM (x5)', 500

    # 4 update the commentDb by this action
    try:
        addOneRow = get_jsm_sys_comments(issueKey=issuekey,
                                         handler=editor,
                                         content=newComment)
        db.session.add(addOneRow)
        db.session.commit()
        db.session.refresh(addOneRow)
        commentDbSn = addOneRow.sn
        db.session.close()
        print(f'[{issuekey}] Done for update new row to local comment db')
    except Exception as e:
        print(e)
        print(
            f'[{issuekey}] Get ERROR when update new row to local comment db')
        return f'[{issuekey}] Get ERROR when update new row to local comment db', 500

    # 5 update localDb
    try:
        # default
        queryByLocalSn = get_jsm_sys_prod.query.filter(
            get_jsm_sys_prod.sn == localSn).first()
        # update comment
        if queryByLocalSn.comments:
            tmpList = json.loads(queryByLocalSn.comments)
            tmpList.append(commentDbSn)
            queryByLocalSn.comments = json.dumps(tmpList)
        else:
            queryByLocalSn.comments = json.dumps([commentDbSn])

        # update by target
        if target == 'title':
            queryByLocalSn.title = _value
        elif target == 'description':
            queryByLocalSn.description = _value
        elif target == 'handler':
            queryByLocalSn.custom_handler = json.dumps(_value)
        elif target == 'participant':
            if len(_value) == 0:
                queryByLocalSn.custom_participant = None
            else:
                queryByLocalSn.custom_participant = json.dumps(_value)
        elif target == 'bizUnit':
            queryByLocalSn.custom_bizUnit = json.dumps(_value)
        elif target == 'category':
            queryByLocalSn.custom_category = json.dumps(_value)
        elif target == 'priority':
            queryByLocalSn.custom_priority = _value
        elif target == 'time':
            queryByLocalSn.startTime = sTimeObject
            queryByLocalSn.endTime = eTimeObject

        db.session.commit()
        db.session.close()
        db.session.remove()
        print(
            f'[{issuekey}] Done for update JSM {localSn} local db for {target}'
        )
        return 'ok', 200
    except Exception as e:
        print(e)
        print(f'[{issuekey}] Get ERROR when update JSM {localSn} local db')
        return f'[{issuekey}] Get ERROR when update JSM {localSn} local db', 500


@app_mainCowork.route('/jsm/ops/update/option', methods=['GET', 'POST'])
def jsmUpdateOpsOption():

    # 1 list default option
    front_data = request.get_json(silent=True)
    editor = front_data['editor']
    target = front_data['target']
    issueId = front_data['jsmIssueId']
    issuekey = front_data['jsmIssueKey']
    localSn = front_data['targetJSMSn']
    _value = front_data['newValue']

    # 2 check the target, and sort out the url and payload
    try:
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{issueId}'
        if target == 'title':
            payload = json.dumps({"fields": {"summary": f'{_value}'}})
            newComment = f'Change ticket title to "{_value}"'
        elif target == 'description':
            url = f'https://ict888.atlassian.net/rest/api/2/issue/{issueId}'
            newValue = markdownify.markdownify(_value, heading_style="ATX")
            payload = json.dumps({"fields": {"description": newValue}})
            newComment = f'Update ticket description'
        elif target == 'handler':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10274',
                get_jsm_field_sets_sortOut.contextId == 4).all()
            option_handler = [{
                "accountId": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10274',
                                             option_handler)
            payload = json.dumps(payloadDict)
            print(payload)
            newComment = f'Update ticket handler to {", ".join(_value)}'
        elif target == 'participant':
            payloadDict = {'fields': {}}
            if len(_value) == 0:
                print('change to 0')
                payloadDict['fields'].setdefault('customfield_10206', None)
                payload = json.dumps(payloadDict)
                newComment = f'Remove all participants'
            else:
                optionsSet = get_jsm_field_sets_sortOut.query.filter(
                    get_jsm_field_sets_sortOut.fieldId == 'customfield_10206',
                    get_jsm_field_sets_sortOut.contextId == 4).all()
                option_participants = [{
                    "accountId": x._id
                } for x in optionsSet if x._value in _value]
                payloadDict['fields'].setdefault('customfield_10206',
                                                 option_participants)
                payload = json.dumps(payloadDict)
                newComment = f'Update participant to {", ".join(_value)}'

        elif target == 'category':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10290',
                get_jsm_field_sets_sortOut._value == _value,
                get_jsm_field_sets_sortOut.contextId == 4).first()
            option_customfield_10290 = {"id": optionsSet._id}
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10290',
                                             option_customfield_10290)
            payload = json.dumps(payloadDict)
            newComment = f'Update category to {_value}'

        elif target == 'bizUnit':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10281',
                get_jsm_field_sets_sortOut.contextId == 4).all()
            option_customfield_10281 = [{
                "id": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10281',
                                             option_customfield_10281)
            payload = json.dumps(payloadDict)
            newComment = f'Update bizUnit to {", ".join(_value)}'

        elif target == 'infra':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10264',
                get_jsm_field_sets_sortOut.contextId == 4).all()
            option_customfield_10264 = [{
                "id": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10264',
                                             option_customfield_10264)
            payload = json.dumps(payloadDict)
            newComment = f'Update infra to {", ".join(_value)}'

        elif target == 'time':
            # print(_value) [startTime, endTime]
            payloadDict = {'fields': {}}
            sTimeObject = datetime.datetime.strptime(_value[0],
                                                     "%Y-%m-%d %H:%M")
            eTimeObject = datetime.datetime.strptime(_value[1],
                                                     "%Y-%m-%d %H:%M")
            payloadDict['fields'].setdefault(
                'customfield_10282',
                sTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            payloadDict['fields'].setdefault(
                'customfield_10283',
                eTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            payload = json.dumps(payloadDict)
            newComment = f'Update time attribute'
        print(f'[{issuekey}] Done for export the {target} PAYLOAD')
    except Exception as e:
        print(e)
        print(f'[{issuekey}] Get ERROR when export the {target} PAYLOAD')
        return f'[{issuekey}] Get ERROR when export the {target} PAYLOAD', 500

    # 3 update JSM
    defineDone = True
    counter = 1
    while defineDone:
        try:
            response = requests.request("PUT",
                                        url,
                                        data=payload,
                                        headers=prodHeaders)
            if response.status_code == 204:
                print(f'[{issuekey}] Done for update {target} to JSM')
                defineDone = False
            else:
                print(
                    f'targetUrl={url}, JSM return status code={response.status_code}'
                )
                counter += 1
                if counter > 5:
                    defineDone = False
                else:
                    time.sleep(2)
        except Exception as e:
            print(e)
            counter += 1
            if counter > 5:
                defineDone = False
            else:
                time.sleep(2)

    if counter > 5:
        print(f'[{issuekey}] Get ERROR when update {target} to JSM (x5)')
        return f'[{issuekey}] Get ERROR when update {target} to JSM (x5)', 500

    # 4 update the commentDb by this action
    try:
        if target == 'title' or target == 'description' or target == 'participant' or target == 'handler':
            addOneRow = get_jsm_ops_comments(issueKey=issuekey,
                                            handler=editor,
                                            commentType=2,
                                            content=newComment)
        else:
            addOneRow = get_jsm_ops_comments(issueKey=issuekey,
                                            handler=editor,
                                            content=newComment)
        db.session.add(addOneRow)
        db.session.commit()
        db.session.refresh(addOneRow)
        commentDbSn = addOneRow.sn
        db.session.close()
        print(f'[{issuekey}] Done for update new row to local comment db')
    except Exception as e:
        print(e)
        print(
            f'[{issuekey}] Get ERROR when update new row to local comment db')
        return f'[{issuekey}] Get ERROR when update new row to local comment db', 500

    # 5 update localDb
    try:
        # default
        queryByLocalSn = get_jsm_ops_prod.query.filter(
            get_jsm_ops_prod.sn == localSn).first()
        # update comment
        if queryByLocalSn.comments:
            tmpList = json.loads(queryByLocalSn.comments)
            tmpList.append(commentDbSn)
            queryByLocalSn.comments = json.dumps(tmpList)
        else:
            queryByLocalSn.comments = json.dumps([commentDbSn])

        # update by target
        if target == 'title':
            queryByLocalSn.title = _value
        elif target == 'description':
            queryByLocalSn.description = _value
        elif target == 'handler':
            queryByLocalSn.custom_handler = json.dumps(_value)
        elif target == 'participant':
            if len(_value) == 0:
                queryByLocalSn.custom_participant = None
            else:
                queryByLocalSn.custom_participant = json.dumps(_value)
        elif target == 'category':
            queryByLocalSn.custom_category = _value
        elif target == 'bizUnit':
            queryByLocalSn.custom_bizUnit = json.dumps(_value)
        elif target == 'infra':
            queryByLocalSn.custom_infra = json.dumps(_value)
        elif target == 'time':
            queryByLocalSn.startTime = sTimeObject
            queryByLocalSn.endTime = eTimeObject

        db.session.commit()
        db.session.close()
        db.session.remove()
        print(
            f'[{issuekey}] Done for update JSM {localSn} local db for {target}'
        )
        return 'ok', 200
    except Exception as e:
        print(e)
        print(f'[{issuekey}] Get ERROR when update JSM {localSn} local db')
        return f'[{issuekey}] Get ERROR when update JSM {localSn} local db', 500


@app_mainCowork.route('/jsm/dba/update/option', methods=['GET', 'POST'])
def jsmUpdateDbaOption():
    # 1 list default option
    front_data = request.get_json(silent=True)
    editor = front_data['editor']
    target = front_data['target']
    issueId = front_data['jsmIssueId']
    issuekey = front_data['jsmIssueKey']
    localSn = front_data['targetJSMSn']
    _value = front_data['newValue']

    # 2 check the target, and sort out the url and payload
    try:
        url = f'https://ict888.atlassian.net/rest/api/3/issue/{issueId}'
        if target == 'title':
            payload = json.dumps({"fields": {"summary": f'{_value}'}})
            newComment = f'Change ticket title to "{_value}"'
        elif target == 'description':
            url = f'https://ict888.atlassian.net/rest/api/2/issue/{issueId}'
            newValue = markdownify.markdownify(_value, heading_style="ATX")
            payload = json.dumps({"fields": {"description": newValue}})
            newComment = f'Update ticket description'
        elif target == 'handler':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10274',
                get_jsm_field_sets_sortOut.contextId == 3).all()
            option_handler = [{
                "accountId": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10274',
                                             option_handler)
            payload = json.dumps(payloadDict)
            newComment = f'Update ticket handler to {", ".join(_value)}'
        elif target == 'participant':
            payloadDict = {'fields': {}}
            if len(_value) == 0:
                print('change to 0')
                payloadDict['fields'].setdefault('customfield_10206', None)
                payload = json.dumps(payloadDict)
                newComment = f'Remove all participants'
            else:
                optionsSet = get_jsm_field_sets_sortOut.query.filter(
                    get_jsm_field_sets_sortOut.fieldId == 'customfield_10206',
                    get_jsm_field_sets_sortOut.contextId == 3).all()
                option_participants = [{
                    "accountId": x._id
                } for x in optionsSet if x._value in _value]
                payloadDict['fields'].setdefault('customfield_10206',
                                                 option_participants)
                payload = json.dumps(payloadDict)
                newComment = f'Update participant to {", ".join(_value)}'

        elif target == 'bizUnit':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10281',
                get_jsm_field_sets_sortOut.contextId == 3).all()
            option_bu = [{
                "id": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10281', option_bu)
            payload = json.dumps(payloadDict)
            newComment = f'Update bizUnit to {", ".join(_value)}'

        elif target == 'category':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10289',
                get_jsm_field_sets_sortOut.contextId == 3).all()
            option_category = [{
                "id": x._id
            } for x in optionsSet if x._value in _value]
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10289',
                                             option_category)
            payload = json.dumps(payloadDict)
            newComment = f'Update category to {", ".join(_value)}'

        elif target == 'priority':
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
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('priority', priorityDict[_value])
            payload = json.dumps(payloadDict)
            newComment = f'Update priority to {_value}'

        elif target == 'time':
            payloadDict = {'fields': {}}
            sTimeObject = datetime.datetime.strptime(_value[0],
                                                     "%Y-%m-%d %H:%M")
            eTimeObject = datetime.datetime.strptime(_value[1],
                                                     "%Y-%m-%d %H:%M")
            payloadDict['fields'].setdefault(
                'customfield_10282',
                sTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            payloadDict['fields'].setdefault(
                'customfield_10283',
                eTimeObject.strftime("%Y-%m-%dT%H:%M:%S.000+0800"))
            payload = json.dumps(payloadDict)
            newComment = f'Update time attribute'
        elif target == 'impact':
            optionsSet = get_jsm_field_sets_sortOut.query.filter(
                get_jsm_field_sets_sortOut.fieldId == 'customfield_10244',
                get_jsm_field_sets_sortOut.contextId == 3).all()
            if _value:
                option_impact = [{
                    "id": x._id
                } for x in optionsSet if x._value == 'Yes'][0]
                newComment = 'Change service impact value to "Yes"'
            else:
                option_impact = [{
                    "id": x._id
                } for x in optionsSet if x._value == 'No'][0]
                newComment = 'Change service impact value to "No"'
            payloadDict = {'fields': {}}
            payloadDict['fields'].setdefault('customfield_10244',
                                             option_impact)
            payload = json.dumps(payloadDict)
        print(f'[{issuekey}] Done for export the {target} PAYLOAD')
    except Exception as e:
        print(e)
        print(f'[{issuekey}] Get ERROR when export the {target} PAYLOAD')
        return f'[{issuekey}] Get ERROR when export the {target} PAYLOAD', 500

    # 3 update JSM
    defineDone = True
    counter = 1
    while defineDone:
        try:
            response = requests.request("PUT",
                                        url,
                                        data=payload,
                                        headers=prodHeaders)
            if response.status_code == 204:
                print(f'[{issuekey}] Done for update {target} to JSM')
                defineDone = False
            else:
                print(
                    f'targetUrl={url}, JSM return status code={response.status_code}'
                )
                counter += 1
                if counter > 5:
                    defineDone = False
                else:
                    time.sleep(2)
        except Exception as e:
            print(e)
            counter += 1
            if counter > 5:
                defineDone = False
            else:
                time.sleep(2)

    if counter > 5:
        print(f'[{issuekey}] Get ERROR when update {target} to JSM (x5)')
        return f'[{issuekey}] Get ERROR when update {target} to JSM (x5)', 500

    # 4 update the commentDb by this action
    try:
        addOneRow = get_jsm_dba_comments(issueKey=issuekey,
                                         handler=editor,
                                         content=newComment)
        db.session.add(addOneRow)
        db.session.commit()
        db.session.refresh(addOneRow)
        commentDbSn = addOneRow.sn
        db.session.close()
        print(f'[{issuekey}] Done for update new row to local comment db')
    except Exception as e:
        print(e)
        print(
            f'[{issuekey}] Get ERROR when update new row to local comment db')
        return f'[{issuekey}] Get ERROR when update new row to local comment db', 500

    # 5 update localDb
    try:
        # default
        queryByLocalSn = get_jsm_dba_prod.query.filter(
            get_jsm_dba_prod.sn == localSn).first()
        # update comment
        if queryByLocalSn.comments:
            tmpList = json.loads(queryByLocalSn.comments)
            tmpList.append(commentDbSn)
            queryByLocalSn.comments = json.dumps(tmpList)
        else:
            queryByLocalSn.comments = json.dumps([commentDbSn])

        # update by target
        if target == 'title':
            queryByLocalSn.title = _value
        elif target == 'description':
            queryByLocalSn.description = _value
        elif target == 'handler':
            queryByLocalSn.custom_handler = json.dumps(_value)
        elif target == 'participant':
            if len(_value) == 0:
                queryByLocalSn.custom_participant = None
            else:
                queryByLocalSn.custom_participant = json.dumps(_value)
        elif target == 'bizUnit':
            queryByLocalSn.custom_bizUnit = json.dumps(_value)
        elif target == 'category':
            queryByLocalSn.custom_category = json.dumps(_value)
        elif target == 'priority':
            queryByLocalSn.custom_priority = _value
        elif target == 'time':
            queryByLocalSn.startTime = sTimeObject
            queryByLocalSn.endTime = eTimeObject
        elif target == 'impact':
            queryByLocalSn.custom_isImpact = _value

        db.session.commit()
        db.session.close()
        db.session.remove()
        print(
            f'[{issuekey}] Done for update JSM {localSn} local db for {target}'
        )
        return 'ok', 200
    except Exception as e:
        print(e)
        print(f'[{issuekey}] Get ERROR when update JSM {localSn} local db')
        return f'[{issuekey}] Get ERROR when update JSM {localSn} local db', 500


@app_mainCowork.route('/jsm/dba/update/worklog', methods=['GET', 'POST'])
def jsmUpdateDbaWorklog():
    # 1 list default option
    front_data = request.get_json(silent=True)
    editor = front_data['editor']
    target = front_data['target']
    issueId = front_data['jsmIssueId']
    issuekey = front_data['jsmIssueKey']
    localSn = front_data['targetJSMSn']
    _value = int(front_data['newValue']) * 60
    mValue = front_data['newValue']
    newComment = f'Update working minutes to {mValue} minutes'
    targetWorkLogId = front_data['targetWorkLogId']
    if targetWorkLogId:
        # 2 Update the JSM worklog and expect return 200
        try:
            url = f'https://ict888.atlassian.net/rest/api/2/issue/{issueId}/worklog/{targetWorkLogId}'
            payload = json.dumps({"timeSpentSeconds": _value})
            defineDone = True
            reTryCounter = 1

            while defineDone:
                response = requests.request("PUT",
                                            url,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 200:
                    print(f'[{issuekey}] Done for update {target} to JSM')
                    defineDone = False
                else:
                    print(
                        f'targetUrl={url}, JSM return status code={response.status_code}, retry - {reTryCounter}'
                    )
                    reTryCounter += 1
                    if reTryCounter > 5:
                        defineDone = False
                    else:
                        time.sleep(2)
        except Exception as e:
            print(e)
            return f'[{issuekey}] - Get error when updating JSM worklog', 500

        if reTryCounter > 5:
            return f'[{issuekey}] - Get unexpected http status code from JSM', 500
    else:
        createWorkLogUrl = f'https://ict888.atlassian.net/rest/api/2/issue/{issueId}/worklog'
        payload = json.dumps({
            "timeSpentSeconds": _value,
            "visibility": {
                "type": "role",
                "value": "Service Desk Team"
            },
            "comment": 'Auto generate by API'
        })

        defineStatus = True
        reTryAddWorkLog = 1
        newWorkLogid = False

        while defineStatus:
            try:
                response = requests.request("POST",
                                            createWorkLogUrl,
                                            headers=prodHeaders,
                                            data=payload)
                if response.status_code == 201:
                    newWorkLogid = response.json()['id']
                    defineStatus = False
                    print(f'[{issuekey}] - Create the Worklog record on JSM')
                else:
                    reTryAddWorkLog += 1
                    print(
                        f'[{issuekey}] - Get unexcept http code {response.status_code}, retry - {reTryAddWorkLog}'
                    )
                    if reTryAddWorkLog > 5:
                        defineStatus = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)
                print(
                    f'[{issuekey}] - Get Exception issue when create the Worklog record on JSM'
                )
                reTryAddWorkLog = 6
                defineStatus = False

        if newWorkLogid:
            # update the jsm dba local db
            searchByLocalSn = get_jsm_dba_prod.query.filter(
                get_jsm_dba_prod.sn == localSn).first()
            searchByLocalSn.custom_workLogId = newWorkLogid
            searchByLocalSn.custom_workLogValue = _value
            print(
                f'[{issuekey}] - Done for update - Add the worklog id and value to local db'
            )
            db.session.commit()
            db.session.close()
            db.session.remove()
        else:
            print(f'[{issuekey}] - Get issue when getting worklog ID')
            return 'bad'

    # 3 - update local comment db
    try:
        addOneRow = get_jsm_dba_comments(issueKey=issuekey,
                                         handler=editor,
                                         content=newComment)
        db.session.add(addOneRow)
        db.session.commit()
        db.session.refresh(addOneRow)
        commentDbSn = addOneRow.sn
        db.session.close()
        print(f'[{issuekey}] Done for update new row to local comment db')
    except Exception as e:
        print(e)
        print(
            f'[{issuekey}] Get ERROR when update new row to local comment db')
        return f'[{issuekey}] Get ERROR when update new row to local comment db', 500
    # 4 - update local db with comments and worklogValue
    try:
        queryByLocalSn = get_jsm_dba_prod.query.filter(
            get_jsm_dba_prod.sn == localSn).first()
        # update comments
        if queryByLocalSn.comments:
            tmpList = json.loads(queryByLocalSn.comments)
            tmpList.append(commentDbSn)
            queryByLocalSn.comments = json.dumps(tmpList)
        else:
            queryByLocalSn.comments = json.dumps([commentDbSn])
        # update worklogValue
        queryByLocalSn.custom_workLogValue = int(_value)

        db.session.commit()
        db.session.close()
        db.session.remove()

        print(
            f'[{issuekey}] Done for update JSM {localSn} local db for {target}'
        )

        return 'ok', 200
    except Exception as e:
        print(e)
        print(f'[{issuekey}] Get ERROR when update JSM {localSn} local db')
        return f'[{issuekey}] Get ERROR when update JSM {localSn} local db', 500


# If the ticket status is 2, user can pull the all data from JSM once, after this action, ticket status will change to 1
# when the ticket status is 2? only when jsm ticket insert by bot (jsm/routine/pull/net)
@app_mainCowork.route('/jsm/pull/net', methods=['GET', 'POST'])
def jsmPullNetPost():
    # 1 - frontend data
    front_data = request.get_json(silent=True)
    dbSn = front_data['LocalSn']
    targetIssueId = front_data['issueId']
    targetIssueKey = front_data['issueKey']
    editor = front_data['editor']
    JiraCloudPlatformURL = f'https://ict888.atlassian.net/rest/api/2/issue/{targetIssueId}?expand=renderedBody'
    # 2 - query JSM API
    defineDone = True
    reTryTime = 1
    try:
        while defineDone:
            response = requests.request("GET",
                                        JiraCloudPlatformURL,
                                        headers=prodHeaders)
            if response.status_code == 200:
                resdict = response.json()['fields']
                defineDone = False
            else:
                print(response.status_code)
                if reTryTime > 5:
                    defineDone = False
                else:
                    reTryTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return 'GET ERROR when query JSM API', 500

    if reTryTime > 5:
        return 'GET UNEXCEPT HTTP STATUS CODE when query JSM API', 500
    else:
        try:  # add new comment
            addOneRow = get_jsm_net_comments(issueKey=targetIssueKey,
                                             handler=editor,
                                             content='Pull JSM data manually')
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn  # get comment sn
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}] -Get Error during update the comment db', 500
        try:  # adjust all option by button
            selectDb = get_jsm_net_prod.query.filter(
                get_jsm_net_prod.sn == dbSn).first()
            selectDb.title = resdict['summary']
            # selectDb.ticketStatus = 1
            if resdict['customfield_10274']:
                tmp_container_list = []
                for i in resdict['customfield_10274']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10274',
                        get_jsm_field_sets_sortOut.contextId == 1,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list.append(queryDb._value)
                selectDb.custom_handler = json.dumps(tmp_container_list)
            if resdict['customfield_10206']:
                tmp_container_list_2 = []
                for i in resdict['customfield_10206']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10206',
                        get_jsm_field_sets_sortOut.contextId == 1,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list_2.append(queryDb._value)
                selectDb.custom_participant = json.dumps(tmp_container_list_2)
            if resdict['customfield_10286']:
                selectDb.custom_category = resdict['customfield_10286'][
                    'value']
            if resdict['customfield_10287']:
                selectDb.custom_facilities = json.dumps(
                    [x['value'] for x in resdict['customfield_10287']])
            if resdict['customfield_10264']:
                selectDb.custom_infra = json.dumps(
                    [x['value'] for x in resdict['customfield_10264']])
            if resdict['customfield_10288']:
                selectDb.custom_vendor = json.dumps(
                    [x['value'] for x in resdict['customfield_10288']])
            if resdict['customfield_10282']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10282'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.startTime = time_obj
            if resdict['customfield_10283']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10283'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.endTime = time_obj

            if selectDb.comments:
                tmpList = json.loads(selectDb.comments)
                tmpList.append(commentDbSn)
                selectDb.comments = json.dumps(tmpList)
            else:
                selectDb.comments = json.dumps([commentDbSn])

            db.session.commit()
            db.session.close()
            db.session.remove()
            return 'ok', 200
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}] -Get Error during update the Net local db', 500


# If the ticket status is 2, user can pull the all data from JSM once, after this action, ticket status will change to 1
# when the ticket status is 2? only when jsm ticket insert by bot (jsm/routine/pull/net)
@app_mainCowork.route('/jsm/pull/sys', methods=['GET', 'POST'])
def jsmPullSysPost():
    # 1 - frontend data
    front_data = request.get_json(silent=True)
    dbSn = front_data['LocalSn']
    targetIssueId = front_data['issueId']
    targetIssueKey = front_data['issueKey']
    editor = front_data['editor']
    JiraCloudPlatformURL = f'https://ict888.atlassian.net/rest/api/2/issue/{targetIssueId}?expand=renderedBody'
    # 2 - query JSM API
    defineDone = True
    reTryTime = 1

    try:
        while defineDone:
            response = requests.request("GET",
                                        JiraCloudPlatformURL,
                                        headers=prodHeaders)
            if response.status_code == 200:
                resdict = response.json()['fields']
                defineDone = False
            else:
                print(response.status_code)
                if reTryTime > 5:
                    defineDone = False
                else:
                    reTryTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return 'GET ERROR when query JSM API', 500

    if reTryTime > 5:
        return 'GET UNEXCEPT HTTP STATUS CODE when query JSM API', 500
    else:
        try:  # add new comment
            addOneRow = get_jsm_sys_comments(issueKey=targetIssueKey,
                                             handler=editor,
                                             content='Pull JSM data manually')
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn  # get comment sn
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}] - Get Error during update the comment db', 500
        try:  # adjust all option by button
            selectDb = get_jsm_sys_prod.query.filter(
                get_jsm_sys_prod.sn == dbSn).first()
            selectDb.title = resdict['summary']
            # selectDb.ticketStatus = 1
            # selectDb.description = resdict['description'] # disable it first, due to hardcode issue
            if resdict['customfield_10274']:
                tmp_container_list = []
                for i in resdict['customfield_10274']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10274',
                        get_jsm_field_sets_sortOut.contextId == 2,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list.append(queryDb._value)
                selectDb.custom_handler = json.dumps(tmp_container_list)
            if resdict['customfield_10206']:
                tmp_container_list_2 = []
                for i in resdict['customfield_10206']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10206',
                        get_jsm_field_sets_sortOut.contextId == 2,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list_2.append(queryDb._value)
                selectDb.custom_participant = json.dumps(tmp_container_list_2)

            if resdict['customfield_10285']:
                selectDb.custom_category = json.dumps(
                    [x['value'] for x in resdict['customfield_10285']])

            if resdict['customfield_10281']:
                selectDb.custom_bizUnit = json.dumps(
                    [x['value'] for x in resdict['customfield_10281']])

            if resdict['priority']:
                selectDb.custom_priority = resdict['priority']['name']

            if resdict['customfield_10282']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10282'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.startTime = time_obj
            if resdict['customfield_10283']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10283'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.endTime = time_obj

            if selectDb.comments:
                tmpList = json.loads(selectDb.comments)
                tmpList.append(commentDbSn)
                selectDb.comments = json.dumps(tmpList)
            else:
                selectDb.comments = json.dumps([commentDbSn])

            db.session.commit()
            db.session.close()
            db.session.remove()
            return 'ok', 200
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}] - Get Error during update the Sys local db', 500


@app_mainCowork.route('/jsm/pull/dba', methods=['GET', 'POST'])
def jsmPullDbaPost():
    # 1 - frontend data
    front_data = request.get_json(silent=True)
    dbSn = front_data['LocalSn']
    targetIssueId = front_data['issueId']
    targetIssueKey = front_data['issueKey']
    editor = front_data['editor']
    JiraCloudPlatformURL = f'https://ict888.atlassian.net/rest/api/2/issue/{targetIssueId}?expand=renderedBody'
    # 2 - query JSM API

    defineDone = True
    reTryTime = 1

    try:
        while defineDone:
            response = requests.request("GET",
                                        JiraCloudPlatformURL,
                                        headers=prodHeaders)
            if response.status_code == 200:
                resdict = response.json()['fields']
                defineDone = False
            else:
                print(response.status_code)
                if reTryTime > 5:
                    defineDone = False
                else:
                    reTryTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return 'GET ERROR when query JSM API', 500

    if reTryTime > 5:
        return 'GET UNEXCEPT HTTP STATUS CODE when query JSM API', 500
    else:
        try:  # add new comment
            addOneRow = get_jsm_dba_comments(issueKey=targetIssueKey,
                                             handler=editor,
                                             content='Pull JSM data manually')
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn  # get comment sn
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}] - Get Error during update the comment db', 500
        try:  # adjust all option by button
            selectDb = get_jsm_dba_prod.query.filter(
                get_jsm_dba_prod.sn == dbSn).first()
            selectDb.title = resdict['summary']
            # selectDb.ticketStatus = 1
            # selectDb.description = resdict['description'] # disable it first, due to hardcode issue

            if resdict['customfield_10274']:
                tmp_container_list = []
                for i in resdict['customfield_10274']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10274',
                        get_jsm_field_sets_sortOut.contextId == 3,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list.append(queryDb._value)
                selectDb.custom_handler = json.dumps(tmp_container_list)
            if resdict['customfield_10206']:
                tmp_container_list_2 = []
                for i in resdict['customfield_10206']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10206',
                        get_jsm_field_sets_sortOut.contextId == 3,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list_2.append(queryDb._value)
                selectDb.custom_participant = json.dumps(tmp_container_list_2)

            if resdict['customfield_10281']:
                selectDb.custom_bizUnit = json.dumps(
                    [x['value'] for x in resdict['customfield_10281']])

            if resdict['customfield_10289']:
                selectDb.custom_category = json.dumps(
                    [x['value'] for x in resdict['customfield_10289']])

            if resdict['priority']:
                selectDb.custom_priority = resdict['priority']['name']

            if resdict['customfield_10244']:
                if resdict['customfield_10244']['value'] == 'No':
                    selectDb.custom_isImpact = 0
                else:
                    selectDb.custom_isImpact = 1

            if resdict['worklog']['total'] != 0:
                selectDb.custom_workLogId = resdict['worklog']['worklogs'][0][
                    'id']
                selectDb.custom_workLogValue = resdict['worklog']['worklogs'][
                    0]['timeSpentSeconds']

            if resdict['customfield_10282']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10282'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.startTime = time_obj

            if resdict['customfield_10283']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10283'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.endTime = time_obj

            if selectDb.comments:
                tmpList = json.loads(selectDb.comments)
                tmpList.append(commentDbSn)
                selectDb.comments = json.dumps(tmpList)
            else:
                selectDb.comments = json.dumps([commentDbSn])

            db.session.commit()
            db.session.close()
            db.session.remove()
            return 'ok', 200
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}] - Get Error during update the dba local db', 500


@app_mainCowork.route('/jsm/pull/ops', methods=['GET', 'POST'])
def jsmPullOpsPost():
    # 1 - frontend data
    front_data = request.get_json(silent=True)
    dbSn = front_data['LocalSn']
    targetIssueId = front_data['issueId']
    targetIssueKey = front_data['issueKey']
    editor = front_data['editor']
    JiraCloudPlatformURL = f'https://ict888.atlassian.net/rest/api/2/issue/{targetIssueId}?expand=renderedBody'
    # 2 - query JSM API

    defineDone = True
    reTryTime = 1

    try:
        while defineDone:
            response = requests.request("GET",
                                        JiraCloudPlatformURL,
                                        headers=prodHeaders)
            if response.status_code == 200:
                resdict = response.json()['fields']
                defineDone = False
            else:
                print(response.status_code)
                if reTryTime > 5:
                    defineDone = False
                else:
                    reTryTime += 1
                    time.sleep(2)
    except Exception as e:
        print(e)
        return f'[{targetIssueKey}][OPS] - GET ERROR when query JSM API', 500

    if reTryTime > 5:
        return f'[{targetIssueKey}][OPS] - GET UNEXCEPT HTTP STATUS CODE when query JSM API', 500
    else:
        try:  # add new comment
            addOneRow = get_jsm_ops_comments(issueKey=targetIssueKey,
                                             handler=editor,
                                             content='Pull JSM data manually')
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn  # get comment sn
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}][OPS] - Get Error during update the comment db', 500
        try:  # adjust all option by button
            selectDb = get_jsm_ops_prod.query.filter(
                get_jsm_ops_prod.sn == dbSn).first()

            selectDb.title = resdict['summary']
            # selectDb.ticketStatus = 1
            # selectDb.description = resdict['description'] # disable it first, due to hardcode issue

            if resdict['customfield_10274']:
                tmp_container_list = []
                for i in resdict['customfield_10274']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10274',
                        get_jsm_field_sets_sortOut.contextId == 4,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list.append(queryDb._value)
                selectDb.custom_handler = json.dumps(tmp_container_list)
            if resdict['customfield_10206']:
                tmp_container_list_2 = []
                for i in resdict['customfield_10206']:
                    queryDb = get_jsm_field_sets_sortOut.query.filter(
                        get_jsm_field_sets_sortOut.fieldId ==
                        'customfield_10206',
                        get_jsm_field_sets_sortOut.contextId == 4,
                        get_jsm_field_sets_sortOut._id ==
                        i['accountId']).first()
                    tmp_container_list_2.append(queryDb._value)
                selectDb.custom_participant = json.dumps(tmp_container_list_2)

            if resdict['customfield_10290']:
                selectDb.custom_category = resdict['customfield_10290'][
                    'value']

            if resdict['customfield_10281']:
                selectDb.custom_bizUnit = json.dumps(
                    [x['value'] for x in resdict['customfield_10281']])

            if resdict['customfield_10264']:
                selectDb.custom_infra = json.dumps(
                    [x['value'] for x in resdict['customfield_10264']])

            if resdict['customfield_10282']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10282'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.startTime = time_obj

            if resdict['customfield_10283']:
                time_obj = datetime.datetime.strptime(
                    resdict['customfield_10283'], "%Y-%m-%dT%H:%M:%S.%f%z")
                selectDb.endTime = time_obj

            if selectDb.comments:
                tmpList = json.loads(selectDb.comments)
                tmpList.append(commentDbSn)
                selectDb.comments = json.dumps(tmpList)
            else:
                selectDb.comments = json.dumps([commentDbSn])

            db.session.commit()
            db.session.close()
            db.session.remove()
            return 'ok', 200
        except Exception as e:
            print(e)
            return f'[{targetIssueKey}][OPS] - Get Error during update the local db', 500


# @app_mainCowork.route('/jsm/query/comments')
@app_mainCowork.route('/jsm/query/comments', methods=['GET', 'POST'])
def jsmQueryHistoryComments():

    returnList = []

    front_data = request.get_json(silent=True)
    whichTeam = front_data['group']

    curTimeObject = datetime.datetime.now()
    curDay = curTimeObject.strftime('%Y-%m-%d')

    try:
        if whichTeam == 'SYS':
            dayResult = get_jsm_sys_comments.query.filter(
                func.DATE(get_jsm_sys_comments.timestamp) == curDay).all()
        elif whichTeam == 'NET':
            dayResult = get_jsm_net_comments.query.filter(
                func.DATE(get_jsm_net_comments.timestamp) == curDay).all()
        elif whichTeam == 'DBA':
            dayResult = get_jsm_dba_comments.query.filter(
                func.DATE(get_jsm_dba_comments.timestamp) == curDay).all()
        elif whichTeam == 'OPS':
            dayResult = get_jsm_ops_comments.query.filter(
                func.DATE(get_jsm_ops_comments.timestamp) == curDay).all()

        if len(dayResult) == 0:
            return jsonify(returnList)
        else:
            for i in dayResult:
                if i.handler != 'Bot':
                    tmpCMapping = {}
                    queryMapping = get_jsm_mapping_prod.query.filter(
                        get_jsm_mapping_prod.issueKey == i.issueKey).first()
                    targetMappingSn = queryMapping.sn
                    if targetMappingSn not in tmpCMapping.keys():
                        # check which team
                        if whichTeam == 'NET':
                            # check the custom_category
                            localResult = get_jsm_net_prod.query.filter(
                                get_jsm_net_prod.mapping ==
                                targetMappingSn).first()
                        elif whichTeam == 'SYS':
                            # check the custom_category
                            localResult = get_jsm_sys_prod.query.filter(
                                get_jsm_sys_prod.mapping ==
                                targetMappingSn).first()
                        elif whichTeam == 'DBA':
                            # check the custom_category
                            localResult = get_jsm_dba_prod.query.filter(
                                get_jsm_dba_prod.mapping ==
                                targetMappingSn).first()
                        elif whichTeam == 'OPS':
                            # check the custom_category
                            localResult = get_jsm_ops_prod.query.filter(
                                get_jsm_ops_prod.mapping ==
                                targetMappingSn).first()

                        if localResult:
                            if localResult.custom_category:
                                if whichTeam == 'SYS':
                                    tmpCMapping.setdefault(
                                        targetMappingSn,
                                        json.loads(
                                            localResult.custom_category))
                                elif whichTeam == 'DBA':
                                    tmpCMapping.setdefault(
                                        targetMappingSn,
                                        json.loads(
                                            localResult.custom_category))
                                elif whichTeam == 'OPS':
                                    tmpCMapping.setdefault(
                                        targetMappingSn,
                                        [localResult.custom_category])
                                elif whichTeam == 'NET':
                                    tmpCMapping.setdefault(
                                        targetMappingSn,
                                        [localResult.custom_category])
                            else:
                                tmpCMapping.setdefault(targetMappingSn, [])
                    tmpDict = {}
                    tmpDict.setdefault('updater', i.handler)
                    tmpDict.setdefault(
                        'ticketNumber',
                        [i.issueKey, f'{i.issueKey} - {localResult.title}'])
                    tmpDict.setdefault(
                        'at', i.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                    tmpDict.setdefault('content', i.content)
                    tmpDict.setdefault('category',
                                       tmpCMapping[targetMappingSn])
                    returnList.append(tmpDict)
            return jsonify(returnList)
    except Exception as e:
        print(e)
        return jsonify(returnList)


@app_mainCowork.route('/otrs/query/dba/<status>')
def otrsqueryDba(status='OPEN'):
    if status == 'OPEN':
        result = get_otrs_dba_ticket.query.filter(
            get_otrs_dba_ticket.status == True).all()
        # returnList = [x.serialize for x in result]

        returnList = []

        for i in result:
            tmpDict = i.serialize
            if len(json.loads(i.comments)) != 0:
                tmpCommentList = []
                # reversed
                for eachComment in reversed(json.loads(i.comments)):
                    queryByCommentsSn = get_otrs_dba_ticket_comments.query.filter(
                        get_otrs_dba_ticket_comments.sn ==
                        eachComment).first()
                    tmpCommentList.append(queryByCommentsSn.serialize)
                tmpDict['comments'] = tmpCommentList
            returnList.append(tmpDict)
        return jsonify(returnList)
    elif status == 'CLOSE':
        return 'do the close table list later'
    else:
        result = get_otrs_dba_ticket.query.filter(
            get_otrs_dba_ticket.sn == status).first()
        tmpDict = result.serialize
        if len(tmpDict['comments']) != 0:
            tmpCommentList = []
            # reversed
            for eachComment in reversed(tmpDict['comments']):
                queryByCommentsSn = get_otrs_dba_ticket_comments.query.filter(
                    get_otrs_dba_ticket_comments.sn == eachComment).first()
                tmpCommentList.append(queryByCommentsSn.serialize)
            tmpDict['comments'] = tmpCommentList
        return jsonify(tmpDict)


@app_mainCowork.route('/otrs/update/comments', methods=['GET', 'POST'])
def otrsUpdateDbaComment():
    # {'editor': 'Stanley.Chen', 'targetSn': 3, 'targetTicketNumber': 92031695, 'comment': 'fasfasfasf'}
    front_data = request.get_json(silent=True)
    editor = front_data['editor']
    localSn = front_data['targetSn']
    ticketNumber = front_data['targetTicketNumber']
    newCommentValue = front_data['comment']

    # add new comment
    try:
        addComment = get_otrs_dba_ticket_comments(ticketNumber=ticketNumber,
                                                  handler=editor,
                                                  content=newCommentValue,
                                                  commentType=1)
        db.session.add(addComment)
        db.session.commit()
        db.session.refresh(addComment)
        newCommentSn = addComment.sn
        db.session.close()
    except Exception as e:
        print(e)
        return 'GET ERROR during add comments record', 500

    # get local db data by sn and assign new value to local db
    try:
        # get local db data
        localDbSet = get_otrs_dba_ticket.query.filter(
            get_otrs_dba_ticket.sn == localSn).first()
        # update the comments
        currentCommentsList = json.loads(localDbSet.comments)
        currentCommentsList.append(newCommentSn)
        localDbSet.comments = json.dumps(currentCommentsList)
        db.session.commit()
        db.session.close()
        db.session.remove()
    except Exception as e:
        print(e)
        return 'GET ERROR during assign new value to local db', 500
    return 'ok'


@app_mainCowork.route('/otrs/query/dba/update', methods=['GET', 'POST'])
def otrsUpdateDba():
    # {'targetSn': 3, 'targetTicketNumber': 92031695, 'target': 'description', 'newValue': 'New OTRS Ticket<br>Update the description', 'editor': 'Stanley.Chen'}
    # {'targetSn': 3, 'targetTicketNumber': 92031695, 'target': 'category', 'newValue': ['DB-Security', 'DB-Decom', 'DB-Config'], 'editor': 'Stanley.Chen'}
    front_data = request.get_json(silent=True)
    localDbSn = front_data['targetSn']
    ticketNumber = front_data['targetTicketNumber']
    target = front_data['target']
    newValue = front_data['newValue']
    editor = front_data['editor']

    # add comments record -
    try:
        if target == 'category':
            newValueString = ', '.join(newValue)
            newCommentValue = f'Assign {target} value as {newValueString}'
        elif target == 'handler':
            newValueString = ', '.join(newValue)
            newCommentValue = f'Assign {target} value as {newValueString}'
        elif target == 'participant':
            newValueString = ', '.join(newValue)
            newCommentValue = f'Assign {target} value as {newValueString}'
        elif target == 'status':
            if newValue:
                newCommentValue = f'Change {target} value to OPEN'
            else:
                newCommentValue = f'Change {target} value to CLOSE'
        else:
            newCommentValue = f'Adjust {target}'
        addComment = get_otrs_dba_ticket_comments(ticketNumber=ticketNumber,
                                                  handler=editor,
                                                  content=newCommentValue,
                                                  commentType=1)
        db.session.add(addComment)
        db.session.commit()
        db.session.refresh(addComment)
        newCommentSn = addComment.sn
        db.session.close()
    except Exception as e:
        print(e)
        return 'GET ERROR during add comments record', 500

    # get local db data by sn and assign new value to local db
    try:
        # get local db data
        localDbSet = get_otrs_dba_ticket.query.filter(
            get_otrs_dba_ticket.sn == localDbSn).first()
        # update the comments
        currentCommentsList = json.loads(localDbSet.comments)
        currentCommentsList.append(newCommentSn)
        localDbSet.comments = json.dumps(currentCommentsList)
        if target == 'description':
            localDbSet.description = newValue
        elif target == 'category':
            localDbSet.custom_category = json.dumps(newValue)
        elif target == 'handler':
            localDbSet.custom_handler = json.dumps(newValue)
        elif target == 'participant':
            localDbSet.custom_participant = json.dumps(newValue)
        elif target == 'status':
            localDbSet.status = newValue
        db.session.commit()
        db.session.close()
        db.session.remove()
    except Exception as e:
        print(e)
        return 'GET ERROR during assign new value to local db', 500

    return 'ok'


@app_mainCowork.route('/change/queue', methods=['GET', 'POST'])
def opsChangeQueue():
    # get data from front-end
    front_data = request.get_json(silent=True)
    editor = front_data['editor']
    newGroup = front_data['newGroup']
    ticketSn = front_data['ticketSn']
    ticketMapping = front_data['ticketMapping']
    ticketIssueId = front_data['ticketIssueId']
    ticketIssueKey = front_data['ticketIssueKey']

    # fixed issue type dict
    issue_type_id = {
        'ops_request': {
            "fields": {
                "issuetype": {
                    "avatarId": 10323,
                    "id": "10125"
                },
                "customfield_10274": None,
                "customfield_10206": None
            }
        },
        'ops_incident': {
            "fields": {
                "issuetype": {
                    "avatarId": 10303,
                    "id": "10126"
                },
                "customfield_10274": None,
                "customfield_10206": None
            }
        },
        'NET': {
            "fields": {
                "issuetype": {
                    "avatarId": 10311,
                    "id": "10129"
                },
                "customfield_10274": None,
                "customfield_10206": None
            }
        },
        'SYS': {
            "fields": {
                "issuetype": {
                    "avatarId": 10309,
                    "id": "10131"
                },
                "customfield_10274": None,
                "customfield_10206": None
            }
        },
        'DBA': {
            "fields": {
                "issuetype": {
                    "avatarId": 10300,
                    "id": "10130"
                },
                "customfield_10274": None,
                "customfield_10206": None
            }
        }
    }

    # [1] -  use the api to change the issueType
    update_issue_type_url = f"https://ict888.atlassian.net/rest/api/2/issue/{ticketIssueKey}"

    payload = json.dumps(issue_type_id[newGroup])

    defineUpdateIssueType = True
    reTryUpdateIssueType = 1
    while defineUpdateIssueType:
        try:
            updateIssueTypeResult = requests.request("PUT",
                                                     update_issue_type_url,
                                                     headers=prodHeaders,
                                                     data=payload)
            if updateIssueTypeResult.status_code == 204:
                print(
                    f'[{ticketIssueId}][ChangeQueueTo{newGroup}][#1] - Use the Jira API to change the issueType - Successful'
                )
                defineUpdateIssueType = False
            else:
                print(
                    f'[{ticketIssueId}][ChangeQueue][#1] - Failed - Get unexpected http status code return {updateIssueTypeResult.status_code}; retry time - {reTryUpdateIssueType}'
                )
                if reTryUpdateIssueType >= 5:
                    defineUpdateIssueType = False
                else:
                    reTryUpdateIssueType += 1
                    time.sleep(2)
        except Exception as e:
            print(f'[{ticketIssueId}][ChangeQueue][#1] - Failed due to - {e}')

    if reTryUpdateIssueType >= 5:
        return 'Failed at #1', 500

    # [2] change the group on mapping db
    try:  #
        current_row_on_mapping_table = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == ticketMapping).first()
        come_from_which_team = current_row_on_mapping_table._group
        if newGroup == 'ops_request':
            current_row_on_mapping_table._group = 'OPS'
        else:
            current_row_on_mapping_table._group = newGroup
        db.session.commit()
        db.session.close()
        print(
            f'[{ticketIssueId}][ChangeQueueTo{newGroup}][#2] - Change the group on mapping db - Successful'
        )
    except Exception as e:
        print(f'[{ticketIssueId}][ChangeQueue][#2] - Failed due to - {e}')
        return 'Failed at #2', 500

    # [3] add new desction db row and one comment
    try:
        # [3-1] - using this dict to add new row on db -
        new_row_dict = {}
        # [3-2] default value -
        new_row_dict.setdefault('description', 'New ticket')
        new_row_dict.setdefault('ticketStatus', 2)
        new_row_dict.setdefault('startTime',
                                datetime.datetime.fromtimestamp(626572800))
        new_row_dict.setdefault('endTime',
                                datetime.datetime.fromtimestamp(626572800))
        new_row_dict.setdefault('mapping', ticketMapping)

        # [3-3] check the request comes from which team ?
        if come_from_which_team == 'NET':
            current_row_on_ticket_mapping_table = get_jsm_net_prod.query.filter(
                get_jsm_net_prod.sn == ticketSn).first()
        elif come_from_which_team == 'SYS':
            current_row_on_ticket_mapping_table = get_jsm_sys_prod.query.filter(
                get_jsm_sys_prod.sn == ticketSn).first()
        elif come_from_which_team == 'OPS':
            current_row_on_ticket_mapping_table = get_jsm_ops_prod.query.filter(
                get_jsm_ops_prod.sn == ticketSn).first()
        elif come_from_which_team == 'DBA':
            current_row_on_ticket_mapping_table = get_jsm_dba_prod.query.filter(
                get_jsm_dba_prod.sn == ticketSn).first()

        # [3-4] copy the value to dict from old row
        new_row_dict.setdefault('title',
                                current_row_on_ticket_mapping_table.title)
        new_row_dict.setdefault('jiraStatus',
                                current_row_on_ticket_mapping_table.jiraStatus)
        new_row_dict.setdefault(
            'createdTime', current_row_on_ticket_mapping_table.createdTime)

        # [3-5] check the new team and custom the field -
        # let this list to create local db directly
        new_row_list = []
        if newGroup == 'NET':
            addOneRow = get_jsm_net_comments(
                issueKey=ticketIssueKey,
                handler=editor,
                content=
                f'{come_from_which_team} - {editor} change this ticket queue to your team ({newGroup})'
            )
            new_row_dict.setdefault('custom_infra', json.dumps([]))
            new_row_dict.setdefault('custom_category', '')
            new_row_dict.setdefault('custom_facilities', json.dumps([]))
            new_row_dict.setdefault('custom_facilities', json.dumps([]))
            new_row_dict.setdefault('custom_handler', json.dumps([]))
            # [3-6] add new comment, and udpate dict
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            new_row_dict.setdefault('comments', json.dumps([commentDbSn]))
            new_row_list.append(new_row_dict)
            for x in new_row_list:
                insertDb = get_jsm_net_prod(**x)
                db.session.add(insertDb)
                db.session.commit()
        elif newGroup == 'SYS':
            addOneRow = get_jsm_sys_comments(
                issueKey=ticketIssueKey,
                handler=editor,
                content=
                f'{come_from_which_team} - {editor} change this ticket queue to your team ({newGroup})'
            )
            new_row_dict.setdefault('custom_bizUnit', json.dumps([]))
            new_row_dict.setdefault('custom_category', json.dumps([]))
            new_row_dict.setdefault('custom_priority', '')
            new_row_dict.setdefault('custom_handler', json.dumps([]))
            # [3-6] add new comment, and udpate dict
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            new_row_dict.setdefault('comments', json.dumps([commentDbSn]))
            new_row_list.append(new_row_dict)
            for x in new_row_list:
                insertDb = get_jsm_sys_prod(**x)
                db.session.add(insertDb)
                db.session.commit()
        elif newGroup == 'ops_request':
            addOneRow = get_jsm_ops_comments(
                issueKey=ticketIssueKey,
                handler=editor,
                content=
                f'{come_from_which_team} - {editor} change this ticket queue to your team (OPS)'
            )
            # [3-6] add new comment, and udpate dict
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            # check if ticket has been changed from OPS
            checker_old_ticket = get_jsm_ops_prod.query.filter(
                get_jsm_ops_prod.mapping == ticketMapping).first()
            if checker_old_ticket:
                # means we can just add the new comment sn and adjust the ticket status
                # - ticket status adjust
                checker_old_ticket.ticketStatus = 1
                # - ticket append comment or add comment
                if checker_old_ticket.comments:
                    tmpList = json.loads(checker_old_ticket.comments)
                    tmpList.append(commentDbSn)
                    checker_old_ticket.comments = json.dumps(tmpList)
                else:
                    checker_old_ticket.comments = json.dumps([commentDbSn])
                db.session.commit()
            else:
                new_row_dict.setdefault('custom_infra', json.dumps([]))
                new_row_dict.setdefault('custom_category', '')
                new_row_dict.setdefault('custom_bizUnit', json.dumps([]))
                new_row_dict.setdefault('custom_handler', json.dumps([]))
                new_row_dict.setdefault('comments', json.dumps([commentDbSn]))
                new_row_list.append(new_row_dict)
                for x in new_row_list:
                    insertDb = get_jsm_ops_prod(**x)
                    db.session.add(insertDb)
                    db.session.commit()
        elif newGroup == 'DBA':
            addOneRow = get_jsm_dba_comments(
                issueKey=ticketIssueKey,
                handler=editor,
                content=
                f'{come_from_which_team} - {editor} change this ticket queue to your team ({newGroup})'
            )
            new_row_dict.setdefault('custom_bizUnit', json.dumps([]))
            new_row_dict.setdefault('custom_category', json.dumps([]))
            new_row_dict.setdefault('custom_handler', json.dumps([]))
            new_row_dict.setdefault('custom_priority', '')
            new_row_dict.setdefault('custom_isImpact', 0)
            # [3-6] add new comment, and udpate dict
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSn = addOneRow.sn
            new_row_dict.setdefault('comments', json.dumps([commentDbSn]))
            new_row_list.append(new_row_dict)
            for x in new_row_list:
                insertDb = get_jsm_dba_prod(**x)
                db.session.add(insertDb)
                db.session.commit()

        print(
            f'[{ticketIssueId}][ChangeQueueTo{newGroup}][#3] - Add new row for new group and comment - Successful'
        )

    except Exception as e:
        print(f'[{ticketIssueId}][ChangeQueue][#3] - Failed due to - {e}')
        return 'Failed at #3', 500

    # [4] addjust source db row ( ticketStatus to 99 ), add the new comment to record the change
    if newGroup != 'ops_request':
        try:
            # add new comment - only OPS
            addOneRow = get_jsm_ops_comments(
                issueKey=ticketIssueKey,
                handler=editor,
                commentType=2,
                content=f'Change this ticket queue to team: ({newGroup})')
            db.session.add(addOneRow)
            db.session.commit()
            db.session.refresh(addOneRow)
            commentDbSnRe = addOneRow.sn

            # adjust source db row
            if current_row_on_ticket_mapping_table.comments:
                tmpList = json.loads(
                    current_row_on_ticket_mapping_table.comments)
                tmpList.append(commentDbSnRe)
                current_row_on_ticket_mapping_table.comments = json.dumps(
                    tmpList)
            else:
                current_row_on_ticket_mapping_table.comments = json.dumps(
                    [commentDbSnRe])
            current_row_on_ticket_mapping_table.ticketStatus = 99
            db.session.commit()
            db.session.close()
            print(
                f'[{ticketIssueId}][ChangeQueueTo{newGroup}][#4] - Adjust old row ticketstatus - Successful'
            )
        except Exception as e:
            print(f'[{ticketIssueId}][ChangeQueue][#4] - Failed due to - {e}')
            return 'Failed at #4', 500

        # skype update the chat to related team.
        # build the message
        returnString = f'Hi <b>{newGroup}</b> \n'
        returnString = returnString + f'New JIRA Ticket <b>{ticketIssueKey}</b> Change to your queue. \n'

        skypeCheck = True
        while skypeCheck:
            try:
                sk = Skype("yt.ops", "QQe*a@a7YE")
                if newGroup == 'SYS':
                    ch = sk.chats["8:yt.sys"]
                elif newGroup == 'NET':
                    ch = sk.chats["8:yt.net"]
                elif newGroup == 'DBA':
                    ch = sk.chats["8:yt.dba"]

                ch.sendMsg(returnString, rich=True)
                print(
                    f'[{ticketIssueId}][ChangeQueueTo{newGroup}][#5] - Send the message to related team - Successful'
                )
                skypeCheck = False
            except Exception as e:
                print(e)
                print('do again after 5 sec')
                time.sleep(5)
    else:
        # other team, just remove the row on the table.
        db.session.delete(current_row_on_ticket_mapping_table)
        db.session.commit()
        db.session.close()

    return 'ok'
