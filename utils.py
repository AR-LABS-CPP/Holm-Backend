import logging
import openai
import pymongo

embedding_model = "text-embedding-3-small"

def get_mongo_client(mongo_uri):
  try:
    mongoClient = pymongo.MongoClient(mongo_uri)
    
    return mongoClient
  except Exception as e:
    return None

def get_embedding(text):
  if not text or not isinstance(text, str):
    return None

  try:
    embedding = openai.embeddings.create(
        input=text,
        model=embedding_model,
        dimensions=256
    ).data[0].embedding

    return embedding

  except Exception as e:
    print(f"Error occurred in get_embedding {e}")
    return None
  
def vector_search(user_query, collection):
  query_embedding = get_embedding(user_query)

  if query_embedding is None:
    return "Invalid query or embedding generation failed"

  pipeline = [
      {
          "$vectorSearch": {
              "index": "vector_index",
              "queryVector": query_embedding,
              "path": "embedding",
              "numCandidates": 150,
              "limit": 5,
          }
      },
      {
          "$project": {
              "_id": 0,
              "embedding": 0,
              "score": {
                  "$meta": "vectorSearchScore"
              }
          }
      }
  ]

  results = collection.aggregate(pipeline)

  return list(results)

def handle_user_query(query, collection, client):
  get_knowledge = vector_search(query, collection)

  search_result = ""

  for result in get_knowledge:
    logging.debug(result)
    search_result += (
        f"Question: {result.get('question', 'N/A')}, "
        f"Option A: {result.get('opa', 'N/A')}, "
        f"Option B: {result.get('opb', 'N/A')}, "
        f"Option C: {result.get('opc', 'N/A')}, "
        f"Option D: {result.get('opd', 'N/A')}, "
        f"Correct Option: {result.get('cop', 'N/A')}, "
        f"Expert_Answer: {result.get('exp', 'N/A')}, "
        f"Subject_Name: {result.get('subject_name', 'N/A')}, "
        f"Topic Name: {result.get('topic_name', 'N/A')}, \n"
    )

  response = client.messages.create(
      model="claude-3-opus-20240229",
      max_tokens=1024,
      system="You are a medical assistant with access to huge amount of medical data, your job is to provide suggestions or closest symptoms to the condition described by the user.",
      messages=[
        {"role": "user", "content": "Answer this user query: " + query + " with the following context: " + search_result}
      ]
  )

  return (response.content[0].text), search_result