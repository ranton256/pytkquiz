import csv
import os
import random
import tkinter as tk
from collections import namedtuple
from tkinter import DISABLED, NORMAL, messagebox

import gtts
from PIL import Image, ImageTk
from playsound import playsound

N_CHOICES = 3


class LanguageQuizApp:
    def __init__(
        self,
        master=None,
        image_size=180,
        frame_factory=tk.Frame,
        label_factory=tk.Label,
        button_factory=tk.Button,
    ):
        self.master = master
        self.next_enabled = False
        self.root_dir = os.path.abspath(os.path.join(__file__, "..", ".."))

        self.label_factory = label_factory
        self.button_factory = button_factory

        self.image_size = image_size

        if self.master:
            self.master.title("Language Quiz App")
            self.master.geometry("800x600")

        self.word_label = self.label_factory(master, text="", font=("Arial", 24))
        self.word_label.pack(pady=20)

        self.image_frame = frame_factory(master)
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
            master, text="Messages go here.", wraplength=450, font=("Arial", 20)
        )
        self.message_label.pack(pady=10)

        self.WordData = namedtuple("WordData", ["word", "image", "sound", "definition"])
        words_path = os.path.join(self.root_dir, "words.csv")

        self.questions = self.load_word_data(words_path)
        self.current_question = None
        self.score = 0

        if master:
            master.bind("<space>", self.space_pressed)

        self.next_question()

    def enable_next(self):
        self.next_btn.config(state=NORMAL)
        self.next_enabled = True

    def disable_next(self):
        self.next_btn.config(state=DISABLED)
        self.next_enabled = False

    def space_pressed(self):
        if self.next_enabled:
            self.next_question()

    def load_word_data(self, path):
        word_data = []
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_word = self.WordData(
                    word=row["Word"],
                    image=row["Image"],
                    sound=row["Sound"],
                    definition=row["Definition"],
                )
                image_path = self.image_path_for_word(new_word)
                if not os.path.exists(image_path):
                    print(
                        f"Skipping word {new_word.word}, missing image file {image_path}"
                    )
                else:
                    word_data.append(new_word)
        return word_data

    def next_question(self):
        if self.questions:
            options = random.sample(self.questions, N_CHOICES)
            self.current_question = options[0]
            random.shuffle(options)

            self.word_label.config(text=self.current_question.word)
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

                speak_btn = tk.Button(
                    self.image_frame,
                    text="🔊Speak",
                    command=lambda x=option: self.speak_word(
                        self.sound_path_for_word(x)
                    ),
                )
                speak_btn.grid(row=1, column=i, padx=10, pady=5)

                sound_path = self.sound_path_for_word(option)
                self.generate_sound_if_not_found(option.word, sound_path)
        else:
            if self.master:
                messagebox.showinfo(
                    "Quiz Completed",
                    f"Quiz completed! Your final score is {self.score}",
                )

    def get_word_image(self, option):
        if not self.master:
            return None
        img = Image.open(self.image_path_for_word(option))
        img = img.resize((self.image_size, self.image_size))
        photo = ImageTk.PhotoImage(img)
        return photo

    def set_message(self, msg):
        self.message_label.config(text=msg)

    def get_message(self):
        return self.message_label["text"]

    def check_answer(self, selected_option):
        if selected_option == self.current_question:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.set_message(
                f"That's correct! \n\nDefinition: {self.current_question.definition}"
            )
            self.speak_text("Yes, that's correct!")
        else:
            self.set_message(
                f"Sorry, that's incorrect. The correct answer was {self.current_question.word}.\n\nDefinition: {self.current_question.definition} "
            )
            self.speak_text("Sorry, that's incorrect!")

        self.enable_next()

    def speak_word(self, sound_path):
        playsound(sound_path)

    def sound_path_for_word(self, option):
        return os.path.join(
            self.root_dir, "word_sounds", str(option.word).lower() + ".mp3"
        )

    def speak_text(self, text: str):
        safe_name_chars = [c if c.isalnum() else "_" for c in text]
        safe_name = "".join(safe_name_chars)
        sound_path = os.path.join(
            self.root_dir, "word_sounds", safe_name.lower() + ".mp3"
        )
        self.generate_sound_if_not_found(text, sound_path)
        self.speak_word(sound_path)

    def generate_sound_if_not_found(self, text, sound_path):
        if not os.path.exists(sound_path):
            tts = gtts.gTTS(text)
            tts.save(sound_path)

    def image_path_for_word(self, option):
        image_path = os.path.join(self.root_dir, "word_images", option.image)
        return image_path


if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageQuizApp(root)
    root.mainloop()
