import argparse
import re
banner = "This is VISCONDE version 0.1.6."
parser = argparse.ArgumentParser()
file = ""

fenced_with_language = False
many_outpus = False
tangle = True
index = True
class Chunk:
    '''Collection of blocks with same name'''
    
    def __init__(self):
        self.blocks = []
class Block:
    '''Lines of a block of code.'''
    block_counter = 0
    
    def __init__(self,line_number,block_lines):
        self.start = line_number
        self.lines = block_lines
        Block.block_counter +=1
        self.id = Block.block_counter
fence_regexp = re.compile('```+')
chunk = {} # all chunks
block = [] # all code blocks
def chunks_of(code):
    return [line.strip()[2:-1].strip() for line in code if is_chunk_line(line)]
def is_chunk_line(l):
    aux = l.strip()
    return aux and (aux[0:2] == '@{' and aux[-1] == '}')

def chunk_line_name(line):
    return line.strip()[2:-1].strip()

def add_indent(indent_amount, code):
    return [' '*indent_amount + line for line in code]
word_reg = '[A-Za-z][A-Za-z0-9_]+'

# file =================================================================
parser.add_argument("file", help="literate source file")

# fencedwithlanguage ===================================================
parser.add_argument(  "--fencedwithlanguage", action="store_true", 
    help="first word on opening fence is language; the rest is chunk name")
parser.add_argument("--nofencedwithlanguage", action="store_true", 
    help="text on opening fence is chunk name (default)")

# manyoutputs ==========================================================
parser.add_argument(         "--manyoutputs", action="store_true", 
    help="generate one output file per root chunk")
parser.add_argument(       "--nomanyoutputs", action="store_true", 
    help="generate one output file per root chunk (default)")

# tangle ===============================================================
parser.add_argument(              "--tangle", action="store_true", 
    help="produce tangled outputs (default)")
parser.add_argument(            "--notangle", action="store_true", 
    help="do not produce tangled outputs")

# index ================================================================
parser.add_argument(               "--index", action="store_true",
    help="produce word index (default)")
parser.add_argument(             "--noindex", action="store_true",
    help="do not produce word index")


# ======================================================================
args = parser.parse_args()
# input file ===========================================================
file = args.file


# flag (no)fencedwithlanguage ==========================================
if args.fencedwithlanguage and args.nofencedwithlanguage:
    print('! error: contradictory flags (fencedwithlanguage and nofencedwithlanguage)')
    #todo abort

fenced_with_language = args.fencedwithlanguage


# flag (no)manyoutputs =================================================
if args.manyoutputs and args.nomanyoutputs:
    print('! error: contradictory flags (manyoutputs and nomanyoutputs)')
    #todo abort

many_outpus = args.manyoutputs


# flag (no)tangle ======================================================
if args.tangle and args.notangle:
    print('! error: contradictory flags (tangle and notangle)')
    #todo abort

tangle = not args.notangle


# flag (no)index =======================================================
if args.index and args.noindex:
    print('! error: contradictory flags (index and noindex)')
    #todo abort

index = not args.noindex

print(banner) # Hi!

with open(file, 'r') as input_file:
    reading_code_chunk = False
    last_line_blank = False
    chunk_name = ''
    block_lines = [] # list of lines

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
                        while line[j] == ' ': # skip spaces before language specification
                            j += 1
                        while line[j] != ' ': # skip language specification
                            j += 1
                    chunk_name = line[j+1:].strip()
                    chunk_line = line_number
                    block_lines = []
                    reading_code_chunk = True
                else:
                    last_line_blank = False
        
            continue
    
        match_fence = fence_regexp.match(line)
        if match_fence and match_fence.end() == fence_length:
            if chunk_name not in chunk:
                chunk[chunk_name] = Chunk()
            new_block = Block(chunk_line+1, block_lines)
            chunk[chunk_name].blocks += [new_block]
            block += [new_block]
            reading_code_chunk = False
            last_line_blank = False
        else:
            block_lines += [line]
used_at = dict()

for blk in chunk:
    if blk not in used_at:
        used_at[blk] = []
    for i,b in enumerate(chunk[blk].blocks):
        for chk in chunks_of(b.lines):
            if chk not in used_at:
                used_at[chk]  = [(blk, b.id, i)]
            else:
                used_at[chk] += [(blk, b.id, i)]

#print(used_at)
root_chunks = [blk for blk, parents in used_at.items() if len(parents) == 0]
if len(root_chunks) == 1:
    print("root chunk: '" + root_chunks[0] + "'")
elif len(root_chunks) > 1:
    print('root chunks: ' + ', '.join(["'" + c + "'" for c in root_chunks]))
else:
    print('! warning: I cannot find any  root chunk')
    #todo: it's alright if no tangle option was chosen

if tangle and (not many_outpus) and (len(root_chunks) > 1):
    print('! error: too many root chunks')
    print('  -----  chunk list:')
    print(root_chunks)
    #todo: abort
else:
    for blk in root_chunks:
        print("Writing file %s...    " % blk,end='')
        with open(blk, 'w') as output:
            buffer = [l for b in chunk[blk].blocks for l in b.lines]
            i = 0
            while i < len(buffer):
                if is_chunk_line(buffer[i]):
                    chunk_name = chunk_line_name(buffer[i])
                    if chunk_name not in chunk:
                        print("! warning: undefined chunk; reference will be kept verbatim: %s" % chunk_name)
                
                        print(buffer[i], file=output, end='') # insert reference verbatim
                        i += 1
                    else:
                        indent = re.compile(' *').match(buffer[i]).end()
                        ind_lns = [x for b in chunk[chunk_name].blocks for x in add_indent(indent, b.lines)]
                        buffer = ind_lns + buffer[i+1:]
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
        code_block_counter = 0
        
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
                        code_block_counter += 1
                        if fenced_with_language:
                            j = fence_length
                            while line[j] == ' ':
                                j += 1
                            chunk_lang_begin = j
                            while line[j] != ' ':
                                j += 1
                            chunk_name = line[j+1:].strip()
                            chunk_id = code_block_counter
                            chunk_language = line[chunk_lang_begin:j]
                        
                            other_blocks = ', '.join([('<'+ 'a href="#%d">%d<' + '/a>') % (b.id,b.id) for b in chunk[chunk_name].blocks if b.id != chunk_id])
                            if other_blocks != '':
                                other_blocks = ' ' + other_blocks
                            code_chunk_header = '<' +'div class="codeblock"><'+ 'span class="codeblock_name"><'+('a id="%d">%d<' % (chunk_id,chunk_id))+'/a> {<'+'strong>' + chunk_name + '<'+'/strong>' + other_blocks + '}<'+'/span>\n\n<'+'pre class="prettyprint language-' + chunk_language +'">'
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
                seealso = ''
                if len(used_at[chunk_name]) > 0:
                    seealso = '<' + 'span class="usedin">Used in ' + ', '.join([(('<' + 'a href="#%d">%d<' +'/a>') % (id,id)) for c,id,i in used_at[chunk_name]]) + '.<' + '/span>'
            
                
                print('<'+'/p'+'re>' + seealso +'<'+'/div>', file=output_file)
            
            
                reading_code_chunk = False
                last_line_blank = False
            else:
                if is_chunk_line(line):
                    j = 0
                    while line[j] != '@':
                        j +=1
                    line = ' '*j + '<' + 'code class="chunk_ref">@{' + chunk_line_name(line) + '}<' + '/code>\n'
                
                print(line, file=output_file, end='')
        
        if index:
            word_dict = {}
        
            for i,b in enumerate(block):
                words = []
                for l in b.lines:
                    if not is_chunk_line(l):
                        words += re.findall(word_reg,l)
            
                for w in words:
                    if w not in word_dict:
                        word_dict[w]  = [i]
                    else:
                        word_dict[w] += [i]
            first_letter = ' '
            print("## Word index\n\n", file=output_file)
            print('<' + 'ul>', file=output_file)
            
            for w in sorted(word_dict.keys()):
                if w[0] != first_letter:
                    if first_letter != ' ':
                        print('<' + '/li><' +'/ul>', file=output_file)
                    print(('<' +'li class="dict_letter">%c<' + 'ul>') % w[0].upper(), file=output_file)
                    first_letter = w[0]
            
                links = ', '.join([('<'+ 'a href="#%d">%d<' + '/a>') % (block[j].id,block[j].id) for j in list(sorted(set(word_dict[w])))])
                print(('<' +'li>%s: ' + links + '<' + '/li>') % w, file=output_file)
            
            print('<' + '/ul><' + '/ul>', file=output_file)
        html_tail = ''
        print(html_tail, file=output_file, end='')
    print("[ DONE ]")
