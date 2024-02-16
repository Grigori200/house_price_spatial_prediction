import pandas as pd
def valid_address(df, eps=1e-6):
    coords = df[['lat', 'lng', 'address', 'price']].sort_values(['lat', 'lng'])
    coords['region_id'] = (coords[['lat', 'lng']].diff().abs() > eps).any(axis=1, skipna=False).astype(int).cumsum()
    region_mapping = coords.groupby('region_id', as_index=False)['address'].value_counts().drop_duplicates(
        'region_id').drop(columns='count').rename(columns={'address': 'valid_address'})
    coords = pd.merge(coords, region_mapping)
    return coords

from torch.utils.data import TensorDataset, DataLoader
import torch.nn.functional as F


def split_data(data, train_size=0.8):
    train_idx = data.sample(frac=train_size).index
    train_data, test_data = data.loc[train_idx], data.drop(index=train_idx)
    train_data = train_data.dropna(axis=1)
    test_data = train_data.dropna(axis=1)

    return train_data, test_data

def to_dataloaders(x_train, y_train, x_test, y_test, bs=32):
    train_ds = TensorDataset(F.normalize(x_train), y_train)
    test_ds = TensorDataset(F.normalize(x_test), y_test)

    train_dl = DataLoader(train_ds, bs)
    test_dl = DataLoader(test_ds, bs)
    return train_dl, test_dl