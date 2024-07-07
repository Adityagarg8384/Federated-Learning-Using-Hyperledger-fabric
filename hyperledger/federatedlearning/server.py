# pylint: disable=too-many-locals
# pylint: disable-all

"""
high level support for doing this and that.
"""

import logging
from collections import OrderedDict
from omegaconf import DictConfig
import torch
from model import Net, test

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_on_fit_config(config: DictConfig):

    def fit_config_fn(server_round: int):
        logging.info(f"Preparing fit config for server round {server_round}")

        return {
            "lr": 0.01,
            "momentum": 0.9,
            "local_epochs": 1,
        }

    return fit_config_fn


def get_evaluate_fn(num_classes: int, testloader):

    def evaluate_fn(server_round: int, parameters, config):
        logging.info(f"Evaluating global model at server round {server_round}")

        model = Net(num_classes)
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        logging.info(f"Using device: {device}")

        params_dict = zip(model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.Tensor(v) for k, v in params_dict})
        model.load_state_dict(state_dict, strict=True)

        loss, accuracy = test(model, testloader, device)

        logging.info(f"Evaluation results - Loss: {loss}, Accuracy: {accuracy}")

        return loss, {"accuracy": accuracy}

    return evaluate_fn
