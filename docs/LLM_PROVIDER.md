# LLM Provider Strategy (`docs/LLM_PROVIDER.md`)

## 1. Multi-Provider Architecture

NEXORA implements `BaseLLMProvider` interface with dynamic runtime routing:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass
```

## 2. Supported LLM Backends

1. **Groq (`GrokProvider` with `gsk_...` key)**:
   - **Model**: `llama-3.3-70b-versatile`
   - **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
   - **Performance**: High speed (~300ms latency), structured JSON enforcement (`response_format: {"type": "json_object"}`).

2. **xAI Grok (`GrokProvider` with `xai-...` key)**:
   - **Model**: `grok-beta`
   - **Endpoint**: `https://api.x.ai/v1/chat/completions`

3. **Mock Fallback (`MockLLMProvider`)**:
   - High-speed deterministic fallback used when LLM API keys are absent or endpoints time out.
