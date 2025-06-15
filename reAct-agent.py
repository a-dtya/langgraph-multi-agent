#reasoning and acting agent
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Sequence # annotated describes the type of a variable, basically stores the metadata of a variable
from langchain_core.messages import SystemMessage, BaseMessage, ToolMessage # base message is the parent class of all message types
#toolmessage is to pass to llm the tool call id and result of tool call
#systemmessage is to pass to llm the instructions
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END #blueprint
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

load_dotenv()

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

class AgentState(StateGraph):
    messages: Annotated[Sequence[BaseMessage],add_messages]

@tool
def add(a: int, b: int):
    """This tool adds two numbers"""
    return a + b

tools = [add]
model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="You are a helpful assistant. Please answer to my query.")

    response = model.invoke([system_prompt]+ state["messages"])

    return {"messages": [response]} # here the reducer fn handles the appending to state["messages"]


#conditional edge
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "our_agent")
graph.add_conditional_edges("our_agent", should_continue, {
    "continue": "tool_node",
    "end": END
})

graph.add_edge("tool_node", "our_agent")

app = graph.compile()

inputs = {"messages": [("user", "What is 1 + 1?")]}

result = app.invoke(inputs)

print(result["messages"])





    
     

