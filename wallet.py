# Import dependencies
import subprocess
import json
import os
from dotenv import load_dotenv
from web3 import Web3
import bit
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI


#create web3 object
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import *
  
# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={depth} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys


# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {
    ETH:derive_wallets(ETH),
    BTC:derive_wallets(BTC)
}

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == BTCTEST:
        return bit.PrivateKeyTestnet(priv_key) 
    elif coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    else:
        print('Error: Invalid coin or key. Please use ETH or BTCTEST and verify wallet keys')
    
    
# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.

def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": to, "value": amount}
    )
        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
    }
    elif coin == BTCTEST:
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to,amount,BTC)])
    else:
        print('Error: Invalid coin selection. Please use ETH or BTCTEST')

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.

def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_tx(account, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        raw_tx = create_tx(coin,account,to,amount)
        signed_tx = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
    else:
        print('Error: Invalid coin selection. Please use ETH or BTCTEST')