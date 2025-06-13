from typing import TypedDict, List 
from langgraph.graph import StateGraph #blueprint

class AgentState(TypedDict): #agentstate keeps track of information as application runs (state schema)
    name: str
    age: str
    final: str

def first_node(state: AgentState) -> AgentState:
    """This is the first node"""

    state["final"] = f"Hi there {state['name']},"

    return state

def second_node(state: AgentState) -> AgentState:
    """This is the second node"""

    state["final"] += f" you are {state['age']} years old"

    return state

graph = StateGraph(AgentState)
graph.add_node("first_node", first_node)
graph.add_node("second_node", second_node)

graph.set_entry_point("first_node")
graph.add_edge("first_node", "second_node")
graph.set_finish_point("second_node")

app = graph.compile()

result = app.invoke({"name": "John", "age": "30"})

print(result["final"])
