import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
import gtts
from playsound import playsound
import csv
from collections import namedtuple

class LanguageQuizApp:
    def __init__(self, master=None):
        self.master = master
        if master:
            self.master.title("Language Quiz App")
            self.master.geometry("800x600")
            self.word_label = tk.Label(master, text="", font=("Arial", 24))
            self.word_label.pack(pady=20)
            self.image_frame = tk.Frame(master)
            self.image_frame.pack(pady=20)
            self.score_label = tk.Label(master, text="Score: 0", font=("Arial", 16))
            self.score_label.pack(pady=10)

        self.WordData = namedtuple('WordData', ['word', 'image', 'sound', 'definition'])
        self.questions = self.load_word_data("words.csv")
        self.current_question = None
        self.score = 0

        if master:
            self.next_question()

    def load_word_data(self, path):
        word_data = []
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_word = self.WordData(
                    word=row['Word'],
                    image=row['Image'],
                    sound=row['Sound'],
                    definition=row['Definition']
                )
                image_path = self.image_path_for_word(new_word)
                if not os.path.exists(image_path):
                    print(f"Skipping word {new_word.word}, missing image file {image_path}")
                else:
                    word_data.append(new_word)
        return word_data

    def next_question(self):
        if self.questions:
            self.current_question = random.choice(self.questions)
            if self.master:
                self.word_label.config(text=self.current_question.word)
                for widget in self.image_frame.winfo_children():
                    widget.destroy()

            options = random.sample(self.questions, 3)
            options.append(self.current_question)
            random.shuffle(options)

            if self.master:
                for i, option in enumerate(options):
                    img = Image.open(self.image_path_for_word(option))
                    img = img.resize((100, 100)) #, Image.ANTIALIAS)
                    photo = ImageTk.PhotoImage(img)
                    btn = tk.Button(self.image_frame, image=photo, command=lambda opt=option: self.check_answer(opt))
                    btn.image = photo
                    btn.grid(row=0, column=i, padx=10, pady=10)

                    speak_btn = tk.Button(self.image_frame, text="🔊", command=lambda x=option: self.speak_word(self.sound_path_for_word(x)))
                    speak_btn.grid(row=1, column=i, padx=10, pady=5)

                    sound_path = self.sound_path_for_word(option)
                    self.generate_sound_if_not_found(option.word, sound_path)
        else:
            if self.master:
                messagebox.showinfo("Quiz Completed", f"Quiz completed! Your final score is {self.score}")

    def check_answer(self, selected_option):
        if selected_option == self.current_question:
            self.score += 1
            if self.master:
                self.score_label.config(text=f"Score: {self.score}")
            self.speak_text("Yes, that's correct!")
            if self.master:
                messagebox.showinfo("Correct", f"That's correct! \n\nDefinition: {self.current_question.definition}")
        else:
            self.speak_text("Sorry, that's incorrect!")
            if self.master:
                messagebox.showinfo("Incorrect", f"Sorry, that's incorrect. The correct answer was {self.current_question.word}.\n\nDefinition: {self.current_question.definition}")

        self.questions.remove(self.current_question)
        self.next_question()

    def speak_word(self, sound_path):
        playsound(sound_path)

    def sound_path_for_word(self, option):
        return os.path.join("word_sounds", str(option.word).lower() + ".mp3")

    def speak_text(self, text: str):
        safe_name_chars = [c if c.isalnum() else '_' for c in text]
        safe_name = ''.join(safe_name_chars)
        sound_path = os.path.join("word_sounds", safe_name.lower() + ".mp3")
        self.generate_sound_if_not_found(text, sound_path)
        self.speak_word(sound_path)

    def generate_sound_if_not_found(self, text, sound_path):
        if not os.path.exists(sound_path):
            tts = gtts.gTTS(text)
            tts.save(sound_path)

    def image_path_for_word(self, option):
        image_path = f"word_images/{option.image}"
        return image_path

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageQuizApp(root)
    root.mainloop()
