import json
from lib2to3.pgen2 import token
from tokenize import Token
from eth_utils import to_checksum_address
from web3 import Web3
import telebot
import requests
from unicodedata import name

avalanche_url = "https://api.avax.network/ext/bc/C/rpc"
web3 = Web3(Web3.HTTPProvider(avalanche_url))

with open ("ABIfactory.json") as f:
    abi = json.load(f)
with open ("ABIpaire.json") as f:
    abiPaires = json.load(f)
with open ("ABItoken.json") as f:
    abiToken = json.load(f)

addresse = "0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10"
contract1 = web3.eth.contract(abi=abi, address=addresse)

previousPaires = 0
while True:
    newPaires = contract1.functions.allPairsLength().call()
    if newPaires > previousPaires:
        previousPaires = newPaires
        print ("New Pair : {}".format(newPaires))
        AddressPaires = contract1.functions.allPairs(newPaires -1).call()
        

        knownTokens = [
        "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7", #WAVAX
        "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e", #USDC
        "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664", #USDC.E
        "0xc7198437980c041c805a1edcba50c1ce5db95118", #USDT.E
        "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7", #USDT
        "0xd586e7f844cea2f87f50152665bcbc2c279d8d70", #DAI.E
        "0x130966628846bfd36ff31a822705796e8cb8c18d", #MIM
        "0xb599c3590f42f8f995ecfa0f85d2980b76862fc1"  #UST
        ]

        def initToken(tokenAddress):
            tokenSC = web3.eth.contract(abi=abiToken, address=web3.toChecksumAddress(tokenAddress))
            token = Token(
                tokenSC.functions.name().call(),
                tokenSC.functions.symbol().call(),
                tokenSC.functions.decimals().call(),
                web3.toChecksumAddress(tokenAddress),
                tokenSC.functions.totalSupply().call()
                )
            return token
        
        class Token():
            def __init__(self, name, symbol, decimals, address, totalSupply):
                self.name = name
                self.symbol = symbol
                self.decimals = decimals
                self.address = address
                self.totalSupply = totalSupply
            def __str__(self):
                return "{}".format(self.symbol)
    

        def whenNewPair(pairAddress):
            pair = {
                "token0":"",
                "token1":"",
                "NewTokenMCap":"",
            }
            pairSC = web3.eth.contract(abi=abiPaires,address=web3.toChecksumAddress(pairAddress))

            #regarder les tokens
            pair["token0"] = initToken(pairSC.functions.token0().call())
            pair["token1"] = initToken(pairSC.functions.token1().call())

            #on prend les reserves de la pool
            pair["reserve0"], pair["reserve1"], _ = pairSC.functions.getReserves().call()

            #si la pool a été initialisée
            if pair["reserve0"] > 0 and pair["reserve1"] > 0 :
                #on détermine si on veut le token 0 ou le token 1
                if pair["token0"].lower() in knownTokens :
                    #on regarde le prix du token en avax
                    url = requests.get("https://api.dexscreener.io/latest/dex/tokens/0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
                    response = url.json()
                    print(response.pairs[0].priceUsd)