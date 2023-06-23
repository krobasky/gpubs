from typing import List, Dict, Set
import os

from gpubs.models import ReferenceData
from gpubs.log import msg1, msg2
from gpubs.reference import download_gene_symbols, extract_gene_data
from gpubs.search_words import fetch_brown_corpus, create_stop_words, read_search_stop, filter_search_terms
from gpubs.fetch import check_disk_space, download_file, verify_md5
from gpubs.parse import get_pub_df

def create_gene_reference_data(m: ReferenceData):
    
    raw_gene_info_filepath = os.path.join(m.raw_path(), m.gene_info_filename)
    reference_gene_symbols_filepath = os.path.join(m.reference_path(), m.gene_symbols_filename)
    reference_gene_synonyms_filepath = os.path.join(m.reference_path(), m.gene_synonyms_filename)
    dbxref_path = m.dbxref_path()
    verbose = m.verbose
    url = m.ncbi_gene_info_url
    
    # Download the gene symbols file
    download_gene_symbols(output_filepath = raw_gene_info_filepath, url = url, verbose = verbose)

    # Extract gene data
    gene_symbols, dbxrefs, gene_synonyms = extract_gene_data(filepath = raw_gene_info_filepath)

    # Save gene symbols to a file
    with open(reference_gene_symbols_filepath, "w") as file:
        for symbol in gene_symbols:
            file.write(symbol + "\n")

    msg2(verbose, f"Gene symbols saved to {reference_gene_symbols_filepath}")

    # Save dbXrefs to separate files
    for identifier in dbxrefs:
            identifier_parts = identifier.split(":")
            identifier_type = identifier_parts[0].replace('/','_')
            identifier_value = ":".join(identifier_parts[1:])
            filename = f"{dbxref_path}/{identifier_type}.txt"
            with open(filename, "a") as file:
                file.write(identifier_value + "\n")

    """
    for identifiers in dbxrefs:
        for identifier in identifiers:
            identifier_parts = identifier.split(":")
            identifier_type = identifier_parts[0].replace('/','_')
            identifier_value = ":".join(identifier_parts[1:])
            filename = f"{dbxref_path}/{identifier_type}.txt"
            with open(filename, "a") as file:
                file.write(identifier_value + "\n")
    """
    msg2(verbose, "dbXrefs saved to individual files.")

    # Save gene synonyms to a file
    with open(reference_gene_synonyms_filepath, "w") as file:
        for synonym in gene_synonyms:
            file.write(synonym + "\n")

    msg2(verbose, f"Gene synonyms saved to {reference_gene_synonyms_filepath}")

def create_frequency_list(m: ReferenceData) -> List:
    
    frequency_list_outpath = os.path.join(m.search_path(), m.frequency_list_filename)
    stop_word_list_length = m.corpus_stop_word_list_length
    verbose = m.verbose
    
    import nltk
    from nltk import FreqDist
    import string

    words = fetch_brown_corpus()

    # Remove punctuation and convert to lowercase
    words = [word.lower() for word in words if word not in string.punctuation and word.isalnum()]

    # Compute the frequency distribution of words
    freq_dist = FreqDist(words)

    # Get the most frequent words
    most_common_words = freq_dist.most_common(stop_word_list_length)

    # Write the frequency list to a file
    with open(frequency_list_outpath, 'w') as file:
        for word, frequency in most_common_words:
            file.write(word + '\n')
    msg2(verbose, f"Wrote {frequency_list_outpath}")
    return most_common_words

def create_search_terms_file(m: ReferenceData):
    import os

    dbxrefs = m.dbxrefs
    dbxrefs_path = m.dbxref_path()  
    gene_symbols_filepath = os.path.join(m.reference_path(), m.gene_symbols_filename)
    gene_synonyms_filepath = os.path.join(m.reference_path(), m.gene_synonyms_filename)
    search_terms_filepath = os.path.join(m.search_path(), m.search_terms_filename)
    verbose = m.verbose

    if dbxrefs == []:
        # Get a list of all files in the directory
        dbxrefs = os.listdir(dbxrefs_path)
        # Filter out directories from the list
        dbxrefs = [f for f in dbxrefs if os.path.isfile(os.path.join(dbxrefs_path, f))]
  
    
    with open(f"{search_terms_filepath}.unsorted", "w") as outfile:
        for ref in dbxrefs:
            with open(os.path.join(dbxrefs_path, ref)) as infile:
                sorted_lines = sorted(set(infile.readlines()))
                outfile.writelines(sorted_lines)
                #outfile.write(infile.read())

        with open(gene_symbols_filepath) as infile:
            sorted_lines = sorted(set(infile.readlines()))
            outfile.writelines(sorted_lines)
            #outfile.write(infile.read())

        with open(gene_synonyms_filepath) as infile:
            sorted_lines = sorted(set(infile.readlines()))
            outfile.writelines(sorted_lines)
            #outfile.write(infile.read())

    # Sort and remove duplicates from the search terms file
    search_terms_unsorted_filepath = f"{search_terms_filepath}.unsorted"
    os.system(f"sort -u {search_terms_unsorted_filepath} | grep -v not > {search_terms_filepath}")

    msg2(verbose, f"Created {search_terms_filepath}.")
    msg2(verbose, f"Created {search_terms_unsorted_filepath} - can be removed.")
    line_count = sum(1 for line in open(search_terms_filepath))
    msg2(verbose, f"Number of lines in {search_terms_filepath}: {line_count}")

def create_filtered_search_terms(m: ReferenceData) -> List:
    
    search_file = os.path.join(m.search_path(), m.search_terms_filename)
    frequency_list_outpath = os.path.join(m.search_path(), m.frequency_list_filename)
    custom_words = m.custom_stop_words
    final_file = os.path.join(m.search_path(), m.filtered_terms_filename)
    verbose = m.verbose
    
    stop_words = create_stop_words(frequency_list_outpath, custom_words)
    
    search_terms = read_search_stop(search_file = search_file, stop_words = stop_words)
    msg2(verbose, f"Number of original search_terms:{len(search_terms)}")
    final_terms, filtered_terms, matched_stop_words = filter_search_terms(search_terms, stop_words)
    msg2(verbose, f"number of filtered_terms:{len(filtered_terms)}\nfinal number of final_terms:{len(final_terms)}\n number of matched_stop_words:{len(matched_stop_words)}\nmatched_stop_words={matched_stop_words}")
    if final_file is not None:
        with open(final_file, "w") as f:
            f.writelines('\n'.join(final_terms))
    msg2(verbose, f"Created {final_file}")
    return final_terms


def fetch_abstracts(m: ReferenceData):
    import subprocess
    
    num_files = m.num_abstract_xml_files
    refresh = m.refresh_abstract_xml_files
    download_dir = m.pub_inpath()
    verbose = m.verbose
    
    """ This can probably be done faster with download_files.sh """ 
    msg2(verbose, f"Download Directory: {download_dir}")
    msg2(verbose, f"Number of abstracts to ensure have been downloaded: {num_files}")
    msg2(verbose, f"Refresh: {refresh}")

    # FTP settings
    ftp_host = "ftp.ncbi.nlm.nih.gov"
    ftp_path = "/pubmed/baseline/"

    # Retrieve file names and find the largest number
    #file_list = subprocess.check_output(['curl', '-s', f"ftp://{ftp_host}{ftp_path}"]).decode().splitlines()
    
    output = subprocess.check_output(['curl', '-s', f"ftp://{ftp_host}{ftp_path}"]).decode()
    file_list = [line.split()[-1] for line in output.splitlines() if line.endswith(".xml.gz")]

    msg2(verbose, f"Total number of NCBI abstract XML files: {len(file_list)}")
    latest_files = [file_name for file_name in file_list if file_name.startswith("pubmed23n") and file_name.endswith(".xml.gz")]
    latest_files.sort(reverse=True)
    latest_files = latest_files[:num_files]
    msg2(verbose, f"latest_files {num_files}: {latest_files}")

    # Check if enough files are available
    if len(latest_files) == 0:
        msg1(verbose, "Error: Insufficient number of files available!")
        exit(1)

    # Calculate total predicted size
    total_size = 0
    for file_name in latest_files:
        response = subprocess.check_output(['curl', '-sI', f"ftp://{ftp_host}{ftp_path}{file_name}"]).decode()
        file_size = int(response.split("Content-Length: ")[1].split("\r")[0])
        total_size += file_size

    # Check disk space before downloading
    check_disk_space(total_size, download_dir, verbose=verbose)

    # Download and check files
    for file_name in latest_files:
        md5_file_name = f"{file_name}.md5"
        file_path = os.path.join(download_dir, file_name)
        md5_file_path = os.path.join(download_dir, md5_file_name)

        # Refresh files that were previously downloaded?
        if not refresh:
            # No, so skip downloading those again

            # If one file or the other is missing, you still have to do a download
            # Here, just provide information as to which files are present.
            if os.path.isfile(file_path) and not os.path.isfile(md5_file_path):
                msg1(verbose, f"ERROR: Missing - {md5_file_path}; re-downloading now")
            if not os.path.isfile(file_path) and os.path.isfile(md5_file_path):
                msg1(verbose, f"ERROR: Missing - {file_path}; re-downloading now")

            if os.path.isfile(file_path) and os.path.isfile(md5_file_path):
                msg1(verbose, f"SKIP: {file_path} exists.")
                continue

        # Check file size
        response = subprocess.check_output(['curl', '-sI', f"ftp://{ftp_host}{ftp_path}{file_name}"]).decode()
        file_size = int(response.split("Content-Length: ")[1].split("\r")[0])

        msg2(verbose, f"File: {file_name}, Size: {file_size} bytes")

        # Download file
        msg2(verbose, f"WARNING: Downloading: {file_name} to {download_dir}")
        if os.path.isfile(file_path):
            os.remove(file_path)
        download_file(f"ftp://{ftp_host}{ftp_path}{file_name}", file_path, verbose)

        # Download MD5 file
        if os.path.isfile(md5_file_path):
            os.remove(md5_file_path)
        download_file(f"ftp://{ftp_host}{ftp_path}{md5_file_name}", md5_file_path, verbose)

        # Check MD5
        verify_md5(file_path, md5_file_path, verbose)

    total_size_human = subprocess.check_output(['numfmt', '--to=iec-i', '--suffix=B', str(total_size)]).decode().strip()
    msg2(verbose, f"Total size of abstract files: {total_size_human}")

def create_pubcsv_dataset(m: ReferenceData) -> List:
    """ Takes about 14min for 30 (2 per minute) """
    
    abstract_length_threshold = m.abstract_length_threshold
    pub_inpath = m.pub_inpath()
    pub_outpath = m.pub_outpath()
    verbose = m.verbose

    import os
    import glob
    
    csv_list = []
    # Iterate through files in the directory
    for filepath in glob.glob(os.path.join(pub_inpath, "pubmed*.xml.gz")):
        msg2(verbose, f"Converting file {filepath}")
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            df = get_pub_df(filename=filename, inpath=pub_inpath, outpath= pub_outpath, prune=True, length_threshold = abstract_length_threshold, verbose = verbose)
            csv_filepath = os.path.join(pub_outpath, f"{filename}.csv")
            df.to_csv(csv_filepath, header=False, index=False, sep="\t")
            msg2(verbose, f"Wrote file:{csv_filepath}")
            csv_list.append(csv_filepath)
            
    return(csv_list)

def create_gene_files(m: ReferenceData):
    """ Calls the search.awk script in gpubs/scripts """
    
    filtered_terms_file = os.path.join(m.search_path(), m.filtered_terms_filename)
    csv_inpath = m.pub_outpath()
    csv_outpath = m.genes_outpath()
    verbose = m.verbose
    
    import glob
    import subprocess
    awk_script = "search.awk"
    # Check if awk_script is under ./scripts - e.g., this is being run from the notebook from inside the repo
    # otherwise awk_script should be in path - e.g. gpubs has been pip install'd
    if os.path.isfile(os.path.join("scripts", awk_script)):
        awk_script = os.path.join("scripts", awk_script)
    for file_name_path in glob.glob(os.path.join(csv_inpath,"pubmed*.xml.gz.csv")):
        file_name = os.path.basename(file_name_path)
        input_csv_file = os.path.join(csv_inpath, file_name)
        output_csv_file = os.path.join(csv_outpath, file_name)
        msg2(verbose, f"Creating {output_csv_file}")
        error_file = os.path.join(csv_outpath, f"{file_name}.err")
        # xxx test this out, then run make to install version 2
        command = [awk_script, filtered_terms_file, input_csv_file]
        with open(output_csv_file, "w") as output, open(error_file, "w") as error:
            subprocess.run(command, stdout=output, stderr=error)

def pipeline(m: ReferenceData):
    """ 
    Run the whole data pipeline, end to end. See QuickStart notebook for step-by-step outputs

    Example:

      import gpubs
      from gpubs.models import ReferenceData
      from gpubs.api import pipeline

      # Create data model
      m = ReferenceData(version = "../../v1",       # make data root above any git repo
                        verbose = 2,                # print all the info messages
                        num_abstract_xml_files = 3, # only fetch 3 files from NCBI
                        dbxrefs = ["AllianceGenome.txt", "Ensembl.txt", "HGNC.txt", "IMGT_GENE-DB.txt"]  # exclude miRNA and MIM
                 )
      pipeline(m)

    """

    # Fetch data/raw/gene_info.gz 
    # and create the human genes lists under data/reference (gene_symbols.txt, gene_synonyms.txt, dbxrefs/*)
    create_gene_reference_data(m)


    # The goal of the following 3 calls is to 
    # create data/search_terms/filtered_terms.txt from english language corpus

    # Create a word frequency list from an English language corpus
    _ = create_frequency_list(m)

    # Create the file of gene search terms (data/search_terms/search_terms.txt) using stop words from frequency list
    create_search_terms_file(m)

    # Create the filtered_terms.txt file
    final_terms = create_filtered_search_terms(m)


    # Fetch NCBI articl zips
    # - There are about 1100 files with about 15000 abstracts each.
    # - ~60GB is needed to get all files
    # - At about 2 min/file ... ~ 2 days to get 'em all
    fetch_abstracts(m)

    # Create CSVs from XMLs
    # - This takes about 3 minutes to do 10 files; or about 5 hours to do them all
    csv_list = create_pubcsv_dataset(m)


    # Create new CSVs that include GENES column under data/csvpubs/genes
    # - Takes about 40s for 10 files, which is much slower than just running the awk script
    # - With default settings, it filters out about 42% of the abstracts, most of which are 2022
    create_gene_files(m)
