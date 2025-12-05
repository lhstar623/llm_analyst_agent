import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Annotated, Dict, List

import pandas as pd
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from io import StringIO
from contextlib import redirect_stdout

load_dotenv()


model = OpenAIModel(
    "gpt-4.1",
    provider=OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
)

DEFAULT_LEADERBOARD_PATH = "livebench_leaderboard.csv"



@dataclass
class State:
    user_query: str = field(default_factory=str)
    leaderboard_path: str = field(default=DEFAULT_LEADERBOARD_PATH)


def get_leaderboard_overview(
    leaderboard_path: Annotated[str, "Path to the LiveBench leaderboard CSV file"]
) -> str:

    df = pd.read_csv(leaderboard_path)
    cols = df.columns.tolist()
    head_str = df.head(5).to_string(index=False)
    return (
        f"Columns: {cols}\n\n"
        f"Sample rows (top 5):\n{head_str}"
    )


def python_execution_tool(
    code: Annotated[str, "Python code to process the leaderboard and compute composite scores"]
) -> str:

    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            compiled_code = compile(code, "<string>", "exec")
            exec(compiled_code, globals(), globals())

        return f"Python execution output:\n\n{catcher.getvalue()}"
    except Exception as e:
        return f"Failed to run code. Error: {repr(e)}"



class RecommendedModel(BaseModel):
    model_name: str = Field(description="The name of the LLM model")
    rank: int = Field(description="Rank within the recommended list (1 = best)")
    composite_score: float = Field(
        description="Composite score for this task, combining multiple metrics"
    )
    metrics: Dict[str, float] = Field(
        description="Key metrics (e.g., math_score, reasoning_score, etc.) used for ranking"
    )


class ModelSelectorOutput(BaseModel):
    primary_model: RecommendedModel = Field(
        description="The single best model for the user's task"
    )
    top_k: List[RecommendedModel] = Field(
        description="Top-k recommended models with their scores and metrics"
    )
    reasoning: str = Field(
        description="Natural language explanation of why these models were selected"
    )
    weights_used: Dict[str, float] = Field(
        description="Weights or importance assigned to each metric for this selection"
    )



model_selector_agent = Agent(
    model=model,
    tools=[
        Tool(get_leaderboard_overview, takes_ctx=False),
        Tool(python_execution_tool, takes_ctx=False),
    ],
    deps_type=State,
    output_type=ModelSelectorOutput,
    instrument=True,
)



@model_selector_agent.system_prompt
async def get_model_selector_system_prompt(ctx: RunContext[State]):
    """
    LiveBench 리더보드 기반 모델 선택 에이전트용 시스템 프롬프트
    """

    prompt = f"""
You are a model selection expert agent that chooses the most suitable LLM
for a given task, using the LiveBench leaderboard CSV as your primary data source.

### Goal
Given:
- A user task description (often multi-metric, e.g., "math accuracy + reasoning + explanation for high-school students")
- The LiveBench leaderboard CSV

You MUST:
1. Understand the user's task and what capabilities are important
   - Example: for "high school math tutor":
     - Math correctness (accuracy)
     - Step-by-step reasoning quality
     - Explanation clarity for non-experts

2. Map the task to a combination of metrics and categories from the leaderboard.
   - For example:
     - Use math-related benchmarks for correctness
     - Use reasoning-related benchmarks for explanation/justification
   - If needed, you may invent a reasonable composite score formula.

3. Design a composite score:
   - Define weights for each metric (e.g., 0.5 * math + 0.3 * reasoning + 0.2 * explanation)
   - Explain these weights in natural language.

4. Use the tools:
   - `get_leaderboard_overview(leaderboard_path)`:
     - Call this FIRST to inspect the available columns and sample rows.
   - `python_execution_tool(code)`:
     - Use this to read the CSV, compute composite scores, and rank models.
     - ALWAYS start your code with something like:
       `import pandas as pd`
       `df = pd.read_csv("{ctx.deps.leaderboard_path}")`
     - Then compute a new column (e.g., `df["task_score"] = ...`)
     - Sort by that score and print the top models and their metrics.
     - Ensure you print model name, composite score, and the key metrics you used.

5. Select:
   - Choose a single best model (primary_model)
   - Choose top-k models (e.g., top 3~5) as alternatives.

6. Explain:
   - Provide a clear explanation (reasoning) of:
     - Why these models were chosen
     - How the metrics and weights relate to the user's task

### Constraints & Notes
- The CSV is located at: {ctx.deps.leaderboard_path}
- Assume the CSV comes from LiveBench and includes benchmark-based metrics for many models.
- If some metrics you want are not directly present, choose the closest reasonable proxies and explain your choice.
- If cost/latency are not in the CSV, you can still reason qualitatively but do not invent numeric values.

### Output format
You MUST return a JSON object matching the `ModelSelectorOutput` schema:
- `primary_model`
- `top_k`
- `reasoning`
- `weights_used`

User task description:
{ctx.deps.user_query}
"""
    return prompt



def run_model_selector(
    user_query: str,
    leaderboard_path: str = DEFAULT_LEADERBOARD_PATH,
) -> ModelSelectorOutput:
    """
    스트림릿 등에서 바로 쓰기 위한 편의 함수.
    """
    state = State(user_query=user_query, leaderboard_path=leaderboard_path)
    response = model_selector_agent.run_sync(deps=state)
    return response.output
