import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def similarity_check(user_embeddings):
    # STEP 4 : SIMILARITY SEARCH
    # 1. Load the structured data (List of dicts: [{"text": "...", "embedding": [...]}, ...])
    with open("embedding_out.pkl", "rb") as f:
        stored_data = pickle.load(f)

    # 2. Extract vectors and convert to NumPy array
    all_vectors = np.array([item["embedding"] for item in stored_data])

    # 3. Get User Input Embedding (Example: user_embedding)
    user_vec = user_embeddings.reshape(1, -1)

    # 4. Calculate similarities
    similarities = cosine_similarity(user_vec, all_vectors)[0]
    # print(similarities)
    return similarities, stored_data

