import os
import logging
import openai
import anthropic
from flask import Flask, request
from flask_cors import CORS
from utils import *

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

openai.api_key = os.environ["OPEN_AI_API_KEY"]

client = anthropic.Client(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

mongo_client = get_mongo_client(os.environ["MONGO_URI"])
database = mongo_client["medical_data"]
collection = database["medical_data_collection"]

@app.route("/respond", methods=["GET"])
def respond():
    question = request.args.get("question")
    response, source_information = handle_user_query(question, collection, client)

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7173)