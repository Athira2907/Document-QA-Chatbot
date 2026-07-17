from langchain_community.document_loaders import PyPDFLoader

# LOAD PDF
loader = PyPDFLoader("Sample_AI.pdf")
docs = loader.load()

full_text = " ".join([doc.page_content for doc in docs])

# STEP 1 : TEXT SPLITTER
from Text_Splitter import text_split
texts = text_split(full_text)

# STEP 2 : SENTENCE TRANSFORMERS - CONVERTING TO VECTORS
from Embedding import sentence_transform
embeddings, model = sentence_transform(texts)


# STEP 3 : USER INPUT
user_in = input("Enter your question: ")
user_embeddings = model.encode(user_in)

# NOTING USER INPUT EMBEDDING IN TXT FILE
with open("chunks_output.txt", "a", encoding="utf-8") as f:
    f.write(f"Embedding shape: {user_embeddings.shape}")
    f.write("")
    f.write(f"Embedding {user_embeddings}")

# STEP 4 : SIMILARITY SEARCH
from Similarity import similarity_check
similarities, stored_data = similarity_check(user_embeddings)


import numpy as np
# Get indices of the Top K matches (e.g., Top 3)
k = 4
top_indices = np.argsort(similarities)[-k:][::-1] 

# STEP 5 : RETRIEVING THE MATCHING SENTENCE FOR THE QUESTION USING LLM
from llm_call import LLMManager

# 1. Get the actual text from your top indices
retrieved_texts = [stored_data[idx]["text"] for idx in top_indices if similarities[idx] > 0.50]

# 2. Initialize Gemini (Replace with your actual API Key)
my_llm = LLMManager(api_key="AIzaSyACum1gsl2y5Bs4fXgcOn_BixlAj9QMoSk") 

# 3. Get the final, clean answer
answer = my_llm.generate_answer(user_in, retrieved_texts)
with open("final_output.txt", "w", encoding="utf-8") as f:
    f.write(f"{answer}")