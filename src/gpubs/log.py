# replace these everywhere
def msginfo(verbose, msg):
    msg2(verbose,msg)
    
def msg2(verbose, msg):
    if verbose >= 2:
        print(msg)

def msg1(verbose, msg):
    if verbose >= 1:
        print(msg)
