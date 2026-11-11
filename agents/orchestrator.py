"""
Multi-Agent Orchestrator using LangGraph (Phase 5)
Controls: Teacher → Researcher → Evaluator flow
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Optional
from agents.teacher_agent import teach
from agents.researcher_agent import research_topic
from agents.evaluator_agent import generate_quiz
import json

# ---------- State ----------
class AgentState(TypedDict):
    user_input: str
    intent: str               # "teach" | "research" | "quiz"
    topic: str
    chat_history: List[Dict]
    teacher_response: Optional[Dict]
    research_response: Optional[Dict]
    quiz_response: Optional[Dict]
    final_output: Optional[Dict]
    error: Optional[str]

# ---------- Nodes ----------
def detect_intent(state: AgentState) -> AgentState:
    """Detect what the user wants based on their message"""
    msg = state["user_input"].lower()
    
    if any(k in msg for k in ["quiz", "test me", "question", "exam", "practice"]):
        intent = "quiz"
    elif any(k in msg for k in ["study plan", "roadmap", "how to learn", "research", "summarize"]):
        intent = "research"
    else:
        intent = "teach"
    
    # Extract topic (simple heuristic)
    topic = state["user_input"]
    for prefix in ["quiz on", "test me on", "study plan for", "research", "teach me", "explain", "what is"]:
        if prefix in msg:
            topic = msg.split(prefix)[-1].strip()
            break
    
    return {**state, "intent": intent, "topic": topic}

def teacher_node(state: AgentState) -> AgentState:
    """Teacher agent node"""
    result = teach(
        user_message=state["user_input"],
        chat_history=state.get("chat_history", []),
        use_rag=True
    )
    return {**state, "teacher_response": result}

def researcher_node(state: AgentState) -> AgentState:
    """Researcher agent node"""
    result = research_topic(state["topic"])
    return {**state, "research_response": result}

def quiz_node(state: AgentState) -> AgentState:
    """Quiz generator node"""
    result = generate_quiz(state["topic"], num_questions=5)
    return {**state, "quiz_response": result}

def output_node(state: AgentState) -> AgentState:
    """Assemble final output"""
    intent = state["intent"]
    
    if intent == "teach" and state.get("teacher_response"):
        final = {
            "type": "teaching",
            "content": state["teacher_response"]["response"],
            "sources": state["teacher_response"]["sources"],
            "used_rag": state["teacher_response"]["used_rag"]
        }
    elif intent == "research" and state.get("research_response"):
        final = {
            "type": "research",
            "content": state["research_response"]
        }
    elif intent == "quiz" and state.get("quiz_response"):
        final = {
            "type": "quiz",
            "content": state["quiz_response"]
        }
    else:
        final = {"type": "error", "content": "Could not process request"}
    
    return {**state, "final_output": final}

# ---------- Route ----------
def route_intent(state: AgentState) -> str:
    return state["intent"]

# ---------- Build Graph ----------
def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("teacher", teacher_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("quiz", quiz_node)
    workflow.add_node("output", output_node)
    
    workflow.set_entry_point("detect_intent")
    
    workflow.add_conditional_edges(
        "detect_intent",
        route_intent,
        {
            "teach": "teacher",
            "research": "researcher",
            "quiz": "quiz"
        }
    )
    
    workflow.add_edge("teacher", "output")
    workflow.add_edge("researcher", "output")
    workflow.add_edge("quiz", "output")
    workflow.add_edge("output", END)
    
    return workflow.compile()

# Global graph instance
edu_graph = build_graph()

def run_agent(user_input: str, chat_history: List[Dict] = None) -> Dict:
    """Main entry point for the multi-agent system"""
    initial_state = AgentState(
        user_input=user_input,
        intent="",
        topic=user_input,
        chat_history=chat_history or [],
        teacher_response=None,
        research_response=None,
        quiz_response=None,
        final_output=None,
        error=None
    )
    
    result = edu_graph.invoke(initial_state)
    return result["final_output"]
