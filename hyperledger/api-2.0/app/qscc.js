import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { Gateway, Wallets } from 'fabric-network';
import log4js from 'log4js';
import util from 'util';
import axios from 'axios';
import path from 'path';
import fs from 'fs';



// import { getCCP, getWalletPath, getRegisteredUser } from './helper.js';

// Use import.meta.url to get the current module file path
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const logger = log4js.getLogger('BasicNetwork');

export const getCCP = async (org) => {
    let ccpPath;
    if (org == "Org1") {
        ccpPath = path.resolve(__dirname, '..', 'config', 'connection-org1.json');

    } else if (org == "Org2") {
        ccpPath = path.resolve(__dirname, '..', 'config', 'connection-org2.json');
    } else
        return null
    const ccpJSON = fs.readFileSync(ccpPath, 'utf8')
    const ccp = JSON.parse(ccpJSON);
    return ccp
}

export const getWalletPath = async (org) => {
    let walletPath;
    if (org == "Org1") {
        walletPath = path.join(process.cwd(), 'org1-wallet');

    } else if (org == "Org2") {
        walletPath = path.join(process.cwd(), 'org2-wallet');
    } else
        return null
    return walletPath

}

export const qscc = async (channelName, chaincodeName, fcn, username, org_name) => {
    try {
        logger.info("In qscc");

        const ccp = await getCCP(org_name);
        const walletPath = await getWalletPath(org_name);
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        logger.info(`Wallet path: ${walletPath}`);

        let identity = await wallet.get(username);
        if (!identity) {
            logger.warn(`An identity for the user ${username} does not exist in the wallet, so registering user`);
            await getRegisteredUser(username, org_name, true);
            identity = await wallet.get(username);
            logger.info('Run the registerUser.js application before retrying');
            return;
        }

        const gateway = new Gateway();
        await gateway.connect(ccp, {
            wallet,
            identity: username,
            discovery: { enabled: true, asLocalhost: true }
        });

        const network = await gateway.getNetwork(channelName);
        const contract = network.getContract(chaincodeName);

        let result;
        result = await contract.evaluateTransaction(fcn);
        logger.info("Got the result: " + result);

        // Example of using axios to make an HTTP POST request
        let url = "http://127.0.0.1:5000/start_simulation";
        const response = await axios.post(url,result, {
            headers: {
                'Content-Type': 'application/json'
            },
            
        });
        const res = response.data; // Assuming the response is JSON
        logger.info("Got the response: " + JSON.stringify(res));

        await gateway.disconnect();

        return result.toString('utf8'); // Convert result to string if needed
    } catch (error) {
        logger.error(`Failed to evaluate transaction: ${error}`);
        return error.message;
    }
};
