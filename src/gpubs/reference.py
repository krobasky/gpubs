from gpubs.log import msg2
import requests

def download_gene_symbols(output_filepath = "data/raw/gene_info.gz", url = "https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz", verbose=0):
    response = requests.get(url)
    response.raise_for_status()

    with open(output_filepath, "wb") as file:
        file.write(response.content)

    msg2(verbose, "Download completed.")

def extract_gene_data(filepath = "data/raw/gene_info.gz"):
    """ returns 3 sets """
    import gzip

    gene_symbols = set()
    dbxrefs = set()
    gene_synonyms = set()

    with gzip.open(filepath, "rt") as file:
        for line in file:
            if not line.startswith("#"):
                fields = line.strip().split("\t")
                gene_symbols.add(fields[2])

                # Extract dbXrefs
                dbxref_field = fields[5]
                if dbxref_field != "-":
                    identifiers = dbxref_field.split("|")
                    dbxrefs.update(identifiers)

                # Extract gene synonyms
                synonym_field = fields[4]
                if synonym_field != "-":
                    synonyms = synonym_field.split("|")
                    gene_synonyms.update(synonyms)

    return gene_symbols, dbxrefs, gene_synonyms
