from bokeh.plotting import figure
from bokeh.embed import components

def power_graph():
    # prepare some data
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 4, 5]

    # create a new plot with a title and axis labels
    p1 = figure(title="Power Graph", x_axis_label='x', y_axis_label='y', toolbar_location=None)

    # add a line renderer with legend and line thickness to the plot
    p1.line(x, y, legend_label="Temp.", line_width=2, color="yellow")

    script7, power_graph = components(p1)

    return{
        "script7":script7,
        "power_graph":power_graph
    }