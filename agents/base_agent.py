"""
Base Agent Class: Abstract base for all pipeline agents.
Provides common functionality and standardizes agent interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from .llm_client import LLMClient, LLMConfig, LLMProvider
from .pipeline_context import PipelineContext
from .schemas import PipelineLogger, TodoTracker


class BaseAgent(ABC):
    """
    Abstract base class for all pipeline agents.

    Provides:
    - Standardized initialization
    - Common error handling
    - LLM client management
    - TODO tracking
    - Logging utilities

    Subclasses must implement the run() method.

    Example:
        class MyAgent(BaseAgent):
            def __init__(self, context, logger, todos):
                super().__init__(
                    context, logger, todos,
                    agent_name="MyAgent",
                    llm_config=LLMConfig(temperature=0.7, max_tokens=4096)
                )

            def run(self, **kwargs) -> Dict:
                # Implementation here
                return {"output_files": [...]}
    """

    def __init__(
        self,
        context: PipelineContext,
        logger: PipelineLogger,
        todos: TodoTracker,
        agent_name: str,
        llm_config: Optional[LLMConfig] = None
    ):
        """
        Initialize base agent.

        Args:
            context: Shared pipeline context
            logger: Pipeline logger
            todos: TODO tracker for manual intervention
            agent_name: Name of the agent (e.g., "BriefBuilder")
            llm_config: Optional LLM configuration (if agent uses LLM)
        """
        self.context = context
        self.logger = logger
        self.todos = todos
        self.agent_name = agent_name

        # Initialize LLM client if config provided
        self.llm = LLMClient(llm_config) if llm_config else None

    @abstractmethod
    def run(self, **kwargs) -> Dict:
        """
        Execute the agent's main logic.

        Args:
            **kwargs: Agent-specific parameters

        Returns:
            Dictionary with agent results. Should include:
            - output_files: List of generated file paths
            - warnings: List of warning messages (optional)
            - metadata: Any additional metadata (optional)

        Example:
            return {
                "output_files": ["/path/to/output.json"],
                "warnings": ["Minor issue in chapter 3"],
                "metadata": {"chapters_processed": 8}
            }
        """
        pass

    def _handle_error(self, error: Exception, task_context: str):
        """
        Standardized error handling.

        Records error in TODO tracker and logs it to console.

        Args:
            error: The exception that occurred
            task_context: Description of what was being done (e.g., "Chapter 03")
        """
        error_msg = f"{self.agent_name} error in {task_context}: {str(error)}"
        self.todos.add(self.agent_name, task_context, error_msg)
        print(f"[{self.agent_name}] ✗ {error_msg}")

    def _safe_generate(
        self,
        prompt: str,
        system_prompt: str = "",
        fallback: str = "",
        task_context: str = ""
    ) -> str:
        """
        Generate text with automatic error handling.

        Wraps LLM generation with try/except and provides fallback value.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            fallback: Value to return if generation fails
            task_context: Description for error tracking

        Returns:
            Generated text or fallback value

        Example:
            text = self._safe_generate(
                prompt="Summarize this chapter",
                system_prompt="You are a technical writer",
                fallback="Summary generation failed",
                task_context="Chapter 03 summary"
            )
        """
        if not self.llm:
            raise RuntimeError(f"{self.agent_name} has no LLM client configured")

        try:
            return self.llm.generate(prompt, system_prompt)
        except Exception as e:
            self._handle_error(e, task_context)
            return fallback

    def _log_info(self, message: str):
        """Log informational message."""
        print(f"[{self.agent_name}] ℹ {message}")

    def _log_success(self, message: str):
        """Log success message."""
        print(f"[{self.agent_name}] ✓ {message}")

    def _log_warning(self, message: str):
        """Log warning message."""
        print(f"[{self.agent_name}] ⚠ {message}")

    def _log_error(self, message: str):
        """Log error message."""
        print(f"[{self.agent_name}] ✗ {message}")

    def _create_result(
        self,
        output_files: List[str],
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Create standardized result dictionary.

        Args:
            output_files: List of generated file paths
            warnings: Optional list of warnings
            metadata: Optional additional metadata

        Returns:
            Standardized result dictionary
        """
        result = {
            "agent": self.agent_name,
            "output_files": output_files
        }

        if warnings:
            result["warnings"] = warnings

        if metadata:
            result["metadata"] = metadata

        return result

    def __repr__(self):
        """String representation."""
        return f"{self.agent_name}(llm={'enabled' if self.llm else 'disabled'})"
