from config import get_config
from rag_core import ingest_documents


def main():
    config = get_config()

    print("Starting document ingestion...")
    print(f"Data folder: {config.DATA_DIR}")
    print(f"Qdrant collection: {config.QDRANT_COLLECTION}")

    total_docs = ingest_documents(config)

    if total_docs == 0:
        print("\nNo documents were ingested.")
        print("Please add PDF/DOCX/TXT files inside the data folder.")
        return

    print("\nIngestion completed successfully.")
    print(f"Total documents loaded: {total_docs}")
    print(f"Vectors stored in Qdrant collection: {config.QDRANT_COLLECTION}")


if __name__ == "__main__":
    main()