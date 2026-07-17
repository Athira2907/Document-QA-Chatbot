from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_split(text):
    # STEP 1 : TEXT SPLITTER
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=0,separators=["\n\n", "\n", ". ", " ",""])
    texts = text_splitter.split_text(text)

    # NOTING CHUNK SPLITTING IN TXT FILE
    with open("chunks_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Number of Chunks: {len(texts)}\n\n")
        for i, chunk in enumerate(texts):
            f.write(f"Chunk {i+1}:\n{chunk}\n\n")

    return texts