"""Base provider interface."""
from typing import Optional, Dict, Any
import pandas as pd
from abc import ABC, abstractmethod


class DataProvider(ABC):
    name: str = "base"

    @abstractmethod
    def fetch_history(self, symbol: str, days: int = 250) -> Optional[pd.DataFrame]:
        ...
