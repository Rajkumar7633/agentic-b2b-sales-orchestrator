"""
Memory Components Unit Tests
Covers SessionMemory and WorkingMemory local fallback operations,
retrieval, appending, and clearing.
"""
import pytest

from app.memory.session import session_memory
from app.memory.working import working_memory


@pytest.mark.asyncio
async def test_session_memory_operations():
    session_id = "test_sess_100"

    # 1. Initially empty
    history = await session_memory.get_session_history(session_id)
    assert history == []

    # 2. Append interaction
    interaction = {"role": "user", "content": "Hello NEXORA"}
    await session_memory.append_interaction(session_id, interaction)

    # 3. Retrieve appended history
    history = await session_memory.get_session_history(session_id)
    assert len(history) == 1
    assert history[0]["content"] == "Hello NEXORA"

    # 4. Clear session
    await session_memory.clear_session(session_id)
    history = await session_memory.get_session_history(session_id)
    assert history == []


@pytest.mark.asyncio
async def test_working_memory_operations():
    corr_id = "corr_test_state_200"

    # 1. Initially None
    state = await working_memory.get_state(corr_id)
    assert state is None

    # 2. Set state
    data = {"step": 2, "status": "IN_PROGRESS", "metadata": {"company": "Acme"}}
    await working_memory.set_state(corr_id, data)

    # 3. Get state
    state = await working_memory.get_state(corr_id)
    assert state is not None
    assert state["step"] == 2
    assert state["metadata"]["company"] == "Acme"

    # 4. Delete state
    await working_memory.delete_state(corr_id)
    state = await working_memory.get_state(corr_id)
    assert state is None
