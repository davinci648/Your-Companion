from flask import Flask, render_template, request, jsonify
from twilio.rest import Client as TwilioRestClient
from twilio import twiml
from credentials import settings
import requests
from flaskext.mysql import MySQL
import Algorithmia
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from random import randint
from ourDataset import conversations

# Declares flask app
app = Flask(__name__)

# For Twilio
client = TwilioRestClient(settings['sid'], settings['auth'])
twilio_number = '(253) 343-9145'

# Changes Jinja's expression blocks so angular can work
jinja_options = app.jinja_options.copy()
jinja_options.update(dict(
    block_start_string='<%',
    block_end_string='%>',
    variable_start_string='%%',
    variable_end_string='%%',
    comment_start_string='<#',
    comment_end_string='#>',
))
app.jinja_options = jinja_options

# Algorithmia setup
# apiKey = 'simwZCh9tS6b81wSwLtrdIauZhi1'
apiKey = 'sim1ulkiERNnkZbh+wYGWAQry3M1'
client = Algorithmia.client(apiKey)
algo = client.algo('StanfordNLP/Lemmatizer/0.1.0')
algo2 = client.algo('nlp/SentimentAnalysis/0.1.2')
algo3 = client.algo('nlp/AutoTag/1.0.0')
algo4 = client.algo('nlp/ProfanityDetection/0.1.2')

# ChatBot Stuff
chatbot = ChatBot(
	'yourCompanion',
	trainer='chatterbot.trainers.ChatterBotCorpusTrainer', 
	storage_adapter="chatterbot.storage.JsonFileStorageAdapter", 
	logic_adapters=[
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.TimeLogicAdapter'
    ],
	database="./database.json")
# chatbot.train("chatterbot.corpus.english.conversations")
# chatbot.train("chatterbot.corpus.english.greetings")
chatbot.set_trainer(ListTrainer)

for conversation in conversations:
	chatbot.train(conversation)

# chatterbot.train

# Main front-end endpoint
@app.route('/')
def intro():
	return render_template('intro.html')

@app.route('/login')
def login():
	return render_template('log-in.html')

@app.route('/signup')
def signin():
	return render_template('sign-in.html')

@app.route('/chat')
def chat():
	return render_template('index.html')

@app.route('/settings')
def settings():
	return render_template('settings.html')

# Handle receiving text messages
@app.route('/api/receive', methods=['POST'])
def recieve_sms():
	from_number = requests.values.get('From', None)
	to_number = requests.values.get('To', None)
	text = requests.values.get('Text', None)
	nums[from_number].append(from_msg)
	res = twiml.Response()
	res.message("Got your message!")
	return str(res)

# Handle sending back text messages
@app.route('/api/messages/', methods=['GET', 'POST'])
def show_messages():
	if len(nums) == 0:
		return "No messages. Send one to " + twilio_number + " to start!"
	else:
		return flask.jsonify(nums)

mainTags = {
 	0: 
 		{
 			0: 'panic attack', 
 			1: 'panic'}, 
 	1: 
 		{
 			0: 'suicide', 
 			1: 'kill'}, 
 	2: 
 		{
 			0: 'break'}
} 
# Determines which group the message belongs to
resources = {
 	0: 
 		{
 			0: {'type': 'url', 'data': 'https://www.lifeline.org.au/Get-Help/Facts---Information/Panic-Attacks/Panic-Attacks'}, 
 		 	1: {'type': 'phone-number', 'data': '800-64-PANIC'}}, 
	1: 
 	 	{
 	 		0: {'type': 'url', 'data': 'http://suicidepreventionlifeline.org/#'}, 
 	 		1: {'type': 'phone-number', 'data': '1-800-273-8255'}},
 	 2: 
 	 	{
 	 		0: {'type': 'url', 'data': 'http://www.7cups.com/how-to-get-over-a-breakup/'}, 
 	 		1: {'type': 'phone-number', 'data': '741-741'}},
 }

concerned_option = ["Oh no. Tell me more.", "What's up?", "Is something wrong?", "Talk to me.", "Need to vent?", "Need to talk?", "I'm here for you.", "I'm listening."]



# Handles receiving a web message
@app.route('/api/chat/receive', methods=['GET'])
def process_message():
	text = request.values.get('text')
	response = algo2.pipe(text)
	result = response.result
	if result >= 2: # Good, Okay, or Conversational
		res = chatbot.get_response(text).text
		res_prof = algo4.pipe(res).result
		if len(res_prof) != 0:
			res = "Sorry, I couldn't understand that."
		return jsonify({'text': res})
	else: # Poor to extremely bad
		res = None
		con = algo.pipe(text)
		tags = algo3.pipe(con.result)
		for a in tags.result:
			for x in mainTags:
				for y in mainTags[x]:
					if a == mainTags[x][y]:
						rand = randint(0, 1)
						res = resources[x][rand]['data']
		if res is None:
			res = concerned_option[randint(0, 6)]
		return jsonify({'text': res})


if __name__ == '__main__':
  app.run()
