"""
Unified LLM Client supporting multiple providers (Gemini, OpenRouter).
Provides automatic fallback, rate limiting, and async support.
"""

import os
import time
import asyncio
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class LLMProvider(Enum):
    """Available LLM providers."""
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    AUTO = "auto"


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    provider: LLMProvider
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    model_name: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 8192
    top_p: float = 0.95
    rate_limit_delay: float = 1.0  # seconds between requests
    max_retries: int = 3
    retry_delay: float = 15.0  # initial retry delay


class RateLimiter:
    """Simple rate limiter to prevent API throttling."""

    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self.last_request_time = 0

    async def acquire(self):
        """Wait if necessary to respect rate limit."""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    def acquire_sync(self):
        """Synchronous version of acquire."""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            time.sleep(wait_time)

        self.last_request_time = time.time()


class LLMClient:
    """
    Unified LLM client with multi-provider support and automatic fallback.

    Supports:
    - Google Gemini (via google-generativeai)
    - OpenRouter (unified API for Claude, GPT-4, Gemini, Llama, etc.)
    - Automatic fallback between providers
    - Rate limiting
    - Retry logic with exponential backoff
    - Both sync and async interfaces
    
    Usage:
        async with LLMClient() as client:
            response = await client.generate_async("Hello")
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = self._load_config_from_env()

        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_delay)

        # Initialize providers
        self.gemini_model = None
        self.openrouter_client = None

        if config.provider in [LLMProvider.GEMINI, LLMProvider.AUTO]:
            self._setup_gemini()

        if config.provider in [LLMProvider.OPENROUTER, LLMProvider.AUTO]:
            self._setup_openrouter()

        # Determine active provider
        self.active_provider = self._determine_active_provider()

        print(f"[LLMClient] Initialized with provider: {self.active_provider.value}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        """Close asynchronous resources."""
        if self.openrouter_client:
            await self.openrouter_client.aclose()
            print("[LLMClient] OpenRouter client closed")

    def _load_config_from_env(self) -> LLMConfig:
        """Load configuration from environment variables."""
        provider_str = os.environ.get("LLM_PROVIDER", "auto").lower()
        provider = LLMProvider(provider_str)

        return LLMConfig(
            provider=provider,
            gemini_api_key=os.environ.get("GEMINI_API_KEY"),
            openrouter_api_key=os.environ.get("OPENROUTER_API_KEY"),
            model_name=os.environ.get("LLM_MODEL"),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "8192")),
            rate_limit_delay=float(os.environ.get("LLM_RATE_LIMIT", "1.0"))
        )

    def _setup_gemini(self):
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            print("[LLMClient] google-generativeai not installed")
            return

        if not self.config.gemini_api_key:
            print("[LLMClient] GEMINI_API_KEY not set")
            return

        try:
            genai.configure(api_key=self.config.gemini_api_key)

            model_name = self.config.model_name or "gemini-2.0-flash-exp"

            generation_config = {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "max_output_tokens": self.config.max_tokens,
            }

            self.gemini_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )

            print(f"[LLMClient] Gemini initialized: {model_name}")
        except Exception as e:
            print(f"[LLMClient] Failed to initialize Gemini: {e}")

    def _setup_openrouter(self):
        """Initialize OpenRouter client."""
        if not HTTPX_AVAILABLE:
            print("[LLMClient] httpx not installed (pip install httpx)")
            return

        if not self.config.openrouter_api_key:
            print("[LLMClient] OPENROUTER_API_KEY not set")
            return

        try:
            self.openrouter_client = httpx.AsyncClient(
                base_url="https://openrouter.ai/api/v1",
                headers={
                    "Authorization": f"Bearer {self.config.openrouter_api_key}",
                    "HTTP-Referer": "https://github.com/viruses-ebook",
                    "X-Title": "Hebrew Virology Ebook Generator"
                },
                timeout=120.0
            )

            print("[LLMClient] OpenRouter initialized")
        except Exception as e:
            print(f"[LLMClient] Failed to initialize OpenRouter: {e}")

    def _determine_active_provider(self) -> LLMProvider:
        """Determine which provider to use."""
        if self.config.provider == LLMProvider.GEMINI:
            if self.gemini_model:
                return LLMProvider.GEMINI
            raise RuntimeError("Gemini requested but not available")

        if self.config.provider == LLMProvider.OPENROUTER:
            if self.openrouter_client:
                return LLMProvider.OPENROUTER
            raise RuntimeError("OpenRouter requested but not available")

        # AUTO mode: prefer Gemini, fallback to OpenRouter
        if self.gemini_model:
            return LLMProvider.GEMINI
        elif self.openrouter_client:
            return LLMProvider.OPENROUTER
        else:
            raise RuntimeError("No LLM provider available")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text synchronously.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text
        """
        self.rate_limiter.acquire_sync()

        for attempt in range(self.config.max_retries):
            try:
                if self.active_provider == LLMProvider.GEMINI:
                    return self._generate_gemini(prompt, system_prompt)
                else:
                    # OpenRouter requires async, so use sync wrapper
                    return asyncio.run(self._generate_openrouter(prompt, system_prompt))

            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    print(f"[LLMClient] Attempt {attempt + 1} failed: {e}")
                    print(f"[LLMClient] Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise

    async def generate_async(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text asynchronously.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text
        """
        await self.rate_limiter.acquire()

        for attempt in range(self.config.max_retries):
            try:
                if self.active_provider == LLMProvider.GEMINI:
                    # Gemini is sync, run in executor
                    return await asyncio.to_thread(
                        self._generate_gemini, prompt, system_prompt
                    )
                else:
                    return await self._generate_openrouter(prompt, system_prompt)

            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    print(f"[LLMClient] Attempt {attempt + 1} failed: {e}")
                    print(f"[LLMClient] Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise

    def _generate_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Gemini."""
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        response = self.gemini_model.generate_content(full_prompt)
        return response.text

    async def _generate_openrouter(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using OpenRouter."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Default to Claude 3.5 Sonnet on OpenRouter
        model = self.config.model_name or "anthropic/claude-3.5-sonnet"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p
        }

        response = await self.openrouter_client.post(
            "/chat/completions",
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    async def generate_batch_async(self, prompts: List[str],
                                   system_prompt: Optional[str] = None) -> List[str]:
        """
        Generate multiple completions concurrently.

        Args:
            prompts: List of prompts to process
            system_prompt: Optional system prompt for all

        Returns:
            List of generated texts
        """
        tasks = [
            self.generate_async(prompt, system_prompt)
            for prompt in prompts
        ]

        return await asyncio.gather(*tasks)


# Convenience function for simple usage
def get_llm_client() -> LLMClient:
    """
    Get a configured LLM client from environment.
    Note: It is recommended to use LLMClient as a context manager:
    async with LLMClient() as client:
        ...
    """
    return LLMClient()