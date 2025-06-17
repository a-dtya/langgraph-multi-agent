from typing import TypedDict, Sequence, Annotated
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END #blueprint
from langgraph.prebuilt import ToolNode

load_dotenv()

reqItems = [{"item":"tomato","quantity":100},{"item":"potato","quantity":200},{"item":"onion","quantity":500}]

def AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    reqItems: List[Dict[str, Union[str, int]]]
    price: List[Dict[str, Union[str, int]]]





#define a tool to update the state["price"] every time user provides the price of an item
@tool
def update_price(item: str, price: int) -> dict:
    """Update the price of an item in the state["price"]"""
    if item in [item["item"] for item in reqItems] and price > 0:
        state["price"].append({"item": item, "price": price})
    
    if len(state["price"]) == len(reqItems):
        return {"status": "completed"}
    
    return {"status": "incomplete"}
       
tools = [update_price]
model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

#create an agent that gets prices of all items from user as specified in reqItems

def get_prices(state: AgentState) -> AgentState:
    
    system_prompt = SystemMessage(content=f"""
    You are a helpful assistant. You are going to get prices of all items from user as specified in {reqItems}

    - call the update_price tool every time you get the price of an item
    - Make sure to show the current state of prices after every update
    """)
    
    if not state["messages"]:
        user_input = f"Ask me for prices of all items as specified in {reqItems}"
        user_message = HumanMessage(content=user_input)

    else:
        user_input = input("\nYour response: ")
        
        print(f"User: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = model.invoke(all_messages)

    print("\nAssistant: ", response.content)
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"using tools: {[tc.name for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}
    