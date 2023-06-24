from typing import List
import os

from gpubs.models import ReferenceData
from gpubs.log import msg1, msg2
from gpubs.reference import download_gene_symbols, extract_gene_data
from gpubs.search_words import (
    fetch_brown_corpus,
    create_stop_words,
    read_search_stop,
    filter_search_terms,
)
from gpubs.fetch import check_disk_space, download_file, verify_md5
from gpubs.parse import parse_pubs


def create_gene_reference_data(m: ReferenceData):
    """Gets gene reference data into a convenient format for creating a m.filtered_terms_files, and ultimately, tagging abstracts with gene information.

    Performs the following:

      1. Downloads gene_info.gz from m.ncbi_gene_info_url

      2. Parses gene_info.gz to create the following files:

        - m.reference_path()/m.gene_symbols_filename [default = v1/reference/gene_symbols.txt]
        - m.reference_path()/m.gene_synonyms_filename [default = v1/reference/gene_synonyms.txt]
        - m.dbxref_path()/*.txt [default = v1/reference/dbxrefs/*.txt]

    """

    raw_gene_info_filepath = os.path.join(m.raw_path(), m.gene_info_filename)
    reference_gene_symbols_filepath = os.path.join(
        m.reference_path(), m.gene_symbols_filename
    )
    reference_gene_synonyms_filepath = os.path.join(
        m.reference_path(), m.gene_synonyms_filename
    )
    dbxref_path = m.dbxref_path()
    verbose = m.verbose
    url = m.ncbi_gene_info_url

    # Download the gene symbols file
    download_gene_symbols(
        output_filepath=raw_gene_info_filepath, url=url, verbose=verbose
    )

    # Extract gene data
    gene_symbols, dbxrefs, gene_synonyms = extract_gene_data(
        filepath=raw_gene_info_filepath
    )

    # Save gene symbols to a file
    with open(reference_gene_symbols_filepath, "w") as file:
        for symbol in gene_symbols:
            file.write(symbol + "\n")

    msg2(verbose, f"Gene symbols saved to {reference_gene_symbols_filepath}")

    # Save dbXrefs to separate files
    for identifier in dbxrefs:
        identifier_parts = identifier.split(":")
        identifier_type = identifier_parts[0].replace("/", "_")
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
    """Creates a file that lists the most common English words, up to (m.corpus_stop_word_list_length) in size,
    and saves to m.search_path()/m.frequency_list_filename [default = v1/data/search_terms/frequency_list.txt]

    Returns:

      A list of most common words, most common first, all lower case

    """
    frequency_list_outpath = os.path.join(m.search_path(), m.frequency_list_filename)
    stop_word_list_length = m.corpus_stop_word_list_length
    verbose = m.verbose

    from nltk import FreqDist
    import string

    words = fetch_brown_corpus()

    # Remove punctuation and convert to lowercase
    words = [
        word.lower()
        for word in words
        if word not in string.punctuation and word.isalnum()
    ]

    # Compute the frequency distribution of words
    freq_dist = FreqDist(words)

    # Get the most frequent words
    most_common_words = freq_dist.most_common(stop_word_list_length)

    # Write the frequency list to a file
    with open(frequency_list_outpath, "w") as file:
        for word, frequency in most_common_words:
            file.write(word + "\n")
    msg2(verbose, f"Wrote {frequency_list_outpath}")
    return most_common_words


def create_search_terms_file(m: ReferenceData):
    """Uses the files from `create_gene_reference_data` to generate the list of terms for searching each abstract.

    Each abstract is searched for gene symbols, synonyms, and
    dbxref's. The file created here lists all the gene info terms to
    use for that search. The file is saved to
    m.search_path()/m.search_terms_filename [default =
    `v1/data/search_terms/search_terms.txt`].

    The file f"{m.search_path()/m.search_terms_filename}.unsorted" is a byproduct and can be discarded.

    Returns:

      A list of the search terms (gene symbols, synonyms and accession IDs)

    """

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
                # outfile.write(infile.read())

        with open(gene_symbols_filepath) as infile:
            sorted_lines = sorted(set(infile.readlines()))
            outfile.writelines(sorted_lines)
            # outfile.write(infile.read())

        with open(gene_synonyms_filepath) as infile:
            sorted_lines = sorted(set(infile.readlines()))
            outfile.writelines(sorted_lines)
            # outfile.write(infile.read())

    # Sort and remove duplicates from the search terms file
    search_terms_unsorted_filepath = f"{search_terms_filepath}.unsorted"
    os.system(
        f"sort -u {search_terms_unsorted_filepath} | grep -v not > {search_terms_filepath}"
    )

    msg2(verbose, f"Created {search_terms_filepath}.")
    msg2(verbose, f"Created {search_terms_unsorted_filepath} - can be removed.")
    line_count = sum(1 for line in open(search_terms_filepath))
    msg2(verbose, f"Number of lines in {search_terms_filepath}: {line_count}")


def create_filtered_search_terms(m: ReferenceData) -> List:
    """Filters search_terms against m.frequency_list_filename and m.custom_stop_words.

    If the search term (e.g., gene name) is also a stop word (e.g.,
    'DANGER'), then retain the term's original case. Otherwise,
    lowercase the term. Either way, add it to the list of terms to be returned.

    Ultimately, when an abstract is searched for a filtered_term, it
    will only match case if the term is a stop_word. This allows for
    more permissive matching against gene names in abstracts that use
    peculiar case.

    Returns:

      List of the terms, all lowercase, accept for those that matched an English language word in the frequency_list.

    """

    search_file = os.path.join(m.search_path(), m.search_terms_filename)
    frequency_list_outpath = os.path.join(m.search_path(), m.frequency_list_filename)
    custom_words = m.custom_stop_words
    final_file = os.path.join(m.search_path(), m.filtered_terms_filename)
    verbose = m.verbose

    stop_words = create_stop_words(frequency_list_outpath, custom_words)

    search_terms = read_search_stop(search_file=search_file, stop_words=stop_words)
    msg2(verbose, f"Number of original search_terms:{len(search_terms)}")
    final_terms, filtered_terms, matched_stop_words = filter_search_terms(
        search_terms, stop_words
    )
    msg2(
        verbose,
        f"number of filtered_terms:{len(filtered_terms)}\nfinal number of final_terms:{len(final_terms)}\n number of matched_stop_words:{len(matched_stop_words)}\nmatched_stop_words={matched_stop_words}",
    )
    if final_file is not None:
        with open(final_file, "w") as f:
            f.writelines("\n".join(final_terms))
    msg2(verbose, f"Created {final_file}")
    return final_terms


def fetch_abstracts(m: ReferenceData, get_updates: bool = False):  # noqa: C901
    """Downloads files from m.ncbi_ftp_host.

    ARGS:

      get_updates: If True then download the updatefiles, otherwise get the baseline. See : https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/README.txt

    """
    import subprocess

    num_files = m.num_abstract_xml_files
    refresh = m.refresh_abstract_xml_files
    ftp_host = m.ncbi_ftp_host
    download_dir = m.pub_inpath()
    verbose = m.verbose
    if get_updates:
        download_dir = os.path.join(download_dir, m.abstract_updatefiles_inpath)
        ftp_path = m.ncbi_ftp_updatefiles_path
        msg2(verbose, f"! Getting update files, download_dir={download_dir}.")
    else:
        ftp_path = m.ncbi_ftp_baseline_path

    """ This can probably be done faster with download_files.sh """
    msg2(verbose, f"Download Directory: {download_dir}")
    msg2(verbose, f"Number of abstracts to ensure have been downloaded: {num_files}")
    msg2(verbose, f"Refresh: {refresh}")

    # Retrieve file names and find the largest number
    # file_list = subprocess.check_output(['curl', '-s', f"ftp://{ftp_host}{ftp_path}"]).decode().splitlines()

    output = subprocess.check_output(
        ["curl", "-s", f"ftp://{ftp_host}{ftp_path}"]
    ).decode()
    msg2(verbose, f"file_list curl: curl -s ftp://{ftp_host}{ftp_path}")
    file_list = [
        line.split()[-1] for line in output.splitlines() if line.endswith(".xml.gz")
    ]

    msg2(verbose, f"Total number of NCBI abstract XML files: {len(file_list)}")
    latest_files = [
        file_name
        for file_name in file_list
        if file_name.startswith("pubmed23n") and file_name.endswith(".xml.gz")
    ]
    latest_files.sort(reverse=True)
    latest_files = latest_files[:num_files]
    msg2(verbose, f"latest_files {num_files}: {latest_files}")

    # Check if enough files are available
    import sys

    if len(latest_files) == 0:
        msg1(verbose, "Error: Insufficient number of files available!")
        sys.exit(1)

    # Calculate total predicted size
    total_size = 0
    for file_name in latest_files:
        response = subprocess.check_output(
            ["curl", "-sI", f"ftp://{ftp_host}{ftp_path}{file_name}"]
        ).decode()
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
        response = subprocess.check_output(
            ["curl", "-sI", f"ftp://{ftp_host}{ftp_path}{file_name}"]
        ).decode()
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
        download_file(
            f"ftp://{ftp_host}{ftp_path}{md5_file_name}", md5_file_path, verbose
        )

        # Check MD5
        verify_md5(file_path, md5_file_path, verbose)

    total_size_human = (
        subprocess.check_output(["numfmt", "--to=iec-i", "--suffix=B", str(total_size)])
        .decode()
        .strip()
    )
    msg2(verbose, f"Total size of abstract files: {total_size_human}")


def create_pubcsv_dataset(m: ReferenceData, parse_updates: bool = False) -> List:
    """Parse all the XML files into csv files. Overwites anything previously written. Takes about 14min for 30 (2-3 per minute)

    ARGS:

      parse_updates: If True then parse the updatefiles, otherwise parse the baseline. See : https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/README.txt

    """
    import os

    abstract_length_threshold = m.abstract_length_threshold
    pub_inpath = m.pub_inpath()
    pub_updatefiles_inpath = os.path.join(m.pub_inpath(), m.abstract_updatefiles_inpath)
    if parse_updates:
        pub_inpath = os.path.join(pub_inpath, m.abstract_updatefiles_inpath)
    pub_outpath = m.pub_outpath()
    verbose = m.verbose

    csv_list = []

    # Iterate through files in the directory
    csv_list = parse_pubs(
        inpath=pub_inpath,
        outpath=pub_outpath,
        length_threshold=abstract_length_threshold,
        csv_list=csv_list,
        verbose=verbose,
    )

    # Repeat for 'updatefiles'
    csv_list = parse_pubs(
        inpath=pub_updatefiles_inpath,
        outpath=pub_outpath,
        length_threshold=abstract_length_threshold,
        csv_list=csv_list,
        verbose=verbose,
    )

    return csv_list


def create_gene_files(m: ReferenceData):
    """Calls the search.awk script in gpubs/scripts. This results in
    all the abstracts files being tagged with the gene
    name/identifier, if present. Uses the m.filtered_terms_filename for search terms.

    If the search term is also a 'stop word', then search.awk matches
    case from filtered_terms.txt (which ultimately comes from NCBI's
    gene_info.gz). Otherwise, case is permissive to accommodate
    abstracts that use peculiar case for a gene. Note that terms in
    filtered_terms.txt are also all lowercase for performance, accept
    those that are stop words.

    Note - to use a custom list of gene symbols/synonyms/accession
    ids, just filter everything out of the filtered_terms.txt except
    the genes of interest. Find the filtered_terms.txt file in
    m.search_path()/m.filtered_terms_filename [default:
    v1/data/search_terms/filtered_terms.txt]

    This is the last setp of the pipeline

    Exmample usage:

    >>> m = ReferenceData()
    >>> create_gene_reference_data(m) # get gene_info from NCBI
    >>> _ = create_frequency_list(m)  # create English stop words from 'brown' corpus
    >>> create_search_terms_file(m)   # combine the files parsed out of gene_info to get search terms
    >>> _ = create_filtered_search_terms(m)  # filter search terms with stop words
    >>> fetch_abstracts(m)            # download abstract XML files from NCBI
    >>> fetch_abstracts(m, get_updates=True) # download abstract XML "updatefiles" from NCBI
    >>> _ = create_pubcsv_dataset(m)  # translate abstract XML files to csv
    >>> # NOTE: keep only genes of interest in v1/data/search_terms/filtered_terms.txt
    >>> create_gene_files(m)          # tag abstracts with the search terms (genes) from filtered_terms.txt
    >>> # final files in m.genes_outpath [default= v1/data/csvpubs/genes]

    """

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
    for file_name_path in glob.glob(os.path.join(csv_inpath, "pubmed*.xml.gz.csv")):
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
    """Run the whole data pipeline, end to end. See QuickStart notebook for step-by-step outputs

    Example usage:

      >>> import gpubs
      >>> from gpubs.models import ReferenceData
      >>> from gpubs.api import pipeline
      >>>
      >>> # Create data model
      >>> # exclude miRNA and MIM dbxrefs
      >>> m = ReferenceData(version = "../../v1",       # put data above the github repo
      >>>                   verbose = 2,                # print info messages
      >>>                   num_abstract_xml_files = 3, # only download 3 abstract XML files from NCBI
      >>>                   dbxrefs = ["AllianceGenome.txt", "Ensembl.txt", "HGNC.txt", "IMGT_GENE-DB.txt"])
      >>> pipeline(m)

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
    _ = create_filtered_search_terms(m)

    # Fetch NCBI article zips
    # - There are 1165 files (2023) with about 15000 abstracts each.
    # - ~60GB is needed to get all files
    # - On AWS you can get them all in under an hour. 5 hours on consumer-grade wifi.
    fetch_abstracts(m)

    # Get NCBI
    # ~ 222 abstracts in June 2023
    fetch_abstracts(m, get_updates=True)

    # Create CSVs from XMLs
    # - This takes about 3 minutes to do 10 files; or about 5 hours to do them all
    _ = create_pubcsv_dataset(m)

    # Create new CSVs that include GENES column under data/csvpubs/genes
    # - Takes about 40s for 10 files, which is much slower than just running the awk script
    # - With default settings, it filters out about 42% of the abstracts, most of which are 2022
    create_gene_files(m)
