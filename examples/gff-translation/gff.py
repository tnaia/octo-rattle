import sys
if len(sys.argv) != 4:
    print('! error: wrong number of arguments.')
    print('  usage: script AGP_FILE GFF_FILE OUTPUT_FILE')
    raise SystemExit('Wrong number of arguments.')

agp_filename = sys.argv[-3]
gff_filename = sys.argv[-2]
out_filename = sys.argv[-1]

with open(gff_filename, 'r') as gff_file:
    with open(out_filename, 'w') as out_file:

        with open(agp_filename, 'r') as agp_file:
            agp_dict = {}
            
            for line in agp_file:
                if line[0] == '#':
                    continue
                
                split_line = line.rstrip().split('\t')
                
                if split_line[7] == 'yes':
                    continue
            
                chrom_name = split_line[0]
                chrom_beg  = int(split_line[1]) # begin and end positions,
                chrom_end  = int(split_line[2]) # relative to the chromosome
                scaff_name = split_line[5]
                scaff_beg  = int(split_line[6]) # begin and end positions,
                scaff_end  = int(split_line[7]) # relative to the scaffold
                direction  = split_line[8]
            
                new_record = [[chrom_name, chrom_beg, chrom_end, scaff_name, scaff_beg, scaff_end, direction]]
                if scaff_name in agp_dict:
                    agp_dict[scaff_name] += new_record
                else:
                    agp_dict[scaff_name]  = new_record

        start_gene_line = ''
        line = gff_file.readline()
        gff_line_number = 1
        
        # loop until file is over
        while line != '':
            if line[0] == '#':
                if line[:12] == '# start gene':
                    start_gene_line = line
                else:
                    print(line, end="", file=out_file)
            
                line = gff_file.readline()
                gff_line_number += 1
                continue
            # At this point we're at a tab-separated line,
            # a record corresponding to a gene.
            split_line = line.rstrip().split('\t')
            scaff_name = split_line[0]
            scaff_beg  = int(split_line[3]) # begin and end positions,
            scaff_end  = int(split_line[4]) # relative to the scaffold
            direction  = split_line[6]
            if scaff_name in agp_dict:
                scaff_list = agp_dict[scaff_name]
                for [cn, cb, ce, sn, sb, se, dr] in scaff_list:
                    if (scaff_beg >= sb) and (scaff_end <= se):
                        split_line[0] = cn
                        
                        if dr == '+':
                            split_line[3] = str(scaff_beg + cb - 1)
                            split_line[4] = str(scaff_end + cb - 1)
                        else:
                            split_line[3] = str(ce - scaff_end + 1)
                            split_line[4] = str(ce - scaff_beg + 1)
                        
                        if direction == dr:
                            split_line[6] = '+'
                        else:
                            split_line[6] = '-'
                        
                        if start_gene_line != '':
                            print(start_gene_line, end='', file=out_file)
                            start_gene_line = ''
                        print('\t'.join(split_line), end='\n', file=out_file)
                        break
            
                else:
                    print("! l.%d  Warning: gene (%s) split in scaffold (%s)" %
                          (gff_line_number, split_line[-1][3:], scaff_name))
                    
                    while not line[0:12] == "# start gene":
                        line = gff_file.readline()
                        gff_line_number += 1
                    
                    continue
            else:
            
                if start_gene_line != '':
                    print(start_gene_line, end='', file=out_file)
                    start_gene_line = ''
                print(line, end='\n', file=out_file)
            
                print('l%4d of GFF file: could not find scaffold (%s) not found in AGP file (%s).' % (gff_line_number, scaff_name, agp_filename))
        
            line = gff_file.readline()
            gff_line_number += 1
