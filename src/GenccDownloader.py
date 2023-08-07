import os
import time
from logging import Logger

from common_utils import read_config_file


class GenccDownloader:
    def __init__(self, logger: Logger, config_file_path: str, output_dir: str):
        config = read_config_file(config_file_path)
        self.logger = logger
        self.config = config["GenCC"]
        self.raw_file_path = os.path.join(output_dir, "gencc_submission.tsv")

    def trim_line(self, split_lines: list) -> list:
        """Trim words in list

        Args:
            split_lines (list): list of split words.

        Returns:
            (list): list of trimmed split words.

        Examples:
            >>> split_lines
            [
                "\"id1",
                "HGNC:00001",
                "PMID:\xa030827498",
                "MIM 618494\t",
                "autism spectrum disorder\""
            ]
            >>> new_split_lines
            [
                "id1",
                "HGNC:0001",
                "PMID:30827498",
                "MIM 618494",
                "autism spectrum disorder
            ]
        """
        new_split_lines = list()
        for split in split_lines:
            new_split_lines.append(
                split.strip(" ")
                .replace("\t", "")
                .replace('"', "")
                .replace("\xa0", "")
            )

        return new_split_lines

    def download_raw_file(self):
        """wget을 이용해 GenCC data raw file을 정해진 디렉토리에 다운로드받고, \
            그 파일의 절대 경로를 리턴하는 함수
            
        Note:
            파일 다운로드는 10초 간격으로 3번까지 시도한 후, 1시간 뒤에 마지막으로 1번 더 시도한다.
            
        """
        gencc_download_url = self.config["download_url"]
        download_command = f"wget -O {self.raw_file_path} {gencc_download_url}"

        trial, max_trial = 1, 3
        while trial <= max_trial:
            if os.system(download_command) == 0:
                break
            time.sleep(10)
            trial += 1

        if not os.path.exists(self.raw_file_path):
            time.sleep(3600)
            if os.system(download_command) != 0:
                self.logger.error("GenCC data file is not downloaded.")
                self.logger.error(f"GenCC download URL: {gencc_download_url}")
                raise Exception("WgetError")

        return

    def read_raw_file(self) -> dict:
        """GenCC tsv 파일을 읽어서 trim한 뒤, \
        GenCC UUID를 key로 하고, target하는 값들의 list를 value로 가진 dictionary로 리턴하는 함수

        Returns:
            (dict): GenCC UUID를 key로 하고, \
                target하는 값들의 list를 value로 가진 dictionary.

        Note:
            target하는 값들의 key는 configuration을 통해 컨트롤된다.
            
        Examples:
            >>> file_open = open(self.raw_file_path)
            >>> data = file_open.readlines()
            >>> data
            [
                "\"uuid\"\t\"gene_name\"\t\"phenotype_name\"\t\"confidence\"\n", 
                "\"GENCC1\"\t\"gene_aa\"\t\"phenotype_8503\"\t\"strong\"\n",
                "\"GENCC2\"\t\"gene_kc\"\t\"phenotype_0239\"\t\"moderate\"\n", 
                "\"GENCC3\"\t\"gene_xs\"\t\"phenotype_1174\"\t\"weak\"\n", 
                "\"GENCC4\"\t\"gene_lp\"\t\"phenotype_9065\n"
                "additional_blah_blah\"\t\"strong\"\n\"
            ]
            >>> self.config["Key"]
            ["phtenotye_name", "gene_name", "confidence"]
            >>> uuid2gencc_data
            {
                "GENCC1": ["phenotype_8503", "gene_aa", "strong"], 
                "GENCC2": ["phenotype_0239", "gene_kc", "moderate"], 
                "GENCC3": ["phenotype_1174", "gene_xs", "weak],
                "GENCC4": ["phenotype_9065additional_blah_blah", "gene_lp", "strong"]
            }
        """
        uuid2gencc_data = dict()
        with open(self.raw_file_path) as file_open:
            for line in file_open:
                if line.startswith('"uuid"'):
                    split_lines = line.strip().split('"\t"')
                    new_split_lines = self.trim_line(split_lines)
                    key_indexes = [
                        new_split_lines.index(gencc_key)
                        for gencc_key in self.config["Key"]
                    ]
                    new_split_lines = list()

                elif line.startswith('"GENCC'):
                    if new_split_lines:
                        uuid = new_split_lines[0]
                        data = [new_split_lines[idx] for idx in key_indexes]
                        uuid2gencc_data[uuid] = data
                    split_lines = line.strip().split('"\t"')
                    new_split_lines = self.trim_line(split_lines)

                else:
                    split_lines = line.strip().split('"\t"')
                    tmp_split_lines = self.trim_line(split_lines)
                    if new_split_lines[-1].endswith(";"):
                        new_split_lines[-1] += f"{tmp_split_lines[0]}"
                    else:
                        new_split_lines[-1] += f";{tmp_split_lines[0]}"
                    if len(split_lines) != 1:
                        new_split_lines.extend(tmp_split_lines[1:])

            uuid = new_split_lines[0]
            data = [new_split_lines[idx] for idx in key_indexes]
            uuid2gencc_data[uuid] = data

        return uuid2gencc_data
