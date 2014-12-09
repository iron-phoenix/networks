from flask import Flask
from operator import itemgetter
import flask
import shelve
import db_init
import copy
import datetime

app = Flask(__name__)
tasks = []
statistics = []

@app.route('/history', methods=['GET'])
def history_get():
	result = ""
	for element in statistics:
		result += "%s : %s<br>" % (element['date'], element['request'])
	return result

@app.route('/rock/task/<int:id>', methods=['DELETE'])
def task_delete(id):
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'DELETE /rock/task/%s' % id})
	try:
		task = (item for item in tasks if item["id"] == id).next()
		tasks.remove(task)
		return flask.Response('DELETED', content_type = 'text/plain', status = 200)
	except StopIteration:
		flask.abort(400)
	
@app.route('/rock/task/<int:id>', methods=['GET'])
def task_get(id):
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'GET /rock/task/%s' % id})
	try:
		task = (item for item in tasks if item["id"] == id).next()
		db = shelve.open("rocks")
		rock_bands = dict(db)
		db.close()
		content_type = flask.request.headers.get('Content-Type')
		if not content_type or content_type == 'text/html':
			return flask.render_template('task.html', band_name = task['name'], albums = rock_bands[task['name']]['albums'][:task['count']])
		if content_type == 'text/plain':
			return flask.render_template('task.txt', band_name = task['name'], albums = rock_bands[task['name']]['albums'][:task['count']])
		if content_type == 'application/json':
			return flask.jsonify({task['name']: {'albums': rock_bands[task['name']]['albums'][:task['count']]}})
		if content_type in ['application/xml', 'text/xml']:
			return flask.render_template('task.xml', band_name = task['name'], albums = rock_bands[task['name']]['albums'][:task['count']])
	except StopIteration:
		flask.abort(400)

@app.route('/rock/task/<int:id>', methods=['POST'])
def task_modify(id):
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'POST /rock/task/%s' % id})
	try:
		if not flask.request.json or not 'count' in flask.request.json:
			flask.abort(400)
		task = (item for item in tasks if item["id"] == id).next()
		db = shelve.open("rocks")
		rock_bands = dict(db)
		db.close()
		task['count'] = flask.request.json['count']
		return flask.jsonify({'task': task})
	except StopIteration:
		flask.abort(400)

@app.route('/rock/task', methods=['PUT'])
def task_put():
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'PUT /rock/task/%s' % id})
	if not flask.request.json or not 'name' in flask.request.json:
		flask.abort(400)
	db = shelve.open("rocks")
	rock_bands = dict(db)
	db.close()
	if flask.request.json['name'] not in rock_bands:
		flask.abort(400)
	task = {
		'id': 0 if not tasks else tasks[-1]['id'] + 1,
		'name': flask.request.json['name'],
		'count': 0 if not 'count' in flask.request.json else flask.request.json['count']
	}
	tasks.append(task)
	return flask.jsonify({'task': task})
	
@app.route('/', methods=['GET'])
def index():
	return flask.render_template('index.html')

@app.route('/rock', methods=['GET'])
def rock():
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'GET /rock'})
	db = shelve.open("rocks")
	rock_bands = dict(db)
	db.close()
	content_type = flask.request.headers.get('Content-Type')
	if not content_type or content_type == 'text/html':
		return flask.render_template('rock.html', bands = rock_bands)
	if content_type == 'text/plain':
		return flask.render_template('rock.txt', bands = rock_bands)
	if content_type == 'application/json':
		return flask.jsonify(rock_bands)
	if content_type in ['application/xml', 'text/xml']:
		return flask.render_template('rock.xml', bands = rock_bands)

if __name__ == '__main__':
	db_init.init()
	app.run(debug = True)