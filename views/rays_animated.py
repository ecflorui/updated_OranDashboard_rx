# views/animate_rays_cycle4.py
import math
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
from bokeh.document import Document

BACKGROUND_URL = "./static/sionna_scene.png"

def load_scene():
    """
    Demo loader: replace with your Sionna loader that returns:
      - transmitters: list of dicts [{"x":..., "y":...}, ...]
      - receivers: list of dicts [{"x":..., "y":...}, ...]
      - ray_paths: list of rays where each ray is a list of (x,y) points (tx -> rx)
    Coordinates here are normalized (0..1).
    """
    # demo transmitters (red) and receivers (green)
    transmitters = [
        {"x": 0.872, "y": 0.85},
    ]
    receivers = [
        {"x": 0.25, "y": 0.6},
        {"x": 0.53, "y": 0.15},
        {"x": 0.9, "y": 0.3},
    ]

    # create rays (some with 0..2 random "bounces")
    ray_paths = []
    for tx in transmitters:
        for rx in receivers:
            pts = [(tx["x"], tx["y"])]
            pts.append((rx["x"], rx["y"]))
            ray_paths.append(pts)

    return transmitters, receivers, ray_paths

# ---------------- geometry helpers -----------------------------------------
def polyline_lengths(points):
    seg_lengths = []
    for i in range(len(points)-1):
        x0, y0 = points[i]; x1, y1 = points[i+1]
        seg_lengths.append(math.hypot(x1-x0, y1-y0))
    total = sum(seg_lengths)
    return seg_lengths, total

def point_along_polyline(points, t):
    if t <= 0:
        return points[0]
    if t >= 1:
        return points[-1]
    seg_lengths, total = polyline_lengths(points)
    target = t * total
    acc = 0.0
    for i, L in enumerate(seg_lengths):
        if acc + L >= target:
            frac = (target - acc) / (L if L != 0 else 1e-9)
            x0, y0 = points[i]; x1, y1 = points[i+1]
            x = x0 + frac * (x1 - x0)
            y = y0 + frac * (y1 - y0)
            return (x, y)
        acc += L
    return points[-1]

def partial_polyline(points, frac):
    if frac <= 0:
        return [points[0][0]], [points[0][1]]
    if frac >= 1:
        xs = [p[0] for p in points]; ys = [p[1] for p in points]
        return xs, ys
    seg_lengths, total = polyline_lengths(points)
    target = frac * total
    acc = 0.0
    out_x = [points[0][0]]
    out_y = [points[0][1]]
    for i, L in enumerate(seg_lengths):
        if acc + L < target - 1e-12:
            out_x.append(points[i+1][0]); out_y.append(points[i+1][1])
        else:
            remain = target - acc
            if L <= 1e-12:
                out_x.append(points[i+1][0]); out_y.append(points[i+1][1])
            else:
                frac_seg = remain / L
                x0, y0 = points[i]; x1, y1 = points[i+1]
                xi = x0 + frac_seg * (x1 - x0)
                yi = y0 + frac_seg * (y1 - y0)
                out_x.append(xi); out_y.append(yi)
            break
        acc += L
    return out_x, out_y

# ---------------- Bokeh app ------------------------------------------------
def animate_rays_cycle4_app(doc: Document):
    txs, rxs, ray_paths = load_scene()
    if not ray_paths:
        return

    # build ray metadata
    rays_meta = []
    for pts in ray_paths:
        seg_lengths, total = polyline_lengths(pts)
        rays_meta.append({"pts": pts, "seg_lengths": seg_lengths, "total_length": total})

    # normalized coordinates 0..1
    p = figure(width=900, height=600, x_range=(0,1), y_range=(0,1), tools="")
    p.axis.visible = False; p.grid.visible = False

    # set the background image
    p.image_url(url=[BACKGROUND_URL], x=0, y=1, w=1, h=1, anchor="top_left")

    # transmitters as red, receivers as green
    tx_source = ColumnDataSource(data=dict(x=[t["x"] for t in txs], y=[t["y"] for t in txs]))
    p.circle('x','y', source=tx_source, size=12, fill_color="red", line_color="black", alpha=0.95)

    rx_source = ColumnDataSource(data=dict(x=[r["x"] for r in rxs], y=[r["y"] for r in rxs]))
    p.square('x','y', source=rx_source, size=10, fill_color="green", line_color="black", alpha=0.95)

    # MultiLine for visible (growing or full) rays
    visible_rays_source = ColumnDataSource(data=dict(xs=[], ys=[], line_width=[]))
    p.multi_line(xs='xs', ys='ys', source=visible_rays_source,
                 line_color="cyan", line_alpha=0.9, line_width='line_width')

    # Particles moving along rays (one particle per active ray)
    particles_source = ColumnDataSource(data=dict(x=[], y=[], size=[], color=[]))
    p.circle('x','y', source=particles_source, size='size', fill_color='color', line_color='black')

    doc.add_root(column(p))

    # Animation configuration
    UPDATE_MS = 50              # 50 ms tick (~20 FPS)
    dt = UPDATE_MS / 1000.0     # seconds per tick
    grow_speed = 0.6            # fraction/sec for ray growth (tune)
    particle_speed = 0.4        # fraction/sec for particle progress (tune)
    cycle_pause = 2.0           # seconds to wait between cycles for each ray

    # activation schedule: we stagger initial activation by small offsets
    activation_schedule = []
    t0_offset = 0.2
    for i in range(len(rays_meta)):
        activation_schedule.append({"ray_index": i, "start_time": i * t0_offset})

    # state for active rays
    # each active entry: { ray_index, grow_frac, particle_frac, phase, transmit_count, next_reactivate_time(opt) }
    active_rays = []
    current_time = 0.0

    def activate_ray(meta_idx):
        active_rays.append({
            "ray_index": meta_idx,
            "grow_frac": 0.0,
            "particle_frac": 0.0,
            "phase": "growing",      # growing -> transmitting -> finished
            "transmit_count": 0
        })

    def schedule_reactivation(meta_idx, at_time):
        activation_schedule.append({"ray_index": meta_idx, "start_time": at_time})

    def update():
        nonlocal current_time
        current_time += dt

        # check and start scheduled activations whose time has arrived
        for sched in activation_schedule[:]:
            if current_time >= sched["start_time"]:
                activate_ray(sched["ray_index"])
                activation_schedule.remove(sched)

        # prepare new arrays for visible rays and particles
        visible_xs = []
        visible_ys = []
        visible_widths = []
        p_x = []
        p_y = []
        p_size = []
        p_color = []

        still_active = []
        for ar in active_rays:
            meta = rays_meta[ar["ray_index"]]
            if ar["phase"] == "growing":
                ar["grow_frac"] += grow_speed * dt
                if ar["grow_frac"] >= 1.0:
                    ar["grow_frac"] = 1.0
                    ar["phase"] = "transmitting"
                    ar["particle_frac"] = 0.0
                # draw partial polyline
                xs_partial, ys_partial = partial_polyline(meta["pts"], ar["grow_frac"])
                visible_xs.append(xs_partial)
                visible_ys.append(ys_partial)
                visible_widths.append(1.0 + 2.0*ar["grow_frac"])
                # no particle yet (or optionally start particle early)
            elif ar["phase"] == "transmitting":
                # Ray is fully visible (we draw full polyline)
                xs_full = [p[0] for p in meta["pts"]]
                ys_full = [p[1] for p in meta["pts"]]
                visible_xs.append(xs_full)
                visible_ys.append(ys_full)
                visible_widths.append(3.0)

                # advance particle
                ar["particle_frac"] += particle_speed * dt
                if ar["particle_frac"] >= 1.0:
                    ar["particle_frac"] = 1.0
                # compute particle position
                px, py = point_along_polyline(meta["pts"], ar["particle_frac"])
                p_x.append(px); p_y.append(py)
                p_size.append(8)
                p_color.append("yellow")

                if ar["particle_frac"] >= 1.0:
                    # one packet completed
                    ar["transmit_count"] += 1
                    if ar["transmit_count"] < 4:
                        # prepare next transmit: reset particle_frac (line stays fully visible)
                        ar["particle_frac"] = 0.0
                    else:
                        # finished 4 transmissions: remove the line and schedule restart
                        ar["phase"] = "finished"
                        # schedule re-activation after pause
                        schedule_reactivation(ar["ray_index"], current_time + cycle_pause)
            # keep only rays that are still active and not 'finished'
            if ar["phase"] in ("growing", "transmitting"):
                still_active.append(ar)
            else:
                # finished - do not append (line removed). If you want to keep final lines visible, append here.
                pass

        # replace sources to trigger rendering
        visible_rays_source.data = {"xs": visible_xs, "ys": visible_ys, "line_width": visible_widths}
        particles_source.data = {"x": p_x, "y": p_y, "size": p_size, "color": p_color}

        # update active_rays list
        active_rays[:] = still_active

    # initial update (nothing active yet)
    update()
    # periodic update
    doc.add_periodic_callback(update, UPDATE_MS)
