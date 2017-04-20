from flask import Flask, render_template, request, jsonify
from credentials import settings
from flaskext.mysql import MySQL
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from random import randint
from ourDataset import conversations
import requests,Algorithmia, random, json, requests

# Declares flask app
yourCompanion = Flask(__name__)

proxies = {'http':'http://202.141.80.24:3128', 'https':'https://202.141.80.24:3128'}
auth = requests.auth.HTTPProxyAuth('username', 'passwd')

# Changes Jinja's expression blocks so angular can work
jinja_options = yourCompanion.jinja_options.copy()
jinja_options.update(dict(
    block_start_string='<%',
    block_end_string='%>',
    variable_start_string='%%',
    variable_end_string='%%',
    comment_start_string='<#',
    comment_end_string='#>',
))
yourCompanion.jinja_options = jinja_options

# Setup Algorithmia
apiKey = 'sim1ulkiERNnkZbh+wYGWAQry3M1'
client = Algorithmia.client(apiKey)
lemmatizerAlgo= client.algo('StanfordNLP/Lemmatizer/0.1.0')
sentimentDetector = client.algo('nlp/SentimentAnalysis/0.1.2')
tagger = client.algo('nlp/AutoTag/1.0.0')
profanityDetector = client.algo('nlp/ProfanityDetection/0.1.2')

# ChatBot Stuff
chatbot=ChatBot('yourCompanion',trainer='chatterbot.trainers.ChatterBotCorpusTrainer',storage_adapter="chatterbot.storage.JsonFileStorageAdapter",database="./database.json")
chatbot.set_trainer(ListTrainer)

for conversation in conversations:
	chatbot.train(conversation)


# Main front-end endpoint
@yourCompanion.route('/')
def intro():
	return render_template('chat.html')


@yourCompanion.route('/com_mov', methods=['POST','GET'])
def recommend_comedy_mov():
	file = open("comedy_movies.txt",'r')
	com_mov_list = []
	for line in file.readlines():
		com_mov_list.append(line)
	print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	#return random.choice(com_mov_list)
	#with requests_cache.enabled('movie_cache', backend='sqlite', expire_after=86400):

	temp = 'http://www.omdbapi.com/?t=' + str(random.choice(com_mov_list)) + '&plot=full&r=json'
	print temp
	#r = requests.get(temp)

	r = requests.get(temp, proxies = proxies, auth = auth)

	data = r.json()
	print data
	print "==========================================================="
	return str('<img src=\'') + str(data['Poster']) + str('\'/> <p>') + str(data['Title']) + str('</p>')

@yourCompanion.route('/mot_mov', methods=['POST','GET'])
def recommend_motivational_mov():
	file = open("motivational_movies.txt",'r')
	mot_mov_list = []
	for line in file.readlines():
		mot_mov_list.append(line)
	print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	#return random.choice(mot_mov_list)
	#with requests_cache.enabled('movie_cache', backend='sqlite', expire_after=86400):

	temp = 'http://www.omdbapi.com/?t=' + str(random.choice(mot_mov_list)) + '&plot=full&r=json'
	print temp
	#r = requests.get(temp)

	r = requests.get(temp, proxies = proxies, auth = auth)

	data = r.json()
	print data
	print "==========================================================="
	return str('<img src=\'') + str(data['Poster']) + str('\'/> <p>') + str(data['Title']) + str('</p>')

@yourCompanion.route('/feel_good_mov', methods=['POST','GET'])
def recommend_feel_good_mov():
	file = open("feel_good_movies.txt",'r')
	feel_good_mov_list = []
	for line in file.readlines():
		feel_good_mov_list.append(line)
	print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	#return random.choice(feel_good_mov_list)
	#with requests_cache.enabled('movie_cache', backend='sqlite', expire_after=86400):

	temp = 'http://www.omdbapi.com/?t=' + str(random.choice(feel_good_mov_list)) + '&plot=full&r=json'
	print temp
	#r = requests.get(temp)

	r = requests.get(temp, proxies = proxies, auth = auth)

	data = r.json()
	print data
	print "==========================================================="
	return str('<img src=\'') + str(data['Poster']) + str('\'/> <p>') + str(data['Title']) + str('</p>')


mainTags = {0: {0:'panic attack',1:'panic'},1:{0:'suicide',1: 'kill'},2:{0:'break'}} 
# Determines which group the message belongs to
resources = {
 	0: 
 		{
 			0:{'type':'url','data':'www.welcomecure.com'}, 
 		 	1:{'type':'phone-number','data': '9833598553'}}, 
	1: 
 	 	{
 	 		0:{'type':'url','data':'www.vandrevalafoundation.com'}, 
 	 		1:{'type':'phone-number','data':'18602662345'}},
 	 2: 
 	 	{
 	 		0:{'type':'url','data':'www.therulesrevisited.com'}, 
 	 		1:{'type':'phone-number','data':'18602662345'}},
 }

concerned_options = ["I am so sorry to hear that. Please tell me more.", "do you feel something has gone wrong ?", "You can talk with me.", "do you need to vent?", "do you want to talk?", "I'm here for you."]


# Handles receiving a web message
@yourCompanion.route('/api/chat/receive', methods=['GET'])
def process_message():
	inputUser = request.values.get('text')
	#First check the sentiment
	result = sentimentDetector.pipe(inputUser).result

	#Check if sentiment is very negative
	if result >= 2: 
		outputUser = chatbot.get_response(inputUser).text
		res_prof = profanityDetector.pipe(outputUser).result
		if len(res_prof) != 0:
			outputUser = "Sorry, Please try something else."
		return jsonify({'text': outputUser})

	else: #Very critical
		outputUser = None
		tags = tagger.pipe(lemmatizerAlgo.pipe(inputUser).result)
		for a in tags.result:
			for x in mainTags:
				for y in mainTags[x]:
					if a == mainTags[x][y]:
						rand = randint(0, 1)
						outputUser = resources[x][rand]['data']
		if outputUser is None:
			outputUser = concerned_options[randint(0, 6)]
		return jsonify({'text': outputUser})


if __name__ == '__main__':
  yourCompanion.run(debug = True)
