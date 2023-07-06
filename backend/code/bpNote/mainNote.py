from models import db, get_handover_notes, get_handover_notes_attachment
from flask import Blueprint, jsonify, render_template, request, Response, send_from_directory
from shutil import copy
import os
import errno

app_mainNote = Blueprint('app_mainNote', __name__, static_folder='../static')

@app_mainNote.route('/test')
def get_backup_test():
    resultByNoteSn = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.noteSn == 35605).all()
    maxNumber = max([n.fileCounter for n in resultByNoteSn]) + 1
    print(maxNumber)
    return 'test the blueprint'

@app_mainNote.route('/attachment/update', methods=['GET', 'POST'])
def updateNoteAttachment():
    
    targetSn = request.headers.get('noteDbSn')
    updater = request.headers.get('updater')
    
    # use NoteSn to get date and shift
    resultBySn = get_handover_notes.query.filter(get_handover_notes.sn == targetSn).first()
    curNoteSn = resultBySn.sn
    curDate = resultBySn.date
    curShift = resultBySn.shift
    
    # check notes_attachment table on DB
    # # if exist check counter, impact filePath, if not exist, just start at 1 and run by itself
    resultByNoteSn = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.noteSn == curNoteSn).all()
    if resultByNoteSn:
        startNumber = max([n.fileCounter for n in resultByNoteSn]) + 1
    else:
        startNumber = 1
    
    print(f'startNumber = {startNumber}')
    
    for i in request.files:
        fileName = i
        fileType = request.files.get(i).content_type
        
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
            
        dbfilePath = f'notes/{curDate}/{curShift}/{targetSn}/{str(startNumber)}.{_type}'       
        filePath = f'./static/notes/{curDate}/{curShift}/{targetSn}/{str(startNumber)}.{_type}'       
        # store file information to DB
        insertToDB = get_handover_notes_attachment(noteSn=curNoteSn, fileName=fileName, fileType=_type, filePath=dbfilePath, fileCounter=startNumber, updater=updater)
        db.session.add(insertToDB)
        
        # store file to Server folder
        ## create folder if folder is not exist
        if not os.path.exists(os.path.dirname(filePath)):
            try:
                os.makedirs(os.path.dirname(filePath))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        ## save to tmp file
        f = request.files.get(fileName)
        f.save(f'noteAttachmentTemp.{_type}')
        
        ## copy local file to related folder
        copy(f'noteAttachmentTemp.{_type}', filePath)
        
        # update the startNumber
        startNumber = startNumber + 1
        
    db.session.commit()
    db.session.close()
    
    # update note table checkImage column based on current attachment table counter
    resultByNoteSnRenew = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.noteSn == targetSn).all()
    checkImageNumber = len(resultByNoteSnRenew)
    
    # update to Note table
    selectNoteDbBySn = get_handover_notes.query.filter(get_handover_notes.sn == targetSn).first()
    selectNoteDbBySn.check_image = checkImageNumber
    db.session.commit()
    db.session.close()
    
    r = Response(response='file upload success', status=200)
    r.headers['Content-Type'] = 'application/json'
    return r

@app_mainNote.route('/attachment/query/<targetSn>')
def noteAttachmentQuery(targetSn):
    returnList = []
    resultByNoteSn = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.noteSn == targetSn).order_by(get_handover_notes_attachment.fileCounter).all()
    for i in resultByNoteSn:
        returnList.append(i.serialize)
    return jsonify(returnList)
    
@app_mainNote.route('/attachment/review/<attachmentSn>')
def documentReturn(attachmentSn):
    resultBySn = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.sn == attachmentSn).first()   
    if resultBySn.fileType == 'png' or resultBySn.fileType == 'jpg':
        returnObject = resultBySn.filePath
        root_dir = os.path.dirname(os.getcwd())
        return send_from_directory(os.path.join(root_dir, 'code/static/'), returnObject)
    else:
        if resultBySn.fileType == 'pptx':
            returnObject = f'ppt.png'
        elif resultBySn.fileType == 'docx':
            returnObject = f'word.png'
        elif resultBySn.fileType == 'xlsx':
            returnObject = f'excel.png'
        elif resultBySn.fileType == 'txt':
            returnObject = f'txt.png'
        elif resultBySn.fileType == 'pdf':
            returnObject = f'pdf.png'
        else:
            returnObject = f'sample.png'
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'code/static/example'), returnObject)

@app_mainNote.route('/attachment/get/<attachmentSn>')
def noteAttachmentGet(attachmentSn):
    resultBySn = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.sn == attachmentSn).first()
    return app_mainNote.send_static_file(resultBySn.filePath)

@app_mainNote.route('/attachment/delete', methods=['GET', 'POST'])
def noteAttachmentDelete():
    targetAttachmentSn = request.get_json(silent=True)['targetAttachmentSn']
    noteSn = request.get_json(silent=True)['noteSn']
    # del attachment db
    resultBySn = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.sn == targetAttachmentSn).first()
    db.session.delete(resultBySn)
    db.session.commit()
    db.session.close()
    # adjust note db
    resultByNoteSn = get_handover_notes.query.filter(get_handover_notes.sn == noteSn).first()
    if resultByNoteSn.check_image == 1:
        resultByNoteSn.check_image = None
    else:
        resultByNoteSn.check_image = resultByNoteSn.check_image - 1

    db.session.commit()
    db.session.close()
    # return current list let frontend update
    returnList = []
    resultByNoteSn = get_handover_notes_attachment.query.filter(get_handover_notes_attachment.noteSn == noteSn).order_by(get_handover_notes_attachment.fileCounter).all()
    for i in resultByNoteSn:
        returnList.append(i.serialize)
    
    return jsonify(returnList)