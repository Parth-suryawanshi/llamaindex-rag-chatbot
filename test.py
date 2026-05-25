import os
from dotenv import load_dotenv
load_dotenv()


api_key=os.getenv("GROQ_API_KEY")


from llama_index.core import VectorStoreIndex,SimpleDirectoryReader,Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 1. Set Groq as LLM
Settings.llm = Groq(
    model="llama-3.1-8b-instant",
    api_key=api_key
)

# 2. Set local embedding model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


#it creates a metadata 
documents=SimpleDirectoryReader("data").load_data()
 
#pdf content converts in vectors then into index
index= VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir="./storage")

query_engine = index.as_query_engine()

response= query_engine.query("what is transformer")
print(response)


