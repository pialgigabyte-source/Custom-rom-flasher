import customtkinter as ctk
import subprocess
import threading
import time
import re
import os
import sys
import platform
from tkinter import filedialog, messagebox

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADB_FOLDER = os.path.join(BASE_DIR, 'adb')
FILES_DIR = os.path.join(BASE_DIR, 'files')
os.makedirs(FILES_DIR, exist_ok=True)

IS_WINDOWS = platform.system() == 'Windows'
adb_name = 'adb.exe' if IS_WINDOWS else 'adb'
fb_name = 'fastboot.exe' if IS_WINDOWS else 'fastboot'
dumper_name = 'payload-dumper-go.exe' if IS_WINDOWS else 'payload-dumper-go'

ADB_EXE = os.path.join(ADB_FOLDER, adb_name)
FB_EXE = os.path.join(ADB_FOLDER, fb_name)
DUMPER_EXE = os.path.join(ADB_FOLDER, dumper_name)

if not IS_WINDOWS:
    try:
        os.chmod(ADB_EXE, 0o755)
        os.chmod(FB_EXE, 0o755)
        os.chmod(DUMPER_EXE, 0o755)
    except Exception:
        pass


def get_sub_kwargs():
    kwargs = {}
    if IS_WINDOWS:
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs['startupinfo'] = startup
    return kwargs


BG_DARK = '#0D1117'
CARD_BG = '#161B22'
BORDER_SHADOW = '#21262D'
ACCENT_TEAL = '#2DD4BF'
ACCENT_PURPLE = '#8B5CF6'
ACCENT_SUCCESS = '#2ECC71'
ACCENT_WARNING = '#F59E0B'
ACCENT_DANGER = '#EF4444'
TEXT_DIM = '#8B949E'
TEXT_WHITE = '#FFFFFF'
CONSOLE_BG = '#010409'
FONT_MAIN = 'Segoe UI'


class ProfessionalFlasher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('ROM Flasher Pro | Developed by Raphael 8s_G4')
        self.geometry('1100x800')
        self.configure(fg_color=BG_DARK)

        self.current_mode = None
        self.selected_file = ''
        self.k_selected_file = ''
        self.angle = 90
        self.k_angle = 90
        self.is_flashing = False
        self.k_is_flashing = False
        self.abort_requested = False
        self.anim_offset = 0
        self.k_anim_offset = 0
        self.active_tab_name = None
        self.current_anim = None

        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.setup_navigation()

        self.main_container = ctk.CTkFrame(self, fg_color='transparent')
        self.main_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))

        self.setup_flasher_tab()
        self.setup_kernel_tab()
        self.setup_logs_tab()

        self.show_tab('ROM')

        self.log('System Initialized. Listening for device connections...')
        if not os.path.exists(DUMPER_EXE):
            self.log('[WARNING] payload-dumper-go not found in adb folder! Extraction will fail.')

        self.after(100, self.auto_check)
        self.animate_loader()
        self.animate_k_loader()

    def on_closing(self):
        if self.is_flashing or self.k_is_flashing:
            messagebox.showwarning(
                'Flashing in Progress',
                "WARNING: A flashing process is currently running!\n\n"
                "Please wait for it to complete or use the 'STOP FLASHING' button before exiting to prevent bricking your device."
            )
            return
        try:
            subprocess.run(f'"{ADB_EXE}" kill-server', shell=True, **get_sub_kwargs())
        except Exception:
            pass
        self.destroy()
        sys.exit(0)

    def _ui(self, func):
        """Schedule a UI-mutating callable to run on the main/Tk thread.

        CustomTkinter/Tkinter widgets are not thread-safe. Background worker
        threads (flash_worker, kernel_worker, _erase_worker) must never touch
        widgets directly; this marshals the call onto the Tk event loop.
        """
        self.after(0, func)

    def setup_navigation(self):
        self.nav = ctk.CTkFrame(self, fg_color='transparent', height=60)
        self.nav.pack(fill='x', padx=30, pady=(20, 10))

        ctk.CTkLabel(
            self.nav, text='🚀 MULTI FLASHER',
            font=(FONT_MAIN, 18, 'bold'), text_color=TEXT_WHITE
        ).pack(side='left')

        self.tab_btns = {}
        self.tab_container = ctk.CTkFrame(self.nav, fg_color='transparent')
        self.tab_container.pack(side='right')

        tab_names = ['ROM', 'KERNEL', 'LOGS']
        for i, name in enumerate(tab_names):
            btn = ctk.CTkButton(
                self.tab_container, text=name, width=100, height=35,
                fg_color='transparent', text_color=TEXT_DIM,
                font=(FONT_MAIN, 13, 'bold'), hover_color=CARD_BG,
                command=lambda n=name: self.show_tab(n)
            )
            btn.grid(row=0, column=i, padx=5)
            self.tab_btns[name] = btn

    def show_tab(self, name):
        if self.active_tab_name == name:
            return

        for n, btn in self.tab_btns.items():
            btn.configure(text_color=ACCENT_TEAL if n == name else TEXT_DIM)

        self.active_tab_name = name

        self.f_tab.place_forget()
        self.k_tab.place_forget()
        self.logs_frame.place_forget()

        if name == 'ROM':
            target_frame = self.f_tab
        elif name == 'KERNEL':
            target_frame = self.k_tab
        else:
            target_frame = self.logs_frame

        if self.current_anim:
            self.after_cancel(self.current_anim)

        self.anim_y = 0.1
        self.animate_tab_transition(target_frame)

    def animate_tab_transition(self, frame):
        if self.anim_y > 0.001:
            frame.place(relx=0, rely=self.anim_y, relwidth=1.0, relheight=1.0)
            self.anim_y -= self.anim_y * 0.2
            self.current_anim = self.after(10, lambda: self.animate_tab_transition(frame))
        else:
            frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            self.current_anim = None

    def get_battery_level(self):
        try:
            out = subprocess.check_output(
                f'"{ADB_EXE}" shell dumpsys battery',
                shell=True, stderr=subprocess.STDOUT, text=True, **get_sub_kwargs()
            )
            match = re.search('level:\\s+(\\d+)', out)
            if match:
                return f'{match.group(1)}%'
        except Exception:
            pass
        return None

    def update_phone_icon(self, canvas, connected, flashing=False, offset=0, active_color=ACCENT_TEAL):
        color = active_color if connected else TEXT_DIM
        canvas.delete('all')

        canvas.create_rectangle(18, 8, 72, 112, outline=color, width=3)

        x1, y1, x2, y2 = (21, 11, 46, 50)
        r = 7
        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style='arc', outline=color, width=2)
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style='arc', outline=color, width=2)
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style='arc', outline=color, width=2)
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style='arc', outline=color, width=2)
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=color, width=2)
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=color, width=2)
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=color, width=2)
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=color, width=2)

        canvas.create_oval(28, 18, 39, 29, outline=color, width=2)
        canvas.create_oval(28, 32, 39, 43, outline=color, width=2)

        if connected:
            canvas.create_line(24, 31, 43, 26, fill=ACCENT_SUCCESS, width=3)
        else:
            canvas.create_line(24, 31, 43, 26, fill=color, width=2)

        canvas.create_oval(51, 22, 54, 30, outline=color, width=2)

        canvas.create_line(18, 37, 18, 52, fill=color, width=3)
        canvas.create_line(18, 60, 18, 67, fill=color, width=3)

        canvas.create_rectangle(40, 112, 50, 120, fill=color, outline='')
        canvas.create_rectangle(36, 120, 54, 135, outline=color, width=3)
        canvas.create_line(45, 135, 45, 150, fill=color, width=3)

        if flashing:
            for i in (0, 15):
                dot_y = 150 - (offset * 1.5 + i) % 30
                if 120 < dot_y < 150:
                    canvas.create_oval(42, dot_y - 3, 48, dot_y + 3, fill=TEXT_WHITE, outline='')

            scan_y = 8 + offset / 20.0 * 104
            canvas.create_line(18, scan_y, 72, scan_y, fill=TEXT_WHITE, width=2)

    def setup_flasher_tab(self):
        self.f_tab = ctk.CTkFrame(self.main_container, fg_color='transparent')
        self.f_tab.grid_columnconfigure(0, weight=4)
        self.f_tab.grid_columnconfigure(1, weight=5)
        self.f_tab.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self.f_tab, fg_color='transparent')
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))

        self.dev_card = ctk.CTkFrame(self.left_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.dev_card.pack(fill='x', pady=(0, 20), ipady=15)

        ctk.CTkLabel(self.dev_card, text='DEVICE STATUS', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM).pack(anchor='w', padx=20, pady=10)

        self.status_lbl = ctk.CTkLabel(self.dev_card, text='● Searching for devices...', font=(FONT_MAIN, 13, 'bold'), text_color=ACCENT_TEAL)
        self.status_lbl.pack(anchor='w', padx=20)

        self.batt_lbl = ctk.CTkLabel(self.dev_card, text='🔋 Battery: Unknown', font=(FONT_MAIN, 11, 'bold'), text_color=TEXT_DIM)
        self.batt_lbl.pack(anchor='w', padx=20)

        btn_row = ctk.CTkFrame(self.dev_card, fg_color='transparent')
        btn_row.pack(fill='x', padx=20, pady=(15, 0))

        self.reboot_btn = ctk.CTkButton(
            btn_row, text='Reboot to Bootloader', height=32, width=160,
            fg_color='transparent', border_width=1, border_color=ACCENT_TEAL,
            text_color=ACCENT_TEAL, hover_color='#1E293B',
            command=self.reboot_bl, state='disabled'
        )
        self.reboot_btn.pack(side='left', padx=(0, 10))

        ctk.CTkButton(
            btn_row, text='REFRESH', height=32, width=80,
            fg_color=ACCENT_PURPLE, text_color=TEXT_WHITE,
            font=(FONT_MAIN, 11, 'bold'), corner_radius=8,
            command=self.check_devices
        ).pack(side='left')

        self.dev_phone_canvas = ctk.CTkCanvas(self.dev_card, width=90, height=150, bg=CARD_BG, highlightthickness=0)
        self.dev_phone_canvas.place(relx=0.82, rely=0.5, anchor='center')
        self.update_phone_icon(self.dev_phone_canvas, False)

        self.file_card = ctk.CTkFrame(self.left_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.file_card.pack(fill='x', pady=(0, 20))

        self.card_title = ctk.CTkLabel(self.file_card, text='SELECT ROM (.zip)', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM)
        self.card_title.pack(anchor='w', padx=20, pady=(15, 5))

        self.browse_btn = ctk.CTkButton(
            self.file_card, text='+ Browse', fg_color=ACCENT_TEAL, text_color=BG_DARK,
            height=45, corner_radius=12, font=(FONT_MAIN, 14, 'bold'), command=self.browse_file
        )
        self.browse_btn.pack(fill='x', padx=20, pady=10)

        self.file_lbl = ctk.CTkLabel(self.file_card, text='No file selected.', font=(FONT_MAIN, 12), text_color=TEXT_DIM)
        self.file_lbl.pack(pady=5)

        self.parts_frame = ctk.CTkFrame(self.file_card, fg_color='transparent')
        self.parts_frame.pack(fill='x', padx=20, pady=(0, 15))

        ctk.CTkLabel(self.parts_frame, text='Fastboot Partitions to Flash:', font=(FONT_MAIN, 12, 'bold'), text_color=TEXT_DIM).pack(anchor='w')

        self.part_vars = {}
        parts_grid = ctk.CTkFrame(self.parts_frame, fg_color='transparent')
        parts_grid.pack(fill='x', pady=2)

        partitions_list = ['boot', 'init_boot', 'vendor_boot', 'dtbo', 'recovery']
        for i, p in enumerate(partitions_list):
            var = ctk.BooleanVar(value=True)
            self.part_vars[p] = var
            chk = ctk.CTkCheckBox(
                parts_grid, text=p, variable=var, font=(FONT_MAIN, 11),
                text_color=TEXT_WHITE, fg_color=ACCENT_TEAL, hover_color=ACCENT_SUCCESS,
                width=10, checkbox_height=16, checkbox_width=16
            )
            chk.grid(row=i // 3, column=i % 3, padx=(0, 12), pady=5, sticky='w')

        self.erase_card = ctk.CTkFrame(self.left_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.erase_card.pack(fill='both', expand=True)

        ctk.CTkLabel(self.erase_card, text='FASTBOOT COMMANDS', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM).pack(anchor='w', padx=20, pady=(15, 5))

        self.erase_row = ctk.CTkFrame(self.erase_card, fg_color='transparent')
        self.erase_row.pack(fill='x', padx=20, pady=(10, 5))

        self.btn_frp = ctk.CTkButton(
            self.erase_row, text='🗑️ Erase FRP', height=32, fg_color='#374151',
            text_color=TEXT_WHITE, font=(FONT_MAIN, 13, 'bold'), state='disabled',
            command=lambda: self.erase_partition('frp')
        )
        self.btn_frp.pack(side='left', padx=(0, 5), expand=True, fill='x')

        self.btn_meta = ctk.CTkButton(
            self.erase_row, text='🗑️ Erase Metadata', height=32, fg_color='#374151',
            text_color=TEXT_WHITE, font=(FONT_MAIN, 13, 'bold'), state='disabled',
            command=lambda: self.erase_partition('metadata')
        )
        self.btn_meta.pack(side='left', padx=(0, 5), expand=True, fill='x')

        self.btn_user = ctk.CTkButton(
            self.erase_row, text='🗑️ Erase Userdata', height=32, fg_color='#374151',
            text_color=TEXT_WHITE, font=(FONT_MAIN, 13, 'bold'), state='disabled',
            command=lambda: self.erase_partition('userdata')
        )
        self.btn_user.pack(side='left', expand=True, fill='x')

        ctk.CTkLabel(
            self.erase_card, text='⚠️ CAUTION: Destructive Actions',
            font=(FONT_MAIN, 12, 'bold'), text_color=ACCENT_WARNING
        ).pack(anchor='w', padx=20, pady=(5, 0))

        erase_info = (
            '• FRP: Removes Google Account Factory Reset Protection.\n'
            '• Metadata: Clears device encryption keys & boot state.\n'
            '• Userdata: Complete factory reset (Wipes internal storage).'
        )
        ctk.CTkLabel(
            self.erase_card, text=erase_info, font=(FONT_MAIN, 13),
            text_color=TEXT_DIM, justify='left'
        ).pack(anchor='w', padx=20, pady=(2, 15))

        self.right_frame = ctk.CTkFrame(self.f_tab, fg_color='transparent')
        self.right_frame.grid(row=0, column=1, sticky='nsew')

        self.auto_card = ctk.CTkFrame(self.right_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.auto_card.pack(fill='x', pady=(0, 20))

        ctk.CTkLabel(self.auto_card, text='AUTOMATED PROGRESS', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM).pack(anchor='w', padx=20, pady=15)

        self.canvas = ctk.CTkCanvas(self.auto_card, width=320, height=320, bg=CARD_BG, highlightthickness=0)
        self.canvas.pack(pady=20)
        self.draw_progress(0, 'Waiting')

        self.flash_btn = ctk.CTkButton(
            self.auto_card, text='▶ START AUTO FLASH', fg_color=ACCENT_TEAL, text_color=BG_DARK,
            width=250, height=55, corner_radius=28, font=(FONT_MAIN, 15, 'bold'),
            state='disabled', command=self.start_flash
        )
        self.flash_btn.pack(pady=20)

        self.setup_checklist()

    def setup_checklist(self):
        self.progress_card = ctk.CTkFrame(self.right_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.progress_card.pack(fill='both', expand=True)

        ctk.CTkLabel(self.progress_card, text='PROGRESS STATUS', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM).pack(anchor='w', padx=20, pady=(15, 5))

        self.check_frame = ctk.CTkScrollableFrame(self.progress_card, fg_color='transparent')
        self.check_frame.pack(fill='both', expand=True, padx=10, pady=(0, 25))

        self.chk_ext = ctk.CTkLabel(self.check_frame, text='○ Gathering Images', font=(FONT_MAIN, 15), text_color=TEXT_DIM)
        self.chk_ext.pack(anchor='w', padx=10, pady=2)

        self.chk_fb = ctk.CTkLabel(self.check_frame, text='○ Flash Fastboot Images', font=(FONT_MAIN, 15), text_color=TEXT_DIM)
        self.chk_fb.pack(anchor='w', padx=10, pady=2)

        self.sub_frame = ctk.CTkFrame(self.check_frame, fg_color='transparent', height=0)
        self.sub_frame.pack(fill='x', padx=(35, 0))

        self.sub_chks = {}

        self.chk_wait = ctk.CTkLabel(self.check_frame, text='○ Waiting for Sideload Mode', font=(FONT_MAIN, 15), text_color=TEXT_DIM)
        self.chk_wait.pack(anchor='w', padx=10, pady=2)

        self.chk_rom = ctk.CTkLabel(self.check_frame, text='○ Flashing ROM Sideload', font=(FONT_MAIN, 15), text_color=TEXT_DIM)
        self.chk_rom.pack(anchor='w', padx=10, pady=2)

        ctk.CTkLabel(
            self.progress_card, text='Developed by Raphael 8s_G4', font=(FONT_MAIN, 9),
            text_color=TEXT_DIM, fg_color='transparent'
        ).place(relx=0.96, rely=0.96, anchor='se')

    def update_checklist(self, step, status):
        color = {'waiting': TEXT_DIM, 'active': ACCENT_WARNING, 'success': ACCENT_SUCCESS, 'fail': ACCENT_DANGER}[status]
        icon = {'waiting': '○', 'active': '▶', 'success': '✓', 'fail': '✗'}[status]

        labels = {1: self.chk_ext, 2: self.chk_fb, 3: self.chk_wait, 4: self.chk_rom}

        if step in labels:
            text = labels[step].cget('text')[2:]
            labels[step].configure(text=f'{icon} {text}', text_color=color)

    def update_sub_chk(self, p, status):
        color = {'waiting': TEXT_DIM, 'active': ACCENT_WARNING, 'success': ACCENT_SUCCESS, 'fail': ACCENT_DANGER, 'skip': '#4B5563'}[status]
        icon = {'waiting': '-', 'active': '▶', 'success': '✓', 'fail': '✗', 'skip': '○'}[status]

        if p in self.sub_chks:
            self.sub_chks[p].configure(text=f'{icon} {p}', text_color=color)

    def reset_checklists(self):
        for i in range(1, 5):
            self.update_checklist(i, 'waiting')
        for p in self.sub_chks.keys():
            self.update_sub_chk(p, 'waiting')

    def setup_kernel_tab(self):
        self.k_tab = ctk.CTkFrame(self.main_container, fg_color='transparent')
        self.k_tab.grid_columnconfigure(0, weight=4)
        self.k_tab.grid_columnconfigure(1, weight=5)
        self.k_tab.grid_rowconfigure(0, weight=1)

        self.k_left_frame = ctk.CTkFrame(self.k_tab, fg_color='transparent')
        self.k_left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))

        self.k_dev_card = ctk.CTkFrame(self.k_left_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.k_dev_card.pack(fill='x', pady=(0, 20), ipady=15)

        ctk.CTkLabel(self.k_dev_card, text='DEVICE STATUS', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM).pack(anchor='w', padx=20, pady=10)

        self.k_status_lbl = ctk.CTkLabel(self.k_dev_card, text='● Searching for devices...', font=(FONT_MAIN, 13, 'bold'), text_color=ACCENT_PURPLE)
        self.k_status_lbl.pack(anchor='w', padx=20)

        self.k_batt_lbl = ctk.CTkLabel(self.k_dev_card, text='🔋 Battery: Unknown', font=(FONT_MAIN, 11, 'bold'), text_color=TEXT_DIM)
        self.k_batt_lbl.pack(anchor='w', padx=20)

        k_btn_row = ctk.CTkFrame(self.k_dev_card, fg_color='transparent')
        k_btn_row.pack(fill='x', padx=20, pady=(15, 0))

        self.k_reboot_btn = ctk.CTkButton(
            k_btn_row, text='Reboot to Recovery', height=32, width=160,
            fg_color='transparent', border_width=1, border_color=ACCENT_PURPLE,
            text_color=ACCENT_PURPLE, hover_color='#1E293B',
            command=self.k_reboot_action, state='disabled'
        )
        self.k_reboot_btn.pack(side='left', padx=(0, 10))

        ctk.CTkButton(
            k_btn_row, text='REFRESH', height=32, width=80,
            fg_color=ACCENT_TEAL, text_color=BG_DARK,
            font=(FONT_MAIN, 11, 'bold'), corner_radius=8,
            command=self.check_devices
        ).pack(side='left')

        self.k_dev_phone_canvas = ctk.CTkCanvas(self.k_dev_card, width=90, height=150, bg=CARD_BG, highlightthickness=0)
        self.k_dev_phone_canvas.place(relx=0.82, rely=0.5, anchor='center')
        self.update_phone_icon(self.k_dev_phone_canvas, False, active_color=ACCENT_PURPLE)

        self.k_file_card = ctk.CTkFrame(self.k_left_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.k_file_card.pack(fill='x', pady=(0, 20))

        self.k_card_title = ctk.CTkLabel(self.k_file_card, text='FILE SELECTION (DISABLED)', font=(FONT_MAIN, 11, 'bold'), text_color=TEXT_DIM)
        self.k_card_title.pack(anchor='w', padx=20, pady=(15, 5))

        self.k_browse_btn = ctk.CTkButton(
            self.k_file_card, text='+ Browse', fg_color='#374151', text_color=TEXT_WHITE,
            height=45, corner_radius=12, font=(FONT_MAIN, 14, 'bold'), state='disabled',
            command=self.browse_kernel
        )
        self.k_browse_btn.pack(fill='x', padx=20, pady=10)

        self.k_file_lbl = ctk.CTkLabel(self.k_file_card, text='Connect device to select file.', font=(FONT_MAIN, 12), text_color=TEXT_DIM)
        self.k_file_lbl.pack(pady=5)

        self.setup_k_checklist()

        k_right_card = ctk.CTkFrame(self.k_tab, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        k_right_card.grid(row=0, column=1, sticky='nsew')

        ctk.CTkLabel(k_right_card, text='KERNEL PROGRESS', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM).pack(anchor='w', padx=20, pady=15)

        self.k_canvas = ctk.CTkCanvas(k_right_card, width=320, height=320, bg=CARD_BG, highlightthickness=0)
        self.k_canvas.pack(pady=20)
        self.draw_k_progress(0, 'Waiting')

        self.k_flash_btn = ctk.CTkButton(
            k_right_card, text='⚡ FLASH KERNEL', fg_color=ACCENT_PURPLE, text_color=TEXT_WHITE,
            width=250, height=55, corner_radius=28, font=(FONT_MAIN, 15, 'bold'),
            state='disabled', command=self.start_kernel_flash
        )
        self.k_flash_btn.pack(pady=20)

        ctk.CTkLabel(
            k_right_card, text='Developed by Raphael 8s_G4', font=(FONT_MAIN, 9),
            text_color=TEXT_DIM, fg_color='transparent'
        ).place(relx=0.97, rely=0.97, anchor='se')

    def setup_k_checklist(self):
        self.k_progress_card = ctk.CTkFrame(self.k_left_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.k_progress_card.pack(fill='both', expand=True)

        ctk.CTkLabel(self.k_progress_card, text='PROGRESS STATUS', font=(FONT_MAIN, 14, 'bold'), text_color=TEXT_DIM).pack(anchor='w', padx=20, pady=(15, 5))

        self.k_check_frame = ctk.CTkScrollableFrame(self.k_progress_card, fg_color='transparent')
        self.k_check_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.chk_k_rec = ctk.CTkLabel(self.k_check_frame, text='○ Reboot to Recovery', font=(FONT_MAIN, 16), text_color=TEXT_DIM)
        self.chk_k_rec.pack(anchor='w', padx=10, pady=3)

        self.chk_k_flash = ctk.CTkLabel(self.k_check_frame, text='○ Flashing Kernel', font=(FONT_MAIN, 16), text_color=TEXT_DIM)
        self.chk_k_flash.pack(anchor='w', padx=10, pady=3)

    def update_k_checklist(self, step, status):
        color = {'waiting': TEXT_DIM, 'success': ACCENT_SUCCESS, 'fail': ACCENT_DANGER}[status]
        icon = {'waiting': '○', 'success': '✓', 'fail': '✗'}[status]

        if step == 1:
            self.chk_k_rec.configure(text=f'{icon} Reboot to Recovery', text_color=color)
            return
        elif step == 2:
            self.chk_k_flash.configure(text=f'{icon} Flashing Kernel', text_color=color)
            return

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[('ROM Zip', '*.zip')])
        if path:
            self.selected_file = path
            filename = os.path.basename(path)

            if self.current_mode == 'fastboot':
                self.flash_btn.configure(state='normal')
                self.file_lbl.configure(text=f'{filename}\nReady to flash.', text_color=ACCENT_SUCCESS)
            else:
                self.file_lbl.configure(text=f'{filename}\nReboot to Fastboot to enable Start button.', text_color=ACCENT_WARNING)

            self.log(f'[*] ROM File loaded: {filename}')

    def browse_kernel(self):
        path = filedialog.askopenfilename(filetypes=[('Kernel Zip', '*.zip')])
        if path:
            self.k_selected_file = path
            filename = os.path.basename(path)
            self.k_file_lbl.configure(text=filename, text_color=TEXT_WHITE)

            if self.current_mode == 'sideload':
                self.k_flash_btn.configure(state='normal')

            self.log(f'[*] Kernel File loaded: {filename}')

    def draw_progress(self, percent, subtext):
        self.canvas.delete('all')
        self.canvas.create_oval(40, 40, 280, 280, outline=BORDER_SHADOW, width=12)

        extent = -(percent / 100) * 360 if percent > 0 else 0
        if percent > 0:
            self.canvas.create_arc(40, 40, 280, 280, outline=ACCENT_TEAL, width=12, style='arc', start=90, extent=extent)

        self.canvas.create_text(160, 140, text=f'{int(percent)}%', fill=TEXT_WHITE, font=(FONT_MAIN, 42, 'bold'))
        if subtext:
            self.canvas.create_text(160, 190, text=subtext, fill=TEXT_DIM, font=(FONT_MAIN, 12))

    def draw_k_progress(self, percent, subtext):
        self.k_canvas.delete('all')
        self.k_canvas.create_oval(40, 40, 280, 280, outline=BORDER_SHADOW, width=12)

        extent = -(percent / 100) * 360 if percent > 0 else 0
        if percent > 0:
            self.k_canvas.create_arc(40, 40, 280, 280, outline=ACCENT_PURPLE, width=12, style='arc', start=90, extent=extent)

        self.k_canvas.create_text(160, 140, text=f'{int(percent)}%', fill=TEXT_WHITE, font=(FONT_MAIN, 42, 'bold'))
        if subtext:
            self.k_canvas.create_text(160, 190, text=subtext, fill=TEXT_DIM, font=(FONT_MAIN, 12))

    def animate_loader(self):
        if self.is_flashing:
            self.canvas.delete('arc_loader')
            self.canvas.create_arc(
                40, 40, 280, 280, outline=ACCENT_TEAL, width=12, style='arc',
                start=self.angle, extent=90, tags='arc_loader'
            )
            self.angle = (self.angle + 8) % 360
            self.anim_offset = (self.anim_offset + 1) % 20
            self.update_phone_icon(self.dev_phone_canvas, True, flashing=True, offset=self.anim_offset, active_color=ACCENT_TEAL)

        self.after(30, self.animate_loader)

    def animate_k_loader(self):
        if self.k_is_flashing:
            self.k_canvas.delete('arc_loader')
            self.k_canvas.create_arc(
                40, 40, 280, 280, outline=ACCENT_PURPLE, width=12, style='arc',
                start=self.k_angle, extent=90, tags='arc_loader'
            )
            self.k_angle = (self.k_angle + 8) % 360
            self.k_anim_offset = (self.k_anim_offset + 1) % 20
            self.update_phone_icon(self.k_dev_phone_canvas, True, flashing=True, offset=self.k_anim_offset, active_color=ACCENT_PURPLE)

        self.after(30, self.animate_k_loader)

    def trigger_abort(self):
        if self.is_flashing:
            self.abort_requested = True
            self.log('[!] STOP REQUESTED! Aborting sequence safely...')
            self.reboot_btn.configure(state='disabled', text='Stopping...', text_color=TEXT_DIM, border_color=TEXT_DIM)

    def erase_partition(self, partition):
        self.log(f'[*] Command issued: fastboot erase {partition}')
        threading.Thread(target=self._erase_worker, args=(partition,), daemon=True).start()

    def _erase_worker(self, partition):
        # Runs on a background thread; all UI touches go through self._ui().
        try:
            res = subprocess.run(
                f'"{FB_EXE}" erase {partition}', shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **get_sub_kwargs()
            )
            self._ui(lambda: self.log(res.stdout))
            if res.returncode == 0:
                self._ui(lambda: self.log(f"[*] Successfully erased '{partition}'."))
            else:
                self._ui(lambda: self.log(f"[!] Failed to erase '{partition}'. Check connection."))
        except Exception as e:
            # `e` is cleared by Python as soon as the except block exits, so
            # it must be captured as a default arg, not read lazily inside
            # the deferred lambda (which runs later on the Tk event loop).
            self._ui(lambda e=e: self.log(f'[!] Critical Error during fastboot erase: {str(e)}'))

    def check_devices(self):
        try:
            adb = subprocess.check_output(
                f'"{ADB_EXE}" devices', shell=True, stderr=subprocess.STDOUT, **get_sub_kwargs()
            ).decode()
            fb = subprocess.check_output(
                f'"{FB_EXE}" devices', shell=True, stderr=subprocess.STDOUT, **get_sub_kwargs()
            ).decode()

            if 'sideload' in adb:
                return 'sideload'
            adb_lines = adb.split('\n')
            if len(adb_lines) > 1 and 'device' in adb_lines[1]:
                return 'adb'
            if fb.strip():
                return 'fastboot'
        except Exception:
            pass
        return None

    def auto_check(self):
        mode = self.check_devices()

        if self.is_flashing or self.k_is_flashing:
            if mode == 'sideload' and self.current_mode != 'sideload':
                self.current_mode = 'sideload'
                self.status_lbl.configure(text='● Status: SIDELOAD Mode Active', text_color=ACCENT_SUCCESS)
                self.k_status_lbl.configure(text='● Status: SIDELOAD Mode Active', text_color=ACCENT_SUCCESS)
                self.log('[Device Connected] Detected mode: SIDELOAD')
            self.after(2000, self.auto_check)
            return

        if mode != self.current_mode:
            if mode:
                self.status_lbl.configure(text=f'● Status: {mode.upper()} Mode Active', text_color=ACCENT_SUCCESS)
                self.k_status_lbl.configure(text=f'● Status: {mode.upper()} Mode Active', text_color=ACCENT_SUCCESS)
                self.log(f'[Device Connected] Detected mode: {mode.upper()}')

                self.update_phone_icon(self.dev_phone_canvas, True, active_color=ACCENT_TEAL)
                self.update_phone_icon(self.k_dev_phone_canvas, True, active_color=ACCENT_PURPLE)

                if mode == 'adb':
                    batt = self.get_battery_level()
                    batt_txt = f'🔋 Battery: {batt}' if batt else '🔋 Battery: Unknown'
                    self.batt_lbl.configure(text=batt_txt, text_color=ACCENT_SUCCESS if batt else TEXT_DIM)
                    self.k_batt_lbl.configure(text=batt_txt, text_color=ACCENT_SUCCESS if batt else TEXT_DIM)

                    self.reboot_btn.configure(text='Reboot to Bootloader', state='normal', text_color=ACCENT_TEAL, border_color=ACCENT_TEAL, command=self.reboot_bl)
                    self.k_reboot_btn.configure(text='Reboot to Recovery', state='normal', text_color=ACCENT_PURPLE, border_color=ACCENT_PURPLE, command=self.k_reboot_action)

                    self.k_card_title.configure(text='FILE SELECTION (DISABLED)')
                    self.k_browse_btn.configure(state='disabled', fg_color='#374151')

                    self.btn_frp.configure(state='disabled', fg_color='#374151')
                    self.btn_meta.configure(state='disabled', fg_color='#374151')
                    self.btn_user.configure(state='disabled', fg_color='#374151')

                    if self.selected_file:
                        self.file_lbl.configure(text=f'{os.path.basename(self.selected_file)}\nReboot to Fastboot to start.', text_color=ACCENT_WARNING)
                    else:
                        self.file_lbl.configure(text='No file selected.', text_color=TEXT_DIM)

                    # Flashing requires fastboot mode; disable the flash button
                    # whenever the device is back in ADB mode so a stale
                    # "normal" state from a previous fastboot session can't be
                    # clicked here.
                    self.flash_btn.configure(state='disabled')

                    if self.k_selected_file:
                        self.k_file_lbl.configure(text=f'{os.path.basename(self.k_selected_file)}\nReboot to Recovery & enable Sideload.', text_color=ACCENT_WARNING)
                    else:
                        self.k_file_lbl.configure(text='Please reboot to Recovery & enable Sideload.', text_color=TEXT_DIM)
                else:
                    self.batt_lbl.configure(text='🔋 Battery: N/A (Recovery/Fastboot)', text_color=TEXT_DIM)
                    self.k_batt_lbl.configure(text='🔋 Battery: N/A (Recovery/Fastboot)', text_color=TEXT_DIM)

                if mode == 'fastboot':
                    self.reboot_btn.configure(text='Reboot to Recovery', state='normal', text_color=ACCENT_TEAL, border_color=ACCENT_TEAL, command=self.reboot_bl)
                    self.k_reboot_btn.configure(text='Reboot to Recovery', state='normal', text_color=ACCENT_PURPLE, border_color=ACCENT_PURPLE, command=self.k_reboot_action)

                    self.k_card_title.configure(text='FILE SELECTION (DISABLED)')
                    self.k_browse_btn.configure(state='disabled', fg_color='#374151')

                    if not self.is_flashing:
                        self.btn_frp.configure(state='normal', fg_color=ACCENT_DANGER)
                        self.btn_meta.configure(state='normal', fg_color=ACCENT_DANGER)
                        self.btn_user.configure(state='normal', fg_color=ACCENT_DANGER)

                    if self.k_selected_file:
                        self.k_file_lbl.configure(text=f'{os.path.basename(self.k_selected_file)}\nReboot to Recovery & enable Sideload.', text_color=ACCENT_WARNING)
                    else:
                        self.k_file_lbl.configure(text='Please reboot to Recovery & enable Sideload.', text_color=TEXT_DIM)

                    if self.selected_file:
                        self.flash_btn.configure(state='normal')
                        self.file_lbl.configure(text=f'{os.path.basename(self.selected_file)}\nReady to flash.', text_color=ACCENT_SUCCESS)
                    else:
                        self.file_lbl.configure(text='No file selected.', text_color=TEXT_DIM)

                if mode == 'sideload':
                    self.reboot_btn.configure(text='Reboot Disabled', state='disabled', text_color=TEXT_DIM, border_color=TEXT_DIM)
                    self.k_reboot_btn.configure(text='Reboot Disabled', state='disabled', text_color=TEXT_DIM, border_color=TEXT_DIM)

                    self.k_card_title.configure(text='SELECT KERNEL (.zip)')
                    self.k_browse_btn.configure(state='normal', fg_color=ACCENT_PURPLE)

                    self.btn_frp.configure(state='disabled', fg_color='#374151')
                    self.btn_meta.configure(state='disabled', fg_color='#374151')
                    self.btn_user.configure(state='disabled', fg_color='#374151')

                    if self.selected_file:
                        self.file_lbl.configure(text=os.path.basename(self.selected_file), text_color=TEXT_WHITE)
                    else:
                        self.file_lbl.configure(text='No file selected.', text_color=TEXT_DIM)

                    if self.k_selected_file:
                        self.k_file_lbl.configure(text=os.path.basename(self.k_selected_file), text_color=TEXT_WHITE)
                        self.k_flash_btn.configure(state='normal')
                    else:
                        self.k_file_lbl.configure(text='Select custom kernel to flash.', text_color=TEXT_DIM)

                    self.update_k_checklist(1, 'success')
            else:
                self.status_lbl.configure(text='● Status: Searching for devices...', text_color=ACCENT_TEAL)
                self.k_status_lbl.configure(text='● Status: Searching for devices...', text_color=ACCENT_PURPLE)
                self.batt_lbl.configure(text='🔋 Battery: Unknown', text_color=TEXT_DIM)
                self.k_batt_lbl.configure(text='🔋 Battery: Unknown', text_color=TEXT_DIM)

                self.update_phone_icon(self.dev_phone_canvas, False, active_color=ACCENT_TEAL)
                self.update_phone_icon(self.k_dev_phone_canvas, False, active_color=ACCENT_PURPLE)

                self.flash_btn.configure(state='disabled')
                self.k_flash_btn.configure(state='disabled')

                self.k_card_title.configure(text='FILE SELECTION (DISABLED)')
                self.k_browse_btn.configure(state='disabled', fg_color='#374151')

                self.reboot_btn.configure(state='disabled', text='Reboot to Bootloader', text_color=ACCENT_TEAL, border_color=ACCENT_TEAL)
                self.k_reboot_btn.configure(state='disabled', text='Reboot to Recovery', text_color=ACCENT_PURPLE, border_color=ACCENT_PURPLE)

                self.btn_frp.configure(state='disabled', fg_color='#374151')
                self.btn_meta.configure(state='disabled', fg_color='#374151')
                self.btn_user.configure(state='disabled', fg_color='#374151')

                if self.selected_file:
                    self.file_lbl.configure(text=f'{os.path.basename(self.selected_file)}\nConnect device to begin.', text_color=TEXT_DIM)
                else:
                    self.file_lbl.configure(text='No file selected.', text_color=TEXT_DIM)

                if self.k_selected_file:
                    self.k_file_lbl.configure(text=f'{os.path.basename(self.k_selected_file)}\nConnect device to begin.', text_color=TEXT_DIM)
                else:
                    self.k_file_lbl.configure(text='Connect device to select file.', text_color=TEXT_DIM)

                if self.current_mode is not None:
                    self.log('[Device Disconnected] Waiting for connection...')
                    if self.current_mode != 'sideload' or self.is_flashing:
                        self.update_k_checklist(1, 'waiting')
                        self.update_k_checklist(2, 'waiting')

            self.current_mode = mode

        self.after(2000, self.auto_check)

    def reboot_bl(self):
        self.log(f"[*] Sending reboot command from {self.current_mode.upper() if self.current_mode else 'UNKNOWN'} mode...")

        cmd = f'"{ADB_EXE}" reboot bootloader'
        if self.current_mode == 'fastboot':
            cmd = f'"{FB_EXE}" reboot recovery'
        elif self.current_mode == 'sideload':
            cmd = f'"{ADB_EXE}" reboot bootloader'

        subprocess.run(cmd, shell=True, **get_sub_kwargs())

    def k_reboot_action(self):
        self.log(f"[*] Sending reboot command from {self.current_mode.upper() if self.current_mode else 'UNKNOWN'} mode...")

        cmd = f'"{ADB_EXE}" reboot recovery'
        if self.current_mode == 'fastboot':
            cmd = f'"{FB_EXE}" reboot recovery'
        elif self.current_mode == 'sideload':
            cmd = f'"{ADB_EXE}" reboot system'

        subprocess.run(cmd, shell=True, **get_sub_kwargs())

    def start_flash(self):
        for lbl in self.sub_chks.values():
            lbl.destroy()
        self.sub_chks.clear()

        selected_parts = [p for p, var in self.part_vars.items() if var.get()]

        for p in selected_parts:
            lbl = ctk.CTkLabel(self.sub_frame, text=f'- {p}', font=(FONT_MAIN, 12), text_color=TEXT_DIM)
            lbl.pack(anchor='w', pady=0)
            self.sub_chks[p] = lbl

        self.reset_checklists()
        self.is_flashing = True
        self.abort_requested = False

        self.flash_btn.configure(state='disabled')
        self.browse_btn.configure(state='disabled')
        self.file_lbl.configure(text=os.path.basename(self.selected_file), text_color=ACCENT_SUCCESS)

        for var in self.part_vars.values():
            var.set(var.get())

        self.btn_frp.configure(state='disabled', fg_color='#374151')
        self.btn_meta.configure(state='disabled', fg_color='#374151')
        self.btn_user.configure(state='disabled', fg_color='#374151')

        self.reboot_btn.configure(state='normal', text='■ STOP FLASHING', text_color=ACCENT_DANGER, border_color=ACCENT_DANGER, command=self.trigger_abort)

        self.log(f'\n[*] AUTO SEQUENCE INITIATED: {os.path.basename(self.selected_file)}')

        threading.Thread(target=self.flash_worker, args=(selected_parts,), daemon=True).start()

    def flash_worker(self, selected_parts):
        # Runs on a background thread; all UI touches go through self._ui().
        # `selected_parts` is passed in from start_flash (computed on the main
        # thread) rather than re-read from the CTkCheckBox BooleanVars here,
        # since Tkinter variables are not safe to read from a worker thread.
        try:
            if not selected_parts:
                self._ui(lambda: self.log('[*] No fastboot partitions selected. Skipping extraction & fastboot flash stages.'))
                self._ui(lambda: self.update_checklist(1, 'success'))
                self._ui(lambda: self.update_checklist(2, 'success'))
            else:
                self._ui(lambda: self.update_checklist(1, 'active'))
                self._ui(lambda: self.log(f"[*] Extracting dynamically selected partitions: {', '.join(selected_parts)}"))
                self._ui(lambda: self.draw_progress(15, 'Gathering Imgs...'))

                dump_cmd = f'"{DUMPER_EXE}" -p {",".join(selected_parts)} -o "{FILES_DIR}" "{self.selected_file}"'

                process = subprocess.Popen(dump_cmd, shell=True, **get_sub_kwargs())
                while process.poll() is None:
                    if self.abort_requested:
                        process.terminate()
                        self._ui(self.abort_flash)
                        return
                    time.sleep(0.5)

                if process.returncode != 0 and not self.abort_requested:
                    self._ui(lambda: self.log('[!] Payload dumper failed. Check if executable exists and is valid.'))
                    self._ui(lambda: self.update_checklist(1, 'fail'))
                    self._ui(self.abort_flash)
                    return

                self._ui(lambda: self.update_checklist(1, 'success'))

                self._ui(lambda: self.update_checklist(2, 'active'))
                self._ui(lambda: self.draw_progress(30, 'Fastboot Flash...'))

                for p in selected_parts:
                    if self.abort_requested:
                        self._ui(self.abort_flash)
                        return

                    img_path = os.path.join(FILES_DIR, f'{p}.img')
                    if os.path.exists(img_path):
                        self._ui(lambda p=p: self.log(f'[*] Flashing {p}...'))
                        self._ui(lambda p=p: self.update_sub_chk(p, 'active'))

                        res = subprocess.run(f'"{FB_EXE}" flash {p} "{img_path}"', shell=True, **get_sub_kwargs())

                        if res.returncode != 0:
                            self._ui(lambda p=p: self.log(f'[!] Failed to flash {p}. Aborting.'))
                            self._ui(lambda: self.update_checklist(2, 'fail'))
                            self._ui(lambda p=p: self.update_sub_chk(p, 'fail'))
                            self._ui(self.abort_flash)
                            return

                        self._ui(lambda p=p: self.update_sub_chk(p, 'success'))
                    else:
                        self._ui(lambda p=p: self.log(f'[*] Skipping {p} (Not found in payload)'))
                        self._ui(lambda p=p: self.update_sub_chk(p, 'skip'))

                if self.abort_requested:
                    self._ui(self.abort_flash)
                    return

                self._ui(lambda: self.update_checklist(2, 'success'))
                self._ui(lambda: self.log('[*] Fastboot flashing complete. Rebooting to Recovery...'))
                subprocess.run(f'"{FB_EXE}" reboot recovery', shell=True, **get_sub_kwargs())

            self._ui(lambda: self.update_checklist(3, 'active'))
            self._ui(lambda: self.draw_progress(45, 'Waiting User...'))
            self._ui(lambda: self.log('\n============================================='))
            self._ui(lambda: self.log('ACTION REQUIRED ON DEVICE:'))
            self._ui(lambda: self.log("1. Navigate to Wipe > Format Data > type 'yes'"))
            self._ui(lambda: self.log('2. Navigate to Apply Update > Apply from ADB'))
            self._ui(lambda: self.log('=============================================\n'))
            self._ui(lambda: self.log('[*] Waiting for device to enter Sideload mode...'))

            while self.current_mode != 'sideload':
                if not self.is_flashing or self.abort_requested:
                    self._ui(self.abort_flash)
                    return
                time.sleep(2)

            self._ui(lambda: self.update_checklist(3, 'success'))

            self._ui(lambda: self.update_checklist(4, 'active'))
            self._ui(lambda: self.reboot_btn.configure(state='disabled', text='Reboot Disabled', text_color=TEXT_DIM, border_color=TEXT_DIM))

            self._ui(lambda: self.log(f'[*] Executing: adb sideload {os.path.basename(self.selected_file)}'))

            process = subprocess.Popen(
                f'"{ADB_EXE}" sideload "{self.selected_file}"', shell=True,
                stdout=subprocess.PIPE, text=True, **get_sub_kwargs()
            )

            rom_current_pct = 50
            last_pct = 0

            for line in process.stdout:
                self._ui(lambda line=line: self.log(line.strip()))
                match = re.search('(\\d+)%', line)
                if not match:
                    continue

                pct = int(match.group(1))
                last_pct = pct
                target_pct = 50 + min(int(pct / 46 * 50), 50)

                while rom_current_pct < target_pct:
                    rom_current_pct += 1
                    self._ui(lambda v=rom_current_pct: self.draw_progress(v, 'Sideloading...'))
                    time.sleep(0.02)

            process.wait()

            if process.returncode == 0:
                if last_pct < 47:
                    self._ui(lambda: self.log(f"serving: '{self.selected_file}' (~47%)"))

                while rom_current_pct < 100:
                    rom_current_pct += 1
                    self._ui(lambda v=rom_current_pct: self.draw_progress(v, 'Finishing...'))
                    time.sleep(0.01)

                self._ui(lambda: self.draw_progress(100, 'ROM Installed!'))
                self._ui(lambda: self.update_checklist(4, 'success'))
                self._ui(lambda: self.log('\n[*] ======================================='))
                self._ui(lambda: self.log('[*] AUTO SEQUENCE COMPLETE SUCCESSFULLY.'))
                self._ui(lambda: self.log('[*] ======================================='))

                for f in os.listdir(FILES_DIR):
                    os.remove(os.path.join(FILES_DIR, f))
            else:
                self._ui(lambda: self.draw_progress(0, 'Flash Failed'))
                self._ui(lambda: self.update_checklist(4, 'fail'))
                self._ui(lambda: self.log('[!] Sideload execution failed.'))

            self._ui(self.finish_flash)
        except Exception as e:
            # `e` is cleared by Python as soon as the except block exits, so
            # it must be captured as a default arg, not read lazily inside
            # the deferred lambda (which runs later on the Tk event loop).
            self._ui(lambda e=e: self.log(f'[!] Critical Error during sequence: {str(e)}'))
            self._ui(self.abort_flash)

    def abort_flash(self):
        self.draw_progress(0, 'Aborted')
        self.finish_flash()

    def finish_flash(self):
        self.is_flashing = False
        self.abort_requested = False

        self.update_phone_icon(self.dev_phone_canvas, True, active_color=ACCENT_TEAL)
        self.browse_btn.configure(state='normal')

        self.reboot_btn.configure(text_color=ACCENT_TEAL, border_color=ACCENT_TEAL, command=self.reboot_bl)

        if self.current_mode == 'sideload':
            self.reboot_btn.configure(text='Reboot Disabled', state='disabled', text_color=TEXT_DIM, border_color=TEXT_DIM)
            return
        elif self.current_mode == 'fastboot':
            self.reboot_btn.configure(text='Reboot to Recovery', state='normal')
            self.btn_frp.configure(state='normal', fg_color=ACCENT_DANGER)
            self.btn_meta.configure(state='normal', fg_color=ACCENT_DANGER)
            self.btn_user.configure(state='normal', fg_color=ACCENT_DANGER)

            if self.selected_file:
                self.flash_btn.configure(state='normal')

    def start_kernel_flash(self):
        self.k_is_flashing = True
        self.k_flash_btn.configure(state='disabled')
        self.k_browse_btn.configure(state='disabled')
        self.k_reboot_btn.configure(state='disabled')
        self.k_file_lbl.configure(text=os.path.basename(self.k_selected_file), text_color=ACCENT_SUCCESS)

        self.log(f'[*] Kernel Flashing sequence started for {os.path.basename(self.k_selected_file)}')

        threading.Thread(target=self.kernel_worker, daemon=True).start()

    def kernel_worker(self):
        # Runs on a background thread; all UI touches go through self._ui().
        self._ui(lambda: self.log(f'Flashing custom kernel via ADB sideload: {self.k_selected_file}'))

        process = subprocess.Popen(
            f'"{ADB_EXE}" sideload "{self.k_selected_file}"', shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **get_sub_kwargs()
        )

        self.k_current_pct = 0
        last_pct = 0

        for line in process.stdout:
            self._ui(lambda line=line: self.log(line.strip()))
            match = re.search('(\\d+)%', line)
            if not match:
                continue

            pct = int(match.group(1))
            last_pct = pct
            target_pct = min(int(pct / 46 * 100), 100)

            while self.k_current_pct < target_pct:
                self.k_current_pct += 1
                self._ui(lambda v=self.k_current_pct: self.draw_k_progress(v, 'Installing Kernel...'))
                time.sleep(0.02)

        process.wait()

        self._ui(lambda: self.log('========================================================='))
        self._ui(lambda: self.log(' ADB sideload command finished.'))
        self._ui(lambda: self.log('========================================================='))

        if process.returncode != 0:
            self._ui(lambda: self.log('ERROR: Flashing failed! Check recovery screen and USB cable.'))
            self._ui(lambda: self.draw_k_progress(0, 'Flash Failed'))
            self._ui(lambda: self.update_k_checklist(2, 'fail'))
        else:
            if last_pct < 47:
                self._ui(lambda: self.log(f"serving: '{self.k_selected_file}' (~47%)"))

            while self.k_current_pct < 100:
                self.k_current_pct += 1
                self._ui(lambda v=self.k_current_pct: self.draw_k_progress(v, 'Finishing...'))
                time.sleep(0.01)

            self._ui(lambda: self.log('Flash completed successfully. Device remains in recovery.'))
            self._ui(lambda: self.draw_k_progress(100, 'Kernel Installed'))
            self._ui(lambda: self.update_k_checklist(2, 'success'))

        self.k_is_flashing = False
        self._ui(lambda: self.update_phone_icon(self.k_dev_phone_canvas, True, active_color=ACCENT_PURPLE))
        self._ui(lambda: self.k_flash_btn.configure(state='normal'))
        self._ui(lambda: self.k_browse_btn.configure(state='normal'))

    def setup_logs_tab(self):
        self.logs_frame = ctk.CTkFrame(self.main_container, fg_color='transparent')

        self.disc_frame = ctk.CTkFrame(self.logs_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER_SHADOW)
        self.disc_frame.pack(side='bottom', fill='x', pady=(20, 0), ipady=10)

        ctk.CTkLabel(
            self.disc_frame, text='⚠️ IMPORTANT DISCLAIMER & FLASHING INSTRUCTIONS',
            font=(FONT_MAIN, 13, 'bold'), text_color=ACCENT_DANGER
        ).pack(anchor='w', padx=20, pady=(15, 5))

        instructions = (
            "1. AUTO ROM FLASH: Boot into Fastboot Mode, browse your ROM (.zip) file and the flasher will flash everything from the zip.\n"
            "2. FORMAT DATA: Reboot to Recovery. Navigate to Wipe > Format Data > type 'yes'.\n"
            "3. SIDELOAD: In Recovery, navigate to Apply Update > Apply from ADB.\n"
            "4. KERNEL FLASH: Browse for your Kernel (.zip) file and click FLASH KERNEL.\n\n"
            "DO NOT disconnect your device or interrupt the tool while a flashing process is ongoing."
        )

        ctk.CTkLabel(
            self.disc_frame, text=instructions, font=(FONT_MAIN, 12),
            text_color=TEXT_DIM, justify='left'
        ).pack(anchor='w', padx=20, pady=(0, 10))

        ctk.CTkLabel(
            self.disc_frame, text='Developed by Raphael 8s_G4', font=(FONT_MAIN, 9),
            text_color=TEXT_DIM, fg_color='transparent'
        ).place(relx=0.98, rely=0.92, anchor='se')

        self.console = ctk.CTkTextbox(self.logs_frame, fg_color=CONSOLE_BG, text_color=ACCENT_TEAL, font=('Consolas', 13), corner_radius=15)
        self.console.pack(side='top', fill='both', expand=True, pady=(0, 0))

    def log(self, msg):
        self.console.insert('end', f'» {msg}\n')
        self.console.see('end')


if __name__ == '__main__':
    app = ProfessionalFlasher()
    app.mainloop()
