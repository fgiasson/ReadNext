import arxiv
import chromadb
import cohere
import os
from nameparser import HumanName
from pyzotero import zotero
from readnext.arxiv_categories import exists
from readnext.embedding import pdf_to_text
from rich import print
from rich.progress import Progress

# Configuring Zotero for the user's personal context
zot = zotero.Zotero(os.environ.get('ZOTERO_LIBRARY_ID'), os.environ.get('ZOTERO_LIBRARY_TYPE'), os.environ.get('ZOTERO_API_KEY'))

def get_collection_id_from_name(collection_name: str):
    """Return the ID of a collection from its name. 
       Return an empty string if no collection's name doesn't exists.
       The comparison is case insensitive."""
    for collection in zot.collections():
        if collection['data']['name'].lower() == collection_name.lower():
            return collection['key']
        
    return ''

def get_target_collection_items(collection_name: str):
    """Given the name of a Zotero collection, return all the items from that collection."""
    collection = get_collection_id_from_name(collection_name)

    if collection != "":        
        return zot.collection_items(collection)
    else:
        return {}

def create_interests_corpus(collection_name: str):
    """Create a corpus of interests from all the documents
    existing in a Zotero collection. This corpus will be used to
    match related daily papers published on ArXiv."""
    interests_corpus = ""

    for item in get_target_collection_items(collection_name):
        if item['data']['itemType'] != 'attachment':
            if 'title' in item['data']:
                interests_corpus = interests_corpus + ' ' + item['data']['title']
            if 'abstractNote' in item['data']:
                interests_corpus = interests_corpus + ' ' + item['data']['abstractNote']
            interests_corpus = interests_corpus + ' ' + '\n'
    
    return interests_corpus

def get_personalized_papers(category: str, zotero_collection: str, nb_proposals=10):
    """Given a ArXiv category and a Zotero personalization collection. 
    Returns a dictionary where the keys are the personalized ArXiv IDs, 
    and the value the distance to the personalization embedding."""
    chroma_client = chromadb.PersistentClient(path=os.environ.get('CHROMA_DB_PATH'))
    
    ids = {}

    if exists(category):
        papers_category_collection = chroma_client.get_or_create_collection(name=category)

        co = cohere.Client(os.environ.get('COHERE_API_KEY'))

        interests_embedding = co.embed([create_interests_corpus(zotero_collection)])

        interesting_papers = papers_category_collection.query(
            query_embeddings=interests_embedding.embeddings,
            n_results=int(nb_proposals)) # need to force int() to convert when from the command line.

        for index, pdf in enumerate(interesting_papers['ids'][0]):
            ids[pdf.rstrip('.pdf')] = str(interesting_papers['distances'][0][index]) 

    return ids

def get_pdf_summary(pdf):
    text = pdf_to_text(pdf)

    co = cohere.Client(os.environ.get('COHERE_API_KEY'))

    res = co.summarize(text[:100000], length='medium')

    return res.summary

def check_already_in_zotero_proposals(title: str):
    """Check if a paper is already in the proposals collection."""
    for item in get_target_collection_items(os.environ.get('ZOTERO_INTERESTING_PAPERS_COLLECTION')):
        if item['data']['itemType'] != 'attachment':
            if 'title' in item['data']:
                if item['data']['title'] == title:
                    return True
    
    return False

def save_personalized_papers_in_zotero(ids: dict, with_artifacts: bool):
    """Get all personalized papers propositions and upload them to the 
    `ZOTERO_INTERESTING_PAPERS_COLLECTION` Zotero collection.
    
    If `with_artifacts=True`, then all documents artifacts will be
    uploaded to Zotero as well (namely PDFs and summary documents), 
    but it will take more space to the Zotero account and will be 
    slower to process."""

    # get information for each matched articles directly from ArXiv
    search = arxiv.Search(id_list=ids.keys())

    with Progress() as progress:
        task = progress.add_task("[cyan]Uploading papers to Zotero...", total=len(list(search.results())))

        for index, result in enumerate(search.results()):
            # skip if the paper is already in the proposals collection
            if(check_already_in_zotero_proposals(result.title)):
                if not progress.finished:
                    progress.update(task, advance=1)
                continue

            # build the template for the Zotero item
            template = zot.item_template('preprint')

            template['title'] = result.title

            creators = []
            for creator in result.authors:
                name = HumanName(creator.name)
                creators.append({'creatorType': 'author', 'firstName': name.first, 'lastName': name.last})

            template['abstractNote'] = result.summary
            template['creators'] = creators
            template['url'] = result.entry_id
            template['DOI'] = result.doi
            template['repository'] = 'arXiv'
            template['archiveID'] = 'arxiv:' + result.get_short_id()
            template['libraryCatalog'] = 'arXiv.org'
            template['collections'] = [get_collection_id_from_name(os.environ.get('ZOTERO_INTERESTING_PAPERS_COLLECTION'))]

            zot.check_items([template])

            resp = zot.create_items([template])

            if '0' in resp['success']:
                if(with_artifacts):
                    parentid = resp['success']['0']
                    rec_path = os.environ.get('RECOMMENDATIONS_PATH').rstrip('/') + '/';

                    if not os.path.exists(rec_path):
                        os.makedirs(rec_path)

                    paper = next(arxiv.Search(id_list=[result.get_short_id()]).results())
                    paper.download_pdf(dirpath=rec_path, filename=result.get_short_id() + '.pdf')

                    # create a new text file
                    with open(rec_path + result.get_short_id() + '.txt', 'w') as f:
                        f.write(get_pdf_summary(rec_path + result.get_short_id() + '.pdf'))
                    
                    zot.attachment_both([[result.get_short_id() + '.pdf', rec_path + result.get_short_id() + '.pdf'],
                                        ['cohere_summary.txt', rec_path + result.get_short_id() + '.txt']], parentid)
            else:
                print("Could not upload paper to Zotero")
            
            if not progress.finished:
                progress.update(task, advance=1)