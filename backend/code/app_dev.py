# Default Flask
from flask import Flask, redirect, render_template, jsonify, request, Response, make_response, redirect
# from sqlalchemy.sql.elements import Null
from sqlalchemy import or_, and_

# DB Requirement
from models import db, get_handover_otrs, get_handover_customer_status, get_handover_notes_attachment, get_handover_jira_ticket, get_handover_jira_key_id_mapping, get_handover_jira_ticket_sysinfo, get_handover_kpi_result, get_handover_ticket_mtn_mapping, get_handover_notes, get_handover_user_controller, get_handover_hyperlink_sre_page, get_customer_status_note, get_handover_shift_table, get_jsm_ops_prod, get_jsm_mapping_prod, get_otrs_dba_ticket, get_otrs_dba_ticket_comments, get_jsm_field_sets_sortOut
from config import DevConfig

# DB migrate
from flask_migrate import Migrate, current

# RE
# import re

# CROS
from flask_cors import CORS
import os

# SendEmail
from flask_mail import Mail, Message

# Other
import requests
import json
import time
import datetime
# from requests.auth import HTTPBasicAuth

import random

# html string to jpg
import imgkit

# js fileReader to localData
# import base64
import errno
from shutil import copyfile, copy

# dict
from collections import defaultdict

# ldap
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES

# Skype
from skpy import Skype, SkypeChats

# JSM
import markdownify

# csv
import csv

# bluePrint
from monitoringSystem.monitoringSystem import app_monitoringSystem
from bpNote.mainNote import app_mainNote
from bpOTRS.mainOTRS import app_mainOTRS
from bpEmail.mainEmail import app_mainEmail
from bpQuery.mainQuery import app_mainQuery
from bpCowork.mainCowork import app_mainCowork
from bpCoworkRoutine.mainRoutine import app_mainRoutine

app = Flask(__name__)
app.config.from_object(DevConfig)
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

app.register_blueprint(app_monitoringSystem, url_prefix='/monitoringSystem')
app.register_blueprint(app_mainNote, url_prefix='/bpNote')
app.register_blueprint(app_mainOTRS, url_prefix='/bpOTRS')
app.register_blueprint(app_mainEmail, url_prefix='/bpEmail')
app.register_blueprint(app_mainCowork, url_prefix='/bpCowork')
app.register_blueprint(app_mainRoutine, url_prefix='/bpRoutine')
app.register_blueprint(app_mainQuery, url_prefix='/bpQuery')

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


class customJiraAction():
    headers = {
        'Authorization':
        'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
        'Cookie':
        'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_952072c727f1fa2e7028e7bbd9f60bac9409f559_lin'
    }

    @classmethod
    def AddJiraAttachByIssueId(cls, targetIssueId, editor, targetFileName,
                               targetFileType, date, shift, localDbSn):

        # Update the file to Jira
        url = f"https://anyhow-test4u.atlassian.net/rest/api/2/issue/{targetIssueId}/attachments"
        newHeader = cls.headers
        newHeader['Accept'] = 'application/json'
        newHeader['X-Atlassian-Token'] = "no-check"
        response = requests.request("POST",
                                    url,
                                    headers=newHeader,
                                    files={
                                        "file": (targetFileName,
                                                 open(f'temp.{targetFileType}',
                                                      'rb'), targetFileType)
                                    })

        if response.status_code == 200:
            print(
                f'Need to update the list into local DB sn: {localDbSn}, for fileName - {targetFileName}'
            )

            queryLocalDbBySn = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.sn == localDbSn).first()
            # print(queryLocalDbBySn.serialize)

            if queryLocalDbBySn.attachmentList:
                # if this ticket have the list already, load and insert
                tmpList = json.loads(queryLocalDbBySn.attachmentList)
                if targetFileName in tmpList:
                    print(f'cover file - {targetFileName}')
                else:
                    tmpList.append(
                        dict(name=targetFileName, _type=targetFileType))
                    queryLocalDbBySn.attachmentList = json.dumps(tmpList)

            else:
                # if no comment list on this ticket, creaet the list with this comment ID directly
                queryLocalDbBySn.attachmentList = json.dumps(
                    [dict(name=targetFileName, _type=targetFileType)])

            db.session.commit()

            return dict(status=200, attachmentName=targetFileName)
        else:
            print(f'Get error when upload the attachment - response from JIRA')
            print(response)
            return dict(status=response.status_code,
                        attachmentName=targetFileName)

    @classmethod
    def UpdateJiraCommentByPicture(cls, targetIssueId, editor, targetBody,
                                   date, shift):
        # Only update the attachment on Jira ticket, but comment will not see it.
        options = {"xvfb": ""}
        pictureBody = f'[{editor}] - ' + targetBody
        a = imgkit.from_string(pictureBody, 'out.jpg', options=options)
        while a != True:
            print('wait for create the note picture')
        print('done for create the note picture')

        # start to use the API to post the picture to JIRA
        url = f"https://anyhow-test4u.atlassian.net/rest/api/2/issue/{targetIssueId}/attachments"

        newHeader = cls.headers
        newHeader['Accept'] = 'application/json'
        newHeader['X-Atlassian-Token'] = "no-check"

        response = requests.request("POST",
                                    url,
                                    headers=newHeader,
                                    files={
                                        "file":
                                        (f"{date}-{shift}_by_{editor}.jpg",
                                         open("out.jpg", "rb"), "image/jpeg")
                                    })

        attachmentUpdateResult = response.json()
        print(attachmentUpdateResult)
        print(type(attachmentUpdateResult))
        attachmentURL = attachmentUpdateResult[0]['content']
        attachmentName = attachmentUpdateResult[0]['filename']
        print(f'attachmentURL = {attachmentURL}')
        print(f'attachmentName = {attachmentName}')
        # cls.UpdateJiraComment(targetIssueId, editor, targetBody, attachmentURL,
        #                       attachmentName)
        return 'ok'

    @classmethod
    def UpdateJiraComment(cls, targetIssueId, editor, targetBody):
        # def UpdateJiraComment(cls, targetIssueId, editor, targetBody,
        #                       attachmentURL, attachmentName):
        url = f"https://anyhow-test4u.atlassian.net/rest/api/2/issue/{targetIssueId}/comment"

        newHeader = cls.headers
        newHeader['Accept'] = 'application/json'
        newHeader['Content-Type'] = 'application/json'

        payload = {
            "visibility": {
                "type": "role",
                "value": "Service Desk Team",
            }
        }
        # payload['customColumn'] = 'CreateByDHS'
        payload['body'] = f'[{editor}] - ' + targetBody
        # payload['body'] = f'<span style="font-size: 14px; font-family:"&quot;Roboto&quot;, &quot;-apple-system&quot;, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif">[{editor}] - ' + targetBody + '</span>'
        newpayload = json.dumps(payload)

        response = requests.request("POST",
                                    url,
                                    headers=newHeader,
                                    data=newpayload)

        # print(response.status_code)
        # print(type(response.status_code))
        try:
            if response.status_code == 201:
                # update the comment list on mapping db
                commentListFromDb = get_handover_jira_key_id_mapping.query.filter(
                    get_handover_jira_key_id_mapping._id ==
                    targetIssueId).first()
                # if this ticket have the list already, load and insert
                if commentListFromDb.commentList:
                    tmpList = json.loads(commentListFromDb.commentList)
                    commentIdFromReponse = int(response.json()['id'])
                    tmpList.append(commentIdFromReponse)
                    commentListFromDb.commentList = json.dumps(tmpList)
                else:
                    # if no comment list on this ticket, creaet the list with this comment ID directly
                    commentListFromDb.commentList = json.dumps(
                        [int(response.json()['id'])])
                db.session.commit()
            return response.status_code
        except Exception as e:
            print(f'Get error - {e}')
            return e


def queryCurrentTime():
    result = get_handover_customer_status.query.order_by(
        get_handover_customer_status.sn.desc()).first()
    return_dict = dict(date=result.date.strftime("%Y%m%d"), shift=result.shift)
    return return_dict


@app.route('/handover/main/init')
@app.route('/handover/main/init/<anything>')
def handover_main_init(anything=None):
    if anything:
        # fake_dict = {"date": "2022-03-09", "shift": "A"}
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        return_dict = dict(date=result.date.strftime("%Y-%m-%d"),
                           shift=result.shift)
        # return fake_dict
        return return_dict
    else:
        # fake_dict = {"date": "20220309", "shift": "A"}
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        return_dict = dict(date=result.date.strftime("%Y%m%d"),
                           shift=result.shift)
        # return jsonify(fake_dict)
        return jsonify(return_dict)


@app.route('/query/db/jiraTicket/status/<targetSn>')
def queryDbJiraTicketStatus(targetSn):
    # need to check the last status same with handover system customer status
    result = get_handover_customer_status.query.order_by(
        get_handover_customer_status.sn.desc()).first()
    lastDate = result.date.strftime("%Y%m%d")
    lastShift = result.shift
    ##
    # check the jira ticket undereditor status by targetSN
    checkDb = get_handover_jira_ticket.query.filter(
        get_handover_jira_ticket.sn == targetSn,
        get_handover_jira_ticket.date == lastDate,
        get_handover_jira_ticket.shift == lastShift).first()

    if checkDb:
        if checkDb.flagUnderEdit:
            return_dict = dict(isUnderEdit=True, editor=checkDb.lastEditor)
            r = Response(status=200, response=json.dumps(return_dict))
        else:
            return_dict = dict(isUnderEdit=False, editor=None)
            r = Response(status=200, response=json.dumps(return_dict))
    else:
        # avoid user use the old ticketSN to query, so return the correct ticketSN.
        checkDbOld = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.sn == targetSn).first()

        targetIssueId = checkDbOld.issueId

        newTargetColumn = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.issueId == targetIssueId,
            get_handover_jira_ticket.date == lastDate,
            get_handover_jira_ticket.shift == lastShift).first()

        print(f'newTargetColumn = {newTargetColumn}')

        newTargetSn = newTargetColumn.sn

        return_dict = dict(
            error=f"server can't find this SN on {lastDate}-{lastShift}",
            newTargetSn=newTargetSn)
        r = Response(status=400, response=json.dumps(return_dict))
    r.headers["Content-Type"] = "application/json"
    return r


@app.route('/update/db/jiraTicket/status', methods=['GET', 'POST'])
def updateDbJiraTicketStatus():
    front_data = request.get_json(silent=True)
    action = front_data['action']
    targetTicketSn = front_data['targetTicketSn']
    newEditor = front_data['newEditor']
    if action == 'edit':
        try:
            selectTargetSn = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.sn == targetTicketSn).first()
            selectTargetSn.lastEditor = newEditor
            selectTargetSn.flagUnderEdit = True
            db.session.commit()
            return f'Edit - update the last editor to {newEditor} on ticket - {selectTargetSn.ticketName}'
        except Exception as e:
            return e
    elif action == 'cancel':
        try:
            selectTargetSn = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.sn == targetTicketSn).first()
            curEditor = selectTargetSn.lastEditor
            selectTargetSn.flagUnderEdit = False
            db.session.commit()
            return f'Cancel - change ticket - {selectTargetSn.ticketName} lastEditor is {curEditor}, but change flagUnderEdit to False'
        except Exception as e:
            return e
    elif action == 'delete':
        print(f'delete target is {targetTicketSn}')
        # ticket_jira
        deleteTarget = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.sn == targetTicketSn).first()
        # change the editor / flagUnderEdit
        deleteTarget.lastEditor = newEditor
        deleteTarget.flagUnderEdit = False
        deleteTarget.flagTicketStatus = 3
        # get Jira SN by ticket_jira
        deleteTargetId = deleteTarget.issueId
        db.session.commit()
        db.session.close()
        # jira_key_id_mapping
        deleteMappingTarget = get_handover_jira_key_id_mapping.query.filter(
            get_handover_jira_key_id_mapping._id == deleteTargetId).first()
        deleteMappingTarget.flagClose = True
        db.session.commit()
        db.session.close()

        print(f'deleteTargetId = {deleteTargetId}')

        updateJiraKPIbyApi = sortoutKpiToJira(deleteTargetId, 'updateJira')
        print(f'updateJiraKPIbyApi = {updateJiraKPIbyApi}')

        return_dict = dict(Status='Success',
                           deleteTarget=targetTicketSn,
                           deleteIssueId=deleteTargetId)
        r = Response(status=200, response=json.dumps(return_dict))
        r.headers["Content-Type"] = "application/json"
        return r
    elif action == 'deleteAll':
        curDateShift = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        return_dict = dict(date=curDateShift.date.strftime("%Y%m%d"),
                           shift=curDateShift.shift)
        listAllClosedTickets = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.flagTicketStatus != 3,
            get_handover_jira_ticket.flagJiraTicketStatus == 'Closed',
            get_handover_jira_ticket.date == return_dict['date'],
            get_handover_jira_ticket.shift == return_dict['shift']).all()

        # will for loop the result, and do following action:
        # - update the jira ticket ticket status from 0 to 3
        # - update the jira ticket key & id mapping flagClose 0 to 1
        # - update the kpi result to Jira
        for jiraTicket in listAllClosedTickets:
            print(f'do the loop - {jiraTicket.sn}')
            deleteTargetId = jiraTicket.issueId
            jiraTicket.flagTicketStatus = 3
            jiraTicket.lastEditor = newEditor
            jiraTicket.flagUnderEdit = False
            db.session.commit()

            deleteMappingTarget = get_handover_jira_key_id_mapping.query.filter(
                get_handover_jira_key_id_mapping._id ==
                deleteTargetId).first()
            deleteMappingTarget.flagClose = True
            db.session.commit()
            updateJiraKPIbyApi = sortoutKpiToJira(deleteTargetId, 'updateJira')

        db.session.close()

        print('done for delete all closed ticket')
        return 'Done for all closed tickets delete and update kpi value on Jira'
    elif action == 'update':
        try:
            diffSync = False
            # Get the last shift and date
            curDateShift = get_handover_customer_status.query.order_by(
                get_handover_customer_status.sn.desc()).first()
            return_dict = dict(date=curDateShift.date.strftime("%Y%m%d"),
                               shift=curDateShift.shift)
            # update dhs DB
            selectTargetSn = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.sn == targetTicketSn).first()

            oldFlagTicketStatus = selectTargetSn.flagTicketStatus

            if selectTargetSn.date == return_dict[
                    'date'] and selectTargetSn.shift == return_dict['shift']:
                print('normal update - date & shift is ok')
            else:
                print('abnormal update - date & shift is diff')
                diffSync = True
                oldTicketissueId = selectTargetSn.issueId
                selectTargetSn = get_handover_jira_ticket.query.filter(
                    get_handover_jira_ticket.issueId == oldTicketissueId,
                    get_handover_jira_ticket.date == return_dict['date'],
                    get_handover_jira_ticket.shift ==
                    return_dict['shift']).first()

            defineToJira = False
            # check the ticket status #0>newTicket, 1>oldTicket, 2>pending_Close, 3> close_directly
            if selectTargetSn.flagTicketStatus == 0:
                # print('newTicket')
                toJiraSummary = front_data['summary']
                defineToJira = True
            elif diffSync and oldFlagTicketStatus == 0:
                # new ticket edit and udpate after next shift and hit this
                toJiraSummary = front_data['summary']
                defineToJira = True
            elif selectTargetSn.flagTicketStatus == 1:
                # print('oldTicket')
                if front_data['updateSummary'] != selectTargetSn.updateSummary:
                    print('hit diff')
                    toJiraSummary = front_data['updateSummary']
                    defineToJira = True
                else:
                    print('hit same')
            elif selectTargetSn.flagTicketStatus == 2:
                print('pendingCloseTicket')
            elif selectTargetSn.flagTicketStatus == 3:
                print('closeTicket')
            else:
                print('unknownTicketStatus')

            # update front end data to localDB
            selectTargetSn.lastEditor = front_data['newEditor']
            selectTargetSn.summary = front_data['summary']
            selectTargetSn.updateSummary = front_data['updateSummary']
            selectTargetSn.flagUnderEdit = False
            db.session.commit()

            # check if need to update DB:
            if defineToJira:
                # update jira comment via API
                targetIssueId = selectTargetSn.issueId
                excObject = customJiraAction()
                # normal update the raw data to Jira system
                excObject.UpdateJiraComment(targetIssueId, newEditor,
                                            toJiraSummary)
                # # for create the picture and update to Jira
                # excObject.UpdateJiraCommentByPicture(targetIssueId,
                #                                      newEditor,
                #                                      toJiraSummary,
                #                                      selectTargetSn.date,
                #                                      selectTargetSn.shift)

            if diffSync:
                resultDict = dict(
                    message=f'Update&Reload-Ticket-{selectTargetSn.sn}',
                    effectTargetSn=selectTargetSn.sn)
                r = Response(status=202, response=json.dumps(resultDict))
            else:
                resultDict = dict(
                    message=f'Update&Success-Ticket-{selectTargetSn.sn}',
                    effectTargetSn=selectTargetSn.sn)
                r = Response(status=200, response=json.dumps(resultDict))
            r.headers["Content-Type"] = "application/json"
            return r
        except Exception as e:
            return e


@app.route('/query/all_issues')
@app.route('/query/all_issues/<target>')
def default_index(target=None):
    # get current status from old handover system db
    curDateShift = get_handover_customer_status.query.order_by(
        get_handover_customer_status.sn.desc()).first()
    # return_dict = dict(date='20211104',
    #                    shift='A')
    return_dict = dict(date=curDateShift.date.strftime("%Y%m%d"),
                       shift=curDateShift.shift)

    if target == 'all':
        # return list of dict
        return_sets = []

        # sysinfo
        sysInfo = get_handover_jira_ticket_sysinfo.query.filter(
            get_handover_jira_ticket_sysinfo.date == return_dict['date'],
            get_handover_jira_ticket_sysinfo.shift == return_dict['shift'],
        ).order_by(get_handover_jira_ticket_sysinfo.sn.desc()).first()

        # to get all data with same date / shift / Ticket is open condition
        for i in get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.date == return_dict['date'],
                get_handover_jira_ticket.shift == return_dict['shift'],
                get_handover_jira_ticket.flagTicketStatus != 3).order_by(
                    get_handover_jira_ticket.issueId.desc()):
            # _id & _key & url mapping
            mapping = get_handover_jira_key_id_mapping.query.filter(
                get_handover_jira_key_id_mapping._id == i.issueId).first()

            if i.attachmentList:
                newAttachmentList = json.loads(i.attachmentList)
            else:
                newAttachmentList = []

            # append result
            return_sets.append(
                dict(name=i.ticketName,
                     editorStatus=True,
                     sn=mapping._key,
                     url=mapping.url,
                     issueId=str(mapping._id),
                     ticketSn=i.sn,
                     seq=i.seq,
                     summary=i.summary,
                     updateSummary=i.updateSummary,
                     attachmentList=newAttachmentList,
                     editorBy=i.lastEditor,
                     flagMtn=i.flagMtn,
                     flagUnderEdit=i.flagUnderEdit,
                     flagTicketStatus=i.flagTicketStatus,
                     flagJiraTicketStatus=i.flagJiraTicketStatus,
                     flagKpiSn=i.flagKpiSn,
                     isDisplay=True))

        return_result = dict(sysInfo=sysInfo.serialize if sysInfo else {},
                             jiraList=return_sets,
                             systemTime=return_dict)

        # return render_template('default.html', names=return_name_list, keys=return_key_list)
        return jsonify(return_result)

    elif target == 'jiraTicketStatus':
        sysInfo = get_handover_jira_ticket_sysinfo.query.filter(
            get_handover_jira_ticket_sysinfo.date == return_dict['date'],
            get_handover_jira_ticket_sysinfo.shift == return_dict['shift'],
        ).order_by(get_handover_jira_ticket_sysinfo.sn.desc()).first()
        closedTicketCounter = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.date == return_dict['date'],
            get_handover_jira_ticket.shift == return_dict['shift'],
            get_handover_jira_ticket.flagJiraTicketStatus == 'Closed').all()
        returnDict = sysInfo.serialize
        returnDict['countClosed'] = len(closedTicketCounter)
        return jsonify(returnDict if sysInfo else {})
    elif target == 'jiraTicketList':

        return_sets = []

        for i in get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.date == return_dict['date'],
                get_handover_jira_ticket.shift == return_dict['shift'],
                get_handover_jira_ticket.flagTicketStatus != 3).order_by(
                    get_handover_jira_ticket.issueId.desc()):
            # _id & _key & url mapping
            mapping = get_handover_jira_key_id_mapping.query.filter(
                get_handover_jira_key_id_mapping._id == i.issueId).first()

            if i.attachmentList:
                newAttachmentList = json.loads(i.attachmentList)
            else:
                newAttachmentList = []

            # append result
            return_sets.append(
                dict(name=i.ticketName,
                     editorStatus=True,
                     sn=mapping._key,
                     url=mapping.url,
                     issueId=str(mapping._id),
                     ticketSn=i.sn,
                     seq=i.seq,
                     summary=i.summary,
                     updateSummary=i.updateSummary,
                     attachmentList=newAttachmentList,
                     editorBy=i.lastEditor,
                     flagMtn=i.flagMtn,
                     flagUnderEdit=i.flagUnderEdit,
                     flagTicketStatus=i.flagTicketStatus,
                     flagJiraTicketStatus=i.flagJiraTicketStatus,
                     flagKpiSn=i.flagKpiSn,
                     isDisplay=True))
        # return render_template('default.html', names=return_name_list, keys=return_key_list)
        return jsonify(return_sets)

    # system check the ticket, if already exist DB just ignore elsewise will add it.
    elif target == 'handover':

        # check if need to create
        checkDbStatus = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.date == return_dict['date'],
            get_handover_jira_ticket.shift == return_dict['shift']).all()

        if len(checkDbStatus) == 0:
            try:
                # get last date and shift on local DB
                resultonDb = get_handover_jira_ticket_sysinfo.query.order_by(
                    get_handover_jira_ticket_sysinfo.sn.desc()).first()

                # assign date / shift term.
                newDate = return_dict['date']
                newShift = return_dict['shift']
                oldDate = resultonDb.date
                oldShift = resultonDb.shift
                print(newDate)
                print(newShift)
                print(oldDate)
                print(oldShift)

                # query old ticket data by old date and shift
                resultCurDb = get_handover_jira_ticket.query.filter(
                    get_handover_jira_ticket.date == oldDate,
                    get_handover_jira_ticket.shift == oldShift).order_by(
                        get_handover_jira_ticket.sn).all()

                # new list to store the change
                nextShiftDataList = []

                # forloop for result for DB
                for idx, value in enumerate(resultCurDb):
                    ## check the ticket status start ##
                    # 0>newTicket, 1>oldTicket, 2>pending_Close, 3> close_directly
                    if value.flagTicketStatus == 0:
                        # assign new to old
                        newflagTicketStatus = 1
                        # summary
                        newSummary = value.summary
                        # updateSummary
                        newUpdateSummary = value.updateSummary
                    elif value.flagTicketStatus == 1:
                        # no change
                        newflagTicketStatus = 1
                        # check if the update summary have the value
                        if value.updateSummary:
                            newSummary = value.summary + '<br>' + value.updateSummary
                        else:
                            newSummary = value.summary
                        # rollback to None
                        newUpdateSummary = None
                    elif value.flagTicketStatus == 3:
                        # will not copy to next shift
                        continue

                    ## check the ticket status end ##
                    newDict = dict(
                        date=newDate,
                        shift=newShift,
                        seq=idx + 1,
                        ticketName=value.ticketName,
                        issueId=value.issueId,
                        lastEditor=None,
                        summary=newSummary,
                        updateSummary=newUpdateSummary,
                        attachmentList=json.dumps([]),
                        flagMtn=value.flagMtn,
                        flagUnderEdit=False,
                        flagTicketStatus=newflagTicketStatus,
                        flagJiraTicketStatus=value.flagJiraTicketStatus)
                    nextShiftDataList.append(newDict)

                print(f'nextShiftDataList = {nextShiftDataList}')

                for x in nextShiftDataList:
                    insertDb = get_handover_jira_ticket(**x)
                    db.session.add(insertDb)
                db.session.commit()
                db.session.close()

                # to resolve the sysinfo issue, when user send the handover let DB to the next shift, if sys does not redirect to query the Jira API, then sysinfo will empty more than 5 mins
                # return Response(json.dumps(nextShiftDataList),
                #                 status=201,
                #                 mimetype='application/json')

                return redirect(
                    "https://okta.opsware.xyz:9487/query/all_issues/systemQuery",
                    code=302)

            except Exception as e:
                print(e)
                return Response(e, status=500)
        else:
            curDate = return_dict['date']
            curShift = return_dict['shift']
            return Response(
                f'no need to create next shift data, current data - {curDate} and shift - {curShift} already have the data on localDb',
                status=409)

    elif target == 'systemQuery':
        # query from jira API, only server side to query it
        payload = {}
        # QAT
        # headers = {
        #     'Authorization':
        #     'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
        #     'Cookie':
        #     'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_952072c727f1fa2e7028e7bbd9f60bac9409f559_lin'
        # }
        # UAT
        headers = {
            'Authorization':
            'Basic c3J2Lm9wc0B5aXRtaC5jb206MFdxeFRMeUZySFdzbXRmZE9QZmJGMkJB',
            'Cookie':
            'atlassian.xsrf.token=06ef7867-f85e-4f6f-9b1f-33a446f98474_ea70846200b67d492bc9ac207b4b4e424970df09_lin'
        }

        curTime = datetime.datetime.now()

        checkDbStatus = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.date == return_dict['date'],
            get_handover_jira_ticket.shift == return_dict['shift']).all()

        # print(len(checkDbStatus))
        # if len(checkDbStatus) == 0:
        #     returnResultDict = dict(
        #         frontEnd=dict(status='404', url="https://10.7.6.199/handover"))
        #     return redirect(
        #         "https://okta.opsware.xyz:8082/query/all_issues/handover",
        #         code=302)

        print(f'System start to query Jira API at {curTime}')

        # to get current db issueID list
        curIssueList = [str(x.issueId) for x in checkDbStatus]
        curIssueListFlagisClosed = [
            str(x.issueId) for x in checkDbStatus
            if x.flagJiraTicketStatus == 'Closed'
        ]

        # init the request start 0 and limit 20
        cLimit = 20
        cStart = 0
        url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/20/queue/550/issue?limit={cLimit}&start={cStart}"
        response = requests.request("GET", url, headers=headers, data=payload)
        dict_response = response.json()
        print(f'dict_response = {dict_response}')

        def callbackResponse(target, default_seq):
            for item in target['values']:
                # "fields"."status"."id" and "fields"."status"."name"
                # Open>1,
                # In Progress>3,
                # Under investigation>10015,
                # Resolved>5,
                # Canceled>10004,
                # Completed>10011,
                # Closed>6
                total_list.append(item['id'])
                curIssueId = item['id']
                # print(item['id'], '---', default_seq)
                if int(item['id']) not in ticket_jira_key_id_mapping:
                    insertMappingDb = get_handover_jira_key_id_mapping(
                        _key=item['key'],
                        _id=item['id'],
                        createdAt=curTime,
                        url='https://ict888.atlassian.net/jira/servicedesk/projects/YTS/queues/custom/16/{}'
                        .format(item['key']))
                    db.session.add(insertMappingDb)
                    db.session.commit()
                if item['fields']['status']['id'] == "10015":
                    return_under_investigation_list.append(item['id'])
                    if int(item['id']) not in cur_db_id_result:
                        return_status_change_list.append(
                            dict(issueId=item['id'],
                                 _key=item['key'],
                                 oldStatus="open",
                                 newStatus="Under investigation"))
                        return_new_ticket_list.append(item['id'])
                        insertDb = get_handover_jira_ticket(
                            date=return_dict['date'],
                            shift=return_dict['shift'],
                            seq=default_seq,
                            ticketName=item['fields']['summary'],
                            issueId=item['id'],
                            summary='New ticket',
                            flagJiraTicketStatus=item['fields']['status']
                            ['name'])
                        db.session.add(insertDb)
                        db.session.commit()
                        # only add DB need to +1 seq number
                        default_seq += 1
                if item['fields']['status']['id'] == "3":
                    return_inprocess_list.append(item['id'])
                    if int(item['id']) not in cur_db_id_result:
                        return_status_change_list.append(
                            dict(issueId=item['id'],
                                 _key=item['key'],
                                 oldStatus="open",
                                 newStatus="In Progress"))
                        return_new_ticket_list.append(item['id'])
                        insertDb = get_handover_jira_ticket(
                            date=return_dict['date'],
                            shift=return_dict['shift'],
                            seq=default_seq,
                            ticketName=item['fields']['summary'],
                            issueId=item['id'],
                            summary='New ticket',
                            flagJiraTicketStatus=item['fields']['status']
                            ['name'])
                        db.session.add(insertDb)
                        db.session.commit()
                        # only add DB need to +1 seq number
                        default_seq += 1
                if item['fields']['status']['id'] == "1":
                    return_open_list.append(item['id'])
                if item['fields']['status']['id'] == "10004":
                    return_cancel_list.append(item['id'])
                    # if this ticket not in the db, with in 5 mins, user change the status from in process / under investigation to here
                    # need to add into DB
                    if int(item['id']) not in cur_db_id_result:
                        return_new_ticket_list.append(item['id'])
                        return_status_change_list.append(
                            dict(issueId=item['id'],
                                 _key=item['key'],
                                 oldStatus="Unknown",
                                 newStatus="Canceled"))
                        insertDb = get_handover_jira_ticket(
                            date=return_dict['date'],
                            shift=return_dict['shift'],
                            seq=default_seq,
                            ticketName=item['fields']['summary'],
                            issueId=item['id'],
                            summary='New ticket',
                            flagJiraTicketStatus=item['fields']['status']
                            ['name'])
                        db.session.add(insertDb)
                        db.session.commit()
                        # only add DB need to +1 seq number
                        default_seq += 1
                        print(f'Add {curIssueId} status (Canceled) into DB')
                    else:
                        # it is not the new ticket, so need to change the status, if the status is diff, then update the DB and append to statusChange list
                        target = get_handover_jira_ticket.query.filter(
                            get_handover_jira_ticket.issueId == item['id'],
                            get_handover_jira_ticket.date ==
                            return_dict['date'], get_handover_jira_ticket.shift
                            == return_dict['shift']).first()
                        if target.flagJiraTicketStatus != item['fields'][
                                'status']['name']:
                            return_status_change_list.append(
                                dict(issueId=item['id'],
                                     _key=item['key'],
                                     oldStatus=target.flagJiraTicketStatus,
                                     newStatus="Canceled"))
                            target.flagJiraTicketStatus = 'Canceled'
                            db.session.commit()
                            print(
                                f'Change status (Canceled) for - {curIssueId}')
                if item['fields']['status']['id'] == "10011":
                    # sysinfo append to list
                    return_completed_list.append(item['id'])
                    # if this ticket not in the db, with in 5 mins, user change the status from in process / under investigation to here
                    # need to add into DB
                    if int(item['id']) not in cur_db_id_result:
                        return_new_ticket_list.append(item['id'])
                        return_status_change_list.append(
                            dict(issueId=item['id'],
                                 _key=item['key'],
                                 oldStatus="Unknown",
                                 newStatus="Completed"))
                        insertDb = get_handover_jira_ticket(
                            date=return_dict['date'],
                            shift=return_dict['shift'],
                            seq=default_seq,
                            ticketName=item['fields']['summary'],
                            issueId=item['id'],
                            summary='New ticket',
                            flagJiraTicketStatus=item['fields']['status']
                            ['name'])
                        db.session.add(insertDb)
                        db.session.commit()
                        # only add DB need to +1 seq number
                        default_seq += 1
                        print(f'Add {curIssueId} status (Completed) into DB')
                    else:
                        # it is not the new ticket, so need to change the status, if the status is diff, then update the DB and append to statusChange list
                        target = get_handover_jira_ticket.query.filter(
                            get_handover_jira_ticket.issueId == item['id'],
                            get_handover_jira_ticket.date ==
                            return_dict['date'], get_handover_jira_ticket.shift
                            == return_dict['shift']).first()
                        if target.flagJiraTicketStatus != item['fields'][
                                'status']['name']:
                            return_status_change_list.append(
                                dict(issueId=item['id'],
                                     _key=item['key'],
                                     oldStatus=target.flagJiraTicketStatus,
                                     newStatus="Completed"))
                            target.flagJiraTicketStatus = 'Completed'
                            db.session.commit()
                            print(
                                f'Change status (Completed) for - {curIssueId}'
                            )
                if item['fields']['status']['id'] == "5":
                    # sysinfo append to list
                    return_resolved_list.append(item['id'])
                    # if this ticket not in the db, with in 5 mins, user change the status from in process / under investigation to here
                    # need to add into DB
                    if int(item['id']) not in cur_db_id_result:
                        return_new_ticket_list.append(item['id'])
                        return_status_change_list.append(
                            dict(issueId=item['id'],
                                 _key=item['key'],
                                 oldStatus="Unknown",
                                 newStatus="Resolved"))
                        insertDb = get_handover_jira_ticket(
                            date=return_dict['date'],
                            shift=return_dict['shift'],
                            seq=default_seq,
                            ticketName=item['fields']['summary'],
                            issueId=item['id'],
                            summary='New ticket',
                            flagJiraTicketStatus=item['fields']['status']
                            ['name'])
                        db.session.add(insertDb)
                        db.session.commit()
                        # only add DB need to +1 seq number
                        default_seq += 1
                        print(f'Add {curIssueId} status (Resolved) into DB')
                    else:
                        # it is not the new ticket, so need to change the status, if the status is diff, then update the DB and append to statusChange list
                        target = get_handover_jira_ticket.query.filter(
                            get_handover_jira_ticket.issueId == item['id'],
                            get_handover_jira_ticket.date ==
                            return_dict['date'], get_handover_jira_ticket.shift
                            == return_dict['shift']).first()
                        if target.flagJiraTicketStatus != item['fields'][
                                'status']['name']:
                            return_status_change_list.append(
                                dict(issueId=item['id'],
                                     _key=item['key'],
                                     oldStatus=target.flagJiraTicketStatus,
                                     newStatus="Resolved"))
                            target.flagJiraTicketStatus = 'Resolved'
                            db.session.commit()
                            print(
                                f'Change status (Resolved) for - {curIssueId}')

            db.session.close()

        return_new_ticket_list = []
        return_status_change_list = []
        return_open_list = []
        return_inprocess_list = []
        return_under_investigation_list = []
        return_cancel_list = []
        return_completed_list = []
        return_resolved_list = []
        total_list = []

        # when return json result is not "LAST PAGE", loop it
        while (dict_response['isLastPage'] == False):

            # 1. get ticket db info by cur data and shift then store to list
            cur_db_id_result = []
            cur_db_seq_result = []
            ticket_jira_db_result = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.date == return_dict['date'],
                get_handover_jira_ticket.shift == return_dict['shift']).all()
            for i in ticket_jira_db_result:
                cur_db_id_result.append(i.issueId)
                cur_db_seq_result.append(i.seq)

            # 2. get all key & id mapping, then put in list
            ticket_jira_key_id_mapping = [
                x._id for x in get_handover_jira_key_id_mapping.query.filter(
                    get_handover_jira_key_id_mapping.flagClose == 0).all()
            ]

            # 3. default key for seq ( ticket )
            default_seq = 1 if len(
                cur_db_seq_result) == 0 else max(cur_db_seq_result) + 1

            # for loop jira api result
            callbackResponse(dict_response, default_seq)

            # after call the function need to adjust the queryString
            cStart = cStart + cLimit
            url = f"https://ict888.atlassian.net/rest/servicedeskapi/servicedesk/1/queue/16/issue?limit={cLimit}&start={cStart}"
            # query Jira again
            response = requests.request("GET",
                                        url,
                                        headers=headers,
                                        data=payload)
            # store the while loop condition
            dict_response = response.json()

        # last query result - then call again to save the data into local DB
        # 1. get ticket db info by cur data and shift then store to list
        cur_db_id_result = []
        cur_db_seq_result = []
        ticket_jira_db_result = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.date == return_dict['date'],
            get_handover_jira_ticket.shift == return_dict['shift']).all()
        for i in ticket_jira_db_result:
            cur_db_id_result.append(i.issueId)
            cur_db_seq_result.append(i.seq)

        # 2. get all key & id mapping, then put in list
        ticket_jira_key_id_mapping = [
            x._id for x in get_handover_jira_key_id_mapping.query.filter(
                get_handover_jira_key_id_mapping.flagClose == 0).all()
        ]

        # 3. default key for seq ( ticket )
        default_seq = 1 if len(
            cur_db_seq_result) == 0 else max(cur_db_seq_result) + 1

        callbackResponse(dict_response, default_seq)
        ###

        # create the list to store combine query list result
        compareList = []
        compareList.extend(return_inprocess_list)
        compareList.extend(return_under_investigation_list)
        compareList.extend(return_completed_list)
        compareList.extend(return_cancel_list)
        compareList.extend(return_resolved_list)

        # to see the DB list compare with above list ( localDb issue list compare Jira API result )
        cancelSet = set(curIssueList).difference(compareList)
        # use compareSetCancel list to change the flagJiraTicketStatus to Closed, if only use cancelSet, waste db commit with same status
        compareSetCancel = set(cancelSet).difference(curIssueListFlagisClosed)

        # if cancelSet have the issueIds, means these ticket is closed
        # adjust the JiraTicketStatus column to closed
        for i in compareSetCancel:
            print(f'hit compareSetCancel loop, target is {i}')
            checkDbStatus = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.date == return_dict['date'],
                get_handover_jira_ticket.shift == return_dict['shift'],
                get_handover_jira_ticket.issueId == int(i)).first()
            checkDbStatus.flagJiraTicketStatus = 'Closed'
            db.session.commit()

        returnResultDict = dict(
            frontEnd=dict(
                date=return_dict['date'],
                shift=return_dict['shift'],
                timestamp=curTime,
                listTotal=total_list,
                listOpen=return_open_list,
                listInprocess=return_inprocess_list,
                listUnderInvestigation=return_under_investigation_list,
                listCanceled=return_cancel_list,
                listCompleted=return_completed_list,
                listResolved=return_resolved_list,
                listNew=return_new_ticket_list,
                listStatusChange=return_status_change_list,
                countTotal=len(total_list),
                countOpen=len(return_open_list),
                countInprocess=len(return_inprocess_list),
                countUnderInvestigation=len(return_under_investigation_list),
                countCanceled=len(return_cancel_list),
                countCompleted=len(return_completed_list),
                countResolved=len(return_resolved_list),
                countNew=len(return_new_ticket_list),
                countStatusChange=len(return_status_change_list),
                status='ok'),
            fields=dict(
                date=return_dict['date'],
                shift=return_dict['shift'],
                timestamp=curTime,
                listTotal=json.dumps(total_list),
                listOpen=json.dumps(return_open_list),
                listInprocess=json.dumps(return_inprocess_list),
                listUnderInvestigation=json.dumps(
                    return_under_investigation_list),
                listCanceled=json.dumps(return_cancel_list),
                listCompleted=json.dumps(return_completed_list),
                listResolved=json.dumps(return_resolved_list),
                listNew=json.dumps(return_new_ticket_list),
                listStatusChange=json.dumps(return_status_change_list),
                countTotal=len(total_list),
                countOpen=len(return_open_list),
                countInprocess=len(return_inprocess_list),
                countUnderInvestigation=len(return_under_investigation_list),
                countCanceled=len(return_cancel_list),
                countCompleted=len(return_completed_list),
                countResolved=len(return_resolved_list),
                countNew=len(return_new_ticket_list),
                countStatusChange=len(return_status_change_list)))

        # check if the sysinfo Db exist more than 3 columns
        resultOnDb = get_handover_jira_ticket_sysinfo.query.filter(
            get_handover_jira_ticket_sysinfo.date == return_dict['date'],
            get_handover_jira_ticket_sysinfo.shift ==
            return_dict['shift']).order_by(
                get_handover_jira_ticket_sysinfo.sn).all()

        # if yes, then delete old one
        if len(resultOnDb) > 2:
            db.session.delete(resultOnDb[0])
            db.session.commit()

        # add into sysinfo
        for i in [returnResultDict['fields']]:
            newDbObject = get_handover_jira_ticket_sysinfo(**i)
            db.session.add(newDbObject)

        db.session.commit()
        db.session.close()

        curEndTime = datetime.datetime.now()
        totalCost = curEndTime - curTime
        print(
            f'System finish to query Jira API at {curEndTime}, total cost = {totalCost}'
        )

        return jsonify(returnResultDict['frontEnd'])

    elif target == 'sysinfoQuery':
        resultOnDb = get_handover_jira_ticket_sysinfo.query.filter(
            get_handover_jira_ticket_sysinfo.date == return_dict['date'],
            get_handover_jira_ticket_sysinfo.shift ==
            return_dict['shift']).order_by(
                get_handover_jira_ticket_sysinfo.sn).first()

        compareList = []
        compareList.extend(json.loads(resultOnDb.listCompleted))
        compareList.extend(json.loads(resultOnDb.listCanceled))
        compareList.extend(json.loads(resultOnDb.listResolved))
        print(compareList)
        print(len(compareList))
        return jsonify(resultOnDb.serialize)
    else:
        print(f'target = {target}')
        # get dict by localDB
        return_target = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.date == return_dict['date'],
            get_handover_jira_ticket.shift == return_dict['shift'],
            get_handover_jira_ticket.seq == target).first()

        if return_target.flagTicketStatus != 3:
            # _id & _key & url mapping
            mapping = get_handover_jira_key_id_mapping.query.filter(
                get_handover_jira_key_id_mapping._id ==
                return_target.issueId).first()

            if return_target.attachmentList:
                formatAttachmentList = json.loads(return_target.attachmentList)
            else:
                formatAttachmentList = []

            return_sets = []
            return_sets.append(
                dict(name=return_target.ticketName,
                     editorStatus=False,
                     sn=mapping._key,
                     url=mapping.url,
                     issueId=str(mapping._id),
                     ticketSn=return_target.sn,
                     seq=return_target.seq,
                     summary=return_target.summary,
                     updateSummary=return_target.updateSummary,
                     editorBy=return_target.lastEditor,
                     attachmentList=formatAttachmentList,
                     flagMtn=return_target.flagMtn,
                     flagKpiSn=return_target.flagKpiSn,
                     flagUnderEdit=return_target.flagUnderEdit,
                     flagTicketStatus=return_target.flagTicketStatus,
                     flagJiraTicketStatus=return_target.flagJiraTicketStatus))
            return jsonify(return_sets)
        else:
            return_dict = dict(Status='Target has been removed',
                               deleteTarget=target,
                               deleteIssueId=str(return_target.issueId))
            r = Response(status=202, response=json.dumps(return_dict))
            r.headers["Content-Type"] = "application/json"
            return r


@app.route('/query/jira/issue/<targetIssueId>/<_type>')
def queryJiraIssueDetail(targetIssueId, _type):
    print(f'target ID is {targetIssueId}')

    payload = {}
    headers = {
        'Authorization':
        'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
        'Cookie':
        'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_952072c727f1fa2e7028e7bbd9f60bac9409f559_lin'
    }

    returnSet = []

    if _type == 'comment':
        url = f"https://anyhow-test4u.atlassian.net/rest/api/2/issue/{targetIssueId}/comment?expand=renderedBody"

        response = requests.request("GET", url, headers=headers, data=payload)
        dict_response = response.json()

        keyMapingFromDb = get_handover_jira_key_id_mapping.query.filter(
            get_handover_jira_key_id_mapping._id == targetIssueId).first()

        if keyMapingFromDb.commentList:
            commentList = json.loads(keyMapingFromDb.commentList)
        else:
            commentList = []

        if len(dict_response['comments']) != 0:
            for i in dict_response['comments']:
                # replace the time format
                try:
                    time_obj = datetime.datetime.strptime(
                        i['updated'], "%Y-%m-%dT%H:%M:%S.%f%z")
                    time_obj_without_sec = time_obj.strftime(
                        "%Y-%m-%d %H:%M:%S (%Z)")
                except:
                    time_obj_without_sec = i['updated']
                if int(i['id']) in commentList:
                    returnSet.append(
                        dict(commentBody=i['body'],
                             commentId=i['id'],
                             who=i['author']['displayName'],
                             when=time_obj_without_sec))
                else:
                    # print(i['renderedBody'])
                    # print(i['body'])
                    # Re get img url = r'jira-url=\"https:\/\/anyhow-test4u.atlassian.net\/secure\/thumbnail\/\d*\/image\d*.png\"'
                    returnSet.append(
                        dict(commentBody=i['renderedBody'],
                             commentId=i['id'],
                             who=i['author']['displayName'],
                             when=time_obj_without_sec))
        else:
            print(f'no comments for ticket - {targetIssueId}')
    elif _type == 'attachment':
        url = f"https://anyhow-test4u.atlassian.net/rest/api/2/issue/{targetIssueId}"

        response = requests.request("GET", url, headers=headers, data=payload)
        dict_response = response.json()
        attachment_returnSet = []

        if dict_response['fields']['attachment']:
            for i in dict_response['fields']['attachment']:
                # format the timestamp
                try:
                    time_obj = datetime.datetime.strptime(
                        i['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
                    time_obj_without_sec = time_obj.strftime(
                        "%Y-%m-%d %H:%M:%S (%Z)")
                except:
                    time_obj_without_sec = i['updated']

                attachment_returnSet.append(
                    dict(attchmentBody=i['content'],
                         attchmentId=i['id'],
                         attchmentName=i['filename'],
                         who=i['author']['displayName'],
                         when=time_obj_without_sec,
                         _type=i['mimeType']))

            print('this ticket have the attachments')
            returnSet = sorted(attachment_returnSet, key=lambda x: x['when'])
        else:
            print('this ticket dont have the attachments')

    return jsonify(returnSet)


@app.route('/delete/attachment', methods=['GET', 'POST'])
def deleteLocalAttachment():
    front_data = request.get_json(silent=True)
    localDbSn = front_data['targetTicketSn']
    targetFileName = front_data['targetFileName']

    queryDbBySn = get_handover_jira_ticket.query.filter(
        get_handover_jira_ticket.sn == localDbSn).first()

    newAttachmentList = []

    for i in json.loads(queryDbBySn.attachmentList):
        if targetFileName != i['name']:
            newAttachmentList.append(i)

    queryDbBySn.attachmentList = json.dumps(newAttachmentList)
    db.session.commit()
    return 'ok'


@app.route('/update/jira/attachment', methods=['GET', 'POST'])
def updateJiraAttachment():

    if request.method == 'GET':
        return 'method is not allow'
    else:
        resultList = []
        returnError = []
        errorCode = ''

        # Get the data and shift from old DHS db
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()

        lastDate = result.date.strftime("%Y%m%d")
        lastShift = result.shift

        updater = request.headers.get('updater')
        localDbSn = request.headers.get('localDbSn')
        issueId = request.headers.get('issueId')

        # due to frontEnd Change the q-uploader method to batch, so only one connection
        for i in request.files:
            fileName = i
            fileType = request.files.get(fileName).content_type

            if fileType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                _type = 'docx'
            elif fileType == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                _type = 'xlsx'
            elif fileType == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                _type = 'pptx'
            elif fileType == 'text/plain':
                _type = 'txt'
            elif fileType == 'image/jpeg':
                _type = 'jpg'
            elif fileType == 'application/pdf':
                _type = 'pdf'
            elif fileType == 'application/vnd.ms-excel':
                _type = 'csv'
            elif fileType == 'application/octet-stream':
                _type = 'rar'
            elif fileType == 'application/x-zip-compressed':
                _type = 'zip'
            else:
                _type = 'png'

            fileDateShift = f'static/attachment/{lastDate}/{lastShift}/{issueId}/{fileName}'
            if not os.path.exists(os.path.dirname(fileDateShift)):
                try:
                    os.makedirs(os.path.dirname(fileDateShift))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            print(f'fileDateShift = {fileDateShift}')

            f = request.files.get(fileName)
            f.save(f'temp.{_type}')  # save local

            # copy local file to related
            copy(f'temp.{_type}', fileDateShift)

            # execute the class and Add Jira attachment by class static function
            exObject = customJiraAction()
            jiraAPIResult = exObject.AddJiraAttachByIssueId(
                issueId, updater, fileName, _type, lastDate, lastShift,
                localDbSn)

            resultList.append(jiraAPIResult)

        for ii in resultList:
            print(ii['status'])
            if ii['status'] != 200:
                returnError.append(ii['attachmentName'])
                errorCode = ii['status']

        if len(returnError) != 0:
            r = Response(response=returnError, status=errorCode)
        else:
            r = Response(response='file upload success', status=200)

        r.headers['Content-Type'] = 'application/json'

        return r


@app.route('/update/jira/comment')
@app.route('/update/jira/comment/<targetIssueId>')
def updateJiraCommentIssueId(targetIssueId=10125):
    url = f"https://anyhow-test4u.atlassian.net/rest/api/2/issue/{targetIssueId}/comment"

    headers = {
        'Accept':
        'application/json',
        'Content-Type':
        'application/json',
        'Authorization':
        'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
        'Cookie':
        'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_a855bf791bbb9404c3dec5668a6a31301406f599_lin'
    }

    payload = json.dumps({
        "visibility": {
            "type": "role",
            "value": "Administrators"
        },
        "body": "Gary test by API"
    })

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return 'ok'


@app.route('/query/issuedetail')
def queryIssueDetail():
    url = "https://anyhow-test4u.atlassian.net/rest/api/2/issue/10104"

    payload = {}
    headers = {
        'Authorization':
        'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
        'Cookie':
        'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_952072c727f1fa2e7028e7bbd9f60bac9409f559_lin'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    dict_response = response.json()
    return jsonify(dict_response)
    # return jsonify(dict_response['fields']['description'])


# review purpose
@app.route('/document/<_type>/<localDbSn>/<fileName>')
def documentReturn(_type, localDbSn, fileName):
    # print(_type)
    if _type == 'png' or _type == 'jpg':
        queryDbBySn = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.sn == localDbSn).first()
        target = f'attachment/{queryDbBySn.date}/{queryDbBySn.shift}/{queryDbBySn.issueId}/{fileName}'
    else:
        if _type == 'pptx':
            target = f'example/ppt.png'
        elif _type == 'docx':
            target = f'example/word.png'
        elif _type == 'xlsx':
            target = f'example/excel.png'
        elif _type == 'txt':
            target = f'example/txt.png'
        elif _type == 'pdf':
            target = f'example/pdf.png'
        else:
            target = f'example/sample.png'
    return app.send_static_file(target)


# get file
@app.route('/view/document/<localDbSn>/<fileName>')
def viewDocumentReturn(localDbSn, fileName):
    queryDbBySn = get_handover_jira_ticket.query.filter(
        get_handover_jira_ticket.sn == localDbSn).first()
    target = f'attachment/{queryDbBySn.date}/{queryDbBySn.shift}/{queryDbBySn.issueId}/{fileName}'
    return app.send_static_file(target)


### KPI Part ###
# see the kpi detail by KpiSn
@app.route('/kpi/view/<targetKpiSn>')
def kpi_view_targetKpiSN(targetKpiSn):
    result = get_handover_kpi_result.query.filter(
        get_handover_kpi_result.sn == targetKpiSn).first()
    return jsonify(result.serialize)


# search the kpi detail by jiraIssueId
@app.route('/kpi/jira/<issueId>')
def kpi_jira_issueId(issueId):
    resultByissueId = get_handover_jira_ticket.query.filter(
        get_handover_jira_ticket.issueId == issueId,
        get_handover_jira_ticket.flagKpiSn != None).all()

    containerKpi = [i.flagKpiSn for i in resultByissueId]

    containerResult = []

    for x in containerKpi:
        resultByKpi = get_handover_kpi_result.query.filter(
            get_handover_kpi_result.sn == x).first()
        containerResult.append(resultByKpi.serialize)

    return jsonify(containerResult)


# search the kpi detail by OTRS ticket number
@app.route('/kpi/ticket/<ticketNumber>')
def kpiOTRSTicketNumber(ticketNumber):
    resultByissueId = get_handover_kpi_result.query.filter(
        get_handover_kpi_result.origin_source_subject == ticketNumber).all()

    containerResult = []

    for x in resultByissueId:
        containerResult.append(x.serialize)

    return jsonify(containerResult)


# search the note kpi detail by related_group
@app.route('/kpi/note/<related_group>')
def kpi_note_related_group(related_group):
    resultByRelatedGroup = get_handover_kpi_result.query.filter(
        get_handover_kpi_result.related_group == related_group).all()

    containerResult = []

    for x in resultByRelatedGroup:
        containerResult.append(x.serialize)

    return jsonify(containerResult)


# sortOut the note kpi detail by related_group
@app.route('/kpi/noteSortOut/<related_group>')
def kpi_noteSortOut_related_group(related_group):
    resultByRelatedGroup = get_handover_kpi_result.query.filter(
        get_handover_kpi_result.related_group == related_group).all()

    # setup the set - for store the result, why i use the Set, due to want to name exist set with unique
    requestHandlerSet = set()
    troubleshootingHandlerSet = set()
    troubleshootingHandlerDeputySet = set()
    troubleshootingParticipantsSet = set()
    # check if the type include 3 or 2 or 1
    kpiTypeList = []
    # KPI type level
    incidentLevel = ('Regular Operation', 'Troubleshooting',
                     'Advanced Troubleshooting')

    for y in resultByRelatedGroup:
        kpiTypeList.append(y.type)
        if y.type == '1':
            tmpHandlerList = y.handler.split(',')
            for z in tmpHandlerList:
                requestHandlerSet.add(z)
        else:
            tmpHandlerList = y.handler.split(',')
            for z in tmpHandlerList:
                troubleshootingHandlerSet.add(z)

            if y.handler_second:
                tmpHandlerDeputyList = json.loads(y.handler_second)
                for z in tmpHandlerDeputyList:
                    troubleshootingHandlerDeputySet.add(z)

            if y.participant:
                tmpParticipantsList = json.loads(y.participant)
                for z in tmpParticipantsList:
                    troubleshootingParticipantsSet.add(z)

            if y.type == '3':
                incidentType = incidentLevel[1]

    # check if the type include 3 or 2 or 1
    if '3' in kpiTypeList:
        incidentType = incidentLevel[2]
    elif '2' in kpiTypeList:
        incidentType = incidentLevel[1]
    elif '1' in kpiTypeList:
        incidentType = incidentLevel[0]
    else:
        incidentType = None

    # print('Request Handler - customfield_10075')
    requestHandlerSetWithJsonHeader = [{'value': i} for i in requestHandlerSet]
    # print('Handler(Deputy - customfield_10079')
    troubleshootingHandlerSetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingHandlerSet]
    # print('Participant(s) - customfield_10076')
    troubleshootingHandlerDeputySetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingHandlerDeputySet]
    # print('Troubleshooting Handler - customfield_10077')
    troubleshootingParticipantsSetSetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingParticipantsSet]

    putPayLoadDict = {
        'fields': {
            'handler': requestHandlerSetWithJsonHeader,
            'tsHandler': troubleshootingHandlerSetWithJsonHeader,
            'tsHandlerD': troubleshootingHandlerDeputySetWithJsonHeader,
            'tsParticipant': troubleshootingParticipantsSetSetWithJsonHeader,
            'kpiType': {
                'value': None
            }
        }
    }

    if incidentType == 'Regular Operation':
        putPayLoadDict['fields']['kpiType'] = {"value": "Regular Operation"}
    elif incidentType == 'Troubleshooting':
        putPayLoadDict['fields']['kpiType'] = {"value": "Troubleshooting"}
    elif incidentType == 'Advanced Troubleshooting':
        putPayLoadDict['fields']['kpiType'] = {
            "value": "Advanced Troubleshooting"
        }

    return jsonify(putPayLoadDict)


@app.route('/update/db/kpi/status', methods=['GET', 'POST'])
def update_db_kpi_status():
    front_data = request.get_json(silent=True)
    newDateFormat = front_data['targetDate'][:4] + '-' + front_data[
        'targetDate'][4:][:2] + '-' + front_data['targetDate'][4:][2:]
    # flow: frontend ( JiraTicketListKpi ) update by axios,
    # 0, check the dataSource
    # 1, check if the KPI result has been saved on originJiraTicketSn
    # 1 true: clear all data on DB, and update again in same kpi sn, and update JiraTicket columns (kpiSn)
    # 1 false: insert new data to kpi db and update JiraTicket DB (kpiSn)
    dataSource = front_data['dataSource']
    if dataSource == 'Note':
        requestType = front_data['_type']
        targetKpiSn = front_data['targetKpiSn']
        originSourceSn = front_data['originSourceSn']
        if requestType == 'reset':
            # delete kpi result
            try:
                returnDict = {'kpisn': 0}
                resultByKpiSn = get_handover_kpi_result.query.filter(
                    get_handover_kpi_result.sn == targetKpiSn).first()
                returnDict['kpiGroup'] = resultByKpiSn.related_group
                db.session.delete(resultByKpiSn)
                db.session.commit()
                db.session.close()
            except Exception as e:
                print(e)
                return f'get issue - {e}'
            return returnDict
        elif requestType == 'update':
            targetKpiGroup = front_data['targetKpiGroup']
            kpiType = front_data['type']
            # will use insertList to for loop and insert db
            insertList = []
            # will use inserdict to update kpi db
            insertdict = {}
            insertdict['type'] = kpiType
            insertdict['origin_source'] = dataSource
            insertdict['related_sn'] = originSourceSn
            # to get subject
            querySubjectByNoteSn = get_handover_notes.query.filter(
                get_handover_notes.sn == originSourceSn).first()
            insertdict['origin_source_subject'] = querySubjectByNoteSn.customer
            # update the insertdict based on kpitype
            if kpiType == '1':
                insertdict['handler'] = ','.join(front_data['handler'])
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']
            elif kpiType == '2':
                print('hit kpi type 2')
                if 'handlerSecond' in front_data.keys():
                    insertdict['handler_second'] = json.dumps(
                        front_data['handlerSecond'])
                if 'participant' in front_data.keys():
                    insertdict['participant'] = json.dumps(
                        front_data['participant'])
                if isinstance(front_data['handler'], list):
                    insertdict['handler'] = ','.join(front_data['handler'])
                else:
                    insertdict['handler'] = front_data['handler']
                insertdict['resolve_status'] = front_data['isSolved']
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']
            elif kpiType == '3':
                print('hit kpi type 3')
                if 'handlerSecond' in front_data.keys():
                    insertdict['handler_second'] = json.dumps(
                        front_data['handlerSecond'])
                if 'participant' in front_data.keys():
                    insertdict['participant'] = json.dumps(
                        front_data['participant'])
                if 'description' in front_data.keys():
                    insertdict['description'] = front_data['description']
                if isinstance(front_data['handler'], list):
                    insertdict['handler'] = ','.join(front_data['handler'])
                else:
                    insertdict['handler'] = front_data['handler']
                insertdict['file_path'] = front_data['filePath']
                insertdict['resolve_status'] = front_data['isSolved']
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']

            if (targetKpiGroup is None) and (targetKpiSn == 0):
                print('hit new kpi and new kpi group')
                # query current max kpi group number and plus 1
                maxGroupNumberOnKpi = get_handover_kpi_result.query.order_by(
                    get_handover_kpi_result.related_group.desc()).first()
                nextGroupNumber = maxGroupNumberOnKpi.related_group + 1
                # update kpi group number to note db
                queryNoteBySn = get_handover_notes.query.filter(
                    get_handover_notes.sn == originSourceSn).first()
                queryNoteBySn.kpi_group = nextGroupNumber
                db.session.commit()
                db.session.close()
                # loop insertdict to kpi db with new kpi group
                insertdict['related_group'] = nextGroupNumber
                insertList.append(insertdict)
                for x in insertList:
                    insertObject = get_handover_kpi_result(**x)
                    db.session.add(insertObject)
                db.session.commit()
                # get new KPI sn by shift & date & related_sn
                resultKpi = get_handover_kpi_result.query.filter(
                    get_handover_kpi_result.related_date == newDateFormat,
                    get_handover_kpi_result.related_shift ==
                    front_data['targetShift'],
                    get_handover_kpi_result.related_sn ==
                    originSourceSn).first()
                returnDict = {
                    'kpisn': resultKpi.sn,
                    'kpiGroup': resultKpi.related_group
                }
                return returnDict
            elif (targetKpiGroup) and (targetKpiSn == 0):
                print(
                    'hit new kpi but this note has kpi result on previous shift'
                )
                # update the kpi group
                insertdict['related_group'] = targetKpiGroup
                # update data into KPI data
                insertList.append(insertdict)
                for x in insertList:
                    insertObject = get_handover_kpi_result(**x)
                    db.session.add(insertObject)
                db.session.commit()
                # get new KPI sn by shift & date & related_sn
                resultKpi = get_handover_kpi_result.query.filter(
                    get_handover_kpi_result.related_date == newDateFormat,
                    get_handover_kpi_result.related_shift ==
                    front_data['targetShift'],
                    get_handover_kpi_result.related_sn ==
                    originSourceSn).first()
                returnDict = {
                    'kpisn': resultKpi.sn,
                    'kpiGroup': resultKpi.related_group
                }
            else:
                print('hit kpi has data, need to adjust the data')
                # query db kpi result by sn
                resultBykpiSn = get_handover_kpi_result.query.filter(
                    get_handover_kpi_result.sn == targetKpiSn).first()
                returnDict = {
                    'kpisn': resultBykpiSn.sn,
                    'kpiGroup': resultBykpiSn.related_group
                }
                # check the kpi type
                if resultBykpiSn.type == kpiType:
                    print('front end kpi type is same with db kpi type')
                    for key, value in insertdict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn == targetKpiSn).update(
                                {key: value})
                        db.session.commit()
                    db.session.close()
                else:
                    print('diff type')
                    rollbackDict = dict(resolve_status=False,
                                        handler_second=None,
                                        participant=None,
                                        description=None,
                                        file_path=None)
                    print(f'rollbackDict = {rollbackDict}')
                    # reset the value
                    for rollbackKey, rollbackValue in rollbackDict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn == targetKpiSn).update(
                                {rollbackKey: rollbackValue})
                    db.session.commit()

                    # assign the value
                    for key, value in insertdict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn == targetKpiSn).update(
                                {key: value})
                    db.session.commit()
            return returnDict
    elif dataSource == 'Jira':
        requestType = front_data['_type']
        originJiraTicketSn = front_data['originSourceSn']
        print(f'originJiraTicketSn = {originJiraTicketSn}')
        if requestType == 'reset':
            resultQueryBySn = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.sn == originJiraTicketSn).first()
            storeFlagKpiSn = resultQueryBySn.flagKpiSn
            resultQueryBySn.flagKpiSn = None
            db.session.commit()
            db.session.close()
            if storeFlagKpiSn:
                resultBykpiSn = get_handover_kpi_result.query.filter(
                    get_handover_kpi_result.sn == storeFlagKpiSn).first()
                db.session.delete(resultBykpiSn)
                db.session.commit()
                db.session.close()
                return 'reset done'
            else:
                return 'Db data empty, no need to reset'
        elif requestType == 'update':
            resultQueryBySn = get_handover_jira_ticket.query.filter(
                get_handover_jira_ticket.sn == originJiraTicketSn).first()
            kpiType = front_data['type']
            insertList = []
            insertdict = {}
            insertdict['type'] = kpiType
            insertdict['origin_source'] = dataSource
            insertdict['origin_source_subject'] = resultQueryBySn.ticketName
            insertdict['related_sn'] = originJiraTicketSn
            if kpiType == '1':
                insertdict['handler'] = ','.join(front_data['handler'])
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']
            elif kpiType == '2':
                # handler create是list, renew是string
                if 'handlerSecond' in front_data.keys():
                    insertdict['handler_second'] = json.dumps(
                        front_data['handlerSecond'])
                if 'participant' in front_data.keys():
                    insertdict['participant'] = json.dumps(
                        front_data['participant'])
                if isinstance(front_data['handler'], list):
                    insertdict['handler'] = ','.join(front_data['handler'])
                else:
                    insertdict['handler'] = front_data['handler']
                insertdict['resolve_status'] = front_data['isSolved']
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']
            elif kpiType == '3':
                print(type(front_data['handler']))
                if 'handlerSecond' in front_data.keys():
                    insertdict['handler_second'] = json.dumps(
                        front_data['handlerSecond'])
                if 'participant' in front_data.keys():
                    insertdict['participant'] = json.dumps(
                        front_data['participant'])
                if 'description' in front_data.keys():
                    insertdict['description'] = front_data['description']
                if isinstance(front_data['handler'], list):
                    insertdict['handler'] = ','.join(front_data['handler'])
                else:
                    insertdict['handler'] = front_data['handler']
                insertdict['file_path'] = front_data['filePath']
                insertdict['resolve_status'] = front_data['isSolved']
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']

            print(insertdict.items())

            # check if flagKpiSn exist
            if resultQueryBySn.flagKpiSn:
                returnKpiSn = resultQueryBySn.flagKpiSn
                # get the KPI data by KpiSn, reset the value
                resultBykpiSn = get_handover_kpi_result.query.filter(
                    get_handover_kpi_result.sn ==
                    resultQueryBySn.flagKpiSn).first()
                # when type is same
                if resultBykpiSn.type == kpiType:
                    print('type is same')
                    for key, value in insertdict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn ==
                            resultQueryBySn.flagKpiSn).update({key: value})
                        db.session.commit()
                else:
                    print('type is diff')
                    rollbackDict = dict(resolve_status=False,
                                        handler_second=None,
                                        participant=None,
                                        description=None,
                                        file_path=None)
                    print(f'rollbackDict = {rollbackDict}')
                    # reset the value
                    for rollbackKey, rollbackValue in rollbackDict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn ==
                            resultQueryBySn.flagKpiSn).update(
                                {rollbackKey: rollbackValue})
                    db.session.commit()

                    # assign the value
                    for key, value in insertdict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn ==
                            resultQueryBySn.flagKpiSn).update({key: value})
                    db.session.commit()
            else:
                # update data into KPI data
                insertList.append(insertdict)
                for x in insertList:
                    insertObject = get_handover_kpi_result(**x)
                    db.session.add(insertObject)
                db.session.commit()
                # db.session.close()
                # get new KPI sn by shift & date & related_sn
                resultKpi = get_handover_kpi_result.query.filter(
                    get_handover_kpi_result.related_date == newDateFormat,
                    get_handover_kpi_result.related_shift ==
                    front_data['targetShift'],
                    get_handover_kpi_result.related_sn ==
                    originJiraTicketSn).first()
                newKpiSn = resultKpi.sn
                returnKpiSn = resultKpi.sn
                # save into JiraTicketSn
                resultQueryBySn.flagKpiSn = newKpiSn
                db.session.commit()
                db.session.close()
        return str(returnKpiSn)
    elif dataSource == 'Ticket':
        requestType = front_data['_type']
        originOTRSTicketSn = front_data['originSourceSn']
        targetKpiSn = front_data['targetKpiSn']
        if requestType == 'reset':
            # check if sn exist DB
            resultBykpiSn = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn == targetKpiSn).first()
            if resultBykpiSn:
                print(f'remove row {targetKpiSn} on kpi_result table')
                db.session.delete(resultBykpiSn)
                db.session.commit()
                db.session.close()
                db.session.remove()
                return '0'
            else:
                print(
                    'this ticket does not have kpi record on kpi_result table')
                return '0'
        elif requestType == 'update':
            kpiType = front_data['type']
            ticketNumber = front_data['originSourceSubject']
            insertList = []
            insertdict = {}
            insertdict['type'] = kpiType
            insertdict['origin_source'] = dataSource
            insertdict['origin_source_subject'] = ticketNumber
            insertdict['related_sn'] = originOTRSTicketSn
            if kpiType == '1':
                insertdict['handler'] = ','.join(front_data['handler'])
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']
            elif kpiType == '2':
                # handler create是list, renew是string
                if 'handlerSecond' in front_data.keys():
                    insertdict['handler_second'] = json.dumps(
                        front_data['handlerSecond'])
                if 'participant' in front_data.keys():
                    insertdict['participant'] = json.dumps(
                        front_data['participant'])
                if isinstance(front_data['handler'], list):
                    insertdict['handler'] = ','.join(front_data['handler'])
                else:
                    insertdict['handler'] = front_data['handler']
                insertdict['resolve_status'] = front_data['isSolved']
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']
            elif kpiType == '3':
                print(type(front_data['handler']))
                if 'handlerSecond' in front_data.keys():
                    insertdict['handler_second'] = json.dumps(
                        front_data['handlerSecond'])
                if 'participant' in front_data.keys():
                    insertdict['participant'] = json.dumps(
                        front_data['participant'])
                if 'description' in front_data.keys():
                    insertdict['description'] = front_data['description']
                if isinstance(front_data['handler'], list):
                    insertdict['handler'] = ','.join(front_data['handler'])
                else:
                    insertdict['handler'] = front_data['handler']
                insertdict['file_path'] = front_data['filePath']
                insertdict['resolve_status'] = front_data['isSolved']
                insertdict['related_date'] = newDateFormat
                insertdict['related_shift'] = front_data['targetShift']

            print(insertdict.items())

            queryResultonKpiTable = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.origin_source == 'Ticket',
                get_handover_kpi_result.origin_source_subject == ticketNumber,
                get_handover_kpi_result.related_sn ==
                originOTRSTicketSn).first()

            # check if this ticket has kpi record
            if queryResultonKpiTable:
                # get DB kpi record type
                dbKpiType = queryResultonKpiTable.type
                targetSn = queryResultonKpiTable.sn
                # when type is same
                if dbKpiType == kpiType:
                    print('type is same')
                    for key, value in insertdict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn == targetSn).update(
                                {key: value})
                        db.session.commit()
                else:
                    print('type is diff')
                    rollbackDict = dict(resolve_status=False,
                                        handler_second=None,
                                        participant=None,
                                        description=None,
                                        file_path=None)
                    print(f'rollbackDict = {rollbackDict}')
                    # reset the value
                    for rollbackKey, rollbackValue in rollbackDict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn == targetSn).update(
                                {rollbackKey: rollbackValue})
                    db.session.commit()

                    # assign the value
                    for key, value in insertdict.items():
                        get_handover_kpi_result.query.filter(
                            get_handover_kpi_result.sn == targetSn).update(
                                {key: value})
                    db.session.commit()
            else:
                # update data into KPI data
                insertList.append(insertdict)
                for x in insertList:
                    insertObject = get_handover_kpi_result(**x)
                    db.session.add(insertObject)
                db.session.commit()

            # get new KPI sn by shift & date & related_sn
            resultKpi = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.origin_source == 'Ticket',
                get_handover_kpi_result.origin_source_subject == ticketNumber,
                get_handover_kpi_result.related_sn ==
                originOTRSTicketSn).first()
            returnKpiSn = resultKpi.sn
            db.session.close()
            db.session.remove()
            return str(returnKpiSn)
            # return 'do it later'
    # return 'ok'


@app.route('/update/db/kpi/filePath', methods=['GET', 'POST'])
def updateDbKpiFilePath():
    if request.method == 'GET':
        return 'method is not allow'
    else:
        # check which zone submit this post ( jiraTicket or Note )
        zoneSource = request.headers.get('zone')
        print(f'zoneSource = {zoneSource}')
        dbSn = request.headers.get('dbSn')
        print(f'dbSn = {dbSn}')

        for i in request.files:
            fileName = i
            fileType = request.files.get(fileName).content_type

            if fileType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                _type = 'docx'
            elif fileType == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                _type = 'xlsx'
            elif fileType == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                _type = 'pptx'
            elif fileType == 'text/plain':
                _type = 'txt'
            elif fileType == 'image/jpeg':
                _type = 'jpg'
            elif fileType == 'application/pdf':
                _type = 'pdf'
            elif fileType == 'application/vnd.ms-excel':
                _type = 'csv'
            elif fileType == 'application/octet-stream':
                _type = 'rar'
            elif fileType == 'application/x-zip-compressed':
                _type = 'zip'
            else:
                _type = 'png'

            # get curdate and shift
            result = get_handover_customer_status.query.order_by(
                get_handover_customer_status.sn.desc()).first()

            lastDate = result.date.strftime("%Y-%m-%d")
            lastShift = result.shift

            # file save to where
            fileDateShift = f'static/kpi/{lastDate}/{lastShift}/{zoneSource}/{dbSn}.{_type}'
            if not os.path.exists(os.path.dirname(fileDateShift)):
                try:
                    os.makedirs(os.path.dirname(fileDateShift))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            # save local
            f = request.files.get(fileName)
            f.save(f'kpitemp.{_type}')

            # copy local file to related folder
            copy(f'kpitemp.{_type}', fileDateShift)

            # return type to frontend, then when kpi update with type equal 3, will save the path with _type
        return _type


# review purpose (kpi)
@app.route(
    '/review/kpi/<targetDate>/<targetShift>/<zone>/<targetJiraTicketSn>/<fileType>'
)
def reviewKpiFile(targetDate, targetShift, zone, targetJiraTicketSn, fileType):
    if '-' not in targetDate:
        newDateFormat = targetDate[:4] + '-' + targetDate[
            4:][:2] + '-' + targetDate[4:][2:]
    else:
        newDateFormat = targetDate

    # print(_type)
    if fileType == 'png' or fileType == 'jpg':
        target = f'kpi/{newDateFormat}/{targetShift}/{zone}/{targetJiraTicketSn}.{fileType}'
    else:
        if fileType == 'pptx':
            target = f'example/ppt.png'
        elif fileType == 'docx':
            target = f'example/word.png'
        elif fileType == 'xlsx':
            target = f'example/excel.png'
        elif fileType == 'txt':
            target = f'example/txt.png'
        else:
            target = f'example/sample.png'
    return app.send_static_file(target)


# get kpi file
@app.route(
    '/query/kpi/<targetDate>/<targetShift>/<zone>/<targetJiraTicketSn>/<fileType>'
)
def queryKpiStaticContent(targetDate, targetShift, zone, targetJiraTicketSn,
                          fileType):
    if '-' not in targetDate:
        newDateFormat = targetDate[:4] + '-' + targetDate[
            4:][:2] + '-' + targetDate[4:][2:]
    else:
        newDateFormat = targetDate

    target = f'kpi/{newDateFormat}/{targetShift}/{zone}/{targetJiraTicketSn}.{fileType}'
    return app.send_static_file(target)


@app.route('/sortout/kpi/otrs/<ticketNumber>')
def sortoutKpiOTRS(ticketNumber):
    # get all row with same ticket number on kpi_result
    resultListByNumber = get_handover_kpi_result.query.filter(
        get_handover_kpi_result.origin_source_subject == ticketNumber,
        get_handover_kpi_result.origin_source == 'Ticket').all()

    # setup the set - for store the result, why i use the Set, due to want to name exist set with unique
    requestHandlerSet = set()
    troubleshootingHandlerSet = set()
    troubleshootingHandlerDeputySet = set()
    troubleshootingParticipantsSet = set()

    # check if the type include 3 or 2 or 1
    kpiTypeList = []

    # KPI type level
    incidentLevel = ('Regular Operation', 'Troubleshooting',
                     'Advanced Troubleshooting')

    for y in resultListByNumber:
        kpiTypeList.append(y.type)
        if y.type == '1':
            tmpHandlerList = y.handler.split(',')
            for z in tmpHandlerList:
                requestHandlerSet.add(z)
        else:
            tmpHandlerList = y.handler.split(',')
            for z in tmpHandlerList:
                troubleshootingHandlerSet.add(z)

            if y.handler_second:
                tmpHandlerDeputyList = json.loads(y.handler_second)
                for z in tmpHandlerDeputyList:
                    troubleshootingHandlerDeputySet.add(z)

            if y.participant:
                tmpParticipantsList = json.loads(y.participant)
                for z in tmpParticipantsList:
                    troubleshootingParticipantsSet.add(z)

            if y.type == '3':
                incidentType = incidentLevel[1]

    # check if the type include 3 or 2 or 1
    if '3' in kpiTypeList:
        incidentType = incidentLevel[2]
    elif '2' in kpiTypeList:
        incidentType = incidentLevel[1]
    else:
        incidentType = incidentLevel[0]

    # print('Request Handler - customfield_10075')
    requestHandlerSetWithJsonHeader = [{'value': i} for i in requestHandlerSet]
    # print('Handler(Deputy - customfield_10079')
    troubleshootingHandlerSetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingHandlerSet]
    # print('Participant(s) - customfield_10076')
    troubleshootingHandlerDeputySetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingHandlerDeputySet]
    # print('Troubleshooting Handler - customfield_10077')
    troubleshootingParticipantsSetSetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingParticipantsSet]

    putPayLoadDict = {
        'fields': {
            'handler': requestHandlerSetWithJsonHeader,
            'tsHandler': troubleshootingHandlerSetWithJsonHeader,
            'tsHandlerD': troubleshootingHandlerDeputySetWithJsonHeader,
            'tsParticipant': troubleshootingParticipantsSetSetWithJsonHeader
        }
    }

    if incidentType == 'Regular Operation':
        putPayLoadDict['fields']['kpiType'] = {'value': 'Regular Operation'}
    elif incidentType == 'Troubleshooting':
        putPayLoadDict['fields']['kpiType'] = {"value": "Troubleshooting"}
    else:
        putPayLoadDict['fields']['kpiType'] = {
            "value": "Advanced Troubleshooting"
        }

    return jsonify(putPayLoadDict)


# sort out the KPI and update to Jira
@app.route('/sortout/kpi/tojira/<jiraIssueId>/<action>')
def sortoutKpiToJira(jiraIssueId, action):
    print(f'start sort out result of KPI - JIRA ISSUE ID: {jiraIssueId}')

    # get all kpi result with same JiraIssueId
    resultByJiraIssueId = get_handover_jira_ticket.query.filter(
        get_handover_jira_ticket.issueId == jiraIssueId,
        get_handover_jira_ticket.flagKpiSn != None).all()

    # store here for kpisn list
    storeOfFlagKpiSn = []
    if len(resultByJiraIssueId) != 0:
        for i in resultByJiraIssueId:
            storeOfFlagKpiSn.append(i.flagKpiSn)
    print(f'storeOfFlagKpiSn = {storeOfFlagKpiSn}')

    # setup the set - for store the result, why i use the Set, due to want to name exist set with unique
    requestHandlerSet = set()
    troubleshootingHandlerSet = set()
    troubleshootingHandlerDeputySet = set()
    troubleshootingParticipantsSet = set()

    # check if the type include 3 or 2 or 1
    kpiTypeList = []

    # KPI type level
    incidentLevel = ('Regular Operation', 'Troubleshooting',
                     'Advanced Troubleshooting')

    for x in storeOfFlagKpiSn:
        kpiResultBySn = get_handover_kpi_result.query.filter(
            get_handover_kpi_result.sn == x).all()
        for y in kpiResultBySn:
            kpiTypeList.append(y.type)
            if y.type == '1':
                tmpHandlerList = y.handler.split(',')
                for z in tmpHandlerList:
                    requestHandlerSet.add(z)
            else:
                tmpHandlerList = y.handler.split(',')
                for z in tmpHandlerList:
                    troubleshootingHandlerSet.add(z)

                if y.handler_second:
                    tmpHandlerDeputyList = json.loads(y.handler_second)
                    for z in tmpHandlerDeputyList:
                        troubleshootingHandlerDeputySet.add(z)

                if y.participant:
                    tmpParticipantsList = json.loads(y.participant)
                    for z in tmpParticipantsList:
                        troubleshootingParticipantsSet.add(z)

                if y.type == '3':
                    incidentType = incidentLevel[1]

    # check if the type include 3 or 2 or 1
    if '3' in kpiTypeList:
        incidentType = incidentLevel[2]
    elif '2' in kpiTypeList:
        incidentType = incidentLevel[1]
    else:
        incidentType = incidentLevel[0]

    # print('Request Handler - customfield_10075')
    requestHandlerSetWithJsonHeader = [{'value': i} for i in requestHandlerSet]
    # print('Handler(Deputy - customfield_10079')
    troubleshootingHandlerSetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingHandlerSet]
    # print('Participant(s) - customfield_10076')
    troubleshootingHandlerDeputySetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingHandlerDeputySet]
    # print('Troubleshooting Handler - customfield_10077')
    troubleshootingParticipantsSetSetWithJsonHeader = [{
        'value': i
    } for i in troubleshootingParticipantsSet]

    putPayLoadDict = {
        'fields': {
            'customfield_10075': requestHandlerSetWithJsonHeader,
            'customfield_10079': troubleshootingHandlerSetWithJsonHeader,
            'customfield_10076': troubleshootingHandlerDeputySetWithJsonHeader,
            'customfield_10077':
            troubleshootingParticipantsSetSetWithJsonHeader
        }
    }

    if incidentType == 'Regular Operation':
        putPayLoadDict['fields']['customfield_10078'] = None
    elif incidentType == 'Troubleshooting':
        putPayLoadDict['fields']['customfield_10078'] = {
            "value": "Troubleshooting"
        }
    else:
        putPayLoadDict['fields']['customfield_10078'] = {
            "value": "Advanced Troubleshooting"
        }

    if action == 'sortout':
        return jsonify(putPayLoadDict)
    elif action == 'updateJira':
        print('hit action updateJira')
        # putPayLoadDict = {'fields': {'customfield_10077': troubleshootingHandlerDeputySetWithJsonHeader}}
        putPayLoadJson = json.dumps(putPayLoadDict)

        # start build the Jira Api POST format -
        putUrl = f"https://anyhow-test4u.atlassian.net/rest/api/2/issue/{jiraIssueId}"

        headers = {
            'Authorization':
            'Basic YW55aG93LnRlc3Q0dUBnbWFpbC5jb206eTVJeE9NYTlvWFp1S3cwUFZ5ZDVCNEQw',
            'Content-Type':
            'application/json',
            'Cookie':
            'atlassian.xsrf.token=1bc1fec3-7102-42db-b436-386dfa5b08f6_952072c727f1fa2e7028e7bbd9f60bac9409f559_lin'
        }

        response = requests.request("PUT",
                                    putUrl,
                                    headers=headers,
                                    data=putPayLoadJson)
        print(response.status_code)

        if response.status_code == 204:
            return 'ok'
        else:
            return 'error'


### MTN Part Start ###
@app.route('/mtn/update', methods=['GET', 'POST'])
def mtnUpdate():
    front_data = request.get_json(silent=True)
    jiraTicketSn = front_data['targetJiraTicketSn']
    print(f'jiraTicketSn = {jiraTicketSn}')
    if front_data['curStatus']:
        updateMTNStatus = 1
    else:
        updateMTNStatus = 0
    resultByTicketSn = get_handover_jira_ticket.query.filter(
        get_handover_jira_ticket.sn == jiraTicketSn).first()
    resultByTicketSn.flagMtn = updateMTNStatus
    db.session.commit()
    db.session.close()
    return 'ok'


@app.route('/mtn/query/<issueId>')
def mtnQueryIssueId(issueId):
    if issueId == 'all':
        # only for CalendarPage onMounted query
        # [{CalanderPublicId: ticket number}]
        # check current date
        currentDate = datetime.datetime.now().strftime("%Y-%m-%d")
        queryResultsAll = get_handover_ticket_mtn_mapping.query.filter(get_handover_ticket_mtn_mapping.endTime.__gt__(currentDate)).all()
        # queryResultsAll = get_handover_ticket_mtn_mapping.query.all()
        if queryResultsAll:
            returnList = []
            for i in queryResultsAll:
                tmpDict = {}
                tmpDict[i.googleCalendarId] = i.relatedJiraIssueId
                returnList.append(tmpDict)
            return jsonify(returnList)
        else:
            return jsonify([])
    else:
        queryResult = get_handover_ticket_mtn_mapping.query.filter(
            get_handover_ticket_mtn_mapping.relatedJiraIssueId ==
            issueId).first()
        if queryResult:
            returndict = queryResult.serialize
        else:
            returndict = {}
        return jsonify(returndict)


@app.route('/mtn/insert', methods=['GET', 'POST'])
def mtnIsert():
    front_data = request.get_json(silent=True)
    newId = front_data['_id']
    newLink = front_data['_link']
    relatedIssueId = front_data['IssueId']
    sTime = front_data['startTime']
    eTime = front_data['endTime']
    if front_data['_type'] == 'ndd':
        mtnType = 'No downtime deployment'
    elif front_data['_type'] == 'dd':
        mtnType = 'Downtime deployment'
    elif front_data['_type'] == 'cm':
        mtnType = 'Circuit maintenance'
    elif front_data['_type'] == 'other':
        mtnType = 'Others'
    insertObject = get_handover_ticket_mtn_mapping(
        relatedJiraIssueId=relatedIssueId,
        googleCalendarId=newId,
        googleCalendarLink=newLink,
        startTime=sTime,
        endTime=eTime,
        _type=mtnType)
    db.session.add(insertObject)
    db.session.commit()
    db.session.close()
    return 'mtn info has been updated into DB'


@app.route('/mtn/delete', methods=['GET', 'POST'])
def mtnDelete():
    front_data = request.get_json(silent=True)
    deleteIssueId = front_data['targetIssueId']
    try:
        queryTarget = get_handover_ticket_mtn_mapping.query.filter(
            get_handover_ticket_mtn_mapping.relatedJiraIssueId ==
            deleteIssueId).first()
        remoteItem = queryTarget.serialize
        db.session.delete(queryTarget)
        db.session.commit()
        db.session.close()
    except Exception as e:
        print(e)
        remoteItem = {}
    return jsonify(remoteItem)


### MTN Part End ###


### Note Part Start ###
# query note detail
@app.route('/notes/query/<target>')
def notesQuery(target=None):
    if target == 'all':
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        return_dict = dict(date=result.date.strftime("%Y%m%d"),
                           shift=result.shift)
        # return_dict = dict(date='20220309', shift='A')
        tryToQueryByDateShift = get_handover_notes.query.filter(
            get_handover_notes.date == return_dict['date'],
            get_handover_notes.shift == return_dict['shift']).all()
        containerList = []
        for i in tryToQueryByDateShift:
            assignObject = i.serialize
            checkKpiResultBySn = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.origin_source == 'Note',
                get_handover_kpi_result.related_sn == i.sn).first()
            if checkKpiResultBySn:
                assignObject['kpi_result'] = checkKpiResultBySn.sn
            else:
                assignObject['kpi_result'] = 0
            containerList.append(assignObject)
        return jsonify(containerList)
    elif target == 'list':
        # for move order function
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        return_dict = dict(date=result.date.strftime("%Y%m%d"),
                           shift=result.shift)
        tryToQueryByDateShift = get_handover_notes.query.filter(
            get_handover_notes.date == return_dict['date'],
            get_handover_notes.shift == return_dict['shift'],
            get_handover_notes.sequence != 99).all()
        optionList = [x + 1 for x in range(len(tryToQueryByDateShift))]
        items = []
        for i in optionList:
            items.append({
                'label': f'Insert to position {i}',
                'value': i,
                'color': 'secondary'
            })
        return jsonify(items)
    elif target:
        containerList = []
        querybySn = get_handover_notes.query.filter(
            get_handover_notes.sn == target).first()
        assignObject = querybySn.serialize
        checkKpiResultBySn = get_handover_kpi_result.query.filter(
            get_handover_kpi_result.origin_source == 'Note',
            get_handover_kpi_result.related_sn == querybySn.sn).first()
        if checkKpiResultBySn:
            assignObject['kpi_result'] = checkKpiResultBySn.sn
        else:
            assignObject['kpi_result'] = 0
        containerList.append(assignObject)
        return jsonify(containerList)
    else:
        return f'Nothing will run for target - {target}'


# update note status
@app.route('/notes/update/status', methods=['GET', 'POST'])
def notesUpdateStatus():
    front_data = request.get_json(silent=True)
    action = front_data['action']
    targetSn = front_data['targetNoteSn']
    updateNoteStatus = get_handover_notes.query.filter(
        get_handover_notes.sn == targetSn).first()
    if action == 'edit':
        newEditor = front_data['newEditor']
        updateNoteStatus.update_by = newEditor
        updateNoteStatus.status = True
        db.session.commit()
        db.session.close()
        return f'Done for edit action on DB ( noteSn - {targetSn} )'
    elif action == 'cancel':
        # unlock isUnderEdit for this sn
        updateNoteStatus.status = False
        db.session.commit()
        db.session.close()
        return f'Done for cancel action on DB ( noteSn - {targetSn} )'
    elif action == 'update':
        newEditor = front_data['newEditor']
        targetSn = front_data['targetNoteSn']
        newSummary = front_data['summary']
        newUpdateSummary = front_data['updateSummary']
        updateNoteStatus.status = 0
        updateNoteStatus.summary = newSummary
        updateNoteStatus.update_summary = newUpdateSummary
        updateNoteStatus.update_by = newEditor
        db.session.commit()
        db.session.close()
        return f'Done for update action on DB ( noteSn - {targetSn} )'
    elif action == 'delete':
        noteLocation = updateNoteStatus.sequence
        noteDate = updateNoteStatus.date
        noteShift = updateNoteStatus.shift
        # update target note sn sequence
        updateNoteStatus.sequence = 99
        updateNoteStatus.status = 99
        db.session.commit()
        db.session.close()
        # get all sn list by target date & shift
        curList = get_handover_notes.query.filter(
            get_handover_notes.date == noteDate,
            get_handover_notes.shift == noteShift,
            get_handover_notes.sequence != 99).all()
        changeList = [x.sn for x in curList if x.sequence > noteLocation]
        for i in changeList:
            adjustSequence = get_handover_notes.query.filter(
                get_handover_notes.sn == i).first()
            adjustSequence.sequence = adjustSequence.sequence - 1
            db.session.commit()
            db.session.close()
        return f'Done for delete action on DB ( noteSn - {targetSn} )'
    elif action == 'rollback':
        noteLocation = updateNoteStatus.sequence
        noteDate = updateNoteStatus.date
        noteShift = updateNoteStatus.shift
        curList = get_handover_notes.query.filter(
            get_handover_notes.date == noteDate,
            get_handover_notes.shift == noteShift,
            get_handover_notes.sequence != 99).all()
        maxSequence = max([x.sequence for x in curList])
        updateNoteStatus.sequence = maxSequence + 1
        db.session.commit()
        db.session.close()
        return f'Done for rollback action on DB ( noteSn - {targetSn} )'
    elif action == 'moveSequence':
        newPosition = front_data['newPosition']
        oldPosition = updateNoteStatus.sequence
        # get current list, need to order by sequence
        noteDate = updateNoteStatus.date
        noteShift = updateNoteStatus.shift
        curList = get_handover_notes.query.filter(
            get_handover_notes.date == noteDate,
            get_handover_notes.shift == noteShift,
            get_handover_notes.sequence != 99).order_by(
                get_handover_notes.sequence).all()
        # just use the turple to avoid query DB twice
        curListOfSequence = [(x.sequence, x.sn) for x in curList]
        if newPosition > oldPosition:
            listOfAfterOldPosition = [
                x for x in curListOfSequence if x[0] > oldPosition
            ]
            listOfBeforeNewPosition = [
                y for y in listOfAfterOldPosition if y[0] <= newPosition
            ]
            # print(f'listOfBeforeNewPosition need to - 1 = {listOfBeforeNewPosition}')
            # db adjust to - 1, and use the sn to avoid sequence loop issue
            for (curSequence, loopTargetSn) in listOfBeforeNewPosition:
                subtractOne = get_handover_notes.query.filter(
                    get_handover_notes.sn == loopTargetSn).first()
                subtractOne.sequence = subtractOne.sequence - 1
                db.session.commit()
        else:
            listOfBeforeOldPosition = [
                x for x in curListOfSequence if x[0] < oldPosition
            ]
            listOfAfterNewPosition = [
                y for y in listOfBeforeOldPosition if y[0] >= newPosition
            ]
            # print(f'listOfAfterNewPosition need to + 1 = {listOfAfterNewPosition}')
            # db adjust to + 1, and use the sn to avoid sequence loop issue
            for (curSequence, loopTargetSn) in listOfAfterNewPosition:
                plusOne = get_handover_notes.query.filter(
                    get_handover_notes.sn == loopTargetSn).first()
                plusOne.sequence += 1
                db.session.commit()

        # adjust the target sn
        updateNoteStatus.sequence = newPosition
        db.session.commit()
        db.session.close()
        return f'Done for moveSequence action on DB ( noteSn - {targetSn} )'
    else:
        return 'else ok'


# Only for create note
@app.route('/note/create', methods=['GET', 'POST'])
def noteCreate():
    front_data = request.get_json(silent=True)
    newTitle = front_data['newTitle']
    updateBy = front_data['newEditor']
    timeDict = queryCurrentTime()  # get current date & shift
    # Query note by date & shift
    resultNoteListByDateShift = get_handover_notes.query.filter(
        get_handover_notes.date == timeDict['date'],
        get_handover_notes.shift == timeDict['shift'],
        get_handover_notes.sequence != 99).all()
    nextNoteNumber = len(resultNoteListByDateShift) + 1
    # create class object and insert to DB session
    createNote = get_handover_notes(date=timeDict['date'],
                                    shift=timeDict['shift'],
                                    sequence=nextNoteNumber,
                                    status=0,
                                    customer=newTitle,
                                    summary='New',
                                    update_summary='New',
                                    update_by=updateBy)
    db.session.add(createNote)
    db.session.commit()
    # query by sequence & date & shift then return the sn
    queryByNewSequence = get_handover_notes.query.filter(
        get_handover_notes.date == timeDict['date'],
        get_handover_notes.shift == timeDict['shift'],
        get_handover_notes.sequence == nextNoteNumber).first()
    return str(queryByNewSequence.sn)


@app.route('/notes/traceLog/<source>/<targetTitle>')
def notesTraceLog(source, targetTitle):
    returnDict = {}
    containerUpdateSummaryList = []
    containerCreateSummaryDict = {}
    containerAttachmentList = []
    if source == 'fromSearch':
        queryNoteDbByTitle = get_handover_notes.query.filter(
            get_handover_notes.customer == targetTitle).order_by(
                get_handover_notes.sn).all()
    else:
        queryNoteDbByTitle = get_handover_notes.query.filter(
            get_handover_notes.customer == targetTitle,
            get_handover_notes.status != 99).order_by(
                get_handover_notes.sn).all()

    # print(f'queryNoteDbByTitle = {queryNoteDbByTitle}')

    # check how long has been created for this note
    if len(queryNoteDbByTitle) % 3 == 0:
        returnDict['dayCounter'] = str(int(
            len(queryNoteDbByTitle) / 3)) + ' days'
    elif len(queryNoteDbByTitle) % 3 == 1:
        returnDict['dayCounter'] = str(int(
            len(queryNoteDbByTitle) / 3)) + ' days and one shift'
    else:
        returnDict['dayCounter'] = str(int(
            len(queryNoteDbByTitle) / 3)) + ' days and two shift'

    for (index, value) in enumerate(queryNoteDbByTitle):
        print(value.update_summary)
        if value.check_image:
            imageResult = get_handover_notes_attachment.query.filter(
                get_handover_notes_attachment.noteSn == value.sn).all()
            if imageResult:
                for i in imageResult:
                    containerAttachmentList.append(i.serialize)
        if value.update_summary == 'New':
            # print(f'hit new, {value}')
            containerCreateSummaryDict.update({
                'date':
                f"{value.date.year}-{value.date.month}-{value.date.day}",
                'shift': value.shift,
                'summary': value.summary,
                'editor': value.update_by
            })
        else:
            emptyDict = {}
            if value.update_summary:
                emptyDict[
                    'date'] = f"{value.date.year}-{value.date.month}-{value.date.day}"
                emptyDict['shift'] = value.shift
                emptyDict['updateSummary'] = value.update_summary
                emptyDict['editor'] = value.update_by
                containerUpdateSummaryList.append(emptyDict)

    returnDict['CreateBy'] = containerCreateSummaryDict
    returnDict['UpdateList'] = containerUpdateSummaryList
    returnDict['AttachmentList'] = containerAttachmentList

    print(returnDict)

    return returnDict


# note kpi query, onMounted note use
@app.route('/notes/kpi/query/<targetSn>')
def noteKpiQueryTargetSn(targetSn):
    print(targetSn)
    resultBySn = get_handover_kpi_result.query.filter(
        get_handover_kpi_result.sn == targetSn).first()
    return resultBySn.serialize


### Note Part End ###


### ICP Start ###
@app.route('/icp/query')
def icpQuery():
    result = requests.get('http://10.7.6.205:5015/axios_querying_icp_db/')
    return jsonify(result.json())


@app.route('/icp/check')
def icpCheck():
    try:
        result = requests.get('http://10.7.6.205:5015/check_icp/')
        return str(result.status_code)
    except Exception as e:
        print(e)
        return 'get issue during check icp api, do it later.'


### ICP End ###


### CustomerStatus Start ###
@app.route('/customerStatus/query')
def customerStatusQuery():
    lastResult = get_handover_customer_status.query.filter().order_by(
        get_handover_customer_status.sn.desc()).first()
    print(lastResult)
    return 'ok'


### CustomerStatus End ###


### Misc ###
# check duty
@app.route('/dutycheck', methods=['GET', 'POST'])
def dutyCheckDateShift():
    if request.method == 'GET':
        catchDateShift = handover_main_init('internal')
        date = catchDateShift['date']
        shift = catchDateShift['shift']
        result = requests.get(f'http://10.7.6.199:4998/{date}/{shift}')
        return jsonify(result.json())
    else:
        return 'not yet'


# provide the avatar
@app.route('/review/avatar/<targetName>')
def reviewAvatarTargetName(targetName):
    print(targetName)
    if targetName == 'undefined':
        target = f'ops_team_pic/dinosaur.png'
    else:
        target = f'ops_team_pic/{targetName}.png'
    return app.send_static_file(target)


# hyperlink of SRE Page
@app.route('/hyperlink', methods=['GET', 'POST'])
@app.route('/hyperlink/<action>', methods=['GET', 'POST'])
def hyperlinkSet(action=None):
    if request.method == 'GET':
        if action == 'query':
            tmpList = []
            resultOfall = get_handover_hyperlink_sre_page.query.all()
            for i in resultOfall:
                tmpList.append(i.serialize)
            returnList = sorted(tmpList,
                                key=lambda x: x['counter'],
                                reverse=True)
            return jsonify(returnList)
        else:
            return 'not yet for other action'
    else:
        front_data = request.get_json(silent=True)
        front_action = front_data['action']
        if front_action == 'updateCounter':
            targetSn = front_data['dbSn']
            callTarget = get_handover_hyperlink_sre_page.query.filter(
                get_handover_hyperlink_sre_page.sn == targetSn).first()
            callTarget.counter += 1
            db.session.commit()
            db.session.close()
            return 'counter increase'
        elif front_action == 'AddLink':
            fixedIcon = 'auto_awesome'
            targetDict = front_data['newSet']
            checker = targetDict['title']
            checkDbByTitle = get_handover_hyperlink_sre_page.query.filter(
                get_handover_hyperlink_sre_page.title == checker).all()
            if checkDbByTitle:
                r = Response(status=409, response=f'existed item - {checker}')
                return r
            else:
                insertNewHyperLinkToDb = get_handover_hyperlink_sre_page(
                    title=targetDict['title'],
                    caption=targetDict['caption'],
                    icon=fixedIcon,
                    link=targetDict['link'],
                    counter=0)
                db.session.add(insertNewHyperLinkToDb)
                db.session.commit()
                db.session.close()
                return f'done for add new hyperlink - {checker}'
        elif front_action == 'removeLink':
            targetSn = front_data['targetHyperLinkSn']
            targetName = front_data['targetName']
            selectBySn = get_handover_hyperlink_sre_page.query.filter(
                get_handover_hyperlink_sre_page.sn == targetSn).first()
            if selectBySn:
                db.session.delete(selectBySn)
                db.session.commit()
                db.session.close()
                return f'done for remove hyperlink {targetName}'
            else:
                r = Response(
                    status=409,
                    response=f'target {targetName} does not exist on DB.')
                return r
        elif front_action == 'updateLink':
            try:
                currentSet = front_data['adjustSet']
                # list dict - forloop these dict
                for i in currentSet:
                    # forloop key & value for each dict and update to DB
                    for key, value in i.items():
                        get_handover_hyperlink_sre_page.query.filter(
                            get_handover_hyperlink_sre_page.sn ==
                            i['sn']).update({key: value})
                    db.session.commit()
                db.session.close()
                return 'done for update all hyperlink info'
            except Exception as e:
                print(e)
                r = Response(status=409,
                             response=f'update failed, error message - {e}')
                return r
        return 'not yet for other POST'


# user controller
@app.route('/controller/update', methods=['GET', 'POST'])
def controllerUpdate():
    front_data = request.get_json(silent=True)
    cUser = front_data['currentUser']
    cSetting = front_data['currentControllerSetting']

    newRecordList = []
    newRecordList.append(
        dict(
            username=cUser,
            controllerCustomerStatus=json.dumps([
                next(item for item in cSetting
                     if item['name'] == 'controllerCustomerStatus')['value'],
                next(item for item in cSetting
                     if item['name'] == 'controllerCustomerStatus')['isExtend']
            ]),
            controllerCalendar=json.dumps([
                next(item for item in cSetting
                     if item['name'] == 'controllerCalendar')['value'],
                next(item for item in cSetting
                     if item['name'] == 'controllerCalendar')['isExtend']
            ]),
            controllerMontoringService=json.dumps([
                next(item for item in cSetting
                     if item['name'] == 'controllerMontoringService')['value'],
                next(item for item in cSetting if item['name'] ==
                     'controllerMontoringService')['isExtend']
            ]),
            controllerICPStatus=json.dumps([
                next(item for item in cSetting
                     if item['name'] == 'controllerICPStatus')['value'],
                next(item for item in cSetting
                     if item['name'] == 'controllerICPStatus')['isExtend']
            ]),
            controllerNote=json.dumps([
                next(item for item in cSetting
                     if item['name'] == 'controllerNote')['value'],
                next(item for item in cSetting
                     if item['name'] == 'controllerNote')['isExtend']
            ]),
            controllerTicket=json.dumps([
                next(item for item in cSetting
                     if item['name'] == 'controllerTicket')['value'],
                next(item for item in cSetting
                     if item['name'] == 'controllerTicket')['isExtend']
            ]),
            controllerFavorite=json.dumps([
                next(item for item in cSetting
                     if item['name'] == 'controllerFavorite')['value'],
                next(item for item in cSetting
                     if item['name'] == 'controllerFavorite')['isExtend']
            ]),
            lastTimeUpdate=datetime.datetime.now()))

    checkDbByUserName = get_handover_user_controller.query.filter(
        get_handover_user_controller.username == cUser).first()
    if checkDbByUserName:
        for key, value in newRecordList[0].items():
            get_handover_user_controller.query.filter(
                get_handover_user_controller.sn ==
                checkDbByUserName.sn).update({key: value})
        db.session.commit()
    else:
        for x in newRecordList:
            insertDb = get_handover_user_controller(**x)
            db.session.add(insertDb)
        db.session.commit()
        db.session.close()

    return 'opk'


@app.route('/controller/updateFavoriteLink', methods=['GET', 'POST'])
def controllerUpdateFavoriteLink():
    front_data = request.get_json(silent=True)
    cUser = front_data['currentUser']
    cSetting = front_data['currentFavoriteLink']
    # sort out the list dict for user
    allhyperLinkList = get_handover_hyperlink_sre_page.query.all()
    sortOutBySettingList = [
        x.serialize for x in allhyperLinkList if x.sn in cSetting
    ]
    # get user controller setting
    targetUser = get_handover_user_controller.query.filter(
        get_handover_user_controller.username == cUser).first()
    favoriteSettingValue = json.loads(targetUser.controllerFavorite)[0]
    newValue = []
    newValue.append(favoriteSettingValue)
    newValue.append(sortOutBySettingList)
    targetUser.controllerFavorite = json.dumps(newValue)
    db.session.commit()
    db.session.close()
    db.session.remove()
    return 'ok'


@app.route('/controller/query/<cUser>')
def controllerQuery(cUser):
    queryDbByCUser = get_handover_user_controller.query.filter(
        get_handover_user_controller.username == cUser).first()
    if queryDbByCUser:
        return queryDbByCUser.serialize
    else:
        return 'new'


@app.route('/get_customer_status_note')
def queryGet_customer_status_note():
    result = get_customer_status_note.query.all()
    print(result)
    return 'ok'


@app.route('/customerStatus/query/<target>')
def queryGet_handover_customer_status(target):
    if target == 'last':
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        newDict = {}
        for key, value in result.serialize.items():
            if value == 'Green':
                newDict[key] = value
            else:
                targetDate = result.date
                targetShift = result.shift
                queryCustomerStatusNote = get_customer_status_note.query.filter(
                    get_customer_status_note.date == targetDate,
                    get_customer_status_note.shift == targetShift).all()
                print(queryCustomerStatusNote)
                eventListContainer = []
                try:
                    for key1, value1 in enumerate(queryCustomerStatusNote):
                        scrollTargetList = json.loads(value1.jira_ticket)
                        if scrollTargetList[0] == 'jira':
                            scrollTargetString = str(scrollTargetList[1])
                        else:
                            scrollTargetString = scrollTargetList[0] + str(
                                scrollTargetList[1])
                        if key == '_188A':
                            if '188A' in json.loads(value1.customer):
                                computedString = f'Cause by {value1.impactby} ( refer to {value1.note} )'
                                eventListContainer.append([
                                    value1.status, f'Event:  {computedString}',
                                    value1.sn, scrollTargetString
                                ])
                        else:
                            if key in json.loads(value1.customer):
                                computedString = f'Cause by {value1.impactby} ( refer to {value1.note} )'
                                eventListContainer.append([
                                    value1.status, f'Event:  {computedString}',
                                    value1.sn, scrollTargetString
                                ])
                    newDict[key] = ['abnormal', [eventListContainer]]
                except Exception as e:
                    print(e)
        return jsonify(newDict)
    elif target == 'relateItem':
        timeDict = queryCurrentTime()
        resultNotes = get_handover_notes.query.filter(
            get_handover_notes.date == timeDict['date'],
            get_handover_notes.shift == timeDict['shift']).all()
        resultOTRS = get_handover_otrs.query.filter(
            get_handover_otrs.date == timeDict['date'],
            get_handover_otrs.shift == timeDict['shift']).all()

        resultJiraRow = get_jsm_ops_prod.query.filter(
            and_(get_jsm_ops_prod.jiraStatus != 121,
                 get_jsm_ops_prod.jiraStatus != 71,
                 get_jsm_ops_prod.jiraStatus != 6,
                 get_jsm_ops_prod.ticketStatus != 99)).all()

        resultJira = [(x.sn, x.title, y.issueId, y.issueKey) for x in resultJiraRow for y in get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == x.mapping).all()]

        resultList = []

        # type: Note, SN: sn, label: Note - customer

        for i in resultNotes:
            resultList.append({
                'value': json.dumps(('note', i.sn)),
                'label': f'Note - {i.customer}'
            })

        for i in resultOTRS:
            resultList.append({
                'value': json.dumps(('otrs', i.number)),
                'label': f'YTS{i.number} - {i.subject}'
            })

        for i in resultJira:
            resultList.append({
                'value':
                json.dumps(('jira', i[0])),
                'label':
                f'[JIRA] {i[3]} - {i[1]}'
            })

        return jsonify(resultList)


@app.route('/customerStatus/delete', methods=['GET', 'POST'])
def customerStatusDeletePost():
    front_data = request.get_json(silent=True)
    targetDbRowSn = front_data['targetSn']
    targetService = front_data['targetService']
    curData = front_data['targetDate']
    curShift = front_data['targetShift']
    selectBySn = get_customer_status_note.query.filter(
        get_customer_status_note.sn == targetDbRowSn).first()
    # adjust customer status note custoemr list
    adjustCustomerList = json.loads(selectBySn.customer)
    adjustCustomerList.remove(targetService)
    selectBySn.customer = json.dumps(adjustCustomerList)
    db.session.commit()
    db.session.close()

    # check cur target service status
    eventList = get_customer_status_note.query.filter(
        get_customer_status_note.date == curData,
        get_customer_status_note.shift == curShift).all()

    checkEventLevelList = []

    for i in eventList:
        if targetService in json.loads(i.customer):
            checkEventLevelList.append(i.status)

    selectCustomerStatus = get_handover_customer_status.query.filter(
        get_handover_customer_status.date == curData,
        get_handover_customer_status.shift == curShift).first()

    if len(checkEventLevelList) == 0:
        eventLevel = 'Green'
    elif 'Red' in checkEventLevelList:
        eventLevel = 'Red'
    else:
        eventLevel = 'Yellow'

    if targetService == '188A':
        selectCustomerStatus._188A = eventLevel
    elif targetService == 'SBK':
        selectCustomerStatus.SBK = eventLevel
    elif targetService == 'LDR':
        selectCustomerStatus.LDR = eventLevel
    elif targetService == 'KENO':
        selectCustomerStatus.KENO = eventLevel
    elif targetService == 'GICT':
        selectCustomerStatus.GICT = eventLevel
    elif targetService == 'CAS':
        selectCustomerStatus.CAS = eventLevel
    elif targetService == 'Others':
        selectCustomerStatus.Others = eventLevel

    db.session.commit()
    db.session.close()
    db.session.remove()

    return 'ok'


@app.route('/customerStatus/update', methods=['GET', 'POST'])
def customerStatusUpdatePost():
    front_data = request.get_json(silent=True)
    curData = front_data['targetDate']
    curShift = front_data['targetShift']
    print(front_data['eventLevel'])
    # update the service status by list
    queryCurRow = get_handover_customer_status.query.filter(
        get_handover_customer_status.date == curData,
        get_handover_customer_status.shift == curShift).first()
    # fix due to class issue, dry already
    for i in front_data['affectedBuList']:
        if i == '188A':
            if queryCurRow._188A != front_data['eventLevel']:
                if queryCurRow._188A != 'Red':
                    queryCurRow._188A = front_data['eventLevel']
        elif i == 'SBK':
            if queryCurRow.SBK != front_data['eventLevel']:
                if queryCurRow.SBK != 'Red':
                    queryCurRow.SBK = front_data['eventLevel']
        elif i == 'LDR':
            if queryCurRow.LDR != front_data['eventLevel']:
                if queryCurRow.LDR != 'Red':
                    queryCurRow.LDR = front_data['eventLevel']
        elif i == 'KENO':
            if queryCurRow.KENO != front_data['eventLevel']:
                if queryCurRow.KENO != 'Red':
                    queryCurRow.KENO = front_data['eventLevel']
        elif i == 'GICT':
            if queryCurRow.GICT != front_data['eventLevel']:
                if queryCurRow.GICT != 'Red':
                    queryCurRow.GICT = front_data['eventLevel']
        elif i == 'CAS':
            if queryCurRow.CAS != front_data['eventLevel']:
                if queryCurRow.CAS != 'Red':
                    queryCurRow.CAS = front_data['eventLevel']
        elif i == 'Others':
            if queryCurRow.Others != front_data['eventLevel']:
                if queryCurRow.Others != 'Red':
                    queryCurRow.Others = front_data['eventLevel']
    db.session.commit()
    db.session.close()

    # update customer status note db
    # check the DB to see if this shift already create the event
    resultBydataShift = get_customer_status_note.query.filter(
        get_customer_status_note.date == curData,
        get_customer_status_note.shift == curShift).all()
    if resultBydataShift:
        curGroupNumber = len(resultBydataShift) + 1
    else:
        curGroupNumber = 1

    insertNewRowToDb = get_customer_status_note(
        date=front_data['targetDate'],
        shift=front_data['targetShift'],
        customer=json.dumps(front_data['affectedBuList']),
        note=front_data['relatedItem'],
        impactby=front_data['rootcause'],
        egset=curGroupNumber,
        status=front_data['eventLevel'],
        event_start_time=front_data['eventStartTime'],
        event_end_time=front_data['eventEndTime'],
        outage_time=front_data['eventOutage'][0],
        jira_ticket=front_data['relatedItemRow'])
    db.session.add(insertNewRowToDb)
    db.session.commit()
    db.session.close()
    db.session.remove()
    return 'ok'


@app.route('/searchPage/query', methods=['GET', 'POST'])
def searchPageQuery():
    front_data = request.get_json(silent=True)
    kw = front_data['keyword'].strip()
    curOffSet = front_data['curOffset']
    curSource = front_data['targetSource']
    isNeedToCheckCount = front_data['firstTime']
    print(f'cur kw - {kw}')
    print(f'cur offset - {curOffSet}')
    print(f'cur source - {curSource}')
    print(f'isNeedToCheckCount - {isNeedToCheckCount}')
    returnList = []
    startTime = datetime.datetime.now()
    # note, search customer, summary, update_summary, or date
    if curSource == 'NOTE':
        noteResult = get_handover_notes.query.filter(
            or_(get_handover_notes.customer.ilike(f'%{kw}%'),
                get_handover_notes.summary.ilike(f'%{kw}%'))).order_by(
                    get_handover_notes.sn.desc()).offset(curOffSet).limit(
                        4).all()
        if isNeedToCheckCount == 0:
            eventCount = get_handover_notes.query.filter(
                or_(get_handover_notes.customer.ilike(f'%{kw}%'),
                    get_handover_notes.summary.ilike(f'%{kw}%'))).count()
        else:
            eventCount = isNeedToCheckCount

        for i in noteResult:
            returnList.append({
                'date': f'{i.date.year}/{i.date.month}/{i.date.day}',
                'shift': i.shift,
                'subject': i.customer,
                'content': i.summary,
                'updateContent': i.update_summary,
                'source': 'NOTE',
                'sourceSn': i.sn
            })

    elif curSource == 'OTRS':
        # orts, search subject, summary, update_summary, or number and date
        otrsResult = get_handover_otrs.query.filter(
            or_(get_handover_otrs.subject.ilike(f'%{kw}%'),
                get_handover_otrs.summary.ilike(f'%{kw}%'))).order_by(
                    get_handover_otrs.sn.desc()).offset(curOffSet).limit(
                        4).all()
        if isNeedToCheckCount == 0:
            print('hit check count')
            eventCount = get_handover_otrs.query.filter(
                or_(get_handover_otrs.subject.ilike(f'%{kw}%'),
                    get_handover_otrs.summary.ilike(f'%{kw}%'))).count()
        else:
            eventCount = isNeedToCheckCount

        for i in otrsResult:
            returnList.append({
                'date': f'{i.date.year}/{i.date.month}/{i.date.day}',
                'shift': i.shift,
                'subject': f'YTS{i.number}-{i.subject}',
                'content': i.summary,
                'updateContent': i.update_summary,
                'source': 'OTRS',
                'sourceSn': i.number
            })

    returnObject = []
    returnObject.append(returnList)
    returnObject.append(eventCount)
    returnObject.append(kw)

    endTime = datetime.datetime.now()
    totalTime = endTime - startTime
    print(totalTime)

    return jsonify(returnObject)
    # jira, ticketName, summary, update_summary, or date, ticket number is more tricky
    return 'ok'


@app.route('/loginCheck', methods=['GET', 'POST'])
def login_using_ldap():
    front_data = request.get_json(silent=True)
    login_username = front_data['userAccount']
    login_password = front_data['userPassword']
    server = Server('172.16.48.20', get_info=ALL)
    list_username_after_split = login_username.split(".")
    first_name = list_username_after_split[1]
    last_name = list_username_after_split[2]
    user_name_to_query_ad = f"{first_name} {last_name}"
    returnName = f'{str.title(first_name)}.{str.title(last_name)}'
    defineGroup = {
        "David.Tung": "DBA",
        "Tony.Wu": "DBA",
        "Albert.Huang": "DBA",
        "Robert.Lin": "DBA",
        "Stanley.Chen": "DBA",
        "Demon.Wu": "DBA",
        "Carny.Chou": "DBA",
        "Austin.Chang": "DBA",
        "William.Liu": "DBA",
        "Gary.Tseng": "SYS",
        "Paul.Chen": "SYS",
        "Sun.Sun": "SYS",
        "Ran.Shih": "SYS",
        "Ian.Hsu": "SYS",
        "Noel.Huang": "SYS",
        "Wesley.Hung": "SYS",
        "Ralf.Wu": "SYS",
        "Justin.Yeh": "NET",
        "Josh.Liu": "NET",
        "Ryo.Bing": "NET",
        "Ray.Hong": "NET",
        "Chris.Yen": "NET",
        "Shane.Tzou": "NET",
        "Daniel.Liu": "OPS",
        "Cyril.Rejas": "OPS",
        "Huck.Chen": "OPS",
        "Albert.Liu": "OPS",
        "Keven.Chang": "OPS",
        "Gary.Wu": "OPS",
        "Allen.Yu": "OPS",
        "Danny.Wu": "OPS",
        "Cadalora.Lin": "OPS",
        "Ivan.Chu": "OPS",
        "Larry.Tsou": "OPS",
        "Thurston.Chao": "OPS",
        "Asky.Huang": "OPS",
        "Bob.Lin": "OPS",
        "Aiden.Tan": "OPS",
        "Eric.Kao": "OPS",
        "Alex.Lin": "OPS",
        "Rorschach.Ye": "OPS",
        "Bayu.Winursito": "OPS",
        "Barret.Tai": "OPS"
    }
    try:
        print({
            'status': 'success',
            'user': returnName,
            'group': defineGroup[returnName]
        })
        return jsonify({
            'status': 'success',
            'user': returnName,
            'group': defineGroup[returnName]
        })
    except Exception as e:
        print(e)
        return jsonify({'status': 'Login failed due to unexpected username'})

    # try:
    #     conn = Connection(
    #         server,
    #         f'CN={user_name_to_query_ad},OU=Users,OU=YT,DC=ICT888,DC=net',
    #         f"{login_password}",
    #         auto_bind=True)
    #     dict_connection_result = conn.result
    #     for key_1, dic_value_1 in dict_connection_result.items():
    #         # print(f"key_1={key_1} / dic_value_1={dic_value_1}")
    #         if key_1 == "description":
    #             if dic_value_1 == "success":
    #                 return jsonify({'status': 'success', 'user': returnName, 'group': defineGroup[returnName]})
    #             else:
    #                 return "Didn't success"
    # except Exception as e:
    #     print(e)
    #     return jsonify({'status': 'failed'})


@app.route('/shiftTable', methods=['GET', 'POST'])
@app.route('/shiftTable/<curData>/<curShift>', methods=['GET', 'POST'])
def shiftTableRouting(curData=None, curShift=None):
    if request.method == 'GET':
        try:
            time_obj = datetime.datetime.strptime(curData, "%Y%m%d")
            queryResult = get_handover_shift_table.query.filter(get_handover_shift_table.date == time_obj, get_handover_shift_table.shift == curShift ).first()
            returnShiftList = json.loads(queryResult.teammates)
            timeFormat = queryResult.date.strftime('%Y%m%d')
            return jsonify([returnShiftList, queryResult.shift, timeFormat, queryResult.serialize_shift])
        except Exception as e:
            queryResult = get_handover_shift_table.query.order_by(get_handover_shift_table.sn.desc()).first()
            returnShiftList = json.loads(queryResult.teammates)
            timeFormat = queryResult.date.strftime('%Y%m%d')
            return jsonify([returnShiftList, queryResult.shift, timeFormat, queryResult.serialize_shift])
    else:
        front_data = request.get_json(silent=True)
        targetDateRow = front_data['date']
        targetDate = f'{targetDateRow[:4]}-{targetDateRow[4:][:2]}-{targetDateRow[6:][:2]}'
        targetShift = front_data['shift']
        targetList = front_data['shiftList']
        shift_details = front_data['shiftDetail']

        # check need to create the new row or update the data
        queryResult = get_handover_shift_table.query.filter(
            get_handover_shift_table.date == targetDate,
            get_handover_shift_table.shift == targetShift).first()
        if queryResult:
            queryResult.teammates = json.dumps(targetList)
            queryResult.shift_leader = shift_details['shift_leader']
            queryResult.title_handover = json.dumps(shift_details['title_handover'])
            queryResult.title_alert_handler = json.dumps(shift_details['title_alert_handler'])
            queryResult.title_message_handler = json.dumps(shift_details['title_message_handler'])
            queryResult.title_request_handler = json.dumps(shift_details['title_request_handler'])
            db.session.commit()
            db.session.close()
            db.session.remove()
        else:
            print('add new row')
            insertToDb = get_handover_shift_table(
                date=targetDate,
                shift=targetShift,
                teammates=json.dumps(targetList),
                shift_leader = shift_details['shift_leader'],
                title_handover = json.dumps(shift_details['title_handover']),
                title_alert_handler = json.dumps(shift_details['title_alert_handler']),
                title_message_handler = json.dumps(shift_details['title_message_handler']),
                title_request_handler = json.dumps(shift_details['title_request_handler']))
            db.session.add(insertToDb)
            db.session.commit()
            db.session.close()
            db.session.remove()
        updateToSkypy = ' | '.join(targetList)
        skypeCheck = True
        while skypeCheck:
            try:
                curSkypeSession = Skype("yt.ops", "0894$Yt8074!@#")
                curSkypeSession.setMood(updateToSkypy)
                skypeCheck = False
            except Exception as e:
                print(e)
                print('do again after 5 sec')
                time.sleep(5)
        return 'method is post, updated list to backend DB and Skype mood'

@app.route('/shiftleader/api/queryraw', methods=['GET', 'POST'])
def shiftleaderapiqueryraw():
    front_data = request.get_json(silent=True)
    targetShift = front_data['shift']
    targetDate = front_data['dateRange']

    # check the date is single date or multiple date
    if isinstance(targetDate, str):
        # print('single date')
        time_obj = datetime.datetime.strptime(targetDate, "%Y/%m/%d")
        time_str_with_format = time_obj.strftime('%Y%m%d')
        time_str_with_local_db_format = time_obj.strftime('%Y-%m-%d')
        result = requests.get(f'http://10.7.6.185:777/ops/{time_str_with_format}/{targetShift}/') # query the excel data based on Ror API
        try:                
            resultJson = result.json()
            returnDict = {}
            # check the local db
            result_local_db = get_handover_shift_table.query.filter(get_handover_shift_table.date == time_str_with_local_db_format, get_handover_shift_table.shift == targetShift).first()
            if result_local_db:
                returnDict = result_local_db.serialize_shift
                returnDict['_type'] = 'localdb'
                returnDict['teammates'] = json.loads(result_local_db.teammates)
            else:
                returnDict['_type'] = 'api'
                returnDict['teammates'] = [ item for item in resultJson['members'] if item ]
            returnDict = dict(result=returnDict, shift=targetShift, date=time_str_with_format, status='success')
            r = Response(status=200, response=json.dumps(returnDict))
            r.headers["Content-Type"] = "application/json"
            return r
        except Exception as e:
            print(e)
            returnResult = result.text
            returnDict = dict(result=returnResult, shift=targetShift, date=time_str_with_format, status='failed')
            r = Response(status=200, response=json.dumps(returnDict))
            r.headers["Content-Type"] = "application/json"
            return r
    elif isinstance(targetDate, dict):
        print('multiple date')
        from_which_date = targetDate['from']
        to_which_date = targetDate['to']
        # string to timeobj
        start = datetime.datetime.strptime(from_which_date, "%Y/%m/%d")
        end = datetime.datetime.strptime(to_which_date, "%Y/%m/%d")
        date_list = []
        delta = datetime.timedelta(days=1)
        while start <= end:
            date_list.append(start.strftime("%Y%m%d"))
            start += delta

        # for the date_list to query the api
        # 1. only accept when all date members are the same, if one of members list is different, will return the error then ask user to selete the date range again
        compare_list = []
        result_list = []
        pass_list = []
        error_list = []
        
        for i in date_list:
            print(f'checking - {i}')
            tmp_url = f'http://10.7.6.185:777/ops/{i}/{targetShift}/'
            try:
                result = requests.get(tmp_url)
                resultJson = result.json()
                if len(compare_list) == 0:
                    compare_list = resultJson['members']
                    compare_list.sort()
                    pass_list.append(i)
                    result_list.append(resultJson)
                else:
                    # means second round already, need to check the member
                    new_list = resultJson['members']
                    new_list.sort()
                    if compare_list == new_list:
                        pass_list.append(i)
                        result_list.append(resultJson)
                    else:
                        error_list.append(i)
                        result_list.append(resultJson)
                        returnDict = dict(result=result_list, diffDay=error_list, originDateRange=targetDate, status='failed', details='One of members list is different, please re select date range again')
                        r = Response(status=200, response=json.dumps(returnDict))
                        r.headers["Content-Type"] = "application/json"
                        return r
            except Exception as e:
                error_list.append(i)
                returnDict = dict(result=result_list, diffDay=error_list, originDateRange=targetDate, status='failed', details=result.text)
                r = Response(status=200, response=json.dumps(returnDict))
                r.headers["Content-Type"] = "application/json"
                return r

        returnDict = dict(result=compare_list, shift=targetShift, date=targetDate, status='success')
        r = Response(status=200, response=json.dumps(returnDict))
        r.headers["Content-Type"] = "application/json"
        return r

@app.route('/shiftleader/api/reviewdate', methods=['GET', 'POST'])
def shiftleaderapireviewdate():
    front_data = request.get_json(silent=True)
    targetDate = front_data['dateRange']
    if isinstance(targetDate, str):
        # print('single date')
        time_obj = datetime.datetime.strptime(targetDate, "%Y/%m/%d")
        queryResult = get_handover_shift_table.query.filter(get_handover_shift_table.date == time_obj, get_handover_shift_table.shift_leader != None).all()

        if len(queryResult) == 0:
            returnDict = dict(result=f'Unable to find the shift leader date based on {targetDate}', status='failed')
            r = Response(status=200, response=json.dumps(returnDict))
            r.headers["Content-Type"] = "application/json"
            return r
        else:
            returnList = [ i.serialize_review_handler for i in queryResult if i.shift_leader != '' ]
            if len(returnList) != 0:
                returnDict = dict(result=returnList, status='success')
                r = Response(status=200, response=json.dumps(returnDict))
                r.headers["Content-Type"] = "application/json"
            else:
                returnDict = dict(result=f'Unable to find the shift leader date based on {targetDate}', status='failed')
                r = Response(status=200, response=json.dumps(returnDict))
                r.headers["Content-Type"] = "application/json"
            return r
    elif isinstance(targetDate, dict):
        print('multiple date')
        result = get_handover_shift_table.query.filter(
            get_handover_shift_table.date.between( 
                targetDate['from'], 
                targetDate['to'])).order_by(get_handover_shift_table.sn.desc()).all()
        
        returnList = [ i.serialize_review_handler for i in result if i.shift_leader != '' ]
        returnDict = dict(result=returnList, status='success')
        r = Response(status=200, response=json.dumps(returnDict))
        r.headers["Content-Type"] = "application/json"
        return r

@app.route('/shiftleader/api/assign', methods=['GET', 'POST'])
def shiftleaderapiassign():
    front_data = request.get_json(silent=True)
    dictDetails = front_data['shiftDetails']
    dateRange = front_data['dateRange']
    whichShift = front_data['whichShift']
    cur_teammates = front_data['curTeammates']
    print(front_data)
    if isinstance(dateRange, str):
        time_obj = datetime.datetime.strptime(dateRange, "%Y/%m/%d")
        time_string_with_format = time_obj.strftime('%Y-%m-%d')
        # check the if the date in the table
        result = get_handover_shift_table.query.filter(get_handover_shift_table.date == time_string_with_format, get_handover_shift_table.shift == whichShift).first()
        if result:
            result.shift_leader = dictDetails['shift_leader']
            result.title_handover = json.dumps(dictDetails['title_handover'])
            result.title_alert_handler = json.dumps(dictDetails['title_alert_handler'])
            result.title_message_handler = json.dumps(dictDetails['title_message_handler'])
            result.title_request_handler = json.dumps(dictDetails['title_request_handler'])
            result.teammates = json.dumps(cur_teammates)
            db.session.commit()
        else:
            print('create a new one')
            insertNewRow = get_handover_shift_table(date=time_string_with_format, shift=whichShift, teammates=json.dumps(cur_teammates), shift_leader=dictDetails['shift_leader'], title_handover=json.dumps(dictDetails['title_handover']), title_alert_handler=json.dumps(dictDetails['title_alert_handler']), title_message_handler=json.dumps(dictDetails['title_message_handler']), title_request_handler=json.dumps(dictDetails['title_request_handler']))
            db.session.add(insertNewRow)
            db.session.commit()
            db.session.close()
        return 'update success', 200
    else:
        print('update the more than one day')
        return 'not support', 500

@app.route('/kpi/detail/<who>/<level>/<cdate>')
def queryKpiDetail(who, level, cdate):
    rangeDict = {
        "2022": [1947],
        '202211': [6004],
        '202210': [6003, 5807],
        '202209': [5806, 5590],
        '202208': [5589, 4975],
        '202207': [4974, 4441],
        '202206': [4440, 3886],
        '202205': [3885, 3306],
        '202204': [3305, 2695],
        '202203': [2694, 2190],
        '202202': [2189, 2077],
        '202201': [2076, 1947],
        "2021": [1946, 143],
        '202112': [1946, 1803],
        '202111': [1802, 1633],
        '202110': [1632, 1543],
        '202109': [1542, 1412],
        '202108': [1411, 1247],
        '202107': [1246, 1105],
        '202106': [1104, 917],
        '202105': [916, 729],
        '202104': [728, 591],
        '202103': [590, 446],
        '202102': [445, 327],
        '202101': [326, 143],
        '202012': [142]
    }

    returnList = []

    if cdate == '2022':
        if level == 'handlerR':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][0],
                get_handover_kpi_result.type == '1',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerT':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][0],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerTs':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][0],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handlerTp':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][0],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.participant.contains(who)).all()
        elif level == 'handleraT':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][0],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handleraTs':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][0],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handleraTp':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][0],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.participant.contains(who)).all()
    elif cdate == '202211':
        if level == 'handlerR':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][1],
                get_handover_kpi_result.type == '1',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerT':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][1],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerTs':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][1],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handlerTp':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][1],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.participant.contains(who)).all()
        elif level == 'handleraT':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][1],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handleraTs':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][1],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handleraTp':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn >= rangeDict[cdate][1],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.participant.contains(who)).all()
    elif len(rangeDict[cdate]) == 1:
        if level == 'handlerR':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn <= rangeDict[cdate][0],
                get_handover_kpi_result.type == '1',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerT':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn <= rangeDict[cdate][0],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerTs':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn <= rangeDict[cdate][0],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handlerTp':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn <= rangeDict[cdate][0],
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.participant.contains(who)).all()
        elif level == 'handleraT':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn <= rangeDict[cdate][0],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handleraTs':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn <= rangeDict[cdate][0],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handleraTp':
            result = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.sn <= rangeDict[cdate][0],
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.participant.contains(who)).all()
    else:
        if level == 'handlerR':
            result = get_handover_kpi_result.query.filter(
                and_(get_handover_kpi_result.sn >= rangeDict[cdate][1],
                     get_handover_kpi_result.sn <= rangeDict[cdate][0]),
                get_handover_kpi_result.type == '1',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerT':
            result = get_handover_kpi_result.query.filter(
                and_(get_handover_kpi_result.sn >= rangeDict[cdate][1],
                     get_handover_kpi_result.sn <= rangeDict[cdate][0]),
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handlerTs':
            result = get_handover_kpi_result.query.filter(
                and_(get_handover_kpi_result.sn >= rangeDict[cdate][1],
                     get_handover_kpi_result.sn <= rangeDict[cdate][0]),
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handlerTp':
            result = get_handover_kpi_result.query.filter(
                and_(get_handover_kpi_result.sn >= rangeDict[cdate][1],
                     get_handover_kpi_result.sn <= rangeDict[cdate][0]),
                get_handover_kpi_result.type == '2',
                get_handover_kpi_result.participant.contains(who)).all()
        elif level == 'handleraT':
            result = get_handover_kpi_result.query.filter(
                and_(get_handover_kpi_result.sn >= rangeDict[cdate][1],
                     get_handover_kpi_result.sn <= rangeDict[cdate][0]),
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler.contains(who)).all()
        elif level == 'handleraTs':
            result = get_handover_kpi_result.query.filter(
                and_(get_handover_kpi_result.sn >= rangeDict[cdate][1],
                     get_handover_kpi_result.sn <= rangeDict[cdate][0]),
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.handler_second.contains(who)).all()
        elif level == 'handleraTp':
            result = get_handover_kpi_result.query.filter(
                and_(get_handover_kpi_result.sn >= rangeDict[cdate][1],
                     get_handover_kpi_result.sn <= rangeDict[cdate][0]),
                get_handover_kpi_result.type == '3',
                get_handover_kpi_result.participant.contains(who)).all()
        # result = get_handover_kpi_result.query.filter(and_(get_handover_kpi_result.sn >= rangeDict[cdate][1], get_handover_kpi_result.sn <= rangeDict[cdate][0])).all()

    for i in result:
        cDate = i.related_date
        cShift = i.related_shift
        cSource = i.origin_source
        cSourceTitle = i.origin_source_subject
        cSourceSn = i.related_sn
        cResolved = i.resolve_status
        returnList.append(
            dict(date=f'{cDate}-{cShift}',
                 title=f'[{cSource}] - {cSourceTitle}',
                 sourceSn=cSourceSn,
                 status=cResolved))
    return jsonify(returnList)


@app.route('/kpi/query/<targetDate>')
def queryKpiResult(targetDate=None):
    tmpDict = {}  # For type 1
    tmpDictType2M = {}  # For type 2 handler
    tmpDictType2S = {}  # For type 2 handler_second
    tmpDictType2P = {}  # For type 2 particident
    tmpDictType3M = {}  # For type 3 handler
    tmpDictType3S = {}  # For type 3 handler_second
    tmpDictType3P = {}  # For type 3 particident
    # tmpDictType2Total = {}  # For type 2 total [m, s, p]
    tmpDictTotal = {}  # For summary table, tmp
    tmpListTotal = []  # For summary table, sorted
    datasetsList = []  # For type 1
    datasetsTsList = []  # For type 2 ts [m]
    datasetsTssList = []  # For type 2 ts [s]
    datasetsTspList = []  # For type 2 ts [p]
    datasetsATsList = []  # For type 2 ts [m]
    datasetsATssList = []  # For type 2 ts [s]
    datasetsATspList = []  # For type 2 ts [p]
    returnDict1 = {}
    returnDict2 = {}
    returnDict2_S = {}
    returnDict2_P = {}
    returnDict3 = {}
    returnDict3_S = {}
    returnDict3_P = {}
    returnList = []
    colorList = [
        "#F08080", "#FFE4E1", "#FFFF4D", "#7FFF00", "#32CD32", "#20B2AA",
        "#87CEFA", "#B8A1CF", "#E68AB8", "#DE3163", "#D94DFF", "#4169E1",
        "#008B8B", "#16982B", "#36BF36", "#FFD700", "#FF8033", "#FF4500",
        "#C0C0C0"
    ]

    # # Get range
    # result = get_handover_kpi_result.query.order_by(
    #     get_handover_kpi_result.sn.desc()).all()
    # curDate = ""
    # rangeSn = {}
    # for i in result:
    #     dateTag = i.related_date.split('-')[0] + i.related_date.split('-')[1]
    #     if curDate == '':
    #         curDate = dateTag
    #     elif curDate != dateTag:
    #         tmpList = rangeSn[curDate]
    #         tmpList.append(i.sn + 1)
    #         rangeSn[curDate] = tmpList
    #         curDate = dateTag
    #     if dateTag not in rangeSn.keys():
    #         rangeSn.setdefault(dateTag, [i.sn])
    # print(rangeSn)

    pplList = [
        'Aiden', 'Albert', 'Alex', 'Asky', 'Bayu', 'Bob', 'Benson', 'Cadalora',
        'Cyril', 'Daniel', 'Danny', 'Eric', 'Gary', 'Huck', 'Ivan', 'Keven',
        'Larry', 'Thurston', 'Rorschach'
    ]

    pplColor = {
        'Aiden': ['#FFCDD2', '#EF9A9A'],
        'Albert': ['#F8BBD0', '#F48FB1'],
        'Alex': ['#E1BEE7', '#CE93D8'],
        'Asky': ['#D1C4E9', '#B39DDB'],
        'Bayu': ['#C5CAE9', '#9FA8DA'],
        'Bob': ['#BBDEFB', '#90CAF9'],
        'Cadalora': ['#B3E5FC', '#81D4FA'],
        'Cyril': ['#B2EBF2', '#80DEEA'],
        'Daniel': ['#F0F4C3', '#E6EE9C'],
        'Danny': ['#FB8C00', '#FFE0B2'],
        'Eric': ['#DCEDC8', '#C5E1A5'],
        'Gary': ['#FFF9C4', '#FFF176'],
        'Huck': ['#FFECB3', '#FFE082'],
        'Ivan': ['#D7CCC8', '#BCAAA4'],
        'Keven': ['#FFCCBC', '#FFAB91'],
        'Larry': ['#C8E6C9', '#A5D6A7'],
        'Thurston': ['#CFD8DC', '#B0BEC5'],
        'Rorschach': ['#D32F2F', '#B71C1C'],
        'Default': ['#F5F5F5', '#E0E0E0']
    }

    rangeDict = {
        "2022": [1947],
        '202211': [6004],
        '202210': [6003, 5807],
        '202209': [5806, 5590],
        '202208': [5589, 4975],
        '202207': [4974, 4441],
        '202206': [4440, 3886],
        '202205': [3885, 3306],
        '202204': [3305, 2695],
        '202203': [2694, 2190],
        '202202': [2189, 2077],
        '202201': [2076, 1947],
        "2021": [1946, 143],
        '202112': [1946, 1803],
        '202111': [1802, 1633],
        '202110': [1632, 1543],
        '202109': [1542, 1412],
        '202108': [1411, 1247],
        '202107': [1246, 1105],
        '202106': [1104, 917],
        '202105': [916, 729],
        '202104': [728, 591],
        '202103': [590, 446],
        '202102': [445, 327],
        '202101': [326, 143],
        '202012': [142]
    }

    # filter by targetDate
    if targetDate == '2022':
        result = get_handover_kpi_result.query.filter(
            get_handover_kpi_result.sn >= rangeDict[targetDate][0]).all()
    elif targetDate == '202211':
        result = get_handover_kpi_result.query.filter(
            get_handover_kpi_result.sn >= rangeDict[targetDate][1]).all()
    elif len(rangeDict[targetDate]) == 1:
        result = get_handover_kpi_result.query.filter(
            get_handover_kpi_result.sn <= rangeDict[targetDate][0]).all()
    else:
        result = get_handover_kpi_result.query.filter(
            and_(
                get_handover_kpi_result.sn >= rangeDict[targetDate][1],
                get_handover_kpi_result.sn <= rangeDict[targetDate][0])).all()

    for i in result:
        if i.type == '1':
            handlerList = i.handler.split(',')
            for ii in handlerList:
                if ii not in tmpDict.keys():
                    if ii not in pplColor.keys():
                        tmpDict.setdefault(
                            ii,
                            dict(label=ii,
                                 data=1,
                                 backgroundColor=pplColor['Default'][0],
                                 borderColor=pplColor['Default'][1],
                                 borderWidth=2))
                    else:
                        tmpDict.setdefault(
                            ii,
                            dict(label=ii,
                                 data=1,
                                 backgroundColor=pplColor[ii][0],
                                 borderColor=pplColor[ii][1],
                                 borderWidth=2))
                else:
                    tmpDict[ii]['data'] += 1
        elif i.type == '2':
            # handler, one string
            handlerTs = i.handler
            if handlerTs not in tmpDictType2M.keys():
                if handlerTs not in pplColor.keys():
                    tmpDictType2M.setdefault(
                        handlerTs,
                        dict(label=handlerTs,
                             data=1,
                             backgroundColor=pplColor['Default'][0],
                             borderColor=pplColor['Default'][1],
                             borderWidth=2))
                else:
                    tmpDictType2M.setdefault(
                        handlerTs,
                        dict(label=handlerTs,
                             data=1,
                             backgroundColor=pplColor[handlerTs][0],
                             borderColor=pplColor[handlerTs][1],
                             borderWidth=2))
            else:
                tmpDictType2M[handlerTs]['data'] += 1
            # handler_secon, string to List
            if i.handler_second:
                try:
                    # stringDict
                    handlerSecondList = json.loads(i.handler_second)
                    for ii in handlerSecondList:
                        if ii not in tmpDictType2S.keys():
                            if ii not in pplColor.keys():
                                tmpDictType2S.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType2S.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType2S[ii]['data'] += 1
                except Exception as e:
                    # string
                    handlerSecondList = i.handler_second.split(',')
                    for ii in handlerSecondList:
                        if ii not in tmpDictType2S.keys():
                            if ii not in pplColor.keys():
                                tmpDictType2S.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType2S.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType2S[ii]['data'] += 1
            if i.participant and i.participant != 'null':
                try:
                    # stringDict
                    participantList = json.loads(i.participant)
                    for ii in participantList:
                        if ii not in tmpDictType2P.keys():
                            if ii not in pplColor.keys():
                                tmpDictType2P.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType2P.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType2P[ii]['data'] += 1
                except Exception as e:
                    # string
                    participantList = i.participant.split(',')
                    for ii in participantList:
                        if ii not in tmpDictType2P.keys():
                            if ii not in pplColor.keys():
                                tmpDictType2P.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType2P.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType2P[ii]['data'] += 1
        elif i.type == '3':
            # handler, one string
            handlerTs = i.handler
            if handlerTs not in tmpDictType3M.keys():
                if handlerTs not in pplColor.keys():
                    tmpDictType3M.setdefault(
                        handlerTs,
                        dict(label=handlerTs,
                             data=1,
                             backgroundColor=pplColor['Default'][0],
                             borderColor=pplColor['Default'][1],
                             borderWidth=2))
                else:
                    tmpDictType3M.setdefault(
                        handlerTs,
                        dict(label=handlerTs,
                             data=1,
                             backgroundColor=pplColor[handlerTs][0],
                             borderColor=pplColor[handlerTs][1],
                             borderWidth=2))
            else:
                tmpDictType3M[handlerTs]['data'] += 1
            # handler_secon, string to List
            if i.handler_second:
                try:
                    # stringDict
                    handlerSecondList = json.loads(i.handler_second)
                    for ii in handlerSecondList:
                        if ii not in tmpDictType3S.keys():
                            if ii not in pplColor.keys():
                                tmpDictType3S.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType3S.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType3S[ii]['data'] += 1
                except Exception as e:
                    # string
                    handlerSecondList = i.handler_second.split(',')
                    for ii in handlerSecondList:
                        if ii not in tmpDictType3S.keys():
                            if ii not in pplColor.keys():
                                tmpDictType3S.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType3S.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType3S[ii]['data'] += 1
            if i.participant and i.participant != 'null':
                try:
                    # stringDict
                    participantList = json.loads(i.participant)
                    for ii in participantList:
                        if ii not in tmpDictType3P.keys():
                            if ii not in pplColor.keys():
                                tmpDictType3P.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType3P.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType3P[ii]['data'] += 1
                except Exception as e:
                    # string
                    participantList = i.participant.split(',')
                    for ii in participantList:
                        if ii not in tmpDictType3P.keys():
                            if ii not in pplColor.keys():
                                tmpDictType3P.setdefault(
                                    ii,
                                    dict(
                                        label=ii,
                                        data=1,
                                        backgroundColor=pplColor['Default'][0],
                                        borderColor=pplColor['Default'][1],
                                        borderWidth=2))
                            else:
                                tmpDictType3P.setdefault(
                                    ii,
                                    dict(label=ii,
                                         data=1,
                                         backgroundColor=pplColor[ii][0],
                                         borderColor=pplColor[ii][1],
                                         borderWidth=2))
                        else:
                            tmpDictType3P[ii]['data'] += 1

    # total table
    tmpTotalDict = {}
    tmpTotalDict.setdefault('name', 'Total')
    tmpTotalDict.setdefault('handlerR', 0)
    tmpTotalDict.setdefault('handlerT', 0)
    tmpTotalDict.setdefault('handlerTs', 0)
    tmpTotalDict.setdefault('handlerTp', 0)
    tmpTotalDict.setdefault('handleraT', 0)
    tmpTotalDict.setdefault('handleraTs', 0)
    tmpTotalDict.setdefault('handleraTp', 0)
    tmpTotalDict.setdefault('score', 0)

    for y in pplList:
        tmpPPLDict = {}
        tmpPPLDict.setdefault('name', y)
        tmpScore = 0
        scoreList = []
        defineInsert = False
        if y in tmpDict.keys():
            tmpScore = tmpScore + tmpDict[y]['data']
            tmpTotalDict[
                'handlerR'] = tmpTotalDict['handlerR'] + tmpDict[y]['data']
            tmpPPLDict.setdefault('handlerR', tmpDict[y]['data'])
            scoreList.append(tmpDict[y]['data'])
            defineInsert = True
        else:
            tmpPPLDict.setdefault('handlerR', 0)
            scoreList.append(0)
        if y in tmpDictType2M.keys():
            tmpScore = tmpScore + tmpDictType2M[y]['data'] * 10
            tmpTotalDict['handlerT'] = tmpTotalDict[
                'handlerT'] + tmpDictType2M[y]['data']
            tmpPPLDict.setdefault('handlerT', tmpDictType2M[y]['data'])
            scoreList.append(tmpDictType2M[y]['data'])
            defineInsert = True
        else:
            tmpPPLDict.setdefault('handlerT', 0)
            scoreList.append(0)
        if y in tmpDictType2S.keys():
            tmpScore = tmpScore + tmpDictType2S[y]['data'] * 6
            tmpTotalDict['handlerTs'] = tmpTotalDict[
                'handlerTs'] + tmpDictType2S[y]['data']
            tmpPPLDict.setdefault('handlerTs', tmpDictType2S[y]['data'])
            scoreList.append(tmpDictType2S[y]['data'])
            defineInsert = True
        else:
            tmpPPLDict.setdefault('handlerTs', 0)
            scoreList.append(0)
        if y in tmpDictType2P.keys():
            tmpScore = tmpScore + tmpDictType2P[y]['data']
            tmpTotalDict['handlerTp'] = tmpTotalDict[
                'handlerTp'] + tmpDictType2P[y]['data']
            tmpPPLDict.setdefault('handlerTp', tmpDictType2P[y]['data'])
            scoreList.append(tmpDictType2P[y]['data'])
            defineInsert = True
        else:
            tmpPPLDict.setdefault('handlerTp', 0)
            scoreList.append(0)
        if y in tmpDictType3M.keys():
            tmpScore = tmpScore + tmpDictType3M[y]['data'] * 30
            tmpTotalDict['handleraT'] = tmpTotalDict[
                'handleraT'] + tmpDictType3M[y]['data']
            tmpPPLDict.setdefault('handleraT', tmpDictType3M[y]['data'])
            scoreList.append(tmpDictType3M[y]['data'])
            defineInsert = True
        else:
            tmpPPLDict.setdefault('handleraT', 0)
            scoreList.append(0)
        if y in tmpDictType3S.keys():
            tmpScore = tmpScore + tmpDictType3S[y]['data'] * 15
            tmpTotalDict['handleraTs'] = tmpTotalDict[
                'handleraTs'] + tmpDictType3S[y]['data']
            tmpPPLDict.setdefault('handleraTs', tmpDictType3S[y]['data'])
            scoreList.append(tmpDictType3S[y]['data'])
            defineInsert = True
        else:
            tmpPPLDict.setdefault('handleraTs', 0)
            scoreList.append(0)
        if y in tmpDictType3P.keys():
            tmpScore = tmpScore + tmpDictType3P[y]['data']
            tmpTotalDict['handleraTp'] = tmpTotalDict[
                'handleraTp'] + tmpDictType3P[y]['data']
            tmpPPLDict.setdefault('handleraTp', tmpDictType3P[y]['data'])
            scoreList.append(tmpDictType3P[y]['data'])
            defineInsert = True
        else:
            tmpPPLDict.setdefault('handleraTp', 0)
            scoreList.append(0)

        tmpPPLDict.setdefault('score', tmpScore)
        tmpPPLDict.setdefault('date', targetDate)

        if defineInsert:
            tmpListTotal.append(tmpPPLDict)
            tmpDictTotal.setdefault(y, dict(label=y, data=scoreList))

    tmpListTotal.append(tmpTotalDict)

    # type 1
    for x in tmpDict:
        tmpDict[x]['data'] = [tmpDict[x]['data']]
        datasetsList.append(tmpDict[x])

    # type 2 - handler
    for x in tmpDictType2M:
        tmpDictType2M[x]['data'] = [tmpDictType2M[x]['data']]
        datasetsTsList.append(tmpDictType2M[x])

    # type 2 - handler_second
    for x in tmpDictType2S:
        tmpDictType2S[x]['data'] = [tmpDictType2S[x]['data']]
        datasetsTssList.append(tmpDictType2S[x])

    # type 2 - participant
    for x in tmpDictType2P:
        tmpDictType2P[x]['data'] = [tmpDictType2P[x]['data']]
        datasetsTspList.append(tmpDictType2P[x])

    # type 3 - handler
    for x in tmpDictType3M:
        tmpDictType3M[x]['data'] = [tmpDictType3M[x]['data']]
        datasetsATsList.append(tmpDictType3M[x])

    # type 3 - handler_second
    for x in tmpDictType3S:
        tmpDictType3S[x]['data'] = [tmpDictType3S[x]['data']]
        datasetsATssList.append(tmpDictType3S[x])

    # type 3 - participant
    for x in tmpDictType3P:
        tmpDictType3P[x]['data'] = [tmpDictType3P[x]['data']]
        datasetsATspList.append(tmpDictType3P[x])

    # # type 2 total
    # for y in pplList:
    #     scoreList = []
    #     defineInsert = False
    #     if y in tmpDictType2M.keys():
    #         scoreList.append(tmpDictType2M[y]['data'])
    #         defineInsert = True
    #     else:
    #         scoreList.append(0)
    #     if y in tmpDictType2S.keys():
    #         scoreList.append(tmpDictType2S[y]['data'])
    #         defineInsert = True
    #     else:
    #         scoreList.append(0)
    #     if y in tmpDictType2P.keys():
    #         scoreList.append(tmpDictType2P[y]['data'])
    #         defineInsert = True
    #     else:
    #         scoreList.append(0)

    #     if defineInsert:
    #         tmpDictType2Total.setdefault(y, dict(label=y,data=scoreList))

    # datasetsTssList = [ tmpDictType2Total[yy] for yy in tmpDictType2Total ]

    # type 1
    returnDict1.setdefault('labels', ['handler'])
    returnDict1.setdefault('datasets', datasetsList)
    # type 2 - handler
    returnDict2.setdefault('labels', ['handler'])
    returnDict2.setdefault('datasets', datasetsTsList)
    # type 2 - second
    returnDict2_S.setdefault('labels', ['handler_second'])
    returnDict2_S.setdefault('datasets', datasetsTssList)
    # type 2 - participant
    returnDict2_P.setdefault('labels', ['participant'])
    returnDict2_P.setdefault('datasets', datasetsTspList)
    # type 3 - handler
    returnDict3.setdefault('labels', ['handler'])
    returnDict3.setdefault('datasets', datasetsATsList)
    # type 3 - second
    returnDict3_S.setdefault('labels', ['handler_second'])
    returnDict3_S.setdefault('datasets', datasetsATssList)
    # type 3 - participant
    returnDict3_P.setdefault('labels', ['participant'])
    returnDict3_P.setdefault('datasets', datasetsATspList)
    # # type 2 - total
    # returnDict2_S.setdefault('labels', ['handler', 'handler_second', 'participant'])
    # returnDict2_S.setdefault('datasets', datasetsTssList)

    returnList.append(returnDict1)
    returnList.append(returnDict2)
    returnList.append(returnDict2_S)
    returnList.append(returnDict2_P)
    returnList.append(returnDict3)
    returnList.append(returnDict3_S)
    returnList.append(returnDict3_P)
    returnList.append(tmpListTotal)
    returnList.append(tmpTotalDict)
    return jsonify(returnList)


@app.route('/dutycheck/ops')
def dutycheckops():
    try:
        resultQuery = requests.get('http://10.7.6.185:777/ops')
        resultContainer = resultQuery.json()
        print(resultContainer)
        returnDict = {}
        returnDict.setdefault('curShiftMember', eval(
            resultContainer['now_shift_members']))
        returnDict.setdefault('curShift', resultContainer['now_shift'])
        if resultContainer['now_shift'] == 'M':
            nextShift = 'A'
        elif resultContainer['now_shift'] == 'A':
            nextShift = 'N'
        else:
            nextShift = 'M'
        returnDict.setdefault('nextShift', nextShift)
        returnDict.setdefault('nextShiftMember', eval(
            resultContainer['next_shift_members']))
    except Exception as e:
        print(e)
        return 'get issue when access 10.7.6.185:777/ops', 503
    return returnDict
    return jsonify(returnDict)


@app.route('/kpi/queryrange')
def querydaterange():
    result = get_handover_kpi_result.query.order_by(
        get_handover_kpi_result.sn.desc()).all()
    curDate = ""
    rangeSn = {}
    for i in result:
        dateTag = i.related_date.split('-')[0] + i.related_date.split('-')[1]
        if curDate == '':
            curDate = dateTag
        elif curDate != dateTag:
            tmpList = rangeSn[curDate]
            tmpList.append(i.sn + 1)
            rangeSn[curDate] = tmpList
            curDate = dateTag
        if dateTag not in rangeSn.keys():
            rangeSn.setdefault(dateTag, [i.sn])
    print(rangeSn)
    return jsonify(rangeSn)


@app.route('/dba/get/otrs/all')
def dba_get_orts():
    # write the result here
    f = open('spider.txt', 'a')

    optionsSet = get_jsm_field_sets_sortOut.query.filter(get_jsm_field_sets_sortOut.contextId == 3).all()

    option_handler = [(x._value, { "accountId": x._id }) for x in optionsSet if x.fieldId == 'customfield_10274']
    option_handler_dict = {}
    for itemKey, itemValue in option_handler:
        option_handler_dict.setdefault(itemKey, itemValue)

    option_category = [(x._value, { "id": x._id }) for x in optionsSet if x.fieldId == 'customfield_10289']
    option_category_dict = {}
    for itemKey, itemValue in option_category:
        option_category_dict.setdefault(itemKey, itemValue)

    result = get_otrs_dba_ticket.query.filter(get_otrs_dba_ticket.status == 0).all()
    # result = get_otrs_dba_ticket.query.all()
    for i in result:
        payloadDict_create = {"serviceDeskId": "21", "requestTypeId": "493", 'requestFieldValues': {}}
        payloadDict_update_option = {'fields': {}}
        
        # summary
        print(f'START - YTS{i.ticketNumber} - {i.title}')
        f.write(f'START - YTS{i.ticketNumber} - {i.title} \n')
        payloadDict_create['requestFieldValues'].setdefault('summary', f'YTS{i.ticketNumber} - {i.title}')
        # description
        description_string = ''
        for item in json.loads(i.comments):
            tmp_comment_result = get_otrs_dba_ticket_comments.query.filter(get_otrs_dba_ticket_comments.sn == item).first()
            if tmp_comment_result.commentType == 1:
                description_string = description_string + f'{tmp_comment_result.content} at {tmp_comment_result.timestamp} by {tmp_comment_result.handler} \n'
        payloadDict_create['requestFieldValues'].setdefault('description', markdownify.markdownify(description_string[:-3], heading_style="ATX"))

        # category
        _category_valueList = []
        for item in json.loads(i.custom_category):
            _category_valueList.append(option_category_dict[f'{item}'])
        payloadDict_update_option['fields'].setdefault('customfield_10289', _category_valueList)
        # handler
        _handler_valueList = []
        for item in json.loads(i.custom_handler):
            _handler_valueList.append(option_handler_dict[f'{item}'])
        payloadDict_update_option['fields'].setdefault('customfield_10274', _handler_valueList)

        payload = json.dumps(payloadDict_create)
        payload_update = json.dumps(payloadDict_update_option)

        # for create
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
                    print(f'[OK] Create YTS{i.ticketNumber} to JSM')
                    f.write(f'[OK] Create YTS{i.ticketNumber} to JSM \n')
                    cur_issueId = res.json()['issueId']
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
            print(f'Failed, get error when create new ticket for {i.ticketNumber}')
            f.write(f'Failed, get error when create new ticket for {i.ticketNumber} \n')
            continue
    
        # for update the option
        url_update_option = f"https://ict888.atlassian.net/rest/api/3/issue/{cur_issueId}"

        defineDone = True
        counter = 1
        returnStatus = 'Success'

        while defineDone:
            try:
                response = requests.request("PUT",
                                            url_update_option,
                                            headers=prodHeaders,
                                            data=payload_update)
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
                f.write(e, '\n')
        
        print(f'[{returnStatus}] Update YTS{i.ticketNumber} option to JSM')
        f.write(f'[{returnStatus}] Update YTS{i.ticketNumber} option to JSM \n')

        # update the ticket status to close
        transition_list = [(11, 'In Progress'), (41, 'Complete Request'), (51, 'Close Ticket')]
        for (int_id, target_status) in transition_list:
            url_change_status = f'https://ict888.atlassian.net/rest/api/3/issue/{cur_issueId}/transitions'
            payload_change_statu = json.dumps({"transition": {"id": f'{int_id}'}})
            defineDone = True
            counter = 1
            updateStatus = 'Success'

            while defineDone:
                try:
                    response = requests.request("POST",
                                                url_change_status,
                                                data=payload_change_statu,
                                                headers=prodHeaders)
                    if response.status_code == 204:
                        defineDone = False
                    else:
                        counter += 1
                        print(response.status_code)
                except Exception as e:
                    print(e)
                    f.write(e, '\n')
                    counter += 1
                    if counter > 5:
                        updateStatus = 'Failed'
                        defineDone = False
                    else:
                        time.sleep(2)

            print(f'[{updateStatus}] YTS{i.ticketNumber} - change to {target_status}')
            f.write(f'[{updateStatus}] YTS{i.ticketNumber} - change to {target_status} \n')
        f.write(f'END - YTS{i.ticketNumber} \n')
    
    f.close()
    return 'ok'

@app.route('/rollback/jira')
def rollbackjiradesc():
    # jira prod header -
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
    # will use this routing to rollback all jira ticket email content
    # get all ops jira ticket ( email only )
    resultSet = get_jsm_ops_prod.query.filter(
        get_jsm_ops_prod.ticketStatus == 2,
        or_(get_jsm_ops_prod.jiraStatus == 121,
            get_jsm_ops_prod.jiraStatus == 71,
            get_jsm_ops_prod.jiraStatus == 6)).order_by(
                get_jsm_ops_prod.mapping).all()
    result_title_list = [ (i.issueId, origin_item.title, origin_item.mapping, origin_item.content_raw, i.issueKey) for origin_item in resultSet if origin_item.content_raw for i in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.sn == origin_item.mapping) ]

    status = []

    for i in result_title_list:
        print(f'== Start - {i[4]} - {i[1]} ==')
        url = f'https://ict888.atlassian.net/rest/api/2/issue/{i[0]}'
        payload = json.dumps({"fields": {"description": i[3]}})
        defineDone = True
        counter = 1
        while defineDone:
            try:
                response = requests.request("PUT",
                                            url,
                                            data=payload,
                                            headers=prodHeaders)
                if response.status_code == 204:
                    print(f'[{i[4]}] Done for update description to JSM')
                    status.append({'url': url, 'status': 'ok'})
                    defineDone = False
                else:
                    print(f'targetUrl={url}, JSM return status code={response.status_code}')
                    counter += 1
                    if counter > 5:
                        status.append({'url': url, 'status': 'failed'})
                        time.sleep(1)
                        defineDone = False
                    else:
                        time.sleep(2)
            except Exception as e:
                print(e)
                if counter > 5:
                    status.append({'url': url, 'status': 'failed'})
                    defineDone = False
                else:
                    counter += 1
        print(f'== End - {i[4]} - {i[1]} ==')

    filename = "output.json"
    with open(filename, "w") as f:
        f.write(json.dumps(status))

    return jsonify(result_title_list)

@app.route('/api/se101', methods=['GET', 'POST'])
def apiofse101():
    if request.method == 'GET':
        returnDict = request.args.to_dict()
        return jsonify(returnDict)
    elif request.method == 'POST':
        returnDict = {
        "yt0003":"Daniel Liu",
        "yt0016":"Cyril Rejas",
        "yt0022":"Huck Chen",
        "yt0028":"Albert Liu",
        "yt0037":"Keven Chang",
        "yt0060":"Gary Wu",
        "yt0062":"Allen Yu",
        "yt0063":"Danny Wu",
        "yt0066":"Cadalora Lin",
        "yt0068":"Ivan Chu",
        "yt0069":"Larry Tsou",
        "yt0079":"Thurston Chao",
        "yt0082":"Asky Huang",
        "yt0091":"Bob Lin",
        "yt0098":"Aiden Tan",
        "yt0101":"Bayu Agung Winursito",
        "yt0120":"Eric Kao",
        "yt0130":"Alex Lin",
        "yt0156":"Rorschach Ye"
        }
        try:
            data = request.get_json(silent=True)
            print(data)
            targetSn = data['sn']
            return f'Hi {returnDict[targetSn]},\n API Server got your post.'
        except Exception as e:
            return f'get error due to {e}'

@app.route('/openai/get_all_jira')
def openai_get_all_note():
    result = get_jsm_ops_prod.query.limit(5).all()
    result_list = []
    for i in result:
        temp_string = f'In the handover system, has one ticket, title is {i.title}, the detail as below:\n'
        temp_string += i.description
        result_list.append(temp_string)
    # result = get_handover_notes.query.order_by(get_handover_notes.sn.desc()).limit(1000).all()
    return jsonify(result_list)

@app.route('/larry/checkjira')
def larry_check_jira():
    result = get_jsm_ops_prod.query.filter(get_jsm_ops_prod.createdTime.between('2023-01-01', '2023-3-31')).order_by(get_jsm_ops_prod.sn).all()
    print(len(result))
    with open("2023Q1_Jira.csv", "w", newline="") as f:
        first_header = True
        for item in result:
            item = item.serialize_sort_out
            if first_header:
                writer = csv.DictWriter(f, fieldnames=item.keys())
                writer.writeheader()
                first_header = False
            writer.writerow(item)
    return 'ok'

@app.route('/larry/checknote')
def larry_check_note():
    result = get_handover_notes.query.filter(get_handover_notes.date.between('2022-07-01', '2023-09-30')).order_by(get_handover_notes.sn).all()
    with open("2022Q3_Note.csv", "w", newline="") as f:
        first_header = True
        for item in result:
            item = item.serialize_sort_out
            if first_header:
                writer = csv.DictWriter(f, fieldnames=item.keys())
                writer.writeheader()
                first_header = False
            writer.writerow(item)
    return 'ok'

context2 = ('./static/g-yt-k8s.crt', './static/g-yt-k8s.key')

if __name__ == '__main__':
    app.run('10.7.6.223',
            debug=True,
            port=9486,
            ssl_context=context2,
            threaded=True)
