from flask import Flask, jsonify, send_from_directory, request
from flask import redirect, url_for, render_template
from flask_socketio import SocketIO, emit, send
import os
import json
import sqlite3
import pandas

app = Flask(__name__)#, static_url_path = '')
app.config['SECRET_KEY'] = "Your_secret_string!@"
port = int(os.getenv("PORT", 5000))
socketio = SocketIO(app)
number = 1

@app.route('/')
def root():
	args = request.args.get('display')
	return render_template('changeName.html', display = args)

@app.route('/goHome', methods = ['POST', 'GET'])
def goHome():
	args = request.args.get('comment')
	return redirect(url_for('root', display = args))

@socketio.on('change_event')
def test_change():

	global number
	#print("hererre")
	#print(number)
	if number == 5:
		emit('response', 'Change')
	else:
		emit('response', 'nothong')

@app.route('/displayNumber')
def displayNumber():
	global number
	number += 1
	conn = sqlite3.connect('quake')
	cur = conn.cursor()
	search = "select count(*) from test"
	cur.execute(search)
	rows = cur.fetchall()
	return jsonify(count = rows[0][0])

@app.route('/displayFewRecords', methods = ['POST'])
def displayFewRecords():
	num = int(request.json['num'])
	conn = sqlite3.connect('quake')
	cur = conn.cursor()
	search = "select time, latitude, longitude, mag, place from test"
	cur.execute(search)
	rows = cur.fetchall()
	send = []
	counter = 0
	for row in rows:
		counter += 1
		temp = []
		for x in row:
			if x == None:
				temp.append("NoData")
			else:
				temp.append(x)
		send.append(temp)
		if counter == num:
			break
	return jsonify(result = send)


@app.route('/displayPie')
def displayPie():
	conn = sqlite3.connect('quake')
	cur = conn.cursor()
	search = "select mag from test"
	cur.execute(search)
	rows = cur.fetchall()
	negMag, mag3, mag5, mag7, mag10 = 0, 0, 0, 0, 0
	for row in rows:
		if row[0] == None:
			continue
		if float(row[0]) < 0:
			negMag += 1
		elif float(row[0]) < 3:
			mag3 += 1
		elif float(row[0]) < 5:
			mag5 += 1
		elif float(row[0]) < 7:
			mag7 += 1
		else:
			mag10 +=1
	return jsonify(result = [negMag, mag3, mag5, mag7, mag10])


@app.route("/storeImage", methods = ['POST'])
def storeImage():
	image = request.files['image']
	code = 0
	try:
		image.save(os.path.join('/home/mahin/uni/adb/', image.filename))
	except:
		code = 1
		comment = "Failed."
	if not code:
		comment = "Successfully uploaded"
	#print(comment)
	return redirect(url_for('goHome', comment = comment))

@app.route("/createTable", methods = ['POST'])
def createTable():
	fileData = request.files['csv']
	userFileName = request.form['tableName']
	if userFileName:
		pass
	else:
		userFileName = fileData.filename.split('.')[0]
	conn = sqlite3.connect('quake')
	df = pandas.read_csv(fileData)
	df.to_sql(userFileName, conn, index = True)
	comment = "Successfully uploaded"
	return redirect(url_for('goHome', comment = comment))

@app.route("/getCSVdetails", methods = ['POST'])
def getCSVdetails():
	fileData = request.files['forpandas']
	attrList = request.form['fields']
	if request.form['numRec']:
		numRec = int(request.form['numRec'])
	else:
		numRec = 10
	df = pandas.read_csv(fileData)
	if attrList:
		attrList = attrList.split(',').strip()
	else:
		attrList = list(df.columns)
	#print(df.loc[:3,'LastName'])
	send = []
	for i in range(numRec):
		send.append(list(df.loc[i, attrList]))
	#print(send[0])
	return render_template('pandasCSVdisplay.html', result = send, attrListLen = len(attrList))


if __name__ == '__main__':
	socketio.run(app, host = '0.0.0.0', port = port, debug = True)
