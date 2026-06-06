from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    research_node,
    linkedin_node,
    vision_node,
    persona_scoring_node,
    alignment_node,
    outreach_node,
    crm_node
)

def create_graph():
    graph = StateGraph(AgentState)
    graph.add_node("research", research_node)
    graph.add_node("linkedin", linkedin_node)
    graph.add_node("vision", vision_node)
    graph.add_node("persona_scoring", persona_scoring_node)
    graph.add_node("alignment", alignment_node)
    graph.add_node("outreach", outreach_node)
    graph.add_node("crm", crm_node)
    
    graph.set_entry_point("research")
    graph.add_edge("research", "linkedin")
    graph.add_edge("linkedin", "vision")
    graph.add_edge("vision", "persona_scoring")
    graph.add_edge("persona_scoring", "alignment")
    graph.add_edge("alignment", "outreach")
    graph.add_edge("outreach", "crm")
    graph.add_edge("crm", END)
    
    return graph.compile()