import os
import time
from logging import Logger

from common_utils import read_config_file


class MondoHandler:
    def __init__(self, logger: Logger, config_file_path: str, output_dir: str):
        config = read_config_file(config_file_path)
        self.logger = logger
        self.config = config["MONDO"]
        self.output_dir = output_dir
        self.files = self.config["file_list"]

    def download_files(self):
        """target하는 MONDO data file들을 정해진 디렉토리에 다운로드하는 함수

        Note:
            target하는 MONDO data file들은 configuration을 통해 컨트롤된다.
            파일 다운로드는 10초 간격으로 3번까지 시도한 후, 1시간 뒤에 마지막으로 1번 더 시도한다.

        """
        download_url = self.config["download_url"]
        for mondo_file in self.files:
            mondo_file_path = os.path.join(self.output_dir, mondo_file)
            print(mondo_file_path)
            download_command = f"wget -O {mondo_file_path} {os.path.join(download_url, mondo_file)}"

            trial, max_trial = 1, 3
            while trial <= max_trial:
                if os.system(download_command) == 0:
                    break
                time.sleep(10)
                trial += 1

            if not os.path.exists(mondo_file_path):
                time.sleep(3600)
                if os.system(download_command) != 0:
                    self.logger.error("MONDO data file is not downloaded")
                    self.logger.error(f"Failed data file: {mondo_file}")
                    raise Exception("WgetError")

        return

    def read_files(self, db_type: str) -> dict:
        """MONDO raw data file 중 특정 db_type에 해당하는 파일들만 읽은 뒤, \
        MONDO ID와 그 DB ID를 mapping 해주는 dictionary를 리턴하는 함수

        Args:
            db_type (str): target하는 db_type

        Returns:
            (dict): MONDO ID와 target DB ID를 mapping 해주는 dictionary
        """
        mondo_id2other_id = dict()
        for mondo_file in self.files:
            if db_type in mondo_file:
                mondo_file_path = os.path.join(self.output_dir, mondo_file)
                with open(mondo_file_path) as mondo_open:
                    for line in mondo_open:
                        if line.startswith("MONDO"):
                            mondo_id = line.strip().split("\t")[0]
                            other_id = line.strip().split("\t")[3]
                            mondo_id2other_id[mondo_id] = other_id

        return mondo_id2other_id
