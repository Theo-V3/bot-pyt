import json
from unicodedata import name
from web3 import Web3
import telebot
import requests


avalanche_url = "https://api.avax.network/ext/bc/C/rpc"
web3 = Web3(Web3.HTTPProvider(avalanche_url))

with open ('ABIfactory.json') as f:
    abi = json.load(f)
with open ('ABIpaire.json') as g:
    abi2 = json.load(g)

addresse = "0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10"
contract = web3.eth.contract(address=addresse, abi=abi)

#configurer et créer le bot --> avec son token 
bot = telebot.TeleBot('5134546712:AAENre6G1HRSBHFwLIqPuJtj0GuoH5MBqDU')
bot.config['api_key'] = "5134546712:AAENre6G1HRSBHFwLIqPuJtj0GuoH5MBqDU"


previous_paires = 0
while True:
    paires = contract.functions.allPairsLength().call()
    if previous_paires < paires:
        previous_paires = paires 
        print("New pair: ", paires)

        #print l'addresse de la dernière paire créée
        address_paires = contract.functions.allPairs(paires -1).call()
        print(address_paires)

        contract2 = web3.eth.contract(address=address_paires, abi=abi2)

        token_0 = contract2.functions.token0().call()
        token_1 = contract2.functions.token1().call()
        print(token_0)
        print(token_1)

        with open ('ABItoken.json') as j:
            abi3 = json.load(j)

        #se co au contrat des tokens de la nouvelle paire (les deux addresses mais une seule abi)
        contract3 = web3.eth.contract(address=token_0, abi=abi3)
        contract4 = web3.eth.contract(address=token_1, abi=abi3)

        #Total supply des nouveaux tokens de la paire
        totalSupply = contract3.functions.totalSupply().call()
        totalSupply2 = contract4.functions.totalSupply().call()
        

        #print le ticker et le nom complet des tokens de la nouvelle paire
        print(contract3.functions.symbol().call())
        print(contract3.functions.name().call())
        print(contract4.functions.symbol().call())
        print(contract4.functions.name().call())

        
        
        #se co à l'api de coinpaprica pour request des infos sur prix/mc/totalsupply
        response = requests.get("https://api.coinpaprika.com/v1/ticker/avax-avalanche") 
        result = response.json()  
        print(result["price_usd"])    
        resultat = float(result["price_usd"])
        
        #Send message on telegram
        message = "New pair : {}/{} \nTo buy: https://traderjoexyz.com/trade?outputCurrency={}&inputCurrency={} \n({}/{})" .format(contract3.functions.symbol().call(), contract4.functions.symbol().call(), token_0, token_1, contract3.functions.name().call(), contract4.functions.name().call(), resultat)
        message2 = "\nMarket cap : {:,}$".format(resultat)
        
        test = bot.send_message("-1001660580072", message + message2)
        

        #avoir la liquidité des deux tokens déposés dans la nouvelle pool
        reserve_token_1, reserve_token_2, _ = contract2.functions.getReserves().call()
        

        #decimales des tokens de la paire:
        #interroger le token sur son nombre de decimales pour ne pas avoir d'erreurs au moment de print le total
        #certains tokens ont 6 décimales et d'autres 18        
        decimals_0 = contract3.functions.decimals().call()
        decimals_1 = contract4.functions.decimals().call()
        print(decimals_0)
        print(decimals_1)

        #faire le calcul pour déterminer le nombre de tokens précis dans la pool 
        nb_token1_pool = reserve_token_1/10**decimals_0
        nb_token2_pool = reserve_token_2/10**decimals_1
        print("nombre token1 pool:", nb_token1_pool)
        print("nombre token2 pool:", nb_token2_pool)

        #calculer le ratio des tokens dans la pool pour définir le marketcap:

        #OPTION 1:
        #nombre de token0/nombre d'avax = ratio de token / avax --> multiplication du nombre de token0/avax par le prix de l'avax
        #then multipication par le totalSupply du token0
        option1 = reserve_token_1/reserve_token_2
        print(option1)
        print(resultat)
        print(totalSupply/10**decimals_0)
        calcul_mc_option1 = option1 * resultat * (totalSupply/10**decimals_0) 
        print(calcul_mc_option1)
        



        #OPTION 2:
        #nombre de token0/nombre de stable(usdt/mim/usdc/dai/frax) = ratio de token / nb de stable dans la pool
        #then multiplication par le totalSupply du token0
        option2 = reserve_token_1/reserve_token_2
        calcul_mc_option2 = (1/option2) * (totalSupply/10**decimals_0)
        print(calcul_mc_option2)