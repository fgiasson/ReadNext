import arxiv
import typer
from readnext.arxiv_categories import exists, main, sub
from readnext.arxiv_sync import sync_arxiv
from readnext.embedding import embed_category_papers
from readnext.personalize import get_personalized_papers, save_personalized_papers_in_zotero
from rich import print
from typing_extensions import Annotated

app = typer.Typer()

@app.command()
def arxiv_top_categories():
    "Display ArXiv main categories. Keys are case sensitive."
    print(main)

@app.command()
def arxiv_sub_categories():
    "Display ArXiv sub categories. Keys are case sensitive."
    print(sub)

@app.command()
def personalized_papers(category: str, 
                        zotero_collection: str, 
                        save_in_zotero: Annotated[bool, 
                                                  typer.Option("--save-in-zotero", 
                                                               "-s",
                                                               help="Save personalized papers in Zotero.")] = False, 
                        with_artifacts: Annotated[bool, 
                                                  typer.Option("--with-artifacts", 
                                                               "-a",
                                                               help="Add paper artifacts (PDFs & summary files) to Zotero when saving.")] = False,                                                               
                        nb_proposals=10):
    """Get personalized papers of a `zotero-collection` from an ArXiv `category`. 
    If the category is `all` then all categories that have been locally synced will be used.
    if --in_zotero is set to True, then the papers will be uploaded to the 
    `ZOTERO_INTERESTING_PAPERS_COLLECTION` Zotero collection, which is the default behaviour,
    otherwise it will only be displayed to the command line.
    """

    # Step 1: Make sure the category exists
    if exists(category):
        # Step 2: get today's list of papers from arXiv
        print("[green]Syncing today's ArXiv latest papers...[/green]")
        sync_arxiv(category)

        # Step 3: create embeddings for each of those new papers
        print("[green]Creating embeddings for each new paper...[/green]")
        embed_category_papers(category)

        # Step 4: get personalized papers
        print("[green]Get personalized papers...[/green]")
        ids = get_personalized_papers(category, zotero_collection, nb_proposals)

        # Step 5: save personalized papers in Zotero
        if bool(save_in_zotero):
            print("[green]Saving personalized papers in Zotero...[/green]")
            save_personalized_papers_in_zotero(ids, with_artifacts)

        # Step 6: display personalized papers to the command line
        search = arxiv.Search(id_list=ids.keys())

        for index, result in enumerate(search.results()):
            print(str(index + 1) + '. [italic yellow][' + list(ids.values())[index] + '][/italic yellow]  [blue][link=' + str(result) + ']' + result.title + '[/link][/blue]')
    else:
        print("[bold red]Error:[/bold red] [italic red]ArXiv category, or sub-category ID non existing.[/italic red] Please specify a valid category ID.")

if __name__ == "__main__":
    app()