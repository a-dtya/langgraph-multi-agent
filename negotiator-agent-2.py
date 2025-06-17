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

# print("Current Price List: ", currentPriceList)
# print("Target Price List: ", targetPriceList)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    currentPriceList: List[Dict[str, Union[str, int]]]
    targetPriceList: List[Dict[str, Union[str, int]]]
    

def negotiator(state: AgentState) -> AgentState:
    
    system_prompt = SystemMessage(content=f"""
    You are a helpful assistant. You are going to negotiate prices of all items from user.
    The current price list is: {state["currentPriceList"]}
    The target price list is: {state["targetPriceList"]}
    You are going to ask supplier to reduce prices to target prices.

    - call the update_current_price tool every time you get the price of an item which is lesser than it's rate in {state["currentPriceList"]}
    - Make sure to show the current state of prices after every update
    - make only ONE tool call at a time
    """)
    # print(f"\nState: {state["messages"]}")
    if not state["messages"]:
        user_input = f"Try negotiating prices of all items in {state["currentPriceList"]} to target prices in {state["targetPriceList"]}"
        user_message = HumanMessage(content=user_input)

    else:
        #check if the last message is of type ToolMessage, if so, skip the user input
        if isinstance(state["messages"][-1], ToolMessage):
            user_input = ""
        else:
            user_input = input("\nYour response: ")
        
        print(f"User: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = model.invoke(all_messages)

    print("\nAssistant: ", response.content)
    # print("\n Price List: ", state["price"])

    return {"messages": list(state["messages"]) + [user_message, response]}