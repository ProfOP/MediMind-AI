import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from config import OLLAMA_BASE_URL, OLLAMA_MODEL


class OllamaError(RuntimeError):
    """A local Ollama service or model error suitable for display in the UI."""


def generate_response(
    prompt: str,
    model: str = OLLAMA_MODEL,
    base_url: str = OLLAMA_BASE_URL,
) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise OllamaError("Only a localhost Ollama service is allowed; remote model APIs are disabled.")
    endpoint = base_url.rstrip("/") + "/api/chat"
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 300},
        }
    ).encode("utf-8")
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise OllamaError(f"Ollama could not find model '{model}'. Pull it into the project-local model store first.") from exc
        raise OllamaError(f"Ollama returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise OllamaError(
            "Ollama is not reachable at 127.0.0.1:11434. Start the local Ollama service, or enable labelled demo mode."
        ) from exc
    except TimeoutError as exc:
        raise OllamaError("The local Ollama request timed out. Try again or enable labelled demo mode.") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OllamaError("Ollama returned a malformed response.") from exc

    message = body.get("message", {})
    answer = message.get("content") if isinstance(message, dict) else None
    if not isinstance(answer, str) or not answer.strip():
        raise OllamaError("Ollama returned an empty or malformed response.")
    return answer.strip()