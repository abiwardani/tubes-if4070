from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from uuid import uuid4
import json
import requests
import os

from .. import pipeline

# global variables
MIN_SIM = 0.7
MAX_SIM = 0.97

# env variables
port = os.environ.get("API_PORT")
api_key = os.environ.get("API_KEY")

# configure app
app = Flask(__name__)
app.config['SECRET_KEY'] = '971cf9854ab52d7c643b13c74795f86b5bc09ab6554e42c27155c581bdf937d5'
socket_ = SocketIO(app)

# load QA pairs
# f = open('../../data/qa_data.json', encoding='utf-8')
# qa_data = json.load(f)
# f.close()

f = open('../../data/title_list.json', encoding='utf-8')
topic_list = json.load(f)
f.close()


# serve index page
@app.route('/')
def index():
    print('REFRESHING')
    return render_template('index.html', async_mode=socket_.async_mode)


# on connect, set user token as randomly generated ID
@socket_.on('connect', namespace='/chat')
def connect():
    user_token = uuid4()
    session["user_token"] = user_token
    print(f'[{session["user_token"]}]: connected')


# on start
@socket_.on('start', namespace='/chat')
def chat_start():
    # send welcome message
    emit('bot_response', {
        'data': "Hello, welcome to the chatbot!<br><br>I can answer your questions, what would you like to know about?"})


# on client send message
@socket_.on('send_message', namespace='/chat')
def chat_send_message(message):
    # similarity API URL
    domain = '127.0.0.1'
    encode_api = f'http://{domain}:{port}/encode'
    search_api = f'http://{domain}:{port}/consult'
    sim_api = f'http://{domain}:{port}/similarity'

    # default error message
    default_error_msg = "Sorry, we are not able to answer your question."

    # find answer

    # IMPLEMENT: POS tagging + NER
    
    # TO-DO process query
    query = message['data']
    tokens = pipeline.seqtagging.to_word_tokens(query)

    # TO-DO sequence tagging NER
    named_entities = pipeline.seqtagging.get_entities(tokens)
    print(named_entities)
    # IMPLEMENT: topic recognition

    # TO-DO ...
    
    topics = topic_list["titles"][:2]

    # IMPLEMENT: question matching/answer extraction

    # TO-DO get embedded query
    try:
        # POST request to encoding API
        r = requests.post(
            encode_api, json={'api_key': api_key, 'query': query})
    except Exception:
        # if unable to connect, send suitable error message
        print(Exception)
        emit('bot_response', {
            'data': "Sorry, this service is currently unavailable."})
        return None

    if (r.status_code == 200):
        q_embedding = r.json()['q_embedding']
    else:
        emit('bot_response', {
            'data': "Sorry, this service is currently unavailable."})
        return None
    
    # TO-DO search best match within topic list
    best_sim = MIN_SIM
    best_ans = ""

    for topic in topics:
        try:
            # POST request to search API
            r = requests.post(
                search_api, json={'api_key': api_key, 'q_embedding': q_embedding, 'topic': topic, 'min_sim': MIN_SIM, 'max_sim': MAX_SIM})
        except Exception:
            # if unable to connect, send suitable error message
            print(Exception)
            emit('bot_response', {
                'data': "Sorry, this service is currently unavailable."})
            return None

        if (r.status_code == 200):
            sim = r.json()['sim']
            ans = r.json()['answer']

            if (sim > best_sim):
                best_sim = sim
                best_ans = ans
        else:
            emit('bot_response', {
                'data': "Sorry, this service is currently unavailable."})
            return None
    
    if (best_ans == ""):
        best_sim = 0
        best_ans = default_error_msg

    print(f'[{session["user_token"]}]: {best_ans}, {best_sim}')

    # emit best answer back to client
    emit('bot_response', {'data': best_ans})


# on disconnect request
@socket_.on('disconnect_request', namespace='/chat')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    # emit greeting message with disconnect callback
    emit('bot_response', {
         'data': 'Thank you for using our service!'}, callback=can_disconnect)


if __name__ == '__main__':
    socket_.run(app, debug=True)
