
from get_data  import Database
from bokeh.models import Div
database = Database()


def format_class(class_output:str):
    output = class_output.split(" ")[0]
    if output == 'unexpected':
        output = class_output.split(":")[1].split(" ")[1]
    
    return output

def classifier_output(doc):
    data = database.log_data
    
    
    def update():
        try:
            # Directly modify the text of 'div'
            current_time = database.current_timestamp
            # Defensive: if data empty, show placeholder
            if not data:
                class_output = "No data"
            else:
                # if exact key exists, use it; otherwise choose the nearest key
                if current_time in data:
                    class_output = data[current_time]
                else:
                    # choose the nearest timestamp key
                    nearest_key = min(data.keys(), key=lambda k: abs(k - current_time))
                    class_output = data.get(nearest_key, "No data")

            # Ensure it's a string
            class_output = str(class_output)
            div.text = class_output   # or whatever widget you update

        except Exception as e:
            # Keep UI stable and log the problem
            try:
                div.text = "Error"
            except Exception:
                pass
            print(f"[classifier_output.update] error: {e}")


    # Initialize 'div' here so that it's in the scope of 'update'
    div = Div(text="")
    

    doc.add_root(div)
    doc.add_periodic_callback(update, 500)  # Update every 250 ms