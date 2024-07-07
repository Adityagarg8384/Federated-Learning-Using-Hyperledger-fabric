# pylint: disable=too-many-locals
# pylint: disable-all

"""
high level support for doing this and that.
"""

import logging
import torch
from torchvision.transforms import ToTensor, Normalize, Compose
from torchvision.datasets import MNIST
from torch.utils.data import random_split, DataLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_mnist(datapath: str = "./data"):
    logging.info("Downloading MNIST dataset")
    transform = Compose([ToTensor(), Normalize((0.1307,), (0.3081,))])
    trainset = MNIST(datapath, train=True, download=True, transform=transform)
    testset = MNIST(datapath, train=False, download=True, transform=transform)
    logging.info("MNIST dataset downloaded")
    return trainset, testset

def preparedatasets(num_clients: int, batch_size: int, val_ratio: float = 0.1):
    logging.info(f"Preparing dataset for {num_clients} clients with batch size {batch_size} and validation ratio {val_ratio}")
    trainset, testset = get_mnist()

    num_images = len(trainset) // num_clients  # Use integer division
    remainder = len(trainset) % num_clients  # Calculate any remainder
    logging.info(f"Each client will have approximately {num_images} images, with {remainder} images distributed to some clients")

    partition_lengths = [num_images] * num_clients
    for i in range(remainder):  # Distribute the remainder images
        partition_lengths[i] += 1

    trainsets = random_split(trainset, partition_lengths, torch.Generator().manual_seed(2023))
    logging.info(f"Train dataset partitioned into {num_clients} subsets")

    trainloaders = []
    valloaders = []
    for idx, subset in enumerate(trainsets):
        num_total = len(subset)
        num_val = int(val_ratio * num_total)
        num_train = num_total - num_val
        train_subset, val_subset = random_split(subset, [num_train, num_val], torch.Generator().manual_seed(2023))
        trainloaders.append(DataLoader(train_subset, batch_size=batch_size, shuffle=True, num_workers=2))
        valloaders.append(DataLoader(val_subset, batch_size=batch_size, shuffle=False, num_workers=2))
        logging.info(f"Client {idx}: {num_train} training samples, {num_val} validation samples")

    testloader = DataLoader(testset, batch_size=128)
    logging.info("Test dataset prepared")

    return trainloaders, valloaders, testloader

