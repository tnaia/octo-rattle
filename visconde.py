import sys
import re

banner = "This is COB version 0.1.1."
file = ""
dashes_regexp = re.compile('```+')
chunk = {}
def chunk_in_references(chunk_text):
    references = []
    for line in chunk_text:
        line = line.strip() 
        # here we would remove comments in the line as well
        if is_chunk_line(line):
            references += [line[2:-1].strip()]

    return references
def is_chunk_line(l):
    aux = l.strip()
    return aux and (aux[0:2] == '@{' and aux[-1] == '}')

def chunk_line_name(line):
    return line.strip()[2:-1].strip()

def indent_code(indentation, code):
    return [' '*indentation + line for line in code]

file = sys.argv[-1]
print(banner) # Hi!

with open(file, 'r') as input_file:
    reading_code_chunk = False
    last_line_blank = False
    chunk_name = ''
    chunk_text = [] # list of lines
    for line_number, line in enumerate(input_file):
        if not reading_code_chunk:
            if line.strip() == "":
                last_line_blank = True
                continue
            elif last_line_blank:
                match_dashes = dashes_regexp.match(line) # at least 3 dashes
                if match_dashes:
                    num_dashes = match_dashes.end()
                    chunk_name = line[num_dashes:].strip()
                    chunk_line = line_number
                    chunk_text = []
                    reading_code_chunk = True
                else:
                    last_line_blank = False
        
            continue
    
        # Now reading code chunk
        match_dashes = dashes_regexp.match(line) # at least 3 dashes
        if match_dashes and match_dashes.end() == num_dashes:
            if chunk_name not in chunk:
                chunk[chunk_name] = []
            chunk[chunk_name] += [(chunk_line+1, chunk_text)]
            reading_code_chunk = False
            last_line_blank = False
        else:
            chunk_text += [line]
used_at = dict()

for blk in chunk:
    if blk not in used_at:
        used_at[blk] = []
    for l,b in chunk[blk]:
        for chk in chunk_in_references(b):
            if chk not in used_at:
                used_at[chk] = [blk]
            else:
                used_at[chk] += [blk]

# expansion_order = [blk for blk, parents in sorted(used_at.items(), key=lambda t: len(t[1]),reverse=True)]
root_chunks = [blk for blk, parents in used_at.items() if len(parents) == 0]


for blk in root_chunks:
    print("Writing file %s... " % blk,end='')
    with open(blk, 'w') as output:
        buffer = [l for c in chunk[blk] for l in c[1]]
        i = 0
        while i < len(buffer):
            if is_chunk_line(buffer[i]):
                the_chunk_name = chunk_line_name(buffer[i])
                if the_chunk_name not in chunk:       # do we know what to insert in place of line?
                    print("! warning: missing text for chunk: %s" % the_chunk_name)
                    print(buffer[i], file=output, end='')
                    i += 1
                else:
                    indentation = re.compile(' *').match(buffer[i]).end()
                    indented_lines = [x for l,c in  chunk[the_chunk_name] for x in indent_code(indentation, c)]
                    buffer = indented_lines + buffer[i+1:]
                    i = 0
            else:
                print(buffer[i], file=output, end='')
                i += 1
        
    print("[ DONE ]")
