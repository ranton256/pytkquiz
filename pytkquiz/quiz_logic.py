import csv
import os
import random
from collections import namedtuple

WordData = namedtuple("WordData", ["word", "image", "sound", "definition", "filename"])


class QuizLogic:
    def __init__(self, root_dir, language:str = "en"):
        self.root_dir = root_dir
        self.questions = []
        self.current_question = None
        self.score = 0
        self.attempts = 0
        self.language = language

    def load_word_data(self, path, word_col_index):
        word_data = []
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            col_names = reader.fieldnames
            if word_col_index < 0 or word_col_index >= len(col_names):
                raise ValueError(
                    f"Invalid word column index: {word_col_index}. Must be between 0 and {len(col_names) - 1}."
                )
            word_col_name = col_names[word_col_index]
            for row in reader:
                filename = row['Word'] if self.language == 'en' else row['Transliteration']
                filename = filename.lower()
                new_word = WordData(
                    word=row[word_col_name],
                    image=row["Image"],
                    sound=row["Sound"],
                    definition=row["Definition"],
                    filename=filename,
                )
                image_path = self.image_path_for_word(new_word)
                if not os.path.exists(image_path):
                    print(
                        f"Skipping word {new_word.word}, missing image file {image_path}"
                    )
                else:
                    word_data.append(new_word)
        self.set_questions(word_data)

        return word_data

    def next_question(self):
        if self.questions:
            options = random.sample(self.questions, 3)
            self.current_question = options[0]
            random.shuffle(options)
            return options
        return None

    def check_answer(self, selected_option):
        self.attempts += 1
        if selected_option == self.current_question:
            self.score += 1
            return True
        return False

    def get_score(self):
        return self.score

    def get_attempts(self):
        return self.attempts

    def image_path_for_word(self, option):
        image_path = os.path.join(self.root_dir, "word_images", option.image)
        return image_path

    def sound_path_for_word(self, option):
        sound_dir = "word_sounds" if self.language == "en" else f"word_sounds_{self.language}"
        filename = option.filename
        return os.path.join(
            self.root_dir, sound_dir, filename + ".mp3"
        )

    def set_questions(self, word_data):
        self.questions = word_data
