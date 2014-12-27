# -*- coding: utf-8 -*-

from flask import Flask
from operator import itemgetter
import flask
import shelve
import copy
import datetime

app = Flask(__name__)
tasks = []
statistics = []
db = {}
db['Iggy Pop'] = {'photo': 'IggyPop.jpg', 'albums': ['The Idiot',
					  'Lust for Life',
					  'New Values',
					  'Soldier',
					  'Party',
					  'Zombie Birdhouse',
					  'Blah Blah Blah',
					  'Instinct',
					  'Brick by Brick',
					  'American Caesar',
					  'Naughty Little Doggie',
					  'Avenue B',
					  "Beat ’Em Up",
					  'Skull Ring'
					  'Preliminaires',
					  'Après']}
db['David Bowie'] = {'photo': 'DavidBowie.jpg', 'albums': ['David Bowie',
					 'Space Oddity',
					 'The Man Who Sold the World',
					 'Hunky Dory',
					 'The Rise and Fall of Ziggy Stardust and the Spiders from Mars',
					 'Aladdin Sane',
					 'Pin Ups',
					 'Diamond Dogs',
					 'Young Americans',
					 'Station to Station',
					 'Low',
					 'Heroes',
					 'Lodger',
					 'Scary Monsters (and Super Creeps)',
					 "Let’s Dance",
					 'Tonight',
					 'Never Let Me Down',
					 'Tin Machine',
					 'Tin Machine II',
					 'Black Tie White Noise',
					 '1.Outside',
					 'Earthling',
					 "‘hours…’",
					 'Heathen',
					 'Reality',
					 'The Next Day']}
db['Queen'] = {'photo': 'Queen.jpg', 'albums': ['Queen',
			   'Queen II',
			   'Sheer Heart Attack',
			   'A Night at the Opera',
			   'A Day at the Races',
			   'News of the World',
			   'Jazz',
			   'The Game',
			   'Flash Gordon',
			   'Hot Space',
			   'The Works',
			   'A Kind of Magic',
			   'The Miracle',
			   'Innuendo',
			   'Made in Heaven',
			   'The Cosmos Rocks']}
db['King Crimson'] = {'photo': 'KingCrimson.jpg', 'albums': ['In the Court of the Crimson King',
					  'In the Wake of Poseidon',
					  'Lizard',
					  'Islands',
					  'Larks’ Tongues in Aspic',
					  'Starless and Bible Black',
					  'Red',
					  'Discipline',
					  'Beat',
					  'Three of a Perfect Pair',
					  'VROOOM',
					  'THRAK',
					  'The ConstruKction of Light',
					  'The Power to Believe']}
db['The Velvet Underground'] = {'photo': 'TheVelvetUnderground.jpg', 'albums': ['The Velvet Underground and Nico',
								'White Light/White Heat',
								'The Velvet Underground',
								'Loaded ',
								'Squeeze']}
db['Joy Division'] = {'photo': 'JoyDivision.jpg', 'albums': ['Unknown Pleasures',
					  'Closer']}
db['The Beatles'] = {'photo': 'TheBeatles.jpg', 'albums': ['Please Please Me',
					 'With The Beatles',
					 'A Hard Day’s Night',
					 'Beatles For Sale',
					 'Help!',
					 'Rubber Soul',
					 'Revolver',
					 'Sgt. Pepper’s Lonely Hearts Club Band',
					 'Magical Mystery Tour',
					 'The Beatles',
					 'Yellow Submarine',
					 'Abbey Road',
					 'Let It Be']}

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
		flask.abort(404)
	
@app.route('/rock/task/<int:id>', methods=['GET'])
def task_get(id):
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'GET /rock/task/%s' % id})
	try:
		task = (item for item in tasks if item["id"] == id).next()
		content_type = flask.request.headers.get('Content-Type')
		if not content_type or content_type == 'text/html':
			return flask.render_template('task.html', band_name = task['name'], albums = db[task['name']]['albums'][:task['count']])
		if content_type == 'text/plain':
			return flask.render_template('task.txt', band_name = task['name'], albums = db[task['name']]['albums'][:task['count']])
		if content_type == 'application/json':
			return flask.jsonify({task['name']: {'albums': db[task['name']]['albums'][:task['count']]}})
		if content_type in ['application/xml', 'text/xml']:
			return flask.render_template('task.xml', band_name = task['name'], albums = db[task['name']]['albums'][:task['count']])
	except StopIteration:
		flask.abort(404)

@app.route('/rock/task/<int:id>', methods=['POST'])
def task_modify(id):
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'POST /rock/task/%s' % id})
	try:
		if not flask.request.json or not 'count' in flask.request.json:
			flask.abort(400)
		task = (item for item in tasks if item["id"] == id).next()
		task['count'] = flask.request.json['count']
		return flask.jsonify({'task': task})
	except StopIteration:
		flask.abort(400)

@app.route('/rock/task', methods=['PUT'])
def task_put():
	statistics.append({'date': str(datetime.datetime.now()), 'request': 'PUT /rock/task/%s' % id})
	if not flask.request.json or not 'name' in flask.request.json:
		flask.abort(400)
	if flask.request.json['name'] not in db:
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
	content_type = flask.request.headers.get('Content-Type')
	if not content_type or content_type == 'text/html':
		return flask.render_template('rock.html', bands = db)
	if content_type == 'text/plain':
		return flask.render_template('rock.txt', bands = db)
	if content_type == 'application/json':
		return flask.jsonify(db)
	if content_type in ['application/xml', 'text/xml']:
		return flask.render_template('rock.xml', bands = db)

if __name__ == '__main__':
	app.run(debug = True)