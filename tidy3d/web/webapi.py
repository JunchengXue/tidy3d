"""Provides lowest level, user-facing interface to server."""

import os
import sys
import time
from shutil import copyfile
import json

import numpy as np
import requests

from .config import DEFAULT_CONFIG as Config
from .httpuils import post, put, get, delete
from .s3utils import get_s3_client
from .task import TaskId, Task, TaskInfo, RunInfo, TaskStatus

from ..components.simulation import Simulation
from ..components.data import SimulationData
from ..log import log

""" webapi functions """


def _upload(
    simulation: Simulation,
    task_name: str,
    folder_name: str = "default",
    solver_version: str = Config.solver_version,
    worker_group: str = Config.worker_group,
) -> TaskId:
    """upload with all kwargs exposed"""

    method = os.path.join("fdtd/model", folder_name, "task")
    data = {
        "status": "draft",
        "solverVersion": solver_version,
        "taskName": task_name,
        "nodeSize": 10,  # need to do these
        "timeSteps": 10,  # need to do these
        "computeWeight": 0.5,  # need to compute thse from simulation
        "workerGroup": worker_group,
    }

    try:
        task = post(method=method, data=data)

    except requests.exceptions.HTTPError as e:
        error_json = json.loads(e.response.text)
        log.error(error_json["error"])

    task_id = task["iaskId"]

    # upload the file to s3
    log.info("Uploading the json file...")

    json_string = simulation.json(indent=4)

    key = os.path.join("users", Config.user["UserId"], task_id, "simulation.json")

    # CONVERSION HERE

    client = get_s3_client()
    client.put_object(
        Body=json_string,
        Bucket=Config.studio_bucket,
        Key=key,
    )

    return task_id


def _upload(simulation: Simulation, task_name: str, folder_name: str = "default") -> TaskId:
    """upload simulation to server (as draft, dont run).

    Parameters
    ----------
    simulation : :class:`Simulation`
        Simulation to upload to server.
    task_name : ``str``
        name of task


    Returns
    -------
    TaskId
        Unique identifier of task on server.
    """
    return _upload(simulation=simulation, task_name=task_name, folder_name=folder_name)


def get_info(task_id: TaskId) -> TaskInfo:
    """Return information about a task.

    Parameters
    ----------
    task_id : TaskId
        Unique identifier of task on server.

    Returns
    -------
    TaskInfo
        Object containing information about status, size, credits of task.
    """
    method = os.path.join('fdtd/task', task_id)
    return get(method)


def get_run_info(task_id: TaskId) -> RunInfo:
    """get information about running status of task

    Parameters
    ----------
    task_id : TaskId
        Description

    Returns
    -------
    RunInfo
        Description
    """
    # task = get_task_by_id(task_id)
    # call server
    # return make_fake_run_info(task_id)


def run(task_id: TaskId) -> None:
    """Start running the simulation associated with task.

    Parameters
    ----------
    task_id : TaskId
        Unique identifier of task on server.
    """
    task = get_info(task_id)
    folder_name = task['folder_name']
    method = os.path.join('fdtd/model', folder_name, 'task', task_id)
    put(method, data=task)



MONITOR_MESSAGE = {
    TaskStatus.INIT: "task hasnt been run, start with `web.run(task)`",
    TaskStatus.SUCCESS: "task finished succesfully, download with `web.download(task, path)`",
    TaskStatus.ERROR: "task errored",
}


def _print_status(task_id: TaskId) -> None:
    status = get_info(task_id).status
    print(f'status = "{status.value}"')


def monitor(task_id: TaskId) -> None:
    """Print the real time task progress until completion.

    Parameters
    ----------
    task_id : TaskId
        Unique identifier of task on server.
    """

    # emulate running the task
    task = get_task_by_id(task_id)
    task.info.status = TaskStatus.RUN

    while True:

        status = get_info(task_id).status

        _print_status(task_id)
        if status in (TaskStatus.SUCCESS, TaskStatus.ERROR):
            print("-> returning")
            return

        task.info.status = TaskStatus.QUEUE
        _print_status(task_id)
        task.info.status = TaskStatus.PRE
        _print_status(task_id)

        task.info.status = TaskStatus.RUN
        num_steps = 4
        for step_num in range(num_steps):
            run_info = RunInfo(
                perc_done=(step_num + 1) / num_steps,
                field_decay=np.exp(-step_num / num_steps),
            )
            _print_status(task_id)
            run_info.display()
            time.sleep(0.1 / num_steps)

        task.info.status = TaskStatus.POST
        _print_status(task_id)

        # emulate completing the task
        task.info.status = TaskStatus.SUCCESS


def download(task_id: TaskId, path: str) -> None:
    """Fownload results of task to file.

    Parameters
    ----------
    task_id : TaskId
        Unique identifier of task on server.
    path : str
        Download path to .hdf5 data file (including filename).
    """

    # load the file into SimulationData
    data_path_server = _get_data_path_server(task_id)
    copyfile(data_path_server, path)


def load_results(task_id: TaskId, path: str) -> SimulationData:
    """Download and Load simultion results into ``SimulationData`` object.

    Parameters
    ----------
    task_id : TaskId
        Unique identifier of task on server.
    path : str
        Download path to .hdf5 data file (including filename).

    Returns
    -------
    SimulationData
        Object containing simulation data.
    """
    download(task_id=task_id, path=path)
    return SimulationData.load(path)


def _rm(path: str):
    if os.path.exists(path) and not os.path.isdir(path):
        os.remove(path)


def delete(task_id: TaskId) -> None:
    """Delete server-side data associated with task.

    Parameters
    ----------
    task_id : TaskId
        Unique identifier of task on server.
    """

    # remove from server directories
    sim_path = _get_sim_path(task_id)
    data_path = _get_data_path_server(task_id)
    _rm(sim_path)
    _rm(data_path)

    # remove task from emulated server queue if still there
    if task_id in TASKS:
        TASKS.pop(task_id)
