def trim_line(splitted_line):
    """trim words in list

    Args:
        splitted_line (list): list of splitted words.

    Returns:
        list: list of trimmed splitted words
    """
    new_splitted_line = list()
    for splitted in splitted_line:
        new_splitted_line.append(
            splitted.strip(" ").replace("\t", "").replace('"', "")
        )

    return new_splitted_line


def reformat_gencc_tsv_file(gencc_tsv_file, gencc_reformat_tsv_file):
    reformat_lines = list()
    with open(gencc_tsv_file) as f:
        for line in f:
            if line.startswith('"uuid"'):
                splitted_line = line.strip().split('"\t"')
                new_splitted_line = trim_line(splitted_line)
                reformat_lines.append(new_splitted_line)
                new_splitted_line = list()
            else:
                if line.startswith('"GENCC'):
                    if new_splitted_line:
                        reformat_lines.append(new_splitted_line)
                    splitted_line = line.strip().split('"\t"')
                    new_splitted_line = trim_line(splitted_line)
                else:
                    splitted_line = line.strip().split('"\t"')
                    if len(splitted_line) == 1:
                        new_splitted_line[-1] += f";{splitted_line[0]}"
                    else:
                        new_splitted_line[-1] += f";{splitted_line[0]}"
                        tmp_splitted_line = trim_line(splitted_line[1:])
                        new_splitted_line.extend(tmp_splitted_line)
        reformat_lines.append(new_splitted_line)

    with open(gencc_reformat_tsv_file, "w") as f:
        for splitted_line in reformat_lines:
            f.write("\t".join(splitted_line) + "\n")


def compare_two_column(gencc_tsv_file, colname1, colname2, comp_way=1):
    gencc_dict = dict()
    with open(gencc_tsv_file) as f:
        chk = False
        for line in f:
            split_line = line.strip().split("\t")
            if not chk:
                colnum1 = split_line.index(colname1)
                colnum2 = split_line.index(colname2)
                print(f"GenCC UUID -- {colname1} -- {colname2}")
                chk = True
            else:
                colval1, colval2 = split_line[colnum1], split_line(colnum2)
                gencc_dict[split_line[0]] = split_line
                if comp_way == 1:
                    if colval1 != colval2:
                        print(f"{split_line[0]} -- {colval1} -- {colval2}")
                elif comp_way == 2:
                    if not (
                        colval1.upper().startswith(colval2.upper())
                        or colval2.upper().startswith(colval1.upper())
                    ):
                        print(f"{split_line[0]} -- {colval1} -- {colval2}")
                else:
                    raise ValueError

    return gencc_dict
