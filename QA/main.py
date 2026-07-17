# from fastapi import FastAPI, UploadFile, File
# from pydantic import BaseModel
# import pickle
# import os
# import numpy as np

# from langchain_community.document_loaders import PyPDFLoader
# from Text_Splitter import text_split
# from Embedding import sentence_transform
# from Similarity import similarity_check
# from llm_call import LLMManager

# app = FastAPI()

# PKL_PATH = "embeddings_store.pkl"
# chat_history = []

# llm = LLMManager(api_key="YOUR_GEMINI_KEY")


# # -------- Request Models --------
# class ChatRequest(BaseModel):
#     question: str


# # -------- Upload & Process Once --------
# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     if os.path.exists(PKL_PATH):
#         return {"message": "Embeddings already exist. Skipping processing."}

#     # Save file
#     with open(file.filename, "wb") as f:
#         f.write(await file.read())

#     # Load PDF
#     loader = PyPDFLoader(file.filename)
#     docs = loader.load()
#     full_text = " ".join([doc.page_content for doc in docs])

#     # Split
#     texts = text_split(full_text)

#     # Embeddings
#     embeddings, model = sentence_transform(texts)

#     # Save everything
#     with open(PKL_PATH, "wb") as f:
#         pickle.dump({
#             "texts": texts,
#             "embeddings": embeddings,
#             "model_name": "sentence-transformers"
#         }, f)

#     return {"message": "File processed and embeddings saved."}


# # -------- Chat Endpoint --------
# # @app.post("/chat")
# # def chat(req: ChatRequest):
# #     question = req.question.lower()

# #     # Greeting / small talk detection
# #     greetings = ["hi", "hello", "hey", "how are you"]
# #     if any(g in question for g in greetings):
# #         answer = llm.generate_answer(question, [])
# #         chat_history.append(("user", question))
# #         chat_history.append(("assistant", answer))
# #         return {"answer": answer, "source": "general"}

# #     # Load embeddings
# #     if not os.path.exists(PKL_PATH):
# #         return {"answer": "Please upload a document first."}

# #     with open(PKL_PATH, "rb") as f:
# #         data = pickle.load(f)

# #     texts = data["texts"]
# #     embeddings = data["embeddings"]

# #     # Encode user query
# #     user_vec = embeddings[0] * 0  # dummy shape
# #     from sentence_transformers import SentenceTransformer
# #     model = SentenceTransformer("all-MiniLM-L6-v2")
# #     user_vec = model.encode(question)

# #     # Similarity
# #     similarities, stored_data = similarity_check(user_vec)

# #     k = 4
# #     top_indices = np.argsort(similarities)[-k:][::-1]
# #     retrieved_texts = [
# #         stored_data[idx]["text"]
# #         for idx in top_indices
# #         if similarities[idx] > 0.5
# #     ]

# #     # LLM
# #     answer = llm.generate_answer(question, retrieved_texts)

# #     chat_history.append(("user", question))
# #     chat_history.append(("assistant", answer))

# #     return {
# #         "answer": answer,
# #         "source": "document",
# #         "history": chat_history
# #     }


# @app.post("/chat")
# def chat(req: ChatRequest):
#     question = req.question.lower()

#     greetings = ["hi", "hello", "hey", "how are you"]
#     if any(g in question for g in greetings):
#         answer = llm.generate_answer(question, [])
#         chat_history.append(("user", question))
#         chat_history.append(("assistant", answer))
#         return {"answer": answer, "source": "general"}

#     if not os.path.exists(PKL_PATH):
#         return {"answer": "Please upload a document first."}

#     # Load embeddings
#     with open(PKL_PATH, "rb") as f:
#         data = pickle.load(f)

#     texts = data["texts"]
#     stored_embeddings = data["embeddings"]

#     # Load model again
#     from sentence_transformers import SentenceTransformer
#     model = SentenceTransformer("all-MiniLM-L6-v2")

#     # Encode user
#     user_vec = model.encode(question)

#     # Similarity
#     similarities = np.dot(stored_embeddings, user_vec) / (
#         np.linalg.norm(stored_embeddings, axis=1) * np.linalg.norm(user_vec)
#     )

#     k = 4
#     top_indices = np.argsort(similarities)[-k:][::-1]
#     retrieved_texts = [
#         texts[idx] for idx in top_indices if similarities[idx] > 0.5
#     ]

#     answer = llm.generate_answer(question, retrieved_texts)

#     chat_history.append(("user", question))
#     chat_history.append(("assistant", answer))

#     return {
#         "answer": answer,
#         "source": "document"
#     }


# # -------- History Endpoint --------
# @app.get("/history")
# def get_history():
#     return {"history": chat_history}




from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import pickle
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Custom imports - ensure these files exist in your folder!
from langchain_community.document_loaders import PyPDFLoader
from Text_Splitter import text_split
from Embedding import sentence_transform
from Similarity import similarity_check
from llm_call import LLMManager

from datetime import datetime

app = FastAPI()
PKL_PATH = "embeddings_store.pkl"
chat_history = []

# Initialize models ONCE at startup
llm = LLMManager(api_key="AIzaSyACum1gsl2y5Bs4fXgcOn_BixlAj9QMoSk")
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

class ChatRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save temporary file to process
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        loader = PyPDFLoader(file_location)
        docs = loader.load()
        full_text = " ".join([doc.page_content for doc in docs])
        
        texts = text_split(full_text)
        # Use your custom embedding logic
        embeddings, _ = sentence_transform(texts)

        with open(PKL_PATH, "wb") as f:
            pickle.dump({
                "texts": texts,
                "embeddings": embeddings
            }, f)
        
        return {"message": "File processed successfully!"}
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)

@app.post("/chat")
def chat(req: ChatRequest):

    question = req.question.lower().strip()

    if question == "history":
        # Filter: Keep only the text where the role was "user"
        user_questions = [entry[1] for entry in chat_history if entry[0] == "user"]
        
        if not user_questions:
            return {"answer": "You haven't asked any questions yet!", "source": "system"}
        
        # Format as a clean numbered list
        history_text = "Here are the questions you've asked so far:\n"
        for i, q in enumerate(user_questions, 1):
            history_text += f"{i}. {q}\n"
            
        return {"answer": history_text, "source": "system"}

    # if question == "chat history":
    #     if not chat_history:
    #         return {"answer": "Our chat history is currently empty.", "source": "system"}
        
    #     # Format the history into a readable string
    #     history_text = "Here is our conversation so far:\n"
    #     for i, entry in enumerate(chat_history, 1):
    #         # entry[0] is 'user', entry[1] is 'assistant'
    #         history_text += f"{i}. You: {entry[0]} | AI: {entry[1]}\n"
            
    #     return {"answer": history_text, "source": "system"}
    # question = req.question.lower()


    if question == "chat history":
        if not chat_history:
            return {"answer": "No history available yet.", "source": "system"}
        
        history_text = "Here is your chat history:\n\n"
        
        # We step by 2 because history is: [User_Q1, AI_A1, User_Q2, AI_A2...]
        # range(0, len, 2) lets us grab the pairs together
        counter = 1
        for i in range(0, len(chat_history), 2):
            try:
                user_part = chat_history[i][1]      # The question text
                assistant_part = chat_history[i+1][1] # The answer text
                
                history_text += f"{counter}) user: {user_part}\n"
                history_text += "\n"
                history_text += f"   assistant: {assistant_part}\n\n"
                counter += 1
            except IndexError:
                # In case there is a trailing user question with no answer yet
                user_part = chat_history[i][1]
                history_text += f"{counter}) user: {user_part}\n   assistant: [No response yet]\n"

        return {"answer": history_text.strip(), "source": "system"}
    
    # 1. Simple Greeting Logic
    greetings = ["hi", "hello", "hey","hlo","heyy","hii"]
    if any(g == question for g in greetings):
        answer = "Hello! I am your AI assistant. How can I help with your document?"
        return {"answer": answer, "source": "general"}
    


    # question = req.question.lower().strip()
    now = datetime.now()
    hour = now.hour # 0-23 format

    # Define time windows
    if 5 <= hour < 12:
        correct_greeting = "good morning"
    elif 12 <= hour < 17:
        correct_greeting = "good afternoon"
    elif 17 <= hour < 21:
        correct_greeting = "good evening"
    else:
        correct_greeting = "good night"

    # Check for greeting mismatch
    greetings = ["good morning", "good afternoon", "good evening", "good night"]
    user_greeting = next((g for g in greetings if g in question), None)

    if user_greeting:
        if user_greeting == correct_greeting:
            msg = f"{correct_greeting.capitalize()}! How can I help you today?"
        else:
            msg = f"Actually, it's {correct_greeting} right now, but {user_greeting} to you too! How can I help?"
        
        return {"answer": msg, "source": "system"}
    

    # question = req.question.lower().strip()
       
    # Define your triggers and responses
    responses = {
        "thanks_phrases": ["thank you", "thanks", "thanku", "thx", "thnx", "appreciate it"],
        "praise_phrases": ["good work", "great job", "awesome", "well done", "nice work", "you're smart"],
        "closing_phrases": ["bye", "goodbye", "see ya", "talk to you later"]
    }

    # 1. Handle Thanks
    if any(phrase in question for phrase in responses["thanks_phrases"]):
        return {
            "answer": "You're very welcome! I'm happy to help. Have a wonderful day!",
            "source": "system"
        }

    # 2. Handle Praise
    if any(phrase in question for phrase in responses["praise_phrases"]):
        return {
            "answer": "Thank you so much! I'm doing my best to be a helpful assistant. Is there anything else you need?",
            "source": "system"
        }
        
    # 3. Handle Closings
    if any(phrase in question for phrase in responses["closing_phrases"]):
        return {
            "answer": "Goodbye! Feel free to come back if you have more questions about your documents.",
            "source": "system"
        }

   

    # 2. RAG Logic
    if not os.path.exists(PKL_PATH):
        return {"answer": "Please upload a document first.", "source": "error"}

    with open(PKL_PATH, "rb") as f:
        data = pickle.load(f)

    stored_embeddings = np.array(data["embeddings"])
    user_vec = model.encode(question)

    # Cosine Similarity
    norm_stored = np.linalg.norm(stored_embeddings, axis=1)
    norm_user = np.linalg.norm(user_vec)
    similarities = np.dot(stored_embeddings, user_vec) / (norm_stored * norm_user)

    top_indices = np.argsort(similarities)[-4:][::-1]
    retrieved_texts = [data["texts"][i] for i in top_indices if similarities[i] > 0.3]

    answer = llm.generate_answer(question, retrieved_texts)
    chat_history.append(("user", question))
    chat_history.append(("assistant", answer))

    return {"answer": answer, "source": "document"}

@app.get("/history")
def get_history():
    return {"history": chat_history}