"""An example Dash-Plotly Application.

Dash is a Python web-application framework built on top of Flask and
Plotly is a Python visualization package. The packages are open source,
but are maintained by a private, for-profit company called
Plotly Technologies Inc., headquartered in Montreal, Canada.
Plotly Inc. provides additional enterprise services (not free), but
their open-source tools should be sufficient for IRS applications.

Dash and Plotly are designed to work together for building web-based
data visualization dashboards.
* [Plotly Graphing Documentation](https://plotly.com/python/)
* [Dash Web Framework](https://dash.plotly.com/)
* [Dash Dashboard Gallery](https://plotly.com/examples)

## Running this Application
This module contains a quick-and-dirty demo Dash application with a
histogram and an interactive table.
1. Download the following files and make sure they are in the same folder:
  * app.py (this file)
  * team-measures.feather
  * requirements.txt
3. Create and activate a new enviornment with conda, venv, or
   virtualenv.
4. Run `pip install -r requirements.txt` to install dash, plotly,
   pandas, jupyterlab, and a couple other packages.
5. Run the app by running `python app.py`. The app will be accessible
   at http://127.0.0.1:8050

## How the Code Works
1. Execution starts at the bottom of the module with the
   `if __name__ == "__main__":` line.
2. The app loads data from the *data/team-measures.feather* file on
   disk.
   * This file contains the IRS's scouting data from the Galileo
     division at the 2023 FIRST World Championships.
   * Feather files are binary files that are optimized for reading and
     storing tabular data. They load much faster than JSON or CSV files.
     See https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#feather
3. The measures data is loaded as a Pandas DataFrame.
4. A measures dataframe is filtered to contain only tasks related to
   placing cubes, and aggregated to contain the total number of cubes
   placed by each team in each match, for each phase (auto to teleop).
5. The module creates a Dash application and a layout that will
   contain one interactive graph and an interactive table.

The code is split into functions. The functions are listed roughly in
the same order in which they'll be run, so read the function docstrings
to get a better understanding of how this code works.

Also, check out [Dash in 20 Minutes](https://dash.plotly.com/tutorial).
"""
import pathlib

import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px


DATA_PATH = pathlib.Path(__file__).parent


def load_team_measures():
    """Read scouting data from a file on disk.
    
    Returns: A Pandas DataFrame, loaded from a feather file.
    """
    return pd.read_feather(DATA_PATH / "team-measures.feather")


def get_cube_measures(measures):
    """Dataframe of total cubes placed by team and match.

    There is nothing new in this function. This is standard Python
    data manipulation.

    Returns:
        A Pandas DataFrme, filtered to only the cube tasks. The
        Dataframe has been aggregated to show the total number of cubes
        placed by a team in each phase of each match.
        Columns: "team", "match", "phase", "hit"
    """
    return (
        measures
        .loc[measures.task.str.startswith("cube"), :]
        .groupby(["team", "match", "phase"], as_index=False)
        .agg({"hit": "sum"})
    )


def get_layout():
    """Creates the layout for the Dash application.
    
    The `app` object was created by the `app = dash.Dash(__name__)`
    statement near the bottom of this module. It is the main Dash
    application object.

    The `html` object is a Dash object that was imported. It has
    classes that represent elements in an HTML page.

    The `dcc` module contains Dash Core Components (DCC).

    Returns:
        A page layout with HTML <div>, <h1>, <h3> elements, as well as
        radio buttons, an interactive table, and a placeholder for
        a Plotly graph.    
    """
    app.layout = html.Div([
        html.H1("Example Plotly App"),
        html.H3("Scouting Data from Galileo Division, 2023"),
        # Add an empty placeholder for a Plotly figure object.
        dcc.Graph(figure={}, id="cube_hist"),
        # Create a set of interactive rado buttons.
        dcc.RadioItems(
            options=["All", "Auto", "Tele"],
            value="All",
            id="phase-control"
        ),
        html.H4("Measures Table"),
        # Add an interactive table.
        _build_measures_table(tmeasures)
    ])
    app.run(debug=True)


@dash.callback(
    dash.Output(component_id="cube_hist", component_property="figure"),
    dash.Input(component_id="phase-control", component_property="value")
)
def update_cube_hist(phase):
    """Connect the radio buttons to the function that creates the graph.

    This function is key to making the graph interactive. The key part
    is the `@dash.callback` decorator that precedes the function. It
    tells dash to do several things:
    1. It tells Dash that this function is a callback function.
    2. This callback function should get the current contents of
       the radio button's `value` property. The radio buttons were
       created in the `get_layout()` function. The callback is linked
       to the radio buttons via the "phase-control" id value.
    3. The output of this callback function should be passed to the
       `figure` property of the `dcc.Graph` object that was also
       defined in `get_layout()`. The callback is linked to the graph
       via the "cube_hist" id value.

    **KEY POINT:** Dash runs all callback functions automatically when
    the application is first loaded. So this function will run even
    before any users click on the radio buttons. This simplifies things,
    because we can use the same code for initializing the page and
    updating the page.    
    """
    return _build_cube_histogram(cube_measures, phase)


def _build_cube_histogram(cube_measures, phase):
    """Histogram of cubes placed by a team during a single match.

    Args:
        cube_measures: A pandas DataFrame
        phase: A string provided by the radio buttons. Either
            "All", "Auto", or "Tele".
    
    This function uses plotly plotting functions to create a histogram
    of cubes placed. Depending on the selected radio button, it
    will show a histogram of all cubes placed, regardless of whether
    they were placed in auto or teleop, or it will just show auto, or
    just teleop.

    Returns:
        A Plotly Figure object containing a histogram.
    """

    # Just filters the dataframe based on the `phase` argument, which
    #   comes from the radio-buttons `value` property.
    # This section does not contain any graphing code.
    if phase.lower() in ["auto", "tele"]:
        cube_measures = (
            cube_measures.loc[cube_measures.phase == phase.lower(), :]
        )
    else:
        cube_measures = (
            cube_measures
            .groupby(["team", "match"], as_index=False)
            .agg({"hit": "sum"})
        )

    # Plot title shows what phase was selected.
    plot_title = f"Histogram of Cubes Placed Per Match: {phase}"
    # Plotly Graphing code starts here.
    # Make a histogram
    cube_hist = px.histogram(
        cube_measures, x="hit",
        title=plot_title,
        labels={"hit": "Cubes Placed by a Team in a Single Match"}
    )
    # Add outlines to each histogram bar, for style! Plot will work without this.
    cube_hist.update_traces(marker_line_width=1,
                            marker_line_color="lightgrey")
    # Capitialize the y-axis title. Plot will work without this line.
    cube_hist.update_layout(yaxis_title="Count")
    return cube_hist


def _build_measures_table(measures):
    """Build an interactive Dash Table object from a dataframe.
    
    Args:
        measures: A Pandas DataFrame

    The table can be sorted and filtered by any column. Very Cool!

    Returns:
        A Dash DataTable object.
    """
    return dash.dash_table.DataTable(
        # Get the data from the dataframe.
        data=measures.to_dict("records"),
        # Have to provide data about each column to make filtering work.
        # Could eliminate this section if we didn't want filtering.
        columns=[
            {"name": col_name, "id": col_name,
             "deletable": True, "selectable": True,
             "type": "numeric" if str(dtype).lower() == "int64" else "any"
             }
            for col_name, dtype in zip(measures.columns, measures.dtypes)
        ],
        page_size=15,
        sort_action="native",
        filter_action="native"
        )


# Here is the high-level code that runs when the module is loaded.
# tmeasures and cube_measures are saved as global variables, so
#   they are available in all functions. They don't have to be
#   passed in as parameters.
tmeasures =  load_team_measures()
cube_measures = get_cube_measures(tmeasures)
app = dash.Dash(__name__)
server = app.server

def main():
    get_layout()
