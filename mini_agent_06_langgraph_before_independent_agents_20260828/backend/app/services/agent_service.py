from app.graphs.travel_graph import run_graph
from app.schemas.agent import AgentRequest, AgentResponse


async def run_agent(request: AgentRequest) -> AgentResponse:
    return AgentResponse.model_validate(await run_graph(request.question.strip()))
