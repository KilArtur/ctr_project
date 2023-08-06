import sys
import pandas as pd
import logging
from tqdm.notebook import tqdm

from sklearn.base import BaseEstimator, TransformerMixin

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class DeviceCountTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, column_name: str):
        self.device_count_feature = []
        self.column_name = column_name
        self.data_group = None

    def fit(self, X: pd.DataFrame, y=None):
        # count the number of ads per unique user ( device ip )
        data_group = X[[self.column_name, "id"]].groupby([self.column_name]).count()

        # make a column with values with device id counts
        for index in tqdm(X[self.column_name]):
            self.device_count_feature.append(data_group["id"][index])

        return self

    def transform(self, X: pd.DataFrame):
        return pd.DataFrame(
            self.device_count_feature, columns=[f"{self.column_name}_count"]
        )
