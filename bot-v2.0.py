import json
from lib2to3.pgen2 import token
from eth_utils import to_checksum_address
from web3 import Web3
import telebot
import requests
from unicodedata import name
import time

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

#configurer et créer le bot --> avec son token 
bot = telebot.TeleBot('5134546712:AAENre6G1HRSBHFwLIqPuJtj0GuoH5MBqDU')
bot.config['api_key'] = "5134546712:AAENre6G1HRSBHFwLIqPuJtj0GuoH5MBqDU"

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
                self.symbol = symbol.replace(" ","")
                self.decimals = decimals
                self.address = address
                self.totalSupply = totalSupply
            def __str__(self):
                return "{}".format(self.symbol)

        def whenNewPair(pairAddress):
            pair = {
                "token0":"",
                "token1":"",
                "reserve0":"",
                "reserve1":"",
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
                url = requests.get("https://api.dexscreener.io/latest/dex/tokens/{}".format(pair["token1"].address))
                response = url.json()
                pair["NewTokenMCap"] = "Pas de liquidité pour déterminer le Mcap"
                resultPriceToken = "Indisponible"
                resultLiquidityToken = "Pas de liquidité"
                resultLiquidityAvax = "Pas de liquidité"
                resultLiquidityUsd = "N/a"
                #on détermine si on veut le token 0 ou le token 1
                if pair["token0"].address.lower() in knownTokens :
                    #on regarde le prix du token en avax
                    url = requests.get("https://api.dexscreener.io/latest/dex/tokens/{}".format(pair["token1"].address))
                    response = url.json()
                    if len(response["pairs"]) > 0 :
                        time.sleep(5)
                        resultPriceToken = response["pairs"][0]["priceUsd"]
                        resultLiquidityToken = response["pairs"][0]["liquidity"]["quote"]
                        resultLiquidityAvax = response["pairs"][0]["liquidity"]["base"]
                        resultLiquidityUsd = response["pairs"][0]["liquidity"]["usd"]
                    else:
                        resultPriceToken = "Aucune informations disponibles"
                        resultLiquidityToken = "Aucune informations disponibles"
                        resultLiquidityAvax = "Aucune informations disponibles"
                        resultLiquidityUsd = "Aucune informations disponibles" 
         
                elif pair["token1"].address.lower() in knownTokens :
                    
                        url = requests.get("https://api.dexscreener.io/latest/dex/tokens/{}".format(pair["token0"].address))
                        response = url.json()
                        if len(response["pairs"]) > 0 :  
                            time.sleep(5)      
                            resultPriceToken = response["pairs"][0]["priceUsd"] 
                            resultLiquidityToken = response["pairs"][0]["liquidity"]["quote"]
                            resultLiquidityAvax = response["pairs"][0]["liquidity"]["base"]
                            resultLiquidityUsd = response["pairs"][0]["liquidity"]["usd"]
                        else:
                            resultPriceToken = "Aucune informations disponibles"
                            resultLiquidityToken = "Aucune informations disponibles"
                            resultLiquidityAvax = "Aucune informations disponibles"
                            resultLiquidityUsd = "Aucune informations disponibles"
                        
                else :
                    pair["NewTokenMCap"] = "Pas de token connus pour déterminer le Mcap"
            else :
                pair["NewTokenMCap"] = "Pas de liquidité pour déterminer le Mcap"
                resultPriceToken = "Indisponible"
                resultLiquidityToken = "N/a"
                resultLiquidityAvax = "N/a"
                resultLiquidityUsd = "N/a"

            return "New pair : {}/{} \nTo buy: https://traderjoexyz.com/trade?outputCurrency={}&inputCurrency={} \n({}/{}) \n \n💰 Prix: {}$ \n🚜 Liquidité Token: {} \n🔺 Liquidité Avax ou Stables: {} \n💸 Liquidité totale: {}$" .format(
                pair["token0"].symbol,
                pair["token1"].symbol,
                pair["token0"].address,
                pair["token1"].address,
                pair["token0"].name,
                pair["token1"].name,
                resultPriceToken,
                resultLiquidityAvax,
                resultLiquidityToken,
                resultLiquidityUsd,
            )

        print(whenNewPair(AddressPaires))
        message = bot.send_message("-1001660580072", whenNewPair(AddressPaires))


        #Fonction Liquidity
        def liquidity(pairAddress):
            pairSC = web3.eth.contract(abi=abiPaires,address=web3.toChecksumAddress(pairAddress))
            pair = {
                "token0":"",
                "token1":"",
                "reserve0":"",
                "reserve1":"",
            }
            pair["token0"] = initToken(pairSC.functions.token0().call())
            pair["token1"] = initToken(pairSC.functions.token1().call())
            pair["reserve0"], pair["reserve1"], _ = pairSC.functions.getReserves().call()

            if pair["token0"].address.lower() in knownTokens :
                pair["token1"].totalSupply
                pair["token1"].decimals
                pair["reserve1"]
                return "Total supply token : {} \nReserve token : {}" .format(
                    pair["token1"].totalSupply / 10 ** pair["token1"].decimals,
                    pair["reserve1"] / 10 ** pair["token1"].decimals,
                )
                                           
            elif pair["token1"].address.lower() in knownTokens :
                pair["token0"].totalSupply
                pair["token0"].decimals
                pair["reserve0"]
                return "\n Total supply token : {} \n Reserve token : {}" .format(
                    pair["token0"].totalSupply / 10 ** pair["token0"].decimals,
                    pair["reserve0"] / 10 ** pair["token0"].decimals,
                )
            else : 
                print("osef ") 
        print(liquidity(AddressPaires))


       
        #Fonction Token
        def token(pairAddress):
            pairSC = web3.eth.contract(abi=abiPaires,address=web3.toChecksumAddress(pairAddress))
            pair = {
                "token0":"",
                "token1":"",
            }
            pair["token0"] = initToken(pairSC.functions.token0().call())
            pair["token1"] = initToken(pairSC.functions.token1().call())

            if pair["token0"].address.lower() in knownTokens:
                print(pair["token1"].address)
            elif pair["token1"].address.lower() in knownTokens:
                print(pair["token0"].address)

        token(AddressPaires)


        pairSC = web3.eth.contract(abi=abiPaires,address=web3.toChecksumAddress(AddressPaires))
        symbol = {
            "BTC":"",
            "AVAX":"",
            "ETH":"",
            "SPORE":""
        }
        