from abc import ABC, abstractmethod
import pandas as pd


class BaseExtractor(ABC):
    COLUMN_RANGES: dict  # subclass must define

    @abstractmethod
    def is_transaction_page(self, words: list) -> bool:
        pass

    @abstractmethod
    def extract(self, pdf_path: str) -> pd.DataFrame:
        pass
