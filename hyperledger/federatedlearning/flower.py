# pylint: disable=too-many-locals
# pylint: disable-all

"""
high level support for doing this and that.
"""

import logging
from collections import OrderedDict
from typing import Dict, Tuple
from flwr.common import NDArrays, Scalar

import torch
import flwr as fl

from model import Net, train, test

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FlowerClient(fl.client.NumPyClient):

    def __init__(self, trainloader, valloader, num_classes) -> None:
        super().__init__()

        self.trainloader = trainloader
        self.valloader = valloader

        self.model = Net(num_classes)

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        logging.info(f"FlowerClient initialized with device {self.device}")

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.Tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)
        logging.info("Model parameters set")

    def get_parameters(self, config: Dict[str, Scalar]):
        logging.info("Getting model parameters")
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def fit(self, parameters, config):
        logging.info("Starting training")
        self.set_parameters(parameters)

        lr = 0.01
        momentum = 0.9
        epochs = 1
        logging.info(f"Training with lr={lr}, momentum={momentum}, epochs={epochs}")

        optim = torch.optim.SGD(self.model.parameters(), lr=lr, momentum=momentum)
        train(self.model, self.trainloader, optim, epochs, self.device)

        logging.info("Training completed")
        return self.get_parameters({}), len(self.trainloader), {}

    def evaluate(self, parameters: NDArrays, config: Dict[str, Scalar]):
        logging.info("Starting evaluation")
        self.set_parameters(parameters)
        loss, accuracy = test(self.model, self.valloader, self.device)
        logging.info(f"Evaluation completed with loss={loss}, accuracy={accuracy}")
        return float(loss), len(self.valloader), {"accuracy": accuracy}


def generate_client_fn(trainloaders, valloaders, num_classes):

    def client_fn(cid: str):
        logging.info(f"Generating client for cid={cid}")
        return FlowerClient(
            trainloader=trainloaders[int(cid)],
            valloader=valloaders[int(cid)],
            num_classes=num_classes,
        )

    return client_fn
