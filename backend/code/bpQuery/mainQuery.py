from flask import Blueprint, jsonify
from models import get_jsm_mapping_prod, get_jsm_ops_comments, get_jsm_ops_prod, get_jsm_sys_prod, get_jsm_sys_comments, get_jsm_net_prod, get_jsm_net_comments, get_jsm_dba_prod, get_jsm_dba_comments
import json
from sqlalchemy import or_

app_mainQuery = Blueprint('app_mainQuery', __name__, static_folder='../static')

@app_mainQuery.route('/search/<target>')
def app_mainQuery_test(target):
    ## OPS ##
    ## check the raw html column - main table
    total_set = set()
    result_title = get_jsm_ops_prod.query.filter(or_(get_jsm_ops_prod.title.ilike(f'%{target}%'), get_jsm_ops_prod.description.ilike(f'%{target}%'), get_jsm_ops_prod.content_raw.ilike(f'%{target}%'))).limit(200).all()
    total_set.update(set(result_title))
    ## check the comments content - check commment table
    result_comment = get_jsm_ops_comments.query.filter(get_jsm_ops_comments.content.ilike(f'%{target}%')).limit(200).all()
    # get the mapping sn
    issuekey_from_comment = set([ x.sn for i in result_comment for x in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey == i.issueKey).all() ])
    current_issuekey_set = set([ i.mapping for i in total_set])
    # check the diff (a - b)
    unique_on_comment_set = issuekey_from_comment.difference(current_issuekey_set)
    # check the main table and write into total_set
    result_comments = set([ x for i in unique_on_comment_set for x in get_jsm_ops_prod.query.filter(get_jsm_ops_prod.mapping == i).all() ])
    total_set.update(result_comments)
    # check if the target is TICKET ISSUE KEY
    # need to check the group
    match_issuekey_full_target = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==target, get_jsm_mapping_prod._group == 'OPS').first()
    if match_issuekey_full_target:
        match_mapping_full_target = get_jsm_ops_prod.query.filter_by(mapping=match_issuekey_full_target.sn).all()
        total_set.update(set(match_mapping_full_target))

    ## SYS ##
    ## check the raw html column - main table
    total_set_sys = set()
    result_title_sys = get_jsm_sys_prod.query.filter(or_(get_jsm_sys_prod.title.ilike(f'%{target}%'), get_jsm_sys_prod.description.ilike(f'%{target}%'))).limit(200).all()
    total_set_sys.update(set(result_title_sys))
    ## check the comments content - check commment table
    result_comment_sys = get_jsm_sys_comments.query.filter(get_jsm_sys_comments.content.ilike(f'%{target}%')).limit(200).all()
    # get the mapping sn
    issuekey_from_comment_sys = set([ x.sn for i in result_comment_sys for x in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey == i.issueKey).all() ])
    current_issuekey_set_sys = set([ i.mapping for i in total_set_sys])
    # check the diff (a - b)
    unique_on_comment_set_sys = issuekey_from_comment_sys.difference(current_issuekey_set_sys)
    # check the main table and write into total_set
    result_comments_sys = set([ x for i in unique_on_comment_set_sys for x in get_jsm_sys_prod.query.filter(get_jsm_sys_prod.mapping == i).all() ])
    total_set_sys.update(result_comments_sys)
    # check if the target is TICKET ISSUE KEY
    match_issuekey_full_target_sys = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==target, get_jsm_mapping_prod._group == 'SYS').first()
    if match_issuekey_full_target_sys:
        match_mapping_full_target_sys = get_jsm_ops_prod.query.filter_by(mapping=match_issuekey_full_target_sys.sn).all()
        total_set_sys.update(set(match_mapping_full_target_sys))

    ## NET ##
    ## check the raw html column - main table
    total_set_net = set()
    result_title_net = get_jsm_net_prod.query.filter(or_(get_jsm_net_prod.title.ilike(f'%{target}%'), get_jsm_net_prod.description.ilike(f'%{target}%'))).limit(200).all()
    total_set_net.update(set(result_title_net))
    ## check the comments content - check commment table
    result_comment_net = get_jsm_net_comments.query.filter(get_jsm_net_comments.content.ilike(f'%{target}%')).limit(200).all()
    # get the mapping sn
    issuekey_from_comment_net = set([ x.sn for i in result_comment_net for x in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey == i.issueKey).all() ])
    current_issuekey_set_net = set([ i.mapping for i in total_set_net])
    # check the diff (a - b)
    unique_on_comment_set_net = issuekey_from_comment_net.difference(current_issuekey_set_net)
    
    # check the main table and write into total_set
    result_comments_net = set([ x for i in unique_on_comment_set_net for x in get_jsm_net_prod.query.filter(get_jsm_net_prod.mapping == i).all() ])
    total_set_net.update(result_comments_net)

    # check if the target is TICKET ISSUE KEY
    match_issuekey_full_target_net = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==target, get_jsm_mapping_prod._group == 'NET').first()
    if match_issuekey_full_target_net:
        match_mapping_full_target_net = get_jsm_net_prod.query.filter_by(mapping=match_issuekey_full_target_net.sn).all()
        total_set_net.update(set(match_mapping_full_target_net))

    ## DBA ##
    ## check the raw html column - main table
    total_set_dba = set()
    result_title_dba = get_jsm_dba_prod.query.filter(or_(get_jsm_dba_prod.title.ilike(f'%{target}%'), get_jsm_dba_prod.description.ilike(f'%{target}%'))).limit(200).all()
    total_set_dba.update(set(result_title_dba))
    ## check the comments content - check commment table
    result_comment_dba = get_jsm_dba_comments.query.filter(get_jsm_dba_comments.content.ilike(f'%{target}%')).limit(200).all()
    # get the mapping sn
    issuekey_from_comment_dba = set([ x.sn for i in result_comment_dba for x in get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey == i.issueKey).all() ])
    current_issuekey_set_dba = set([ i.mapping for i in total_set_dba])
    # check the diff (a - b)
    unique_on_comment_set_dba = issuekey_from_comment_dba.difference(current_issuekey_set_dba)
    
    # check the main table and write into total_set
    result_comments_dba = set([ x for i in unique_on_comment_set_dba for x in get_jsm_dba_prod.query.filter(get_jsm_dba_prod.mapping == i).all() ])
    total_set_dba.update(result_comments_dba)

    # check if the target is TICKET ISSUE KEY
    match_issuekey_full_target_dba = get_jsm_mapping_prod.query.filter(get_jsm_mapping_prod.issueKey==target, get_jsm_mapping_prod._group == 'DBA').first()
    if match_issuekey_full_target_dba:
        match_mapping_full_target_dba = get_jsm_dba_prod.query.filter_by(mapping=match_issuekey_full_target_dba.sn).all()
        total_set_dba.update(set(match_mapping_full_target_dba))

    result_dict = {}
    ops_list = []
    sys_list = []
    net_list = []
    dba_list = []
    for i in total_set:
        tmp_dict={}
        tmp_dict.setdefault("title",i.title)
        try:
            tmp_dict.setdefault("bizUnit", ', '.join(json.loads(i.custom_bizUnit)))
        except Exception as e:
            tmp_dict.setdefault("bizUnit",i.custom_bizUnit)
        tmp_dict.setdefault("category",i.custom_category)
        try:
            tmp_dict.setdefault("infra", ', '.join(json.loads(i.custom_infra)))
        except Exception as e:
            tmp_dict.setdefault("infra",i.custom_infra)
        tmp_dict.setdefault("description",i.description)
        tmp_dict.setdefault("mapping",i.mapping)
        tmp_dict.setdefault("sn",i.sn)
        tmp_dict.setdefault("createdTime",f'{i.createdTime}')
        tmp_dict.setdefault("raw",i.ticketStatus) # to see if it is coming from JSM
        ops_list.append(tmp_dict)

    for i in total_set_sys:
        tmp_dict={}
        tmp_dict.setdefault("title",i.title)
        tmp_dict.setdefault("description",i.description)
        try:
            tmp_dict.setdefault("custom_category", ', '.join(json.loads(i.custom_category)))
        except Exception as e:
            tmp_dict.setdefault("custom_category", i.custom_category)
        try:
            tmp_dict.setdefault("custom_bizUnit", ', '.join(json.loads(i.custom_bizUnit)))
        except Exception as e:
            tmp_dict.setdefault("custom_bizUnit",i.custom_bizUnit)
        tmp_dict.setdefault("custom_priority",i.custom_priority)
        tmp_dict.setdefault("createdTime",f'{i.createdTime}')
        tmp_dict.setdefault("mapping",i.mapping)
        tmp_dict.setdefault("sn",i.sn)
        sys_list.append(tmp_dict)

    for i in total_set_net:
        tmp_dict={}
        tmp_dict.setdefault("title",i.title)
        tmp_dict.setdefault("description",i.description)
        tmp_dict.setdefault("custom_category", i.custom_category) #string
        try:
            tmp_dict.setdefault("custom_infra", ', '.join(json.loads(i.custom_infra)))
        except Exception as e:
            tmp_dict.setdefault("custom_infra",i.custom_infra)
        try:
            tmp_dict.setdefault("custom_facilities", ', '.join(json.loads(i.custom_facilities)))
        except Exception as e:
            tmp_dict.setdefault("custom_facilities",i.custom_facilities)
        try:
            tmp_dict.setdefault("custom_vendor", ', '.join(json.loads(i.custom_vendor)))
        except Exception as e:
            tmp_dict.setdefault("custom_vendor",i.custom_vendor)
        tmp_dict.setdefault("createdTime",f'{i.createdTime}')
        tmp_dict.setdefault("mapping",i.mapping)
        tmp_dict.setdefault("sn",i.sn)
        net_list.append(tmp_dict)

    for i in total_set_dba:
        tmp_dict={}
        tmp_dict.setdefault("title",i.title)
        tmp_dict.setdefault("description",i.description)
        try:
            tmp_dict.setdefault("custom_category", ', '.join(json.loads(i.custom_category)))
        except Exception as e:
            tmp_dict.setdefault("custom_category", i.custom_category)
        try:
            tmp_dict.setdefault("custom_bizUnit", ', '.join(json.loads(i.custom_bizUnit)))
        except Exception as e:
            tmp_dict.setdefault("custom_bizUnit",i.custom_bizUnit)
        tmp_dict.setdefault("createdTime",f'{i.createdTime}')
        tmp_dict.setdefault("mapping",i.mapping)
        tmp_dict.setdefault("sn",i.sn)
        dba_list.append(tmp_dict)

    result_dict.setdefault('ops_result', ops_list)
    result_dict.setdefault('sys_result', sys_list)
    result_dict.setdefault('net_result', net_list)
    result_dict.setdefault('dba_result', dba_list)

    return jsonify(result_dict)

@app_mainQuery.route('/checkEmail/<whichTeam>/<target_sn>')
def app_mainQuery_check_email(whichTeam, target_sn):
    if whichTeam == 'OPS':
        try:
            result = get_jsm_ops_prod.query.filter_by(sn=target_sn).first()
            return result.content_html
        except Exception as e:
            print(e)
            return 'get issue on checkEmail', 500
    elif whichTeam == 'SYS':
        try:
            result = get_jsm_sys_prod.query.filter_by(sn=target_sn).first()
            return result.content_html
        except Exception as e:
            print(e)
            return 'get issue on checkEmail', 500
    elif whichTeam == 'NET':
        try:
            result = get_jsm_net_prod.query.filter_by(sn=target_sn).first()
            return result.content_html
        except Exception as e:
            print(e)
            return 'get issue on checkEmail', 500


@app_mainQuery.route('/checkComments/<whichTeam>/<target_sn>')
def app_mainQuery_check_comment(whichTeam, target_sn):
    if whichTeam == 'OPS':
        try:
            result = get_jsm_ops_prod.query.filter_by(sn=target_sn).first()
            returnString = ""
            for i in json.loads(result.comments):
                check_comment_db = get_jsm_ops_comments.query.filter_by(sn=i).first()
                returnString = returnString + f'Update by {check_comment_db.handler} at {check_comment_db.timestamp}, {check_comment_db.content}<br>'
            return returnString
        except Exception as e:
            print(e)
            return 'get issue on checkComments', 500
    elif whichTeam == 'SYS':
        try:
            result = get_jsm_sys_prod.query.filter_by(sn=target_sn).first()
            returnString = ""
            for i in json.loads(result.comments):
                check_comment_db = get_jsm_sys_comments.query.filter_by(sn=i).first()
                returnString = returnString + f'Update by {check_comment_db.handler} at {check_comment_db.timestamp}, {check_comment_db.content}<br>'
            return returnString
        except Exception as e:
            print(whichTeam, target_sn)
            print(e)
            return 'get issue on checkComments', 500
    elif whichTeam == 'NET':
        try:
            result = get_jsm_net_prod.query.filter_by(sn=target_sn).first()
            returnString = ""
            for i in json.loads(result.comments):
                check_comment_db = get_jsm_net_comments.query.filter_by(sn=i).first()
                returnString = returnString + f'Update by {check_comment_db.handler} at {check_comment_db.timestamp}, {check_comment_db.content}<br>'
            return returnString
        except Exception as e:
            print(whichTeam, target_sn)
            print(e)
            return 'get issue on checkComments', 500
    elif whichTeam == 'DBA':
        try:
            result = get_jsm_dba_prod.query.filter_by(sn=target_sn).first()
            returnString = ""
            for i in json.loads(result.comments):
                check_comment_db = get_jsm_dba_comments.query.filter_by(sn=i).first()
                returnString = returnString + f'Update by {check_comment_db.handler} at {check_comment_db.timestamp}, {check_comment_db.content}<br>'
            return returnString
        except Exception as e:
            print(whichTeam, target_sn)
            print(e)
            return 'get issue on checkComments', 500