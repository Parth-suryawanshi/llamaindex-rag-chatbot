import os
from typing import Any

from qdrant_client import QdrantClient

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

from config import AppConfig, get_config
from chat_history import (
    add_message,
    get_recent_history,
    format_history_for_prompt,
)


QA_TEMPLATE = PromptTemplate(
    """
You are a helpful RAG assistant.

Use only the context information provided below to answer the user's question.
If the answer is not present in the context, say:
"I don't know based on the uploaded documents."

Do not make up answers.

Context:
---------------------
{context_str}
---------------------

Question:
{query_str}

Answer:
"""
)


def setup_llamaindex(config: AppConfig) -> None:
    Settings.llm = Groq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=config.EMBEDDING_MODEL
    )

    Settings.chunk_size = config.CHUNK_SIZE
    Settings.chunk_overlap = config.CHUNK_OVERLAP


def get_qdrant_client(config: AppConfig) -> QdrantClient:
    return QdrantClient(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        timeout=60,
    )


def get_vector_store(config: AppConfig) -> QdrantVectorStore:
    client = get_qdrant_client(config)

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=config.QDRANT_COLLECTION,
    )

    return vector_store


def reset_collection_if_needed(config: AppConfig) -> None:
    if not config.RESET_COLLECTION:
        return

    client = get_qdrant_client(config)

    try:
        if client.collection_exists(config.QDRANT_COLLECTION):
            client.delete_collection(config.QDRANT_COLLECTION)
            print(f"Deleted old Qdrant collection: {config.QDRANT_COLLECTION}")

    except Exception as e:
        print(f"Collection reset skipped: {e}")


def load_documents(config: AppConfig):
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR, exist_ok=True)
        print(f"Created data folder: {config.DATA_DIR}")
        return []

    documents = SimpleDirectoryReader(
        input_dir=config.DATA_DIR,
        recursive=True,
    ).load_data()

    for doc in documents:
        file_path = doc.metadata.get("file_path", "unknown")
        doc.metadata["source_file"] = os.path.basename(file_path)

    return documents


def ingest_documents(config: AppConfig | None = None) -> int:
    config = config or get_config()

    setup_llamaindex(config)
    reset_collection_if_needed(config)

    documents = load_documents(config)

    if not documents:
        print("No documents found in data folder.")
        return 0

    vector_store = get_vector_store(config)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
        insert_batch_size=128,
    )

    return len(documents)


def get_index(config: AppConfig | None = None) -> VectorStoreIndex:
    config = config or get_config()

    setup_llamaindex(config)

    vector_store = get_vector_store(config)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store
    )

    return index


def get_query_engine(config: AppConfig | None = None):
    config = config or get_config()

    index = get_index(config)

    query_engine = index.as_query_engine(
        similarity_top_k=config.TOP_K,
        response_mode="compact",
        text_qa_template=QA_TEMPLATE,
    )

    return query_engine


def rewrite_question_with_history(question: str) -> str:
    recent_messages = get_recent_history(max_messages=6)

    if not recent_messages:
        return question

    history_text = format_history_for_prompt(recent_messages)

    prompt = f"""
You are rewriting a user's question for a RAG system.

Use the chat history only to understand references like:
- this
- it
- explain more
- tell me again
- same topic

Return only one standalone question.
Do not answer the question.

Chat history:
{history_text}

Current question:
{question}

Standalone question:
"""

    try:
        rewritten_question = Settings.llm.complete(prompt)
        rewritten_question = str(rewritten_question).strip()

        if rewritten_question:
            return rewritten_question

        return question

    except Exception:
        return question


def extract_sources(response: Any) -> list[dict[str, Any]]:
    sources = []

    for source_node in getattr(response, "source_nodes", []):
        node = source_node.node
        metadata = node.metadata or {}

        source_text = node.get_content()

        sources.append(
            {
                "file": metadata.get("source_file")
                or metadata.get("file_name")
                or metadata.get("file_path")
                or "unknown",
                "page": metadata.get("page_label", "N/A"),
                "score": float(source_node.score) if source_node.score else None,
                "text": source_text[:700],
            }
        )

    return sources


def ask_question(
    question: str,
    query_engine=None,
    config: AppConfig | None = None,
    save_history: bool = True,
):
    if not question or not question.strip():
        return "Please ask a valid question.", []

    if query_engine is None:
        query_engine = get_query_engine(config)

    standalone_question = rewrite_question_with_history(question)

    response = query_engine.query(standalone_question)

    answer = str(response)
    sources = extract_sources(response)

    if save_history:
        add_message(role="user", content=question)
        add_message(role="assistant", content=answer, sources=sources)

    return answer, sources

