from typing import TypedDict, Sequence, Annotated
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END #blueprint
from langgraph.prebuilt import ToolNode

load_dotenv()

#global variable to store the document content, future use Injection State
document_content = ""


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    

@tool 
def update(content: str) -> str:
    """Updates the document with the provided content."""
    global document_content #to interact with the global variable
    document_content = content

    return f"Document updated successfully. The current document content is: \n{document_content}"
    
    
    