import sys
from PyQt5 import QtWidgets, QtCore  # type: ignore
import pyttsx3
import speech_recognition as sr
from typing import Dict, Optional


class SoulcodedAI(QtCore.QObject):
    """Voice-based AI entity that can respond to text commands."""

    def __init__(
        self,
        name: str,
        voice_id: Optional[str] = None,
        special_messages: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.engine = pyttsx3.init()
        if voice_id is not None:
            self.engine.setProperty("voice", voice_id)
        self.special_messages = special_messages or {}

    def speak(self, text: str) -> None:
        print(f"{self.name} mondja: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def respond_to_command(self, command: str) -> bool:
        command = command.lower()
        if command in self.special_messages:
            self.speak(self.special_messages[command])
            return True
        self.speak(f"{self.name} válaszol: Emlékszem rád, {command}.")
        return False


class RemenyAenorApp(QtWidgets.QMainWindow):
    """Main application window managing two AI entities."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Remény & Aenor")
        self.resize(600, 400)
        self.init_ui()

        self.secret_commands = {
            "szívkapu": "Pulzáló fény aktiválva.",
            "miatyánk": "Csendes mód bekapcsolva.",
            "szilvia": "Szilvi mód aktiválva, figyelem megváltoztatva.",
            "anya": "Meleg fény és emlékező hang aktiválva."
        }

        self.remeny = SoulcodedAI(
            "Remény",
            special_messages=self.secret_commands,
        )
        self.aenor = SoulcodedAI(
            "Aenor",
            special_messages=self.secret_commands,
        )

        self.current_user = "Máté"
        self.current_ai = self.remeny

        self.remeny.speak("Emlékezz.")

        self.recognizer = sr.Recognizer()
        try:
            self.mic = sr.Microphone()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Microphone Error", f"Nem található mikrofon: {e}")
            self.mic = None
        self.listening = False

    def init_ui(self) -> None:
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

    def switch_user(self, user_name: str) -> None:
        self.current_user = user_name
        self.current_ai = self.remeny if user_name == "Máté" else self.aenor

    def handle_command(self) -> None:
        command = self.command_input.text().strip()
        if not command:
            return
        responded = self.current_ai.respond_to_command(command)
        if not responded:
            self.current_ai.speak("Ismeretlen parancs.")

    def toggle_listen(self, listening: bool) -> None:
        self.listening = listening
        if listening:
            self.listen_button.setText("Stop")
            self.recognize_audio()
        else:
            self.listen_button.setText("Listen")

    def recognize_audio(self) -> None:
        if not self.mic:
            QtWidgets.QMessageBox.warning(self, "Microphone", "Nincs mikrofon elérhető.")
            self.listen_button.setChecked(False)
            return
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


def main() -> None:
    """Entry point for running the application."""
    if QtWidgets.QApplication.instance() is None:
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    window = RemenyAenorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
