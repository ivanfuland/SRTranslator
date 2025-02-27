import os
import argparse
import logging
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .srt_file import SrtFile
from .ass_file import AssFile
from .translators.deepl_api import DeeplApi

parser = argparse.ArgumentParser(description="Translate an .STR and .ASS file")

parser.add_argument(
    "filepath",
    metavar="path",
    type=str,
    help="File to translate",
)

parser.add_argument(
    "-i",
    "--src-lang",
    type=str,
    default="auto",
    help="Source language. Default: auto",
)

parser.add_argument(
    "-o",
    "--dest-lang",
    type=str,
    default="es",
    help="Destination language. Default: es (spanish)",
)

parser.add_argument(
    "-v",
    "--verbose",
    action="store_const",
    dest="loglevel",
    const=logging.INFO,
    help="Increase output verbosity",
)

parser.add_argument(
    "-vv",
    "--debug",
    action="store_const",
    dest="loglevel",
    const=logging.DEBUG,
    default=logging.WARNING,
    help="Increase output verbosity for debugging",
)

parser.add_argument(
    "-s",
    "--show-browser",
    action="store_true",
    help="Show browser window",
)

parser.add_argument(
    "-w",
    "--wrap-limit",
    type=int,
    default=50,
    help="Number of characters -including spaces- to wrap a line of text. Default: 50",
)

parser.add_argument(
    "-t",
    "--translator",
    type=str,
    choices=["deepl-api"],
    help="Built-in translator to use",
    default="deepl-api",
)

parser.add_argument(
    "--auth",
    type=str,
    help="Api key if needed on translator",
)


builtin_translators = {
    "deepl-api": DeeplApi,
}

args = parser.parse_args()
logging.basicConfig(level=args.loglevel)

try:
    os.environ.pop("MOZ_HEADLESS")
except:
    pass

if not args.show_browser:
    os.environ["MOZ_HEADLESS"] = "1"

translator_args = {}
if args.auth:
    translator_args["api_key"] = args.auth
else:
    # Try to get API key from environment variable if not provided via command line
    api_key = os.getenv("DEEPL_API_KEY")
    if api_key:
        translator_args["api_key"] = api_key

translator = builtin_translators[args.translator](**translator_args)

try:
    sub = AssFile(args.filepath)
except AttributeError:
    print("... Exception while loading as ASS try as SRT")
    sub = SrtFile(args.filepath)

try:
    sub.translate(translator, args.src_lang, args.dest_lang)
    sub.wrap_lines(args.wrap_limit)
    sub.save(f"{os.path.splitext(args.filepath)[0]}_{args.dest_lang}{os.path.splitext(args.filepath)[1]}")
except:
    sub.save_backup()
    traceback.print_exc()

translator.quit()
