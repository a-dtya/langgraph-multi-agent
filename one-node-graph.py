from typing import TypedDict, Dict 
from langgraph.graph import StateGraph #blueprint


class AgentState(TypedDict): #agentstate keeps track of information as application runs (state schema)
    message: str

def greeting_node(state: AgentState) -> AgentState:
    """Node that adds greeting message to the state"""
    state["message"] = f"Hello {state['message']}, how are you?"
    return state

graph = StateGraph(AgentState)
graph.add_node("greeting", greeting_node)

graph.set_entry_point("greeting")
graph.set_finish_point("greeting")

app = graph.compile()

result = app.invoke({"message": "John"})

print(result["message"])