import argparse
import re

banner = "This is VISCONDE version 0.1.4."
parser = argparse.ArgumentParser()
file = ""

fenced_with_language = False
many_outpus = False
fence_regexp = re.compile('```+')
chunk = {}
def chunks_of(code):
    return [line.strip()[2:-1].strip() for line in code if is_chunk_line(line)]
def is_chunk_line(l):
    aux = l.strip()
    return aux and (aux[0:2] == '@{' and aux[-1] == '}')

def chunk_line_name(line):
    return line.strip()[2:-1].strip()

def indent_code(indentation, code):
    return [' '*indentation + line for line in code]

parser.add_argument("file", help="literate source file")

# fencedwithlanguage ===================================================
parser.add_argument("--fencedwithlanguage", help="first word on opening fence is language; the rest is chunk name",
                    action="store_true")
parser.add_argument("--nofencedwithlanguage", help="text on opening fence is chunk name (default)",
                    action="store_true")
# manyoutputs ==========================================================
parser.add_argument("--manyoutputs", help="generate one output file per root chunk",
                    action="store_true")
parser.add_argument("--nomanyoutputs", help="generate one output file per root chunk (default)",
                    action="store_true")
# tangle ===============================================================
parser.add_argument("--tangle", help="produce tangled outputs (default)",
                    action="store_true")
parser.add_argument("--notangle", help="do not produce tangled outputs",
                    action="store_true")


args = parser.parse_args()

# input file
file = args.file

# flag (no)fencedwithlanguage
if args.fencedwithlanguage and args.nofencedwithlanguage:
    print('! error: contradictory flags (fencedwithlanguage and nofencedwithlanguage)')
    #todo abort

fenced_with_language = args.fencedwithlanguage

# flag (no)manyoutputs
if args.manyoutputs and args.nomanyoutputs:
    print('! error: contradictory flags (manyoutputs and nomanyoutputs)')
    #todo abort

many_outpus = args.manyoutputs

# flag (no)tangle
if args.tangle and args.notangle:
    print('! error: contradictory flags (tangle and notangle)')
    #todo abort

tangle = not args.notangle

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
                match_fence = fence_regexp.match(line)
                if match_fence:
                    fence_length = match_fence.end()
                    j = fence_length
                    if fenced_with_language:
                        while line[j] == ' ':
                            j += 1
                        while line[j] != ' ':
                            j += 1
                    chunk_name = line[j+1:].strip()
                    chunk_line = line_number
                    chunk_text = []
                    reading_code_chunk = True
                else:
                    last_line_blank = False
        
            continue
    
        match_fence = fence_regexp.match(line)
        if match_fence and match_fence.end() == fence_length:
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
        for chk in chunks_of(b):
            if chk not in used_at:
                used_at[chk] = [blk]
            else:
                used_at[chk] += [blk]


root_chunks = [blk for blk, parents in used_at.items() if len(parents) == 0]

if tangle and (not many_outpus) and (len(root_chunks) > 1):
    print('! error: too many root chunks')
    #todo: abort
else:
    for blk in root_chunks:
        print("Writing file %s... " % blk,end='')
        with open(blk, 'w') as output:
            buffer = [l for c in chunk[blk] for l in c[1]]
            i = 0
            while i < len(buffer):
                if is_chunk_line(buffer[i]):
                    the_chunk_name = chunk_line_name(buffer[i])
                    if the_chunk_name not in chunk:
                        print("! warning: undefined chunk; reference will be kept verbatim: %s" % the_chunk_name)
                
                        print(buffer[i], file=output, end='') # insert reference verbatim
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
with open(file, 'r') as input_file:
    out_filename = file + '.md'
    print("Writing file %s... " % out_filename,end='')
    with open(out_filename, 'w') as output_file:
        html_header = ''
        
        print(html_header, file=output_file, end='\n')
        reading_code_chunk = False
        last_line_blank = False
        chunk_name = ''
        
        for line_number, line in enumerate(input_file):
            if not reading_code_chunk:
                if line.strip() == "":
                    print(line,file=output_file, end='')
                    last_line_blank = True
                    continue
                elif last_line_blank:
                    match_fence = fence_regexp.match(line)
                    if match_fence:
                        fence_length = match_fence.end()
                        if fenced_with_language:
                            j = fence_length
                            while line[j] == ' ':
                                j += 1
                            chunk_lang_begin = j
                            while line[j] != ' ':
                                j += 1
                            chunk_language = line[chunk_lang_begin:j]
                            chunk_name = line[j+1:].strip()
                            code_chunk_header = '<' +'div class="codeblock"><'+'span class="codeblock_name">{<'+'strong>' + chunk_name + '<'+'/strong>}<'+'/span>\n\n<'+'pre class="prettyprint language-' + chunk_language +'">'
                        else:
                            chunk_name = line[fence_length:].strip()
                            code_chunk_header = '<' +'div class="codeblock"><'+'span class="codeblock_name">{<'+'strong>' + chunk_name + '<'+'/strong>}<'+'/span>\n\n<'+'pre class="prettyprint">'
                        print(code_chunk_header, file=output_file)
                        reading_code_chunk = True
                    else:
                        print(line,file=output_file, end='')
                        last_line_blank = False
                else:
                    print(line, file=output_file, end='')
            
                continue
            match_fence = fence_regexp.match(line)
            if match_fence and match_fence.end() == fence_length:
                print('<'+'/p'+'re><'+'/div>', file=output_file)
                reading_code_chunk = False
                last_line_blank = False
            else:
                print(line, file=output_file, end='')
        
        html_tail = ''
        print(html_tail, file=output_file, end='')
    print("[ DONE ]")

