#!/usr/bin/gawk -f

BEGIN {
    FS = "\t"  # Set the field separator to tab
    OFS = "\t" # Set the output field separator to tab
}

# Read the search terms from the search_terms file
NR == FNR {
    term = $1
    if (tolower(term) == term) {
        search_terms[tolower(term)] = 1
    } else {
        exact_terms[term] = 1
    }
    next
}

# Function to process title or abstract
function process_text(text, matches, terms) {
    # Remove non-alphanumeric characters on word boundary
    gsub(/[,.():]+[[:space:]]*/, " ", text)

    # Split text into words
    n = split(text, words, " ")

    # Loop through each word
    for (i = 1; i <= n; i++) {
        word = words[i]
        lc_word = tolower(word)

        # Check for matches
        if ((lc_word in search_terms) || (word in exact_terms && word ~ /^[[:alnum:]]+$/)) {
            terms[word] = 1
        }
    }

    return matches
}

# Process the title and abstract data
{
    #PMID,Title,Abstract,Journal,PublicationDate,JournalTitle,ArticleType,MeshHeadingList,PublicationTypeList
    title = $2
    abstract = $3

    # Clear the term arrays for the current record
    delete title_terms
    delete abstract_terms

    # Process title
    process_text(title, "", title_terms)

    # Process abstract
    process_text(abstract, "", abstract_terms)



    # Combine matches_title and matches_abstract into all_matches
    all_matches = ""
    for (term in title_terms) {
            all_matches = (all_matches == "") ? term : all_matches "," term
    }
    for (term in abstract_terms) {
        if (!(term in title_terms)) {
	    all_matches = (all_matches == "") ? term : all_matches "," term
        }
    }


    # Print the result
    printf "%s\t%s\t%s", $1, $2, $3
    for (i = 4; i <= NF; i++) {
        printf "\t%s", $i
    }
    if (all_matches != "") {
        printf "\t%s", all_matches
    }
    printf "\n"
}
