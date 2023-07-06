import sys
print(sys.path)
import models


customFieldslist = []
customFieldslist.append(dict(customFieldName='Infra', customFieldId='customfield_10264', optionType='multiple'))
customFieldslist.append(dict(customFieldName='Category NET', customFieldId='customfield_10286', optionType='single'))
customFieldslist.append(dict(customFieldName='Facilities', customFieldId='customfield_10287', optionType='multiple'))
customFieldslist.append(dict(customFieldName='Vendor Support', customFieldId='customfield_10288', optionType='multiple'))
customFieldslist.append(dict(customFieldName='Request Handler', customFieldId='customfield_10274', optionType='multiple'))
customFieldslist.append(dict(customFieldName='Participants', customFieldId='customfield_10206', optionType='multiple'))
customFieldslist.append(dict(customFieldName='Start Date Time', customFieldId='customfield_10282', optionType='timeString'))
customFieldslist.append(dict(customFieldName='End Date Time', customFieldId='customfield_10283', optionType='timeString'))


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
tmp_list3.append(('10971', 'Certificate'))
customFieldslist[2]['values'] = tmp_list3

tmp_list4 = []
tmp_list4.append(('10972','Sanfran'))
tmp_list4.append(('10973','Lantro'))
tmp_list4.append(('10974','eASPNet'))
customFieldslist[3]['values'] = tmp_list4

tmp_list5 = []
tmp_list5.append(('70121:565832f6-008f-473c-b45f-ebdd52eb1ab7', 'Major Chang'))
tmp_list5.append(('61237809fc55090071e40617','Justin Yeh'))
tmp_list5.append(('6123807fec0a83006a1e72ce','Josh Liu'))
tmp_list5.append(('612380814f29230069223aae','Ryo Bing'))
tmp_list5.append(('612380810511d6006a0e12eb','Ray Hong'))
tmp_list5.append(('612389351827d100682d0079','Chris Yen'))
tmp_list5.append(('612389380511d6006a0e7db7','Shane Tzou'))
customFieldslist[4]['values'] = tmp_list5
customFieldslist[5]['values'] = tmp_list5

url = 'ict888.atlassian.net'

print('start net loop')

# for i in customFieldslist:
#     print(i['customFieldName'], i['customFieldId'])
#     tmp_values_list = []
#     if 'values' in i.keys():
#         for ii in i['values']:
#             tmp_values_list.append(dict(id=ii[0], value=ii[1], disabled=False))
#     insertDb = get_jsm_field_sets(env=url, optionName=i['customFieldName'], fieldId=i['customFieldId'], contextId=1, value=json.dumps(tmp_values_list))
#     db.session.add(insertDb)
# db.session.commit()
# db.session.close()
# db.session.remove()
print('end net loop')