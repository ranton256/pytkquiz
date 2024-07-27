import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
import gtts
from playsound import playsound


class LanguageQuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Language Quiz App")
        self.master.geometry("800x600")

        self.questions = [
            {"word": "Apple", "correct": "apple.jpg", "options": ["apple.jpg", "banana.jpg", "orange.jpg"]},
            {"word": "Car", "correct": "car.jpg", "options": ["car.jpg", "bike.jpg", "bus.jpg"]},
            # Add more questions here
        ]

        self.current_question = None
        self.score = 0

        self.word_label = tk.Label(master, text="", font=("Arial", 24))
        self.word_label.pack(pady=20)

        self.image_frame = tk.Frame(master)
        self.image_frame.pack(pady=20)

        self.score_label = tk.Label(master, text="Score: 0", font=("Arial", 16))
        self.score_label.pack(pady=10)

        self.next_question()

    def next_question(self):
        if self.questions:
            self.current_question = random.choice(self.questions)
            self.word_label.config(text=self.current_question["word"])

            for widget in self.image_frame.winfo_children():
                widget.destroy()

            random.shuffle(self.current_question["options"])
            for i, image_file in enumerate(self.current_question["options"]):
                img = Image.open(f"word_images/{image_file}")
                img = img.resize((200, 200)) # , Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)

                btn = tk.Button(self.image_frame, image=photo, command=lambda x=image_file: self.check_answer(x))
                btn.image = photo
                btn.grid(row=0, column=i, padx=10)

                speak_btn = tk.Button(self.image_frame, text="Speak", command=lambda x=image_file: self.speak_word(x))
                speak_btn.grid(row=1, column=i, padx=10, pady=5)
        else:
            messagebox.showinfo("Quiz Completed", f"Quiz completed! Your final score is {self.score}")

    def check_answer(self, selected_image):
        if selected_image == self.current_question["correct"]:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            messagebox.showinfo("Correct", "That's correct!")
        else:
            messagebox.showinfo("Incorrect",
                                f"Sorry, that's incorrect. The correct answer was {self.current_question['correct']}")

        self.questions.remove(self.current_question)
        self.next_question()

    def speak_word(self, image_file):
        word = os.path.splitext(image_file)[0].capitalize()
        tts = gtts.gTTS(word)
        # TODO: generate in a cache directory by the word name.
        tts.save("temp.mp3")
        playsound("temp.mp3")
        os.remove("temp.mp3")


if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageQuizApp(root)
    root.mainloop()
