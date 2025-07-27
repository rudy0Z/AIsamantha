import sys
import threading
import time
import requests
import pyaudio
import wave
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter

class HealthCheckThread(QThread):
    status_update = pyqtSignal(bool)

    def run(self):
        while True:
            try:
                response = requests.get("http://localhost:5000/health", timeout=1)
                if response.status_code == 200:
                    self.status_update.emit(True)
                else:
                    self.status_update.emit(False)
            except requests.RequestException:
                self.status_update.emit(False)
            time.sleep(5)

class FloatingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.chat_history = []
        self.initUI()
        self.init_health_check()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 120, 120)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.mic_button = QPushButton("🎤")
        self.mic_button.setFixedSize(100, 100)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                border-radius: 50px;
                font-size: 50px;
                color: white;
                border: 3px solid #1a1a1a;
            }
            QPushButton:hover {
                border: 3px solid #6bcf7f;
            }
        """)
        self.mic_button.clicked.connect(self.toggle_recording)
        self.layout.addWidget(self.mic_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(10, 10)
        self.status_dot.setStyleSheet("background-color: #ff6b6b; border-radius: 5px;")
        self.layout.addWidget(self.status_dot, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("background-color: #555; color: white; border-radius: 10px;")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.show()

    def init_health_check(self):
        self.health_thread = HealthCheckThread()
        self.health_thread.status_update.connect(self.update_status)
        self.health_thread.start()

    def update_status(self, is_healthy):
        if is_healthy:
            self.status_dot.setStyleSheet("background-color: #6bcf7f; border-radius: 5px;")
        else:
            self.status_dot.setStyleSheet("background-color: #ff6b6b; border-radius: 5px;")

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.mic_button.setText("⏳")
            self.mic_button.setStyleSheet("background-color: #f1c40f; border-radius: 50px; font-size: 50px; color: white;")
            self.record_and_process()
        else:
            self.is_recording = False
            self.mic_button.setText("🎤")
            self.mic_button.setStyleSheet("background-color: #ff6b6b; border-radius: 50px; font-size: 50px; color: white;")

    def record_and_process(self):
        threading.Thread(target=self._record_and_process_thread).start()

    def _record_and_process_thread(self):
        try:
            # 1. Record Audio
            audio_path = "temp_recording.wav"
            self.record_audio(audio_path)

            # 2. Transcribe Audio
            with open(audio_path, 'rb') as f:
                files = {'audio': f}
                response = requests.post("http://localhost:5000/transcribe", files=files)
                transcript = response.json()['text']

            # 3. Detect Emotion
            response = requests.post("http://localhost:5000/detect_emotion", json={'text': transcript})
            emotion = response.json()['emotion']

            # 4. Generate Response
            response = requests.post("http://localhost:5000/generate_response", json={
                'user_text': transcript,
                'detected_emotion': emotion,
                'chat_history': self.chat_history
            })
            ai_response = response.json()['response']
            self.chat_history.append({"user": transcript, "ai": ai_response})

            # 5. Synthesize Speech
            response = requests.post("http://localhost:5000/synthesize_speech", json={'text': ai_response, 'emotion': emotion})
            
            # 6. Play Speech
            self.mic_button.setText("🔊")
            self.mic_button.setStyleSheet("background-color: #3498db; border-radius: 50px; font-size: 50px; color: white;")
            
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
            stream.write(response.content)
            stream.stop_stream()
            stream.close()
            p.terminate()

        except Exception as e:
            print(f"Error: {e}")
            self.mic_button.setText("❌")
        finally:
            self.is_recording = False
            self.mic_button.setText("🎤")
            self.mic_button.setStyleSheet("background-color: #6bcf7f; border-radius: 50px; font-size: 50px; color: white;")


    def record_audio(self, file_path):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 3

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(file_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FloatingApp()
    sys.exit(app.exec())
