import os
from typing import List, Dict, Set
from pydantic import BaseModel, root_validator

from gpubs.log import msg1,msg2

class ReferenceData(BaseModel):
    """
    Files for retrieving and transforming reference gene information
    """
    
    def __init__(self, *args, **kwargs):
        super(ReferenceData, self).__init__(*args, **kwargs)

        self.version_root = os.path.join(os.getcwd(), str(self.version), self.data_root)
        msg2(self.verbose, f"version_root={self.version_root}")
        
        # make directory structure
        os.makedirs(self.version_root, exist_ok=True)
        os.makedirs(self.raw_path(), exist_ok=True)
        os.makedirs(self.reference_path(), exist_ok=True)
        os.makedirs(self.dbxref_path(), exist_ok=True)
        os.makedirs(self.search_path(), exist_ok=True)
        os.makedirs(self.pub_inpath(), exist_ok=True)
        os.makedirs(self.pub_outpath(), exist_ok=True)
        os.makedirs(self.genes_outpath(), exist_ok=True)
        
        msg2(self.verbose, "Created directory structure.")

    ncbi_gene_info_url: str = "https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz"
    
    data_root: str  = "data/"
    """ full path to where all the raw, reference, and generated data are stored """
    
    raw_data_path: str = "raw/"
    
    reference_data_path: str = "reference/"
    
    dbxref_reference_data_path: str = "dbxrefs/"
    
    dbxrefs: List = [] 
    """ if empty, it will just get filled with a list of all the files created in the m.dbxref_path() """
        
    gene_info_filename: str = "gene_info.gz"
    
    gene_symbols_filename: str = "gene_symbols.txt"
    
    gene_synonyms_filename: str = "gene_synonyms.txt"
    
    search_terms_path: str = "search_terms/"
    
    frequency_list_filename: str = "frequency_list.txt"
    
    corpus_stop_word_list_length:int = 4000
    
    # old lsit
    #custom_stop_words:List = ['ago', 'aim', 'amid', 'april', 'arch', 'bed', 'bite', 'bug', 'co', 'crop', 'damage', 'et', 
    #                'fast', 'fat', 'fate', 'gap', 'genesis', 'ii', 'iv', 'lamp', 'laser', 'mater', 'melt', 'mice', 'minor', 'mv', 'net', 
    #                'not', 'race', 'rank', 'se', 'sink', 'soft', 'spatial', 'steel', 'stop', 'tau', 'traits', 'via']
    
    # may overlap somewhat with stop words
    custom_stop_words:List = ['ago', 'aim', 'amid', 'april', 'arch', 'bed', 'bite', 'bug', 'cage', 'co', 'crop',
                    'damage', 'danger', 'digit', 'et', 'fast', 'fat', 'fate', 'fire', 'flower', 'gap', 'genesis', 'gov', 'gpa', 'grasp',
                    'ii', 'inos', 'iv', 'killer', 'lab', 'lamp', 'laser', 'map', 'mask', 'mater', 'melt', 'mice', 'minor', 'miss', 'mv',
                    'nail', 'net', 'not', 'osf', 'pan', 'par', 'pha', 'rab', 'race', 'rain', 'rank',
                    'san', 'sand', 'se', 'sink', 'soft', 'spatial', 'spin', 'spp', 'steel', 'stop',
                    'storm', 'tactile', 'tau', 'theta', 'tip', 'traits', 'via']

    search_terms_filename: str = "search_terms.txt"
    
    filtered_terms_filename: str = "filtered_terms.txt"
    
    abstract_inpath: str = "pubs/"
    
    refresh_abstract_xml_files: bool = False
    """ Set to True to overwrite downloaded NCBI XML abstract files and checksum files """
    
    num_abstract_xml_files: int
    """ Number of NCBI XML files to download; Set this to -1 to get all abstracts """
    
    abstract_outpath: str = "csvpubs/"

    abstract_length_threshold: int = 405

    abstract_genes_outpath: str = "genes/"

    
    #path functions
    def raw_path(self):
        return os.path.join(os.getcwd(), self.version_root, self.raw_data_path)
    def reference_path(self):
        return os.path.join(os.getcwd(), self.version_root, self.reference_data_path)
    def dbxref_path(self):
        return os.path.join(os.getcwd(), self.version_root, self.reference_data_path, self.dbxref_reference_data_path)
    def search_path(self):
        return os.path.join(os.getcwd(), self.version_root, self.search_terms_path)
    def pub_inpath(self):
        return os.path.join(os.getcwd(), self.version_root, self.raw_data_path, self.abstract_inpath)
    def pub_outpath(self):
        return os.path.join(os.getcwd(), self.version_root, self.abstract_outpath)
    def genes_outpath(self):
        return os.path.join(self.pub_outpath(), self.abstract_genes_outpath)

    verbose: int = 0
    """ 0 prints nothing, 1 prints errors and warnings, 2 prints info """
    
    debug: bool = False
    """ Prints very detailed debuggin messages """
    
    version: str = None
    """ If None, version will e set to timestamp """
    
    rand_seed: int = 42
    """ if None, reproducible within the same release"""
    
    version_root: str = None
    """ leave this alone it will be computed as data_root/version """
    
    
    @root_validator(pre=False, skip_on_failure=True)
    def valid_paths_for_data_tree(cls, v: Dict) -> Dict:
        data_root = v.get("data_root")
        version = v.get("version")
        
        import os
        
        if version is None:
            import subprocess
            
            # use miliseconds and create new directory structure
            version = str(subprocess.check_output(["date", "+%1N.%S_%M_%H_%Y_%m_%d"]).strip().decode())
            v["version"] = version
        
        if data_root is None:
            raise Exception("Error: data_root cannot be None.")
            
        version_root = os.path.join(os.getcwd(), data_root, str(version))
        v["version_root"] = version_root
        
        if os.path.exists(version_root):
            msg2(f"Using existing data director {version_root}")
            
        return v
    
