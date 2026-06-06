import os, httpx
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

async def generate_section(template_name: str, data: dict) -> str:
    template = env.get_template(template_name)
    prompt = template.render(**data)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": "mistral", "prompt": prompt, "stream": False}
            )
            return response.json().get("response", "").strip()
    except Exception as e:
        return f"Could not generate content: {str(e)}"