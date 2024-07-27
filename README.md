# PyTkQuiz

PyTkQuiz is a desktop GUI application built with Python and Tkinter, designed to help language learners improve their vocabulary through an interactive quiz format.

## Features

- Image-based quizzes for efficient language learning
- Text-to-speech functionality for pronunciation practice
- Customizable word list via CSV file
- Score tracking to monitor progress
- Simple and intuitive user interface

## Installation

To run PyTkQuiz, you'll need Python 3.x installed on your system. Follow these steps to get started:

1. Clone the repository:
   ```
   git clone https://github.com/ranton256/pytkquiz.git
   ```

2. Navigate to the project directory:
   ```
   cd pytkquiz
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure you have a CSV file named `words.csv` in the project directory, containing your word list in the following format:
   ```
   Word,Image,Sound,Definition
   Apple,apple.jpg,apple.mp3,A round fruit with red, yellow, or green skin and white flesh
   ...
   ```

2. Place corresponding image files (e.g., `apple.jpg`) in the `word_images` folder.

3. Run the application:
   ```
   python main.py
   ```

4. Click on the image that matches the displayed word. Use the "Speak" button to hear the pronunciation of each option.

5. Your score will be displayed and updated as you progress through the quiz.

## Customization

You can easily customize the word list by modifying the `words.csv` file.
Ensure that you have corresponding image files for any new words you add.

## Contributing

Contributions to PyTkQuiz are welcome! Please feel free to submit a Pull Request.

## License

Copyright 2024 Richard N. Anton. Available under the 3-clause BSD License.
See [LICENSE]('LICENSE') for complete license.

## Contact

Richard N. Anton - http://ranton.org

Project Link: https://github.com/ranton256/pytkquiz

## Acknowledgments

- This app makes use of the gTTS library for text to speech, and most of the images were generated using Google Gemini and GPT-4o.
