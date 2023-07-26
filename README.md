# Why Personal Papers Recommender?

There is about 500 new daily papers in arXiv's `cs` category, a few tens in `cs.AI` alone. With the recent Generative AI craze, it was impossible for me to keep up with the speed at which papers were published, to distil the ones that I should read given the current focus of my work and the work of my employer in the space.

This project is spawn from the following requirements:

 - It needs to be embodied as a command line tool, something I can run from the command line or that can be run as a cron job
 - It needs to get access to all the latest papers on [arXiv](https://arxiv.org)
 - It needs to be integrated with [Zotero](https://www.zotero.org), which is my papers management tool by excellence
 - It needs to propose `x` number of possibly relevent papers
   - Proposed papers can be accessed from the command line
   - Proposed papers can be uploaded to Zotero
 - Proposed relevent papers should be related to the papers I am currently interested in

# Requirements

## Zotero Account

## Cohere Account

# Install

# Cnfigure

# Usage

# How it works?

# Future Work

 - Adding an abstraction layer to enable multiple diffgerent embedding services. Currently only Cohere is used for the initial version. LangChain could potentially be an option as an abstraction layer for that purpose.
 - Adding an abstraction layer to integrate more paper sources than just arXiv
 - Improve tests beyond testing utility functions by mocking external services, etc.
 - Add functionality to the command line tool to have the user configuring it directly in the command line with proper prompts, etc.
 - At the moment, every time `readnext` is run, it gets today's latest papers from `arXiv`, checks which papers are currently of interests, and match all harvested papers against the current personal research focus. Eventually, we may want to add more capabilities in this area such that we restrict the proposed papers to be today's paper only for example, etc.

# License

