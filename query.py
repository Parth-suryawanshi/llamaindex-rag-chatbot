from rag_core import get_query_engine, ask_question
from chat_history import clear_chat_history


def main():
    print("Loading RAG query engine...")
    query_engine = get_query_engine()

    print("RAG is ready.")
    print("Type your question.")
    print("Type 'exit' to stop.")
    print("Type 'clear' to clear chat history.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("Exiting...")
            break

        if question.lower() == "clear":
            clear_chat_history()
            print("Chat history cleared.\n")
            continue

        answer, sources = ask_question(
            question=question,
            query_engine=query_engine,
            save_history=True,
        )

        print("\nAssistant:")
        print(answer)

        if sources:
            print("\nSources:")
            for i, source in enumerate(sources, start=1):
                print(f"\nSource {i}")
                print(f"File: {source['file']}")
                print(f"Page: {source['page']}")
                print(f"Score: {source['score']}")
                print(f"Text: {source['text'][:300]}...")

        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()