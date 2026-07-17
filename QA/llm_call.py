import google.generativeai as genai

class LLMManager:
    def __init__(self, api_key):
        # Setup the Gemini API
        genai.configure(api_key=api_key)
        # self.model = genai.GenerativeModel('gemini-1.5-flash')
        # self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        # Gemini 3 Flash is the recommended 'best' model as of 2026
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        # self.model = genai.GenerativeModel('models/gemini-flash-lite-latest')

    def generate_answer(self, user_query, retrieved_chunks):
        # Combine the relevant chunks found by your similarity search
        context = "\n\n".join(retrieved_chunks)
        
        # This prompt is the 'filter' that stops 'Applications' 
        # from showing up when asking about 'Types'.
        # prompt = f"""
        # 1)If the user's query is a greeting (like 'Hi' or 'Hello'), respond ONLY with a standard greeting.

        # 2)If the user's query is unrelated to the context, DO NOT greet them. Respond exactly with: "I'm sorry, that information isn't in the document."

        # # 3)DO NOT use your own knowledge to answer.
        # # You are a helpful AI assistant. Answer the user's question based ONLY on the context provided below. 
        
        # # CONTEXT FROM DOCUMENT:
        # # {context}
        
        # # USER QUESTION: 
        # # {user_query}
        
        # # INSTRUCTIONS:
        # # -You are a Q&A assistant. Use only the provided context to answer. If the answer is not in the context, do not greet the user or make things up; say "I'm sorry, that information isn't in the document."
        # # - If the context doesn't contain the answer, say "I'm sorry, that information isn't in the document."
        # # - If questions expects one word answer give in a single word else give detailed.
        # # - Be concise and organized.
        # # - If the user asks for 'Types', do not include 'Applications' even if they are in the context.
        # # """

        prompt = f"""
        SYSTEM ROLE:
        You are a strict Document Retrieval Assistant. Your only job is to extract information from the provided CONTEXT.

        STRICT CONSTRAINTS:
        1. If the USER QUESTION is a greeting (e.g., "Hi", "Hello", "Hey"), reply with: "Hello! How can I help you with the document today?"
        2. If NOT a greeting, look for the USER_QUERY (or keywords like "{user_query}") in the CONTEXT below.
        3. If the keyword or answer is NOT present in the CONTEXT, you MUST respond EXACTLY with: "I'm sorry, that information isn't in the document."
        4. If the answer is NOT found in the CONTEXT below, respond EXACTLY with: "I'm sorry, that information isn't in the document."
        5. Do NOT use your internal knowledge. If the context is empty or irrelevant, trigger the "not in the document" response.
        6. If the user asks for 'Types', do NOT include 'Applications'.
        7. If a one-word answer is sufficient, provide only one word.

        CONTEXT:
        {context}

        USER QUESTION: 
        {user_query}

        """
        
        response = self.model.generate_content(prompt)
        return response.text