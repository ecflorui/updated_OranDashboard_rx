# views/image_pairs.py
import os
from glob import glob
import numpy as np

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.layouts import row
from bokeh.document import Document

# Directory where your numpy files live. Adapt as needed.
NP_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data", "pairs")

def load_pair_from_file(path):
    """
    Load a file and return one pair in the normalized format:
      ((left_x_list, left_y_list), (right_x_list, right_y_list))

    Supported:
      - .npz file with 'ratio_batch' and 'demapper_batch' (this matches your saved files).
        Both arrays can be complex; we use real->x, imag->y.
      - .npz file with 'x' and 'y' (1D coords): used as left plot, right empty.
      - .npy file that is 2 x N (treated as two rows: x and y) -> left plot, right empty.
    Raises ValueError for unsupported/ malformed files.
    """
    if path.endswith(".npz"):
        npz = np.load(path, allow_pickle=True)
        keys = list(npz.keys())

        # Prefer explicit saved format
        if "ratio_batch" in npz and "demapper_batch" in npz:
            r = np.asarray(npz["ratio_batch"])
            d = np.asarray(npz["demapper_batch"])

            # Ensure 1D arrays
            r = r.ravel()
            d = d.ravel()

            # Convert complex -> real/imag lists
            left_x = r.real.tolist()
            left_y = r.imag.tolist()
            right_x = d.real.tolist()
            right_y = d.imag.tolist()
            return ((left_x, left_y), (right_x, right_y))

        # Fallback: x/y arrays saved in npz (treat as coordinates for left plot)
        if "x" in npz and "y" in npz:
            x = np.asarray(npz["x"]).ravel()
            y = np.asarray(npz["y"]).ravel()
            return ((x.tolist(), y.tolist()), ([], []))

        # Generic: take first two arrays (if present)
        if len(keys) >= 2:
            a = np.asarray(npz[keys[0]]).ravel()
            b = np.asarray(npz[keys[1]]).ravel()

            # If they are complex, treat as complex pairs
            if np.iscomplexobj(a) and np.iscomplexobj(b):
                left_x = a.real.tolist()
                left_y = a.imag.tolist()
                right_x = b.real.tolist()
                right_y = b.imag.tolist()
                return ((left_x, left_y), (right_x, right_y))
            else:
                # treat a,b as x and y coordinates for left
                return ((a.tolist(), b.tolist()), ([], []))

        raise ValueError(f"npz file {path} has no usable arrays")

    elif path.endswith(".npy"):
        arr = np.load(path, allow_pickle=True)
        arr = np.asarray(arr)
        # if arr is 2 x N (rows: x,y) or (2,N)
        if arr.ndim == 2 and arr.shape[0] >= 2:
            x = arr[0].ravel().tolist()
            y = arr[1].ravel().tolist()
            return ((x, y), ([], []))
        # If it's 1D or other shapes, try to interpret as x coords only (no y)
        raise ValueError(f"npy file {path} not in expected shape (2,N)")

    else:
        raise ValueError("Unsupported extension")

def discover_pairs(folder):
    """
    Discover files in `folder` and return list of pairs:
      [ ((left_x,left_y),(right_x,right_y)), ... ]
    The function looks for:
      - *.npz files (each becomes one pair if it matches expected keys)
      - *_x.npy / *_y.npy pairs (converted to left plot)
    If nothing is found, it returns a small synthetic fallback list.
    """
    pairs = []

    # 1) .npz files
    npz_files = sorted(glob(os.path.join(folder, "*.npz")))
    for f in npz_files:
        try:
            pair = load_pair_from_file(f)
            pairs.append(pair)
        except Exception as e:
            # skip malformed files silently (or print for debug)
            # print(f"Skipping {f}: {e}")
            continue

    # 2) .npy files with naming scheme *_x.npy, *_y.npy
    x_files = sorted(glob(os.path.join(folder, "*_x.npy")))
    for xf in x_files:
        yf = xf.replace("_x.npy", "_y.npy")
        if os.path.exists(yf):
            try:
                x_arr = np.load(xf, allow_pickle=True).ravel().tolist()
                y_arr = np.load(yf, allow_pickle=True).ravel().tolist()
                pairs.append(((x_arr, y_arr), ([], [])))
            except Exception:
                continue

    # 3) Fallback synthetic pairs if nothing found
    if not pairs:
        t = np.linspace(-1.3, 1.3, 128)
        pairs = [
            ((t.tolist(), (0.5 * np.sin(2*np.pi*t)).tolist()), ([], [])),
            ((t.tolist(), (0.5 * np.cos(2*np.pi*t)).tolist()), ([], []))
        ]
    return pairs

def image_pairs_app(doc: Document):
    # Discover/load all pairs (preloads into memory)
    pairs = discover_pairs(NP_FOLDER)

    # Shared settings
    limit = 1.3
    x_min, x_max, y_min, y_max = -limit, limit, -limit, limit

    # Create two ColumnDataSources
    src_left = ColumnDataSource(data=dict(x=[], y=[]))
    src_right = ColumnDataSource(data=dict(x=[], y=[]))

    p_left = figure(title="Ratio", width=350, height=350,
                    x_range=(x_min, x_max), y_range=(y_min, y_max), tools="")
    p_right = figure(title="Demapper", width=350, height=350,
                     x_range=(x_min, x_max), y_range=(y_min, y_max), tools="")

    # Plot only points (scatter)
    p_left.scatter('x', 'y', source=src_left, size=24, color="blue", marker="dot")
    p_right.scatter('x', 'y', source=src_right, size=24, color="#e37a31", marker="dot")

    p_left.xaxis.axis_label = "Real"
    p_left.yaxis.axis_label = "Imag"
    p_right.xaxis.axis_label = "Real"
    p_right.yaxis.axis_label = "Imag"

    layout = row(p_left, p_right)
    doc.add_root(layout)

    state = {"idx": 0}

    def update():
        if not pairs:
            return
        idx = state["idx"] % len(pairs)

        left, right = pairs[idx]  # left = (left_x, left_y), right = (right_x, right_y)
        left_x, left_y = left
        right_x, right_y = right

        # If right is empty, show only left (right source cleared)
        if right_x and right_y:
            src_right.data = {"x": right_x, "y": right_y}
        else:
            src_right.data = {"x": [], "y": []}

        if left_x and left_y:
            src_left.data = {"x": left_x, "y": left_y}
        else:
            src_left.data = {"x": [], "y": []}

        state["idx"] += 1  # step by one

    # Do initial populate
    update()

    # Add periodic callback every 5000 ms (5 seconds)
    doc.add_periodic_callback(update, 1000)
