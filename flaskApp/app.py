import requests
import json
from flask import Flask, render_template, session, request, redirect, url_for,jsonify
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
import urllib
from dateutil.parser import parse
from tokenFetcher import getToken

app = Flask(__name__)
CORS(app, support_credentials=True)

app.config['MONGO_DBNAME'] = 'test'
app.config['MONGO_URI'] = 'mongodb+srv://<USER_NAME>:<PASSWORD>@innov-shellkore-wdunp.mongodb.net/test?retryWrites=true&w=majority'

mongo = PyMongo(app)

def getQuiz():
	quiz = mongo.db.quiz
	output = []
	for m in quiz.find({}, {'_id': False}):
		print(m)
		ques = m["question"]
		opt = m["options"]
		print(type(ques))
		print(type(opt))
		formattedData = {ques:opt}
		print(type(formattedData))
		output.append(formattedData)
	# print(output)
	return output

def isodateformat(dateString):
	tzinfos ={
    "EST":"UTC-5",
    "EDT":"UTC-5",
    "CDT":"UTC-6"
	}
	dt = parse(dateString,tzinfos=tzinfos)
	return (dt.isoformat())

@app.route('/')
def home():
	return "working!!!"

@app.route('/getquiz')
def getquiz():
	data = getQuiz()
	return jsonify(data)

@app.route("/externalCall")
def externalCall():
	meetingDetails = createMeeting()

	try:
		joinUrl =meetingDetails['joinUrl']
	except:
		getToken()
		meetingDetails = createMeeting()
		joinUrl = meetingDetails['joinUrl']

	result = {'url':joinUrl}
	return jsonify(result)

@app.route("/schedule", methods=['POST'])
def schedule():
	recieved = request.data.decode('UTF-8')
	info = json.loads(recieved)
	# print(info['dateString'])
	meetingDateTime = isodateformat(info['dateString'])

	meetingDetails = createMeeting(startDateTime=meetingDateTime)
	try:
		joinUrl =meetingDetails['joinUrl']
	except:
		getToken()
		meetingDetails = createMeeting(startDateTime=meetingDateTime)
		joinUrl = meetingDetails['joinUrl']

	entryId = updateSchedule(info,joinUrl)
	print(f"database updated with entryId as {entryId}")
	return "recieved"

@app.route('/scheduled', methods=['GET'])
@cross_origin(supports_credentials=True)
def scheduled():
	result = getAllSchedules()
	# print(result)
	return jsonify(schedule=result)

if __name__ == '__main__':
	app.run(debug=True,port=5000)
