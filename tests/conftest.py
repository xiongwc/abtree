import pytest
import asyncio


@pytest.fixture(autouse=True)
def setup_event_loop() -> None:
    """Ensure event loop is available for tests."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # Create a new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop) 