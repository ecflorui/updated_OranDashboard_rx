
from get_data  import Database
from bokeh.models import Div
database = Database()




def scheduling_policy(doc):
    data = database.scheduling_policy
    
    
    def update():
        try:
            # Directly modify the text of 'div'
            
            policy = database.map_scheduling_policy(data.get(database.current_timestamp,""))
            # Defensive conversion
            if policy is None:
                display_text = "N/A"
            else:
                display_text = str(policy)

            div.text = display_text

        except Exception as e:
            # Keep UI stable and log the problem
            try:
                div.text = "Error"
            except Exception:
                pass
            print(f"[scheduling_policy.update] error: {e}")
        


    # Initialize 'div' here so that it's in the scope of 'update'
    div = Div(text="")
    

    doc.add_root(div)
    doc.add_periodic_callback(update, 500)  # Update every 250 ms