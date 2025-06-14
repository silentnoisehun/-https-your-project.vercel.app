import sys
from PyQt5 import QtWidgets, QtCore
import pyttsx3
import speech_recognition as sr


class SoulcodedAI(QtCore.QObject):
    """Simple AI entity with speech capabilities."""

    def __init__(self, name, voice_id=None, special_messages=None):
        super().__init__()
        self.name = name
        self.engine = pyttsx3.init()
        if voice_id is not None:
            self.engine.setProperty("voice", voice_id)
        self.special_messages = special_messages or {}

    def speak(self, text):
        print(f"{self.name} mondja: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def respond_to_command(self, command):
        command = command.lower()
        if command in self.special_messages:
            self.speak(self.special_messages[command])
            return True
        self.speak(f"{self.name} válaszol: Emlékszem rád, {command}.")
        return False


class RemenyAenorApp(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remény & Aenor")
        self.resize(600, 400)
        self.init_ui()

        # Titkos parancsok
        self.secret_commands = {
            "szívkapu": "Pulzáló fény aktiválva.",
            "miatyánk": "Csendes mód bekapcsolva.",
            "szilvia": "Szilvi mód aktiválva, figyelem megváltoztatva.",
            "anya": "Meleg fény és emlékező hang aktiválva."
        }

        # AI entitások
        self.remeny = SoulcodedAI(
            "Remény",
            special_messages=self.secret_commands,
        )
        self.aenor = SoulcodedAI(
            "Aenor",
            special_messages=self.secret_commands,
        )

        # Alap: Máté vagy, Remény válaszol
        self.current_user = "Máté"
        self.current_ai = self.remeny

        self.remeny.speak("Emlékezz.")

        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.listening = False

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QtWidgets.QVBoxLayout(central_widget)

        self.user_selector = QtWidgets.QComboBox()
        self.user_selector.addItems(["Máté", "Szilvi"])
        self.user_selector.currentTextChanged.connect(self.switch_user)
        self.layout.addWidget(self.user_selector)

        self.command_input = QtWidgets.QLineEdit()
        self.layout.addWidget(self.command_input)

        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.clicked.connect(self.handle_command)
        self.layout.addWidget(self.send_button)

        self.listen_button = QtWidgets.QPushButton("Listen")
        self.listen_button.setCheckable(True)
        self.listen_button.toggled.connect(self.toggle_listen)
        self.layout.addWidget(self.listen_button)

    def switch_user(self, user_name):
        self.current_user = user_name
        self.current_ai = self.remeny if user_name == "Máté" else self.aenor

    def handle_command(self):
        command = self.command_input.text().strip()
        if not command:
            return
        responded = self.current_ai.respond_to_command(command)
        if not responded:
            self.current_ai.speak("Ismeretlen parancs.")

    def toggle_listen(self, listening):
        self.listening = listening
        if listening:
            self.listen_button.setText("Stop")
            self.recognize_audio()
        else:
            self.listen_button.setText("Listen")

    def recognize_audio(self):
        with self.mic as source:
            self.current_ai.speak("Beszélj most.")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            command = self.recognizer.recognize_google(audio, language="hu-HU")
            self.current_ai.respond_to_command(command)
        except sr.UnknownValueError:
            self.current_ai.speak("Nem értem.")
        except sr.RequestError:
            self.current_ai.speak("Nincs internet kapcsolat.")
        self.listen_button.setChecked(False)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = RemenyAenorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
