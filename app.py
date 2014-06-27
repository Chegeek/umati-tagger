# -*- coding: utf-8 -*- 

# import os, glob, re, json
# import pandas as pd
import postgresops
import json
import csv

from flask import Flask, request, session, g, redirect, url_for, \
      abort, render_template, flash, jsonify

from time import strftime

''' ------------------------------- setup and initialize app ------------------------------- '''

app = Flask(__name__)
#app.run(debug=True)

''' ---------------------------------------- Routes ---------------------------------------- '''
@app.route('/')
def index():
    # load_data()
    return render_template('index.html')

@app.route('/sessions/<tag_sessionid>')
def session_code(tag_sessionid):
    return render_template('tagSession.html', session_id = tag_sessionid)

@app.route('/view/<tag_sessionid>', methods=['GET'])
def load_data(tag_sessionid):
    '''' Code to read data from the database '''
    try:
        filePath = 'static/_data/sessions/' + tag_sessionid + '.json'
        with open(filePath, "r") as session_file:
            session_info = json.load(session_file)

        comments_list = session_info['comments_to_tag']
        
        #Comment ID formatting to remove unicode character
        comments_list = [s.encode('utf-8') for s in comments_list]
        comments_list = str(comments_list).strip('[]')

        dbase = postgresops.PostGresDBase()
        comments_data = dbase.getComments(comments_list)
        
        session_info['comments_to_tag'] = comments_data
        
        return jsonify(session_info)            

    except IOError as e:
        return 'Session ({0}) has not been found'.format(tag_sessionid)

@app.route('/sessions/add', methods=['POST'])
def saveLabels():
    tagdataString = request.form['toSave']
    tagdata = json.loads(tagdataString)

    tag_time = strftime("%Y-%m-%d %H:%M:%S")

    # TEMP JSON write 
    # Jun25.14 --> Need to figure how to add the tags to the jsonfile or whatever and trim file

    try:
        filePath = 'static/_data/sessions/' + tagdata['session_id'] + '.json'
        with open(filePath, "r") as session_file:
            session_info = json.load(session_file)        

        filePath = 'static/_data/tagged_data/' + tagdata['session_qst'] + '.csv'
        with open(filePath, "a+") as csvreader:
            qst_file = csv.writer(csvreader, delimiter=',')
            tag_lines=[]
            for tag_item in tagdata['tags']:
                line =[]
                line.append(tagdata['session_id'])
                line.append(tagdata['session_desc'])
                line.append(tagdata['tagged_by'])
                line.append(tag_time)
                line.append(tag_item)
                line.append(tagdata['tags'][tag_item])
                tag_lines.append(line)

                session_info['comments_to_tag'].remove(tag_item)
                # = session_info['comments_to_tag'][tagdata['tag_pos']:]

            qst_file.writerows(tag_lines)
            # session_info = json.load(qst_file)
    # ''' Code to post tags to RedisDBase or wherever '''
    # # dbase = postgresops.PostGresDBase()
    # # dbase.postTags(tagdata)    

        filePath = 'static/_data/sessions/' + tagdata['session_id'] + '.json'
        with open(filePath, "w") as session_file:
            json.dump(session_info, session_file, indent=4)
        
        return jsonify(session_info)            

    except IOError as e:
        return 'Session ({0}) has not been found'.format(tagdata['session_id'])    

    # result = {'comments': tag_lines}
    # return jsonify(**result)    
    # return jsonify(tagdata)    

@app.route('/create', methods=['GET', 'POST'])
def create_sessions():
    '''' Code to create sessions '''
    sessions_to_create = []
    start_position = 0
    details_string = request.form['sessionsObject']
    sessions_details = (json.loads(details_string))['taggers_info']

    total_tags = sum(item['comments_to_tag'] for item in sessions_details)
    dbase = postgresops.PostGresDBase()
    comments_to_tag = dbase.getToTag(total_tags)
    
    for user_session in sessions_details:
        end_position =  start_position + user_session['comments_to_tag']
        user_session['comments_to_tag'] = comments_to_tag[start_position:end_position]
        # sessions_to_create.append({'tag_qid': user_session['tag_qid'], 'user_to_tag': user_session['user_to_tag'], 'user_email': user_session['user_email'], \
        #     'comments_to_tag': comments_to_tag[start_position:end_position]})
        

    #     #Create the dynamic path for the tagging session
    #     tag_session_url = url_for('session_code', tag_sessionid=str(user_session['tag_qid'] + '_'+ user_session['user_to_tag']))

    #     #Temp Writing  TO JSON
    #     filePath = 'static/_data/' + tag_session_url + '.json'
    #     with open(filePath, "w") as outfile:
    #         json.dump({'tag_qid': user_session['tag_qid'], 'user_to_tag': user_session['user_to_tag'], 'user_email': user_session['user_email'], \
    #         'comments_to_tag': comments_to_tag[start_position:end_position]}, outfile, indent=4)

    #     start_position+=user_session['comments_to_tag']
    # # # dbase = postgresops.RedisDBase()
    # # # dbase.createSessions(sessions_to_create)
    # # tag_session_url = url_for('session_code', tag_sessionid='q1_chalengezw@gmail.com')

    # result = {'comments': tag_session_url}
    result = {'comments': sessions_details}
    return jsonify(**result)    

''' --------------------------------- Main Function -------------------------------------- '''                  
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',
         port=int('80'))
    # load_data()