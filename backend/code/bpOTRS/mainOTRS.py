from models import db, get_handover_otrs, get_handover_customer_status, get_handover_kpi_result, get_handover_otrs_closeTable, get_jsm_ops_comments, get_jsm_ops_prod, get_jsm_mapping_prod
from flask import Blueprint, jsonify, render_template, request, Response, send_from_directory
from shutil import copy
from difflib import *
import diff_match_patch as dmp_module
import os
import errno
import json
from sqlalchemy import and_
import requests
import time

app_mainOTRS = Blueprint('app_mainOTRS', __name__, static_folder='../static')

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

@app_mainOTRS.route('/query/<target>')
@app_mainOTRS.route('/query/<target>/<pattern>')
def ortsQuery(target=None, pattern=None):
    if target == 'all':
        containerList = []  # return this list with custom result
        # get last date and shift
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        # export time dict
        return_dict = dict(date=result.date.strftime("%Y%m%d"),
                           shift=result.shift)
        # query orts db table
        allResult = get_handover_otrs.query.filter(
            get_handover_otrs.date == return_dict['date'],
            get_handover_otrs.shift == return_dict['shift']).all()
        for i in allResult:
            # using this to store the this run dict
            assignObject = i.serialize
            checkKpiResultBySn = get_handover_kpi_result.query.filter(
                get_handover_kpi_result.origin_source == 'Ticket',
                get_handover_kpi_result.related_sn == i.sn).first()
            if checkKpiResultBySn:
                assignObject['kpi_result'] = checkKpiResultBySn.sn
            else:
                assignObject['kpi_result'] = 0
            # use this query to check if this ticket already assign close flag by user or not
            checkCloseTicketBySn = get_handover_otrs_closeTable.query.filter(
                get_handover_otrs_closeTable.ticket_sn == i.sn,
                get_handover_otrs_closeTable.ticket_action ==
                'Ticket closed').first()
            if checkCloseTicketBySn:
                assignObject['flagCloseTicket'] = True
            else:
                assignObject['flagCloseTicket'] = False
            containerList.append(assignObject)
        return jsonify(containerList)
    elif target == 'list':
        # for move order function
        result = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        return_dict = dict(date=result.date.strftime("%Y%m%d"),
                           shift=result.shift)
        tryToQueryByDateShift = get_handover_otrs.query.filter(
            get_handover_otrs.date == return_dict['date'],
            get_handover_otrs.shift == return_dict['shift'],
            get_handover_otrs.sequence != 99,
            get_handover_otrs.customer == pattern).all()
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
        querybySn = get_handover_otrs.query.filter(
            get_handover_otrs.sn == target).first()
        assignObject = querybySn.serialize
        checkKpiResultBySn = get_handover_kpi_result.query.filter(
            get_handover_kpi_result.origin_source == 'Ticket',
            get_handover_kpi_result.related_sn == querybySn.sn).first()
        if checkKpiResultBySn:
            assignObject['kpi_result'] = checkKpiResultBySn.sn
        else:
            assignObject['kpi_result'] = 0
        containerList.append(assignObject)
        return jsonify(containerList)


@app_mainOTRS.route('/update/status', methods=['GET', 'POST'])
def otrsUpdateStatus():
    front_data = request.get_json(silent=True)
    action = front_data['action']
    targetSn = front_data['targetSn']
    updateOTRStarget = get_handover_otrs.query.filter(
        get_handover_otrs.sn == targetSn).first()
    targetTicketNumber = 'YTS-' + str(updateOTRStarget.number)
    if action == 'edit':
        newEditor = front_data['newEditor']
        updateOTRStarget.update_by = newEditor
        updateOTRStarget.status = True
        db.session.commit()
        db.session.close()
        db.session.remove()
        return f'Change status to edit on DB ( {targetTicketNumber} )'
    elif action == 'cancel':
        # unlock isUnderEdit for this sn
        updateOTRStarget.status = False
        db.session.commit()
        db.session.close()
        db.session.remove()
        return f'Change status to normal on DB ( {targetTicketNumber} )'
    elif action == 'update':
        newEditor = front_data['newEditor']
        targetSn = front_data['targetSn']
        newSummary = front_data['summary']
        newUpdateSummary = front_data['updateSummary']
        updateOTRStarget.status = 0
        updateOTRStarget.summary = newSummary
        updateOTRStarget.update_summary = newUpdateSummary
        updateOTRStarget.update_by = newEditor
        db.session.commit()
        db.session.close()
        db.session.remove()
        return f'Done for update action on DB ( {targetTicketNumber} )'
    elif action == 'moveSequence':
        newPosition = front_data['newPosition']
        oldPosition = updateOTRStarget.sequence
        targetCustomer = front_data['targetZone']
        # get current list, need to order by sequence
        targetDate = updateOTRStarget.date
        targetShift = updateOTRStarget.shift
        curList = get_handover_otrs.query.filter(
            get_handover_otrs.date == targetDate,
            get_handover_otrs.shift == targetShift,
            get_handover_otrs.sequence != 99,
            get_handover_otrs.customer == targetCustomer).order_by(
                get_handover_otrs.sequence).all()

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
                subtractOne = get_handover_otrs.query.filter(
                    get_handover_otrs.sn == loopTargetSn).first()
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
                plusOne = get_handover_otrs.query.filter(
                    get_handover_otrs.sn == loopTargetSn).first()
                plusOne.sequence += 1
                db.session.commit()

        # adjust the target sn
        updateOTRStarget.sequence = newPosition
        db.session.commit()
        db.session.close()
        db.session.remove()
        return f'Done for moveSequence action on DB ( {targetTicketNumber} )'
    elif action == 'close':
        # add this ticket sn to close ticket table, it will trigger close on next shift
        targetDate = updateOTRStarget.date
        targetShift = updateOTRStarget.shift
        targetUpdateSummary = front_data['option']
        newEditor = front_data['editor']

        # check if user select the option
        if targetUpdateSummary:
            updateOTRStarget.update_summary = targetUpdateSummary
            updateOTRStarget.update_by = newEditor
            db.session.commit()

        isExist = get_handover_otrs_closeTable.query.filter(
            get_handover_otrs_closeTable.ticket_sn ==
            updateOTRStarget.sn).first()
        if isExist:
            isExist.ticket_action = 'Ticket closed'
        else:
            insertRecordToDb = get_handover_otrs_closeTable(
                date=targetDate,
                shift=targetShift,
                ticket_sn=updateOTRStarget.sn,
                ticket_action='Ticket closed')
            db.session.add(insertRecordToDb)
        db.session.commit()
        db.session.close()
        db.session.remove()
        return f'Done for make flag close action on DB ( {targetTicketNumber} )'
    elif action == 'rmClose':
        # rollback update_by and update_summary
        updateOTRStarget.update_by = None
        updateOTRStarget.update_summary = None
        db.session.commit()
        # remove target ticket sn on close ticket table
        queryBySn = get_handover_otrs_closeTable.query.filter(
            get_handover_otrs_closeTable.ticket_sn ==
            updateOTRStarget.sn).first()
        if queryBySn:
            db.session.delete(queryBySn)
            db.session.commit()
            db.session.close()
            db.session.remove()
        return f'Done for remove close flag action on DB ( {targetTicketNumber} )'
    elif action == 'rollback':
        targetCustomer = front_data['targetZone']
        targetDate = updateOTRStarget.date
        targetShift = updateOTRStarget.shift
        curList = get_handover_otrs.query.filter(
            get_handover_otrs.date == targetDate,
            get_handover_otrs.shift == targetShift,
            get_handover_otrs.sequence != 99,
            get_handover_otrs.customer == targetCustomer).all()
        maxSequence = max([x.sequence for x in curList])
        updateOTRStarget.sequence = maxSequence + 1
        db.session.commit()
        db.session.close()
        db.session.remove()
        return f'Done for rollback action on DB ( {targetTicketNumber} )'
    else:
        return 'else ok'


# traceroute log, new function by plugin dmp_module
@app_mainOTRS.route('/traceLog/<targetNumber>')
def otrsTraceLog(targetNumber):

    print(f'targetNumber = {targetNumber}')

    returnDict = {}
    containerUpdateSummaryList = []
    containerCreateSummaryDict = {}
    containerAttachmentList = []

    # get all results by SN, without order
    queryTicketByNumber = get_handover_otrs.query.filter(
        get_handover_otrs.number == targetNumber).all()

    # check how long has been created for this note
    if len(queryTicketByNumber) % 3 == 0:
        returnDict['dayCounter'] = str(int(
            len(queryTicketByNumber) / 3)) + ' days'
    elif len(queryTicketByNumber) % 3 == 1:
        returnDict['dayCounter'] = str(int(
            len(queryTicketByNumber) / 3)) + ' days and one shift'
    else:
        returnDict['dayCounter'] = str(int(
            len(queryTicketByNumber) / 3)) + ' days and two shift'

    # compare container - two pointer.
    previousSummaryLen = len(queryTicketByNumber[0].summary)
    if (queryTicketByNumber[0].update_summary
        ) and queryTicketByNumber[0].update_summary != 'New':
        previousUpdateSummaryLen = len(queryTicketByNumber[0].update_summary)
    else:
        previousUpdateSummaryLen = 0
    previousSummary = queryTicketByNumber[0].summary
    previousDate = queryTicketByNumber[0].date
    previousShift = queryTicketByNumber[0].shift
    checkList = []

    for (index, value) in enumerate(queryTicketByNumber):
        # means summary is diff between current summary and previous summary
        # print(str(value.date) + '-' + value.shift)
        # print(f'previousSummaryLen = {previousSummaryLen}')
        # print(f'previousUpdateSummaryLen = {previousUpdateSummaryLen}')
        # print('curSummaryLen', len(value.summary))
        if (previousSummaryLen + previousUpdateSummaryLen) != len(
                value.summary):
            if value.update_by:
                dmp = dmp_module.diff_match_patch()
                # create diffs by diff_main
                diff = dmp.diff_main(previousSummary, value.summary)
                # using diff_cleanupEfficiency
                dmp.diff_cleanupEfficiency(diff)
                # return HTML
                returnHtml = dmp.diff_prettyHtml(diff)
                checkList.append([
                    str(value.date) + '-' + value.shift + ' / ' +
                    value.update_by, returnHtml,
                    str(previousDate) + '-' + previousShift, previousSummary,
                    str(value.date) + '-' + value.shift, value.summary
                ])
        previousSummaryLen = len(value.summary)
        if (value.update_summary) and (value.update_summary != 'New'):
            previousUpdateSummaryLen = len(value.update_summary)
        else:
            previousUpdateSummaryLen = 0
        previousSummary = value.summary
        previousDate = value.date
        previousShift = value.shift
        if value.update_summary == 'New':
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
    returnDict['diff'] = checkList

    return returnDict


@app_mainOTRS.route('/kpi/query/<targetKpiSn>')
def otrsKpiQuery(targetKpiSn):
    resultBySn = get_handover_kpi_result.query.filter(
        get_handover_kpi_result.sn == targetKpiSn).first()
    return resultBySn.serialize


# MTN
@app_mainOTRS.route('/mtn/update', methods=['GET', 'POST'])
def otrsMtnUpdate():
    front_data = request.get_json(silent=True)
    targetSn = front_data['targeOTRSTicketSn']
    if front_data['curStatus']:
        updateMTNStatus = 1
    else:
        updateMTNStatus = 0
    resultByTicketSn = get_handover_otrs.query.filter(
        get_handover_otrs.sn == targetSn).first()
    resultByTicketSn.maintenance = updateMTNStatus
    db.session.commit()
    db.session.close()
    db.session.remove()
    return 'ok'


@app_mainOTRS.route('/jsm/get/allcomments/<targetSn>')
def jsmGetAllComments(targetSn):
    resultJsm = get_jsm_ops_prod.query.filter(
        get_jsm_ops_prod.sn == targetSn).first()
    commentList = json.loads(resultJsm.comments)
    returnList = []
    for i in commentList:
        try:
            result = get_jsm_ops_comments.query.filter(
                get_jsm_ops_comments.sn == i).first()
            returnList.append(result.serialize)
        except Exception as e:
            print(e)
            print(f'get issue for comment id - {i}')
    return jsonify(returnList)


@app_mainOTRS.route('/jsm/get/allTicketSn/<comefrom>')
def jsmGetAllTicketSn(comefrom):
    resultSet = get_jsm_ops_prod.query.filter(
        and_(get_jsm_ops_prod.jiraStatus != 121,
             get_jsm_ops_prod.jiraStatus != 71,
             get_jsm_ops_prod.jiraStatus != 6,
             get_jsm_ops_prod.ticketStatus != 99)).all()

    # collect the ticket information
    returnList = []
    for i in resultSet:
        if i.sn != int(comefrom):
            mappingResult = get_jsm_mapping_prod.query.filter(
                get_jsm_mapping_prod.sn == i.mapping).first()
            returnList.append(
                dict(color='secondary',
                     value=i.sn,
                     label=f'{mappingResult.issueKey} - {i.title}'))
    return jsonify(returnList)


@app_mainOTRS.route('/jsm/merge', methods=['GET', 'POST'])
def jsmMerge():
    front_data = request.get_json(silent=True)
    print(front_data)
    handler = front_data['handler']
    targetSn = front_data['targetSn']
    sourceSn = front_data['sourceSn']
    sourceTitle = front_data['sourceTitle']
    sourceIssueKey = front_data['sourceIssueKey']
    # add the source ticket sn into target ticket relations list
    # - check the list first
    try:
        mergeTarget = get_jsm_ops_prod.query.filter(
            get_jsm_ops_prod.sn == targetSn).first()
        # 1 - update the relations on targetJSM
        if mergeTarget.relations:
            tmp_relation_list = json.loads(mergeTarget.relations)
            if sourceSn in tmp_relation_list:
                # return 'This ticket had been merged, please refresh the handover system', 200
                print('hit return 200, duplicate')
            else:
                tmp_relation_list.append(sourceSn)
            mergeTarget.relations = json.dumps(tmp_relation_list)
        else:
            mergeTarget.relations = json.dumps([sourceSn])
        # 2 - update the comment history for targetJSM
        mergeMapping = get_jsm_mapping_prod.query.filter(
            get_jsm_mapping_prod.sn == mergeTarget.mapping).first()
        targetTicket = f'{mergeMapping.issueKey} - {mergeTarget.title}'
        addOneRow = get_jsm_ops_comments(
            issueKey=mergeMapping.issueKey,
            handler=handler,
            content=f'<span class="text-blue-14">{sourceIssueKey} - {sourceTitle}</span> has been merged into this ticket',
            commentType=2
        )
        db.session.add(addOneRow)
        db.session.commit()
        db.session.refresh(addOneRow)
        commentDbSn = addOneRow.sn
        # 3 - update the comment list on targetJSM
        tmp_comment_List = json.loads(mergeTarget.comments)
        tmp_comment_List.append(commentDbSn)
        mergeTarget.comments = json.dumps(tmp_comment_List)
        db.session.commit()
        db.session.close()
    except Exception as e:
        print(e)
        return f'Get issue when update the target JSM backend, alert details - {e}', 500

    # update source JSM status to close ( cloud )
    transition_list = [(31, 'Cancel Request'), (51, 'Close Ticket')]
    for (int_id, target_status) in transition_list:
        url_change_status = f'https://ict888.atlassian.net/rest/api/3/issue/{sourceIssueKey}/transitions'
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
                    if counter > 5:
                        updateStatus = 'Failed'
                        defineDone = False
                    else:
                        counter += 1
                        print(response.status_code)
            except Exception as e:
                print(e)
                counter += 1
                if counter > 5:
                    updateStatus = 'Failed'
                    defineDone = False
                else:
                    time.sleep(2)

        print(f'[{updateStatus}] {sourceIssueKey} - change to {target_status}')

    if updateStatus != 'Success':
        return f'Get issue when update source JSM status to close ( cloud )', 500

    # update the comment on JSM
    url = f"https://ict888.atlassian.net/rest/api/2/issue/{sourceIssueKey}/comment"

    try:
        payload = json.dumps({
            "visibility": {
                "type": "role",
                "value": "Service Desk Team"
            },
            "body": f'(Update by {handler})This ticket has been merged to {targetTicket}'
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
                    f'[{sourceIssueKey}] Done for update comment')
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

    # Update the comment for source JSM
    try:
        # 1 - update the comment history for source
        addOneRowSource = get_jsm_ops_comments(
            issueKey=sourceIssueKey,
            commentType=2,
            handler=handler,
            content=f'This ticket merged to <span class="text-blue-14">{targetTicket}</span>, <span class="text-red">ticket closed</span>'
        )
        db.session.add(addOneRowSource)
        db.session.commit()
        db.session.refresh(addOneRowSource)
        commentDbSourceSn = addOneRowSource.sn
        # 2 - update the comment list on targetJSM
        sourceJSM = get_jsm_ops_prod.query.filter(
            get_jsm_ops_prod.sn == sourceSn).first()
        sourceJSM.jiraStatus = 6
        tmp_source_comment_list = json.loads(sourceJSM.comments)
        tmp_source_comment_list.append(commentDbSourceSn)
        sourceJSM.comments = json.dumps(tmp_source_comment_list)
        db.session.commit()
        db.session.close()
    except Exception as e:
        print(e)
        return f'Get issue when update the source JSM backend, alert details - {e}', 500

    return targetTicket


@app_mainOTRS.route('/jsm/get/related/<source_sn>')
def jsm_get_related_sn_details(source_sn):
    source_result = get_jsm_ops_prod.query.filter(
        get_jsm_ops_prod.sn == source_sn).first()
    returnList = []
    if source_result.relations:
        for i in json.loads(source_result.relations):
            # ( originsn, ticket number - ticket title, ticket type, content )
            tmp = [(i, f'{y.issueKey} - {x.title}', x.ticketStatus, x.description, x.content_html, y.issueUrl) for x in get_jsm_ops_prod.query.filter(get_jsm_ops_prod.sn == i) for y in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.sn == x.mapping)]
            returnList.append(tmp[0])
        return jsonify(returnList)
    else:
        return jsonify(returnList)
