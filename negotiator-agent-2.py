import operator
from typing import Literal, TypedDict, Sequence, Annotated, List, Dict, Union, Set 
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END #blueprint
from langgraph.prebuilt import ToolNode, InjectedState
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig

load_dotenv()

currentPriceList = [{"item":"tomato","rate":25},{"item":"potato","rate":35}]
targetPriceList = [{"item":i["item"], "rate":int(i["rate"]*0.8)} for i in currentPriceList]

print("Current Price List: ", currentPriceList)
print("Target Price List: ", targetPriceList)