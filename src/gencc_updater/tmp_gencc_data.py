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