from typing import TypedDict, List 
from langgraph.graph import StateGraph #blueprint

class AgentState(TypedDict): #agentstate keeps track of information as application runs (state schema)
    values: List[int]
    name: str
    result: str

def process_values(state: AgentState) -> AgentState:
    """This function handles multiple different inputs"""

    state["result"] = f"Hi there {state['name']}, your sum is {sum(state['values'])}"

    return state

graph = StateGraph(AgentState)
graph.add_node("process_values", process_values)

graph.set_entry_point("process_values")
graph.set_finish_point("process_values")

app = graph.compile()

result = app.invoke({"values": [1, 2, 3], "name": "John"})

print(result["result"])
