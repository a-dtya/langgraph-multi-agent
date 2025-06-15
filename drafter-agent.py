from typing import TypedDict, Sequence, Annotated
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END #blueprint
from langgraph.prebuilt import ToolNode

load_dotenv()

#global variable to store the document content, future use Injection State
document_content = ""


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    

@tool 
def update(content: str) -> str:
    """Updates the document with the provided content."""
    global document_content #to interact with the global variable
    document_content = content

    return f"Document updated successfully. The current document content is: \n{document_content}"

#save tool is called, towards conversation completion to save draft into a txt file

@tool
def save(filename: str) -> str:
    """ Save the current document to a text file and finish the process. 
    
    Args:
        filename (str): The name of the text file to save the document to.

    """ 
    global document_content

    if not filename.endswith(".txt"):
        filename += ".txt"
        
    try:
        with open(filename, "w") as f:
            f.write(document_content)
        print(f"Success: Document saved successfully to {filename}")
        return f"Success: Document saved successfully to {filename}"
    except Exception as e:
        return f"Error: Failed to save document: {str(e)}"


tools = [save, update]

model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
        You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
        
        - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
        - If the user wants to save and finish, you need to use the 'save' tool.
        - Make sure to always show the current document state after modifications.
        
        The current document content is:{document_content}
        """)
    if not state["messages"]:
        user_input = "I will help you to update a document. What would you like to create?"
        user_message = HumanMessage(content=user_input)

    else:
        user_input = input("\nWhat would you like to do with the document? ")
        
        print(f"User: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = model.invoke(all_messages)

    print("\nAssistant: ", response.content)
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"using tools: {[tc.name for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}

    
    
    

        





    
    