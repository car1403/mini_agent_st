from app.graphs.travel_graph import run_graph
from app.schemas.agent import AgentRequest, AgentResponse


def run_agent(request: AgentRequest) -> AgentResponse:
    return AgentResponse.model_validate(run_graph(request.question.strip()))
