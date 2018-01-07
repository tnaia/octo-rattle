import sys
import re

banner = "This is COB version 0.1."
file = ""
dashes_regexp = re.compile('```+')
block = {}
def chunk_in_references(block_text):
    references = []
    for line in block_text:
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
    reading_code_block = False
    last_line_blank = False
    block_name = ''
    block_text = [] # list of lines
    for line_number, line in enumerate(input_file):
        if not reading_code_block:
            if line.strip() == "":
                last_line_blank = True
                continue
            elif last_line_blank:
                match_dashes = dashes_regexp.match(line) # at least 3 dashes
                if match_dashes:
                    num_dashes = match_dashes.end()
                    block_name = line[num_dashes:].strip()
                    block_line = line_number
                    block_text = []
                    reading_code_block = True
                else:
                    last_line_blank = False
        
            continue
    
        # Now reading code block
        match_dashes = dashes_regexp.match(line) # at least 3 dashes
        if match_dashes and match_dashes.end() == num_dashes:
            if block_name not in block:
                block[block_name] = []
            block[block_name] += [(block_line+1, block_text)]
            reading_code_block = False
            last_line_blank = False
        else:
            block_text += [line]
used_at = dict()

for blk in block:
    if blk not in used_at:
        used_at[blk] = []
    for l,b in block[blk]:
        for chk in chunk_in_references(b):
            if chk not in used_at:
                used_at[chk] = [blk]
            else:
                used_at[chk] += [blk]

# expansion_order = [blk for blk, parents in sorted(used_at.items(), key=lambda t: len(t[1]),reverse=True)]
root_blocks = [blk for blk, parents in used_at.items() if len(parents) == 0]


for blk in root_blocks:
    print("Writing file %s... " % blk,end='')
    with open(blk, 'w') as output:
        buffer = [l for c in block[blk] for l in c[1]]
        i = 0
        while i < len(buffer):
            if is_chunk_line(buffer[i]):
                the_chunk_name = chunk_line_name(buffer[i])
                if the_chunk_name not in block:       # do we know what to insert in place of line?
                    print("! warning: missing text for chunk: %s" % the_chunk_name)
                    print(buffer[i], file=output, end='')
                    i += 1
                else:
                    indentation = re.compile(' *').match(buffer[i]).end()
                    indented_lines = [x for l,c in  block[the_chunk_name] for x in indent_code(indentation, c)]
                    buffer = indented_lines + buffer[i+1:]
                    i = 0
            else:
                print(buffer[i], file=output, end='')
                i += 1
        
    print("[ DONE ]")
