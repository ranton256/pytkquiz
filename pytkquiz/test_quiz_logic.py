import unittest
from unittest.mock import patch, mock_open
from quiz_logic import QuizLogic, WordData


class TestQuizLogic(unittest.TestCase):
    def setUp(self):
        self.quiz_logic = QuizLogic("/test/root/dir")

    @patch('quiz_logic.csv.DictReader')
    @patch('quiz_logic.open', new_callable=mock_open)
    @patch('quiz_logic.os.path.exists')
    def test_load_word_data_success(self, mock_exists, mock_file, mock_reader):
        mock_exists.return_value = True
        mock_reader.return_value = [
            {"Word": "apple", "Image": "apple.jpg", "Sound": "apple.mp3", "Definition": "A fruit"},
            {"Word": "banana", "Image": "banana.jpg", "Sound": "banana.mp3", "Definition": "A yellow fruit"}
        ]

        word_data = self.quiz_logic.load_word_data("dummy_path")

        self.assertEqual(len(word_data), 2)
        self.assertEqual(word_data[0].word, "apple")
        self.assertEqual(word_data[1].word, "banana")

    @patch('quiz_logic.csv.DictReader')
    @patch('quiz_logic.open', new_callable=mock_open)
    @patch('quiz_logic.os.path.exists')
    def test_load_word_data_missing_image(self, mock_exists, mock_file, mock_reader):
        mock_exists.side_effect = [True, False]
        mock_reader.return_value = [
            {"Word": "apple", "Image": "apple.jpg", "Sound": "apple.mp3", "Definition": "A fruit"},
            {"Word": "banana", "Image": "banana.jpg", "Sound": "banana.mp3", "Definition": "A yellow fruit"}
        ]

        word_data = self.quiz_logic.load_word_data("dummy_path")

        self.assertEqual(len(word_data), 1)
        self.assertEqual(word_data[0].word, "apple")

    @patch('quiz_logic.csv.DictReader')
    @patch('quiz_logic.open', new_callable=mock_open)
    @patch('quiz_logic.os.path.exists')
    def test_load_word_data_empty_file(self, mock_exists, mock_file, mock_reader):
        mock_exists.return_value = True
        mock_reader.return_value = []

        word_data = self.quiz_logic.load_word_data("dummy_path")

        self.assertEqual(len(word_data), 0)

    @patch('quiz_logic.csv.DictReader')
    @patch('quiz_logic.open', new_callable=mock_open)
    @patch('quiz_logic.os.path.exists')
    def test_load_word_data_unicode_characters(self, mock_exists, mock_file, mock_reader):
        mock_exists.return_value = True
        mock_reader.return_value = [
            {"Word": "café", "Image": "cafe.jpg", "Sound": "cafe.mp3", "Definition": "A place to drink coffee"}
        ]

        word_data = self.quiz_logic.load_word_data("dummy_path")

        self.assertEqual(len(word_data), 1)
        self.assertEqual(word_data[0].word, "café")

    @patch('quiz_logic.csv.DictReader')
    @patch('quiz_logic.open', new_callable=mock_open)
    @patch('quiz_logic.os.path.exists')
    def test_load_word_data_missing_fields(self, mock_exists, mock_file, mock_reader):
        mock_exists.return_value = True
        mock_reader.return_value = [
            {"Word": "apple", "Image": "apple.jpg", "Sound": "apple.mp3"},
            {"Word": "banana", "Image": "banana.jpg", "Definition": "A yellow fruit"}
        ]

        with self.assertRaises(KeyError):
            self.quiz_logic.load_word_data("dummy_path")


class TestImagePathForWord(unittest.TestCase):
    def setUp(self):
        self.quiz_logic = QuizLogic("/test/root/dir")

    def test_image_path_for_word_valid(self):
        word_data = WordData("cat", "cat.jpg", "cat.mp3", "A feline animal")
        expected_path = "/test/root/dir/word_images/cat.jpg"
        self.assertEqual(self.quiz_logic.image_path_for_word(word_data), expected_path)

    def test_image_path_for_word_no_image(self):
        word_data = WordData("dog", "", "dog.mp3", "A canine animal")
        expected_path = "/test/root/dir/word_images/"
        self.assertEqual(self.quiz_logic.image_path_for_word(word_data), expected_path)

    def test_image_path_for_word_different_extension(self):
        word_data = WordData("bird", "bird.png", "bird.mp3", "A flying animal")
        expected_path = "/test/root/dir/word_images/bird.png"
        self.assertEqual(self.quiz_logic.image_path_for_word(word_data), expected_path)

    @patch("os.path.join")
    def test_image_path_for_word_os_join_called(self, mock_join):
        word_data = WordData("fish", "fish.jpg", "fish.mp3", "An aquatic animal")
        self.quiz_logic.image_path_for_word(word_data)
        mock_join.assert_called_once_with(self.quiz_logic.root_dir, "word_images", "fish.jpg")



if __name__ == '__main__':
    unittest.main()
