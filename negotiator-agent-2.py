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
import asyncio
from aioconsole import ainput

load_dotenv()

currentPriceList = [{"item":"tomato","rate":25},{"item":"potato","rate":35}]
targetPriceList = [{"item":i["item"], "rate":int(i["rate"]*0.8)} for i in currentPriceList]

# print("Current Price List: ", currentPriceList)
# print("Target Price List: ", targetPriceList)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    currentPriceList: List[Dict[str, Union[str, int]]]
    targetPriceList: List[Dict[str, Union[str, int]]]
    
@tool
def update_current_price(
    item: str,
    price: int,
    state: Annotated[AgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    config: RunnableConfig) -> Command[Literal["negotiator"]]:
    """Update the price of an item in the state["currentPriceList"]"""
    if item in [entry["item"] for entry in state["currentPriceList"]] and price > 0:
        for entry in state["currentPriceList"]:
            if entry["item"] == item and price < entry["rate"]:
                entry["rate"] = price
                break
        return Command(update={
            "currentPriceList": state["currentPriceList"],
            "messages": [
                ToolMessage(content=str({"status": "updated", "item": item, "price": price}), tool_call_id=tool_call_id)
            ]
        }, goto="negotiator")

@tool
def exit(state: Annotated[AgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    config: RunnableConfig) -> Command[Literal[END]]:
    """Exit the conversation"""
    print("\nConversation ended with final price list: ", state["currentPriceList"])
    return Command(update={"messages": list(state["messages"])+[ToolMessage(content="Conversation ended", tool_call_id=tool_call_id)]}, goto=END)

async def negotiator(state: AgentState) -> AgentState:
    
    system_prompt = SystemMessage(content=f"""
    You are a helpful assistant. You are going to negotiate prices of all items from user.
    The current price list is: {state["currentPriceList"]}
    The target price list is: {state["targetPriceList"]}
    You are going to ask supplier to reduce prices. They don't have to reduce prices to {state["targetPriceList"]}, try lowering the rates from {state["currentPriceList"]}

    IMPORTANT: 
    1. Don't ask multiple questions like -  \"The price of 30 for potatoes is still above our target price of 28. Can we lower it to meet our target? If not, would you like to end the conversation?\"
    2. Ask only one question at a time, either confirm the rate or prompt to end conversation

    INSTRUCTIONS:
    - call the update_current_price tool every time you get the price of an item which is lesser than it's rate in {state["currentPriceList"]}
    - Make sure to show the current state of prices after every update
    - make only ONE tool call at a time
    - if supplier not interested in reducing price, ask if supplier wants to end the conversation, if yes, then call exit tool
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
            user_input = await ainput("\nYour response: ")
        
        print(f"User: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = await model.ainvoke(all_messages)

    print("\nAssistant: ", response.content)
    # print("\n Price List: ", state["price"])

    return {"messages": list(state["messages"]) + [user_message, response]}

tools = [update_current_price, exit]
model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

def should_exit(state: AgentState):
    """Determine whether to exit or continue the conversation."""
    if not state["messages"]:
        return "continue"
    
    messages = state["messages"]

    for message in reversed(messages):
        if isinstance(message, ToolMessage) and "Conversation ended" in message.content:
            return "exit"
        return "continue"

graph = StateGraph(AgentState)
graph.add_node("negotiator", negotiator)
graph.add_node("tool_node", ToolNode(tools))
graph.add_edge(START, "negotiator")
graph.add_edge("negotiator", "tool_node")
graph.add_conditional_edges("tool_node", should_exit, {
    "exit": END,
    "continue": "negotiator"
})

app = graph.compile()

def print_messages(messages):
    if not messages:
        return

    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print("\n Tool result: ", message.content)

# async def run_price_reducer_agent():
#     print("\n PRICE REDUCER STARTED")
#     # state = {"messages": [], "reqItems": reqItems, "price": []
#     state: AgentState = {"messages": [], "currentPriceList": currentPriceList, "targetPriceList": targetPriceList}
    
#     async for step in app.astream(state, stream_mode="values"):
#         if "messages" in step:
#             print_messages(step["messages"])
#     # print(state)
#     print("\n PRICE REDUCER ENDED")

# if __name__ == "__main__":
#     run_price_reducer_agent()

async def run_func():
    state: AgentState = {"messages": [], "currentPriceList": currentPriceList, "targetPriceList": targetPriceList}
    
    async for step in app.astream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    
#create a task using asyncio.create_task to execute run_func and another task that timeout for 20 seconds, after 20 seconds, callback run_func task cancel
async def main():
    task = asyncio.create_task(run_func())
    timeout_task = asyncio.create_task(asyncio.sleep(20))
    done, pending = await asyncio.wait([task, timeout_task], return_when=asyncio.FIRST_COMPLETED)
    if timeout_task in done:
        task.cancel()
        print("\nTimeout: Negotiation not completed in 20 seconds")
    else:
        print("\nNegotiation completed")

if __name__ == "__main__":
    asyncio.run(main())