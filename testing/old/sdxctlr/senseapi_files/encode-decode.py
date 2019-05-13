# From https://bitbucket.org/berkeleylab/sensenrm-oscars/src/d09db31aecbe7654f03f15eed671c0675c5317b5/sensenrm_server.py?at=master&fileviewer=file-view-default

import base64
import gzip
import zlib
import sys

#### gzip and base64
def data_gzip_b64encode(tcontent):
    gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
    gzipped_data = gzip_compress.compress(tcontent) + gzip_compress.flush()
    b64_gzip_data = base64.b64encode(gzipped_data).decode()
    return b64_gzip_data

def data_b64decode_gunzip(tcontent):
    unzipped_data = zlib.decompress(base64.b64decode(tcontent), 16+zlib.MAX_WBITS)
    return unzipped_data


usage = "python encode-decode.py <encode|decode> <input-filename.txt> <output-filename>"

if len(sys.argv) != 4:
    print usage
    exit

inputfilename = sys.argv[2]
outputfilename = sys.argv[3]
output = None

if sys.argv[1].lower() == 'encode':
    with open(inputfilename) as inputfile:
        output = data_gzip_b64encode(inputfile.read())
        
elif sys.argv[1].lower() == 'decode':
    with open(inputfilename) as inputfile:
        output = data_b64decode_gunzip(inputfile.read())

else:
    print usage
    exit

with open(outputfilename, 'w') as outputfile:
    outputfile.write(output)
    outputfile.close()
