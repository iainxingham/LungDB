# Base class for various report parsers

from tika import parser
from os import path # Replace with pathlib?
from pathlib import Path
from enum import Enum, unique, auto
import re
import logging 

@unique
class ParseError(Enum):
    PARSE_OK = auto()
    PARSE_NO_FILE = auto()
    PARSE_CANT_EXTRACT = auto()
    PARSE_NOT_EXTRACTED_YET = auto()

class BaseParse:
    def __init__(self, file: Path):
        self.extracted = dict()
        self.source_file = file.resolve().as_uri()
        if file.exists():
            data = parser.from_file(self.source_file)
            self.text = data['content']
            self.error_code = ParseError.PARSE_NOT_EXTRACTED_YET
        else:
            self.error_code = ParseError.PARSE_NO_FILE
            logging.error('Can\'t read file: {0}'.format(self.source_file))

    def is_ok(self) -> bool:
        if self.error_code is ParseError.PARSE_OK:
            return True
        else:
            return False

    def _add_extract(self, key: str, regex: str, group: int):
        result = re.compile(regex).search(self.text)
        if result is None:
            self._log('Unable to extract \"{0}\" from {1}\n'.format(key, self.source_file))
            self.error_code = ParseError.PARSE_CANT_EXTRACT
        else:
            self.extracted[key] = result.group(group)

    def _log(self, msg: str):
        logging.warning(str)

    def get_data(self) -> dict:
        """
        Return a dictionary with the extracted data
        Will return something (possibly an empty dictionary, possibly a partly extracted record) even if
        error_code != PARSE_OK
        """
        return self.extracted

    def get_sourcefile(self) -> str:
        return self.source_file


    
