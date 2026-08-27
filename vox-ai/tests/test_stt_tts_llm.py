"""Unit tests for STT, TTS, and LLM modules."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stt import DeepgramSTTEngine  # noqa: E402
from tts import ElevenLabsTTSEngine  # noqa: E402
from llm import GPT4oVoiceAgent  # noqa: E402


def test_stt_transcribe_chunk():
    """Tests Deepgram STT engine transcription latency & response structure."""
    async def run():
        engine = DeepgramSTTEngine()
        result = await engine.transcribe_stream_chunk(b"Check order ORD-1001")
        assert "text" in result
        assert result["confidence"] > 0
        assert result["latency_ms"] > 0

    asyncio.run(run())


def test_tts_synthesize_stream():
    """Tests ElevenLabs TTS engine streaming audio generation."""
    async def run():
        engine = ElevenLabsTTSEngine()
        chunks = []
        async for chunk in engine.synthesize_stream("Your order has been shipped successfully."):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert "audio_bytes" in chunks[0]
        assert chunks[0]["latency_ms"] > 0

    asyncio.run(run())


def test_llm_function_calling_execution():
    """Tests GPT-4o agent tool calling execution."""
    agent = GPT4oVoiceAgent()
    res = agent.generate_response([{"role": "user", "content": "Check my order ORD-1001"}])
    assert "content" in res
    assert len(res["function_calls"]) > 0
    assert res["function_calls"][0]["tool_name"] == "check_order"
    assert res["latency_ms"] > 0
