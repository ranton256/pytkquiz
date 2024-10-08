import os
import tkinter as tk
from tkinter import DISABLED, NORMAL
from typing import Optional, Callable

import gtts  # type: ignore
from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage
from playsound import playsound

from pytkquiz.sound_gen import generate_sound_if_not_found
from quiz_logic import QuizLogic, WordData

N_CHOICES = 3


class LanguageQuizApp:
    """
    The `LanguageQuizApp` provides a graphical user interface (GUI) for displaying word information,
    allowing users to select answers, and tracking the user's score.

    The class has the following key features:

    - Loads word data from a CSV file and presents a random selection of words to the user.
    - Displays the word and a set of images representing possible answers.
    - Allows the user to select an answer and provides feedback on whether the answer is correct.
    - Keeps track of the user's score and displays it.
    - Provides functionality to speak the word and its definition using text-to-speech.
    - Handles the overall flow of the quiz, including advancing to the next question.

    The class can be customized by providing different factories for the GUI elements (frames, labels, buttons)
    and the image size.
    """

    def __init__(
            self,
            master: Optional[tk.Tk] = None,
            image_size: int = 180,
            frame_factory: Callable[..., tk.Frame] = tk.Frame,
            label_factory: Callable[..., tk.Label] = tk.Label,
            button_factory: Callable[..., tk.Button] = tk.Button,
            image_factory: Callable[..., ImageTk.PhotoImage] = ImageTk.PhotoImage,
    ) -> None:
        """
        Initializes the LanguageQuizApp instance with the provided configuration.

        Args:
            master (Optional[tk.Tk]): The root Tkinter window for the application.
            image_size (int): The size of the images to be displayed in the quiz.
            frame_factory (Callable[..., tk.Frame]): A factory function to create Tkinter frames.
            label_factory (Callable[..., tk.Label]): A factory function to create Tkinter labels.
            button_factory (Callable[..., tk.Button]): A factory function to create Tkinter buttons.

        The constructor sets up the initial state of the application, including the GUI elements, score tracking,
        and loading the word data. It also binds the space key press event to the `next_question` method.
        :param language:
        """

        self.master = master
        self.next_enabled = False
        self.root_dir = os.path.abspath(os.path.join(__file__, "..", ".."))

        self.label_factory = label_factory
        self.frame_factory =frame_factory
        self.button_factory = button_factory
        self.image_factory = image_factory

        self.language_chooser = self.label_factory(master, text="Choose a language:")
        self.language_chooser.pack(pady=10)
        self.language_chooser.config(font=("Arial", 16))

        lang_options = ['Greek', 'English']  #TODO: reverse
        chosen_lang = tk.StringVar(value=lang_options[0])
        self.chosen_lang = chosen_lang

        lang_menu = tk.OptionMenu(master, chosen_lang, *lang_options, command=self.update_language)
        self.lang_menu = lang_menu
        lang_menu.pack(pady=10)

        if self.master:
            self.master.title("Language Quiz App")
            self.master.geometry("800x600")

        self.word_label = self.label_factory(master, text="", font=("Arial", 24))
        self.word_label.pack(pady=20)

        self.image_frame = self.frame_factory(master)
        self.image_frame.pack(pady=20)

        self.next_btn = self.button_factory(
            master, text="Next Question", command=lambda: self.next_question()
        )
        self.next_btn.pack(pady=10)

        self.disable_next()
        self.score_label = self.label_factory(
            master, text="Score: 0", font=("Arial", 16)
        )
        self.score_label.pack(pady=10)
        self.message_label = self.label_factory(
            master, text="Messages go here.", wraplength=450, font=("Arial", 20), justify="left"
        )
        self.message_label.pack(pady=10)

        self.image_size = image_size

        if master:
            master.bind("<space>", self.space_pressed)

        self.update_language()

    def update_language(self, *args):
        """
        Update the language based on the selected language name.
        """

        lang_name = self.chosen_lang.get()
        lang_map = {
            'English': 'en',
            'Greek': 'el'
        }
        self.language = lang_map[lang_name]

        if self.language == "en":
            words_path = os.path.join(self.root_dir, "words.csv")
        else:
            words_path = os.path.join(self.root_dir, "words_" + self.language + ".csv")
        word_col_index = 0 if self.language == "en" else 4

        self.quiz_logic = QuizLogic(root_dir=self.root_dir, language=self.language)
        self.quiz_logic.load_word_data(words_path, word_col_index)

        self.next_question()

    def enable_next(self):
        """
        Enable the 'Next' button and set the next_enabled flag to True.

        This method configures the next_btn widget to be in a normal (clickable) state
        and sets the next_enabled attribute to True, allowing the user to proceed
        to the next question.
        """
        self.next_btn.config(state=NORMAL)
        self.next_enabled = True

    def disable_next(self):
        """
        Disable the 'Next' button and set the next_enabled flag to False.

        This method configures the next_btn widget to be in a disabled (non-clickable) state
        and sets the next_enabled attribute to False, preventing the user from proceeding
        to the next question until the current question is answered correctly.
        """
        self.next_btn.config(state=DISABLED)
        self.next_enabled = False

    def space_pressed(self, event):
        print(f"You pressed space: {event}")
        if self.next_enabled:
            self.next_question()

    def next_question(self):
        options = self.quiz_logic.next_question()
        current_question = self.quiz_logic.current_question

        self.word_label.config(text=current_question.word)
        self.message_label.config(text="")
        self.disable_next()
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        for i, option in enumerate(options):
            photo = self.get_word_image(option)
            btn = self.button_factory(
                self.image_frame,
                image=photo,
                command=lambda opt=option: self.check_answer(opt),
            )
            btn.image = photo
            btn.grid(row=0, column=i, padx=10, pady=10)

            speak_btn = self.button_factory(
                self.image_frame,
                text="🔊Speak",
                command=lambda x=option: self.speak_word(
                    self.quiz_logic.sound_path_for_word(x)
                ),
            )
            speak_btn.grid(row=1, column=i, padx=10, pady=5)

            sound_path = self.quiz_logic.sound_path_for_word(option)
            generate_sound_if_not_found(self.language, option.word, sound_path)

    def get_word_image(self, option: WordData) -> PhotoImage or None:
        """
        Get the Tkinter PhotoImage object for the image associated with the given word option.

        Args:
            option (WordData): The word option to get the image for.

        Returns:
            PhotoImage or None: The Tkinter PhotoImage object for the image, or None if the image file does not exist.
        """
        img = Image.open(self.quiz_logic.image_path_for_word(option))
        img = img.resize((self.image_size, self.image_size))
        photo = self.image_factory(img)
        return photo

    def set_message(self, msg: str) -> None:
        """Set the currently displayed message for the user."""
        self.message_label.config(text=msg)

    def get_message(self) -> str:
        """Return the currently displayed message."""
        return self.message_label["text"]

    def check_answer(self, selected_option: WordData) -> bool:
        correct = self.quiz_logic.check_answer(selected_option)
        if correct:
            self.score_label.config(text=f"Score: {self.quiz_logic.score}")
            self.set_message(
                f"That's correct! \n\nDefinition: {self.quiz_logic.current_question.definition}"
            )
            self.speak_text("Yes, that's correct!")
        else:
            self.set_message(
                f"""Sorry, that's incorrect. The correct answer was {self.quiz_logic.current_question.word}.
                Definition: {self.quiz_logic.current_question.definition}"""
            )
            self.speak_text("Sorry, that's incorrect!")

        self.enable_next()
        return correct

    @staticmethod
    def speak_word(sound_path: str) -> None:
        playsound(sound_path)

    def speak_text(self, text: str) -> None:
        """
        Speaks the given text by generating an audio file for it and playing it.

        Args:
            text (str): The text to be spoken.

        Returns:
            None
        """
        # TODO: not sure if we need this filtering.
        text = text.lower()
        safe_name_chars = [c if c.isalnum() else "_" for c in text]
        safe_name = "".join(safe_name_chars)

        sound_path = os.path.join(
            self.root_dir, "word_sounds", safe_name.lower() + ".mp3"
        )

        generate_sound_if_not_found(self.language, text, sound_path)
        self.speak_word(sound_path)

    @property
    def score(self):
        return self.quiz_logic.score

    @property
    def current_question(self):
        return self.quiz_logic.current_question


if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageQuizApp(root)
    root.mainloop()
