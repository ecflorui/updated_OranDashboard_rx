import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Button
from bokeh.layouts import column, row
from bokeh.document import Document

# Generate dummy loss data (100 epochs, starting at epoch 0) --- Needs to be replaced
# Using a decreasing loss curve with some noise
np.random.seed(42)
epochs = np.arange(0, 100)  # Start at epoch 0
# Create a decreasing loss curve: starts high, decreases with noise
base_loss = 2.0 * np.exp(-epochs / 30) + 0.1
noise = np.random.normal(0, 0.05, 100)
loss_values = base_loss + noise
loss_values = np.clip(loss_values, 0, None)  # Ensure no negative values, levels at 0

# Graph styling Stuff (Background Black)
graph_background_color = (37, 37, 37)
graph_grid_color = (67, 67, 67)
tick_color = 'white'
line_color = 'lightgreen'

def loss_epoch_graph(doc: Document):
    try:
        # Create fixed axes: epochs 0-99, loss range based on data
        x_range = (0, 99)
        y_min = 0
        y_max = max(loss_values) * 1.1  # Add 10% padding on top
        y_range = (y_min, y_max)
        
        # Create the figure with fixed axes
        p = figure(
            title="Loss vs Epoch",
            x_axis_label="Epoch",
            y_axis_label="Loss",
            x_range=x_range,
            y_range=y_range,
            width=1200,
            height=500,
            toolbar_location=None,
            tools=[],
            output_backend="canvas"
        )
        
        # Create ColumnDataSource - start empty (epoch 0)
        source = ColumnDataSource(data=dict(x=[], y=[]))
        
        # Add the line plot with visible styling
        p.line(x='x', y='y', source=source, color=line_color, line_width=3, alpha=1.0)
        # Also add circles to make points more visible
        p.circle(x='x', y='y', source=source, color=line_color, size=6, alpha=0.8)
        
        # Apply dark theme styling
        p.background_fill_color = graph_background_color
        p.border_fill_color = graph_background_color
        p.outline_line_color = graph_background_color
        p.title.text_color = tick_color
        p.grid.grid_line_width = 1
        p.grid.grid_line_color = graph_grid_color
        p.xaxis.major_tick_line_color = tick_color
        p.xaxis.minor_tick_line_color = tick_color
        p.xaxis.major_label_text_color = tick_color
        p.yaxis.major_tick_line_color = tick_color
        p.yaxis.major_label_text_color = tick_color
        p.xaxis.axis_label_text_color = tick_color
        p.yaxis.axis_label_text_color = tick_color
        
        # State to track current epoch and pause status
        state = {
            "current_epoch": 0,  # Start at epoch 0
            "is_paused": False,
            "callback_id": None
        }
        
        def update():
            # Only update if not paused
            if not state["is_paused"] and state["current_epoch"] < len(epochs):
                # Get the current epoch index
                epoch_idx = state["current_epoch"]
                
                # Add the new point
                new_x = [epochs[epoch_idx]]
                new_y = [loss_values[epoch_idx]]
                
                # Stream the new data point
                source.stream({'x': new_x, 'y': new_y}, rollover=100)
                
                # Move to next epoch
                state["current_epoch"] += 1
        
        def pause_handler():
            state["is_paused"] = not state["is_paused"]
            if state["is_paused"]:
                pause_button.label = "Resume"
                pause_button.button_type = "success"
            else:
                pause_button.label = "Pause"
                pause_button.button_type = "warning"
        
        def reset_handler():
            # Reset the graph to epoch 0
            source.data = dict(x=[], y=[])
            state["current_epoch"] = 0
            state["is_paused"] = False
            pause_button.label = "Pause"
            pause_button.button_type = "warning"
        
        # Create buttons with better styling
        pause_button = Button(
            label="Pause", 
            button_type="warning", 
            width=120, 
            height=35,
            css_classes=["custom-btn"]
        )
        reset_button = Button(
            label="Reset", 
            button_type="danger", 
            width=120, 
            height=35,
            css_classes=["custom-btn"]
        )
        
        # Set button callbacks
        pause_button.on_click(pause_handler)
        reset_button.on_click(reset_handler)
        
        # Create layout with buttons above the plot (side by side with spacing)
        button_row = row([pause_button, reset_button], sizing_mode="fixed", spacing=10)
        layout = column([button_row, p], sizing_mode="scale_width", spacing=15)
        
        # Add the layout to the document
        doc.add_root(layout)
        
        # Start the periodic callback and store its ID
        callback_id = doc.add_periodic_callback(update, 1000)
        state["callback_id"] = callback_id
        
        print("loss_epoch_graph initialized successfully")
    except Exception as e:
        print(f"Error in loss_epoch_graph: {e}")
        import traceback
        traceback.print_exc()