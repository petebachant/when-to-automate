"""A model for computing the value of automating scientific workflows."""

from pydantic import BaseModel


class Artifact(BaseModel):
    name: str


class Task(BaseModel):
    name: str
    inputs: list[Artifact] = []
    outputs: list[Artifact] = []
    cost_fixed_hr: float = 0.0
    cost_to_automate_hr: float
    cost_to_do_manual_hr: float
    cost_to_do_auto_hr: float
    iterations: int = 1


class Workflow(BaseModel):
    tasks: list[Task] = []


artifacts: dict[str, Artifact] = {
    name: Artifact(name=name)
    for name in [
        "raw-data",
        "processed-data",
        "figure1",
        "figure2",
        "figure3",
        "figure4",
        "result1",
        "result2",
        "result3",
        "result4",
    ]
}

workflow = Workflow(
    tasks=[
        Task(
            name="Collect data",
            inputs=[],
            outputs=[artifacts["raw-data"]],
            cost_fixed_hr=0,
            cost_to_automate_hr=100,
            cost_to_do_manual_hr=20,
            cost_to_do_auto_hr=5,
            iterations=1,
        ),
        Task(
            name="Process data",
            inputs=[artifacts["raw-data"]],
            outputs=[artifacts["processed-data"]],
            cost_to_automate_hr=40,
            cost_to_do_auto_hr=1,
            cost_to_do_manual_hr=5,
            iterations=10,
        )
    ]
)

# A dictionary defining modifications to the workflow step costs and number
# of iterations
scenarios = {}
