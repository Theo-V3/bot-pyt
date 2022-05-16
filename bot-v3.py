from asyncio.log import logger
from audioop import add
import json
from symtable import Symbol
from eth_account import Account
from eth_utils import to_checksum_address
from web3 import Web3
import telebot
import requests
from unicodedata import name
import time

avalanche_url = "https://api.avax.network/ext/bc/C/rpc"
web3 = Web3(Web3.HTTPProvider(avalanche_url))


with open ("ABIfactory.json") as f:
    ABIfactory = json.load(f)
with open ("ABIpaire.json") as f:
    ABIpaire = json.load(f)
with open ("ABItoken.json") as f:
    ABItoken = json.load(f)


addresse = "0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10"
contratFactory = web3.eth.contract(abi=ABIfactory, address=addresse)

prevPaires = 0
while True:
    newPaires = contratFactory.functions.allPairsLength().call()
    if newPaires > prevPaires:
        prevPaires = newPaires
        print("New pair : {}" .format(newPaires))
        addressNewPair = contratFactory.functions.allPairs(newPaires-1).call()
        
        print(addressNewPair)

        knownTokens = [
            "0xc7198437980c041c805A1EDcbA50c1Ce5db95118"
            "0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664"
            "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7"
        ]

        def InitToken(tokenAddress):
            contratToken = web3.eth.contract(abi=ABItoken, address=web3.toChecksumAddress(tokenAddress))
            token = Token(
                contratToken.functions.name().call(),
                contratToken.functions.symbol().call(),
                contratToken.functions.decimals().call(),
                contratToken.totalSupply().call(),
                web3.toChecksumAddress(tokenAddress),
            )
            return token

        class Token ():
            def __init__(self, name, symbol, decimals, totalSupply, address):
                self.name = name
                self.decimals = decimals
                self.symbol = symbol.replace (" ", "")
                self.totalSupply = totalSupply
                self.address = address
            def __str__ (self):
                return "{}".format(self.symbol)
        
        def whenNewPair(pairAddress):
            pair = {
                "token0":"",
                "token1":"",
                "NewTokenMC":"",
                "reserve0":"",
                "reserve1":"",
            }
            contractPaires = web3.eth.contract(abi=ABIpaire, address=addressNewPair)
            #check les tokens
            pair["token0"] = InitToken(contractPaires.functions.token0().call())
            pair["token1"] = InitToken(contractPaires.functions.token1().call())

            pair["reserve0"], pair["reserve1"], _ = contractPaires.functions.getReserves().call()

            if pair["reserve0"] > 0 and pair["reserve1"] > 0 :
                if pair["token0"].address.lower() in knownTokens :
