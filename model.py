from torch import nn

class SpatialModel(nn.Module):
    def __init__(self, *hidden_dims, features=30):
        super().__init__()
        self.model = nn.Sequential(
            *[layer for dim_in, dim_out in zip([features, *hidden_dims],
                                               [*hidden_dims, 1])
              for layer in [nn.Linear(dim_in, dim_out), nn.ReLU()]][:-1]
        )

    def forward(self, x):
        return self.model(x)