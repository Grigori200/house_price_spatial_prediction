import plotly.offline as plo
import plotly.figure_factory as ff
from functools import partial
import numpy as np


def plot_map(coords):

    minfig = ff.create_hexbin_mapbox(
        data_frame=coords, lat="lat", lon="lng",
        nx_hexagon=15, opacity=0.5, min_count=10,
        color="price", agg_func=partial(np.quantile, q=0.1), color_continuous_scale="Bluered",
        center=dict(lat=51.107883, lon=17.038538), zoom=10
    ).data[0]

    maxfig = ff.create_hexbin_mapbox(
        data_frame=coords, lat="lat", lon="lng",
        nx_hexagon=15, opacity=0.5, min_count=10,
        color="price", agg_func=partial(np.quantile, q=0.9), color_continuous_scale="Bluered",
        center=dict(lat=51.107883, lon=17.038538), zoom=10
    ).data[0]

    fig = ff.create_hexbin_mapbox(
        data_frame=coords, lat="lat", lon="lng",
        nx_hexagon=15, opacity=0.5, min_count=10,
        color="price", agg_func=np.mean, color_continuous_scale="Bluered",
        center=dict(lat=51.107883, lon=17.038538), zoom=10
    )
    fig.add_trace(minfig)
    fig.add_trace(maxfig)

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        updatemenus=[dict(type="buttons", direction="left",
                          buttons=list([
                              dict(args=[{'visible': [False, True, False]}, ],
                                   label="min", method="update"),

                              dict(args=[{'visible': [True, False, False]}, ],
                                   label="median", method="update"),

                              dict(args=[{'visible': [False, False, True]}, ],
                                   label="max", method="update")
                          ])), ]
    )

    plo.plot(fig)