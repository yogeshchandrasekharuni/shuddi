import torch
from core import MLP
import torch
import torch.nn as nn
import torch.optim as opt
torch.set_printoptions(linewidth=120)
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter

if __name__ == '__main__':
    '''
    Gets the model as an onnx file and also draws the architecture onto a TensorBoard
    '''
    model = MLP()
    model.load_state_dict(torch.load('data/mlp_model_state_dict.pth'))
    dummy_input = torch.autograd.Variable(torch.randn(1, 302))
    torch.onnx.export(model, dummy_input, 'data/model.onnx')

    writer = SummaryWriter()
    writer.add_graph(model, dummy_input)
    writer.close()