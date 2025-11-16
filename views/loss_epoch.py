import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Button, Range1d, SingleIntervalTicker
from bokeh.layouts import column, row
from bokeh.document import Document

# Validation BER metric
val_ber_metric = [
    0.0599, 0.0416, 0.0374, 0.0363, 0.0357,
    0.0354, 0.0353, 0.0352, 0.0351, 0.0350,
    0.0351, 0.0350, 0.0351, 0.0352, 0.0350,
    0.0351, 0.0351, 0.0352
]
epochs = np.arange(len(val_ber_metric))

graph_background_color = (37, 37, 37)
graph_grid_color = (67, 67, 67)
tick_color = 'white'

# Colors
line_color = "#7EC8E3"  
first_color = "#8BC34A" 
last_color ="#FF6F61"   

def loss_epoch_graph(doc: Document):
    try:
        x_range = Range1d(start=0, end=5)
        y_range = Range1d(start=0.03, end=0.065)

        p = figure(
            title="Performance on Real-World OAI Data",
            x_axis_label="Epoch",
            y_axis_label="BER on Validation Dataset",
            x_range=x_range,
            y_range=y_range,
            width=550,
            height=335,
            toolbar_location=None,
            tools=[],
            output_backend="canvas"
        )

        p.yaxis.ticker = SingleIntervalTicker(interval=0.005)
        source = ColumnDataSource(data=dict(x=[], y=[]))

        p.line('x', 'y', source=source, color=line_color, line_width=3, legend_label="Validation BER")
        p.circle('x', 'y', source=source, color=line_color, size=6, legend_label="Validation BER")

        # First and last points for legend
        first_dot = p.circle(x=[], y=[], size=10, color=first_color, legend_label="Pre-trained model")
        last_dot = p.circle(x=[], y=[], size=10, color=last_color, legend_label="After fine-tuning")

        p.legend.location = "top_right"
        p.legend.label_text_color = "white"
        p.legend.background_fill_color = "#252525"
        p.legend.border_line_color = "white"


        p.background_fill_color = graph_background_color
        p.border_fill_color = graph_background_color
        p.outline_line_color = graph_background_color
        p.title.text_color = tick_color
        p.grid.grid_line_color = graph_grid_color
        p.xaxis.major_label_text_color = tick_color
        p.yaxis.major_label_text_color = tick_color
        p.xaxis.axis_label_text_color = tick_color
        p.yaxis.axis_label_text_color = tick_color

        state = {"current_epoch": 0, "is_paused": False}

        update_interval_ms = 1000

        def update():
            if state["is_paused"]:
                return
            i = state["current_epoch"]
            if i >= len(epochs):
                return

            new_x = epochs[i]
            new_y = val_ber_metric[i]

            source.stream({"x": [new_x], "y": [new_y]})

            if new_x == 0:
                first_dot.data_source.data = {"x": [new_x], "y": [new_y]}
            if new_x == epochs[-1]:
                last_dot.data_source.data = {"x": [new_x], "y": [new_y]}

            if new_x >= p.x_range.end:
                p.x_range.end = new_x + 1

            state["current_epoch"] += 1

        # PAUSE BUTTON
        def pause_handler():
            state["is_paused"] = not state["is_paused"]
            pause_button.label = "Resume" if state["is_paused"] else "Pause"

        pause_button = Button(label="Pause", button_type="warning", width=120)
        pause_button.on_click(pause_handler)

        # RESET BUTTON
        def reset_handler():
            state["current_epoch"] = 0
            state["is_paused"] = False
            pause_button.label = "Pause"
            source.data = dict(x=[], y=[])
            first_dot.data_source.data = {"x": [], "y": []}
            last_dot.data_source.data = {"x": [], "y": []}
            p.x_range.start = 0
            p.x_range.end = 5

        reset_button = Button(label="Reset", button_type="danger", width=120)
        reset_button.on_click(reset_handler)


        button_layout = column(
            row(pause_button, reset_button, sizing_mode="scale_width"),
            align="center",
            sizing_mode="scale_width"
        )

        layout = column(
            p,
            button_layout,
            sizing_mode="scale_width"
        )

        doc.add_root(layout)
        doc.add_periodic_callback(update, update_interval_ms)

        print("loss_epoch_graph initialized successfully")

    except Exception as e:
        print("Error in loss_epoch_graph:", e)
