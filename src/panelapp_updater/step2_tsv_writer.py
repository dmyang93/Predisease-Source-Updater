def write_tsv_file(input_dict, tsv_filename, header_list):
    with open(tsv_filename, 'w') as f:
        f.write('\t'.join(header_list) + '\n')
        for key in input_dict:
            f.write(key)
            for header in header_list[1:]:
                f.write('\t' + input_dict[key][header])
            f.write('\n')

    