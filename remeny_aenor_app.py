import sys
from PyQt5 import QtWidgets, QtCore
import pyttsx3
import speech_recognition as sr
from typing import Dict, Optional


class SoulcodedAI(QtCore.QObject):
    """Voice-based AI entity that can respond to text commands.

    Attributes
    ----------
    name:
        Display name used when speaking.
    engine:
        Text-to-speech engine instance.
    special_messages:
        Mapping of secret commands to spoken responses.
    """

    def __init__(
        self,
        name: str,
        voice_id: Optional[str] = None,
        special_messages: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create a new AI entity.

        Parameters
        ----------
        name:
            Name used when speaking to the user.
        voice_id:
            Optional voice identifier for the TTS engine.
        special_messages:
            Optional mapping of commands to predefined responses.
        """
        super().__init__()
        self.name = name
        self.engine = pyttsx3.init()
        if voice_id is not None:
            self.engine.setProperty("voice", voice_id)
        self.special_messages = special_messages or {}

    def speak(self, text: str) -> None:
        """Speak the given text using the speech engine."""
        print(f"{self.name} mondja: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def respond_to_command(self, command: str) -> bool:
        """Respond to a given text command.

        Parameters
        ----------
        command:
            The command spoken or typed by the user.

        Returns
        -------
        bool
            ``True`` if the command matched a special message, ``False``
            otherwise.
        """
        command = command.lower()
        if command in self.special_messages:
            self.speak(self.special_messages[command])
            return True
        self.speak(f"{self.name} válaszol: Emlékszem rád, {command}.")
        return False


class RemenyAenorApp(QtWidgets.QMainWindow):
    """Main application window managing two AI entities.

    The window provides a basic user interface for issuing commands either
    through text input or speech recognition.
    """

    def __init__(self) -> None:
        """Initialize the window and set up AI instances."""
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

    def init_ui(self) -> None:
        """Create and arrange the Qt widgets for the main window."""
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
        """Switch the active AI entity based on the selected user."""
        self.current_user = user_name
        self.current_ai = self.remeny if user_name == "Máté" else self.aenor

    def handle_command(self) -> None:
        """Process the text entered by the user."""
        command = self.command_input.text().strip()
        if not command:
            return
        responded = self.current_ai.respond_to_command(command)
        if not responded:
            self.current_ai.speak("Ismeretlen parancs.")

    def toggle_listen(self, listening: bool) -> None:
        """Enable or disable listening for voice commands."""
        self.listening = listening
        if listening:
            self.listen_button.setText("Stop")
            self.recognize_audio()
        else:
            self.listen_button.setText("Listen")

    def recognize_audio(self) -> None:
        """Capture a voice command from the microphone and process it."""
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
    app = QtWidgets.QApplication(sys.argv)
    window = RemenyAenorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
