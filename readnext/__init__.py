import os
from dotenv import load_dotenv
from rich import print

__version__ = "0.0.3"

load_dotenv()

# check for the existance of all configuration options
def config_exists(env_var: str):
    v = env_var.upper()
    if not os.environ.get(v) or os.environ.get(v) == '':
        print("[bold red]Error:[/bold red] [italic red]Configuration option not set.[/italic red] [yellow]Please set the [bold]" + v + "[/bold] environment variable.[/yellow]\n")
        exit()

config_exists('ZOTERO_API_KEY')
config_exists('ZOTERO_LIBRARY_TYPE')
config_exists('ZOTERO_LIBRARY_ID')
config_exists('COHERE_API_KEY')
config_exists('CHROMA_DB_PATH')
config_exists('DOCS_PATH')
config_exists('RECOMMENDATIONS_PATH')
