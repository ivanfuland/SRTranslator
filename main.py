import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SRT File
from srtranslator import SrtFile
# ASS File
# from srtranslator import AssFile

from srtranslator.translators.deepl_api import DeeplApi

# Get API key from environment variable
api_key = os.getenv("DEEPL_API_KEY")
if not api_key:
    raise ValueError("DEEPL_API_KEY environment variable is not set. Please set it in a .env file or in your environment.")

translator = DeeplApi(api_key)
filepath = "./filepath/test.srt"

# SRT File
sub = SrtFile(filepath)
# ASS File
# sub = AssFile(filepath)

# Translate
sub.translate(translator, "en", "zh")

# Making the result subtitles prettier
sub.wrap_lines()

sub.save(f"{os.path.splitext(filepath)[0]}_translated.srt")

translator.quit()
