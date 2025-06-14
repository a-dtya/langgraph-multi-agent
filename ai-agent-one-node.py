from typing import TypedDict, List 
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI 
from langgraph.graph import StateGraph, START, END #blueprint
from dotenv import load_dotenv 

load_dotenv()

class AgentState(TypedDict): #agentstate keeps track of information as application runs (state schema)
    messages: List[HumanMessage]

llm = ChatOpenAI(model="gpt-4o-mini")

def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])
    print(f"Assistant: {response}")

    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()

user_input = input("User: ")
agent.invoke({"messages": [HumanMessage(content=user_input)]})