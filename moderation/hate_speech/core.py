import torch
from torch import nn
import numpy as np

class MLP(nn.Module):
    def __init__(self, batch_size = 256):
        super().__init__() # initializing super class
        
        self.batch_size = batch_size
        
        # first dense layer
        self.dense_1 = nn.Linear(
            in_features = 302,
            out_features = 1024
        )
        
        self.dense_2 = nn.Linear(
            in_features = 1024,
            out_features = 512
        )
        
        self.dense_3 = nn.Linear(
            in_features = 512,
            out_features = 256
        )
        
        self.dense_4 = nn.Linear(
            in_features = 256,
            out_features = 128
        )
        
        self.dense_5 = nn.Linear(
            in_features = 128,
            out_features = 64
        )
        
        self.dense_6 = nn.Linear(
            in_features = 64,
            out_features = 32
        )
        
        self.out = nn.Linear(
            in_features = 32,
            out_features = 1
        )
        
        self.dropout_p4 = nn.Dropout(p=0.4)
        self.dropout_p5 = nn.Dropout(p=0.5)
        self.dropout_p3 = nn.Dropout(p=0.3)
        
        self.batchnorm_1024 = nn.BatchNorm1d(1024)
        self.batchnorm_512 = nn.BatchNorm1d(512)
        self.batchnorm_256 = nn.BatchNorm1d(256)
        self.batchnorm_128 = nn.BatchNorm1d(128)
        self.batchnorm_64 = nn.BatchNorm1d(64)
        self.batchnorm_32 = nn.BatchNorm1d(32)
        
        return
    
        
    def forward(self, X: np.array):
        
        X = torch.relu(self.dense_1(X))
        X = self.dropout_p5(X)
        X = self.batchnorm_1024(X)
        
        X = torch.relu(self.dense_2(X))
        X = self.dropout_p4(X) # 3 -> 5 -> 4
        X = self.batchnorm_512(X)

        X = torch.relu(self.dense_3(X))
        X = self.dropout_p5(X)
        X = self.batchnorm_256(X)
        
        X = torch.relu(self.dense_4(X))
        X = self.dropout_p3(X)
        X = self.batchnorm_128(X)
        
        X = torch.relu(self.dense_5(X))
        X = self.dropout_p3(X)
        X = self.batchnorm_64(X)

        
        X = torch.relu(self.dense_6(X))
        X = self.batchnorm_32(X)
        
        X = self.out(X)
        
        return X