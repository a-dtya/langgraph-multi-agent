from typing import TypedDict, List 
from langgraph.graph import StateGraph, START, END #blueprint

import random

class AgentState(TypedDict): #agentstate keeps track of information as application runs (state schema)
    name: str
    number: List[int]
    counter: int


def greeting_node(state: AgentState) -> AgentState:
    """Node that adds greeting message to the state"""
    state["name"] = f"Hello {state['name']}, how are you?"
    state["counter"] = 0
    return state


def random_node(state: AgentState) -> AgentState:
    """Node that adds random number to the state"""
    if "number" not in state:
        state["number"] = []
    else:
        state["number"].append(random.randint(0, 10))
    state["counter"] += 1
    return state

def should_continue(state: AgentState) -> AgentState:
    """Node that decides whether to continue or not"""
    if state["counter"] < 5:
        print("Entering loop with counter value", state["counter"])
        return "loop"
    else:
        return "exit"

graph = StateGraph(AgentState)
graph.add_node("greeting", greeting_node)
graph.add_node("random", random_node)

graph.add_edge(START, "greeting")
graph.add_edge("greeting", "random")
graph.add_conditional_edges("random", should_continue, {
    "loop": "random",
    "exit": END
})

app = graph.compile()

result = app.invoke({"name": "John"})

print(result["number"])



