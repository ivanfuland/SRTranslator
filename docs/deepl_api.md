# DeepL API Translator

## Usage

```python
import os
from dotenv import load_dotenv
from srtranslator.translators.deepl_api import DeeplApi

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("DEEPL_API_KEY")
if not api_key:
    raise ValueError("DEEPL_API_KEY environment variable is not set")

translator = DeeplApi(api_key)

translator.translate(text, source_language, destination_language)

translator.quit() # Optional
```

## Glossary Support

The translator now supports using a glossary for consistent translations of specific terms. The glossary is stored in a CSV file at `glossary/glossary.csv` with the following format:

```
source_term,target_term
Transformer,Transformer
Token,Token
Activation Function,激活函数
```

Features:
- The glossary is automatically created or updated when the CSV file is modified
- The glossary is named "myllm_glossary" in the DeepL API
- The translator will automatically use the glossary when translating
- If there are any issues with the glossary, the translator will fall back to translation without the glossary

### Setting up your API key

1. Sign up for a DeepL API account at https://www.deepl.com/pro-api
2. Create a `.env` file in your project root (you can copy from `.env.example`):
```
DEEPL_API_KEY=your-api-key-here
```

### From CLI:

You can either use the API key from your environment variables:

```bash
python -m srtranslator --translator deepl-api -i src_lang -o target_lang /path/to/srt
```

Or provide it directly via the command line:

```bash
python -m srtranslator --translator deepl-api --auth YOUR_API_KEY -i src_lang -o target_lang /path/to/srt
```

## Supported languages

`Refer to deepl-api docs, but should be the same ones in the scraper`

## Limitations

Change the translator character limit (set in 1500 by default) if use a paid API version. You can translate more than that at once.
