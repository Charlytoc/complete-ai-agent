import json
from src.completions import create_completion_ollama
from src.utils.extract_substring import extract_substring


class CustomTextSplitter:
    def __init__(self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    def generate_text_objective(self, text):
        _system_prompt = """You work at the backend of a vector storage application. 
        We want to categorize the text in a way that is easier to retrieve and analyze.


        You need to extract the objective of any given text, understand the importance of the document to use it in the future.

        
        Give your entire response in the following format:

        Thought about the text, meditation about the text, and then write the objective in the following format:

        _objective_
        A brief explanation of up to 300 characters of the main objective of the text.
        _end_

        _objective_ and _end_ are delimiters to separate the objective from the rest of the text. They are mandatory.
        """
        
        if not text:
            return ""
        res = create_completion_ollama(
            prompt=text, system_prompt=_system_prompt, stream=False
        )
        objective = extract_substring(res, "_objective_", "_end_")
        return objective


    def create_ai_chunks(self, text, objective):
        _system_prompt = f"""You work at the backend of a vector storage application. 
        We want to enhance vector retrieval for a chat application, for that reason, we want to save multiple affirmative phrases and vectorized them for each piece of text, in that way, is easier to get relevant results.

        This is the objective of the document the following text is extracted from:
        {objective}

        Your task is the following:

        Generate up to 3 affirmative phrases from the extractable knowledge from the text in the same language as the text. 
        Each phrase must represent something real from the given text.
        Separate each phrase with a new line.

        Give your entire response in the following format:

        _affirmatives_
        First affirmation\n
        Second affirmation\n
        Third affirmation
        _end_

        _affirmatives_ and _end_ are delimiters to separate the affirmations from the rest of the text. They are mandatory.

        
        """
        if not text:
            return []
        res = create_completion_ollama(
            prompt=text, system_prompt=_system_prompt, stream=True
        )
        affirmations = extract_substring(res, "_affirmatives_", "_end_")
        return [
            a.strip()
            for a in affirmations.split("\n")
            if (a.strip() and isinstance(a, str))
        ]

    def split_text(self, text):
        if len(text) <= self.chunk_size:
            return [text]
        else:
            chunks = []
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunks.append(text[start:end])
                start += self.chunk_size - self.chunk_overlap
            return chunks

    def split_documents(self, docs: list[str], metadatas: list[dict] = None):
        if metadatas is None:
            metadatas = [{} for _ in docs]

        if len(docs) != len(metadatas):
            raise ValueError("The number of documents and metadatas must be the same")

        splits = []
        final_metadatas = []

        for i, d in enumerate(docs):
            if not isinstance(d, str):
                raise ValueError("Each document must be a string")
            
            _objective = self.generate_text_objective(d)
            _chunks = self.split_text(d)
            _metadata = metadatas[i]
            _metadata["original_text"] = d

            for c in _chunks:
                splits.append(c)
                final_metadatas.append(_metadata.copy())
                ai_chunks = self.create_ai_chunks(c, _objective)

                for ai_chunk in ai_chunks:
                    splits.append(ai_chunk)
                    final_metadatas.append({"original_text": c})

        assert len(splits) == len(final_metadatas)
        return splits, final_metadatas


class ChromaManager:
    chunk_size = 500
    chunk_overlap = 50

    def __init__(self, path="chroma_db", collection_name="default_collection"):
        import chromadb
        self.client = chromadb.PersistentClient(path=path)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(collection_name)

    def create_ids(self, n):
        import uuid

        return [str(uuid.uuid4()) for _ in range(n)]

    def add_documents(self, docs: list[str], metadatas=None):
        if metadatas is None:
            metadatas = [{} for _ in docs]

        splitter = CustomTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        splits, _metadatas = splitter.split_documents(docs, metadatas)
        ids = self.create_ids(len(splits))
        self.collection.add(ids=ids, documents=splits, metadatas=_metadatas)
    def count_documents(self):
        return self.collection.count()

    def delete(self):
        self.client.delete_collection(self.collection_name)
        self.client.reset()

    def query(self, query_text, n_results=1):
        return self.collection.query(query_texts=[query_text], n_results=n_results)

    def list_collections(self):
        return self.client.list_collections()

    def get_context_from_query(self, query_text, n_results=1):
        results = self.query(query_text, n_results)
        context = ""

        for n in range(len(results["ids"][0])):
            _metadata = results["metadatas"][0][n]
            # Remove the key original_text from metadata
            original_text = _metadata.pop("original_text", None)
            context += f"Document {n+1} ({_metadata}): {original_text}\n\n"

        return context
