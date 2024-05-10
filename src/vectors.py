from src.completions import create_completion_ollama
from src.utils.extract_substring import extract_substring



class CustomTextSplitter:
    def __init__(self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_ai_chunks(self, text):
        _system_prompt = """You work at the backend of a vector storage application. We want to enhance vector retrieval for a chat application, for that reason, we want to save multiple vectors for each piece of text, save the text as metadata, and embed just simple phrases. In that way, is easier to get relevant results.

        Your task is the following:

        Generate 5 questions or phrases associated with the given text. 
        Each phrase of question must represent a hypotetical query that a user could ask from the given text.
        Separate each phrase with a new line.
        Give your entire response in the following format:

        _affirmatives_
        First affirmation\n
        Second affirmation\n
        Third affirmation
        _end_
        """
        res = create_completion_ollama(prompt=text, system_prompt=_system_prompt, stream=True)
        afirmations = extract_substring(res, "_affirmatives_", "_end_")
        return [a.strip() for a in afirmations.split("\n") if a.strip()]

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
        # ai_splits = []
        final_metadatas = []

        for i, d in enumerate(docs):
            if not isinstance(d, str):
                raise ValueError("Each document must be a string")

            _chunks = self.split_text(d)
            _metadata = metadatas[i]
            _metadata["original_text"] = d

            final_metadatas.extend([_metadata for _ in _chunks])
            splits.extend(_chunks)
        
        # for i, s in enumerate(splits):
        #     affirmations = self.create_ai_chunks(s)
        #     ai_splits.extend(affirmations)
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

        splitter = CustomTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        
        splits, _metadatas = splitter.split_documents(docs, metadatas)
        ids = self.create_ids(len(splits))
        self.collection.add(ids=ids, documents=splits, metadatas=_metadatas)

    def delete(self):
        self.client.delete_collection(self.collection_name)

    def query(self, query_text, n_results=1):
        return self.collection.query(query_texts=[query_text], n_results=n_results)
    
    def get_context_from_query(self, query_text, n_results=1):
        results = self.query(query_text, n_results)
        context = ""

        for n in range(len(results["ids"][0])):
            _metadata = results["metadatas"][0][n]
            # Remove the key original_text from metadata
            _metadata.pop("original_text", None)
            context += f"Document {n+1} ({_metadata}): {results['documents'][0][n]}\n\n"

        return context
