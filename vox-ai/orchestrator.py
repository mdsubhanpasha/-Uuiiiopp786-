"""VOX-AI Voice Pipeline Orchestrator.

Orchestrates STT, LLM function calling, Sentiment detection, TTS audio streaming,
interrupt handling, and end-to-end latency benchmark measurement.
"""

from typing import Any, AsyncGenerator, Dict, Optional

from database import DEFAULT_DB_PATH
from llm import GPT4oVoiceAgent
from memory import ConversationMemory
from sentiment import analyze_sentiment
from stt import DeepgramSTTEngine
from tts import ElevenLabsTTSEngine


class VoicePipelineOrchestrator:
    """Enterprise Real-Time Voice Pipeline Agent."""

    def __init__(
        self,
        session_id: str = "default_session",
        db_path: str = DEFAULT_DB_PATH,
        redis_url: Optional[str] = None
    ) -> None:
        """Initializes voice pipeline components.

        Args:
            session_id: Session identifier string.
            db_path: Path to SQLite DB.
            redis_url: Optional Redis URL.
        """
        self.session_id = session_id
        self.db_path = db_path
        self.memory = ConversationMemory(session_id=session_id, redis_url=redis_url)

        self.stt_engine = DeepgramSTTEngine()
        self.llm_agent = GPT4oVoiceAgent(db_path=db_path)
        self.tts_engine = ElevenLabsTTSEngine()

        # Orchestration state variables
        self.is_interrupted = False
        self.is_speaking = False
        self.is_escalated = False
        self.current_sentiment_score = 0.0

    def trigger_interrupt(self) -> Dict[str, Any]:
        """Triggers user mid-speech interrupt signal.

        Clears current TTS speech synthesis stream and resets pipeline state.

        Returns:
            Dict[str, Any]: Interrupted event status.
        """
        self.is_interrupted = True
        self.is_speaking = False
        return {
            "status": "interrupted",
            "session_id": self.session_id,
            "message": "AI speech playback interrupted by user input."
        }

    def reset_interrupt(self) -> None:
        """Resets interrupt status flag for next turn."""
        self.is_interrupted = False

    async def process_user_audio_chunk(
        self,
        audio_chunk: bytes
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Processes user audio chunk through STT -> Sentiment -> LLM -> TTS pipeline.

        Args:
            audio_chunk: Raw audio PCM/WAV chunk from WebRTC or WebSocket.

        Yields:
            Dict[str, Any]: Pipeline events including STT result, LLM text, function calls,
                            latency benchmarks, and audio stream chunks.
        """
        self.reset_interrupt()

        # 1. STT Stage (Deepgram Nova-2 Streaming)
        stt_result = await self.stt_engine.transcribe_stream_chunk(audio_chunk)
        user_text = stt_result.get("text", "").strip()
        stt_latency = stt_result.get("latency_ms", 200.0)

        yield {
            "event": "stt_complete",
            "transcript": user_text,
            "stt_latency_ms": stt_latency,
            "session_id": self.session_id
        }

        if not user_text:
            return

        # 2. Sentiment Analysis Stage
        sentiment = analyze_sentiment(user_text)
        self.current_sentiment_score = sentiment["score"]
        self.memory.add_sentiment_score(sentiment["score"])

        if sentiment["should_escalate"] and not self.is_escalated:
            self.is_escalated = True

        yield {
            "event": "sentiment_analysis",
            "sentiment": sentiment,
            "is_escalated": self.is_escalated,
            "session_id": self.session_id
        }

        # Save user message into conversation memory
        self.memory.add_message("user", user_text)

        # Check for interrupt mid-pipeline
        if self.is_interrupted:
            yield {"event": "pipeline_interrupted", "stage": "post_stt"}
            return

        # 3. LLM Stage (GPT-4o with Function Calling & Empathetic Tone)
        history = self.memory.get_history()
        llm_result = self.llm_agent.generate_response(
            messages=history,
            is_empathetic=self.is_escalated
        )

        ai_text = llm_result.get("content", "")
        function_calls = llm_result.get("function_calls", [])
        llm_latency = llm_result.get("latency_ms", 400.0)

        # Save assistant response to memory
        self.memory.add_message("assistant", ai_text)

        yield {
            "event": "llm_complete",
            "response_text": ai_text,
            "function_calls": function_calls,
            "llm_latency_ms": llm_latency,
            "session_id": self.session_id
        }

        if self.is_interrupted:
            yield {"event": "pipeline_interrupted", "stage": "post_llm"}
            return

        # 4. TTS Stage (ElevenLabs Streaming synthesis <300ms)
        self.is_speaking = True
        first_chunk_latency = 0.0
        chunk_count = 0

        async for tts_chunk in self.tts_engine.synthesize_stream(ai_text):
            if self.is_interrupted:
                self.is_speaking = False
                yield {
                    "event": "speech_interrupted",
                    "chunk_index": chunk_count,
                    "session_id": self.session_id
                }
                break

            if chunk_count == 0:
                first_chunk_latency = tts_chunk.get("latency_ms", 300.0)

            chunk_count += 1
            yield {
                "event": "audio_chunk",
                "chunk_index": tts_chunk["chunk_index"],
                "audio_bytes": tts_chunk["audio_bytes"],
                "tts_latency_ms": tts_chunk["latency_ms"],
                "session_id": self.session_id
            }

        self.is_speaking = False

        # 5. Calculate Total End-To-End Latency Benchmark
        total_end_to_end_latency = round(stt_latency + llm_latency + first_chunk_latency, 2)

        yield {
            "event": "turn_complete",
            "session_id": self.session_id,
            "latency_breakdown": {
                "stt_ms": stt_latency,
                "llm_ms": llm_latency,
                "tts_first_chunk_ms": first_chunk_latency,
                "total_end_to_end_ms": total_end_to_end_latency,
                "within_target": total_end_to_end_latency < 1200.0
            }
        }
