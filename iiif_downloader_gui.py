import iiif_downloader
import logging
from tkinter import Tk, Menu, Toplevel, StringVar, IntVar
from tkinter import ttk
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmsgbox


class GUI:
    def __init__(self, window):
        # Custom styles
        ttk.Style().configure("TRadiobutton", padding=(0, 0, 10, 0))
        ttk.Style().configure("WithEntry.TRadiobutton", padding=(0, 0, 5, 0))
        ttk.Style().configure("TCheckbutton", padding=(0, 0, 5, 0))
        ttk.Style().configure("TButton", margins=(10, 0, 10, 0))

        # Window
        self.window = window
        self.window.title("IIIF Downloader")
        self.window.resizable(True, False)  # block vertical resizing
        self.window.bind("<Return>", self.bindEnter)  # bind Return key to run
        # TODO change default window icon

        # Menu
        self.menu = Menu(self.window)
        self.window.configure(menu=self.menu)
        menu2 = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Help', menu=menu2)
        menu2.add_command(label='About', command=self.about)

        frame = ttk.Frame(master=self.window)
        frame.columnconfigure(index=1, weight=1)

        # Manifest
        self.manifest_radio = StringVar()
        self.manifest_url = StringVar()
        self.manifest_url.trace_add('write', self.checkAntenati)
        self.manifest_file = StringVar()

        lbl_manifest = ttk.Label(master=frame, text="Manifest path")
        lbl_manifest.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        manifest_frame = ttk.Frame(master=frame)
        manifest_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        manifest_frame.columnconfigure(index=1, weight=1)

        self.ent_manifest_url = ttk.Entry(
            master=manifest_frame, textvariable=self.manifest_url)
        self.ent_manifest_file = ttk.Entry(
            master=manifest_frame, textvariable=self.manifest_file)
        self.btn2_manifest = ttk.Button(
            master=manifest_frame, text='Browse', command=self.browse_manifest)
        btn_manifest_url = ttk.Radiobutton(
            master=manifest_frame, text="URL", variable=self.manifest_radio,
            value="url", command=self.enableManifestURLEntry,
            style="WithEntry.TRadiobutton")
        btn_manifest_url.invoke()  # url radio button set by default
        btn_manifest_url.grid(row=0, column=0, sticky="w")
        self.ent_manifest_url.grid(row=0, column=1, columnspan=2, sticky="ew")
        btn_manifest_file = ttk.Radiobutton(
            master=manifest_frame, text="File", variable=self.manifest_radio,
            value="file", command=self.enableManifestFileEntry)
        btn_manifest_file.grid(row=1, column=0, sticky="w")
        self.ent_manifest_file.grid(row=1, column=1, sticky="ew")
        self.btn2_manifest.grid(row=1, column=2, padx=(5, 0))

        # Output folder
        self.path = StringVar()

        lbl_path = ttk.Label(master=frame, text="Destination folder")
        lbl_path.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        path_frame = ttk.Frame(master=frame)
        path_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        path_frame.columnconfigure(index=0, weight=1)

        ent_path = ttk.Entry(master=path_frame, textvariable=self.path)
        btn_browse = ttk.Button(
            master=path_frame, text='Browse', command=self.browse_path)
        ent_path.grid(row=0, column=0, sticky="ew")
        btn_browse.grid(row=0, column=1, padx=(5, 0))

        # Pages
        self.pages_radio = StringVar()
        self.pages_range = StringVar()

        lbl_pages = ttk.Label(master=frame, text="Pages")
        lbl_pages.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        pages_frame = ttk.Frame(master=frame)
        pages_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ent_pages = ttk.Entry(
            master=pages_frame, textvariable=self.pages_range, width=5)
        btn_all_pages = ttk.Radiobutton(
            master=pages_frame, text="All", variable=self.pages_radio,
            value="all", command=lambda: self.disableEntry(ent_pages))
        btn_all_pages.invoke()  # all pages button set by default
        btn_range_pages = ttk.Radiobutton(
            master=pages_frame, text="Range", variable=self.pages_radio,
            value="range", command=lambda: self.enableEntry(ent_pages),
            style="WithEntry.TRadiobutton")
        btn_all_pages.pack(side="left")
        btn_range_pages.pack(side="left")
        ent_pages.pack(side="left")

        # Width
        self.width_radio = StringVar()
        self.custom_width = StringVar()

        lbl_width = ttk.Label(master=frame, text="Images width")
        lbl_width.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        width_frame = ttk.Frame(master=frame)
        width_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        ent_width = ttk.Entry(
            master=width_frame, textvariable=self.custom_width, width=5)
        btn_highest_width = ttk.Radiobutton(
            master=width_frame, text="Highest", variable=self.width_radio,
            value="highest", command=lambda: self.disableEntry(ent_width))
        btn_highest_width.invoke()  # highest width button set by default
        btn_host_width = ttk.Radiobutton(
            master=width_frame, text="Website-defined",
            variable=self.width_radio, value="host",
            command=lambda: self.disableEntry(ent_width))
        btn_custom_width = ttk.Radiobutton(
            master=width_frame, text="Custom", variable=self.width_radio,
            value="custom", command=lambda: self.enableEntry(ent_width),
            style="WithEntry.TRadiobutton")
        btn_highest_width.pack(side="left")
        btn_host_width.pack(side="left")
        btn_custom_width.pack(side="left")
        ent_width.pack(side="left")

        # Threads
        self.threads = StringVar(value=1)

        lbl_threads = ttk.Label(master=frame, text="Threads (max: 64)")
        lbl_threads.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        box_threads = ttk.Spinbox(
            master=frame, from_=1, to=64, textvariable=self.threads, width=5)
        vcmd_threads = (frame.register(self.validateThreads), "%P")
        box_threads.config(validate="key", validatecommand=vcmd_threads)
        box_threads.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Referer
        self.referer_radio = StringVar()
        self.referer = StringVar()

        lbl_referer = ttk.Label(master=frame, text="HTTP referer")
        lbl_referer.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        referer_frame = ttk.Frame(master=frame)
        referer_frame.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        ent_referer = ttk.Entry(
            master=referer_frame, textvariable=self.referer)
        self.btn_default_referer = ttk.Radiobutton(
            master=referer_frame, text="Default", variable=self.referer_radio,
            value="default", command=lambda: self.disableEntry(ent_referer))
        self.btn_default_referer.invoke()  # all pages button set by default
        self.btn_custom_referer = ttk.Radiobutton(
            master=referer_frame, text="Custom", variable=self.referer_radio,
            value="custom", command=lambda: self.enableEntry(ent_referer),
            style="WithEntry.TRadiobutton")
        self.btn_default_referer.pack(side="left")
        self.btn_custom_referer.pack(side="left")
        ent_referer.pack(fill="x")

        # Overwrite check button
        self.force = IntVar()

        cbtn_force = ttk.Checkbutton(
            master=frame, variable=self.force, onvalue=1, offvalue=0,
            text="Overwrite existing files")
        cbtn_force.grid(
            row=7, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Use labels check button
        self.uselabels = IntVar()

        cbtn_uselabels = ttk.Checkbutton(
            master=frame, variable=self.uselabels, onvalue=1, offvalue=0,
            text="Use manifest labels as file names")
        cbtn_uselabels.grid(
            row=8, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # All images check button
        self.allimages = IntVar()

        cbtn_allimages = ttk.Checkbutton(
            master=frame, variable=self.allimages, onvalue=1, offvalue=0,
            text="Download all files in multiple files canvases")
        cbtn_allimages.grid(
            row=9, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Log file check button
        self.log = IntVar()
        self.log_file = StringVar(value="iiif_downloader.log")

        log_frame = ttk.Frame(master=frame)
        log_frame.grid(
            row=10, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.cbtn_log = ttk.Checkbutton(
            master=log_frame, variable=self.log, onvalue=1, offvalue=0,
            text="Save log file", command=self.enableLogEntry)
        self.ent_log = ttk.Entry(master=log_frame, textvariable=self.log_file)
        self.ent_log.config(state="disabled")
        self.cbtn_log.pack(side="left")
        self.ent_log.pack(fill="x")

        # Download button
        btn_download = ttk.Button(
            master=frame, text="Download document", command=self.run)
        btn_download.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

        # Pack the frame in the window, as small as possible, responsive on x
        frame.pack(fill="x")

    def about(self):
        txt = "IIIF Downloader v1.0.0\n"
        txt += "Copyright (C) 2025 Claudio Martino\n"
        txt += "github.com/ClaudioMartino/IIIF-Downloader"
        new_window = Toplevel()
        new_window.title("About")
        new_window.resizable(False, False)
        ttk.Label(new_window, text=txt).pack(padx=10, pady=5)

    def browse_path(self):
        selected_path = tkfile.askdirectory()
        if selected_path:
            self.path.set(selected_path)

    def browse_manifest(self):
        filepath = tkfile.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filepath:
            self.manifest_file.set(filepath)

    def enableManifestURLEntry(self):
        self.ent_manifest_url.configure(state="normal")
        self.ent_manifest_url.update()
        self.ent_manifest_file.configure(state="disabled")
        self.ent_manifest_file.update()
        self.btn2_manifest.config(state="disabled")

    def enableManifestFileEntry(self):
        self.ent_manifest_file.configure(state="normal")
        self.ent_manifest_file.update()
        self.ent_manifest_url.configure(state="disabled")
        self.ent_manifest_url.update()
        self.btn2_manifest.config(state="normal")

    def checkAntenati(self, var, index, mode):
        if("dam-antenati.cultura.gov.it" in self.manifest_url.get()):
            self.btn_custom_referer.invoke()
            self.referer.set("https://antenati.cultura.gov.it/")
        else:
            self.btn_default_referer.invoke()
            self.referer.set("")

    def enableEntry(self, entry):
        entry.configure(state="normal")
        entry.update()

    def disableEntry(self, entry):
        entry.configure(state="disabled")
        entry.update()

    def enableLogEntry(self):
        if (self.log.get() == 1):
            self.ent_log.config(state="normal")
            self.ent_log.update()
        elif (self.log.get() == 0):
            self.ent_log.config(state="disabled")
            self.ent_log.update()

    def validateThreads(self, user_input):
        if (user_input.isdigit()):
            if int(user_input) not in range(1, 64+1):
                return False
            return True
        elif (user_input == ""):
            # We accept temporarily an emtpy string and check later
            return True
        else:
            return False

    def bindEnter(self, event):
        self.run()

    def run(self):
        try:
            # Read all values
            manifest_radio = self.manifest_radio.get()
            manifest_url = self.manifest_url.get()
            manifest_file = self.manifest_file.get()

            path_value = self.path.get()

            pages_radio_value = self.pages_radio.get()
            pages_range_value = self.pages_range.get()

            force_value = bool(self.force.get())
            uselabels_value = bool(self.uselabels.get())
            allimages_value = bool(self.allimages.get())

            referer_radio_value = self.referer_radio.get()
            referer_value = self.referer.get()

            width_radio_value = self.width_radio.get()
            custom_width_value = self.custom_width.get()

            threads_value = self.threads.get()

            log_value = bool(self.log.get())
            log_file_value = self.log_file.get()

            # Check values
            manifest = ""
            if (manifest_radio == "url"):
                if (iiif_downloader.is_url(manifest_url)):
                    manifest = manifest_url
                else:
                    raise Exception('Please enter a valid manifest URL.')
            elif (manifest_radio == "file"):
                manifest = manifest_file
            if (len(manifest) == 0):
                raise Exception('Please enter a manifest.')

            if (len(path_value) == 0):
                raise Exception('Please enter a destination folder.')

            pages_range = ""
            if (pages_radio_value == "all"):
                pages_range = "all"
            elif (pages_radio_value == "range"):
                pages_range = pages_range_value
            firstpage, lastpage = iiif_downloader.get_pages(pages_range)

            width = 0
            if (width_radio_value == "host"):
                width = None
            elif (width_radio_value == "custom"):
                if (custom_width_value.isdigit()):
                    width = int(custom_width_value)
                else:
                    raise Exception('Please enter a valid width.')

            threads = 1
            if (threads_value == ""):
                raise Exception('Please enter a thread number.')
            else:
                threads = int(threads_value)

            referer = None
            if (referer_radio_value == "custom"):
                if (len(referer_value) == 0):
                    raise Exception('Please enter an HTTP referer.')
                elif (not iiif_downloader.is_url(referer_value)):
                    raise Exception('Please enter a valid HTTP referer.')
                else:
                    referer = referer_value

            rootLogger = logging.getLogger()
            rootLogger.setLevel(logging.DEBUG)
            rootLogger.handlers.clear()  # delete all previous handlers
            logFormatter = logging.Formatter("%(message)s")
            # When the root logger has no handlers, basicConfig() is called.
            # We might as well create a StreamHandler for the console.
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            consoleHandler.setLevel(logging.DEBUG)
            rootLogger.addHandler(consoleHandler)
            if (log_value):
                if (len(log_file_value) == 0):
                    raise Exception('Please enter a valid log file name.')
                else:
                    fileHandler = logging.FileHandler(
                        path_value + "/" + log_file_value)
                    fileHandler.setFormatter(logFormatter)
                    fileHandler.setLevel(logging.DEBUG)
                    rootLogger.addHandler(fileHandler)

            # Create downloader and run
            downloader = iiif_downloader.IIIF_Downloader()

            downloader.json_file = manifest
            downloader.maindir = path_value
            downloader.firstpage = firstpage
            downloader.lastpage = lastpage
            downloader.force = force_value
            downloader.use_labels = uselabels_value
            downloader.all_images = allimages_value
            downloader.referer = referer
            downloader.num_threads = threads
            downloader.width = width  # -w not used: 0; -w without arg: None

            downloader.pages.clear()  # clear page list
            downloader.run()

        except Exception as e:
            tkmsgbox.showwarning(title="Error", message="Error", detail=str(e))


if __name__ == '__main__':
    window = Tk()
    gui = GUI(window)

    window.mainloop()
