from flask import Flask, render_template
from views.kpi_graph import kpi_graph
from views.rbs_assigned import rbs_assigned
from views.classifier_output import classifier_output
from views.scheduling_policy import scheduling_policy
from views.toggle_switch import toggle_switch
from views.image_pairs import image_pairs_app
from views.rays_animated import animate_rays_cycle4_app
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.embed import server_document
from views.loss_epoch import loss_epoch_graph

# Initialize the Flask application

app = Flask(__name__)


@app.route('/', methods=['GET'])
# def bkapp_page():
#     graphs_script = server_document('http://localhost:5006/graphs')
#     image_pairs_script = server_document('http://localhost:5006/image_pairs')
#     animate_rays_script = server_document('http://localhost:5006/animate_rays')
#     rbs_assigned_script = server_document('http://localhost:5006/rbs_assigned')
#     classifier_output_script = server_document('http://localhost:5006/classifier_output')
#     scheduling_policy_script = server_document('http://localhost:5006/scheduling_policy')
#     toggle_switch_script = server_document('http://localhost:5006/toggle_switch')
#     return render_template("index.html", 
#                            graphs_script=graphs_script,
#                            image_pairs_script=image_pairs_script,
#                            animate_rays_script = animate_rays_script,
#                            rbs_assigned_script = rbs_assigned_script,
#                            classifier_output_script = classifier_output_script,
#                            scheduling_policy_script = scheduling_policy_script,
#                            toggle_switch_script = toggle_switch_script,
#                            )
def bkapp_page():
    graphs_script = server_document('http://localhost:5006/graphs')
    image_pairs_script = server_document('http://localhost:5006/image_pairs')
    animate_rays_script = server_document('http://localhost:5006/animate_rays')
    rbs_assigned_script = server_document('http://localhost:5006/rbs_assigned')
    classifier_output_script = server_document('http://localhost:5006/classifier_output')
    scheduling_policy_script = server_document('http://localhost:5006/scheduling_policy')
    toggle_switch_script = server_document('http://localhost:5006/toggle_switch')
    loss_epoch_script = server_document('http://localhost:5006/loss_epoch')  # Add this line
    return render_template("index.html", 
                           graphs_script=graphs_script,
                           image_pairs_script=image_pairs_script,
                           animate_rays_script = animate_rays_script,
                           rbs_assigned_script = rbs_assigned_script,
                           classifier_output_script = classifier_output_script,
                           scheduling_policy_script = scheduling_policy_script,
                           toggle_switch_script = toggle_switch_script,
                           loss_epoch_script = loss_epoch_script,  # Add this line
                           )

# def bk_worker():
#     bk_apps = {
#         '/graphs': kpi_graph,
#         '/rbs_assigned' : rbs_assigned,
#         '/classifier_output' : classifier_output,
#         '/scheduling_policy': scheduling_policy,
#         '/toggle_switch': toggle_switch,
#         '/image_pairs': image_pairs_app,
#         '/animate_rays': animate_rays_cycle4_app,
#     }
#     server = Server(bk_apps, io_loop=IOLoop(), port=5006, allow_websocket_origin=["localhost:8000", "127.0.0.1:8000"])
#     server.start()
#     server.io_loop.start()

def bk_worker():
    try:
        bk_apps = {
            '/graphs': kpi_graph,
            '/rbs_assigned' : rbs_assigned,
            '/classifier_output' : classifier_output,
            '/scheduling_policy': scheduling_policy,
            '/toggle_switch': toggle_switch,
            '/image_pairs': image_pairs_app,
            '/animate_rays': animate_rays_cycle4_app,
            '/loss_epoch': loss_epoch_graph,
        }
        print(f"Starting Bokeh server with {len(bk_apps)} apps: {list(bk_apps.keys())}")
        server = Server(bk_apps, io_loop=IOLoop(), port=5006, allow_websocket_origin=["localhost:8000", "127.0.0.1:8000"])
        server.start()
        print("Bokeh server started successfully on port 5006")
        server.io_loop.start()
    except Exception as e:
        print(f"Error starting Bokeh server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Running flask app instance on port 8000
    from threading import Thread
    import time
    print("Starting Bokeh server in background thread...")
    Thread(target=bk_worker, daemon=True).start()
    # Give Bokeh server a moment to start
    time.sleep(2)
    print("Starting Flask app on port 8000...")
    app.run(port=8000, debug=False)
