

from src.vectors import ChromaManager
from src.internet import get_text_from_page
from src.completions import create_completion_ollama

chroma = ChromaManager()




long_doc = ""
with open("./very_long_doc.txt", "r", encoding="utf-8") as file:
    long_doc = file.read()


some_docs = ["Charly is a software developer with many years of experience, it is a pleasure to work with him.",
             "Jenniffer is a manicurist, she is very good at what she does.",
             "John is a teacher, he is very patient with his students.",
             "Charly likes to cook pizza all homemade.",
             long_doc]
some_metadatas = [{"source": "Written in Facebook"}, {"source": "Blog of Jenniffer"}, {"source": "Linkedin"}, {"source": "Twitter"}, {"source": "https://docs.trychroma.com/api-reference"}]

chroma.add_documents(docs=some_docs, metadatas=some_metadatas)





# prompt = "How to setup a client in Chroma?"
# context = chroma.get_context_from_query(query_text=prompt, n_results=2)

# chroma.delete()


# system_prompt = f"""You are an useful assistant. Your task is just talk with the user and help him solve his task. You must always answer in the same language as the user message.

# This context may be useful for your task:
# '''
# {context}
# '''
# """

# res = create_completion_ollama(prompt=prompt, system_prompt=system_prompt, stream=True)

