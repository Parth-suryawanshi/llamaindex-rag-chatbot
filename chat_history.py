import json
import os
from typing import Any

from config import get_config


def get_history_file() -> str:
    config = get_config()
    return config.CHAT_HISTORY_FILE


def load_chat_history() -> list[dict[str, Any]]:
    history_file = get_history_file()

    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        if isinstance(data,list):
            return data
        
        return []
    
    except Exception :
        return []
    
def save_chat_history(messages: list[dict[str,Any]]) -> None:
    history_file = get_history_file()
    
    with open(history_file, "w" , encoding= "utf-8") as  file:
        json.dump(messages,file,indent=4,ensure_ascii=False)
        
        
def create_message(
    role: str,
    content:str,
    sources: list[dict[str, Any]] | None = None, )-> dict[str, Any]:

    message={
        "role": role,
        "content":content
    }
    
    if sources is not None:
        message["sources"]=sources
        
    return message

def add_message(
    role:str,
    content:str,
    sources: list[dict[str,Any]] | None = None, ) -> None:
    messages = load_chat_history()
    
    messages.append(
        create_message(
            role=role,
            content=content,
            sources=sources
        )
    )
    
    save_chat_history(messages)
    
    
# Clear Chat History Function 
def clear_chat_history()-> None:
    save_chat_history([])
    
def get_recent_history(max_messages: int=6  ) -> list[dict[str,Any]]:
    messages=load_chat_history()
    return messages[-max_messages:]
    
def format_history_for_prompt(messages: list[dict[str,Any]])-> str:
    if not messages:
        return "No previous chat history"
    
    formatted_messages=[]
    
    for message in messages:
        role=message.get("role","unknown")
        content=message.get("content","")
        
        if not content:
            continue
        
        formatted_messages.append(f"{role}:{content}")
        
    
    return "\n".join(formatted_messages)