import os
from typing import TypedDict, List, Union 
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI 
from langgraph.graph import StateGraph, START, END #blueprint
from dotenv import load_dotenv 

load_dotenv()

class AgentState(TypedDict): #agentstate keeps track of information as application runs (state schema)
    messages: List[Union[HumanMessage, AIMessage]] # to store either human or AI messages in state["messages"]

llm = ChatOpenAI(model="gpt-4o-mini")

def process(state: AgentState) -> AgentState:
    """This node will solve the request you input """
    response = llm.invoke(state["messages"])

    state["messages"].append(AIMessage(content=response.content))
    print(f"Assistant: {response.content}")
    print("\n Current State: ", state["messages"])
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()

conversation_history = []

user_input = input("User: ")

while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    #if the number of HumanMessages exceeds 5, remove the first HumanMessage
    if len(conversation_history) > 10:
        for message in conversation_history:
            if isinstance(message, HumanMessage):
                conversation_history.remove(message)
                break
            elif isinstance(message, AIMessage):
                conversation_history.remove(message)
    result = agent.invoke({"messages": conversation_history})
    conversation_history = result["messages"]
    user_input = input("User: ")

#for prototyping, using local save
with open("logging.txt", "w") as f:
    f.write("Conversation Starts...\n\n")

    for message in conversation_history:
        if isinstance(message, HumanMessage):
            f.write(f"User: {message.content}\n")
        elif isinstance(message, AIMessage):
            f.write(f"Assistant: {message.content}\n\n")

    f.write("Conversation Ends...\n\n\n")
    





    
    

