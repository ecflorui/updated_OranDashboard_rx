import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.document import Document

# Generate dummy loss data (100 epochs)
# Using a decreasing loss curve with some noise
np.random.seed(42)
epochs = np.arange(1, 101)
# Create a decreasing loss curve: starts high, decreases with noise
base_loss = 2.0 * np.exp(-epochs / 30) + 0.1
noise = np.random.normal(0, 0.05, 100)
loss_values = base_loss + noise
loss_values = np.clip(loss_values, 0, None)  # Ensure no negative values

# Graph styling (matching the KPI graphs)
graph_background_color = (37, 37, 37)
graph_grid_color = (67, 67, 67)
tick_color = 'white'
line_color = 'lightgreen'

def loss_epoch_graph(doc: Document):
    try:
        # Create fixed axes: epochs 1-100, loss range based on data
        x_range = (1, 100)
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
        
        # Create ColumnDataSource - start with first 5 data points so graph is clearly visible immediately
        initial_x = epochs[:5].tolist()
        initial_y = loss_values[:5].tolist()
        source = ColumnDataSource(data=dict(x=initial_x, y=initial_y))
        
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
        
        # State to track current epoch (start at 5 since we already have epochs 0-4)
        state = {"current_epoch": 5}
        
        def update():
            # Add one epoch per update (1 second = 1000ms)
            if state["current_epoch"] < len(epochs):
                # Get the next epoch index
                epoch_idx = state["current_epoch"]
                
                # Add the new point
                new_x = [epochs[epoch_idx]]
                new_y = [loss_values[epoch_idx]]
                
                # Stream the new data point
                source.stream({'x': new_x, 'y': new_y}, rollover=100)
                
                # Move to next epoch
                state["current_epoch"] += 1
        
        # Add the plot to the document
        doc.add_root(p)
        
        # Update every 1 second (1000ms) to add one epoch
        doc.add_periodic_callback(update, 1000)
        print("loss_epoch_graph initialized successfully")
    except Exception as e:
        print(f"Error in loss_epoch_graph: {e}")
        import traceback
        traceback.print_exc()