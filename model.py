"""A model for computing the value of automating scientific workflows."""

from copy import deepcopy
from typing import Any, Callable

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
    automated: bool = False


class PostIteration(BaseModel):
    task: Task
    do_downstream: bool
    iterations: int = 1


class Workflow(BaseModel):
    tasks: dict[str, Task] = {}
    post_iterations: list[PostIteration] = []

    @property
    def total_time(self) -> float:
        total = 0.0
        for _, task in self.tasks.items():
            total += task.cost_fixed_hr
            if task.automated:
                total += task.cost_to_automate_hr
                total += task.cost_to_do_auto_hr * task.iterations
            else:
                total += task.cost_to_do_manual_hr * task.iterations
        # Handle post-iterations
        for pi in self.post_iterations:
            total += self.calc_post_iteration_time(pi)
        return total

    def calc_post_iteration_time(self, post_iteration: PostIteration) -> float:
        total = 0.0
        task = post_iteration.task
        if task.automated:
            total += task.cost_to_do_auto_hr
        else:
            total += task.cost_to_do_manual_hr
        if post_iteration.do_downstream:
            for downstream_task in self.get_downstream_tasks(task):
                if downstream_task.automated:
                    total += downstream_task.cost_to_do_auto_hr
                else:
                    total += downstream_task.cost_to_do_manual_hr
        total *= post_iteration.iterations
        return total

    def get_downstream_tasks(self, task: Task) -> list[Task]:
        """Get any downstream tasks for a given task.

        A downstream task is one who has an input that is an output of the
        given task or any of the other downstream tasks.
        """
        downstream_tasks = []
        for downstream_task in self.tasks.values():
            if any(
                artifact in downstream_task.inputs for artifact in task.outputs
            ):
                downstream_tasks.append(downstream_task)
                downstream_tasks.extend(
                    self.get_downstream_tasks(downstream_task)
                )
        return downstream_tasks


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
    tasks={
        "collect": Task(
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
        "process": Task(
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
        "plot": Task(
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
        "paper": Task(
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
    }
)


class Scenario(BaseModel):
    """A scenario defines a set of updates to the base workflow that
    describe changing automation status, changing costs, or adding
    sub-iterations or partial runs of the DAG after it's been completed once.
    """

    updates: dict[str, dict[str, Any]]


def update_plot() -> Workflow:
    """In this scenario we need to update a plot later."""
    w = deepcopy(workflow)
    # Add a post-iteration for plotting
    plot_task = w.tasks["plot"]
    w.post_iterations.append(PostIteration(task=plot_task, do_downstream=True))
    return w


# A dictionary defining modifications to the workflow step costs and number
# of iterations
# TODO: How do we define multi-stage feedback loops?
# For example, post-iterations on processing requires downstream stages to
# run
# The callables here return a modified copy of the base workflow
scenarios: dict[str, Callable] = {}
