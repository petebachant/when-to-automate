"""A model for computing the value of automating scientific workflows."""

from pydantic import BaseModel


class Artifact(BaseModel):
    name: str


class Task(BaseModel):
    name: str
    iterations: int = 1
    inputs: list[Artifact] = []
    outputs: list[Artifact] = []
    cost_fixed_hr: float = 0.0
    cost_to_automate_hr: float
    cost_to_do_manual_hr: float
    cost_to_do_auto_hr: float
    cost_to_automate_input_transfer_hr: float
    input_transfer_cost_manual_hr: float
    input_transfer_cost_auto_hr: float


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
        "paper",
    ]
}

workflow = Workflow(
    tasks=[
        Task(
            name="Collect raw data",
            inputs=[],
            outputs=[artifacts["raw-data"]],
            cost_fixed_hr=0,
            cost_to_automate_hr=100,
            cost_to_do_manual_hr=20,
            cost_to_do_auto_hr=5,
            iterations=1,
            input_transfer_cost_auto_hr=0,
            input_transfer_cost_manual_hr=0,
            cost_to_automate_input_transfer_hr=0,
        ),
        Task(
            name="Process data",
            inputs=[artifacts["raw-data"]],
            outputs=[
                artifacts["processed-data"],
                artifacts["result1"],
                artifacts["result2"],
                artifacts["result3"],
                artifacts["result4"],
            ],
            cost_to_automate_hr=40,
            cost_to_do_auto_hr=1,
            cost_to_do_manual_hr=5,
            iterations=10,
            cost_to_automate_input_transfer_hr=10,
            input_transfer_cost_auto_hr=0,
            input_transfer_cost_manual_hr=1,
        ),
        Task(
            name="Create figures",
            inputs=[artifacts["raw-data"], artifacts["processed-data"]],
            outputs=[
                artifacts["figure1"],
                artifacts["figure2"],
                artifacts["figure3"],
                artifacts["figure4"],
            ],
            cost_to_automate_hr=20,
            cost_to_do_auto_hr=0,
            cost_to_do_manual_hr=2,
            iterations=5,
            cost_to_automate_input_transfer_hr=5,
            input_transfer_cost_auto_hr=0,
            input_transfer_cost_manual_hr=0.5,
        ),
        Task(
            name="Produce paper PDF",
            inputs=[
                artifacts["result1"],
                artifacts["result2"],
                artifacts["result3"],
                artifacts["result4"],
                artifacts["figure1"],
                artifacts["figure2"],
                artifacts["figure3"],
                artifacts["figure4"],
            ],
            outputs=[artifacts["paper"]],
            cost_to_automate_hr=10,
            cost_to_do_auto_hr=0.01,
            cost_to_do_manual_hr=0.1,
            iterations=10,
            cost_to_automate_input_transfer_hr=20,
            input_transfer_cost_auto_hr=0,
            input_transfer_cost_manual_hr=0.5,
        ),
    ]
)

# A dictionary defining modifications to the workflow step costs and number
# of iterations
scenarios = {}
