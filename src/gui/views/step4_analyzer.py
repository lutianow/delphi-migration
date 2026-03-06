import customtkinter as ctk
import os
import threading
from tkinter import messagebox
from src.gui.components import SectionHeader, StyledButton
from src.gui.theme import COLOR_PRIMARY, COLOR_SECONDARY, BG_INPUT, BG_MAIN
from src.core.analyzer import ProjectAnalyzer

class Step4AnalyzerView(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self._ = controller._
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header_label = SectionHeader(self, text=self._("step_4", default="4. Pre-Migration Analyzer"), size="large")
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        self.analyzer_action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.analyzer_action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.analyzer_action_frame.grid_columnconfigure(1, weight=1)

        # Main call to action button
        self.btn_run_analyzer = ctk.CTkButton(
            self.analyzer_action_frame, 
            text=self._("btn_run_analyzer", default="Run Impact Analysis"), 
            command=self._run_analyzer, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            fg_color=COLOR_PRIMARY, 
            text_color=BG_MAIN, 
            hover_color="#E5E5E5", 
            corner_radius=16, 
            height=40
        )
        self.btn_run_analyzer.pack(side="left")

        self.analyzer_console_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.analyzer_console_frame.grid(row=2, column=0, sticky="nsew")
        self.analyzer_console_frame.grid_rowconfigure(0, weight=1)
        self.analyzer_console_frame.grid_columnconfigure(0, weight=1)

        self.analyzer_log_textbox = ctk.CTkTextbox(
            self.analyzer_console_frame, 
            fg_color="#101014", 
            text_color="#A4A4B5", 
            corner_radius=12, 
            font=ctk.CTkFont(family="Consolas", size=13), 
            border_width=2, 
            border_color="#2A2A35"
        )
        self.analyzer_log_textbox.grid(row=0, column=0, sticky="nsew")
        self.analyzer_log_textbox.insert("end", "Click 'Run Impact Analysis' to parse the source project and generate estimations.\n")
        self.analyzer_log_textbox.configure(state="disabled")

        # Step Navigation Row (Bottom)
        self.step_nav = ctk.CTkFrame(self, fg_color="transparent")
        self.step_nav.grid(row=3, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev = StyledButton(self.step_nav, text=self._("btn_prev", default="Previous Step"), command=lambda: self.controller.show_step(3), style_type="ghost")
        self.btn_prev.pack(side="left")
        
        self.btn_next = ctk.CTkButton(
            self.step_nav, 
            text=self._("btn_next", default="Next Step"), 
            command=lambda: self.controller.show_step(5), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            fg_color=COLOR_PRIMARY, 
            text_color=BG_MAIN, 
            hover_color="#E5E5E5", 
            corner_radius=16, 
            height=40, 
            width=200
        )
        self.btn_next.pack(side="right")

    def _run_analyzer(self):
        src_path = self.controller.source_dir.get()
        if not src_path or not os.path.exists(src_path):
            messagebox.showerror("Error", self._("msg_bad_source", default="Origin folder does not exist."))
            return
            
        self.analyzer_log_textbox.configure(state="normal")
        self.analyzer_log_textbox.delete("1.0", "end")
        self.btn_run_analyzer.configure(state="disabled", text="Analyzing...")
        self.update()
        
        def analyzer_worker():
            def ui_log(msg):
                self.analyzer_log_textbox.insert("end", msg + "\n")
                self.analyzer_log_textbox.yview_moveto(1.0)
            
            analyzer = ProjectAnalyzer(src_path, ui_log)
            analyzer.run_analysis()
            
            # Re-enable button
            self.controller.ui_queue.put(self._enable_analyzer_btn)
            
        self.controller.analyzer_thread = threading.Thread(target=analyzer_worker, daemon=True)
        self.controller.analyzer_thread.start()

    def _enable_analyzer_btn(self):
        self.btn_run_analyzer.configure(state="normal", text=self._("btn_run_analyzer", default="Run Impact Analysis"))
        self.analyzer_log_textbox.configure(state="disabled")

    def update_texts(self):
        self._ = self.controller._
        self.header_label.configure(text=self._("step_4", default="4. Pre-Migration Analyzer"))
        self.btn_run_analyzer.configure(text=self._("btn_run_analyzer", default="Run Impact Analysis"))
        self.btn_prev.configure(text=self._("btn_prev", default="Previous Step"))
        self.btn_next.configure(text=self._("btn_next", default="Next Step"))
