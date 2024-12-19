3. Ensure the folder contains subdirectories named by year (e.g., `2020-01`).

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
Each file contains time-series data with columns such as:
- `'Date (YYYY-MM-DD HH:MM:SS)`': Timestamp of the data.
- `'Date (J2000 mseconds)`': Time in milliseconds since J2000 epoch.
- Specific housekeeping parameters (e.g., temperatures, reset reasons).

### Examples of Parameters
- **LEM Satellite**:
- `'SStates Loadshed'`
- `'Tx ADC Temperature(°C)`'
- **HEWELIUSZ Satellite**:
- `'EulerAngleErrors Data[0]'`
- `'Telemetry WheelSpeed Value[0]`'

---

## Acknowledgements
This tool was developed to simplify the analysis of satellite telemetry data and is part of a portfolio of projects designed for scientific applications. Special thanks to the teams behind LEM and HEWELIUSZ for their contributions to satellite telemetry.

For further inquiries or bug reports, please contact [your_email@example.com].
