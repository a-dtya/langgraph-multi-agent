from typing import TypedDict, Dict 
from langgraph.graph import StateGraph #blueprint


class AgentState(TypedDict): #agentstate keeps track of information as application runs
    message: str



def greeting_node(state: AgentState) -> AgentState:
    """Node that adds greeting message to the state"""
    state["message"] = f"Hello {state['message']}, how are you?"
    return state
    