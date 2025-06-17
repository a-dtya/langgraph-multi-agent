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

reqItems = [{"item":"tomato","quantity":100},{"item":"potato","quantity":200},{"item":"onion","quantity":500}]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    reqItems: List[Dict[str, Union[str, int]]]
    price: Annotated[List[Dict[str, Union[str, int]]], operator.add]


#define a tool to update the state["price"] every time user provides the price of an item
@tool
def update_price(
    item: str,
    price: int,
    state: Annotated[AgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    config: RunnableConfig
) -> Command[Literal[END, "get_prices"]]:
    """Update the price of an item in the state["price"]"""

    already_added = {p["item"] for p in state["price"]}
    update = []

    if item in [entry["item"] for entry in state["reqItems"]] and price > 0 and item not in already_added:
        update.append({"item": item, "price": price})

    new_price_list = state["price"] + update

    if len(new_price_list) == len(state["reqItems"]):
        result = {"status": "completed"}
        #logic to perform db write
        return Command(update={
            "price": update,  # just the new addition; LangGraph will append
            "messages": [
                ToolMessage(content=str(result), tool_call_id=tool_call_id)
            ]
        }, goto=END)
    else:
        missing = [
            i["item"]
            for i in state["reqItems"]
            if i["item"] not in [p["item"] for p in new_price_list]
        ]
        result = {"status": "incomplete", "missing_items": missing}
        return Command(update={
            "price": update,
            "messages": [
                ToolMessage(content=str(result), tool_call_id=tool_call_id)
            ]
        }, goto="get_prices")


       
tools = [update_price]
model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

#create an agent that gets prices of all items from user as specified in reqItems

def get_prices(state: AgentState) -> AgentState:
    
    system_prompt = SystemMessage(content=f"""
    You are a helpful assistant. You are going to get prices of all items from user as specified in {reqItems}

    - call the update_price tool every time you get the price of an item
    - Make sure to show the current state of prices after every update
    - make only ONE tool call at a time
    """)
    # print(f"\nState: {state["messages"]}")
    if not state["messages"]:
        user_input = f"Ask me for prices of all items as specified in {reqItems}"
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
    print("\n Price List: ", state["price"])

    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState):
    """Determine whether to continue or end the conversation."""
    priceList = state["price"]

    if not priceList:
        return "continue"

    messages = state["messages"]

    for message in reversed(messages):
        if isinstance(message, ToolMessage) and "completed" in message.content.lower():
            return "end"
        return "continue"

def print_messages(messages):
    if not messages:
        return

    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print("\n Tool result: ", message.content)

graph = StateGraph(AgentState)
graph.add_node("get_prices", get_prices)
graph.add_node("tool_node", ToolNode(tools))
graph.add_edge(START, "get_prices")
graph.add_edge("get_prices", "tool_node")
graph.add_conditional_edges("tool_node", should_continue, {
    "continue": "get_prices",
    "end": END
})

app = graph.compile()

def run_price_capture_agent():
    print("\n PRICE CAPTURE STARTED")
    # state = {"messages": [], "reqItems": reqItems, "price": []
    state: AgentState = {"messages": [], "reqItems": reqItems, "price": []}
    
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    # print(state)
    print("\n PRICE CAPTURE ENDED")

if __name__ == "__main__":
    run_price_capture_agent()
    
    