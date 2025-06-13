from typing import TypedDict, List 
from langgraph.graph import StateGraph, START, END #blueprint

class AgentState(TypedDict): #agentstate keeps track of information as application runs (state schema)
    number1: int
    operation: str
    number2: int
    result: int

def adder(state: AgentState) -> AgentState:
    """This function adds two numbers"""

    state["result"] = state["number1"] + state["number2"]

    return state

def subtractor(state: AgentState) -> AgentState:
    """This function subtracts two numbers"""

    state["result"] = state["number1"] - state["number2"]

    return state

def decide_next_node(state: AgentState) -> AgentState:
    """This function decides which node to run next"""

    if state["operation"] == "+":
        return "addition_operation"
    else:
        return "subtraction_operation"

graph = StateGraph(AgentState)
graph.add_node("router", lambda state:state) #passthrough node
graph.add_node("add_node", adder)
graph.add_node("subtract_node", subtractor)

graph.add_edge(START, "router")
graph.add_conditional_edges("router", decide_next_node, {
    "addition_operation": "add_node",
    "subtraction_operation": "subtract_node"
})
graph.add_edge("add_node", END)
graph.add_edge("subtract_node", END)

app = graph.compile()

result = app.invoke({"number1": 1, "operation": "-", "number2": 2})

print(result["result"])
        