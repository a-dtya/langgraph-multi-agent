#reasoning and acting agent
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Sequence # annotated describes the type of a variable, basically stores the metadata of a variable
from langchain_core.messages import SystemMessage, BaseMessage, ToolMessage # base message is the parent class of all message types
#toolmessage is to pass to llm the tool call id and result of tool call
#systemmessage is to pass to llm the instructions
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END #blueprint
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

#add_messages is a reducer function
#it tells us how to merge data into the current state

#without reducer, updates would have replaced the existing values entirely

# #without reducer
# state = {"messages": ["hi"]}
# update = {"messages": ["hello"]}
# new_state = {"messages": ["hello"]}

# #with reducer
# state = {"messages": ["hi"]}
# update = {"messages": ["hello"]}
# new_state = {"messages": ["hi", "hello"]} append is not an option in complex workflows



