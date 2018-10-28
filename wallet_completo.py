import subprocess
import time
import requests
import json

from uuid import uuid4
from turtlecoin import Walletd
from threading import Thread


#rpc_host = 'localhost'
#rpc_port = 8070
#rpc_password = '123'



#Walletd commands
# generate wallet: turtle-service -g -w test.wallet -p 123 --daemon-address public.turtlenode.io --daemon-port 11898 --rpc-password 123
# or: >turtle-service -g -w test.wallet -p 123 --daemon-address localhost --daemon-port 11898 --rpc-password 123
# 
# open wallet: >turtle-service -w test.wallet -p 123 --daemon-address localhost --daemon-port 11898 --rpc-password 123
#
#help command: turtle-service --help

class Turtle_Wallet(Thread):
    rpc_host = 'localhost'
    rpc_port = 8070
    rpc_password = str("sabo{}_revolutionary{}".format(uuid4(),uuid4()))
    turtlewalletd = Walletd(rpc_password, rpc_host, rpc_port)
    walletPath = ""
    walletPassword = ""
    walletd_service = None
    walletAddress = None
    AvailableBalance = None
    lockedBalance = None
    walletNetBlock = None
    walletLocalBlock = None
    wFee = None
    walletTx = None
    wpeers = ""
    

    def __init__(self, walletdArgs):
        subprocessArgs = walletdArgs         

        subprocessArgs.append(self.rpc_password) #add rpc password to walletd arguments
        subprocessArgs = " ".join(subprocessArgs)
        self.walletd_service = subprocess.Popen(subprocessArgs) #open wallet service

        super(Turtle_Wallet, self).__init__(args = walletdArgs)

    def run(self, *args):
        #this retrieves the data from wallet service
        #like available balance, locked balance, transaction history
        self.walletAddress = str(self.turtlewalletd.get_addresses()['result']['addresses'][0])
        self.wFee = self.turtlewalletd.get_fee_info()['result']['amount']/100
        while True:
            time.sleep(2)
            try:
                a_b = self.turtlewalletd.get_balance(self.walletAddress)['result']['availableBalance']/100
                l_b = self.turtlewalletd.get_balance(self.walletAddress)['result']['lockedAmount']/100
                self.AvailableBalance =  str(a_b)
                self.lockedBalance = str(l_b)
                status = self.turtlewalletd.get_status()['result']
                self.walletNetBlock = status['knownBlockCount']
                self.walletLocalBlock = status['blockCount']
                self.wpeers = status['peerCount']
                
                self.walletTx = self.turtlewalletd.get_transactions([self.walletAddress], self.walletLocalBlock, '' ,1) #address, blockcount, paymentID, firstblockcount
                self.walletTx = self.walletTx['result']['items']


            except Exception as e:

                print(e)
            

    def sendTransaction(self, address, amount,paymentId, *args):
        #send transaction is working, but more things to be added, see to-do-list.txt
          
        #needs to be like this to work
        #when sending a transaction, the node fee is included in the 'amount' instead of 'fee', 'fee' is for network fee I guess
        #the query should be displayed as amount: node fee: fee: whereas fee = fee, amount = amount - node fee - fee, node fee is just node fee
        '''
        transfer = [{'address':str(address),'amount':amount}]
        
        if paymentId == '':
            self.turtlewalletd.send_transaction(transfer, 3, 10, [], '')
        else:
            self.turtlewalletd.send_transaction(transfer, 3, 10, [], paymentId)
        
        if paymentId == '':
            print(paymentId)
            self.turtlewalletd.send_transaction([{"address": address,"amount":amount}],3, 10, [], '')
        else:
            self.turtlewalletd.send_transaction([{"address": address,"amount":amount}],3, 10, [], paymentId)
            
        '''
        #make sure the send amount is in int not float, else it will get an error
                #this works
                    
        sendTx = requests.post('http://localhost:8070/json_rpc',
                                data = json.dumps({
                                                'jsonrpc': '2.0',
                                                'method': 'sendTransaction',
                                                'password': self.rpc_password,
                                                'id': 0,
                                                'params': {'transfers':[{"address": address,
                                                            "amount":int(amount)}],
                                                            'fee':10,
                                                            'anonymity':3,
                                                            'paymentId':''}
                                                            }),
                                headers = {'content-type': 'application/json'}).json()
        print(sendTx) #sendTx stores the transaction hash
                
       

    def Kill_SubProcessWalletd(self, *args):
        #this function is supposed to kill the walletd thread
        self.turtlewalletd.terminate()
        self.turtlewalletd.kill()


    
