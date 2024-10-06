import os

import gtts


def generate_sound_if_not_found(language, text, sound_path: str):
    """
    Generates a sound file for the given text if it doesn't already exist.

    Args:
        text (str): The text to generate the sound file for.
        sound_path (str): The path to save the generated sound file.

    Returns:
        None
    """
    if not os.path.exists(sound_path):
        if language == "en":
            tts = gtts.gTTS(text)
        else:
            tts = gtts.gTTS(text, lang=language, slow=False)
        tts.save(sound_path)
        print(f"Generated sound for {sound_path}")