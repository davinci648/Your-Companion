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
apiKey = 'simwZCh9tS6b81wSwLtrdIauZhi1'
client = Algorithmia.client(apiKey)
algo = client.algo('StanfordNLP/Lemmatizer/0.1.0')
algo2 = client.algo('nlp/SentimentAnalysis/0.1.2')
algo3 = client.algo('nlp/AutoTag/1.0.0')
algo4 = client.algo('nlp/ProfanityDetection/0.1.2')

# ChatBot Stuff
chatbot = ChatBot('Ahuna',trainer='chatterbot.trainers.ChatterBotCorpusTrainer', storage_adapter="chatterbot.storage.JsonFileStorageAdapter", database="./database.json")
# chatbot.train("chatterbot.corpus.english.conversations")
chatbot.set_trainer(ListTrainer)
chatbot.train([
	"Hmm",
	"So what are you feeling",
    "How are you?",
    "I am good.",
    "That is good to hear.",
    "Thank you",
    "You are welcome.",
    "I am feeling sad",
    "Awww, What happened that made you feel low ?",

])

chatbot.train(["I want to die.",
					"Mohit, it sounds like you are thinking of doing something drastic.",
					"Are you feeling you can't cope up anymore",
					"Yes I can't cope anymore",
					"Mohit, I am a bot, and not able to deal with life-threatening situations. \
					Please call one of these helplines or pick one from a comprehensive list of helplines here:109",
					])
chatbot.train([
	"I have lost all my money.",
	"Okay. But before we dig in deeper, let's begin by relaxing our neck and\
	 shoulder muscles as even the mildest level of stress has its physical impact.\
	 Take a deep breath and relax the neck. ",])

chatbot.train(["I am stressed.","Ok... Let's start. You may have felt stressed before.\
 Feelings that felt overwhelming at the time, turned out to be temporary.",])

chatbot.train(["I want to improve my life.","For me meditation and breathing helps\
 .. but real change comes by changing our thoughts...",
 "what is the true meaning of life?",
 "don't overthink...no one can actually know this..enjoy the time you have and make the people in your life happy!",
 "i dont want to live any more",
 "failures are the stepping stones of success dont get disheartened",
 "Why are people so selfish?",
 "Nobody is selfless in the world.\
  Being selfless means doing good to others which makes 'you' feel good, and hence a selfish deed.\
   It's just that reasons of being satisfied are different for different people.",
   "How are you so happy all the time?",
   "I look at the positive side of life.",
   "Why doesn't anyone like me?",
   "You haven't met everyone.",
   "Will I die alone? ",
   "It might not seem to be quite apparent now, but you always have people who love and care for you.\
    Other than your family, there are most definitely at least a handful of friends who really cherish you.\
     Yo just thought of a couple of names didn't you? Call them up and just talk like how you normally would.\
      If you couldn't come up with the names for some reason, call your mother; and tell her you love her.\
       Now even if that is not the best solution, promise to yourself that even if there is no one else in this\
        world for you, you yourself will ALWAYS be there for you.. and if you could make it this far without anyone,\
         you sure can make it a lot further. Lots of love. :)",
         "I am feeling tired. What should I eat?",
         "How about something sugary like juice or lassi?",
         "Why should I be happy?",
         "Happy people are more productive.",
         "Why Should I be happy?",
         " Happy people have better relationships.",
         "Why Should I be happy?",
         "Seeing you Happy makes me happy.",


 ])

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


# apiKey = 'simwZCh9tS6b81wSwLtrdIauZhi1'
# client = Algorithmia.client(apiKey)
# algo = client.algo('StanfordNLP/Lemmatizer/0.1.0')
# algo2 = client.algo('nlp/SentimentAnalysis/0.1.2')
# algo3 = client.algo('nlp/AutoTag/1.0.0')
# algo4 = client.algo('nlp/ProfanityDetection/0.1.2')

# # ChatBot Stuff
# chatbot = ChatBot('Ahuna',trainer='chatterbot.trainers.ChatterBotCorpusTrainer', storage_adapter="chatterbot.storage.JsonFileStorageAdapter", database="./database.json")
# chatbot.train("chatterbot.corpus.english.conversations")




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
