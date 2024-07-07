# pylint: disable=too-many-locals
# pylint: disable-all

"""
high level support for doing this and that.
"""

import logging
import pickle
from pathlib import Path
from flask import Flask, jsonify, request
import flwr as fl
from flower import generate_client_fn
from server import get_on_fit_config, get_evaluate_fn
from datasets import preparedatasets
from omegaconf import DictConfig, OmegaConf
import hydra
from hydra.utils import instantiate
from hydra.core.hydra_config import HydraConfig
import re
import numpy as np



app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

history = None
save_path = None

@hydra.main(config_path="conf", config_name="base", version_base=None)
def hydra_main(cfg: DictConfig):
    global app
    app.config['HYDRA_CFG'] = cfg
    app.run(debug=True, port=5000)

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    print("Currently in the start_simulation congrats")
    global history, save_path
    cfg = app.config['HYDRA_CFG']


    if request.method == 'POST':
        data = request.get_json()
        print("Hello world")
        print(data)
        train=[]
        trainloaders, validationloaders, testloader = preparedatasets(10, 10)
        t=[]
        v=[]
        for i in data:
            match = re.search(r'client(\d+)', i)
          
            if match:
               b=int(match.group(1))
               t.append(trainloaders[b])
               v.append(validationloaders[b])
        
        trainloaders=t
        validationloaders=v
        print("Generating client")
        client_fn = generate_client_fn(trainloaders, validationloaders, 10)
        print("Client generated successfully")
        print("Generating Strategy")
        layer1_weights = np.random.rand(784, 10).astype(np.float32)
        layer1_bias = np.random.rand(10).astype(np.float32)
        # initial_parameters = fl.common.ndarrays_to_parameters([layer1_weights, layer1_bias])
        
        # strategy = fl.server.strategy.FedAvg(
        #     fraction_fit=0.0,
        #     min_fit_clients=2,
        #     fraction_evaluate=0.0,
        #     min_evaluate_clients=2,
        #     min_available_clients=10,
        #     on_fit_config_fn=get_on_fit_config({
        #          "lr":0.01,
        #          "momentum":0.9,
        #          "local_epochs":1
        #     }),
        #     evaluate_fn=get_evaluate_fn(10, testloader),
        #     initial_parameters= cfg.initial_paramers
                
        # )
        strategy= instantiate(cfg.strategy, evaluate_fn=get_evaluate_fn(10, testloader),)


        print("Strategy generated successfully")
        print("Starting simulation")
        history = fl.simulation.start_simulation(
            client_fn=client_fn,
            num_clients=10,
            config=fl.server.ServerConfig(num_rounds=5),
            strategy=strategy,
            client_resources={'num_cpus':2}
        )

        print("Simulation started successfully")
        return jsonify({"succ": "Successfullt done the operation"})
    else:
        return jsonify({"error": "Invalid request method"})

@app.route('/get_history', methods=['GET'])
def get_history():
    global history

    if history:
        return jsonify(history)
    else:
        return jsonify({"message": "History not available"})

if __name__ == "__main__":
    hydra_main()
    Port= 5000
    print("Backend is running ${Port}" )
    app.run(debug=True,port= Port)
