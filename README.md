<<<<<<< HEAD
# ORAN Dashboard

A Flask + Bokeh web dashboard for visualizing ORAN (Open Radio Access Network) metrics and data.

## Prerequisites

Before running this project, you need:

1. **Python 3.8+** installed on your system
2. **MongoDB** installed and running locally (or access to a MongoDB instance)

### Installing MongoDB

**Windows:**
- Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
- Install and start the MongoDB service
- Or use MongoDB as a Windows service (it should start automatically)

**Alternative:** You can also use MongoDB Atlas (cloud) by setting the `MONGO_URI` environment variable.

## Setup Instructions

### Step 1: Install Python Dependencies

1. Open a terminal/command prompt in the project directory
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Set Up MongoDB (if using local MongoDB)

1. Make sure MongoDB is running on `localhost:27017` (default port)
2. If you're using a different MongoDB instance, create a `.env` file in the project root:
   ```
   MONGO_URI=mongodb://localhost:27017
   ```
   Or for MongoDB Atlas:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   ```

### Step 3: Populate the Database

Before running the dashboard, you need to populate MongoDB with data from the Excel file and log file:

```bash
python database.py
```

This will:
- Read the Excel file from `data/1010123456002_metrics.xlsx`
- Read the log file from `data/xapp-logger.log`
- Store the data in MongoDB (database: `myDatabase`, collections: `csv` and `log`)

### Step 4: Run the Dashboard

Start the Flask application:

```bash
python app.py
```

The application will:
- Start a **Bokeh server** on port **5006** (for interactive visualizations)
- Start a **Flask server** on port **8000** (for the web interface)

### Step 5: Access the Dashboard

Open your web browser and navigate to:

```
http://localhost:8000
```

You should see the ORAN Dashboard with various visualizations and metrics.

## Project Structure

- `app.py` - Main Flask application with Bokeh server integration
- `database.py` - Script to populate MongoDB with data
- `get_data.py` - Database connection and data retrieval utilities
- `views/` - Bokeh visualization components:
  - `kpi_graph.py` - KPI graphs
  - `rbs_assigned.py` - Resource blocks assigned
  - `classifier_output.py` - Classifier output visualization
  - `scheduling_policy.py` - Scheduling policy display
  - `toggle_switch.py` - Toggle switch component
  - `image_pairs.py` - Image pair visualization
  - `rays_animated.py` - Animated rays visualization
- `templates/index.html` - Main dashboard HTML template
- `data/` - Data files (Excel and log files)

## Troubleshooting

### MongoDB Connection Issues

- Make sure MongoDB is running: `mongosh` or check Windows Services
- Verify the connection string in `.env` if you're using a custom MongoDB instance
- Check that the MongoDB port (default: 27017) is not blocked by a firewall

### Port Already in Use

If port 8000 or 5006 is already in use:
- Change the port in `app.py` (line 56 for Flask, line 47 for Bokeh)
- Or stop the application using those ports

### Missing Data

- Make sure you've run `database.py` before starting the dashboard
- Verify that `data/1010123456002_metrics.xlsx` and `data/xapp-logger.log` exist
- Check MongoDB to ensure data was inserted (you can use MongoDB Compass or `mongosh`)

### Import Errors

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using the correct Python version (3.8+)
- Activate your virtual environment if you created one

## Notes

- The dashboard uses Bokeh for interactive visualizations embedded in a Flask web application
- Data is stored in MongoDB for efficient querying and real-time updates
- The application runs both Flask (port 8000) and Bokeh server (port 5006) simultaneously
=======
# updated_OranDashboard_rx
Oran Dashboard updates for GENESYS Lab
>>>>>>> 8f915159f09e84d4d447d7ee8a311a65924af4a9
