import chromadb
import cohere
import os
from chromadb.errors import IDAlreadyExistsError
from pypdf import PdfReader
from readnext.arxiv_categories import exists
from readnext.arxiv_sync import get_docs_path
from rich import print
from rich.progress import Progress

def pdf_to_text(file_path):
    """Read a PDF file and output it as a text string."""
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PdfReader(pdf_file_obj)
    text = ''

    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

def get_pdfs_from_folder(folder_path: str):
    """Given a folder path, return all the PDF files existing in that folder."""
    pdfs = []

    for pdf in os.listdir(folder_path):
        if pdf.endswith(".pdf"):
            pdfs.append(pdf)

    return pdfs

def embed_category_papers(category: str):
    """Given a ArXiv category, create the embeddings for each of the PDF paper existing locally.
    Embeddings is currently using Cohere's embedding service.
    Returns True if successful, False otherwise."""

    co = cohere.Client(os.environ.get('COHERE_API_KEY'))

    chroma_client = chromadb.PersistentClient(path=os.environ.get('CHROMA_DB_PATH'))

    if exists(category):
        # We create two Chroma collection of embeddings:
        #   1. a general one with all and every embeddings called 'all'
        #   2. one for the specific ArXiv category
        papers_all_collection = chroma_client.get_or_create_collection(name="all")
        papers_category_collection = chroma_client.get_or_create_collection(name="zotero_" + category)

        with Progress() as progress:
            folder_path = get_docs_path(category)
            pdfs = get_pdfs_from_folder(folder_path)

            task = progress.add_task("[cyan]Embedding papers...", total=len(pdfs))

            for pdf in pdfs:
                # check if the PDF file has already been embedded and indexed in Chromadb,
                # let's not do all this processing if that is the case.
                check_pdf = papers_all_collection.get(ids=[pdf])

                if not progress.finished:
                    progress.update(task, advance=1)

                if len(check_pdf['ids']) == 0:
                    doc = pdf_to_text(folder_path.rstrip('/') + '/' + pdf)

                    # get the embedding of the paper from Cohere
                    embedding = co.embed([doc])

                    try:
                        papers_all_collection.add(
                            embeddings=embedding.embeddings,
                            documents=[doc.encode("unicode_escape").decode()], # necessary escape to prevent possible encoding errors when adding to Chroma
                            metadatas=[{"source": pdf,
                                        "category": category}],
                            ids=[pdf]
                        )
                    except IDAlreadyExistsError:
                        print("[yellow]ID already existing in Chroma DB, skipping...[/yellow]")
                        continue
                        
                    try:
                        papers_category_collection.add(
                            embeddings=embedding.embeddings,
                            documents=[doc.encode("unicode_escape").decode()], # necessary escape to prevent possible encoding errors when adding to Chroma
                            metadatas=[{"source": pdf}],
                            ids=[pdf]
                        )
                    except IDAlreadyExistsError:
                        print("[yellow]ID already existing in Chroma DB, skipping...[/yellow]")
                        continue
        return True
    else:
        print("[red]Can't persist embeddings in local vector db, ArXiv category not existing[/red]")
        return False