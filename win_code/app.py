import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from parser import Parser
from plot import Plots
import os
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
# Tkinter Application
class App:
    def __init__(self, root):
        ctk.set_appearance_mode("System")  # Możesz wybrać "Light" lub "Dark"
        ctk.set_default_color_theme("blue")  # Motyw kolorystyczny
        self.parsed_data = None
        self.file_pattern = "0-Power Board"
        self.root = root
        self.root.title("Data Parser Application")
        self.root.geometry("620x800")
        self.status_label = ctk.CTkLabel(root, text="", text_color="blue", font=("Arial", 10, "italic"))
        self.status_label.grid(row=9, column=0, columnspan=2, pady=20, sticky="n")

        # Mapowanie wzorców plików na listy kolumn
        self.pattern_columns = {
            "0-Power Board": self.get_columns_0(),
            "1-BCDR0": self.get_columns_1(),
            "2-BCDR1": self.get_columns_2(),
            "3-S-Band": self.get_columns_3(),
            "4-HKC": self.get_columns_4(),
            "5-IOBC": self.get_columns_5(),
            "6-ACS": self.get_columns_6(),
            "7-ADCS": self.get_columns_7(),
            "8-ADC_SUB": self.get_columns_8(),
            "9-Header Board": self.get_columns_9()
        }

        # Label
        ctk.CTkLabel(
            root,
            text="Please click Browse to select the 'WOD/Parsed' folder with data to begin.",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, columnspan=4, pady=5)

        # Folder Entry and Browse Button
        ctk.CTkLabel(root, text="Base Folder").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.folder_entry = ctk.CTkEntry(root, width=400)
        self.folder_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkButton(root, text="Browse", command=self.browse_folder).grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Start & End Year
        ctk.CTkLabel(root, text="Start Year").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.start_year_entry = ctk.CTkEntry(root, width=100)
        self.start_year_entry.grid(row=2, column=1, padx=(0, 10), pady=5, sticky="w")

        ctk.CTkLabel(root, text="End Year").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.end_year_entry = ctk.CTkEntry(root, width=100)
        self.end_year_entry.grid(row=3, column=1, padx=(0, 10), pady=5, sticky="w")

        # File Pattern ComboBox
        ctk.CTkLabel(root, text="File Pattern").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.pattern_combo = ctk.CTkComboBox(root, values=list(self.pattern_columns.keys()), command=self.on_pattern_selected)
        self.pattern_combo.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        self.pattern_combo.set("0-Power Board")

        # Columns Frame with Scrollable Area
        self.column_frame = ctk.CTkFrame(root)
        self.column_frame.grid(row=5, column=1, columnspan=3, padx=10, pady=5, sticky="w")

        self.canvas = ctk.CTkCanvas(self.column_frame, width=200, height=200)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ctk.CTkScrollbar(self.column_frame, orientation="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Radio Buttons for Processing Mode
        self.mode_var = ctk.StringVar(value="single")
        ctk.CTkLabel(root, text="Processing Mode").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        ctk.CTkRadioButton(root, text="Single-process mode", variable=self.mode_var, value="single", command=self.toggle_workers).grid(row=6, column=1, sticky="w")
        ctk.CTkRadioButton(root, text="Parallel processing mode", variable=self.mode_var, value="multi", command=self.toggle_workers).grid(row=7, column=1, sticky="w")

        # Slider for Workers
        ctk.CTkLabel(root, text="Parallel tasks").grid(row=8, column=0, padx=10, pady=5, sticky="e")
        self.workers_slider = ctk.CTkSlider(root, from_=2, to=16, number_of_steps=14)
        self.workers_slider.grid(row=8, column=1, padx=(10, 50), pady=5, sticky="w")
        self.workers_slider.set(2)  # Ustawienie domyślnej wartości na 2

        # Buttons
        ctk.CTkButton(root, text="Run Parser", command=self.run_parser).grid(row=9, column=0, padx=10, pady=20, sticky="e")
        self.download_button = ctk.CTkButton(root, text="Save Parsed File", command=self.download_parsed_file, state="disabled")
        self.download_button.grid(row=8, column=2, padx=10, pady=20)

        ctk.CTkButton(root, text="Plot Data", command=self.plot_data).grid(row=9, column=2, padx=10, pady=10)
        ctk.CTkButton(root, text="Exit", command=self.terminate_app).grid(row=16, column=1, columnspan=2, pady=10)

        # Definicja plot_type
        self.plot_type = ctk.StringVar(value="linear")  # Domyślnie "linear"

        # Radiobuttons dla wyboru typu wykresu
        ctk.CTkRadioButton(
            root, text="Linear", variable=self.plot_type, value="linear"
        ).grid(row=10, column=1, padx=(140, 0), pady=5, sticky="e")

        ctk.CTkRadioButton(
            root, text="Logarithmic", variable=self.plot_type, value="log"
        ).grid(row=10, column=2, padx=(40, 10), pady=5, sticky="w")

        # Progress Bar
        self.progress_var = ctk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(root, variable=self.progress_var)
        self.progress_bar.grid(row=14, column=1, columnspan=1, padx=2, pady=2)
        self.progress_bar.set(0)  # Ustawienie początkowego postępu na 0%

        # Progress Label
        self.progress_label = ctk.CTkLabel(root, text="Files processed: 0/0", fg_color="transparent")
        self.progress_label.grid(row=15, column=1, columnspan=1, pady=2)

        # Update default columns
        self.update_columns()


    def show_tooltip(self, event, text):
        # Create a tooltip window
        self.tooltip = tk.Toplevel()
        self.tooltip.overrideredirect(True)  # Remove window decorations
        self.tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")  # Position near cursor
        label = tk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1, font=("Arial", 10))
        label.pack()

    def hide_tooltip(self, event):
        # Destroy the tooltip window
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()

    def on_pattern_selected(self, event=None):
        self.update_columns(event)
        self.update_file_pattern(event)

    def update_file_pattern(self, event=None):
        self.file_pattern = self.pattern_combo.get()


    def browse_folder(self):
        parent_dir = os.path.dirname(os.getcwd())
        folder_selected = filedialog.askdirectory(initialdir=parent_dir, title="Select Folder")
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def update_columns(self, event=None):
        # Wyczyść istniejące elementy w scrollable_frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        selected_pattern = self.pattern_combo.get()
        columns = self.pattern_columns.get(selected_pattern, [])
        self.column_checkboxes = {}

        for col in columns:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(self.scrollable_frame, text=col, variable=var, anchor="w", width=50)
            chk.pack(fill="x", pady=1)
            self.column_checkboxes[col] = var

    def update_progress_callback(self, processed_count, total_files):
        try:
            progress_percentage = processed_count / total_files
            self.progress_var.set(progress_percentage)
            self.progress_label.configure(text=f"Files processed: {processed_count}/{total_files}")
            self.root.update_idletasks()
        except Exception as e:
            print(f"Error in progress callback: {e}")  # Debugowanie błędów

    def run_parser(self):
        self.base_folder = self.folder_entry.get()
        start_year = self.start_year_entry.get()
        end_year = self.end_year_entry.get()
        if not self.base_folder:
            messagebox.showerror("Error", "Please select a base folder")
            return

        self.additional_columns = [col for col, var in self.column_checkboxes.items() if var.get()]

        mode = self.mode_var.get()
        if mode == "multi":
            workers = int(self.workers_slider.get())
        else:
            workers = 1

        try:
            self.status_label.configure(text="", text_color="orange")  # Resetowanie statusu
            self.root.update_idletasks()

            # Logika parsowania danych
            parser = Parser(
                self.base_folder,
                self.additional_columns,
                start_year=start_year if start_year else None,
                end_year=end_year if end_year else None,
                workers=workers
            )
            self.parsed_data = parser.parse_data_no_merging(self.file_pattern,
                                                            progress_callback=self.update_progress_callback)

            elapsed_time = parser.end_time - parser.start_time
            row_count = len(self.parsed_data)

            # Ustawienie statusu na sukces
            self.status_label.configure(
                text=f"Time: {elapsed_time:.2f} sec. Rows: {row_count}",
                text_color="green"
            )
            messagebox.showinfo("Success",
                                "Data parsed successfully. You can now download the parsed file or plot the data.")
            self.download_button.configure(state="normal")

        except Exception as e:
            # Wyświetl błąd, jeśli rzeczywiście wystąpił
            self.status_label.configure(text="Parsing failed.", text_color="red")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def toggle_workers(self):
        mode = self.mode_var.get()
        if mode == "multi":
            self.workers_slider.config(state="normal")
        else:
            self.workers_slider.config(state="disabled")

    def download_parsed_file(self):
        if self.parsed_data is not None and not self.parsed_data.empty:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Parsed File"
            )
            if output_file:
                try:

                    #self.status_label.config(text="Saving...", fg="orange")
                    self.root.update_idletasks()

                    self.parsed_data.to_csv(output_file, index=False)

                    #self.status_label.config(text=f"File saved successfully: {output_file}", fg="green")
                    messagebox.showinfo("Success", f"File saved to: {output_file}")
                except Exception as e:
                    self.status_label.config(text="save failed.", text_color="red")
                    messagebox.showerror("Error", f"An error occurred while saving the file: {e}")
            else:
                self.status_label.config(text="save canceled.", text_color="blue")
        else:
            self.status_label.config(text="No data to save.", text_color="red")
            messagebox.showerror("Error", "No data available to save.")

    def get_columns_0(self):
        return ["'SStates Loadshed","'SStates Loadshed Latch","'SStates Test Mode","'SStates Magnetometer","'SStates PXFSS","'SStates NXFSS","'SStates PYFSS","'SStates NYFSS","'SStates PZFSS","'SStates NZFSS","'SStates XWheel","'SStates YWheel","'SStates ZWheel","'SStates RateGyro","'SStates MTX","'SStates MTY","'SStates MTZ","'SStates GPS Supply","'SStates 5V Supply","'SStates Spare","'SStates Instrument","'SStates GPS","'SStates BCDR0State","'SStates BCDR1State","'+X Panel Current(mA)","'+Y Panel Current(mA)","'+Z Panel Current(mA)","'-X Panel Current(mA)","'-Y Panel Current(mA)","'-Z Panel Current(mA)","'+X Panel Temperature(°C)","'+Y Panel Temperature(°C)","'+Z Panel Temperature(°C)","'-X Panel Temperature(°C)","'-Y Panel Temperature(°C)","'-Z Panel Temperature(°C)","'Bus Voltage(V)","'Main Switch Current(A)","'5V Rail Voltage(V)","'3V Rail Voltage(V)","'3V Rail Current(mA)","'ADC0 Temperture(°C)","'ADC1 Temperture(°C)","'ADC2 Temperture(°C)","'BCDR0 Battery Voltage(V)","'BCDR1 Battery Voltage(V)","'HKC Current(mA)","'ADCC Current(mA)","'Magnetometer Voltage(V)","'Rate Sensor Voltage(V)","'Rate Sensor Current(mA)","'Sun Sensor Voltage(V)","'Sun Sensor Current(mA)","'Mag. Torquer X Current(mA)","'Mag. Torquer Y Current(mA)","'Mag. Torquer Z Current(mA)","'Wheel Sum Current(mA)","'Wheel X Voltage(V)","'Wheel Y Voltage(V)","'Wheel Z Voltage(V)","'ST Switch Voltage(V)","'ST Switch Current(mA)","'ST Voltage(V)","'ST Current(mA)","'Instrument Voltage(V)","'Instrument Current(mA)","'UHF Rx Current(mA)","'UHF Rx Temperature(°C)","'UHF Rx SSI(V)","'S-Band Tx Voltage(V)","'S-Band Tx Current(A)"]

    def get_columns_1(self):
        return ["'Reset Reason","'Reset Count","'SEU Count","'Ping Pointer","'Control Pointer","'Battery Temperature(°C)","'Heater On","'Mode","'Bus Voltage(V)","'Battery Voltage(V)","'Battery Current(mA)","'State of Charge(mA*h)","'Bus Target(V)","'Discharge Command"]

    def get_columns_2(self):
        return ["'Reset Reason","'Reset Count","'SEU Count","'Ping Pointer","'Control Pointer","'Battery Temperature(°C)","'Heater On","'Mode","'Bus Voltage(V)","'Battery Voltage(V)","'Battery Current(mA)","'State of Charge(mA*h)","'Bus Target(V)","'Discharge Command"]

    def get_columns_3(self):
        return ["'Tx ADC Temperature(°C)","'PA Forward Power(V)","'PA Reverse Power(V)","'PA Control Signal(V)","'3V Analog Supply Current PA(mA)","'5V Supply(V)","'Synthesizer Temperature(°C)","'3V Analog Supply Voltage PA(V)","'Power Amplifier Temperature(°C)","'5V Supply Current(mA)","'3V Analog Supply Current CB(mA)","'3V VCO Supply Current(mA)","'3V Digital Supply Current(mA)","'Synthesizer Lock A(V)","'Synthesizer Lock B(V)","'3V Analog Supply Voltage CB(V)","'3V Digital Supply Voltage CB(V)"]

    def get_columns_4(self):
        return ["'HKC Temperature(°C)","'Reset Count","'Last Reset Reason"]

    def get_columns_5(self):
        return ["'TMS470 Video ADC Temperature(°C)","'TMS470 Heater Voltage(V)","'TMS470 +6V(V)","'MAX1231 Temperature(°C)","'MAX1231 H1H (+6V)(V)","'MAX1231 HRH (+1.5V)(V)","'MAX1231 vh+fdh (+8V)(V)","'MAX1231 RDL (+11V)(V)","'MAX1231 RR (+1.5V)(V)","'MAX1231 +15V(V)","'MAX1231 +Sub (+10V)(V)","'MAX1231 +18V(V)","'MAX1231 +5VA(V)","'MAX1231 H1L (-4V)(V)","'MAX1231 ESD (+8V)(V)","'MAX1231 -FDL (-9V)(V)","'MAX1231 HRL (-3.5V)(V)","'MAX1231 OGL (-2.5V)(V)","'MAX1231 -18V(V)","'MAX1231 -5VA(V)","'GPIO GIO Dir A","'GPIO GIO DIn A","'GPIO GIO DOut A","'GPIO HET Dir A","'GPIO HET DIn A","'GPIO HET DOut A","'FPGA Status[0]","'FPGA Status[1]","'IOBC Exception[0]","'IOBC Exception[1]","'IOBC Exception[2]","'IOBC Exception[3]"]

    def get_columns_6(self):
        return ["'EulerAngleErrors Data[0]","'EulerAngleErrors Data[1]","'EulerAngleErrors Data[2]","'EulerAngleErrors Length","'Mode In","'Mode In","'Mode Out","'Mode Out","'StateVector Data[0]","'StateVector Data[1]","'StateVector Data[2]","'StateVector Data[3]","'StateVector Data[4]","'StateVector Data[5]","'StateVector Data[6]","'StateVector Length","'Chosen FSS","'Current FFS Data[0]","'Current FFS Data[1]","'Current FFS Data[2]","'Current FFS Data[3]","'Current FFS Data[4]","'Current FFS Data[5]","'Current FFS Data[6]","'Cycle Counter","'Gamma","'Useable FSS Data[0]","'Useable FSS Data[1]","'Useable FSS Data[2]","'Useable FSS Data[3]","'Useable FSS Data[4]","'Useable FSS Data[5]","'Useable_FSS Length","'Active Sensors Data[0]","'Active Sensors Data[1]","'Active Sensors Data[2]","'Active Sensors Data[3]","'Active Sensors Length","'Hold Transition","'StatePkp1p Data[0]","'StatePkp1p Data[1]","'StatePkp1p Data[2]","'StatePkp1p Data[3]","'StatePkp1p Data[4]","'StatePkp1p Data[5]","'StatePkp1p Data[6]","'StatePkp1p Length"]

    def get_columns_7(self):
        return ["'ACS Cycle Count","'ACS Cycle Timeout Count","'ACS Cycle OASYS Count","'ACS State","'ACS SubState[0]","'ACS SubState[1]","'ACS SubState[2]","'ACS SubState[3]","'ACS SubState[4]","'ACS SubState[5]","'ACS SubState[6]","'ACS SubState[7]","'ACS SubState[8]","'ACS SubState[9]","'ACS Error Code","'ACS Device Config Mask","'SS CoarseVoltage 0(V)","'SS Exposure Time 0(ms)","'SS CoarseVoltage 1(V)","'SS Exposure Time 1(ms)","'SS CoarseVoltage 2(V)","'SS Exposure Time 2(ms)","'SS CoarseVoltage 3(V)","'SS Exposure Time 3(ms)","'SS CoarseVoltage 4(V)","'SS Exposure Time 4(ms)","'SS CoarseVoltage 5(V)","'SS Exposure Time 5(ms)","'Wheel Speed[0](rad/s)","'Wheel Speed[1](rad/s)","'Wheel Speed[2](rad/s)","'Magnetometer X","'Magnetometer Y","'Magnetometer Z","'Magnetometer Temperature(°C)","'Rate Sensor X","'Rate Sensor Y","'Rate Sensor Z","'Rate Sensor Temperature(°C)"]

    def get_columns_8(self):
        return ["'Error Code","'Telemetry WheelSpeed Value[0]","'Telemetry WheelSpeed Value[1]","'Telemetry WheelSpeed Value[2]","'Telemetry WheelSpeed Length","'EKFMon Mag Iterations","'EKFMon Mag Residual Value[0]","'EKFMon Mag Residual Value[1]","'EKFMon Mag Residual Value[2]","'EKFMon Mag Residual Length","'EKFMon Mag Trace P","'EKFMon Fss Iterations","'EKFMon Fss Residual Value[0]","'EKFMon Fss Residual Value[1]","'EKFMon Fss Residual Value[2]","'EKFMon Fss Residual Value[3]","'EKFMon Fss Residual Value[4]","'EKFMon Fss Residual Value[5]","'EKFMon Fss Residual Length","'EKFMon Fss Trace P","'EKFMon RTS Iterations","'EKFMon RTS Residual Value[0]","'EKFMon RTS Residual Value[1]","'EKFMon RTS Residual Value[2]","'EKFMon RTS Residual Length"]

    def get_columns_9(self):
        return ["'Reset Count File","'Reset Reason File","'Comm Err Count File","'Scrub Index File","'SEU Count File","'Init Pointer File","'Ping Pointer File","'ADC Raw1 File","'ADC Raw2 File","'ADC Raw3 File","'ADC Raw4 File","'PWM Setting File","'PWM Period File","'PWM Controller Pointer File","'PWM Controller Cycle File","'PWM DCycle1 File","'PWM DCycle2 File","'PWM DCycle3 File","'PWM DCycle4 File","'Converted Temp1 File(°C)","'Converted Temp2 File(°C)","'Converted Temp3 File(°C)","'Converted Temp4 File(°C)","'Controller P Gain File","'Controller I Gain File","'Controller D Gain File","'Controller I Max File","'Controller Max DT File","'Controller SetPoint File","'Controller I State File"]

    def confirm_and_plot(self, window, column_listbox, plot_type):
        selected_indices = column_listbox.curselection()
        selected_columns = [column_listbox.get(i) for i in selected_indices]

        if not selected_columns:
            messagebox.showerror("Error", "No columns selected for plotting.")
            return

        window.destroy()

        plots = Plots()
        plots.plot(self.parsed_data, selected_columns, plot_type)

    def plot_data(self):
        if self.parsed_data is None or self.parsed_data.empty:
            messagebox.showerror("Error", "No data to plot. Please run the parser first.")
            return

        plot_type = self.plot_type.get()

        plot_window = tk.Toplevel(self.root)
        plot_window.title("Select Columns to Plot")
        plot_window.geometry("200x400")

        tk.Label(plot_window, text="Select Columns for Plotting:").pack(pady=10)

        column_listbox = tk.Listbox(plot_window, selectmode="multiple", height=15, width=50)
        column_listbox.pack(padx=10, pady=10)

        for col in self.parsed_data.columns[3:]:
            column_listbox.insert(tk.END, col)

        tk.Button(plot_window, text="Plot Selected",
                  command=lambda: self.confirm_and_plot(plot_window, column_listbox, plot_type)).pack(pady=5)

    def plot_loop(self):
        def plot_and_show_options():
            selected_indices = self.column_listbox.curselection()
            selected_columns = [self.column_listbox.get(i) for i in selected_indices]

            if not selected_columns:
                messagebox.showerror("Error", "No columns selected for plotting.")
                return

            plots = Plots()
            plots.plot(self.parsed_data, selected_columns)

            options_window = tk.Toplevel(self.root)
            options_window.title("Plot Options")
            options_window.geometry("300x150")

            tk.Label(options_window, text="Choose an action:").pack(pady=10)

            tk.Button(options_window, text="Download Plot", command=lambda: self.download_plot(options_window)).pack(
                pady=5)

            tk.Button(options_window, text="Move to Another", command=lambda: options_window.destroy()).pack(pady=5)

            tk.Button(options_window, text="Terminate", command=lambda: self.terminate_app(options_window)).pack(pady=5)

        while True:
            plot_and_show_options()
            if hasattr(self, 'terminate') and self.terminate:
                break

    def download_plot(self, window):
        plt.savefig("plot_output.pdf", format="pdf")
        messagebox.showinfo("Success", "Plot saved as plot_output.pdf")
        window.destroy()

    def terminate_app(self):
        self.root.destroy()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    root = tk.Tk()
    app = App(root)
    root.mainloop()