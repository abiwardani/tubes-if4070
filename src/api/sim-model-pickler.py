from sentence_transformers import SentenceTransformer
import pickle

model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')

with open("models/sim-model.pkl", "wb") as outfile:
    pickle.dump(model, outfile)