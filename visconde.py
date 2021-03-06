import argparse
import re
banner = "This is VISCONDE version 0.1.7."
parser = argparse.ArgumentParser()
file = ""

fenced_with_language = False
many_outpus = False
tangle = True
weave = False
index = True
dry_run = False
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

# dry-run ==============================================================
parser.add_argument(  "--dry-run", action="store_true", 
    help="write no files, but output warnings", dest='dry_run')

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

# weave ================================================================
parser.add_argument(  "--weave", action="store_true", 
    help="produce weaved output")
parser.add_argument("--noweave", action="store_true", 
    help="do not produce weaved output (default)")

# index ================================================================
parser.add_argument(               "--index", action="store_true",
    help="produce word index (default)")
parser.add_argument(             "--noindex", action="store_true",
    help="do not produce word index")


# ======================================================================
args = parser.parse_args()
# input file ===========================================================
file = args.file

# flag dry-run =========================================================
dry_run = args.dry_run

# flag (no)fencedwithlanguage ==========================================
if args.fencedwithlanguage and args.nofencedwithlanguage:
    raise SystemExit('! error: contradictory flags (fencedwithlanguage and nofencedwithlanguage)')

fenced_with_language = args.fencedwithlanguage


# flag (no)manyoutputs =================================================
if args.manyoutputs and args.nomanyoutputs:
    raise SystemExit('! error: contradictory flags (manyoutputs and nomanyoutputs)')

many_outpus = args.manyoutputs


# flag (no)tangle ======================================================
if args.tangle and args.notangle:
    raise SystemExit('! error: contradictory flags (tangle and notangle)')

tangle = not args.notangle

# flag (no)weave =======================================================
if args.weave and args.noweave:
    raise SystemExit('! error: contradictory flags (weave and noweave)')

weave = args.weave

# flag (no)index =======================================================
if args.index and args.noindex:
    raise SystemExit('! error: contradictory flags (index and noindex)')

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
    raise SystemExit('! error: too many root chunks\n  -----  chunk list:' + ','.join(root_chunks))
else:
    for blk in root_chunks:
        if not dry_run:
            print("Writing file %s...    " % blk,end='')
        
            with open(blk, 'w') as output:
                buffer = [l for b in chunk[blk].blocks for l in b.lines]
                i = 0
                while i < len(buffer):
                    if is_chunk_line(buffer[i]):
                        chunk_name = chunk_line_name(buffer[i])
                        if chunk_name not in chunk:
                            print("! warning: undefined chunk; reference will be kept verbatim: %s" % chunk_name)
                    
                            if not dry_run:
                                print(buffer[i], file=output, end='') # insert reference verbatim
                            i += 1
                        else:
                            indent = re.compile(' *').match(buffer[i]).end()
                            ind_lns = [x for b in chunk[chunk_name].blocks for x in add_indent(indent, b.lines)]
                            buffer = ind_lns + buffer[i+1:]
                            i = 0
                    else:
                        if not dry_run:
                            print(buffer[i], file=output, end='')
                        i += 1
        
            print("[ DONE ]")
if weave:
    with open(file, 'r') as input_file:
        out_filename = file + '.md'
        if not dry_run:
            print("Writing file %s... " % out_filename,end='')
        with open(out_filename, 'w') as output_file:
            html_header = ''
            
            if not dry_run:
                print(html_header, file=output_file, end='\n')
            reading_code_chunk = False
            last_line_blank = False
            chunk_name = '' # current chunk name (when reading_code_chunk == True)
            code_block_counter = 0
            
            for line_number, line in enumerate(input_file):
                if not reading_code_chunk:
                    if line.strip() == "":
                        if not dry_run:
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
                            
                                open_div_span = '<' +'div class="codeblock"><'+ 'span class="codeblock_name">'
                                block_id_anchor = '<'+('a id="%d">%d<' % (chunk_id,chunk_id)) +'/a>'
                                weaved_chunk_name = ' {<'+'strong>' + chunk_name + '<'+'/strong>}'
                                
                                equals = ' =' if chunk_id == chunk[chunk_name].blocks[0].id else ' +='
                                
                                open_pre = '<' + '/span>\n\n<'+'pre class="prettyprint language-' + chunk_language +'">'
                                
                                code_chunk_header = open_div_span + block_id_anchor + weaved_chunk_name + equals + open_pre
                            
                            else:
                                chunk_name = line[fence_length:].strip()
                                code_chunk_header = '<' +'div class="codeblock"><'+'span class="codeblock_name">{<'+'strong>' + chunk_name + '<'+'/strong>}<'+'/span>\n\n<'+'pre class="prettyprint">'
                            if not dry_run:
                                print(code_chunk_header, file=output_file)
                            reading_code_chunk = True
                
                        else:
                            if not dry_run:
                                print(line,file=output_file, end='')
                            last_line_blank = False
                    else:
                        if not dry_run:
                            print(line, file=output_file, end='')
                
                    continue
                match_fence = fence_regexp.match(line)
                if match_fence and match_fence.end() == fence_length:
                    other_blocks = ', '.join([('<'+ 'a href="#%d">%d<' + '/a>') % (b.id,b.id) if b.id != chunk_id else '%d' % b.id for b in chunk[chunk_name].blocks])
                    if len(chunk[chunk_name].blocks) > 1:
                        other_blocks  = '<' + 'span class="seealso">See also ' + other_blocks + '.<' + '/span>'
                    else:
                        other_blocks = ''
                    seealso = ''
                    if len(used_at[chunk_name]) > 0:
                        seealso = '<' + 'span class="usedin">Used in ' + ', '.join([(('<' + 'a href="#%d">%d<' +'/a>') % (id,id)) for c,id,i in used_at[chunk_name]]) + '.<' + '/span>'
                
                    if not dry_run:
                        print('<'+'/p'+'re>' + other_blocks + seealso +'<'+'/div>', file=output_file)
                
                
                    reading_code_chunk = False
                    last_line_blank = False
                else:
                    if is_chunk_line(line):
                        n = chunk_line_name(line)
                        r = chunk[n].blocks[0].id # reference to first occurence of block
                        j = 0
                        while line[j] != '@':
                            j +=1
                        line = ' '*j + '<' + 'code class="chunk_ref">@{' + n + ' <' + (('a href="#%d">%d<' + '/a>') % (r,r)) +  '}<' + '/code>\n'
                    
                    if not dry_run:
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
                if not dry_run:
                    print("## Word index\n\n", file=output_file)
                    print('<' + 'ul>', file=output_file)
                
                for w in sorted(word_dict.keys()):
                    if w[0] != first_letter:
                        if first_letter != ' ':
                            if not dry_run:
                                print('<' + '/li><' +'/ul>', file=output_file)
                        if not dry_run:
                            print(('<' +'li class="dict_letter">%c<' + 'ul>') % w[0].upper(), file=output_file)
                        first_letter = w[0]
                
                    links = ', '.join([('<'+ 'a href="#%d">%d<' + '/a>') % (block[j].id,block[j].id) for j in list(sorted(set(word_dict[w])))])
                    if not dry_run:
                        print(('<' +'li>%s: ' + links + '<' + '/li>') % w, file=output_file)
                
                if not dry_run:
                    print('<' + '/ul><' + '/ul>', file=output_file)
            html_tail = ''
            if not dry_run:
                print(html_tail, file=output_file, end='')
        if not dry_run:
            print("[ DONE ]")
