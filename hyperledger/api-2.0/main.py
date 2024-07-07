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
import requests
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def store_partition_info(client_id, train_count, val_count, url, peers, token, username, orgname):
    headers = {
        "Content-Type": "application/json",
         "Authorization": f"Bearer {token}",
    }
    data = {
        "fcn": "StoreDatasetInfo",
        "args": [client_id, str(train_count), str(val_count)],
        "username": username,
        "orgname":orgname
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        logging.info(f"Partition info for client {client_id} stored successfully on {url}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Error connecting to {url}: {e}")
    except requests.exceptions.Timeout as e:
        logging.error(f"Request to {url} timed out: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")

def get_mnist(datapath: str = "./data"):
    transform = Compose([ToTensor(), Normalize((0.1307,), (0.3081,))])

    for _ in range(3):  # Retry up to 3 times
        try:
            trainset = MNIST(datapath, train=True, download=True, transform=transform)
            testset = MNIST(datapath, train=False, download=True, transform=transform)
            return trainset, testset
        except Exception as e:
            logging.error(f"Error downloading MNIST dataset: {e}. Retrying...")

    raise RuntimeError("Failed to download MNIST dataset after multiple attempts.")

def preparedatasets(num_clients: int, batch_size: int, val_ratio: float = 0.1):
    trainset, testset = get_mnist()

    num_images = len(trainset) // num_clients
    remainder = len(trainset) % num_clients

    partition_lengths = [num_images] * num_clients
    for i in range(remainder):
        partition_lengths[i] += 1

    trainsets = random_split(trainset, partition_lengths, torch.Generator().manual_seed(2023))

    trainloaders = []
    valloaders = []
    urls = [
        "http://localhost:4000/channels/mychannel/chaincodes/fabcar2",
        "http://localhost:4000/channels/mychannel/chaincodes/fabcar2"
    ]

    peers = [
        "peer0.org1.example.com",
        "peer0.org2.example.com",
        "peer1.org2.example.com",
        "peer1.org1.example.com",
    ]
    token=[
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTk5NjA3MzIsInVzZXJuYW1lIjoiYWRpdHlhIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE3MTk5MjQ3MzJ9.mjbB4STX8zJk7RR_r0AmFMivSo6VGf2gNWwVOV5fAM4",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTk5NjA3MzIsInVzZXJuYW1lIjoiYWRpdHlhIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE3MTk5MjQ3MzJ9.mjbB4STX8zJk7RR_r0AmFMivSo6VGf2gNWwVOV5fAM4",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTk5NjA3MzIsInVzZXJuYW1lIjoiYWRpdHlhIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE3MTk5MjQ3MzJ9.mjbB4STX8zJk7RR_r0AmFMivSo6VGf2gNWwVOV5fAM4",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTk5NjA3MzIsInVzZXJuYW1lIjoiYWRpdHlhIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE3MTk5MjQ3MzJ9.mjbB4STX8zJk7RR_r0AmFMivSo6VGf2gNWwVOV5fAM4",
    ]

    username=[
        "aditya",
        "aditya2",
        "aditya3",
        "aditya4"
    ]

    orgname=[
        "Org1",
        "Org2",
        "Org2",
        "Org1"
    ]

    for idx, subset in enumerate(trainsets):
        num_total = len(subset)
        num_val = int(val_ratio * num_total)
        num_train = num_total - num_val
        train_subset, val_subset = random_split(subset, [num_train, num_val])
        trainloaders.append(DataLoader(train_subset, batch_size=batch_size, shuffle=True, num_workers=2))
        valloaders.append(DataLoader(val_subset, batch_size=batch_size, shuffle=False, num_workers=2))
        logging.info(f"Client {idx}: {num_train} training samples, {num_val} validation samples")
        
        store_partition_info(f"client{idx}", num_train, num_val, urls[idx % 2], peers[idx%4], token[idx%1], username[idx%1], orgname[idx%1])

    testloader = DataLoader(testset, batch_size=128)
    logging.info("Test dataset prepared")

    return trainloaders, valloaders, testloader

def fetchdata(username, orgname, token, url):
    headers = {
        "Content-Type": "application/json",
         "Authorization": f"Bearer {token}",
    }
    data = {
        "fcn": "GetAllData",
        "username": username,
        "orgname":orgname
    }

    try:
        response = requests.get(url, headers=headers, data=json.dumps(data))
        print(response)
        t= response.json()
        print(t)
        return t
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Error connecting to {url}: {e}")
    except requests.exceptions.Timeout as e:
        logging.error(f"Request to {url} timed out: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
    return []




if __name__ == "__main__":
    # trainloaders, valloaders, testloaders= preparedatasets(10, 10)
    url="http://localhost:4000/qscc/channels/mychannel/chaincodes/fabcar2"
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjAzODE3MzMsInVzZXJuYW1lIjoiYWRpdHlhIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE3MjAzNDU3MzN9.Fe8eZ3cPQaYoJz250F6AT0UsC5_-ZctCQ9anfOU678A"
    t=fetchdata("aditya", "Org1", token, url)

