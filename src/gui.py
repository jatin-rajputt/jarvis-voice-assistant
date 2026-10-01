"""
Ironman JARVIS Futuristic GUI Interface.
Built with PyQt6 using custom QPainter vector graphics, dynamic Arc Reactor,
audio equalizer visualizer, system telemetry gauges, and cyber terminal.
"""

import sys
import math
import random
import datetime
import psutil
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, 
    QLinearGradient, QConicalGradient, QPainterPath
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar, QFrame,
    QGridLayout, QGraphicsDropShadowEffect
)

from jarvis_core import JarvisCore, OWNER_NAME, PROJECT_NAME

# ================= Color Palette =================
COLOR_BG = QColor(7, 11, 20)           # Deep Futuristic Dark
COLOR_PANEL_BG = "#0f172a"             # Translucent Card Dark
COLOR_CYAN = QColor(0, 240, 255)       # Standard Ironman HUD Cyan
COLOR_CYAN_STR = "#00f0ff"
COLOR_GOLD = QColor(255, 170, 0)       # Accent Gold
COLOR_GOLD_STR = "#ffaa00"
COLOR_GREEN = QColor(0, 255, 136)      # Active Listening Green
COLOR_GREEN_STR = "#00ff88"
COLOR_RED = QColor(255, 51, 102)       # PIN / Warning Crimson
COLOR_RED_STR = "#ff3366"


class ArcReactorWidget(QWidget):
    """
    Custom Vector-Painted Animated Ironman Arc Reactor Widget.
    Renders rotating tech rings, core energy pulses, and state-based color shifts.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        
        self.angle = 0.0
        self.counter_angle = 0.0
        self.pulse_phase = 0.0
        self.state = "IDLE"
        
        # 30 FPS Animation Loop
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(33)

    def set_state(self, state):
        self.state = state
        self.update()

    def update_animation(self):
        # Rotation speeds based on state
        speed = 1.5 if self.state == "PROCESSING" else 0.8
        self.angle = (self.angle + speed) % 360
        self.counter_angle = (self.counter_angle - (speed * 1.3)) % 360
        self.pulse_phase = (self.pulse_phase + 0.08) % (2 * math.pi)
        self.update()

    def get_theme_color(self):
        if self.state == "LISTENING":
            return COLOR_GREEN
        elif self.state == "PROCESSING":
            return COLOR_GOLD
        elif self.state == "SPEAKING":
            return QColor(220, 250, 255)
        elif self.state in ["PIN_VERIFICATION", "ERROR"]:
            return COLOR_RED
        return COLOR_CYAN

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2.0
        center_y = height / 2.0
        radius = min(width, height) / 2.0 - 15

        color = self.get_theme_color()

        # 1. Outer Glow Circle
        radial = QRadialGradient(center_x, center_y, radius * 1.1)
        c_outer = QColor(color)
        c_outer.setAlpha(40)
        c_transparent = QColor(color)
        c_transparent.setAlpha(0)
        radial.setColorAt(0.0, c_outer)
        radial.setColorAt(1.0, c_transparent)
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), radius * 1.1, radius * 1.1)

        # 2. Outer Rotating Segment Ring
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle)

        pen = QPen(QColor(color.red(), color.green(), color.blue(), 180), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        num_segments = 12
        seg_angle = 360.0 / num_segments
        for i in range(num_segments):
            start = i * seg_angle
            painter.drawArc(
                QRectF(-radius, -radius, radius * 2, radius * 2),
                int(start * 16), int((seg_angle - 10) * 16)
            )
        painter.restore()

        # 3. Inner Counter-Rotating Ring
        inner_r1 = radius * 0.75
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.counter_angle)

        pen_inner = QPen(QColor(color.red(), color.green(), color.blue(), 220), 3)
        painter.setPen(pen_inner)
        num_inner = 8
        inner_seg_angle = 360.0 / num_inner
        for i in range(num_inner):
            start = i * inner_seg_angle
            painter.drawArc(
                QRectF(-inner_r1, -inner_r1, inner_r1 * 2, inner_r1 * 2),
                int(start * 16), int((inner_seg_angle - 15) * 16)
            )
        painter.restore()

        # 4. Tech Tick Marks
        inner_r2 = radius * 0.55
        painter.save()
        painter.translate(center_x, center_y)
        pen_tick = QPen(QColor(color.red(), color.green(), color.blue(), 120), 1)
        painter.setPen(pen_tick)
        for i in range(36):
            angle_rad = math.radians(i * 10)
            x1 = inner_r2 * math.cos(angle_rad)
            y1 = inner_r2 * math.sin(angle_rad)
            x2 = (inner_r2 - 6) * math.cos(angle_rad)
            y2 = (inner_r2 - 6) * math.sin(angle_rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        painter.restore()

        # 5. Core Pulsing Reactor
        pulse = 0.85 + (0.15 * math.sin(self.pulse_phase))
        core_r = radius * 0.40 * pulse
        core_gradient = QRadialGradient(center_x, center_y, core_r)
        
        c_core_center = QColor(255, 255, 255, 255)
        c_core_mid = QColor(color.red(), color.green(), color.blue(), 200)
        c_core_edge = QColor(color.red(), color.green(), color.blue(), 80)
        
        core_gradient.setColorAt(0.0, c_core_center)
        core_gradient.setColorAt(0.5, c_core_mid)
        core_gradient.setColorAt(1.0, c_core_edge)
        
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 255), 2))
        painter.drawEllipse(QPointF(center_x, center_y), core_r, core_r)

        # 6. Central Triangle Overlay (Classic Ironman Arc Emblem)
        tri_r = core_r * 0.55
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle * 0.5)
        
        path = QPainterPath()
        for i in range(3):
            ang = math.radians(i * 120 - 90)
            tx = tri_r * math.cos(ang)
            ty = tri_r * math.sin(ang)
            if i == 0:
                path.moveTo(tx, ty)
            else:
                path.lineTo(tx, ty)
        path.closeSubpath()
        
        painter.setPen(QPen(QColor(0, 0, 0, 180), 2))
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 150)))
        painter.drawPath(path)
        painter.restore()


class SoundVisualizerWidget(QWidget):
    """
    Animated Audio Waveform Equalizer Widget.
    Simulates dynamic sound waves during voice input/output.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(45)
        self.num_bars = 20
        self.bars = [5] * self.num_bars
        self.state = "IDLE"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_wave)
        self.timer.start(50)

    def set_state(self, state):
        self.state = state
        self.update()

    def animate_wave(self):
        if self.state in ["LISTENING", "SPEAKING"]:
            self.bars = [random.randint(10, 38) for _ in range(self.num_bars)]
        elif self.state == "PROCESSING":
            self.bars = [random.randint(5, 20) for _ in range(self.num_bars)]
        else:
            # Idle smooth resting wave
            t = datetime.datetime.now().timestamp() * 4
            self.bars = [int(8 + 5 * math.sin(t + i * 0.4)) for i in range(self.num_bars)]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_w = (w - (self.num_bars * 4)) / self.num_bars

        for i, val in enumerate(self.bars):
            x = i * (bar_w + 4) + 2
            y = (h - val) / 2.0

            color = COLOR_GREEN if self.state == "LISTENING" else COLOR_CYAN
            if self.state == "SPEAKING":
                color = COLOR_GOLD

            gradient = QLinearGradient(x, y, x, y + val)
            c1 = QColor(color)
            c1.setAlpha(240)
            c2 = QColor(color)
            c2.setAlpha(80)
            gradient.setColorAt(0.0, c1)
            gradient.setColorAt(1.0, c2)

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_w, val), 2, 2)


# ================= Background Threads =================
class VoiceListenThread(QThread):
    signal_recognized = pyqtSignal(str)

    def __init__(self, jarvis_core):
        super().__init__()
        self.jarvis = jarvis_core

    def run(self):
        text = self.jarvis.listen_speech(timeout=5, phrase_time_limit=4)
        if text:
            self.signal_recognized.emit(text)


class CommandExecThread(QThread):
    signal_finished = pyqtSignal(str)

    def __init__(self, jarvis_core, command):
        super().__init__()
        self.jarvis = jarvis_core
        self.command = command

    def run(self):
        try:
            res = self.jarvis.process_command(self.command)
            self.signal_finished.emit(res or "DONE")
        except Exception as e:
            print(f"[Command Execution Exception Suppressed] {e}")
            try:
                self.jarvis.speak("An unexpected error occurred while processing your request.")
            except Exception:
                pass
            self.signal_finished.emit("ERROR")


class JarvisMainWindow(QMainWindow):
    """
    Main Ironman JARVIS GUI Window.
    Combines HUD Header, Central Arc Reactor, Sound Wave, Cyber Log, System Gauges, and Input Bar.
    """
    def __init__(self):
        super().__init__()
        self.jarvis = JarvisCore(log_callback=self.gui_log_callback, state_callback=self.gui_state_callback)
        
        self.setWindowTitle("JARVIS // STARK INDUSTRIES OS")
        self.resize(1020, 680)
        self.setMinimumSize(900, 600)
        
        self.init_ui()
        self.init_telemetry_timer()

        # Initial JARVIS welcome speech in background thread
        QThread.msleep(300)
        self.exec_thread = CommandExecThread(self.jarvis, "")
        # Welcome voice greeting
        QTimer.singleShot(500, self.say_welcome)

    def say_welcome(self):
        welcome_msg = f"Initializing Stark Industries Protocol. Jarvis online. Owner is {OWNER_NAME}."
        self.run_async_speech(welcome_msg)

    def init_ui(self):
        # Global Window Theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #070b14;
            }}
            QFrame {{
                background-color: {COLOR_PANEL_BG};
                border: 1px solid #1e293b;
                border-radius: 8px;
            }}
            QLabel {{
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLineEdit {{
                background-color: #020617;
                border: 1px solid {COLOR_CYAN_STR};
                border-radius: 6px;
                color: #ffffff;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', monospace;
            }}
            QPushButton {{
                background-color: #0f172a;
                color: {COLOR_CYAN_STR};
                border: 1px solid {COLOR_CYAN_STR};
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_CYAN_STR};
                color: #020617;
            }}
            QProgressBar {{
                background-color: #020617;
                border: 1px solid #334155;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_CYAN_STR};
                border-radius: 3px;
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ---------------- 1. Top HUD Header ----------------
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 8, 16, 8)

        lbl_title = QLabel("⚡ J.A.R.V.I.S // O7 SERVICES AI WORKSHOP")
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLOR_CYAN_STR}; letter-spacing: 2px;")

        self.lbl_status = QLabel("STATUS: STANDBY")
        self.lbl_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_GOLD_STR}; border: 1px solid {COLOR_GOLD_STR}; padding: 4px 10px; border-radius: 4px;")

        self.lbl_clock = QLabel()
        self.lbl_clock.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_CYAN_STR}; font-family: 'Consolas', monospace;")
        self.update_clock()

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_status)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.lbl_clock)
        main_layout.addWidget(header_frame)

        # ---------------- 2. Middle Body Grid Layout ----------------
        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        # ---- Left Panel: System Telemetry ----
        telemetry_frame = QFrame()
        telemetry_frame.setFixedWidth(240)
        tel_layout = QVBoxLayout(telemetry_frame)
        tel_layout.setContentsMargins(14, 14, 14, 14)
        tel_layout.setSpacing(10)

        lbl_tel_header = QLabel("SYSTEM TELEMETRY")
        lbl_tel_header.setStyleSheet(f"font-weight: bold; color: {COLOR_GOLD_STR}; font-size: 12px; letter-spacing: 1px;")
        tel_layout.addWidget(lbl_tel_header)

        # CPU Usage Bar
        tel_layout.addWidget(QLabel("CPU LOAD"))
        self.bar_cpu = QProgressBar()
        self.bar_cpu.setValue(0)
        tel_layout.addWidget(self.bar_cpu)

        # RAM Usage Bar
        tel_layout.addWidget(QLabel("RAM USAGE"))
        self.bar_ram = QProgressBar()
        self.bar_ram.setValue(0)
        tel_layout.addWidget(self.bar_ram)

        # Battery Gauge
        tel_layout.addWidget(QLabel("POWER / BATTERY"))
        self.lbl_battery = QLabel("Checking battery...")
        self.lbl_battery.setStyleSheet("font-size: 12px; color: #94a3b8;")
        tel_layout.addWidget(self.lbl_battery)

        # Security Owner & Workshop Card
        tel_layout.addSpacing(10)
        owner_box = QFrame()
        owner_box.setStyleSheet("background-color: #020617; border: 1px solid #334155;")
        ob_layout = QVBoxLayout(owner_box)
        ob_layout.setContentsMargins(10, 10, 10, 10)
        ob_layout.addWidget(QLabel(f"<b>ORGANIZATION:</b><br><font color='{COLOR_CYAN_STR}'>{self.jarvis.company_name}</font>"))
        ob_layout.addWidget(QLabel(f"<b>SCHOOL VENUE:</b><br><font color='{COLOR_GREEN_STR}'>{self.jarvis.school_name}</font>"))
        ob_layout.addWidget(QLabel(f"<b>TRAINER / AUTHOR:</b><br><font color='{COLOR_GOLD_STR}'>{OWNER_NAME}</font>"))
        tel_layout.addWidget(owner_box)

        tel_layout.addStretch()
        body_layout.addWidget(telemetry_frame)

        # ---- Center Panel: Arc Reactor Core & Sound Visualizer ----
        center_frame = QFrame()
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(14, 14, 14, 14)
        center_layout.setSpacing(10)

        lbl_core_header = QLabel("ARC REACTOR CORE MATRIX")
        lbl_core_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_core_header.setStyleSheet(f"font-weight: bold; color: {COLOR_CYAN_STR}; font-size: 12px; letter-spacing: 2px;")
        center_layout.addWidget(lbl_core_header)

        # Arc Reactor Core Canvas
        self.arc_reactor = ArcReactorWidget()
        center_layout.addWidget(self.arc_reactor, alignment=Qt.AlignmentFlag.AlignCenter)

        # Audio Equalizer Waveform
        self.sound_wave = SoundVisualizerWidget()
        center_layout.addWidget(self.sound_wave)

        # Quick Control HUD Buttons
        quick_btns_layout = QHBoxLayout()
        quick_btns_layout.setSpacing(6)

        btn_voice = QPushButton("🎤 VOICE ACTIVATE")
        btn_voice.setStyleSheet(f"background-color: {COLOR_CYAN_STR}; color: #020617; font-weight: bold;")
        btn_voice.clicked.connect(self.on_click_voice_activate)

        btn_school = QPushButton("🏫 SCHOOL DEMO")
        btn_school.setStyleSheet(f"background-color: {COLOR_GREEN_STR}; color: #020617; font-weight: bold;")
        btn_school.clicked.connect(lambda: self.on_quick_command("welcome presentation"))

        btn_google = QPushButton("🌐 GOOGLE")
        btn_google.clicked.connect(lambda: self.on_quick_command("open google"))

        btn_yt = QPushButton("▶ YOUTUBE")
        btn_yt.clicked.connect(lambda: self.on_quick_command("open youtube"))

        btn_joke = QPushButton("😄 JOKE")
        btn_joke.clicked.connect(lambda: self.on_quick_command("tell me a joke"))

        quick_btns_layout.addWidget(btn_voice)
        quick_btns_layout.addWidget(btn_school)
        quick_btns_layout.addWidget(btn_google)
        quick_btns_layout.addWidget(btn_yt)
        quick_btns_layout.addWidget(btn_joke)

        center_layout.addLayout(quick_btns_layout)
        body_layout.addWidget(center_frame, stretch=1)

        # ---- Right Panel: Cyber Terminal Log ----
        terminal_frame = QFrame()
        terminal_frame.setFixedWidth(320)
        term_layout = QVBoxLayout(terminal_frame)
        term_layout.setContentsMargins(14, 14, 14, 14)

        lbl_term_header = QLabel("CYBER TERMINAL LOG")
        lbl_term_header.setStyleSheet(f"font-weight: bold; color: {COLOR_CYAN_STR}; font-size: 12px; letter-spacing: 1px;")
        term_layout.addWidget(lbl_term_header)

        self.txt_terminal = QTextEdit()
        self.txt_terminal.setReadOnly(True)
        self.txt_terminal.setStyleSheet(f"""
            QTextEdit {{
                background-color: #020617;
                border: 1px solid #1e293b;
                color: #e2e8f0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }}
        """)
        term_layout.addWidget(self.txt_terminal)
        body_layout.addWidget(terminal_frame)

        main_layout.addLayout(body_layout, stretch=1)

        # ---------------- 3. Bottom Input Controls ----------------
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 8, 12, 8)

        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Enter command or query (e.g. 'play song', 'cpu usage', 'who is Tony Stark')...")
        self.txt_input.returnPressed.connect(self.on_send_command)

        btn_send = QPushButton("SEND COMMAND")
        btn_send.setFixedWidth(130)
        btn_send.clicked.connect(self.on_send_command)

        input_layout.addWidget(self.txt_input, stretch=1)
        input_layout.addWidget(btn_send)

        main_layout.addWidget(input_frame)

    # ---------------- Telemetry & Clock ----------------
    def init_telemetry_timer(self):
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start(1500)
        self.update_telemetry()

    def update_clock(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d  %I:%M:%S %p")
        self.lbl_clock.setText(now)

    def update_telemetry(self):
        self.update_clock()

        # CPU Usage
        cpu = psutil.cpu_percent()
        self.bar_cpu.setValue(int(cpu))

        # RAM Usage
        ram = psutil.virtual_memory().percent
        self.bar_ram.setValue(int(ram))

        # Battery
        battery = psutil.sensors_battery()
        if battery:
            plugged = " ⚡" if battery.power_plugged else ""
            self.lbl_battery.setText(f"Level: {battery.percent}%{plugged}")
        else:
            self.lbl_battery.setText("AC Power connected")

    # ---------------- Callbacks & Logging ----------------
    def gui_log_callback(self, text, tag="JARVIS"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if tag == "JARVIS":
            html = f"<font color='#64748b'>[{timestamp}]</font> <font color='{COLOR_CYAN_STR}'><b>[JARVIS]</b></font> {text}<br>"
        elif tag == "USER":
            html = f"<font color='#64748b'>[{timestamp}]</font> <font color='{COLOR_GOLD_STR}'><b>[USER]</b></font> {text}<br>"
        else:
            html = f"<font color='#64748b'>[{timestamp}]</font> <font color='{COLOR_GREEN_STR}'><b>[{tag}]</b></font> {text}<br>"
        
        self.txt_terminal.append(html)
        self.txt_terminal.verticalScrollBar().setValue(
            self.txt_terminal.verticalScrollBar().maximum()
        )

    def gui_state_callback(self, state):
        self.arc_reactor.set_state(state)
        self.sound_wave.set_state(state)
        
        if state == "LISTENING":
            self.lbl_status.setText("STATUS: LISTENING...")
            self.lbl_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_GREEN_STR}; border: 1px solid {COLOR_GREEN_STR}; padding: 4px 10px; border-radius: 4px;")
        elif state == "PROCESSING":
            self.lbl_status.setText("STATUS: PROCESSING...")
            self.lbl_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_GOLD_STR}; border: 1px solid {COLOR_GOLD_STR}; padding: 4px 10px; border-radius: 4px;")
        elif state == "SPEAKING":
            self.lbl_status.setText("STATUS: SPEAKING...")
            self.lbl_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_CYAN_STR}; border: 1px solid {COLOR_CYAN_STR}; padding: 4px 10px; border-radius: 4px;")
        elif state == "PIN_VERIFICATION":
            self.lbl_status.setText("STATUS: PIN SECURITY CHECK")
            self.lbl_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_RED_STR}; border: 1px solid {COLOR_RED_STR}; padding: 4px 10px; border-radius: 4px;")
        else:
            self.lbl_status.setText("STATUS: STANDBY")
            self.lbl_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_GOLD_STR}; border: 1px solid {COLOR_GOLD_STR}; padding: 4px 10px; border-radius: 4px;")

    # ---------------- Async Actions ----------------
    def on_click_voice_activate(self):
        self.gui_log_callback("Listening for voice input...", tag="SYSTEM")
        self.listen_thread = VoiceListenThread(self.jarvis)
        self.listen_thread.signal_recognized.connect(self.on_voice_recognized)
        self.listen_thread.start()

    def on_voice_recognized(self, text):
        if text:
            self.txt_input.setText(text)
            self.execute_command_async(text)

    def on_send_command(self):
        command = self.txt_input.text().strip()
        if command:
            self.txt_input.clear()
            self.gui_log_callback(command, tag="USER")
            self.execute_command_async(command)

    def on_quick_command(self, cmd):
        self.gui_log_callback(cmd, tag="USER")
        self.execute_command_async(cmd)

    def execute_command_async(self, command):
        self.cmd_thread = CommandExecThread(self.jarvis, command)
        self.cmd_thread.signal_finished.connect(self.on_command_finished)
        self.cmd_thread.start()

    def run_async_speech(self, text):
        class SpeechThread(QThread):
            def __init__(self, jc, t):
                super().__init__()
                self.jc = jc
                self.t = t
            def run(self):
                self.jc.speak(self.t)
        self.sp_thread = SpeechThread(self.jarvis, text)
        self.sp_thread.start()

    def on_command_finished(self, result):
        if result == "EXIT":
            QTimer.singleShot(1500, self.close)


def launch_gui():
    app = QApplication(sys.argv)
    window = JarvisMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()
