from dataclasses import dataclass
from flask import Flask
from sqlalchemy.sql.elements import Null
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevConfig, Config
from sqlalchemy import inspect
from sqlalchemy.dialects.mysql import LONGTEXT
import collections
import datetime
import json

db = SQLAlchemy()


class get_handover_customer_status(db.Model):
    __bind_key__ = 'toHandover'
    __tablename__ = 'customer_status'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    shift = db.Column(db.String(16))
    Internal = db.Column(db.String(16), default='')
    _188A = db.Column('188A', db.String(16), default='Green')
    SBK = db.Column(db.String(16), default='Green')
    LDR = db.Column(db.String(16), default='Green')
    KENO = db.Column(db.String(16), default='Green')
    CAS = db.Column(db.String(16), default='Green')
    GICT = db.Column(db.String(16), default='Green')
    Others = db.Column(db.String(16), default='Green')

    # def __getitem__(self, field):
    #     return self.__dict__[field]

    # def __setitem__(self, item, value):
    #     self.__dict__[item] = value

    @property
    def serialize(self):
        returnOrderDict = collections.OrderedDict()
        # returnOrderDict["sn"] = self.sn
        # returnOrderDict["date"] = self.date
        # returnOrderDict["shift"] = self.shift
        returnOrderDict["_188A"] = self._188A
        returnOrderDict["SBK"] = self.SBK
        returnOrderDict["LDR"] = self.LDR
        returnOrderDict["KENO"] = self.KENO
        # returnOrderDict["CAS"] = self.CAS
        returnOrderDict["GICT"] = self.GICT
        returnOrderDict["Others"] = self.Others
        return returnOrderDict


class get_handover_notes(db.Model):
    __bind_key__ = 'toHandover'
    __tablename__ = 'notes'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    shift = db.Column(db.String(1))
    sequence = db.Column(db.Integer)
    status = db.Column(db.Integer)
    customer = db.Column(db.String(500))
    summary = db.Column(db.Text)
    update_summary = db.Column(db.Text, nullable=True, default=None)
    update_by = db.Column(db.String(16), default=None)
    check_image = db.Column(db.Integer, default=None)
    kpi_group = db.Column(db.Integer, default=None)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "shift": self.shift,
            "sequence": self.sequence,
            "status": self.status,
            "customer": self.customer,
            "summary": self.summary,
            "update_summary": self.update_summary,
            "update_by": self.update_by,
            "check_image": self.check_image,
            "kpi_group": self.kpi_group
        }
    
    @property
    def serialize_sort_out(self):
        if self.update_summary:
            return {
                "sn": self.sn,
                "date": self.date,
                "shift": self.shift,
                "sequence": self.sequence,
                "status": self.status,
                "customer": self.customer,
                "summary": self.summary,
                "update_summary": self.update_summary
            }
        else:
            return {
                "sn": self.sn,
                "date": self.date,
                "shift": self.shift,
                "sequence": self.sequence,
                "status": self.status,
                "customer": self.customer,
                "summary": self.summary,
                "update_summary": 'None'
            }

class get_handover_otrs(db.Model):
    __bind_key__ = 'toHandover'
    __tablename__ = 'ticket'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    shift = db.Column(db.String(1))
    sequence = db.Column(db.Integer)
    status = db.Column(db.Integer)
    customer = db.Column(db.String(16))
    number = db.Column(db.Integer)
    subject = db.Column(db.String(550))
    summary = db.Column(db.Text)
    update_summary = db.Column(db.Text, nullable=True, default=None)
    maintenance = db.Column(db.Integer)
    update_by = db.Column(db.String(16), nullable=True, default=None)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "shift": self.shift,
            "sequence": self.sequence,
            "status": self.status,
            "customer": self.customer,
            "number": self.number,
            "subject": self.subject,
            "summary": self.summary,
            "update_summary": self.update_summary,
            "maintenance": self.maintenance,
            "update_by": self.update_by
        }


class get_handover_otrs_closeTable(db.Model):
    __bind_key__ = 'toHandover'
    __tablename__ = 'close_ticket'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    shift = db.Column(db.String(1))
    ticket_sn = db.Column(db.Integer)
    ticket_action = db.Column(db.String(16))

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "shift": self.shift,
            "ticket_sn": self.ticket_sn,
            "ticket_action": self.ticket_action
        }


class get_handover_checkbox(db.Model):
    __bind_key__ = 'toHandover'
    __tablename__ = 'checkbox'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    shift = db.Column(db.String(1))


class get_handover_kpi_result(db.Model):
    __bind_key__ = 'toHandover'
    __tablename__ = 'kpi_result'
    sn = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    resolve_status = db.Column(db.Boolean, default=False)
    handler = db.Column(db.String(500))
    handler_second = db.Column(db.String(500), nullable=True)
    participant = db.Column(db.String(500), nullable=True)
    origin_source = db.Column(db.String(10))
    origin_source_subject = db.Column(db.String(300))
    related_sn = db.Column(db.Integer)
    related_date = db.Column(db.String(10))
    related_shift = db.Column(db.String(1))
    related_group = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(1000), nullable=True)

    @property
    def serialize(self):
        if self.participant:
            handler_second_format = json.loads(self.handler_second)
        else:
            handler_second_format = None
        if self.participant:
            participant_format = json.loads(self.participant)
        else:
            participant_format = None
        return {
            "sn": self.sn,
            "type": self.type,
            "resolve_status": self.resolve_status,
            "handler": self.handler.split(','),
            "handler_second": handler_second_format,
            "participant": participant_format,
            "origin_source": self.origin_source,
            "origin_source_subject": self.origin_source_subject,
            "related_sn": self.related_sn,
            "related_date": self.related_date,
            "related_shift": self.related_shift,
            "related_group": self.related_group,
            "description": self.description,
            "file_path": self.file_path
        }

    @property
    def serialize_origin(self):
        return {
            "sn": self.sn,
            "type": self.type,
            "resolve_status": self.resolve_status,
            "handler": self.handler.split(','),
            "handler_second": self.handler_second,
            "participant": self.participant,
            "origin_source": self.origin_source,
            "origin_source_subject": self.origin_source_subject,
            "related_sn": self.related_sn,
            "related_date": self.related_date,
            "related_shift": self.related_shift,
            "related_group": self.related_group,
            "description": self.description,
            "file_path": self.file_path
        }


class get_handover_jira_ticket(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'ticket_jira'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    shift = db.Column(db.String(10))
    seq = db.Column(db.Integer)
    ticketName = db.Column(db.String(1000))
    issueId = db.Column(db.Integer)
    lastEditor = db.Column(db.String(20))
    summary = db.Column(db.Text)
    updateSummary = db.Column(db.Text)
    attachmentList = db.Column(db.Text)
    flagMtn = db.Column(db.Boolean, default=0)
    flagUnderEdit = db.Column(db.Boolean, default=0)
    flagTicketStatus = db.Column(
        db.Integer, default=0
    )  #0>newTicket, 1>oldTicket, 2>pending_Close, 3> close_directly
    flagJiraTicketStatus = db.Column(db.String(20))
    flagKpiSn = db.Column(db.Integer)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "shift": self.shift,
            "seq": self.seq,
            "ticketName": self.ticketName,
            "issueId": self.issueId,
            "lastEditor": self.lastEditor,
            "summary": self.summary,
            "updateSummary": self.updateSummary,
            "attachmentList ": self.attachmentList,
            "flagMtn": self.flagMtn,
            "flagUnderEdit": self.flagUnderEdit,
            "flagTicketStatus": self.flagTicketStatus,
            "flagJiraTicketStatus": self.flagJiraTicketStatus,
            "flagKpiSn": self.flagKpiSn
        }


class get_handover_jira_key_id_mapping(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jira_key_id_mapping'
    sn = db.Column(db.Integer, primary_key=True)
    _key = db.Column(db.String(10))
    _id = db.Column(db.Integer)
    url = db.Column(db.String(150))
    createdAt = db.Column(db.DateTime)
    flagClose = db.Column(db.Boolean, default=0)
    commentList = db.Column(db.Text)


class get_handover_ticket_mtn_mapping(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'ticket_mtn_mapping'
    sn = db.Column(db.Integer, primary_key=True)
    relatedJiraIssueId = db.Column(db.Integer)
    googleCalendarId = db.Column(db.String(200))
    googleCalendarLink = db.Column(db.String(500))
    startTime = db.Column(db.DateTime, default=None)
    endTime = db.Column(db.DateTime, default=None)
    _type = db.Column(db.String(50), default=None)
    _status = db.Column(db.String(50), default=None)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "relatedJiraIssueId": self.relatedJiraIssueId,
            "googleCalendarId": self.googleCalendarId,
            "googleCalendarLink": self.googleCalendarLink,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "_type": self._type,
            "_status": self._status
        }


class get_handover_jira_ticket_sysinfo(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jira_sysinfo'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    shift = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime)
    listTotal = db.Column(db.Text)
    listOpen = db.Column(db.Text)
    listInprocess = db.Column(db.Text)
    listUnderInvestigation = db.Column(db.Text)
    listCanceled = db.Column(db.Text)
    listCompleted = db.Column(db.Text)
    listResolved = db.Column(db.Text)
    listNew = db.Column(db.Text)
    listStatusChange = db.Column(db.Text)
    countTotal = db.Column(db.Integer)
    countOpen = db.Column(db.Integer)
    countInprocess = db.Column(db.Integer)
    countUnderInvestigation = db.Column(db.Integer)
    countCanceled = db.Column(db.Integer)
    countCompleted = db.Column(db.Integer)
    countResolved = db.Column(db.Integer)
    countNew = db.Column(db.Integer)
    countStatusChange = db.Column(db.Integer)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "shift": self.shift,
            "timestamp": self.timestamp,
            "listTotal": json.loads(self.listTotal),
            "listOpen": json.loads(self.listOpen),
            "listInprocess": json.loads(self.listInprocess),
            "listUnderInvestigation": json.loads(self.listUnderInvestigation),
            "listCanceled": json.loads(self.listCanceled),
            "listCompleted": json.loads(self.listCompleted),
            "listResolved": json.loads(self.listResolved),
            "listNew": json.loads(self.listNew),
            "listStatusChange": json.loads(self.listStatusChange),
            "countTotal": self.countTotal,
            "countOpen": self.countOpen,
            "countInprocess": self.countInprocess,
            "countUnderInvestigation": self.countUnderInvestigation,
            "countCanceled": self.countCanceled,
            "countCompleted": self.countCompleted,
            "countResolved": self.countResolved,
            "countNew": self.countNew,
            "countStatusChange": self.countStatusChange,
        }


class get_handover_user_controller(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'user_controller'
    sn = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    controllerCustomerStatus = db.Column(db.String(20))
    controllerCalendar = db.Column(db.String(20))
    controllerMontoringService = db.Column(db.String(20))
    controllerICPStatus = db.Column(db.String(20))
    controllerNote = db.Column(db.String(20))
    controllerTicket = db.Column(db.String(20))
    controllerOTRS = db.Column(db.String(20))
    controllerFavorite = db.Column(db.Text, nullable=True)
    lastTimeUpdate = db.Column(db.DateTime)

    @property
    def serialize(self):
        return {
            "controllerCustomerStatus":
            json.loads(self.controllerCustomerStatus),
            "controllerCalendar":
            json.loads(self.controllerCalendar),
            "controllerMontoringService":
            json.loads(self.controllerMontoringService),
            "controllerICPStatus":
            json.loads(self.controllerICPStatus),
            "controllerNote":
            json.loads(self.controllerNote),
            "controllerTicket":
            json.loads(self.controllerTicket),
            "controllerFavorite":
            json.loads(self.controllerFavorite)
        }


class get_handover_hyperlink_sre_page(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'hyperlink_sre_page'
    sn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    caption = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    link = db.Column(db.String(1000))
    counter = db.Column(db.Integer)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "title": self.title,
            "caption": self.caption,
            "icon": self.icon,
            "link": self.link,
            "counter": self.counter
        }


class get_handover_health_map(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'health_map'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    shift = db.Column(db.String(1))
    WhatsUpGold = db.Column(db.Text, nullable=True)
    PRTG_SUN = db.Column(db.Text, nullable=True)
    PRTG_FRI = db.Column(db.Text, nullable=True)
    JKB = db.Column(db.Text, nullable=True)
    PageDuty = db.Column(db.Text, nullable=True)
    HM93 = db.Column(db.Text, nullable=True)
    HM94 = db.Column(db.Text, nullable=True)
    HM81 = db.Column(db.Text, nullable=True)
    HM82 = db.Column(db.Text, nullable=True)
    Ver = db.Column(db.Integer)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "shift": self.shift,
            "WhatsUpGold": self.WhatsUpGold,
            "PRTG_SUN": self.PRTG_SUN,
            "PRTG_FRI": self.PRTG_FRI,
            "JKB": self.JKB,
            "PageDuty": self.PageDuty,
            "HM93": self.HM93,
            "HM94": self.HM94,
            "HM81": self.HM81,
            "HM82": self.HM82,
            "Ver": self.Ver
        }


class get_handover_notes_attachment(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'notes_attachment'
    sn = db.Column(db.Integer, primary_key=True)
    noteSn = db.Column(db.Integer)
    fileName = db.Column(db.String(150))
    fileType = db.Column(db.String(50))
    filePath = db.Column(db.Text)
    fileCounter = db.Column(db.Integer)
    updater = db.Column(db.String(150))

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "noteSn": self.noteSn,
            "fileName": self.fileName,
            "fileType": self.fileType,
            "filePath": self.filePath,
            "fileCounter": self.fileCounter,
            "updater": self.updater
        }


class get_handover_shift_table(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'shift_table'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    shift = db.Column(db.String(1))
    teammates = db.Column(db.String(200))
    shift_leader = db.Column(db.String(200), nullable=True)
    title_handover = db.Column(db.String(1000), nullable=True)
    title_alert_handler = db.Column(db.String(1000), nullable=True)
    title_message_handler = db.Column(db.String(1000), nullable=True)
    title_request_handler = db.Column(db.String(1000), nullable=True)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "shift": self.shift,
            "teammates": self.teammates
        }
    @property
    def serialize_shift(self):
        return {
            "shift_leader": self.shift_leader,
            "title_handover": json.loads(self.title_handover),
            "title_alert_handler": json.loads(self.title_alert_handler),
            "title_message_handler": json.loads(self.title_message_handler),
            "title_request_handler": json.loads(self.title_request_handler)
        }

    @property
    def serialize_review_handler(self):
        return {
            "sn": self.sn,
            "shift_leader": self.shift_leader,
            "title_handover": json.loads(self.title_handover),
            "title_alert_handler": json.loads(self.title_alert_handler),
            "title_message_handler": json.loads(self.title_message_handler),
            "title_request_handler": json.loads(self.title_request_handler),
            "date": self.date.strftime('%Y-%m-%d'),
            "shift": self.shift
        }


class get_customer_status_note(db.Model):
    __bind_key__ = 'toHandover'
    __tablename__ = 'customer_status_note'
    sn = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    shift = db.Column(db.String(1))
    customer = db.Column(db.String(1000))
    note = db.Column(db.String(100))
    impactby = db.Column(db.String(1000))
    egset = db.Column(db.String(10))
    status = db.Column(db.String(10))
    event_start_time = db.Column(db.DateTime, nullable=True)
    event_end_time = db.Column(db.DateTime, nullable=True)
    outage_time = db.Column(db.Integer, nullable=True)
    jira_ticket = db.Column(db.String(100), nullable=True)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "date": self.date,
            "customer": self.customer,
            "note": self.note,
            "impactby": self.impactby,
            "egset": self.egset,
            "status": self.status,
            "event_start_time": self.event_start_time,
            "event_end_time": self.event_end_time,
            "outage_time": self.outage_time,
            "jira_ticket": self.jira_ticket,
        }


class get_jsm_ops(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_ops'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime, nullable=True)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    custom_infra = db.Column(db.String(255))
    custom_bizUnit = db.Column(db.String(255))
    custom_category = db.Column(db.String(255))
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    mapping = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        tmpDict = {
            "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            "custom_infra": json.loads(self.custom_infra),
            "custom_category": self.custom_category,
            "custom_bizUnit": json.loads(self.custom_bizUnit),
            "custom_handler": json.loads(self.custom_handler),
            "title": self.title,
            "description": self.description,
            "mapping": self.mapping
        }
        if self.custom_participant:
            tmpDict.setdefault("custom_participant",
                               json.loads(self.custom_participant))
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        return tmpDict


class get_jsm_ops_prod(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_ops_prod'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime, nullable=True)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(2000), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    relations = db.Column(db.String(255), nullable=True)
    custom_infra = db.Column(db.String(255))
    custom_bizUnit = db.Column(db.String(255))
    custom_category = db.Column(db.String(255))
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    content_raw = db.Column(db.Text, nullable=True)
    content_html = db.Column(db.Text, nullable=True)
    mapping = db.Column(db.Integer, nullable=True)
    mtn = db.Column(db.Boolean, default=0)

    @property
    def serialize(self):
        tmpDict = {
            "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            "custom_infra": json.loads(self.custom_infra),
            "custom_category": self.custom_category,
            "custom_bizUnit": json.loads(self.custom_bizUnit),
            "custom_handler": json.loads(self.custom_handler),
            "title": self.title,
            "description": self.description,
            "content_html": self.content_html,
            "mapping": self.mapping,
            "mtn": self.mtn
        }
        if self.custom_participant:
            tmpDict.setdefault("custom_participant",
                               json.loads(self.custom_participant))
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        if self.relations:
            tmpDict.setdefault("relations",
                               json.loads(self.relations))
        else:
            tmpDict.setdefault("relations", self.relations)
        
        return tmpDict
    
    @property
    def serialize_sort_out(self):
        return {
            "sn": self.sn,
            "title": self.title,
            "description": self.description
        }


class get_jsm_net(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_net'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime, nullable=True)
    endTime = db.Column(db.DateTime, nullable=True)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    custom_infra = db.Column(db.String(255))
    custom_category = db.Column(db.String(255))
    custom_facilities = db.Column(db.String(255))
    custom_vendor = db.Column(db.String(255), nullable=True)
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    title = db.Column(db.Text)
    description = db.Column(LONGTEXT)
    mapping = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        tmpDict = {
            "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            # "custom_infra": self.custom_infra,
            "custom_infra": json.loads(self.custom_infra),
            "custom_category": self.custom_category,
            # "custom_facilities": self.custom_facilities,
            "custom_facilities": json.loads(self.custom_facilities),
            # "custom_handler": self.custom_handler,
            "custom_handler": json.loads(self.custom_handler),
            "title": self.title,
            "description": self.description,
            "mapping": self.mapping
        }
        if self.custom_vendor:
            # tmpDict.setdefault("custom_vendor", self.custom_vendor)
            tmpDict.setdefault("custom_vendor", json.loads(self.custom_vendor))
        else:
            tmpDict.setdefault("custom_vendor", self.custom_vendor)
        if self.custom_participant:
            # tmpDict.setdefault("custom_participant", self.custom_participant)
            tmpDict.setdefault("custom_participant",
                               json.loads(self.custom_participant))
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        return tmpDict


class get_jsm_net_prod(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_net_prod'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime, nullable=True)
    endTime = db.Column(db.DateTime, nullable=True)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    custom_infra = db.Column(db.String(255))
    custom_category = db.Column(db.String(255))
    custom_facilities = db.Column(db.String(255))
    custom_vendor = db.Column(db.String(255), nullable=True)
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    title = db.Column(db.Text)
    description = db.Column(LONGTEXT)
    content_raw = db.Column(db.Text, nullable=True)
    content_html = db.Column(db.Text, nullable=True)
    mapping = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        tmpDict = {
            "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            "custom_infra": json.loads(self.custom_infra),
            "custom_category": self.custom_category,
            "custom_facilities": json.loads(self.custom_facilities),
            "custom_handler": json.loads(self.custom_handler),
            "title": self.title,
            "description": self.description,
            "content_html": self.content_html,
            "mapping": self.mapping
        }
        if self.custom_vendor:
            tmpDict.setdefault("custom_vendor", json.loads(self.custom_vendor))
        else:
            tmpDict.setdefault("custom_vendor", self.custom_vendor)
        if self.custom_participant:
            tmpDict.setdefault("custom_participant",
                               json.loads(self.custom_participant))
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        return tmpDict


class get_jsm_sys(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_sys'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime, nullable=True)
    endTime = db.Column(db.DateTime, nullable=True)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    custom_bizUnit = db.Column(db.String(255))
    custom_category = db.Column(db.String(255))
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    custom_priority = db.Column(db.String(20))
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    mapping = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        tmpDict = {
            # "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            "custom_bizUnit": self.custom_bizUnit,
            "custom_category": self.custom_category,
            "custom_handler": self.custom_handler,
            # "custom_bizUnit": json.loads(self.custom_bizUnit),
            # "custom_category": json.loads(self.custom_category),
            # "custom_handler": json.loads(self.custom_handler),
            "custom_priority": self.custom_priority,
            "title": self.title,
            "description": self.description,
            "mapping": self.mapping
        }
        if self.custom_participant:
            # tmpDict.setdefault("custom_participant", json.loads(self.custom_participant))
            tmpDict.setdefault("custom_participant", self.custom_participant)
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        return tmpDict


class get_jsm_sys_prod(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_sys_prod'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime, nullable=True)
    endTime = db.Column(db.DateTime, nullable=True)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    custom_bizUnit = db.Column(db.String(255))
    custom_category = db.Column(db.String(255))
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    custom_priority = db.Column(db.String(20))
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    content_raw = db.Column(db.Text, nullable=True)
    content_html = db.Column(db.Text, nullable=True)
    mapping = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        tmpDict = {
            "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            "custom_bizUnit": json.loads(self.custom_bizUnit),
            "custom_category": json.loads(self.custom_category),
            "custom_handler": json.loads(self.custom_handler),
            "custom_priority": self.custom_priority,
            "title": self.title,
            "description": self.description,
            "content_html": self.content_html,
            "mapping": self.mapping
        }
        if self.custom_participant:
            tmpDict.setdefault("custom_participant",
                               json.loads(self.custom_participant))
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        return tmpDict


class get_jsm_dba(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_dba'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    custom_bizUnit = db.Column(db.String(255))
    custom_category = db.Column(db.Text)
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    custom_priority = db.Column(db.String(20))
    custom_isImpact = db.Column(db.Boolean)
    custom_workLogId = db.Column(db.Integer, nullable=True)
    custom_workLogValue = db.Column(db.Integer, nullable=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    mapping = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        tmpDict = {
            "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime.strftime("%Y-%m-%d %H:%M"),
            "endTime": self.endTime.strftime("%Y-%m-%d %H:%M"),
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            "custom_bizUnit": json.loads(self.custom_bizUnit),
            "custom_category": json.loads(self.custom_category),
            "custom_handler": json.loads(self.custom_handler),
            "custom_priority": self.custom_priority,
            "custom_isImpact": self.custom_isImpact,
            "custom_workLogId": self.custom_workLogId,
            "custom_workLogValue": self.custom_workLogValue,
            "title": self.title,
            "description": self.description,
            "mapping": self.mapping
        }
        if self.custom_participant:
            tmpDict.setdefault("custom_participant",
                               json.loads(self.custom_participant))
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        return tmpDict


class get_jsm_dba_prod(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_dba_prod'
    sn = db.Column(db.Integer, primary_key=True)
    createdTime = db.Column(db.DateTime, default=datetime.datetime.now)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    jiraStatus = db.Column(db.Integer, nullable=True)
    ticketStatus = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    custom_bizUnit = db.Column(db.String(255))
    custom_category = db.Column(db.String(255))
    custom_handler = db.Column(db.String(255))
    custom_participant = db.Column(db.String(255), nullable=True)
    custom_priority = db.Column(db.String(20))
    custom_isImpact = db.Column(db.Boolean)
    custom_workLogId = db.Column(db.Integer, nullable=True)
    custom_workLogValue = db.Column(db.Integer, nullable=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    content_raw = db.Column(db.Text, nullable=True)
    content_html = db.Column(db.Text, nullable=True)
    mapping = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        tmpDict = {
            "sn": self.sn,
            "createdTime": self.createdTime,
            "startTime": self.startTime.strftime("%Y-%m-%d %H:%M"),
            "endTime": self.endTime.strftime("%Y-%m-%d %H:%M"),
            "jiraStatus": self.jiraStatus,
            "ticketStatus": self.ticketStatus,
            "comments": self.comments,
            "attachments": self.attachments,
            "custom_bizUnit": json.loads(self.custom_bizUnit),
            "custom_category": json.loads(self.custom_category),
            "custom_handler": json.loads(self.custom_handler),
            "custom_priority": self.custom_priority,
            "custom_isImpact": self.custom_isImpact,
            "custom_workLogId": self.custom_workLogId,
            "custom_workLogValue": self.custom_workLogValue,
            "title": self.title,
            "description": self.description,
            "content_html": self.content_html,
            "mapping": self.mapping
        }
        if self.custom_participant:
            tmpDict.setdefault("custom_participant",
                               json.loads(self.custom_participant))
        else:
            tmpDict.setdefault("custom_participant", self.custom_participant)
        return tmpDict


class get_jsm_dba_comments(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_dba_comments'
    sn = db.Column(db.Integer, primary_key=True)
    issueKey = db.Column(db.String(50))
    handler = db.Column(db.String(50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    jsmCommentId = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "handler": self.handler,
            "content": self.content,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class get_jsm_sys_comments(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_sys_comments'
    sn = db.Column(db.Integer, primary_key=True)
    issueKey = db.Column(db.String(50))
    handler = db.Column(db.String(50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    jsmCommentId = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "handler": self.handler,
            "content": self.content,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class get_jsm_net_comments(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_net_comments'
    sn = db.Column(db.Integer, primary_key=True)
    issueKey = db.Column(db.String(50))
    handler = db.Column(db.String(50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    jsmCommentId = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "handler": self.handler,
            "content": self.content,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class get_jsm_ops_comments(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_ops_comments'
    sn = db.Column(db.Integer, primary_key=True)
    issueKey = db.Column(db.String(50))
    handler = db.Column(db.String(50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    commentType = db.Column(db.Integer, nullable=True, default=1)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "handler": self.handler,
            "content": self.content,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "commentType": self.commentType
        }


class get_jsm_mapping(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_mapping'
    sn = db.Column(db.Integer, primary_key=True)
    issueId = db.Column(db.String(50))
    issueKey = db.Column(db.String(50))
    issueUrl = db.Column(db.String(255))
    _group = db.Column(db.String(10))

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "issueId": self.issueId,
            "issueKey": self.issueKey,
            "issueUrl": self.issueUrl,
            "_group": self._group
        }


class get_jsm_mapping_prod(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_mapping_prod'
    sn = db.Column(db.Integer, primary_key=True)
    issueId = db.Column(db.String(50))
    issueKey = db.Column(db.String(50))
    issueUrl = db.Column(db.String(255))
    _group = db.Column(db.String(10))

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "issueId": self.issueId,
            "issueKey": self.issueKey,
            "issueUrl": self.issueUrl,
            "_group": self._group
        }


class get_jsm_field_sets(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_field_sets'
    sn = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.String(50))
    optionName = db.Column(db.String(50))
    fieldId = db.Column(db.String(50))
    contextId = db.Column(db.Integer, nullable=True)
    value = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    @property
    def serialize(self):
        if self.value:
            return {
                "sn": self.sn,
                "env": self.env,
                "optionName": self.optionName,
                "fieldId": self.fieldId,
                "contextId": self.contextId,
                "value": json.loads(self.value),
                "timestamp": self.timestamp
            }
        else:
            return {
                "sn": self.sn,
                "env": self.env,
                "optionName": self.optionName,
                "fieldId": self.fieldId,
                "contextId": self.contextId,
                "value": self.value,
                "timestamp": self.timestamp
            }


class get_jsm_field_sets_sortOut(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'jsm_field_sets_sortOut'
    sn = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.String(50))
    optionName = db.Column(db.String(50))
    fieldId = db.Column(db.String(50))
    contextId = db.Column(db.Integer)
    _id = db.Column(db.String(255))
    _value = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "env": self.env,
            "optionName": self.optionName,
            "fieldId": self.fieldId,
            "contextId": self.contextId,
            "_id": self._id,
            "_value": self._value,
            "timestamp": self.timestamp
        }


class get_otrs_dba_ticket(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'otrs_dba'
    sn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean,
                       default=True)  # True is open, False is close
    comments = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    customerId = db.Column(db.String(255))
    ticketNumber = db.Column(db.Integer)
    createTime = db.Column(db.DateTime, default=datetime.datetime.now)
    custom_category = db.Column(db.String(255), nullable=True)
    custom_handler = db.Column(db.String(255), nullable=True)
    custom_participant = db.Column(db.String(255), nullable=True)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "comments": json.loads(self.comments),
            "attachments": json.loads(self.attachments),
            "customerId": self.customerId,
            "ticketNumber": self.ticketNumber,
            "custom_category": json.loads(self.custom_category),
            "custom_handler": json.loads(self.custom_handler),
            "custom_participant": json.loads(self.custom_participant),
            "createTime": f'{self.createTime}'
        }


class get_otrs_dba_ticket_comments(db.Model):
    __bind_key__ = 'toDHS'
    __tablename__ = 'otrs_dba_comments'
    sn = db.Column(db.Integer, primary_key=True)
    ticketNumber = db.Column(db.Integer)
    handler = db.Column(db.String(50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    commentType = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        return {
            "sn": self.sn,
            "ticketNumber": self.ticketNumber,
            "handler": self.handler,
            "content": self.content,
            "timestamp": self.timestamp,
            "commentType": self.commentType
        }


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevConfig)
    db.init_app(app)
    return app