import httpx
from typing import Optional
from core.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        # Max characters for transcript (to avoid overwhelming the model)
        self.max_transcript_chars = 50000  # ~12,500 words

    async def generate_summary(
        self,
        transcript: str,
        style: str = "concise"
    ) -> str:
        """
        Generate a summary of the transcript using Ollama.
        """
        # Truncate transcript if too long
        if len(transcript) > self.max_transcript_chars:
            transcript = transcript[:self.max_transcript_chars] + "\n\n[... transcript truncated for summarization ...]"

        prompts = {
            "concise": f"""Summarize the following transcript in 2-3 concise paragraphs. Focus on the main points and key takeaways.

Transcript:
{transcript}

Summary:""",

            "detailed": f"""Provide a detailed summary of the following transcript. Include all important points, context, and conclusions discussed.

Transcript:
{transcript}

Detailed Summary:""",

            "bullet_points": f"""Summarize the following transcript as a list of bullet points. Extract the key points, facts, and conclusions.

Transcript:
{transcript}

Key Points:
-"""
        }

        prompt = prompts.get(style, prompts["concise"])

        try:
            # Use longer timeout for summarization (5 minutes)
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 2048  # Allow longer summaries
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    summary = result.get("response", "")
                    if not summary:
                        raise Exception("Ollama returned empty response")
                    return summary
                else:
                    error_text = response.text[:200] if response.text else "Unknown error"
                    raise Exception(f"Ollama error {response.status_code}: {error_text}")

        except httpx.TimeoutException:
            raise Exception("Ollama request timed out. The model may be loading or the transcript is too long.")
        except httpx.ConnectError:
            raise Exception("Cannot connect to Ollama. Make sure Ollama is running (ollama serve)")
        except Exception as e:
            if "Ollama" in str(e):
                raise
            raise Exception(f"Summarization failed: {str(e)}")

    async def check_health(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    return any(self.model in name for name in model_names)
                return False
        except Exception:
            return False

ollama_service = OllamaService()
