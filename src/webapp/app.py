from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from uuid import uuid4
import json
import requests
import os
from time import sleep

from .. import pipeline

# global variables
MIN_SIM = 0.8
MAX_SIM = 0.97
TOPIC_LIMIT = [3, 5, 10, 20]
DEFAULT_ERR_MSG = "Sorry, we are not able to answer your question."

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

f = open('../../data/embedded_titles/title_list.json', encoding='utf-8')
embedded_topic_list = json.load(f)
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
    sim_api = f'http://{domain}:{port}/similarity2'

    # find answer

    # IMPLEMENT: POS tagging + NER
    
    # process query
    query = message['data']
    tokens = pipeline.seqtagging.to_word_tokens(query)

    # sequence tagging NER
    named_entities = pipeline.seqtagging.get_entities(tokens)

    # NER embedding
    if len(named_entities) == 0:
        ner = query
    else:
        ner = " ".join(named_entities)

    try:
        # POST request to encoding API
        r = requests.post(encode_api, json={'api_key': api_key, 'query': ner})
    except Exception:
        # if unable to connect, send suitable error message
        print(Exception)
        emit('bot_response', {
            'data': "Sorry, this service is currently unavailable."})
        return None

    if (r.status_code == 200):
        ner_embedding = r.json()['q_embedding']
    else:
        emit('bot_response', {
            'data': "Sorry, this service is currently unavailable."})
        return None

    # IMPLEMENT: topic recognition

    # TO-DO ...
    
    # if (len(named_entities) == 0):
    #     pipe = None
    #     topics = [pipe.run(query)]
    # else:
    #     for named_entity in named_entities:
    #         topics = [pipe.run(named_entity)]
        
    #     if (len(named_entities) > 1):
    #         topics.append(pipe.run(" ".join(named_entities)))
        
    #     topics.append(pipe.run(query))

    topics = topic_list["titles"]
    topic_sim_list = [0 for _ in topics]
    embedding_list = [topic["embed"] for topic in embedded_topic_list]

    try:
        # POST request to search API
        r = requests.post(
            sim_api, json={'api_key': api_key, 'e1': ner_embedding, 'e_list': embedding_list})
    except Exception:
        # if unable to connect, send suitable error message
        print(Exception)
        emit('bot_response', {
            'data': "Sorry, this service is currently unavailable."})
        return None

    if (r.status_code == 200):
        topic_sim_list = r.json()['sim']

    sorted_topic_list = [x for _, x in sorted(zip(topic_sim_list, topic_list["titles"]), reverse=True)]
    topics = sorted_topic_list

    # IMPLEMENT: question matching/answer extraction

    try:
        # POST request to encoding API
        r = requests.post(encode_api, json={'api_key': api_key, 'query': query})
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
    lim = 0

    while (best_ans == "" and lim < len(TOPIC_LIMIT)):
        if lim == 0:
            search_topics = topics[:TOPIC_LIMIT[lim]]
        else:
            search_topics = topics[TOPIC_LIMIT[lim-1]+1:TOPIC_LIMIT[lim]]
        
        for topic in search_topics:
            print(topic)
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
                
                if (sim > MAX_SIM):
                    break
            else:
                emit('bot_response', {
                    'data': "Sorry, this service is currently unavailable."})
                return None
        
        if (sim > MAX_SIM):
            break
            
        lim += 1
    
    if (best_ans == ""):
        best_sim = 0
        best_ans = DEFAULT_ERR_MSG
    
    best_ans = best_ans[0].upper()+best_ans[1:]

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
