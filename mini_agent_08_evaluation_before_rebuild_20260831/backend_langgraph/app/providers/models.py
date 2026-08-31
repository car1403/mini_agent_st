"""Provider Adapter가 반환하는 공통 결과 모델입니다."""

from dataclasses import asdict,dataclass
from typing import Any

@dataclass
class ProviderResult:
    provider:str
    model:str
    content:Any
    latency_ms:int
    fallback_used:bool=False
    def to_dict(self)->dict[str,Any]: return asdict(self)
