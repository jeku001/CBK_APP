# Data Parser and Plotting Application

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Using the Application](#using-the-application)
  - [Step 1: Loading Data](#step-1-loading-data)
  - [Step 2: Configuring the Parser](#step-2-configuring-the-parser)
  - [Step 3: Running the Parser](#step-3-running-the-parser)
  - [Step 4: Plotting Data](#step-4-plotting-data)
  - [Optional: Saving Parsed Data](#optional-saving-parsed-data)
- [Data Structure and Context](#data-structure-and-context)
- [Acknowledgements](#acknowledgements)

---

## Overview
This application is designed to help scientists efficiently process large housekeeping datasets from the **LEM** and **HEWELIUSZ** satellites. The primary goal is to enable the extraction and visualization of specific data columns from CSV files containing over 30GB of satellite telemetry data.

Key features include:
- Parsing and filtering CSV data based on selected columns.
- Support for single-process and multi-process data processing.
- Interactive plotting with linear and logarithmic scales.
- User-friendly interface for quick navigation and data handling.

---

## Installation
To run the application, follow these steps:

1. **Download the application**
   - Obtain the `app.exe` file and the accompanying directory containing necessary resources.

2. **Run the executable**
   - Double-click `app.exe` to launch the application. No additional installation is required.

3. **System Requirements**
   - Windows 10 or later, or a modern Linux distribution (e.g., Ubuntu 20.04+).
   - At least 8GB of RAM (recommended for larger datasets).
   - Python 3.9+ with `matplotlib` and `pandas` installed (if using the source code).

---

## Using the Application

### Step 1: Loading Data
1. Launch the application by running `app.exe`.
2. Click the **Browse** button to select the folder containing your satellite data files.

### Step 2: Configuring the Parser
1. Use the **Start Year** and **End Year** fields to filter data by year. These fields are optional and can be left empty to include all available data.
2. Select a **File Pattern** to narrow down the type of data you want to parse (e.g., "0-Power Board").
3. Check the desired columns in the **Select Columns** section to include them in the output.
4. Choose a processing mode:
   - **Single-process mode**: Processes files one by one (useful for small datasets).
   - **Parallel processing mode**: Enables faster processing by using multiple CPU cores. You can specify the number of tasks in the **Parallel Tasks** field.

### Step 3: Running the Parser
1. Click **Run Parser** to start the data processing.
2. Monitor the progress using the progress bar and file count indicator.
3. Once completed, the parsed data will be ready for plotting or saving.

### Step 4: Plotting Data
1. Click **Plot Data** to open the column selection window.
2. Choose one or more columns to plot.
3. Select a scale:
   - **Linear**: Standard scale.
   - **Logarithmic**: For data with a wide range of values.
4. View the interactive plot. Use the red cursor to inspect specific points.

### Optional: Saving Parsed Data
1. Click **Save Parsed File** to export the parsed data as a CSV file.
2. Choose the destination and filename in the save dialog.

---

## Data Structure and Context

### Source of Data
The data originates from the LEM and HEWELIUSZ satellites, launched as part of a collaborative project to collect telemetry data. 

- **LEM Satellite**: A Polish satellite launched in 2013, primarily designed for stellar photometry and astrophysical observations.
- **HEWELIUSZ Satellite**: Launched in 2014, HEWELIUSZ complements LEM's mission, with additional capabilities for space environment monitoring. The dataset spans from their launch dates to the present, amounting to over 30GB of CSV files.

### Data Format
The files are organized in a hierarchical structure. For example:
