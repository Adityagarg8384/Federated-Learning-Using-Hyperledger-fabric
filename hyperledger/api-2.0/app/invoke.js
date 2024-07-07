// import constants from './config/constants.json' assert { type: 'json' };

import { Gateway, Wallets, DefaultEventHandlerStrategies } from 'fabric-network';

import fs from 'fs';
import path from 'path';
import log4js from 'log4js';
const { getLogger } = log4js;
const logger = getLogger('BasicNetwork');
import util from 'util';

import {getWalletPath} from './helper.js';


export const invokeTransaction = async (channelName, chaincodeName, fcn, args, username, org_name, transientData) => {
    try{
        console.log(channelName);
        console.log(chaincodeName);
        console.log(fcn);
        console.log(args);
        console.log(username);
        console.log(org_name);
        const ccp = await helper.getCCP(org_name) 
        console.log("Getting ccp done")
        const walletPath = await helper.getWalletPath(org_name)
        console.log("Getting wallet done")
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        console.log(`Wallet path: ${walletPath}`);

        let identity = await wallet.get(username);
        if (!identity) {
            console.log(`An identity for the user ${username} does not exist in the wallet, so registering user`);
            await helper.getRegisteredUser(username, org_name, true)
            identity = await wallet.get(username);
            console.log('Run the registerUser.js application before retrying');
            return;
        }
        console.log("identity = "+identity)
        const connectOptions = {
            wallet, identity: username, discovery: { enabled: true, asLocalhost: true },
            eventHandlerOptions: {
                commitTimeout: 100,
                strategy: DefaultEventHandlerStrategies.NETWORK_SCOPE_ALLFORTX
            }
            
        }

        console.log("Connectoptions successful");

        const gateway = new Gateway();
        await gateway.connect(ccp, connectOptions);
        console.log("gateway successful");

        const network = await gateway.getNetwork(channelName);
        console.log("network successful");

        const contract = network.getContract(chaincodeName);
        console.log("Contract successful");

        let result
        let message;
        // console.log(contract)
         result = await contract.submitTransaction(fcn, args[0], args[1], args[2]);
         console.log("Result successful")
        message = `Successfully added the images asset with key ${args[0]}`

        console.log(message)
        console.log(result);
        if (result.length > 0) {
            try {
                result = JSON.parse(result.toString('utf8'));
                console.log("Result parsed as JSON", result);
            } catch (e) {
                console.log("Result is not a JSON string", result.toString('utf8'));
            }
        } else {
            result = 'No return value from the chaincode';
        }
        console.log(result);
        console.log("result step")

        let response = {
            message: message,
            result
        }
        console.log(response)
        return response;
    }
    catch(err){
        console.log(`Getting error: ${err}`)
    }
}

// export {invokeTransaction}
// exports.invokeTransaction = invokeTransaction;