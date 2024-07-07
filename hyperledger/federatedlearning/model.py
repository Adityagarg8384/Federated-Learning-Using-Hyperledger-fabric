# pylint: disable=too-many-locals
# pylint: disable-all

"""
high level support for doing this and that.
"""

import logging
import torch
import torch.nn as nn
import torch.nn.functional as F

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Net(nn.Module):

    def __init__(self, num_classes: int) -> None:
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 4 * 4, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def train(net, trainloader, optimizer, epochs, device: str):

    logging.info("Starting training")
    criterion = torch.nn.CrossEntropyLoss()
    net.train()
    net.to(device)
    for epoch in range(epochs):
        running_loss = 0.0
        for i, (images, labels) in enumerate(trainloader, 0):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # Print statistics
            running_loss += loss.item()
            if i % 100 == 99:  # Print every 100 mini-batches
                logging.info(f"[Epoch {epoch + 1}, Batch {i + 1}] loss: {running_loss / 100:.3f}")
                running_loss = 0.0
    logging.info("Finished training")

def test(net, testloader, device: str):

    logging.info("Starting evaluation")
    criterion = torch.nn.CrossEntropyLoss()
    correct, total, loss = 0, 0, 0.0
    net.eval()
    net.to(device)
    with torch.no_grad():
        for data in testloader:
            images, labels = data[0].to(device), data[1].to(device)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    accuracy = correct / total
    logging.info(f"Test loss: {loss:.3f}, Accuracy: {accuracy:.3f}")
    return loss, accuracy

def models_to_parameters(model):
    from flwr.common.parameter import ndarrays_to_parameters
    ndarrays= [val.cpu().numpy() for _, val in model.state_dict().items()]
    parameters= ndarrays_to_parameters(ndarrays)
    print("Extracting parameters")
    return parameters
