from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

_solc_version = "0.6.0"
install_solc(_solc_version)

with open("SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile our solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version=_solc_version,
)

with open("compiled_sol", "w") as file:
    json.dump(compiled_sol, file)


# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# deploy
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/ba4d736917a04b6a899a0def0f36825f")
)
chain_id = 4
my_address = "0x7688C02322d88a468F17399E852309D77e9348Cb"
private_key = os.getenv("PRIVATE_KEY")


# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)
# create transaction object
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
# print(transaction)


# sign transaction
signed_trans = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_trans)

# send signed trans
print("Deploying Contract....")
tx_hash = w3.eth.send_raw_transaction(signed_trans.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

######################################## -------------------- #########################


# working with the contract, you always need
# contract address
# contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> making a call and getting something to return NO STATE CHANGES
# Transact -> actually makes a state change

# this is "our FAVORITENUMBER"
print(simple_storage.functions.retrieve().call())


############################# --------------------------------- #######################
# created transaction
print("Updating Contract......")
store_trans = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
# signed transaction
signed_store_trans = w3.eth.account.sign_transaction(
    store_trans, private_key=private_key
)
# sent transaction

trans__store_hash = w3.eth.send_raw_transaction(signed_store_trans.rawTransaction)
# waited for it to finish
trans_store_receipt = w3.eth.wait_for_transaction_receipt(trans__store_hash)
print("Updated!")
print(simple_storage.functions.retrieve().call())
