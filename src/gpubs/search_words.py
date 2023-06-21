from typing import List, Dict, Set

import nltk
from nltk import FreqDist
import string

def fetch_brown_corpus():
    from nltk.corpus import brown
    corpus = 'brown'
    # Select a specific category from the Brown Corpus for analysis
    category = 'learned'
    # Load the Brown Corpus
    nltk.download('brown')
    # Get the words from the selected category
    words = brown.words(categories=category)
    return words

def read_search_stop(search_file, stop_words):
    # Load search terms from the file into a set
    search_terms=[]
    with open(search_file, 'r') as f:
        search_terms = [line.strip() for line in f]
    return search_terms

def filter_search_terms(search_terms, stop_words):
    filtered_terms = []
    matched_stop_words = []
    
    # get the matched stop words and keep in original case
    for term in search_terms:
        if term.lower() in stop_words:
            matched_stop_words.append(term)

    # get the filtered terms, lower case them
    filtered_terms = [term.lower() for term in search_terms if term.lower() not in stop_words]

    # add the two lists together so the matched terms retain original case
    # this will allow for finding genes that are also common english words
    final_terms = filtered_terms + matched_stop_words
    return (final_terms, filtered_terms, matched_stop_words)

def create_stop_words(frequency_list_outpath, custom_words) -> Set:
    from nltk.corpus import stopwords

    # Download the stopwords corpus
    nltk.download('stopwords')

    # Load the existing stop words
    stop_words = set(stopwords.words('english'))

    # Read the words from the frequency_list.txt file
    with open(frequency_list_outpath, 'r') as file:
        frequency_words = file.read().splitlines()

    # Add the frequency words to the stop words set
    stop_words.update(frequency_words)

    # Add custom words
    stop_words.update(custom_words)
    return stop_words
