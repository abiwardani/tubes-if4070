from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sentence_transformers import util
import hashlib
import os
import pickle
import json
import numpy as np

from .. import pipeline

# global variables
SALT = b',w\x1dnW\xfdM3T\xe4\x1c\xb3_c(\xeb\xc9\x19\xbat\xe7\x0e\xa3\x19@2u\x0f\x8b;\xe8\xb0'

port = os.environ.get("API_PORT")

app = Flask(__name__)

with open('../pipeline/answerextraction/models/sim-model.pkl', 'rb') as filehandler:
    model = pickle.load(filehandler)

# configure sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keys.sqlite3'
db = SQLAlchemy(app)


# define key model
class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hashed_key = db.Column(db.LargeBinary)

    def __init__(self, api_key, **kwargs):
        super(Key, self).__init__(**kwargs)
        self.hashed_key = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for HMAC
            api_key.encode('utf-8'),  # Convert the password to bytes
            SALT,  # Provide the salt
            100000  # It is recommended to use at least 100,000 iterations of SHA-256
        )

    def __repr__(self):
        return '<Hash %r>' % self.hashed_key


def hash_key(api_key):
    return hashlib.pbkdf2_hmac(
        'sha256',  # The hash digest algorithm for HMAC
        api_key.encode('utf-8'),  # Convert the password to bytes
        SALT,  # Provide the salt
        100000  # It is recommended to use at least 100,000 iterations of SHA-256
    )


# default app route
@app.route('/')
def index():
    return "Hello, World!"

# get sentence embedding
# encode_sentence(query)
@app.route('/encode', methods=['POST'])
def encode_sentence():
    # client validation
    # check if hash of API key exists in database
    api_key = request.json['api_key']
    hashed_key = hash_key(api_key)
    if (Key.query.filter_by(hashed_key=hashed_key) is None):
        abort(401, {"error": "Unauthorized access!"})

    # encoding
    query = request.json['query']
    q_embedding = model.encode(query)

    return jsonify({'q_embedding': q_embedding.tolist()})


# s1 -> q for q in topic, sim?
# find most similar embedded question within topic
# calculate_nearest_sentence(q_embedding, topic)

currentphase = 0 
answerlist = []
simlist = []

@app.route('/consult', methods=['POST'])
def calculate_nearest_sentence(self, threshold, limit):
    # client validation
    # check if hash of API key exists in database
    api_key = request.json['api_key']
    hashed_key = hash_key(api_key)
    if (Key.query.filter_by(hashed_key=hashed_key) is None):
        abort(401, {"error": "Unauthorized access!"})

    # similarity calculation

    q_embedding = np.array(request.json['q_embedding'])
    topic = request.json['topic']
    topic_filename = pipeline.answerextraction.clean_filename(topic)

    if 'min_sim' in request.json:
        MIN_SIM = 0
    else:
        MIN_SIM = request.json['min_sim']
    
    if 'max_sim' in request.json:
        MAX_SIM = 1
    else:
        MAX_SIM = request.json['max_sim']
    
    f = open(f'../../data/embedded_qa/{topic_filename}.json', encoding='utf-8')
    topic_qa_data = json.load(f)
    f.close()

    best_sim = MIN_SIM
    best_ans = ""

    for qa in topic_qa_data["qas"]:
        doc_embedding = np.array(qa["embed"])
        sim = util.cos_sim(q_embedding, doc_embedding)[0][0].item()
        ans = qa["answer"]

        if (sim > threshold):
            if(sim < limit):
                best_sim = sim
                best_ans = ans
                answerlist.append(best_ans)
                simlist.append(best_sim)
        
        if (sim > MAX_SIM):
            break
    
    currentphase += 1

    if currentphase <= 3:
        return jsonify({'sim': simlist, 'answer': answerlist})

    else :
        calculate_nearest_sentence(threshold, limit)


# compare similarity of two sentences
# calculate_sentence_similarity(s1, s2)
@app.route('/similarity', methods=['POST'])
def calculate_sentence_similarity():
    # check if hash of API key exists in database
    api_key = request.json['api_key']
    hashed_key = hash_key(api_key)
    if (Key.query.filter_by(hashed_key=hashed_key) is None):
        abort(401, {"error": "Unauthorized access!"})

    s1 = request.json['s1']
    s2 = request.json['s2']
    s1_embedding = model.encode(s1)
    s2_embedding = model.encode(s2)

    sim = util.cos_sim(s1_embedding, s2_embedding)

    return jsonify({'sim': sim[0][0].item()})

# flask run --port 6970

if __name__ == '__main__':
    app.run(debug=True, port=6970)
