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

openai.api_key = "OPEN_AI_API_KEY"

client = anthropic.Client(
    api_key="ANTHROPIC_API_KEY"
)

mongo_client = get_mongo_client("MONGO_URI")
database = mongo_client["medical_data"]
collection = database["medical_data_collection"]

@app.route("/respond", methods=["GET"])
def respond():
    question = request.args.get("question")
    response, source_information = handle_user_query(question, collection, client)

    return response