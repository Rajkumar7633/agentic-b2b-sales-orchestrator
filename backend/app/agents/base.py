import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base Agent interface establishing standardized metadata, capability tagging,
    and invocation execution wrappers for all NEXORA Pursuit Engine agents.
    """
    def __init__(
        self,
        agent_id: str,
        name: str,
        version: str = "1.0.0",
        capabilities: list[str] | None = None,
        supported_tasks: list[str] | None = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.capabilities = capabilities or []
        self.supported_tasks = supported_tasks or []
        self.status = "HEALTHY"
        self.total_invocations = 0
        self.successful_invocations = 0
        self.failed_invocations = 0
        self.last_execution_latency_ms = 0.0
        self.total_tokens_used = 0
        self.estimated_cost_usd = 0.0
        self.last_heartbeat = datetime.now(timezone.utc)

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        import time
        start_time = time.time()
        self.total_invocations += 1
        self.last_heartbeat = datetime.now(timezone.utc)

        correlation_id = payload.get("correlation_id", "corr_none")
        tenant_id = payload.get("tenant_id", "tenant_default")

        logger.info(
            f"[{self.name}] [AgentID: {self.agent_id}] [CorrelationID: {correlation_id}] "
            f"[TenantID: {tenant_id}] Executing task with payload keys: {list(payload.keys())}"
        )
        try:
            result = await self.run(payload)
            self.successful_invocations += 1
            self.status = "HEALTHY"
            self.last_execution_latency_ms = (time.time() - start_time) * 1000
            logger.info(f"[{self.name}] Completed successfully in {self.last_execution_latency_ms:.2f}ms")
            return result
        except Exception as exc:
            self.failed_invocations += 1
            self.status = "DEGRADED"
            self.last_execution_latency_ms = (time.time() - start_time) * 1000
            logger.error(f"[{self.name}] Execution error in {self.last_execution_latency_ms:.2f}ms: {exc!s}")
            raise exc

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def get_info(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "supported_tasks": self.supported_tasks,
            "total_invocations": self.total_invocations,
            "successful_invocations": self.successful_invocations,
            "failed_invocations": self.failed_invocations,
            "last_execution_latency_ms": round(self.last_execution_latency_ms, 2),
            "total_tokens_used": self.total_tokens_used,
            "estimated_cost_usd": self.estimated_cost_usd,
            "last_heartbeat": self.last_heartbeat.isoformat()
        }
