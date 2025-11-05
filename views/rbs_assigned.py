
from get_data  import Database
from bokeh.models import Slider,CustomJS
import random
database = Database()

def rbs_assigned(doc):
    data = database.rbs_assigned
    
    
    def update():
        # Directly modify the text of 'div'
        slider.value = data.get(database.current_timestamp,0)

    # Initialize 'div' here so that it's in the scope of 'update'
    slider = Slider(start=0,end=50,value=10,bar_color='blue', disabled=True,title="Rb's assigned")
    

    doc.add_root(slider)
    doc.add_periodic_callback(update, 500)  # Update every 250 ms
        