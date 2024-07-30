import os
import streamlit as st
from PIL import Image
import gtts

from streamlit.components.v1 import html

from quiz_logic import QuizLogic, WordData


class StreamlitLanguageQuizApp:
    def __init__(self):
        self.audio_button = None
        self.question_fragment = None
        self.root_dir = os.path.abspath(os.path.join(__file__, "..", ".."))
        self.quiz_logic = QuizLogic(root_dir=self.root_dir)
        words_path = os.path.join(self.root_dir, "words.csv")
        self.quiz_logic.load_word_data(words_path)

        if 'current_question' not in st.session_state:
            self.next_question()
        else:
            self.quiz_logic.current_question = st.session_state.current_question
            self.quiz_logic.options = st.session_state.options

    def next_question(self):
        options = self.quiz_logic.next_question()
        st.session_state.current_question = self.quiz_logic.current_question
        st.session_state.options = options
        st.session_state.answered = False
        st.session_state.message = ''

    @st.fragment
    def show_word(self):
        # Display word
        st.header(st.session_state.current_question.word)

        # Display images
        cols = st.columns(3)
        for i, option in enumerate(st.session_state.options):
            with cols[i]:
                image_path = self.quiz_logic.image_path_for_word(option)
                image = Image.open(image_path)
                st.image(image, use_column_width=True)

                if st.button(f"Select {option.word}", key=f"select_{i}"):
                    self.check_answer(option)

                self.audio_element_for_word(option.word)

        # Display message
        if 'message' in st.session_state:
            st.write(st.session_state.message)

        # Next question button
        if st.session_state.get('answered', False):
            if st.button("Next Question"):
                self.next_question()
                st.rerun(scope="fragment")

    def run(self):
        st.title("Language Quiz App")
        self.show_word()

        # Display score
        st.sidebar.metric("Score", self.quiz_logic.score)

    def check_answer(self, selected_option: WordData):
        correct = self.quiz_logic.check_answer(selected_option)
        if correct:
            st.session_state.message = f"That's correct! \n\nDefinition: {st.session_state.current_question.definition}"
            self.speak_text("Yes, that's correct!")
        else:
            st.session_state.message = f"""Sorry, that's incorrect. The correct answer was {st.session_state.current_question.word}.
            Definition: {st.session_state.current_question.definition}"""
            self.speak_text("Sorry, that's incorrect!")

        st.session_state.answered = True

    def audio_element_for_word(self, word: str):
        sound_path = self.quiz_logic.sound_path_for_word(WordData(word, "", "", ""))
        return self.show_audio(sound_path, word)

    def speak_text(self, text: str):
        safe_name = ''.join(c if c.isalnum() else "_" for c in text)
        sound_path = os.path.join(self.root_dir, "word_sounds", safe_name.lower() + ".mp3")
        return self.show_audio(sound_path, safe_name, hidden=True, autoplay=True)

    def show_audio(self, sound_path, word, hidden=False, autoplay=False):
        self.generate_sound_if_not_found(word, sound_path)
        audio_file = open(sound_path, 'rb')
        audio_bytes = audio_file.read()
        audio_elem = st.audio(audio_bytes, format='audio/mp3', autoplay=autoplay)
        if hidden:
            st.markdown('<style>audio {display: none}</style>', unsafe_allow_html=True)

        return audio_elem

    @staticmethod
    def generate_sound_if_not_found(text, sound_path: str):
        if not os.path.exists(sound_path):
            tts = gtts.gTTS(text)
            tts.save(sound_path)


if __name__ == "__main__":
    app = StreamlitLanguageQuizApp()
    app.run()
