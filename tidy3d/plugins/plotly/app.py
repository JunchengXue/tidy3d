"""Makes an app to visualize SimulationData objects."""
from abc import ABC, abstractmethod
from typing import Optional
from typing_extensions import Literal

from jupyter_dash import JupyterDash
from dash import Dash, dcc, html
import pydantic as pd

from .simulation import SimulationPlotly
from .data import DataPlotly
from ...components.base import Tidy3dBaseModel
from ...components.simulation import Simulation
from ...components.data import SimulationData

AppMode = Literal["python", "jupyter", "jupyterlab"]

# app config settings
DEFAULT_MODE = "jupyterlab"
PORT = 8090
DEV_TOOLS_UI = False
DEV_TOOLS_HOT_RELOAD = False


class App(Tidy3dBaseModel, ABC):
    """Basic dash app template: initializes, makes layout, and fires up a server."""

    mode: AppMode = pd.Field(
        DEFAULT_MODE,
        title="App Mode",
        description='Run app in mode that is one of `"python"`, `"jupyter"`, `"jupyterlab"`.',
    )

    def _initialize_app(self) -> Dash:
        """Creates an app based on specs."""
        if "jupyter" in self.mode.lower():
            return JupyterDash(__name__)
        if "python" in self.mode.lower():
            return Dash(__name__)
        raise NotImplementedError(f"App doesn't support mode='{self.mode}'.")

    @abstractmethod
    def _make_layout(self, app: Dash) -> dcc.Tabs:
        """Creates the layout for the app."""
        raise NotImplementedError("Must implement in subclass.")

    def _make_app(self) -> Dash:
        """Initialize everything and make the plotly app."""
        app = self._initialize_app()
        app.layout = self._make_layout(app)
        return app

    def run(self, debug: bool = False) -> None:
        """Starts running the app based on specs."""

        app = self._make_app()

        if self.mode.lower() == "jupyterlab":
            app.run_server(
                mode="jupyterlab",
                port=PORT,
                dev_tools_ui=DEV_TOOLS_UI,
                dev_tools_hot_reload=DEV_TOOLS_HOT_RELOAD,
                threaded=True,
                debug=debug,
            )
        elif self.mode.lower() == "jupyter":
            app.run_server(
                mode="inline",
                port=PORT,
                dev_tools_ui=DEV_TOOLS_UI,
                dev_tools_hot_reload=DEV_TOOLS_HOT_RELOAD,
                threaded=True,
                debug=debug,
            )
        elif self.mode.lower() == "python":
            app.run_server(debug=debug, port=PORT)
        else:
            raise NotImplementedError(f"App doesn't support mode='{self.mode}'.")


class SimulationDataApp(App):
    """App for viewing contents of a :class:`.SimulationData` instance."""

    sim_data: SimulationData = pd.Field(
        ..., title="Simulation data", description="A :class:`.SimulationData` instance to view."
    )

    def _make_layout(self, app: Dash) -> dcc.Tabs:
        """Creates the layout for the app."""

        layout = dcc.Tabs([])

        # simulation
        sim_plotly = SimulationPlotly(simulation=self.sim_data.simulation)
        component = sim_plotly.make_component(app)
        layout.children += [component]

        # monitors
        for monitor_name, monitor_data in self.sim_data.monitor_data.items():
            data_plotly = DataPlotly.from_monitor_data(
                monitor_data=monitor_data, monitor_name=monitor_name
            )
            if data_plotly is None:
                continue
            component = data_plotly.make_component(app)
            layout.children += [component]

        # log
        component = dcc.Tab(
            [
                html.Div([html.H1("Solver Log")]),
                html.Div([html.Code(self.sim_data.log, style={"whiteSpace": "pre-wrap"})]),
            ],
            label="log",
        )
        layout.children += [component]

        return layout

    @classmethod
    def from_file(
        cls, fname: str, mode: AppMode = DEFAULT_MODE, normalize_index: Optional[int] = 0
    ):  # pylint:disable=arguments-differ
        """Load the :class:`.SimulationDataApp` from a tidy3d data file in .hdf5 format."""
        sim_data = SimulationData.from_file(fname, normalize_index=normalize_index)
        return cls(sim_data=sim_data, mode=mode)


class SimulationApp(App):
    """TODO: App for viewing and editing a :class:`.Simulation`."""

    simulation: Simulation = pd.Field(
        ..., title="Simulation", description="A :class:`.Simulation` instance to view."
    )

    def _make_layout(self, app: Dash) -> dcc.Tabs:
        """Creates the layout for the app."""
        return dcc.Tabs([])

    @classmethod
    def from_file(cls, fname: str, mode: AppMode = DEFAULT_MODE):  # pylint:disable=arguments-differ
        """Load the SimulationApp from a tidy3d Simulation file in .json or .yaml format."""
        simulation = Simulation.from_file(fname)
        return cls(simulation=simulation, mode=mode)
