
from bokeh.models import Switch, Div
from bokeh.layouts import row


def toggle_switch(doc):
    
    
    def update():
        # Directly modify the text of 'div'
        if switch.active:
            div.text = "On"
        else:
            div.text = "Off"

    # Initialize 'div' here so that it's in the scope of 'update'
    switch = Switch()
    
    div = Div(text="Off")

    doc.add_root(row(switch,div))
    doc.add_periodic_callback(update, 500)  # Update every 250 ms
        