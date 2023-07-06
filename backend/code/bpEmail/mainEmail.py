from email.policy import default
from enum import Flag
from re import template

from sqlalchemy import false, true, and_
from models import db, get_customer_status_note, get_handover_customer_status, get_handover_health_map, get_handover_notes, get_handover_otrs, get_handover_jira_ticket, get_handover_ticket_mtn_mapping, get_handover_otrs_closeTable, get_handover_notes_attachment, get_handover_checkbox, get_handover_shift_table, get_handover_jira_ticket_sysinfo, get_jsm_ops_prod, get_jsm_mapping_prod, get_jsm_ops_comments
from flask import Blueprint, jsonify, render_template, request, Response, send_from_directory, current_app, url_for
from flask_mail import Mail, Message
import os
import docx
from htmldocx import HtmlToDocx
import json
import collections
import requests
import datetime
import diff_match_patch as dmp_module

app_mainEmail = Blueprint('app_mainEmail', __name__)


class GenerateEmail():
    # class default argument
    def __init__(self, query_date, query_shift):
        self.query_date = query_date
        self.query_shift = query_shift

    # @staticmethod
    # @classmethod
    def getServiceStatus(self):
        result = get_handover_customer_status.query.filter(
            get_handover_customer_status.date == self.query_date,
            get_handover_customer_status.shift == self.query_shift).first()
        buDict = collections.OrderedDict()
        for key, value in result.serialize.items():
            if value == 'Green':
                if key == '_188A':
                    buDict['188A'] = value
                else:
                    buDict[key] = value
            else:
                targetDate = result.date
                targetShift = result.shift
                queryCustomerStatusNote = get_customer_status_note.query.filter(
                    get_customer_status_note.date == targetDate,
                    get_customer_status_note.shift == targetShift).all()
                print(f'queryCustomerStatusNote = {queryCustomerStatusNote}')
                eventListContainer = []
                for key1, value1 in enumerate(queryCustomerStatusNote):
                    print(value1.serialize)
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
                if key == '_188A':
                    buDict['188A'] = ['abnormal', eventListContainer]
                else:
                    buDict[key] = ['abnormal', eventListContainer]

        tableList = []
        tableList.append(
            '<tbody><tr><th style="width:100%" class="topHead" colspan="3">BU</th></tr>'
        )
        tableList.append(
            '<tr><th style="width:25%">Name</th><th style="width:25%">Status</th><th style="width:50%">Detail</th></tr>'
        )
        for k, v in dict(buDict).items():
            tableList.append('<tr>')
            tableList.append(f'<td>{k}</td>')
            if v == 'Green':
                tableList.append(
                    f'<td><font color="#00BB00"><b>Good</b></font></td>')
                tableList.append(f'<td></td>')
            else:
                tableList.append(
                    f'<td><font color="#F75000"><b>Abnormal</b></font></td>')
                tableList.append(f'<td>{v}</td>')

            tableList.append('</tr>')
        tableList.append('</tbody>')
        htmltable = "".join(tableList)
        return htmltable

    def getMonitoringStatus(self):
        result = get_handover_health_map.query.filter(
            get_handover_health_map.date == self.query_date,
            get_handover_health_map.shift == self.query_shift).first()
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

        tableList = []
        tableList.append(
            '<tbody><tr><th class="topHead" colspan="3" style="width:100%">Monitoring System</th></tr>'
        )
        tableList.append(
            '<tr><th style="width:25%"">Name</th><th style="width:25%">Status</th><th style="width:50%">Detail</th></tr>'
        )
        for x in rebuildList:
            k = list(x.keys())[0]
            v = list(x.values())[0]['status']
            detail = list(x.values())[0]['detail']
            tableList.append('<tr>')
            tableList.append(f'<td>{k}</td>')
            # check the status
            if v == 'Good':
                tableList.append(
                    f'<td><font color="#00BB00"><b>Good</b></font></td>')
            else:
                tableList.append(
                    f'<td><font color="#F75000"><b>Abnormal</b></font></td>')
            # check the detail
            if detail == 'null':
                tableList.append(f'<td></td>')
            else:
                tableList.append(f'<td>{detail}</td>')
        tableList.append('</tr>')
        tableList.append('</tbody>')
        htmltable = "".join(tableList)
        return htmltable

    @staticmethod
    def getICPStatus():
        result = requests.get('http://10.7.6.205:5015/axios_querying_icp_db/')
        tableList = []
        tableList.append(
            '<tbody><tr><th class="topHead" colspan="3" style="width:100%">ICP</th></tr>'
        )
        tableList.append(
            '<tr><th style="width:25%">Name</th><th style="width:25%">Status</th><th style="width:50%">Detail</th></tr>'
        )
        for i in result.json():
            tableList.append('<tr>')
            targetDomain = i['each_domain']
            targetIcpNumber = i['icp_number']
            tableList.append(f'<td>{targetDomain}</td>')
            if targetIcpNumber != 'no icp':
                tableList.append(
                    f'<td><font color="#00BB00"><b>Good</b></font></td>')
                tableList.append(f'<td>{targetIcpNumber}</td>')
            else:
                tableList.append(
                    f'<td><font color="#F75000"><b>Abnormal</b></font></td>')
                tableList.append(f'<td>Can not find the ICP license</td>')
            tableList.append('</tr>')
        tableList.append('</tbody>')
        return "".join(tableList)

    def getSummaryNote(self):
        result = get_handover_notes.query.filter(
            get_handover_notes.date == self.query_date,
            get_handover_notes.shift == self.query_shift).all()
        # check the new note, and append the html tag li
        newCounterList = [(x.customer, x.sequence) for x in result
                          if (x.update_summary == 'New') and (x.sequence != 99)
                          ]
        newCounter = str(len(newCounterList))
        if newCounter != '0':
            newCounter = ''
            for i in newCounterList:
                newCounter = newCounter + f'<li> Note {i[1]} - ' + i[
                    0] + '</li>'
        # check the del note, and append the html tag li
        deleteCounterList = [x.customer for x in result if x.sequence == 99]
        deleteCounter = str(len(deleteCounterList))
        if deleteCounter != '0':
            deleteCounter = ''
            for i in deleteCounterList:
                deleteCounter = deleteCounter + f'<li> Note - ' + i + '</li>'
        # check the update note, and append the html tag li
        updateCounterList = [
            (x.customer, x.sequence) for x in result
            if (x.update_summary) and (x.update_summary != 'New')
        ]
        updateCounter = str(len(updateCounterList))
        if updateCounter != '0':
            updateCounter = ''
            for i in updateCounterList:
                updateCounter = updateCounter + f'<li> Note {i[1]} - ' + i[
                    0] + '</li>'
        totalCounter = len(result) - len(deleteCounterList)
        # print(f'total notes: {totalCounter}')
        # print(f'new notes: {newCounter}')
        # print(f'updated notes: {updateCounter}')
        # print(f'delete notes: {deleteCounter}')
        # <tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr>
        resultList = [
            'Note', totalCounter, newCounter, updateCounter, deleteCounter
        ]
        updateHtmlList = [f'<td>{x}</td>' for x in resultList]
        # updateHtmlList = [f'<td style="border:1px solid black;">{x}</td>' for x in resultList]
        updateHtmlStr = "".join(updateHtmlList)
        return f'<tr>{updateHtmlStr}</tr>'

    def getSummaryOTRS(self):
        result = get_handover_otrs.query.filter(
            get_handover_otrs.date == self.query_date,
            get_handover_otrs.shift == self.query_shift).all()
        closeResult = get_handover_otrs_closeTable.query.filter(
            get_handover_otrs_closeTable.date == self.query_date,
            get_handover_otrs_closeTable.shift == self.query_shift,
            get_handover_otrs_closeTable.ticket_action ==
            'Ticket closed').all()
        newCounterList = [(x.number, x.subject) for x in result
                          if x.update_summary == 'New']
        newCounter = str(len(newCounterList))
        if newCounter != '0':
            newCounter = ''
            for i in newCounterList:
                newCounter = newCounter + f'<li> YTS{i[0]}-' + i[1] + '</li>'
        deleteCounterList = [x.ticket_sn for x in closeResult]
        deleteCounter = str(len(deleteCounterList))
        if deleteCounter != '0':
            deleteCounter = ''
            for i in deleteCounterList:
                queryByOTRSbySn = get_handover_otrs.query.filter(
                    get_handover_otrs.sn == i).first()
                deleteCounter = deleteCounter + f'<li> YTS{queryByOTRSbySn.number}-' + queryByOTRSbySn.subject + '</li>'
        updateCounterList = [
            (x.number, x.subject) for x in result
            if (x.update_summary) and (x.update_summary != 'New')
        ]
        updateCounter = str(len(updateCounterList))
        if updateCounter != '0':
            updateCounter = ''
            for i in updateCounterList:
                updateCounter = updateCounter + f'<li> YTS{i[0]}-' + i[
                    1] + '</li>'
        totalCounter = len(result) - len(deleteCounterList)
        # print(f'total tickets: {totalCounter}')
        # print(f'new tickets: {newCounter}')
        # print(f'updated tickets: {updateCounter}')
        # print(f'delete tickets: {deleteCounter}')
        resultList = [
            'OTRS', totalCounter, newCounter, updateCounter, deleteCounter
        ]
        updateHtmlList = [f'<td>{x}</td>' for x in resultList]
        updateHtmlStr = "".join(updateHtmlList)
        return f'<tr>{updateHtmlStr}</tr>'

    def getSummaryJIRA(self):
        replaceDateFormat = self.query_date.replace('-', '')
        result = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.date == replaceDateFormat,
            get_handover_jira_ticket.shift == self.query_shift).all()
        newCounter = len([x for x in result if x.flagTicketStatus == 0])
        deleteCounter = len([x for x in result if x.flagTicketStatus == 3])
        updateCounter = len([
            x for x in result
            if (x.flagTicketStatus == 1) and (x.updateSummary)
        ])
        totalCounter = len(result) - deleteCounter
        # print(f'total jira tickets: {totalCounter}')
        # print(f'new jira tickets: {newCounter}')
        # print(f'updated jira tickets: {updateCounter}')
        # print(f'delete jira tickets: {deleteCounter}')
        resultList = [
            'JIRA', totalCounter, newCounter, updateCounter, deleteCounter
        ]
        updateHtmlList = [f'<td>{x}</td>' for x in resultList]
        updateHtmlStr = "".join(updateHtmlList)
        return f'<tr>{updateHtmlStr}</tr>'

    def getMtnOTRS(self):
        # curShift datetime string to timeObject
        shiftTimeMapping = {'M': '07:30', 'A': '15:00', 'N': '23:00'}
        # use the stime_obj to get etime_obj, why, avoid change date
        stime_time = shiftTimeMapping[self.query_shift]
        shift_stime = f'{self.query_date} {stime_time}'
        shift_stime_obj = datetime.datetime.strptime(shift_stime,
                                                     "%Y-%m-%d %H:%M")
        shift_stime_unix = datetime.datetime.timestamp(shift_stime_obj)
        shift_etime_unix = shift_stime_unix + 32400
        shift_etime_obj = datetime.datetime.fromtimestamp(shift_etime_unix)

        # print(f'start - {shift_stime_obj}')
        # print(f'end - {shift_etime_obj}')

        # Refer this - https://stackoverflow.com/questions/10747974/how-to-check-if-the-current-time-is-in-range-in-python
        def time_in_range(start, end, x):
            """Return true if x is in the range [start, end]"""
            if start <= end:
                return start <= x <= end
            else:
                return start <= x or x <= end

        # get all OTRS mtn ticket
        result = get_handover_otrs.query.filter(
            get_handover_otrs.date == self.query_date,
            get_handover_otrs.shift == self.query_shift,
            get_handover_otrs.maintenance == 1).all()


        # filter ticket number to list
        mtnList = [(x.number, x.subject, x.summary, x.update_summary, x.update_by) for x in result]
        
        # store and for loop later
        onGoingList = []
        finishedList = []
        comingSoonList = []

        # check on mapping
        for i in mtnList:
            searchByNumber = get_handover_ticket_mtn_mapping.query.filter(
                get_handover_ticket_mtn_mapping.relatedJiraIssueId ==
                i[0]).first()
            # print(i[0])
            if searchByNumber:
                # print(searchByNumber.endTime)
                # means created by ndhs
                ## filter ongoing - ms in shift range, but me not in the shift range
                if (time_in_range(
                        shift_stime_obj, shift_etime_obj,
                        searchByNumber.startTime)) and (time_in_range(
                            shift_stime_obj, shift_etime_obj,
                            searchByNumber.endTime) == False):
                    onGoingList.append([
                        i, searchByNumber.startTime, searchByNumber.endTime,
                        searchByNumber._type
                    ])
                    # print('Ongoing:', i[0], i[1]) # do the html table later
                ## ms - shift s - shift e - me
                elif (time_in_range(searchByNumber.startTime,
                                    searchByNumber.endTime, shift_etime_obj)):
                    onGoingList.append([
                        i, searchByNumber.startTime, searchByNumber.endTime,
                        searchByNumber._type
                    ])
                ## filter finished - ms in shift range, but me not in the shift range
                elif (time_in_range(shift_stime_obj, shift_etime_obj,
                                    searchByNumber.endTime)):
                    finishedList.append([
                        i, searchByNumber.startTime, searchByNumber.endTime,
                        searchByNumber._type
                    ])
                    # print('Finished:', i[0], i[1])
                ## filter coming soon, if the result less 86400 sec as 24 hours
                elif 0 <= (
                        datetime.datetime.timestamp(searchByNumber.startTime) -
                        datetime.datetime.timestamp(shift_etime_obj)) <= 86400:
                    comingSoonList.append([
                        i, searchByNumber.startTime, searchByNumber.endTime,
                        searchByNumber._type
                    ])
                    # print('Coming soon', i[0], i[1])

        # build the html table
        returnList = []
        if len(onGoingList) > 0:
            counter = len(onGoingList)
            returnList.append(
                f'<tr class="topHead"><th colspan="5" width="100%">Ongoing: {counter}</th></tr>'
            )
            returnList.append(
                f'<tr><th width="25%">TicketName</th><th width="10%">Type</th><th width="10%">StartTime</th><th width="10%">EndTime</th><th width="45%">Detail</th></tr>'
            )
            for i in onGoingList:
                returnList.append('<tr>')
                returnList.append(f'<td>YTS{i[0][0]}<br>{i[0][1]}</td>')
                returnList.append(f'<td>{i[3]}</td>')
                returnList.append(f'<td>{i[1]}</td>')
                returnList.append(f'<td>{i[2]}</td>')
                returnList.append('<td>')
                if i[0][3] == 'New':
                    returnList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Create by {i[0][4]}</b></span></div>'
                    )
                    returnList.append(f'<div>{i[0][2]}</div>')
                elif (i[0][3] != None) and (i[0][3] != ''):
                    returnList.append(f'<div><b>Current status:</b></div>')
                    returnList.append(f'<div>{i[0][2]}</div>')
                    returnList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Update by {i[0][4]}</b></span> {i[0][3]}</div>'
                    )
                else:
                    returnList.append(f'<div>{i[0][2]}</div>')
                returnList.append('</td>')
                returnList.append('</tr>')
        else:
            returnList.append(
                '<tr class="topHead" colspan="5"><th width="100%" colspan="5">Ongoing: 0</th></tr>'
            )

        if len(finishedList) > 0:
            counter = len(finishedList)
            returnList.append(
                f'<tr class="topHead"><th colspan="5" width="100%">Finished: {counter}</th></tr>'
            )
            returnList.append(
                f'<tr><th width="25%">TicketName</th><th width="10%">Type</th><th width="10%">StartTime</th><th width="10%">EndTime</th><th width="45%">Detail</th></tr>'
            )
            for i in finishedList:
                returnList.append('<tr>')
                returnList.append(f'<td>YTS{i[0][0]}<br>{i[0][1]}</td>')
                returnList.append(f'<td>{i[3]}</td>')
                returnList.append(f'<td>{i[1]}</td>')
                returnList.append(f'<td>{i[2]}</td>')
                returnList.append('<td>')
                if i[0][3] == 'New':
                    returnList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Create by {i[0][4]}</b></span></div>'
                    )
                    returnList.append(f'<div>{i[0][2]}</div>')
                elif (i[0][3] != None) and (i[0][3] != ''):
                    returnList.append(f'<div><b>Current status:</b></div>')
                    returnList.append(f'<div>{i[0][2]}</div>')
                    returnList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Update by {i[0][4]}</b></span> {i[0][3]}</div>'
                    )
                else:
                    returnList.append(f'<div>{i[0][2]}</div>')
                returnList.append('</td>')
                returnList.append('</tr>')
        else:
            returnList.append(
                '<tr class="topHead" colspan="5"><th width="100%" colspan="5">Finished: 0</th></tr>'
            )

        if len(comingSoonList) > 0:
            counter = len(comingSoonList)
            returnList.append(
                f'<tr class="topHead"><th colspan="5" width="100%">Coming soon within 24 hours: {counter}</th></tr>'
            )
            returnList.append(
                f'<tr><th width="25%">TicketName</th><th width="10%">Type</th><th width="10%">StartTime</th><th width="10%">EndTime</th><th width="45%">Detail</th></tr>'
            )
            for i in comingSoonList:
                returnList.append('<tr>')
                returnList.append(f'<td>YTS{i[0][0]}<br>{i[0][1]}</td>')
                returnList.append(f'<td>{i[3]}</td>')
                returnList.append(f'<td>{i[1]}</td>')
                returnList.append(f'<td>{i[2]}</td>')
                returnList.append('<td>')
                if i[0][3] == 'New':
                    returnList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Create by {i[0][4]}</b></span></div>'
                    )
                    returnList.append(f'<div>{i[0][2]}</div>')
                elif (i[0][3] != None) and (i[0][3] != ''):
                    returnList.append(f'<div><b>Current status:</b></div>')
                    returnList.append(f'<div>{i[0][2]}</div>')
                    returnList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Update by {i[0][4]}</b></span> {i[0][3]}</div>'
                    )
                else:
                    returnList.append(f'<div>{i[0][2]}</div>')
                returnList.append('</td>')
                returnList.append('</tr>')
        else:
            returnList.append(
                '<tr class="topHead" colspan="5"><th width="100%" colspan="5">Coming soon within 24 hours: 0</th></tr>'
            )

        return "".join(returnList)

    def getMtnJira(self):
        # curShift datetime string to timeObject
        shiftTimeMapping = {'M': '07:30', 'A': '15:00', 'N': '23:00'}
        # use the stime_obj to get etime_obj, why, avoid change date
        stime_time = shiftTimeMapping[self.query_shift]
        shift_stime = f'{self.query_date} {stime_time}'
        shift_stime_obj = datetime.datetime.strptime(shift_stime,
                                                     "%Y-%m-%d %H:%M")
        shift_stime_unix = datetime.datetime.timestamp(shift_stime_obj)
        shift_etime_unix = shift_stime_unix + 32400
        shift_etime_obj = datetime.datetime.fromtimestamp(shift_etime_unix)

        # Refer this - https://stackoverflow.com/questions/10747974/how-to-check-if-the-current-time-is-in-range-in-python
        def time_in_range(start, end, x):
            """Return true if x is in the range [start, end]"""
            if start <= end:
                return start <= x <= end
            else:
                return start <= x or x <= end

        # store and for loop later - for jira
        onGoingListJsm = []
        finishedListJsm = []
        comingSoonListJsm = []

        result_jsm = get_jsm_ops_prod.query.filter(
            and_(get_jsm_ops_prod.jiraStatus != 121,
                 get_jsm_ops_prod.jiraStatus != 71,
                 get_jsm_ops_prod.jiraStatus != 6,
                 get_jsm_ops_prod.mtn == 1)).all()

        
        mtnList2 = [ (x.sn, x.title, y.issueId, y.issueKey, z.startTime, z.endTime, z._type, x.description, json.loads(x.comments)[-1] ) for x in result_jsm for y in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.sn == x.mapping).all() for z in get_handover_ticket_mtn_mapping.query.filter(get_handover_ticket_mtn_mapping.relatedJiraIssueId == y.issueId).all() ]

        for i in mtnList2:
            # print(i)
            # (3, 'Email testing by Keven', '66202', 'YTS-1051', datetime.datetime(2022, 7, 25, 18, 0), datetime.datetime(2022, 7, 25, 20, 0), 'No downtime deployment')
            ## filter ongoing - ms in shift range, but me not in the shift range
            if (time_in_range(shift_stime_obj, shift_etime_obj, i[4])) and (time_in_range(shift_stime_obj, shift_etime_obj, i[5]) == False):                
                onGoingListJsm.append(i)
                # print('Ongoing:', i[0], i[1]) # do the html table later
            ## ms - shift s - shift e - me
            elif (time_in_range(i[4], i[5], shift_etime_obj)):
                onGoingListJsm.append(i)
            ## filter finished - ms in shift range, but me not in the shift range
            elif (time_in_range(shift_stime_obj, shift_etime_obj, i[5])):
                finishedListJsm.append(i)
                # print('Finished:', i[0], i[1])
            ## filter coming soon, if the result less 86400 sec as 24 hours
            elif 0 <= (datetime.datetime.timestamp(i[4]) - datetime.datetime.timestamp(shift_etime_obj)) <= 86400:
                comingSoonListJsm.append(i)

        # build the html table
        returnList = []

        if len(onGoingListJsm) > 0:
            counter = len(onGoingListJsm)
            returnList.append(f'<tr class="topHead"><th colspan="5" width="100%">Ongoing: {counter}</th></tr>')
            returnList.append(f'<tr><th width="25%">TicketName</th><th width="10%">Type</th><th width="10%">StartTime</th><th width="10%">EndTime</th><th width="45%">Detail</th></tr>')
            lastComment = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.sn == i[8]).first()
            for i in onGoingListJsm:
                returnList.append('<tr>')
                returnList.append(f'<td>{i[3]}<br>{i[1]}</td>')
                returnList.append(f'<td>{i[6]}</td>')
                returnList.append(f'<td>{i[4]}</td>')
                returnList.append(f'<td>{i[5]}</td>')
                returnList.append('<td>')
                returnList.append(f'{i[7]}')
                returnList.append(f'<div>Last comment update by {lastComment.handler}: {lastComment.content}</div>')
                returnList.append('</td>')
                returnList.append('</tr>')
        else:
            returnList.append('<tr class="topHead" colspan="5"><th width="100%" colspan="5">Ongoing: 0</th></tr>')

        if len(finishedListJsm) > 0:
            counter = len(finishedListJsm)
            returnList.append(f'<tr class="topHead"><th colspan="5" width="100%">Finished: {counter}</th></tr>')
            returnList.append(f'<tr><th width="25%">TicketName</th><th width="10%">Type</th><th width="10%">StartTime</th><th width="10%">EndTime</th><th width="45%">Detail</th></tr>')
            lastComment = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.sn == i[8]).first()
            for i in finishedListJsm:
                returnList.append('<tr>')
                returnList.append(f'<td>{i[3]}<br>{i[1]}</td>')
                returnList.append(f'<td>{i[6]}</td>')
                returnList.append(f'<td>{i[4]}</td>')
                returnList.append(f'<td>{i[5]}</td>')
                returnList.append('<td>')
                returnList.append(f'{i[7]}')
                returnList.append(f'<div>Last comment update by {lastComment.handler}: {lastComment.content}</div>')
                returnList.append('</td>')
                returnList.append('</tr>')
        else:
            returnList.append('<tr class="topHead" colspan="5"><th width="100%" colspan="5">Finished: 0</th></tr>')

        if len(comingSoonListJsm) > 0:
            counter = len(comingSoonListJsm)
            returnList.append(f'<tr class="topHead"><th colspan="5" width="100%">Coming soon within 24 hours: {counter}</th></tr>')
            returnList.append(f'<tr><th width="25%">TicketName</th><th width="10%">Type</th><th width="10%">StartTime</th><th width="10%">EndTime</th><th width="45%">Detail</th></tr>')
            lastComment = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.sn == i[8]).first()
            for i in comingSoonListJsm:
                returnList.append('<tr>')
                returnList.append(f'<td>{i[3]}<br>{i[1]}</td>')
                returnList.append(f'<td>{i[6]}</td>')
                returnList.append(f'<td>{i[4]}</td>')
                returnList.append(f'<td>{i[5]}</td>')
                returnList.append('<td>')
                returnList.append(f'{i[7]}')
                returnList.append(f'<div>Last comment update by {lastComment.handler}: {lastComment.content}</div>')
                returnList.append('</td>')
                returnList.append('</tr>')
        else:
            returnList.append('<tr class="topHead" colspan="5"><th width="100%" colspan="5">Coming soon within 24 hours: 0</th></tr>')

        return "".join(returnList)

    def getOtrs(self):
        # result = get_handover_otrs.query.filter(get_handover_otrs.date==self.query_date, get_handover_otrs.shift==self.query_shift).all()
        return 'hit function getOTRS'

    def getNote(self):
        result = get_handover_notes.query.filter(
            get_handover_notes.date == self.query_date,
            get_handover_notes.shift == self.query_shift).all()
        containerList = []
        containerList.append('<tr>')
        containerList.append('<td bgcolor="#ffffff">')
        containerList.append('<!--[if mso]>')
        containerList.append(
            '<table class="noteZone" style="border-spacing:0;Margin:0;padding:0;width:100%;min-width:600;">'
        )
        containerList.append('<![endif]-->')
        containerList.append('<!--[if !mso]><!---->')
        containerList.append(
            '<table class="noteZone" style="border-spacing:0;Margin:0;padding:0;width:100%;min-width:600px;">'
        )
        containerList.append('<!-- <![endif]-->')
        containerList.append('<thead><tr><th>Note</th></tr></thead>')
        for i in result:
            # check if any update for this note, check the update_summary
            if i.update_summary:
                if i.update_summary == 'New':
                    # print(f'means new ticket - {i.customer}')
                    containerList.append(
                        f'<tr style="border:1px gray solid;"><td>')
                    containerList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Create by {i.update_by}</b></span><font color="#FF0000"><b> {i.sequence}. {i.customer}</b></font></div>'
                    )
                    containerList.append(f'<div>{i.summary}</div>')
                    containerList.append(f'</td></tr>')
                    # means new ticket
                else:
                    # print(f'means update ticket - {i.customer}')
                    containerList.append(
                        f'<tr style="border:1px gray solid;"><td>')
                    containerList.append(
                        f'<div><font color="#FF0000"><b> {i.sequence}. {i.customer}</b></font></div>'
                    )
                    containerList.append(f'<div>{i.summary}</div>')
                    containerList.append(
                        f'<div><span style="background-color:#FFFF00;"><b>Update by {i.update_by}</b></span> {i.update_summary}</div>'
                    )
                    containerList.append(f'</td></tr>')
            else:
                # just build the note tamplate
                containerList.append(
                    f'<tr style="border:1px gray solid;"><td>')
                containerList.append(
                    f'<div><font color="#FF0000"><b>{i.sequence}. {i.customer}</b></font></div>'
                )
                containerList.append(f'<span>{i.summary}</span>')
                containerList.append(f'</td></tr>')
        containerList.append('</table>')
        containerList.append('</td></tr>')
        return "".join(containerList)

    def getAttachment(self):
        result_note_with_attachments_list = get_handover_notes.query.filter(
            get_handover_notes.date == self.query_date,
            get_handover_notes.shift == self.query_shift,
            get_handover_notes.check_image != None).all()
        reverseDict = {
            'docx':
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx':
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pptx':
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'pdf': 'application/pdf',
            'csv': 'application/vnd.ms-excel',
            'rar': 'application/octet-stream',
            'zip': 'application/x-zip-compressed',
            'png': 'image/png'
        }
        if result_note_with_attachments_list:
            attachmentNoteSnList = [
                x.sn for x in result_note_with_attachments_list
            ]
            # ( fileName, fileType, filePath )
            attachmentsList = []
            for i in attachmentNoteSnList:
                get_note_attachment_detail_by_sn_list = get_handover_notes_attachment.query.filter(
                    get_handover_notes_attachment.noteSn == i).all()
                for ii in get_note_attachment_detail_by_sn_list:
                    attachmentsList.append(
                        (ii.fileName, reverseDict[f'{ii.fileType}'],
                         ii.filePath))
            return attachmentsList
        else:
            return []


@app_mainEmail.route('/jira/checkComments')
def jira_check_comments():

    # input - jira comments object, output - string with html tag
    def convert_comment_to_string(targetDict):
        return_string = '<span style="background-color: yellow"> Update by <b>' + targetDict['handler'] + '</b></span> at <span style="color:#FF0000">' + targetDict['timestamp'] + '</span><br><div>' + targetDict['content'] + '</div>'
        return return_string
        
    # get date and shift    
    lastRow = get_handover_customer_status.query.order_by(
        get_handover_customer_status.sn.desc()).first()
    date = lastRow.date
    shift = lastRow.shift
    # date = '2022-07-26'
    # shift = 'N'
    # print(date)
    # print(shift)

    # get the shift start time and end time
    shiftTimeMapping = {'M': '07:30', 'A': '15:00', 'N': '23:00'}
    stime_time = shiftTimeMapping[shift]
    shift_stime = f'{date} {stime_time}'
    shift_stime_obj = datetime.datetime.strptime(shift_stime, "%Y-%m-%d %H:%M")
    shift_stime_unix = datetime.datetime.timestamp(shift_stime_obj)
    shift_etime_unix = shift_stime_unix + 32400
    shift_etime_obj = datetime.datetime.fromtimestamp(shift_etime_unix)

    # Using the shift start time and endtime to get all comments during that time.
    result = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.timestamp.between(shift_stime_obj, shift_etime_obj)).order_by(get_jsm_ops_comments.sn.desc()).all()

    # full report, get all jira ticket status is not equal close
    result_open_jira = get_jsm_ops_prod.query.filter(and_(get_jsm_ops_prod.jiraStatus != 121,
                 get_jsm_ops_prod.jiraStatus != 71,
                 get_jsm_ops_prod.jiraStatus != 6)).all()

    result_open_jira_key = [ y.issueKey for x in result_open_jira for y in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.sn == x.mapping) ]

    print(f'result_open_jira_key = {result_open_jira_key}')

    #  store the data based on Jira ticket issueKey
    commentsHash = {}

    for i in result:
        if i.issueKey in commentsHash.keys():
            currentList = commentsHash[i.issueKey]
            currentList.append(i.serialize)
        else:
            commentsHash[i.issueKey] = [i.serialize]

    resultJiraList = []

    # store the jira ticket all infromations with commentlists
    # for x in list(commentsHash.keys()):
    for x in result_open_jira_key:
        if x in commentsHash.keys():
            commentList = [itemComment for itemComment in commentsHash[x]]
        else:
            commentList = []
        mappingSn = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==x).first().sn
        jsmContent = [ dict(title=itemContent.title, description=itemContent.description, status=itemContent.jiraStatus) for itemContent in get_jsm_ops_prod.query.filter(get_jsm_ops_prod.mapping==mappingSn).limit(1).all()]
        resultJiraList.append(dict(ticket=x, comments=commentList, contents=jsmContent[0]))

    tmpList = [f'<span style="color:#ff0000"><b>*</b></span><div><b>[{date} {shift}] YiTMH Operation Handover(Brief)</b></div><br>']
    tmpList.append('<span style="color:#D3D3D3"><i>===HANDOVER START===</i></span><br>')
    tmpList.append('<span style="color:#D3D3D3"><i>====NOTE START====</i></span><br>')
    tmpList.append('<span style="color:#D3D3D3"><i>====NOTE END====</i></span><br><br>')
    tmpList.append('<span style="color:#D3D3D3"><i>====OTRS TICKET START====</i></span><br>')
    tmpList.append('<span style="color:#D3D3D3"><i>====OTRS TICKET END====</i></span><br><br>')
    tmpList.append('<span style="color:#D3D3D3"><i>====JIRA TICKET START====</i></span><br><br>')
    
    for item in resultJiraList:
        ticketName = item['ticket'] + ' - ' + item['contents']['title']
        ticketContent = item['contents']['description']
        commentLists = item['comments']
        commentLists.reverse() # reverse the comment on list, show the old timestamp first.
        tmpList.append(f'<div><span style="color:#0000FF"><b>{ticketName}</b></span></div>')
        tmpList.append(f'<div>{ticketContent}</div>')
        for i in commentLists:
            tmpList.append(convert_comment_to_string(i))
        tmpList.append('<br>')

    tmpList.append('<span style="color:#D3D3D3"><i>====JIRA  TICKET END====</i></span><br><br>')
    htmlString = "".join(tmpList)
    # print(f'htmlString = {htmlString}')
 
    return htmlString
    # return jsonify(resultList)

@app_mainEmail.route('/exportword')  # default for confirm page
@app_mainEmail.route('/exportword/<date>/<shift>/<_type>')
def exportword(date=None, shift=None, _type=None):
    if date == None and shift == None and _type == None:
        lastRow = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        date = lastRow.date
        shift = lastRow.shift
        _type = 'reviewF'

    result_note = get_handover_notes.query.filter(
        get_handover_notes.date == date, get_handover_notes.shift == shift,
        get_handover_notes.sequence != 99).all()
    result_otrs = get_handover_otrs.query.filter(
        get_handover_otrs.date == date, get_handover_otrs.shift == shift,
        get_handover_otrs.sequence != 99).order_by(
            get_handover_otrs.sn.desc()).all()

    # input - jira comments object, output - string with html tag
    def convert_comment_to_string(targetDict):
        return_string = '<span style="background-color: yellow"> Update by <b>' + targetDict['handler'] + '</b></span> at <span style="color:#FF0000">' + targetDict['timestamp'] + '</span><br><div>' + targetDict['content'] + '</div><br>'
        return return_string

    # get the shift start time and end time
    shiftTimeMapping = {'M': '07:30', 'A': '15:30', 'N': '23:30'}
    stime_time = shiftTimeMapping[shift]
    shift_stime = f'{date} {stime_time}'
    shift_stime_obj = datetime.datetime.strptime(shift_stime, "%Y-%m-%d %H:%M")
    shift_stime_unix = datetime.datetime.timestamp(shift_stime_obj)
    shift_etime_unix = shift_stime_unix + 28800
    shift_etime_obj = datetime.datetime.fromtimestamp(shift_etime_unix)

    resultJiraList = []

    # jira part
    result_jira = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.timestamp.between(shift_stime_obj, shift_etime_obj)).order_by(get_jsm_ops_comments.sn.desc()).all()
    # result_jira_b = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.timestamp.between(shift_stime_obj, shift_etime_obj), ).order_by(get_jsm_ops_comments.sn.desc()).all()

    #  store the data based on Jira ticket issueKey
    commentsHash = {}

    for i in result_jira:
        if i.issueKey in commentsHash.keys():
            currentList = commentsHash[i.issueKey]
            currentList.append(i.serialize)
        else:
            commentsHash[i.issueKey] = [i.serialize]


    if _type == 'F' or _type == 'reviewF':
        # full report, get all jira ticket status is not equal close
        result_open_jira = get_jsm_ops_prod.query.filter(and_(get_jsm_ops_prod.jiraStatus != 121,
                    get_jsm_ops_prod.jiraStatus != 71,
                    get_jsm_ops_prod.jiraStatus != 6,
                    get_jsm_ops_prod.ticketStatus != 99
                    )).all()

        result_open_jira_key = [ y.issueKey for x in result_open_jira for y in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.sn == x.mapping) ]

        for x in result_open_jira_key:
            if x in commentsHash.keys():
                commentList = [itemComment for itemComment in commentsHash[x]]
            else:
                commentList = []
            mappingSn = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==x).first().sn
            jsmContent = [ dict(title=itemContent.title, description=itemContent.description, status=itemContent.jiraStatus) for itemContent in get_jsm_ops_prod.query.filter(get_jsm_ops_prod.mapping==mappingSn).limit(1).all()]
            if len(jsmContent) != 0:
                resultJiraList.append(dict(ticket=x, comments=commentList, contents=jsmContent[0]))

        tmpList = [f'<span style="color:#ff0000"><b>*</b></span><div><b>[{date} {shift}] YiTMH Operation Handover</b></div><br>']
        tmpList.append('<span style="color:#D3D3D3"><i>===HANDOVER START===</i></span><br>')
        # note start
        tmpList.append('<span style="color:#D3D3D3"><i>====NOTE START====</i></span><br>')
        for item in result_note:
            # new note
            if item.update_summary == 'New':
                tmpList.append(f'<span style="background-color: yellow"><b>Created by {item.update_by}</b></span> <div><span style="color:#ff0000"><b>Note {item.sequence} - {item.customer}</b></span></div><br>')
                tmpList.append(f'<div>{item.summary}</div><br>')
            # update note
            elif item.update_summary and item.update_by:
                tmpList.append(f'<div><span style="color:#ff0000"><b>Note {item.sequence} - {item.customer}</b></span></div><br>')
                tmpList.append(f'<div>{item.summary}</div><br>')
                tmpList.append(f'<span style="background-color: yellow"><b>Updated by {item.update_by}</b></span> <div>{item.update_summary}</div><br>')
            # non changtmpList note
            else:
                tmpList.append(f'<div><span style="color:#ff0000"><b>Note {item.sequence} - {item.customer}</b></span></div><br>')
                tmpList.append(f'<div>{item.summary}</div><br>')
            tmpList.append('<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>')
        tmpList.append('<span style="color:#D3D3D3"><i>====NOTE END====</i></span><br><br>')
        # note end
        # otrs start
        tmpList.append('<span style="color:#D3D3D3"><i>====OTRS TICKET START====</i></span><br>')
        for item in result_otrs:
            if item.update_summary == 'New':
                tmpList.append(f'<span style="background-color: yellow"><b>handled by {item.update_by}</b></span> <div><span style="color:#0000FF"><b>YTS{item.number} - {item.subject}</b></span></div><br>')
                tmpList.append(f'<div>{item.summary}</div><br>')
            elif item.update_by and item.update_summary:
                tmpList.append(f'<div><span style="color:#0000FF"><b>YTS{item.number} - {item.subject}</b></span></div><br>')
                tmpList.append(f'<div>{item.summary}</div><br>')
                tmpList.append(f'<span style="background-color: yellow"><b>Updated by {item.update_by}</b></span> <div>{item.update_summary}</div><br>')
            else:
                tmpList.append(f'<div><span style="color:#0000FF"><b>YTS{item.number} - {item.subject}</b></span></div><br>')
                tmpList.append(f'<div>{item.summary}</div><br>')
            tmpList.append('<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>')
        tmpList.append('<span style="color:#D3D3D3"><i>====OTRS TICKET END====</i></span><br>')
        # otrs end

        tmpList.append('<span style="color:#D3D3D3"><i>====JIRA TICKET START====</i></span><br><br>')
        for item in resultJiraList:
            tmpList.append('<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>')
            ticketName = item['ticket'] + ' - ' + item['contents']['title']
            ticketContent = item['contents']['description']
            commentLists = item['comments']
            commentLists.reverse() # reverse the comment on list, show the old timestamp first.
            tmpList.append(f'<div><span style="color:#0000FF"><b>{ticketName}</b></span></div><br>')
            tmpList.append(f'<div>{ticketContent}</div><br>')
            for i in commentLists:
                tmpList.append(convert_comment_to_string(i))
            tmpList.append('<br>')
            tmpList.append('<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>')

        tmpList.append('<span style="color:#D3D3D3"><i>====JIRA  TICKET END====</i></span><br><br>')

        tmpList.append(
            '<span style="color:#D3D3D3"><i>===HANDOVER END===</i></span><br>')

        tmpString = "".join(tmpList)
        if _type == 'reviewF':
            # need to check the attachment -
            checkAttachmentCounter = get_handover_notes.query.filter(
                get_handover_notes.date == date,
                get_handover_notes.shift == shift,
                get_handover_notes.check_image != None).all()
            # adjust date
            ## after handover need to change, store on .223, now need to load .199
            # check .223
            if checkAttachmentCounter:
                attachmentNoteSnList = [(x.sn, x.customer)
                                        for x in checkAttachmentCounter]
                attachmentsList = []
                for i in attachmentNoteSnList:
                    get_note_attachment_detail_by_sn_list = get_handover_notes_attachment.query.filter(
                        get_handover_notes_attachment.noteSn == i[0]).all()
                    for ii in get_note_attachment_detail_by_sn_list:
                        attachmentsList.append(
                            (ii.fileName, ii.fileType, ii.sn, i[1]))
                return jsonify([
                    tmpString, True, attachmentsList,
                    f'<span style="color:#ff0000"><b>*</b></span><div><b>[{date}-{shift}] YiTMH Operation Handover</b></div><br>',
                    f'{date}', shift
                ])
            else:
                return jsonify([
                    tmpString, False, [],
                    f'<div><b>[{date}-{shift}] YiTMH Operation Handover</b></div>',
                    f'{date}', shift
                ])
        else:
            # new_parser = HtmlToDocx()
            # tmp = new_parser.parse_html_string(tmpString)
            # tmp.save('bpEmail/staticLocal/reportFull.docx')
            # target = 'staticLocal/reportFull.docx'
            target = 'staticLocal/reportFull.html'
            with open("bpEmail/staticLocal/reportFull.html", "w") as f:
                f.write('<!DOCTYPE html>')
                f.write('<html lang="en">')
                f.write('<head>')
                f.write('<meta charset="UTF-8">')
                f.write('<meta http-equiv="X-UA-Compatible" content="IE=edge">')
                f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
                f.write('<title>HandoverSystemBrief</title>')
                f.write('</head>')
                f.write('<body>')
                for i in tmpList:
                    f.write(i)
                f.write('</body>')
                f.write('</html>')
            return target
            # return full report path

    elif _type == 'B':
        # store the jira ticket all infromations with commentlists
        for x in list(commentsHash.keys()):
            commentList = [itemComment for itemComment in commentsHash[x]]
            mappingSn = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==x).first().sn
            jsmContent = [ dict(title=itemContent.title, description=itemContent.description, status=itemContent.jiraStatus) for itemContent in get_jsm_ops_prod.query.filter(get_jsm_ops_prod.mapping==mappingSn).limit(1).all()]
            if len(jsmContent) != 0:
                resultJiraList.append(dict(ticket=x, comments=commentList, contents=jsmContent[0]))

        tmpList = [f'<span style="color:#ff0000"><b>*</b></span><div><b>[{date} {shift}] YiTMH Operation Handover(Brief)</b></div><br>']
        tmpList.append(
            '<span style="color:#D3D3D3"><i>===HANDOVER START===</i></span><br>'
        )
        tmpList.append(
            '<span style="color:#D3D3D3"><i>====NOTE START====</i></span><br>')
        for item in result_note:
            # new note
            if item.update_summary == 'New':
                tmpList.append(
                    f'<span style="background-color: yellow"><b>Created by {item.update_by}</b></span> <div><span style="color:#ff0000"><b>Note {item.sequence} - {item.customer}</b></span></div><br>'
                )
                tmpList.append(f'<div>{item.summary}</div><br>')
                tmpList.append(
                    '<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>'
                )
            # update note
            elif item.update_summary and item.update_by:
                tmpList.append(
                    f'<div><span style="color:#ff0000"><b>Note {item.sequence} - {item.customer}</b></span></div><br>'
                )
                tmpList.append(f'<div>{item.summary}</div><br>')
                tmpList.append(
                    f'<span style="background-color: yellow"><b>Updated by {item.update_by}</b></span> <div>{item.update_summary}</div><br>'
                )
                tmpList.append(
                    '<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>'
                )
            # non changtmpList note
        tmpList.append(
            '<span style="color:#D3D3D3"><i>====NOTE END====</i></span><br><br>'
        )
        tmpList.append(
            '<span style="color:#D3D3D3"><i>====OTRS TICKET START====</i></span><br>'
        )
        for item in result_otrs:
            if item.update_summary == 'New':
                tmpList.append(
                    f'<span style="background-color: yellow"><b>handled by {item.update_by}</b></span> <div><span style="color:#0000FF"><b>YTS{item.number} - {item.subject}</b></span></div><br>'
                )
                tmpList.append(f'<div>{item.summary}</div><br>')
                tmpList.append(
                    '<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>'
                )
            elif item.update_by and item.update_summary:
                tmpList.append(
                    f'<div><span style="color:#0000FF"><b>YTS{item.number} - {item.subject}</b></span></div><br>'
                )
                tmpList.append(f'<div>{item.summary}</div><br>')
                tmpList.append(
                    f'<span style="background-color: yellow"><b>Updated by {item.update_by}</b></span> <div>{item.update_summary}</div><br>'
                )
                tmpList.append(
                    '<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>'
                )
        tmpList.append(
            '<span style="color:#D3D3D3"><i>====OTRS TICKET END====</i></span><br>'
        )

        tmpList.append('<span style="color:#D3D3D3"><i>====JIRA TICKET START====</i></span><br><br>')
    
        for item in resultJiraList:
            tmpList.append('<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>')
            ticketName = item['ticket'] + ' - ' + item['contents']['title']
            ticketContent = item['contents']['description']
            commentLists = item['comments']
            commentLists.reverse() # reverse the comment on list, show the old timestamp first.
            tmpList.append(f'<div><span style="color:#0000FF"><b>{ticketName}</b></span></div><br>')
            tmpList.append(f'<div>{ticketContent}</div><br>')
            for i in commentLists:
                tmpList.append(convert_comment_to_string(i))
            tmpList.append('<span style="color:#D3D3D3"><i>=====Split=====</i></span><br>')

        tmpList.append('<span style="color:#D3D3D3"><i>====JIRA  TICKET END====</i></span><br><br>')
        
        tmpString = "".join(tmpList)
        # new_parser = HtmlToDocx()
        # tmp = new_parser.parse_html_string(tmpString)
        # tmp.save('bpEmail/staticLocal/reportBrief.docx')
        target = 'staticLocal/reportBrief.html'
        with open("bpEmail/staticLocal/reportBrief.html", "w") as f:
            f.write('<!DOCTYPE html>')
            f.write('<html lang="en">')
            f.write('<head>')
            f.write('<meta charset="UTF-8">')
            f.write('<meta http-equiv="X-UA-Compatible" content="IE=edge">')
            f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
            f.write('<title>HandoverSystemBrief</title>')
            f.write('</head>')
            f.write('<body>')
            for i in tmpList:
                f.write(i)
            f.write('</body>')
            f.write('</html>')
        return target
    elif _type == 'reviewB':
        for x in list(commentsHash.keys()):
            commentList = [itemComment for itemComment in commentsHash[x] if itemComment['commentType'] == 2]
            if len(commentList) != 0:
                mappingSn = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==x).first().sn
                jsmContent = [ dict(title=itemContent.title, description=itemContent.description, status=itemContent.jiraStatus, ticketSn=itemContent.sn, category=itemContent.custom_category  ) for itemContent in get_jsm_ops_prod.query.filter(get_jsm_ops_prod.mapping==mappingSn).limit(1).all()]
                # incase if the ticket status is OPEN
                if len(jsmContent) != 0:
                    resultJiraList.append(dict(ticket=x, comments=commentList, contents=jsmContent[0]))

        print('hit reviewB')
        returnList = []
        returnList.append([x.serialize for x in result_note])
        returnList.append([x.serialize for x in result_otrs])

        # sort the jira
        resultJiraList_for_review_b = []
        for item in resultJiraList:
            ticketName = item['ticket'] + ' - ' + item['contents']['title']
            category = item['contents']['category']
            ticketSn = item['contents']['ticketSn']
            ticketContent = item['contents']['description']
            ticketStatus = item['contents']['status']
            commentLists = item['comments']
            commentLists.reverse()
            resultJiraList_for_review_b.append((ticketName, ticketContent, ticketStatus, commentLists, ticketSn, category))

        checkAttachmentCounter = get_handover_notes.query.filter(
            get_handover_notes.date == date, get_handover_notes.shift == shift,
            get_handover_notes.check_image != None).all()
        ## after handover need to change, store on .223, now need to load .199
        # check to .223
        if checkAttachmentCounter:
            attachmentNoteSnList = [x.sn for x in checkAttachmentCounter]
            # ( fileName, fileType, filePath )
            attachmentsList = []
            for i in attachmentNoteSnList:
                get_note_attachment_detail_by_sn_list = get_handover_notes_attachment.query.filter(
                    get_handover_notes_attachment.noteSn == i).all()
                for ii in get_note_attachment_detail_by_sn_list:
                    attachmentsList.append(
                        (ii.fileName, ii.fileType, ii.sn, ii.noteSn))
            returnList.append(attachmentsList)
        else:
            returnList.append([])
        # .199
        # if checkAttachmentCounter:
        #     attachmentList = []
        #     for i in checkAttachmentCounter:
        #         for ii in range(i.check_image):
        #             tmpInt = ii + 1
        #             attachmentList.append([f'http://10.7.6.199/handover/notes_carousel.php?data={date}&shift={shift}&notename={i.customer}&sn={tmpInt}&max={i.check_image}', i.customer])
        #     returnList.append(attachmentList)
        # else:
        #     returnList.append([])
        ## check diff
        # calculate previos date & shift
        previousDate = date
        if shift == 'M':
            previousShift = 'N'
            curDateObject = datetime.datetime.strptime(date, "%Y-%m-%d")
            curDateUnix = datetime.datetime.timestamp(curDateObject)
            previousDateUnix = curDateUnix - 86400
            previousDateObject = datetime.datetime.fromtimestamp(
                previousDateUnix)
            previousDate = f'{previousDateObject.year}-{previousDateObject.month}-{previousDateObject.day}'
        elif shift == 'A':
            previousShift = 'M'
        elif shift == 'N':
            previousShift = 'A'
        result_note_tmp = [
            (x.customer, x.summary, x.update_by) for x in result_note
            if x.update_by and (
                x.update_summary == None or x.update_summary == '')
        ]
        result_otrs_tmp = [
            (f'YTS{x.number} - {x.subject}', x.summary, x.update_by, x.number)
            for x in result_otrs if x.update_by and (
                x.update_summary == None or x.update_summary == '')
        ]
        # print(result_otrs_tmp)
        diffList = []
        for i in result_note_tmp:
            checkDbByPreviosTime = get_handover_notes.query.filter(
                get_handover_notes.date == previousDate,
                get_handover_notes.shift == previousShift,
                get_handover_notes.customer == i[0]).first()
            if checkDbByPreviosTime:
                if i[1] != checkDbByPreviosTime.summary:
                    dmp = dmp_module.diff_match_patch()
                    diff = dmp.diff_main(checkDbByPreviosTime.summary, i[1])
                    dmp.diff_cleanupEfficiency(diff)
                    returnHtml = dmp.diff_prettyHtml(diff)
                    diffList.append(
                        dict(
                            source='Note - ',
                            target=i[0],
                            lastEditor=i[2],
                            oldDateShift=
                            f'{checkDbByPreviosTime.date}-{checkDbByPreviosTime.shift}',
                            curDateShift=f'{date}-{shift}',
                            oldContent=checkDbByPreviosTime.summary,
                            curContent=i[1],
                            diffHtml=returnHtml))

        for i in result_otrs_tmp:
            # print(i)
            # print('===')
            # print(f'previousDate = {previousDate}')
            # print(f'previousShift = {previousShift}')
            # print(i[3])
            # print('---')
            checkDbByPreviosTime = get_handover_otrs.query.filter(
                get_handover_otrs.date == previousDate,
                get_handover_otrs.shift == previousShift,
                get_handover_otrs.number == i[3]).first()

            if checkDbByPreviosTime:
                previousSummaryLen = len(checkDbByPreviosTime.summary)

                if (checkDbByPreviosTime.update_summary
                    ) and checkDbByPreviosTime.update_summary != 'New':
                    previousUpdateSummaryLen = len(
                        checkDbByPreviosTime.update_summary)
                else:
                    previousUpdateSummaryLen = 0
                if (previousSummaryLen + previousUpdateSummaryLen) != len(
                        i[1]):
                    if i[2]:
                        dmp = dmp_module.diff_match_patch()
                        diff = dmp.diff_main(checkDbByPreviosTime.summary,
                                             i[1])
                        dmp.diff_cleanupEfficiency(diff)
                        returnHtml = dmp.diff_prettyHtml(diff)
                        diffList.append(
                            dict(
                                source='Ticket - ',
                                target=i[0],
                                lastEditor=i[2],
                                oldDateShift=
                                f'{checkDbByPreviosTime.date}-{checkDbByPreviosTime.shift}',
                                curDateShift=f'{date}-{shift}',
                                oldContent=checkDbByPreviosTime.summary,
                                curContent=i[1],
                                diffHtml=returnHtml))
        returnList.append(diffList)
        returnList.append(resultJiraList_for_review_b)
        return jsonify(returnList)
    else:
        return 'not allow'


@app_mainEmail.route('/export', methods=['GET', 'POST'])
@app_mainEmail.route('/export/<date>/<shift>')
def exportSummaryTableV2(date=None, shift=None):
    # check the query type
    if request.method == 'GET':
        customQuery = True
        if date == None and shift == None:
            lastRow = get_handover_customer_status.query.order_by(
                get_handover_customer_status.sn.desc()).first()
            date = lastRow.date
            shift = lastRow.shift
    elif request.method == 'POST':
        customQuery = False
        lastRow = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        date = lastRow.date
        shift = lastRow.shift
        front_data = request.get_json(silent=True)
        sender = front_data['sender']

    classObject = GenerateEmail(date, shift)
    # mtnZone = classObject.getMtnOTRS()

    newMtnZone = classObject.getMtnJira()
    # print(f'newMtnZone = {newMtnZone}')

    shiftTimeMapping = {'M': '07:30', 'A': '15:00', 'N': '23:00'}

    highLevelPplList = ['Larry', 'Danny', 'Huck', 'Keven', 'Bayu']
    staff_list = []
    staff_l3_list = []

    # Part 1 & Part 2
    ## 1
    stime_time = shiftTimeMapping[shift]
    shift_stime = f'{date} {stime_time}'
    shift_stime_obj = datetime.datetime.strptime(shift_stime, "%Y-%m-%d %H:%M")
    shift_stime_unix = datetime.datetime.timestamp(shift_stime_obj)
    shift_etime_unix = shift_stime_unix + 32400
    shift_etime_obj = datetime.datetime.fromtimestamp(shift_etime_unix)
    pt = datetime.datetime.now()
    printed_time_format = pt.strftime("%Y-%m-%d %H:%M:%S")
    # print(f'Period: {printed_time_format}')
    # print(f'start - {shift_stime_obj}')
    # print(f'end - {shift_etime_obj}')
    ## 2
    result_shift_list = get_handover_shift_table.query.filter(
        get_handover_shift_table.date == date,
        get_handover_shift_table.shift == shift).first()
    teammatesList = json.loads(result_shift_list.teammates)
    for i in teammatesList:
        if i in highLevelPplList:
            staff_l3_list.append(i)
        else:
            staff_list.append(i)
    # print(f'Staff on duty: {", ".join(staff_list)}, L3 on duty: {", ".join(staff_l3_list)}')
    basicInfoList = []
    basicInfoList.append(f'<tbody>')
    basicInfoList.append('<tr>')
    basicInfoList.append(f'<td>Printed</td><td>{printed_time_format}</td>')
    basicInfoList.append('</tr>')
    basicInfoList.append('<tr>')
    basicInfoList.append(
        f'<td>Period</td><td>{shift_stime_obj} ~ {shift_etime_obj}</td>')
    basicInfoList.append('</tr>')
    basicInfoList.append('<tr>')
    basicInfoList.append(
        f'<td>Staff on duty</td><td>{", ".join(staff_list)}</td>')
    basicInfoList.append('</tr>')
    basicInfoList.append('<tr>')
    if shift == 'N':
        basicInfoList.append(
            f'<td>L3 Standby</td><td>{", ".join(staff_l3_list)}</td>')
    else:
        basicInfoList.append(
            f'<td>L3 on duty</td><td>{", ".join(staff_l3_list)}</td>')
    basicInfoList.append('</tr>')
    basicInfoList.append('</tbody>')
    basicInfoHtml = "".join(basicInfoList)

    # Part 3 - Summary information
    result_bu = get_handover_customer_status.query.filter(
        get_handover_customer_status.date == date,
        get_handover_customer_status.shift == shift).first()
    buDict = collections.OrderedDict()
    keyList = []
    valueList = []
    isNeedToInsertIssueMitigated = False
    isNeedToInsertUnclosedIssue = False
    for key, value in result_bu.serialize.items():
        if value == 'Yellow':
            isNeedToInsertIssueMitigated = True
        elif value == 'Red':
            isNeedToInsertUnclosedIssue = True
        if key == '_188A':
            keyList.append('188A')
            valueList.append(value)
        else:
            keyList.append(key)
            valueList.append(value)
    buDict['bu'] = keyList
    buDict['status'] = valueList
    serviceMapLength = len(buDict['bu'])

    buTableList = []
    buTableList.append(
        f'<tbody><tr><th style="width:100%" class="topHead" colspan="{serviceMapLength}">BU</th></tr>'
    )
    buTableList.append('<tr>')
    for buName in buDict['bu']:
        buTableList.append(f'<th>{buName}</th>')
    buTableList.append('</tr>')
    buTableList.append('<tr>')
    for buStatus in buDict['status']:
        if buStatus == 'Green':
            buTableList.append(
                f'<td><font color="#00BB00"><b>{buStatus}</b></font></td>')
        elif buStatus == 'Yellow':
            buTableList.append(
                f'<td><font color="#FDB133"><b>{buStatus}</b></font></td>')
        elif buStatus == 'Red':
            buTableList.append(
                f'<td><font color="#EA0000"><b>{buStatus}</b></font></td>')
    buTableList.append('</tr>')
    buTableList.append('</tbody>')
    buhtmltable = "".join(buTableList)

    # Issue Mitigated
    if isNeedToInsertIssueMitigated:
        yellowEventList = []
        get_all_yellow_event = get_customer_status_note.query.filter(
            get_customer_status_note.date == date,
            get_customer_status_note.shift == shift,
            get_customer_status_note.status == 'Yellow').all()
        for item in get_all_yellow_event:
            customerStr = ", ".join(json.loads(item.customer))
            yellowEventList.append(f'<tbody>')
            yellowEventList.append(f'<tr>')
            yellowEventList.append(f'<th>{item.note}</th>')
            yellowEventList.append(f'</tr>')
            yellowEventList.append(f'<tr>')
            yellowEventList.append(f'<td>Impacted BU: {customerStr}</td>')
            yellowEventList.append(f'</tr>')
            yellowEventList.append(f'<tr>')
            yellowEventList.append(f'<td>Cause by: {item.impactby}</td>')
            yellowEventList.append(f'</tr>')
            yellowEventList.append(f'<tr>')
            yellowEventList.append(
                f'<td>Timestamp: {item.event_start_time} - {item.event_end_time}</td>'
            )
            yellowEventList.append(f'</tr>')
            yellowEventList.append(f'<tr>')
            yellowEventList.append(
                f'<td>Outage time: {item.outage_time} minutes</td>')
            yellowEventList.append(f'</tr>')
            yellowEventList.append(f'<tr>')
            yellowEventList.append(f'<td>Detail:</td>')
            yellowEventList.append(f'</tr>')
            yellowEventList.append(f'<tr>')
            # check the resource
            targetSn = json.loads(item.jira_ticket)[1]
            if json.loads(item.jira_ticket)[0] == 'otrs':
                result = get_handover_otrs.query.filter(
                    get_handover_otrs.date == date,
                    get_handover_otrs.shift == shift,
                    get_handover_otrs.number == targetSn).first()
                detail = result.summary
            elif json.loads(item.jira_ticket)[0] == 'note':
                result = get_handover_notes.query.filter(
                    get_handover_notes.date == date,
                    get_handover_notes.shift == shift,
                    get_handover_notes.sn == targetSn).first()
                detail = result.summary
            elif json.loads(item.jira_ticket)[0] == 'jira':
                result = get_jsm_ops_prod.query.filter(
                    get_jsm_ops_prod.sn == targetSn).first()
                detail = result.description
            yellowEventList.append(f'<td class="customLast">{detail}</td>')
            yellowEventList.append(f'</tr>')
            yellowEventList.append(f'</tbody>')
        yellowEventHtml = "".join(yellowEventList)

    if isNeedToInsertUnclosedIssue:
        redEventList = []
        get_all_red_event = get_customer_status_note.query.filter(
            get_customer_status_note.date == date,
            get_customer_status_note.shift == shift,
            get_customer_status_note.status == 'Red').all()
        for item in get_all_red_event:
            customerStr = ", ".join(json.loads(item.customer))
            redEventList.append(f'<tbody>')
            redEventList.append(f'<tr>')
            redEventList.append(f'<th>{item.note}</th>')
            redEventList.append(f'</tr>')
            redEventList.append(f'<tr>')
            redEventList.append(f'<td>Impacted BU: {customerStr}</td>')
            redEventList.append(f'</tr>')
            redEventList.append(f'<tr>')
            redEventList.append(f'<td>Cause by: {item.impactby}</td>')
            redEventList.append(f'</tr>')
            redEventList.append(f'<tr>')
            redEventList.append(
                f'<td>Timestamp: {item.event_start_time} - {item.event_end_time}</td>'
            )
            redEventList.append(f'</tr>')
            redEventList.append(f'<tr>')
            redEventList.append(
                f'<td>Outage time: {item.outage_time} minutes</td>')
            redEventList.append(f'</tr>')
            redEventList.append(f'<tr>')
            redEventList.append(f'<td>Detail:</td>')
            redEventList.append(f'</tr>')
            redEventList.append(f'<tr>')
            # check the resource
            targetSn = json.loads(item.jira_ticket)[1]
            if json.loads(item.jira_ticket)[0] == 'otrs':
                result = get_handover_otrs.query.filter(
                    get_handover_otrs.date == date,
                    get_handover_otrs.shift == shift,
                    get_handover_otrs.number == targetSn).first()
                detail = result.summary
            elif json.loads(item.jira_ticket)[0] == 'note':
                result = get_handover_notes.query.filter(
                    get_handover_notes.date == date,
                    get_handover_notes.shift == shift,
                    get_handover_notes.sn == targetSn).first()
                detail = result.summary
            elif json.loads(item.jira_ticket)[0] == 'jira':
                result = get_jsm_ops_prod.query.filter(
                    get_jsm_ops_prod.sn == targetSn).first()
                detail = result.description
            redEventList.append(f'<td class="customLast">{detail}</td>')
            redEventList.append(f'</tr>')
            redEventList.append(f'</tbody>')
        redEventHtml = "".join(redEventList)

    # Part 4 - Build the fix html
    startWholeHtmlList = []
    endWholeHtmlList = []
    startBasicInfoHtmlList = []
    endBasicInfoHtmlList = []
    startServiceMapList = []
    endServiceMapList = []
    startMtnList = []
    startYellowEventList = []
    endYellowEventList = []
    startRedEventList = []
    endRedEventList = []
    startWholeHtmlList.append('<!DOCTYPE html><html>')
    startWholeHtmlList.append('<head>')
    startWholeHtmlList.append(
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">')
    startWholeHtmlList.append(
        '<meta name="viewport" content="width=device-width, initial-scale=1">')
    startWholeHtmlList.append(
        '<meta http-equiv="X-UA-Compatible" content="IE=edge">')
    startWholeHtmlList.append('<title>Handover review</title>')
    startWholeHtmlList.append('<style type="text/css">')
    startWholeHtmlList.append('''
                        body {
                            font-family: sans-serif;
                        }
                        table {
                            border-collapse: collapse;
                            font-family: sans-serif;
                        }
                        table .serviceMap {
                            color: gray;
                            border-bottom: 1px solid;
                        }
                        table .eventTable {
                            color: gray;
                        }
                        table .mtnMap td{
                            border-bottom: 1px solid;
                        }
                        table .serviceMap td{
                            border-bottom: 1px solid;
                        }
                        .customLast{
                            border-bottom: 1px solid;
                        }
                        table .operationMap td{
                            color: gray;
                            border-bottom: 1px solid;
                        }
                        table thead {
                            background-color: #36304A;
                            color: #FFFFFF;
                        }
                        table thead th {
                            border-radius: 5px 5px 0 0;
                        }
                        table tbody tr th {
                            text-align: left;
                        }
                        table tbody tr th:first-child {
                            padding-left: 2%;
                        }
                        table tbody tr td:first-child {
                            padding-left: 2%;
                        }
                        table tbody tr td:last-child {
                            padding-right: 2%;
                        }
                        table tbody tr th:last-child {
                            padding-right: 2%;
                        }
                        table .serviceMap tbody tr:nth-of-type(odd) {
                            background-color: rgba(0, 0, 0, .05);
                        }
                        table .operationMap tbody tr:nth-of-type(odd) {
                            background-color: rgba(0, 0, 0, .05);
                        }
                        .topHead {
                            color: #FFFFFF;
                            background-color: #9D9D9D;
                        }
                        table .noteZone {
                        border-collapse: collapse;
                        }
                    ''')
    startWholeHtmlList.append('</style>')
    startWholeHtmlList.append('</head>')
    startWholeHtmlList.append(
        '<body style="margin:0; padding:0; background-color:#F2F2F2;">')
    startWholeHtmlList.append(
        '<table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" min-width="600">'
    )
    startWholeHtmlList.append('<tr>')
    startWholeHtmlList.append('<td>')
    startWholeHtmlList.append(
        f'<div style="text-align: center; font-size: 48px; padding-top: 2%; padding-bottom: 2%"><b>Infra operation report</b></div>'
    )
    startWholeHtmlList.append('</td>')
    startWholeHtmlList.append('</tr>')
    startServiceMapList.append('<tr>')
    startServiceMapList.append('<td>')
    startServiceMapList.append('<!--[if mso]>')
    startServiceMapList.append(
        '<table class="serviceMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startServiceMapList.append('<![endif]-->')
    startServiceMapList.append('<!--[if !mso]><!---->')
    startServiceMapList.append(
        '<table class="serviceMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600px;">'
    )
    startServiceMapList.append('<!-- <![endif]-->')
    startServiceMapList.append(
        f'<thead><tr><th style="width:100%" colspan="{serviceMapLength}">Services map</th></tr></thead>'
    )
    endServiceMapList.append(
        '</table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    )
    endServiceMapList.append('</td>')
    endServiceMapList.append('</tr>')
    startBasicInfoHtmlList.append('<tr>')
    startBasicInfoHtmlList.append('<td>')
    startBasicInfoHtmlList.append('<!--[if mso]>')
    startBasicInfoHtmlList.append(
        '<table class="serviceMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startBasicInfoHtmlList.append('<![endif]-->')
    startBasicInfoHtmlList.append('<!--[if !mso]><!---->')
    startBasicInfoHtmlList.append(
        '<table class="serviceMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600px;">'
    )
    startBasicInfoHtmlList.append('<!-- <![endif]-->')
    startBasicInfoHtmlList.append(
        f'<thead><tr><th style="width:100%" colspan="2">Basic information</th></tr></thead>'
    )
    endBasicInfoHtmlList.append(
        '</table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    )
    endBasicInfoHtmlList.append('</td>')
    endBasicInfoHtmlList.append('</tr>')
    startMtnList.append('<tr><td>')
    startMtnList.append('<!--[if mso]>')
    startMtnList.append(
        '<table class="mtnMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startMtnList.append('<![endif]-->')
    startMtnList.append('<!--[if !mso]><!---->')
    startMtnList.append(
        '<table class="mtnMap" style="border-spacing:0;Margin:0;padding:20px 20px 20px 20px;width:100%;min-width:600px;">'
    )
    startMtnList.append('<!-- <![endif]-->')
    startMtnList.append(
        '<thead><tr><th colspan="5">Maintenance</th></tr></thead>')
    startMtnList.append('<tbody>')
    frontMtnListHtml = "".join(startMtnList)
    closeMtnListHtml = '</tbody></table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    startYellowEventList.append('<tr>')
    startYellowEventList.append('<td>')
    startYellowEventList.append('<!--[if mso]>')
    startYellowEventList.append(
        '<table class="eventTable" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startYellowEventList.append('<![endif]-->')
    startYellowEventList.append('<!--[if !mso]><!---->')
    startYellowEventList.append(
        '<table class="eventTable" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600px;">'
    )
    startYellowEventList.append('<!-- <![endif]-->')
    startYellowEventList.append(
        f'<thead><tr><th style="width:100%" colspan="2">Mitigated event</th></tr></thead>'
    )
    endYellowEventList.append(
        '</table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    )
    endYellowEventList.append('</td>')
    endYellowEventList.append('</tr>')
    startRedEventList.append('<tr>')
    startRedEventList.append('<td>')
    startRedEventList.append('<!--[if mso]>')
    startRedEventList.append(
        '<table class="eventTable" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startRedEventList.append('<![endif]-->')
    startRedEventList.append('<!--[if !mso]><!---->')
    startRedEventList.append(
        '<table class="eventTable" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600px;">'
    )
    startRedEventList.append('<!-- <![endif]-->')
    startRedEventList.append(
        f'<thead><tr><th style="width:100%" colspan="2">Unclosed event</th></tr></thead>'
    )
    endRedEventList.append(
        '</table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    )
    endRedEventList.append('</td>')
    endRedEventList.append('</tr>')
    startYellowEventHtml = "".join(startYellowEventList)
    endYellowEventHtml = "".join(endYellowEventList)
    startRedEventHtml = "".join(startRedEventList)
    endRedEventHtml = "".join(endRedEventList)
    endWholeHtmlList.append('</table>')
    endWholeHtmlList.append('</body></html>')
    frontHtml = "".join(startWholeHtmlList)
    closeHtml = "".join(endWholeHtmlList)
    startbuHtml = "".join(startServiceMapList)
    endbuHtml = "".join(endServiceMapList)
    startBasicInfoHtml = "".join(startBasicInfoHtmlList)
    endBasicInfoHtml = "".join(endBasicInfoHtmlList)
    returnHtml = frontHtml + startBasicInfoHtml + basicInfoHtml + endBasicInfoHtml + startbuHtml + buhtmltable + endbuHtml
    if isNeedToInsertIssueMitigated:
        returnHtml = returnHtml + startYellowEventHtml + yellowEventHtml + endYellowEventHtml
    if isNeedToInsertUnclosedIssue:
        returnHtml = returnHtml + startRedEventHtml + redEventHtml + endRedEventHtml

    # if carry the date and shift, means just review
    if customQuery:
        summaryZone = classObject.getSummaryNote(
        ) + classObject.getSummaryOTRS()
        startSummaryList = []
        startSummaryList.append('<tr><td>')
        startSummaryList.append('<!--[if mso]>')
        startSummaryList.append(
            '<table class="operationMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
        )
        startSummaryList.append('<![endif]-->')
        startSummaryList.append('<!--[if !mso]><!---->')
        startSummaryList.append(
            '<table class="operationMap" style="border-spacing:0;Margin:0;padding:20px 20px 20px 20px;width:100%;min-width:600px;">'
        )
        startSummaryList.append('<!-- <![endif]-->')
        startSummaryList.append(
            '<thead><tr><th style="width:100%" colspan="5">Operation summary</th></tr></thead>'
        )
        startSummaryList.append(
            '<tbody><tr><th style="width:14%"><font color="#000000"><b>Unit</b></font></th><th style="width:14%"><font color="#000000"><b>Total</b></font></th><th style="width:24%"><font color="#000000"><b>New</b></font></th><th style="width:24%"><font color="#000000"><b>Update</b></font></th><th style="width:24%"><font color="#000000"><b>Closed</b></font></th></tr>'
        )
        frontSummaryListHtml = "".join(startSummaryList)
        closeSummaryListHtml = '</tbody></table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
        returnHtml = returnHtml + frontMtnListHtml + newMtnZone + closeMtnListHtml + frontSummaryListHtml + summaryZone + closeSummaryListHtml + closeHtml
        # outPutDate = f'{date.year}-{date.month}-{date.day}'
        # return jsonify([returnHtml, outPutDate, shift])
        return returnHtml
    else:
        returnHtml = returnHtml + frontMtnListHtml + newMtnZone + closeMtnListHtml + closeHtml
        # do the db copy
        # create the handover report ( docx file ) ***
        try:
            fullReportPath = exportword(date, shift, 'F')
        except Exception as e:
            print(e)
            print('get issue during export the word for full report')

        try:
            briefReportPath = exportword(date, shift, 'B')
        except Exception as e:
            print(e)
            print('get issue during export the word for brief report')

        # start to send the email by Flask Mail
        mail = Mail(current_app)
        msg = Message(
            f'[NDHS][{date}-{shift}] Infra Operation Report',
            sender="ops-infra-report@myggpro.com",
            # recipients=["gary.wu@yitmh.com"],
            recipients=[
                "ops@yitmh.com", "net@yitmh.com", "roxy.wang@yitmh.com"
            ],
            charset="utf-8")
        msg.html = returnHtml

        # check attachment
        attachmentZone = classObject.getAttachment()
        try:
            if len(attachmentZone) != 0:
                script_dir = os.path.dirname(os.getcwd(
                ))  # get root folder dir name - /home/ops/handover/backend
                # rel_path = "code/static/notes/2022-02-07/M/36001/1.png" # after root folder path
                # abs_file_path = os.path.join(script_dir, rel_path) # using abs path to get file - /home/ops/handover/backend/code/static/notes/2022-02-07/M/36001/1.png

                for i in attachmentZone:
                    # ( fileName, fileType, filePath )
                    rel_path = 'code/static/' + i[2]
                    abs_file_path = os.path.join(script_dir, rel_path)
                    with open(abs_file_path, 'rb') as fp:
                        msg.attach(i[0], i[1], fp.read())
            else:
                print('no attachment has been found on this shift')
        except Exception as e:
            print(e)
            print(
                'i think it is due to old dhs attachment file location cause this error'
            )
        # *** for word covert
        # with app_mainEmail.open_resource(fullReportPath) as fp:
        #     msg.attach(
        #         "reportFull.docx",
        #         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        #         fp.read())
        # *** for word covert
        # with app_mainEmail.open_resource(briefReportPath) as fp:
        #     msg.attach(
        #         "reportBrief.docx",
        #         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        #         fp.read())
        with app_mainEmail.open_resource(fullReportPath) as fp:
            msg.attach(
                "reportFull.html",
                "text/html",
                fp.read())
        with app_mainEmail.open_resource(briefReportPath) as fp:
            msg.attach(
                "reportBrief.html",
                "text/html",
                fp.read())
        mail.send(msg)

        # backend insert new Data
        # start to update the handover backend DB
        nextDate = date
        if shift == 'M':
            nextShift = 'A'
            curDateObject = datetime.datetime.strptime(
                f'{date.year}-{date.month}-{date.day}', "%Y-%m-%d")
            nextDateJira = curDateObject.strftime("%Y%m%d")
        elif shift == 'A':
            nextShift = 'N'
            curDateObject = datetime.datetime.strptime(
                f'{date.year}-{date.month}-{date.day}', "%Y-%m-%d")
            nextDateJira = curDateObject.strftime("%Y%m%d")
        elif shift == 'N':
            nextShift = 'M'
            curDateObject = datetime.datetime.strptime(
                f'{date.year}-{date.month}-{date.day}', "%Y-%m-%d")
            curDateUnix = datetime.datetime.timestamp(curDateObject)
            nextDateUnix = curDateUnix + 86400
            nextDateObject = datetime.datetime.fromtimestamp(nextDateUnix)
            nextDate = nextDateObject.strftime("%Y-%m-%d")
            nextDateJira = nextDateObject.strftime("%Y%m%d")

        # checkbox table
        insertCheckboxNewRow = get_handover_checkbox(date=nextDate,
                                                     shift=nextShift)
        db.session.add(insertCheckboxNewRow)
        db.session.commit()
        db.session.close()
        # update the customer status, adjust to 1 for Internal column
        updateCustomerStatusInternal = get_handover_customer_status.query.filter(
            get_handover_customer_status.date == date,
            get_handover_customer_status.shift == shift).first()
        updateCustomerStatusInternal.Internal = 1
        db.session.commit()
        db.session.close()
        # create the new row
        insertCustomerStatusNewRow = get_handover_customer_status(
            date=nextDate, shift=nextShift)
        db.session.add(insertCustomerStatusNewRow)
        db.session.commit()
        db.session.close()

        # get current customer status
        # get db row
        getCustomerStatus = get_handover_customer_status.query.filter(
            get_handover_customer_status.date == date,
            get_handover_customer_status.shift == shift).first()
        for k, v in getCustomerStatus.serialize.items():
            if v == 'Red':
                updateNextShiftCustomerStatus = get_handover_customer_status.query.filter(
                    get_handover_customer_status.date == nextDate,
                    get_handover_customer_status.shift == nextShift).first()
                if k == '_188A':
                    updateNextShiftCustomerStatus._188A = 'Red'
                    db.session.commit()
                elif k == 'SBK':
                    updateNextShiftCustomerStatus.SBK = 'Red'
                    db.session.commit()
                elif k == 'LDR':
                    updateNextShiftCustomerStatus.LDR = 'Red'
                    db.session.commit()
                elif k == 'KENO':
                    updateNextShiftCustomerStatus.KENO = 'Red'
                    db.session.commit()
                elif k == 'CAS':
                    updateNextShiftCustomerStatus.CAS = 'Red'
                    db.session.commit()
                elif k == 'Others':
                    updateNextShiftCustomerStatus.Others = 'Red'
                    db.session.commit()
        db.session.close()
        db.session.remove()

        # check customer status note, if status == 'red', will clone to next shift
        get_all_red_event = get_customer_status_note.query.filter(
            get_customer_status_note.date == date,
            get_customer_status_note.shift == shift,
            get_customer_status_note.status == 'Red').all()

        if len(get_all_red_event) != 0:
            for i in get_all_red_event:
                insertDb = get_customer_status_note(
                    date=nextDate,
                    shift=nextShift,
                    customer=i.customer,
                    note=i.note,
                    impactby=i.impactby,
                    egset=i.egset,
                    status=i.status,
                    event_start_time=i.event_start_time,
                    event_end_time=i.event_end_time,
                    outage_time=i.outage_time,
                    jira_ticket=i.jira_ticket)
                db.session.add(insertDb)
                db.session.commit()
                db.session.refresh(insertDb)
            db.session.close()
            db.session.remove()

        # <clone note> ####
        curNoteList = get_handover_notes.query.filter(
            get_handover_notes.shift == shift, get_handover_notes.date == date,
            get_handover_notes.sequence != 99).order_by(
                get_handover_notes.sequence).all()
        newNoteList = []
        for i in curNoteList:
            tmpDict = {}
            # summary part
            if (i.update_summary != '') and (i.update_summary != 'New') and (
                    i.update_summary != None):
                ## check if update_summary has been updated
                if i.summary == "":
                    tmpDict['summary'] = i.update_summary
                else:
                    tmpDict['summary'] = f'{i.summary}<br>{i.update_summary}'
            else:
                # means no update for this note
                tmpDict['summary'] = i.summary
            tmpDict['date'] = nextDate
            tmpDict['shift'] = nextShift
            tmpDict['shift'] = nextShift
            tmpDict['sequence'] = i.sequence
            tmpDict['status'] = 0
            tmpDict['customer'] = i.customer
            if i.kpi_group:
                tmpDict['kpi_group'] = i.kpi_group
            newNoteList.append(tmpDict)

        for x in newNoteList:
            tmpObject = get_handover_notes(**x)
            db.session.add(tmpObject)
        db.session.commit()
        db.session.close()

        # <clone otrs ticket> ####
        curTicketList = get_handover_otrs.query.filter(
            get_handover_otrs.date == date, get_handover_otrs.shift == shift,
            get_handover_otrs.sequence != 99).order_by(
                get_handover_otrs.number).all()
        closeTicketList = get_handover_otrs_closeTable.query.filter(
            get_handover_otrs_closeTable.date == date,
            get_handover_otrs_closeTable.shift == shift,
            get_handover_otrs_closeTable.ticket_action != 'C_mail sent').all()
        clostTicketSnList = [x.ticket_sn for x in closeTicketList]
        newOTRSList = []
        for i in curTicketList:
            tmpDict = {}
            # summary
            if (i.update_summary != "") and (i.update_summary != 'New') and (
                    i.update_summary != None):
                if i.summary == "":
                    tmpDict['summary'] = i.update_summary
                else:
                    tmpDict['summary'] = f'{i.summary}<br>{i.update_summary}'
            else:
                tmpDict['summary'] = i.summary
            # check if ticket need to close
            if i.sn in clostTicketSnList:
                tmpDict['sequence'] = 99
            else:
                tmpDict['sequence'] = i.sequence

            tmpDict['date'] = nextDate
            tmpDict['shift'] = nextShift
            tmpDict['status'] = i.status
            tmpDict['customer'] = i.customer
            tmpDict['number'] = i.number
            tmpDict['subject'] = i.subject
            tmpDict['maintenance'] = i.maintenance
            newOTRSList.append(tmpDict)

        for x in newOTRSList:
            tmpObject = get_handover_otrs(**x)
            db.session.add(tmpObject)
        db.session.commit()
        db.session.close()
        db.session.remove()

        # # <clone jira ticket> ####
        # https://okta.opsware.xyz:9487/query/all_issues/systemQuery

        resultonDb = get_handover_jira_ticket_sysinfo.query.order_by(
            get_handover_jira_ticket_sysinfo.sn.desc()).first()
        oldDate = resultonDb.date
        oldShift = resultonDb.shift

        ### query old ticket data by old date and shift
        resultCurDb = get_handover_jira_ticket.query.filter(
            get_handover_jira_ticket.date == oldDate,
            get_handover_jira_ticket.shift == oldShift).order_by(
                get_handover_jira_ticket.sn).all()

        ### new list to store the change
        nextShiftDataList = []

        ### forloop for result for DB
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
            newDict = dict(date=nextDateJira,
                           shift=nextShift,
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
        db.session.remove()
        return 'Handover sent!'


@app_mainEmail.route('/exportSummaryTable')  # default for confirmPage
@app_mainEmail.route('/exportSummaryTable/<date>/<shift>'
                     )  # will let reviewPage see it
def exportSummaryTable(date=None, shift=None):
    if date == None and shift == None:
        print('do the query here')
        lastRow = get_handover_customer_status.query.order_by(
            get_handover_customer_status.sn.desc()).first()
        date = lastRow.date
        shift = lastRow.shift
        customQuery = False
    else:
        customQuery = True

    queryHumanResource = get_handover_shift_table.query.filter(
        get_handover_shift_table.date == date,
        get_handover_shift_table.shift == shift).first()

    try:
        recordStaff = ", ".join(json.loads(queryHumanResource.teammates))
    except Exception as e:
        print(e)
        recordStaff = ''

    print(recordStaff)

    classObject = GenerateEmail(date, shift)
    # first table service map
    buZone = classObject.getServiceStatus()
    # no need to add icp and monitoring system status
    # monitoringZone = classObject.getMonitoringStatus()
    # icpZone = classObject.getICPStatus()
    # second table - Operation summary
    # no need to add JIRA for now
    summaryZone = classObject.getSummaryNote() + classObject.getSummaryOTRS()
    # summaryZone = classObject.getSummaryNote() + classObject.getSummaryOTRS() + classObject.getSummaryJIRA()
    # third table - mtn
    mtnZone = classObject.getMtnOTRS()
    # detail, later
    # noteZone = classObject.getNote()
    # otrsZone = classObject.getOtrs()
    # container list
    startWholeHtmlList = []
    endWholeHtmlList = []
    startServiceMapList = []
    startSummaryList = []
    startMtnList = []
    startWholeHtmlList.append('<!DOCTYPE html><html>')
    startWholeHtmlList.append('<head>')
    startWholeHtmlList.append(
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">')
    startWholeHtmlList.append(
        '<meta name="viewport" content="width=device-width, initial-scale=1">')
    startWholeHtmlList.append(
        '<meta http-equiv="X-UA-Compatible" content="IE=edge">')
    startWholeHtmlList.append('<title>Handover review</title>')
    startWholeHtmlList.append('<style type="text/css">')
    startWholeHtmlList.append('''
                        body {
                            font-family: sans-serif;
                        }
                        table {
                            border-collapse: collapse;
                            font-family: sans-serif;
                        }
                        table .serviceMap {
                            color: gray;
                            border-bottom: 1px solid;
                        }
                        table .mtnMap td{
                            border-bottom: 1px solid;
                        }
                        table .serviceMap td{
                            border-bottom: 1px solid;
                        }
                        table .operationMap td{
                            color: gray;
                            border-bottom: 1px solid;
                        }
                        table thead {
                            background-color: #36304A;
                            color: #FFFFFF;
                        }
                        table thead th {
                            border-radius: 5px 5px 0 0;
                        }
                        table tbody tr th {
                            text-align: left;
                        }
                        table tbody tr th:first-child {
                            padding-left: 2%;
                        }
                        table tbody tr td:first-child {
                            padding-left: 2%;
                        }
                        table tbody tr td:last-child {
                            padding-right: 2%;
                        }
                        table tbody tr th:last-child {
                            padding-right: 2%;
                        }
                        table .serviceMap tbody tr:nth-of-type(odd) {
                            background-color: rgba(0, 0, 0, .05);
                        }
                        table .operationMap tbody tr:nth-of-type(odd) {
                            background-color: rgba(0, 0, 0, .05);
                        }
                        .topHead {
                            color: #FFFFFF;
                            background-color: #9D9D9D;
                        }
                        table .noteZone {
                        border-collapse: collapse;
                        }
                    ''')
    startWholeHtmlList.append('</style>')
    startWholeHtmlList.append('</head>')
    startWholeHtmlList.append(
        '<body style="margin:0; padding:0; background-color:#F2F2F2;">')
    startWholeHtmlList.append(
        '<table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" min-width="600">'
    )
    startWholeHtmlList.append('<tr>')
    startWholeHtmlList.append('<td>')
    startWholeHtmlList.append(
        f'<div style="text-align: right; padding-right: 2%;"><b>Staff on duty</b>: {recordStaff}</div>'
    )
    startWholeHtmlList.append('</td>')
    startWholeHtmlList.append('</tr>')
    startWholeHtmlList.append('<tr>')
    startWholeHtmlList.append('<td>')
    frontHtml = "".join(startWholeHtmlList)
    startServiceMapList.append('<!--[if mso]>')
    startServiceMapList.append(
        '<table class="serviceMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startServiceMapList.append('<![endif]-->')
    startServiceMapList.append('<!--[if !mso]><!---->')
    startServiceMapList.append(
        '<table class="serviceMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600px;">'
    )
    startServiceMapList.append('<!-- <![endif]-->')
    startServiceMapList.append(
        '<thead><tr><th style="width:100%" colspan="3">Services map</th></tr></thead>'
    )
    frontServiceMapHtml = "".join(startServiceMapList)
    closeServiceMapHtml = '</table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    startSummaryList.append('<tr><td>')
    startSummaryList.append('<!--[if mso]>')
    startSummaryList.append(
        '<table class="operationMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startSummaryList.append('<![endif]-->')
    startSummaryList.append('<!--[if !mso]><!---->')
    startSummaryList.append(
        '<table class="operationMap" style="border-spacing:0;Margin:0;padding:20px 20px 20px 20px;width:100%;min-width:600px;">'
    )
    startSummaryList.append('<!-- <![endif]-->')
    startSummaryList.append(
        '<thead><tr><th style="width:100%" colspan="5">Operation summary</th></tr></thead>'
    )
    startSummaryList.append(
        '<tbody><tr><th style="width:14%"><font color="#000000"><b>Unit</b></font></th><th style="width:14%"><font color="#000000"><b>Total</b></font></th><th style="width:24%"><font color="#000000"><b>New</b></font></th><th style="width:24%"><font color="#000000"><b>Update</b></font></th><th style="width:24%"><font color="#000000"><b>Closed</b></font></th></tr>'
    )
    frontSummaryListHtml = "".join(startSummaryList)
    closeSummaryListHtml = '</tbody></table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    startMtnList.append('<tr><td>')
    startMtnList.append('<!--[if mso]>')
    startMtnList.append(
        '<table class="mtnMap" style="border-spacing:0;Margin:0;padding:20 20 20 20;width:100%;min-width:600%;">'
    )
    startMtnList.append('<![endif]-->')
    startMtnList.append('<!--[if !mso]><!---->')
    startMtnList.append(
        '<table class="mtnMap" style="border-spacing:0;Margin:0;padding:20px 20px 20px 20px;width:100%;min-width:600px;">'
    )
    startMtnList.append('<!-- <![endif]-->')
    startMtnList.append(
        '<thead><tr><th colspan="5">Maintenance</th></tr></thead>')
    startMtnList.append('<tbody>')
    frontMtnListHtml = "".join(startMtnList)
    closeMtnListHtml = '</tbody></table></td></tr><tr><td style="font-size: 0; line-height: 0;" height="15">&nbsp;</td></tr>'
    endWholeHtmlList.append('</table>')
    endWholeHtmlList.append('</body></html>')
    closeHtml = "".join(endWholeHtmlList)
    returnHtml = frontHtml + frontServiceMapHtml + buZone + closeServiceMapHtml + frontMtnListHtml + mtnZone + closeMtnListHtml + frontSummaryListHtml + summaryZone + closeSummaryListHtml + closeHtml
    # then front end will use this list to build the q-dialog popup widnows
    if customQuery:
        return returnHtml
    else:
        outPutDate = f'{date.year}-{date.month}-{date.day}'
        return jsonify([returnHtml, outPutDate, shift])

# @app_mainEmail.route('/tmp/adjust/comment')
# def reviewPageQueryJsmDetail():
#     result = get_jsm_ops_comments.query.all()
#     for i in result:
#         i.commentType = 1
#         db.session.commit()
#     db.session.close()
#     return 'ok'