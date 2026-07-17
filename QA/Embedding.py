# STEP 2 : SENTENCE TRANSFORMERS - CONVERTING TO VECTORS
from sentence_transformers import SentenceTransformer

def sentence_transform(texts):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

    embeddings = model.encode(texts)

    # PICKLING CHUNK AND EMBEDDING IN .pkl FILE
    # Create a list of dictionaries containing both text and vector
    data_to_save = []
    for i, chunk in enumerate(texts): # 'chunks' are the text strings from your splitter
        data_to_save.append({
            "text": chunk,
            "embedding": embeddings[i]
        })

    # Save the structured object as binary
    import pickle
    with open("embedding_out.pkl", "wb") as f:
        pickle.dump(data_to_save, f)

    return embeddings, model