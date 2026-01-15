"""
Pipeline Orchestrator: Manages concurrent execution of independent agents.
Maximizes parallelism while respecting dependencies.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

from .pipeline_context import PipelineContext
from .schemas import PipelineLogger, TodoTracker


class AgentStage(Enum):
    """Pipeline stages."""
    CORPUS_ANALYSIS = "corpus_analysis"
    CURRICULUM_DESIGN = "curriculum_design"
    BRIEF_GENERATION = "brief_generation"
    DRAFT_WRITING = "draft_writing"
    EDITING = "editing"
    VALIDATION = "validation"


@dataclass
class AgentTask:
    """Represents a single agent task."""
    agent_name: str
    stage: AgentStage
    dependencies: List[str] = field(default_factory=list)
    function: Optional[Callable] = None
    parallelizable: bool = False
    max_workers: int = 4


@dataclass
class StageResult:
    """Result of a pipeline stage."""
    stage: AgentStage
    agent_name: str
    success: bool
    duration: float
    output: Any = None
    error: Optional[str] = None


class PipelineOrchestrator:
    """
    Orchestrates the multi-agent pipeline with optimized execution.

    Features:
    - Parallel execution of independent agents
    - Dependency management
    - Progress tracking
    - Performance metrics
    - Error handling and recovery
    """

    def __init__(self, context: PipelineContext, logger: PipelineLogger,
                 todos: TodoTracker, max_parallel_agents: int = 4):
        self.context = context
        self.logger = logger
        self.todos = todos
        self.max_parallel_agents = max_parallel_agents

        self.results: List[StageResult] = []
        self.stage_times: Dict[AgentStage, float] = {}

    async def run_stage(self, stage: AgentStage, tasks: List[AgentTask]) -> List[StageResult]:
        """
        Run a pipeline stage with optimal parallelization.

        Args:
            stage: The pipeline stage
            tasks: List of agent tasks for this stage

        Returns:
            List of stage results
        """
        print(f"\n{'='*60}")
        print(f"STAGE: {stage.value.upper()}")
        print(f"{'='*60}")

        start_time = time.time()
        stage_results = []

        # Check if tasks can run in parallel
        parallelizable_tasks = [t for t in tasks if t.parallelizable]
        sequential_tasks = [t for t in tasks if not t.parallelizable]

        # Run parallel tasks
        if parallelizable_tasks:
            print(f"Running {len(parallelizable_tasks)} tasks in parallel...")
            parallel_results = await self._run_parallel_tasks(parallelizable_tasks)
            stage_results.extend(parallel_results)

        # Run sequential tasks
        for task in sequential_tasks:
            print(f"Running {task.agent_name} (sequential)...")
            result = await self._run_single_task(task)
            stage_results.append(result)

        duration = time.time() - start_time
        self.stage_times[stage] = duration

        print(f"\nStage completed in {duration:.2f}s")

        return stage_results

    async def _run_parallel_tasks(self, tasks: List[AgentTask]) -> List[StageResult]:
        """Run multiple tasks concurrently."""
        async_tasks = [self._run_single_task(task) for task in tasks]
        return await asyncio.gather(*async_tasks, return_exceptions=True)

    async def _run_single_task(self, task: AgentTask) -> StageResult:
        """Run a single agent task."""
        start_time = time.time()
        st_dt = datetime.now()

        try:
            # Log start
            st_dt = self.logger.log_start(task.agent_name)

            # Execute agent function
            if asyncio.iscoroutinefunction(task.function):
                output = await task.function(self.context)
            else:
                # Run sync function in executor
                output = await asyncio.to_thread(task.function, self.context)

            duration = time.time() - start_time

            # Log end
            self.logger.log_end(task.agent_name, st_dt, [], [], [])

            result = StageResult(
                stage=task.stage,
                agent_name=task.agent_name,
                success=True,
                duration=duration,
                output=output
            )

            self.results.append(result)
            print(f"  ✓ {task.agent_name} completed ({duration:.2f}s)")

            return result

        except Exception as e:
            duration = time.time() - start_time

            error_msg = f"Error in {task.agent_name}: {str(e)}"
            self.logger.log_end(task.agent_name, st_dt, [], [error_msg], [error_msg])

            result = StageResult(
                stage=task.stage,
                agent_name=task.agent_name,
                success=False,
                duration=duration,
                error=error_msg
            )

            self.results.append(result)
            print(f"  ✗ {task.agent_name} failed: {error_msg}")

            return result

    async def run_validation_stage_parallel(self, validation_agents: List[Callable]) -> List[StageResult]:
        """
        Run validation agents (G, H, I) in parallel.

        These agents are independent and can run concurrently.
        """
        tasks = [
            AgentTask(
                agent_name=agent.__name__,
                stage=AgentStage.VALIDATION,
                function=agent,
                parallelizable=True
            )
            for agent in validation_agents
        ]

        return await self.run_stage(AgentStage.VALIDATION, tasks)

    def generate_performance_report(self) -> str:
        """Generate a detailed performance report."""
        report = "# Pipeline Performance Report\n\n"

        total_time = sum(self.stage_times.values())
        report += f"**Total Pipeline Time:** {total_time:.2f}s\n\n"

        report += "## Stage Breakdown\n\n"
        report += "| Stage | Duration | % of Total |\n"
        report += "|-------|----------|------------|\n"

        for stage, duration in sorted(self.stage_times.items(), key=lambda x: x[1], reverse=True):
            pct = (duration / total_time * 100) if total_time > 0 else 0
            report += f"| {stage.value} | {duration:.2f}s | {pct:.1f}% |\n"

        report += "\n## Agent Results\n\n"

        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful

        report += f"- **Successful:** {successful}/{len(self.results)}\n"
        report += f"- **Failed:** {failed}/{len(self.results)}\n\n"

        if failed > 0:
            report += "### Failed Agents\n\n"
            for result in self.results:
                if not result.success:
                    report += f"- **{result.agent_name}**: {result.error}\n"

        report += "\n## Performance Metrics\n\n"

        # Calculate speedup from parallelization
        sequential_time = sum(r.duration for r in self.results)
        speedup = sequential_time / total_time if total_time > 0 else 1.0

        report += f"- **Sequential execution time estimate:** {sequential_time:.2f}s\n"
        report += f"- **Actual parallel execution time:** {total_time:.2f}s\n"
        report += f"- **Speedup factor:** {speedup:.2f}x\n"
        report += f"- **Time saved:** {sequential_time - total_time:.2f}s ({((sequential_time - total_time) / sequential_time * 100) if sequential_time > 0 else 0:.1f}%)\n"

        return report

    def save_performance_metrics(self, output_path: str):
        """Save performance metrics as JSON."""
        metrics = {
            "total_time": sum(self.stage_times.values()),
            "stage_times": {stage.value: duration for stage, duration in self.stage_times.items()},
            "results": [
                {
                    "stage": r.stage.value,
                    "agent_name": r.agent_name,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error
                }
                for r in self.results
            ],
            "summary": {
                "total_agents": len(self.results),
                "successful": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "speedup": sum(r.duration for r in self.results) / sum(self.stage_times.values()) if sum(self.stage_times.values()) > 0 else 1.0
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        print(f"[Orchestrator] Performance metrics saved to {output_path}")


async def run_optimized_pipeline(
    context: PipelineContext,
    logger: PipelineLogger,
    todos: TodoTracker,
    agents: Dict[str, Callable]
) -> PipelineOrchestrator:
    """
    Run the complete pipeline with optimized parallelization.

    Args:
        context: Shared pipeline context
        logger: Pipeline logger
        todos: TODO tracker
        agents: Dictionary mapping agent names to callable functions

    Returns:
        Orchestrator with results and metrics
    """
    orchestrator = PipelineOrchestrator(context, logger, todos)

    # Stage 1: Corpus Analysis (sequential, depends on raw files)
    if "corpus_librarian" in agents:
        await orchestrator.run_stage(
            AgentStage.CORPUS_ANALYSIS,
            [AgentTask("CorpusLibrarian", AgentStage.CORPUS_ANALYSIS,
                      function=agents["corpus_librarian"])]
        )

    # Stage 2: Curriculum Design (sequential, depends on corpus)
    if "curriculum_architect" in agents:
        await orchestrator.run_stage(
            AgentStage.CURRICULUM_DESIGN,
            [AgentTask("CurriculumArchitect", AgentStage.CURRICULUM_DESIGN,
                      function=agents["curriculum_architect"])]
        )

    # Stage 3: Brief Generation (parallel per chapter)
    if "brief_builder" in agents:
        await orchestrator.run_stage(
            AgentStage.BRIEF_GENERATION,
            [AgentTask("BriefBuilder", AgentStage.BRIEF_GENERATION,
                      function=agents["brief_builder"], parallelizable=True)]
        )

    # Stage 4: Draft Writing (parallel per chapter, with rate limiting)
    if "draft_writer" in agents:
        await orchestrator.run_stage(
            AgentStage.DRAFT_WRITING,
            [AgentTask("DraftWriter", AgentStage.DRAFT_WRITING,
                      function=agents["draft_writer"], parallelizable=True)]
        )

    # Stage 5: Editing (parallel per chapter)
    if "dev_editor" in agents:
        await orchestrator.run_stage(
            AgentStage.EDITING,
            [AgentTask("DevelopmentalEditor", AgentStage.EDITING,
                      function=agents["dev_editor"], parallelizable=True)]
        )

    # Stage 6: Validation (all three can run in parallel!)
    validation_agents = []
    if "terminology" in agents:
        validation_agents.append(
            AgentTask("TerminologyKeeper", AgentStage.VALIDATION,
                     function=agents["terminology"], parallelizable=True)
        )
    if "proofreader" in agents:
        validation_agents.append(
            AgentTask("Proofreader", AgentStage.VALIDATION,
                     function=agents["proofreader"], parallelizable=True)
        )
    if "safety" in agents:
        validation_agents.append(
            AgentTask("SafetyReviewer", AgentStage.VALIDATION,
                     function=agents["safety"], parallelizable=True)
        )

    if validation_agents:
        await orchestrator.run_stage(AgentStage.VALIDATION, validation_agents)

    # Generate report
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(orchestrator.generate_performance_report())

    return orchestrator
