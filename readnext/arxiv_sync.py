# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_arxiv_sync.ipynb.

# %% auto 0
__all__ = ['get_arxiv_pdfs_url', 'get_docs_path', 'delete_broken_pdf', 'sync_arxiv']

# %% ../nbs/02_arxiv_sync.ipynb 6
import concurrent.futures
import feedparser
import os
import re
import urllib.request
from pypdf import PdfReader
from .arxiv_categories import exists
from rich import print
from rich.progress import Progress

# %% ../nbs/02_arxiv_sync.ipynb 8
def get_arxiv_pdfs_url(category: str) -> list:
    "Get all the papers refferenced in the daily RSS feed on ArXiv for input 'category'."
    if exists(category):
        feed = feedparser.parse('http://arxiv.org/rss/' + category)

        # get the URL of the PDF file of each paper from the RSS feed
        return [entry.link for entry in feed.entries]
    else:
        return []

# %% ../nbs/02_arxiv_sync.ipynb 10
def get_docs_path(category: str) -> str:
    "Generate the proper docs path from a category ID"
    return os.environ.get('DOCS_PATH').rstrip('/') + '/' + category + '/'

# %% ../nbs/02_arxiv_sync.ipynb 14
def delete_broken_pdf(category: str):
    """Detect and delete broken PDF files.
       TODO Next iteration needs a better fail over with retry when PDF files are broken from a download.
    """

    docs_path = get_docs_path(category)

    # get the list of the PDF files
    pdf_files = os.listdir(docs_path)

    # try to open each PDF file
    for pdf_file in pdf_files:
        try:
            with open (docs_path + pdf_file, 'rb') as pdf_file_obj:
                PdfReader(pdf_file_obj)
        except Exception as exc:
            # delete the PDF file if it is broken
            os.remove(docs_path + pdf_file)
            print('[italic yellow]Broken file deleted: ' + docs_path + pdf_file + '   [' + str(exc) + '][/italic yellow]')

# %% ../nbs/02_arxiv_sync.ipynb 19
def sync_arxiv(category: str):
    """Synchronize all latest arxiv papers for `category`.
       Concurrently download three PDF files from ArXiv. 
       The PDF files will be saved in the `DOCS_PATH` folder 
       under the category's sub-folder.
    """

    # create the "docs" folder if it does not exist
    docs_path = get_docs_path(category)

    if not os.path.exists(docs_path):
        print("[italic yellow]Creating directory '" + docs_path + "'[/italic yellow]")
        os.makedirs(docs_path)

    with Progress() as progress:

        urls = get_arxiv_pdfs_url(category)

        task = progress.add_task("[cyan]Downloading papers...", total=len(urls))

        def progress_indicator(future):
            "Local progress indicator callback for the concurrent.futures module."
            if not progress.finished:
                progress.update(task, advance=1)

        # download each PDF from the URL list into the local "docs" folder
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            for url in urls:
                # get the name of the PDF file
                paper_name = url.split('/')[-1]

                # skip if the paper is already downloaded
                if os.path.exists(docs_path + paper_name + '.pdf'):
                    if not progress.finished:
                        progress.update(task, advance=1)
                    continue

                # transform the URL to get the URL of the PDF file
                url = re.sub('abs', 'pdf', url) + '.pdf'

                # download the PDF file
                futures = [executor.submit(urllib.request.urlretrieve, url, docs_path + paper_name + '.pdf')]

                # register the progress indicator callback for each of the future
                for future in futures:
                    future.add_done_callback(progress_indicator)

    # delete possible broken PDF files during download.
    # a better detection & fallback mechanism should be implemented in the future.
    delete_broken_pdf(category)
