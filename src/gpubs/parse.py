import pandas as pd
import numpy as np
import re
import os

from gpubs.log import msg1, msg2

def extract_data(element):
    data = {}
    data['PMID'] = element.findtext('MedlineCitation/PMID')
    data['Title'] = element.findtext('MedlineCitation/Article/ArticleTitle')
    data['Abstract'] = element.findtext('MedlineCitation/Article/Abstract/AbstractText')
    data['Journal'] = element.findtext('MedlineCitation/Article/Journal/Title')
    data['PublicationDate'] = element.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
    data['JournalTitle'] = element.findtext('MedlineCitation/Article/Journal/Title')
    data['ArticleType'] = element.findtext('MedlineCitation/Article/PublicationTypeList/PublicationType')
    
    # Extract the descriptor names and qualifier names from the XML
    mesh_headings = element.findall('.//MeshHeading')
    mesh_heading_list = []
    for heading in mesh_headings:
        descriptor_name = heading.findtext('DescriptorName')
        qualifier_names = [qualifier.text for qualifier in heading.findall('QualifierName')]
        mesh_heading_list.append(descriptor_name)
        mesh_heading_list.extend(qualifier_names)
    data['MeshHeadingList'] = ','.join(mesh_heading_list)
                                        
    publication_types = element.findall('MedlineCitation/Article/PublicationTypeList/PublicationType')
    data['PublicationTypeList'] = ",".join([ptype.text for ptype in publication_types])
    
    return data

def prune_df(df, length_threshold = 405, verbose=2):
    # exclude articles with no abstract, no date, or abstracts that are too short (less than length_threshold letters)
    pruned_df = df[df['Abstract'].notna() & df['PublicationDate'].notna()]

    # cut out any short articles
    all_pruned = len(pruned_df)
    msg2(verbose, f"Number of all abstracts before pruning short articles = {all_pruned}")
    pruned_df = pruned_df[pruned_df['Abstract'].str.len() >= length_threshold]
    long_pruned = len(pruned_df)
    msg2(verbose, f"Number after pruning short articles = {long_pruned}")
    msg2(verbose, f"Number discarded for being too short: {all_pruned - long_pruned}")

    return pruned_df

def get_pub_df(filename, inpath, outpath, length_threshold, prune=True,verbose=0):
    import gzip
    import xml.etree.ElementTree as ET
    import pandas as pd

    pubmed_filepath = os.path.join(inpath, filename)
    # Open the gzip'd XML file
    with gzip.open(pubmed_filepath, 'rb') as f:
        # Read the contents of the gzip'd file
        gzip_content = f.read()

    # Parse the XML content using ElementTree
    root = ET.fromstring(gzip_content)

    # Extract data from each article and store in a list
    articles = []
    for article in root.findall('.//PubmedArticle'):
        articles.append(extract_data(article))

    # Create a DataFrame from the list of articles
    df = pd.DataFrame(articles)
    df = df.drop_duplicates()
    if prune:
        msg2(verbose, f"Number of all articles:{len(df)}")
        df = prune_df(df, length_threshold = length_threshold, verbose=verbose)
        msg2(verbose, f"Number of pruned articles:{len(df)}")
    
    # convert objects to simple types
    df['PublicationDate'] = df['PublicationDate'].astype(int)

    return df
