import unittest
from unittest.mock import patch, MagicMock

from language_quiz_app import LanguageQuizApp
from pytkquiz.sound_gen import generate_sound_if_not_found
from quiz_logic import WordData


class FakeLabel(dict):
    def __init__(self, master, **kwargs):
        super().__init__(self)
        self.master = master
        self.update(**kwargs)

    def pack(self, pady=None):
        # mostly to make lint happy.
        print(f"pack received, pady:{pady}")

    def config(self, **kwargs):
        self.update(kwargs)


class TestLanguageQuizApp(unittest.TestCase):
    def setUp(self):
        self.app = LanguageQuizApp(frame_factory=MagicMock(), label_factory=FakeLabel, button_factory=MagicMock(),
                                   image_factory=MagicMock())

    @patch("language_quiz_app.gtts.gTTS.save")
    @patch("language_quiz_app.os.path.exists")
    def test_generate_sound_if_not_found(self, mock_os_path_exists, mock_gtts_save):
        mock_os_path_exists.return_value = False

        generate_sound_if_not_found(self.app.language, "test text", "dummy_path.mp3")

        mock_gtts_save.assert_called_once()

    @patch("language_quiz_app.Image.open")
    def test_next_question(self, mock_image_open):
        word_data = [
            WordData("cat", "cat.jpg", "cat.mp3", "A small domesticated carnivorous feline mammal"),
            WordData("dog", "dog.jpg", "dog.mp3", "A domesticated wolf known for its loyalty and faithfulness."),
            WordData("goat", "goat.jpg", "goat.mp3", "A domesticated herbivorous, farm mammal with square pupils",)
        ]

        self.app.quiz_logic.set_questions(word_data)

        mock_image_open.return_value = MagicMock()

        self.app.next_question()

        self.assertTrue(self.app.current_question.word in [w.word for w in word_data])
        self.assertEqual(self.app.word_label["text"], self.app.current_question.word)
        self.assertEqual(mock_image_open.called, 1)

    @patch("language_quiz_app.LanguageQuizApp.speak_text")
    def test_check_answer_correct(self, mock_speak_text):
        word_data = [
            WordData(
                "cat", "cat.jpg", "cat.mp3", "A small domesticated carnivorous mammal"
            )
        ]
        self.app.quiz_logic = MagicMock()
        self.app.quiz_logic.current_question.return_value=word_data[0]
        self.app.quiz_logic.score = 1

        self.app.next_question()

        self.app.check_answer(self.app.current_question)

        self.assertEqual(self.app.score, 1)
        self.assertTrue("correct" in self.app.get_message())
        self.assertFalse("incorrect" in self.app.get_message())
        self.assertEqual(mock_speak_text.call_args[0][0], "Yes, that's correct!")

    @patch("language_quiz_app.LanguageQuizApp.speak_text")
    def test_check_answer_incorrect(self, mock_speak_text):
        word_data = [
            WordData(
                "cat", "cat.jpg", "cat.mp3", "A small domesticated carnivorous mammal"
            )
        ]
        self.app.next_question()

        self.app.check_answer(
            WordData(
                "dog", "dog.jpg", "dog.mp3", "A domesticated carnivorous mammal"
            )
        )

        self.assertEqual(self.app.score, 0)
        self.assertEqual(mock_speak_text.call_args[0][0], "Sorry, that's incorrect!")
        self.assertTrue("incorrect" in self.app.get_message())


class TestGenerateSoundIfNotFound(unittest.TestCase):
    def setUp(self):
        self.app = LanguageQuizApp(label_factory=FakeLabel)

    @patch("language_quiz_app.os.path.exists")
    @patch("language_quiz_app.gtts.gTTS")
    def test_generate_sound_if_not_found_existing_file(self, mock_gtts, mock_exists):
        mock_exists.return_value = True
        generate_sound_if_not_found(self.app.language, "hello", "hello.mp3")
        mock_gtts.assert_not_called()

    @patch("language_quiz_app.os.path.exists")
    @patch("language_quiz_app.gtts.gTTS")
    def test_generate_sound_if_not_found_new_file(self, mock_gtts, mock_exists):
        mock_exists.return_value = False
        mock_tts_instance = mock_gtts.return_value
        generate_sound_if_not_found(self.app.language, "world", "world.mp3")
        mock_gtts.assert_called_once_with("world")
        mock_tts_instance.save.assert_called_once_with("world.mp3")

    @patch("language_quiz_app.os.path.exists")
    @patch("language_quiz_app.gtts.gTTS")
    def test_generate_sound_if_not_found_empty_text(self, mock_gtts, mock_exists):
        mock_exists.return_value = False
        generate_sound_if_not_found(self.app.language, "", "empty.mp3")
        mock_gtts.assert_called_once_with("")

    @patch("language_quiz_app.os.path.exists")
    @patch("language_quiz_app.gtts.gTTS")
    def test_generate_sound_if_not_found_special_characters(self, mock_gtts, mock_exists):
        mock_exists.return_value = False
        generate_sound_if_not_found(self.app.language, "Hello, World!", "special.mp3")
        mock_gtts.assert_called_once_with("Hello, World!")


if __name__ == "__main__":
    unittest.main()
