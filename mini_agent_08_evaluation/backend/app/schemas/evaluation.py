from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    inject_regression: bool = False


class LiveEvaluationRequest(BaseModel):
    api_base_url: str = "http://127.0.0.1:8000"
    actor_id: str = "evaluation-user"
    question: str = "무선 키보드 2개의 재고와 금액을 확인해서 주문해 줘."
