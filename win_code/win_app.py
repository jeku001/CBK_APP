import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from win_parser import Parser
from win_plot import Plots
import os
import matplotlib
from threading import Thread
from win_tooltip import ToolTip
matplotlib.use("TkAgg")


# Tkinter Application
class App:
    def __init__(self, root):
        ctk.set_appearance_mode("System")  # Możesz wybrać "Light" lub "Dark"
        ctk.set_default_color_theme("blue")  # Motyw kolorystyczny

        self.root = root
        self.root.title("Data Parser Application")
        self.root.geometry("900x600")  # Ustawienie większego rozmiaru dla lepszego układu
        self.parsed_data = None
        self.file_pattern = "0-Power Board"
        self.additional_columns = []
        self.last_selected_pattern = "0-Power Board"
        self.parse_column_checkboxes = {}
        self.plot_column_checkboxes = {}
        self.plot_type_var = tk.StringVar(value="linear")
        self.mode_var = tk.StringVar(value="single")
        self.thread_number = 0
        self.cpu_cores = os.cpu_count()

        # Layout konfiguracji siatki
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

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

        # Środkowy panel (status i wybór kolumn)
        self.center_frame = ctk.CTkFrame(self.root, corner_radius=10, bg_color="transparent")
        self.center_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.center_frame, text="File Pattern").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.pattern_combo = ctk.CTkComboBox(self.center_frame, values=list(self.pattern_columns.keys()),
                                             command=self.on_pattern_selected)
        self.pattern_combo.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.pattern_combo.set("0-Power Board")

        # Scrollable Frame
        self.column_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.column_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="nswe")

        self.canvas = ctk.CTkCanvas(self.column_frame, width=200, height=200)
        self.scrollbar = ctk.CTkScrollbar(self.column_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.status_label = ctk.CTkLabel(self.center_frame, text="", text_color="blue", font=("Arial", 10, "italic"))
        self.status_label.grid(row=3, column=0, columnspan=3, pady=10)

        # Etykieta postępu
        self.progress_label = ctk.CTkLabel(self.center_frame, text="Files processed: 0/0", font=("Arial", 10))
        self.progress_label.grid(row=5, column=0, columnspan=3, pady=5)

        # Lewy panel (parsowanie)
        self.left_frame = ctk.CTkFrame(self.root, width=250, corner_radius=10)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.left_frame.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(self.left_frame, text="Parsing Options", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(self.left_frame, text="Base Folder").pack(pady=5)

        self.folder_entry = ctk.CTkEntry(self.left_frame, width=230)
        self.folder_entry.pack(pady=10)
        ctk.CTkButton(self.left_frame, text="Browse", command=self.browse_folder).pack(pady=5)

        # Dla etykiety "Start Year"
        ctk.CTkLabel(self.left_frame, text="Start Year").pack(pady=(1, 0))  # Zmniejszamy górny margines
        self.start_year_entry = ctk.CTkEntry(self.left_frame, width=100)
        self.start_year_entry.pack(pady=(0, 5))  # Usuwamy górny margines, dodajemy tylko dolny

        # Dla etykiety "End Year"
        ctk.CTkLabel(self.left_frame, text="End Year").pack(pady=(1, 0))  # Zmniejszamy górny margines
        self.end_year_entry = ctk.CTkEntry(self.left_frame, width=100)
        self.end_year_entry.pack(pady=(0, 5))  # Usuwamy górny margines, dodajemy tylko dolny

        # Kontenery dla przycisków radiowych i znaków zapytania
        single_mode_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        single_mode_container.pack(pady=10)

        self.single_mode_button = ctk.CTkRadioButton(single_mode_container, text="Single Mode",
                                                     variable=self.mode_var, value="single",
                                                     command=self.toggle_workers)
        self.single_mode_button.pack(side='left', padx=(10, 2))

        self.question_button_single = ctk.CTkButton(single_mode_container, text="?", width=20, text_color="#141414",
                                                    fg_color="#edd7af", font=("Arial", 14, "bold"))
        self.question_button_single.pack(side='left', padx=(2, 10))
        self.create_tooltip(self.question_button_single, "Process files one by one. \n"
                                                         "Recommended for smaller datasets \n"
                                                         "or limited computational resources.")

        multi_mode_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        multi_mode_container.pack(pady=10)

        self.multi_mode_button = ctk.CTkRadioButton(multi_mode_container, text="Parallel Mode",
                                                    variable=self.mode_var, value="multi",
                                                    command=self.toggle_workers)
        self.multi_mode_button.pack(side='left', padx=(10, 2))

        self.question_button_multi = ctk.CTkButton(multi_mode_container, text="?", width=20, text_color="#141414",
                                                   fg_color="#edd7af", font=("Arial", 14, "bold"))
        self.question_button_multi.pack(side='left', padx=(2, 10))
        self.create_tooltip(self.question_button_multi, "This mode processes multiple files simultaneously, "
                                                        "using parallel threads. \n"
                                                        "Ideal for larger data or device "
                                                        "with higher computational power.")

        # Suwak dla zadań równoległych
        self.workers_slider = ctk.CTkSlider(self.left_frame, from_=2, to=self.cpu_cores,
                                            number_of_steps=14, command=self.update_worker_label)
        self.workers_slider.set(2)
        self.workers_slider.pack(pady=10)
        self.workers_slider.configure(state="disabled")

        # Kontener dla etykiety i pytajnika
        worker_label_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")  # Przezroczyste tło
        worker_label_frame.pack(pady=(1, 10), fill="x")

        # Frame wewnętrzny do zarządzania układem
        inner_frame = ctk.CTkFrame(worker_label_frame, fg_color="transparent")
        inner_frame.pack(anchor="center")

        # Etykieta "Parallel tasks"
        self.worker_label = ctk.CTkLabel(inner_frame, text="Parallel tasks: 2")
        self.worker_label.pack(side="left", padx=(0, 5))  # Odstęp po prawej stronie

        # Przycisk z pytajnikiem obok etykiety
        self.worker_tooltip_button = ctk.CTkButton(inner_frame,text="?", width=20, text_color="#141414",
                                                   fg_color="#edd7af", font=("Arial", 14, "bold"))
        self.worker_tooltip_button.pack(side="left", padx=(5, 0))  # Odstęp po lewej stronie

        self.create_tooltip(self.worker_tooltip_button,
                            f"Adjust the number of parallel tasks.\n"
                            f"This controls how many files are processed simultaneously.\n"
                            f"Recommended: Up to the number of your CPU cores ({self.cpu_cores}).")


        ctk.CTkButton(self.left_frame, text="Run Parser", command=self.parse_button_clicked).pack(pady=20)

        # Prawy panel (zapis i wykresy)
        self.right_frame = ctk.CTkFrame(self.root, width=200, corner_radius=10)
        self.right_frame.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)
        self.right_frame.grid_rowconfigure(4, weight=1)  # Zmiana tutaj, aby przycisk Exit był na dole

        ctk.CTkLabel(self.right_frame, text="Plot and Save", font=("Arial", 16, "bold")).pack(pady=10)
        self.download_button = ctk.CTkButton(self.right_frame, text="Save Parsed File",
                                             command=self.download_parsed_file, state="disabled")
        self.download_button.pack(pady=10)

        self.setup_plot_options()  # inicjowanie ramki na typ skali

        # Stworzenie scrollable frame dla kolumn do plotowania
        self.plot_column_frame = ctk.CTkFrame(self.right_frame)
        self.plot_column_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.plot_column_canvas = ctk.CTkCanvas(self.plot_column_frame, width=200, height=200)
        self.plot_column_scrollbar = ctk.CTkScrollbar(self.plot_column_frame, orientation="vertical",
                                                      command=self.plot_column_canvas.yview)
        self.plot_column_scrollable_frame = ctk.CTkFrame(self.plot_column_canvas)

        self.plot_column_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.plot_column_canvas.configure(scrollregion=self.plot_column_canvas.bbox("all"))
        )

        self.plot_column_canvas.create_window((0, 0), window=self.plot_column_scrollable_frame, anchor="nw")
        self.plot_column_canvas.configure(yscrollcommand=self.plot_column_scrollbar.set)

        self.plot_column_canvas.pack(side="left", fill="both", expand=True)
        self.plot_column_scrollbar.pack(side="right", fill="y")
        ctk.CTkButton(self.right_frame, text="Plot Selected Columns", command=self.plot_selected_columns).pack(pady=10)

        # Przycisk Exit teraz umieszczony na dole i z lekko czerwonym kolorem
        exit_button = ctk.CTkButton(self.right_frame, text="Exit", command=self.terminate_app, fg_color="#f73e3e")
        exit_button.pack(side="bottom", pady=10)

        # Aktualizacja kolumn
        self.update_parse_columns()

        # Pasek postępu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(self.center_frame, variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=5)
        self.progress_bar.set(0)

    def update_worker_label(self, value):
        self.worker_label.configure(text=f"Tasks: {int(value)}")

    def update_parse_columns(self, event=None):
        selected_pattern = self.pattern_combo.get()
        columns = self.pattern_columns.get(selected_pattern, [])
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.parse_column_checkboxes = {}
        for col in columns:
            var = tk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(self.scrollable_frame, text=col, variable=var, width=50)
            chk.pack(fill="x", pady=1)
            self.parse_column_checkboxes[col] = var

        columns = self.pattern_columns.get(selected_pattern, [])

        if not self.parse_column_checkboxes:
            for col in columns:
                var = tk.BooleanVar(value=False)
                chk = ctk.CTkCheckBox(self.scrollable_frame, text=col, variable=var, width=50)
                chk.pack(fill="x", pady=1)
                self.parse_column_checkboxes[col] = var

        self.last_selected_pattern = selected_pattern

    def on_pattern_selected(self, event=None):
        selected_pattern = self.pattern_combo.get()
        self.file_pattern = selected_pattern
        self.update_parse_columns(event)
        self.update_plot_columns_list()

    def update_progress_callback(self, processed_count, total_files):
        try:
            progress_percentage = processed_count / total_files
            self.progress_var.set(progress_percentage)
            self.progress_label.configure(text=f"Files processed: {processed_count}/{total_files}")
            self.root.update_idletasks()
        except Exception as e:
            print(f"Error in progress callback: {e}")

    def browse_folder(self):
        parent_dir = os.path.dirname(os.getcwd())
        folder_selected = filedialog.askdirectory(initialdir=parent_dir, title="Select Folder")
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def parse_button_clicked(self):
        thread_name = "run_parser_thread_" + str(self.thread_number)
        new_thread = Thread(target=self.run_parser,
                            daemon=True, name=thread_name)
        print(f"starting thread named {thread_name}")
        self.thread_number += 1
        new_thread.start()

    def run_parser(self):
        self.base_folder = self.folder_entry.get()
        start_year = self.start_year_entry.get()
        end_year = self.end_year_entry.get()
        if not self.base_folder:
            messagebox.showerror("Error", "Please select a base folder")
            return

        self.additional_columns = [col for col, var in self.parse_column_checkboxes.items() if var.get()]

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

        self.update_plot_columns_list_safe()

    def toggle_workers(self):
        mode = self.mode_var.get()
        print(f"mode: {mode}")  # Debug print
        if mode == "multi":
            self.workers_slider.configure(state="normal")
        else:
            self.workers_slider.configure(state="disabled")

    def download_parsed_file(self):
        if self.parsed_data is not None and not self.parsed_data.empty:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Parsed File"
            )
            if output_file:
                try:

                    # self.status_label.config(text="Saving...", fg="orange")
                    self.root.update_idletasks()

                    self.parsed_data.to_csv(output_file, index=False)

                    # self.status_label.config(text=f"File saved successfully: {output_file}", fg="green")
                    messagebox.showinfo("Success", f"File saved to: {output_file}")
                except Exception as e:
                    self.status_label.configure(text="save failed.", text_color="red")
                    messagebox.showerror("Error", f"An error occurred while saving the file: {e}")
            else:
                self.status_label.configure(text="save canceled.", text_color="blue")
        else:
            self.status_label.configure(text="No data to save.", text_color="red")
            messagebox.showerror("Error", "No data available to save.")

    @staticmethod
    def get_columns_0():
        return ["'SStates Loadshed", "'SStates Loadshed Latch", "'SStates Test Mode", "'SStates Magnetometer",
                "'SStates PXFSS", "'SStates NXFSS", "'SStates PYFSS", "'SStates NYFSS", "'SStates PZFSS",
                "'SStates NZFSS", "'SStates XWheel", "'SStates YWheel", "'SStates ZWheel", "'SStates RateGyro",
                "'SStates MTX", "'SStates MTY", "'SStates MTZ", "'SStates GPS Supply", "'SStates 5V Supply",
                "'SStates Spare", "'SStates Instrument", "'SStates GPS", "'SStates BCDR0State", "'SStates BCDR1State",
                "'+X Panel Current(mA)", "'+Y Panel Current(mA)", "'+Z Panel Current(mA)", "'-X Panel Current(mA)",
                "'-Y Panel Current(mA)", "'-Z Panel Current(mA)", "'+X Panel Temperature(°C)",
                "'+Y Panel Temperature(°C)", "'+Z Panel Temperature(°C)", "'-X Panel Temperature(°C)",
                "'-Y Panel Temperature(°C)", "'-Z Panel Temperature(°C)", "'Bus Voltage(V)", "'Main Switch Current(A)",
                "'5V Rail Voltage(V)", "'3V Rail Voltage(V)", "'3V Rail Current(mA)", "'ADC0 Temperture(°C)",
                "'ADC1 Temperture(°C)", "'ADC2 Temperture(°C)", "'BCDR0 Battery Voltage(V)",
                "'BCDR1 Battery Voltage(V)", "'HKC Current(mA)", "'ADCC Current(mA)", "'Magnetometer Voltage(V)",
                "'Rate Sensor Voltage(V)", "'Rate Sensor Current(mA)", "'Sun Sensor Voltage(V)",
                "'Sun Sensor Current(mA)", "'Mag. Torquer X Current(mA)", "'Mag. Torquer Y Current(mA)",
                "'Mag. Torquer Z Current(mA)", "'Wheel Sum Current(mA)", "'Wheel X Voltage(V)", "'Wheel Y Voltage(V)",
                "'Wheel Z Voltage(V)", "'ST Switch Voltage(V)", "'ST Switch Current(mA)", "'ST Voltage(V)",
                "'ST Current(mA)", "'Instrument Voltage(V)", "'Instrument Current(mA)", "'UHF Rx Current(mA)",
                "'UHF Rx Temperature(°C)", "'UHF Rx SSI(V)", "'S-Band Tx Voltage(V)", "'S-Band Tx Current(A)"]

    @staticmethod
    def get_columns_1():
        return ["'Reset Reason", "'Reset Count", "'SEU Count", "'Ping Pointer", "'Control Pointer",
                "'Battery Temperature(°C)", "'Heater On", "'Mode", "'Bus Voltage(V)", "'Battery Voltage(V)",
                "'Battery Current(mA)", "'State of Charge(mA*h)", "'Bus Target(V)", "'Discharge Command"]

    @staticmethod
    def get_columns_2():
        return ["'Reset Reason", "'Reset Count", "'SEU Count", "'Ping Pointer", "'Control Pointer",
                "'Battery Temperature(°C)", "'Heater On", "'Mode", "'Bus Voltage(V)", "'Battery Voltage(V)",
                "'Battery Current(mA)", "'State of Charge(mA*h)", "'Bus Target(V)", "'Discharge Command"]

    @staticmethod
    def get_columns_3():
        return ["'Tx ADC Temperature(°C)", "'PA Forward Power(V)", "'PA Reverse Power(V)", "'PA Control Signal(V)",
                "'3V Analog Supply Current PA(mA)", "'5V Supply(V)", "'Synthesizer Temperature(°C)",
                "'3V Analog Supply Voltage PA(V)", "'Power Amplifier Temperature(°C)", "'5V Supply Current(mA)",
                "'3V Analog Supply Current CB(mA)", "'3V VCO Supply Current(mA)", "'3V Digital Supply Current(mA)",
                "'Synthesizer Lock A(V)", "'Synthesizer Lock B(V)", "'3V Analog Supply Voltage CB(V)",
                "'3V Digital Supply Voltage CB(V)"]

    @staticmethod
    def get_columns_4():
        return ["'HKC Temperature(°C)", "'Reset Count", "'Last Reset Reason"]

    @staticmethod
    def get_columns_5():
        return ["'TMS470 Video ADC Temperature(°C)", "'TMS470 Heater Voltage(V)", "'TMS470 +6V(V)",
                "'MAX1231 Temperature(°C)", "'MAX1231 H1H (+6V)(V)", "'MAX1231 HRH (+1.5V)(V)",
                "'MAX1231 vh+fdh (+8V)(V)", "'MAX1231 RDL (+11V)(V)", "'MAX1231 RR (+1.5V)(V)", "'MAX1231 +15V(V)",
                "'MAX1231 +Sub (+10V)(V)", "'MAX1231 +18V(V)", "'MAX1231 +5VA(V)", "'MAX1231 H1L (-4V)(V)",
                "'MAX1231 ESD (+8V)(V)", "'MAX1231 -FDL (-9V)(V)", "'MAX1231 HRL (-3.5V)(V)", "'MAX1231 OGL (-2.5V)(V)",
                "'MAX1231 -18V(V)", "'MAX1231 -5VA(V)", "'GPIO GIO Dir A", "'GPIO GIO DIn A", "'GPIO GIO DOut A",
                "'GPIO HET Dir A", "'GPIO HET DIn A", "'GPIO HET DOut A", "'FPGA Status[0]", "'FPGA Status[1]",
                "'IOBC Exception[0]", "'IOBC Exception[1]", "'IOBC Exception[2]", "'IOBC Exception[3]"]

    @staticmethod
    def get_columns_6():
        return ["'EulerAngleErrors Data[0]", "'EulerAngleErrors Data[1]", "'EulerAngleErrors Data[2]",
                "'EulerAngleErrors Length", "'Mode In", "'Mode In", "'Mode Out", "'Mode Out", "'StateVector Data[0]",
                "'StateVector Data[1]", "'StateVector Data[2]", "'StateVector Data[3]", "'StateVector Data[4]",
                "'StateVector Data[5]", "'StateVector Data[6]", "'StateVector Length", "'Chosen FSS",
                "'Current FFS Data[0]", "'Current FFS Data[1]", "'Current FFS Data[2]", "'Current FFS Data[3]",
                "'Current FFS Data[4]", "'Current FFS Data[5]", "'Current FFS Data[6]", "'Cycle Counter", "'Gamma",
                "'Useable FSS Data[0]", "'Useable FSS Data[1]", "'Useable FSS Data[2]", "'Useable FSS Data[3]",
                "'Useable FSS Data[4]", "'Useable FSS Data[5]", "'Useable_FSS Length", "'Active Sensors Data[0]",
                "'Active Sensors Data[1]", "'Active Sensors Data[2]", "'Active Sensors Data[3]",
                "'Active Sensors Length", "'Hold Transition", "'StatePkp1p Data[0]", "'StatePkp1p Data[1]",
                "'StatePkp1p Data[2]", "'StatePkp1p Data[3]", "'StatePkp1p Data[4]", "'StatePkp1p Data[5]",
                "'StatePkp1p Data[6]", "'StatePkp1p Length"]

    @staticmethod
    def get_columns_7():
        return ["'ACS Cycle Count", "'ACS Cycle Timeout Count", "'ACS Cycle OASYS Count", "'ACS State",
                "'ACS SubState[0]", "'ACS SubState[1]", "'ACS SubState[2]", "'ACS SubState[3]", "'ACS SubState[4]",
                "'ACS SubState[5]", "'ACS SubState[6]", "'ACS SubState[7]", "'ACS SubState[8]", "'ACS SubState[9]",
                "'ACS Error Code", "'ACS Device Config Mask", "'SS CoarseVoltage 0(V)", "'SS Exposure Time 0(ms)",
                "'SS CoarseVoltage 1(V)", "'SS Exposure Time 1(ms)", "'SS CoarseVoltage 2(V)",
                "'SS Exposure Time 2(ms)", "'SS CoarseVoltage 3(V)", "'SS Exposure Time 3(ms)",
                "'SS CoarseVoltage 4(V)", "'SS Exposure Time 4(ms)", "'SS CoarseVoltage 5(V)",
                "'SS Exposure Time 5(ms)", "'Wheel Speed[0](rad/s)", "'Wheel Speed[1](rad/s)", "'Wheel Speed[2](rad/s)",
                "'Magnetometer X", "'Magnetometer Y", "'Magnetometer Z", "'Magnetometer Temperature(°C)",
                "'Rate Sensor X", "'Rate Sensor Y", "'Rate Sensor Z", "'Rate Sensor Temperature(°C)"]

    @staticmethod
    def get_columns_8():
        return ["'Error Code", "'Telemetry WheelSpeed Value[0]", "'Telemetry WheelSpeed Value[1]",
                "'Telemetry WheelSpeed Value[2]", "'Telemetry WheelSpeed Length", "'EKFMon Mag Iterations",
                "'EKFMon Mag Residual Value[0]", "'EKFMon Mag Residual Value[1]", "'EKFMon Mag Residual Value[2]",
                "'EKFMon Mag Residual Length", "'EKFMon Mag Trace P", "'EKFMon Fss Iterations",
                "'EKFMon Fss Residual Value[0]", "'EKFMon Fss Residual Value[1]", "'EKFMon Fss Residual Value[2]",
                "'EKFMon Fss Residual Value[3]", "'EKFMon Fss Residual Value[4]", "'EKFMon Fss Residual Value[5]",
                "'EKFMon Fss Residual Length", "'EKFMon Fss Trace P", "'EKFMon RTS Iterations",
                "'EKFMon RTS Residual Value[0]", "'EKFMon RTS Residual Value[1]", "'EKFMon RTS Residual Value[2]",
                "'EKFMon RTS Residual Length"]

    @staticmethod
    def get_columns_9():
        return ["'Reset Count File", "'Reset Reason File", "'Comm Err Count File", "'Scrub Index File",
                "'SEU Count File", "'Init Pointer File", "'Ping Pointer File", "'ADC Raw1 File", "'ADC Raw2 File",
                "'ADC Raw3 File", "'ADC Raw4 File", "'PWM Setting File", "'PWM Period File",
                "'PWM Controller Pointer File", "'PWM Controller Cycle File", "'PWM DCycle1 File", "'PWM DCycle2 File",
                "'PWM DCycle3 File", "'PWM DCycle4 File", "'Converted Temp1 File(°C)", "'Converted Temp2 File(°C)",
                "'Converted Temp3 File(°C)", "'Converted Temp4 File(°C)", "'Controller P Gain File",
                "'Controller I Gain File", "'Controller D Gain File", "'Controller I Max File",
                "'Controller Max DT File", "'Controller SetPoint File", "'Controller I State File"]

    def confirm_and_plot(self, window, column_listbox, plot_type_var):
        selected_indices = column_listbox.curselection()
        selected_columns = [column_listbox.get(i) for i in selected_indices]

        if not selected_columns:
            messagebox.showerror("Error", "No columns selected for plotting.")
            return

        window.destroy()

        plots = Plots()
        plots.plot(self.parsed_data, selected_columns, plot_type_var)

    def update_plot_columns_list_safe(self):
        if self.root:
            self.root.after(0, self.update_plot_columns_list)

    def update_plot_columns_list(self):
        for widget in self.plot_column_scrollable_frame.winfo_children():
            widget.destroy()
        self.plot_column_checkboxes = {}
        if self.parsed_data is not None and not self.parsed_data.empty:
            for col in self.parsed_data.columns[3:]:
                var = tk.BooleanVar(value=False)
                chk = ctk.CTkCheckBox(self.plot_column_scrollable_frame, text=col, variable=var)
                chk.pack(fill="x", pady=1)
                self.plot_column_checkboxes[col] = var

    def plot_selected_columns(self):
        selected_columns = [col for col, var in self.plot_column_checkboxes.items() if var.get()]

        if not selected_columns:
            messagebox.showerror("Error", "No columns selected for plotting.")
            return

        # Przekazanie odpowiedniego typu plotowania
        plot_type_var = self.plot_type_var.get()
        plots = Plots()
        plots.plot(self.parsed_data, selected_columns, plot_type_var)

    def plot_type_changed(self):
        current_plot_type = self.plot_type_var.get()
        print(f"Plot type changed to: {current_plot_type}")

    def setup_plot_options(self):
        # Ramka dla opcji wykresu
        self.plot_options_frame = ctk.CTkFrame(self.right_frame)
        self.plot_options_frame.pack(pady=10, fill='x', expand=False)

        # Tytuł sekcji
        plot_options_label = ctk.CTkLabel(self.plot_options_frame, text="Plot Type Options", font=("Arial", 12, "bold"))
        plot_options_label.pack(pady=(10, 5))

        # Przyciski radio dla wyboru typu wykresu
        linear_button = ctk.CTkRadioButton(self.plot_options_frame, text="Linear", variable=self.plot_type_var,
                                           value="linear", command=self.plot_type_changed)
        linear_button.pack(side="left", padx=15, pady=10)

        logarithmic_button = ctk.CTkRadioButton(self.plot_options_frame, text="Logarithmic",
                                                variable=self.plot_type_var, value="logarithmic",
                                                command=self.plot_type_changed)
        logarithmic_button.pack(side="left", padx=0, pady=10)

        self.plot_options_frame.configure(fg_color="transparent")
        self.plot_options_frame.configure(bg_color="transparent")

    def terminate_app(self):
        self.root.destroy()


    def create_tooltip(self, widget, text):
        tooltip = ToolTip(widget)
        widget.bind('<Enter>', lambda e: tooltip.show_tip(text))
        widget.bind('<Leave>', lambda e: tooltip.hide_tip())

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    print(f"app starting")
    root = tk.Tk()
    app = App(root)
    root.mainloop()
