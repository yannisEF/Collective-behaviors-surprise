import torch

class ActionNetwork(torch.nn.Module):
    def __init__(self, input_size=5, hidden_size=2, output_size=1):
        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.fully_connected1 = torch.nn.Linear(self.input_size, self.hidden_size)
        self.fully_connected2 = torch.nn.Linear(self.hidden_size, self.output_size)

    def forward(self, x):
        relu = torch.nn.ReLU()(self.fully_connected1(x))
        return torch.nn.Sigmoid()(self.fully_connected2(relu))
    
class PredictionNetwork(torch.nn.Module):
    def __init__(self, input_size=5, hidden_size=4, output_size=4):
        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.fully_connected1 = torch.nn.RNN(self.input_size, self.hidden_size)
        self.fully_connected2 = torch.nn.Linear(self.hidden_size, self.output_size)

        self.hn = torch.randn(1, 1, 4)

    def forward(self, x):
        out, self.hn = self.fully_connected1(x, self.hn)
        relu = torch.nn.ReLU()(out)
        return torch.nn.Sigmoid()(self.fully_connected2(relu))

