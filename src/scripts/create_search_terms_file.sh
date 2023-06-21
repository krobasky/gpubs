#!/bin/bash

# Default variable values
root_dir="v4/data"
reference_dir="reference"
dbxrefs_dir="dbxrefs"
dbxrefs="AllianceGenome.txt Ensembl.txt HGNC.txt IMGT_GENE-DB.txt"
search_dir="search_terms"
search_terms_filename="search_terms.txt"
gene_symbols_filename="gene_symbols.txt"
gene_synonyms_filename="gene_synonyms.txt"
verbose=0

# Usage function
usage() {
  echo "Usage: $0 [--root-dir <root_directory>] [--ref-dir <reference_directory>] [--dbx-dir <dbxrefs_directory>] [--dbx <dbxrefs>] [--search-dir <search_directory>] [--search-file <search_terms_filename>] [--gene-symbols <gene_symbols_filename>] [--gene-synonyms <gene_synonyms_filename>] [--verbose <verbosity_level>] [--help]"
  echo "Options:"
  echo "  --root-dir <root_directory>: Set the root directory path (default: 'v4/data')"
  echo "  --ref-dir <reference_directory>: Set the reference directory name (default: 'reference')"
  echo "  --dbx-dir <dbxrefs_directory>: Set the dbxrefs directory name (default: 'dbxrefs')"
  echo "  --dbx <dbxrefs>: Set the dbxrefs file names separated by space (default: 'AllianceGenome.txt Ensembl.txt HGNC.txt IMGT_GENE-DB.txt')"
  echo "  --search-dir <search_directory>: Set the search directory name (default: 'search_terms')"
  echo "  --search-file <search_terms_filename>: Set the search terms filename (default: 'search_terms.txt')"
  echo "  --gene-symbols <gene_symbols_filename>: Set the gene symbols filename (default: 'gene_symbols.txt')"
  echo "  --gene-synonyms <gene_synonyms_filename>: Set the gene synonyms filename (default: 'gene_synonyms.txt')"
  echo "  --verbose <verbosity_level>: Set the verbosity level (0: no output, 1: errors and warnings, 2: informational) (default: 0)"
  echo "  --help: Display this help message"
  echo ""
  echo " Creates files: "
  echo "   <root_directory>/<search_directory>/<search_terms_filename>"
  echo "   <root_directory>/<search_directory>/<search_terms_filename>.unsorted (temporary file)"
  echo ""
  echo " example: "
  echo "   $0"' --root-dir "v4/data" --ref-dir "reference" --dbx-dir "dbxrefs" --dbx "AllianceGenome.txt Ensembl.txt HGNC.txt IMGT_GENE-DB.txt" --search-dir "search_terms" --search-file "search_terms.txt" --gene-symbols "gene_symbols.txt" --gene-synonyms "gene_synonyms.txt" --verbose 0'
  exit 1
}

# Set variable values from switches
while [ "$#" -gt 0 ]; do
  case "$1" in
    --root-dir)
      root_dir=$2
      shift 2
      ;;
    --ref-dir)
      reference_dir=$2
      shift 2
      ;;
    --dbx-dir)
      dbxrefs_dir=$2
      shift 2
      ;;
    --dbx)
      dbxrefs=$2
      shift 2
      ;;
    --search-dir)
      search_dir=$2
      shift 2
      ;;
    --search-file)
      search_terms_filename=$2
      shift 2
      ;;
    --gene-symbols)
      gene_symbols_filename=$2
      shift 2
      ;;
    --gene-synonyms)
      gene_synonyms_filename=$2
      shift 2
      ;;
    --verbose)
      verbose=$2
      shift 2
      ;;
    --help)
      usage
      ;;
    *)
      echo "Invalid option: $1" >&2
      exit 1
      ;;
  esac
done

# Set paths
reference_path="${root_dir}/${reference_dir}"
dbxrefs_path="${reference_path}/${dbxrefs_dir}"
search_path="${root_dir}/${search_dir}"
search_terms_filepath="${search_path}/${search_terms_filename}"
gene_symbols_filepath="${reference_path}/${gene_symbols_filename}"
gene_synonyms_filepath="${reference_path}/${gene_synonyms_filename}"

# Combine search terms into a single file
for ref in $dbxrefs; do
  cat "${dbxrefs_path}/${ref}" >> "${search_terms_filepath}.unsorted"
done

cat "${gene_symbols_filepath}" >> "${search_terms_filepath}.unsorted"
cat "${gene_synonyms_filepath}" >> "${search_terms_filepath}.unsorted"
cat "${search_terms_filepath}.unsorted" | sort -u | grep -v not > "${search_terms_filepath}"

# Display number of lines in the search terms file if verbose level is 2
if [ "$verbose" -eq 2 ]; then
  echo "Created ${search_terms_filepath}."
  echo "Created ${search_terms_filepath}.unsorted - can be removed."
  line_count=$(wc -l < "${search_terms_filepath}")
  echo "Number of lines in ${search_terms_filepath}: $line_count"
fi
