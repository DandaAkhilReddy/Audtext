import httpx
from typing import Optional
from core.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def generate_summary(
        self,
        transcript: str,
        style: str = "concise"
    ) -> str:
        """
        Generate a summary of the transcript using Ollama.
        """
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

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1024
                    }
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Failed to generate summary")
            else:
                raise Exception(f"Ollama error: {response.status_code}")

    async def check_health(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    return any(self.model in name for name in model_names)
                return False
        except:
            return False

ollama_service = OllamaService()
