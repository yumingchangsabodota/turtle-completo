import subprocess
import time

from turtlecoin import TurtleCoind
from threading import Thread


class Turtle_Explorer(Thread):
    
    #explorer parameters
    local_host = 'localhost'
    local_port = 11898
    turtlecoind = TurtleCoind(local_host, local_port)
    heightInfo = None
    netHeight = None
    txPool = None
    blocks = None
    peers = None

    Daemon = None
    
    def __init__(self):
        #remove --rpc-bind-ip=0.0.0.0 if you don't want to be connected
        trtlDaemon = "turtleservices\\TurtleCoind.exe --enable_blockexplorer --rpc-bind-ip=0.0.0.0 --rpc-bind-port=11898 --fee-amount 100 --fee-address TRTLv1nQeHwinWcyxrPQSN3gdqxgKZqawZVJzQJ59Kwq45QvU9vafwG1bff2BecELJ3qaS16TeWEPW6UvxzxRd4u6D9wzUU5ERE"  
        #trtlDaemon = "turtleservices\\TurtleCoind.exe --enable_blockexplorer --rpc-bind-ip=0.0.0.0 --rpc-bind-port=11898"  
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE #hide daemon console
        self.Daemon = subprocess.Popen(trtlDaemon, startupinfo = startupinfo)
        #self.Daemon = subprocess.Popen(trtlDaemon)
        super(Turtle_Explorer, self).__init__()

    def run(self, *args):
        while True:
            time.sleep(5)
            try:
                self.heightInfo = self.turtlecoind.get_height()['height']
                self.netHeight = self.turtlecoind.get_height()['network_height']
                self.peers =len(self.turtlecoind.get_peers()['peers'])
                if self.heightInfo != self.netHeight:
                    self.txPool = None
                    self.blocks = None
                else:
                    self.txPool = self.turtlecoind.get_transaction_pool()['result']['transactions']
                    recentBlocks1 = self.turtlecoind.get_blocks(self.heightInfo-1)
                    recentBlocks2 = self.turtlecoind.get_blocks(self.heightInfo-31)
                    self.blocks = recentBlocks1['result']['blocks']+recentBlocks2['result']['blocks']
            except Exception as e:
                print(e)

    def searchTx(self, txHash, *args):
        txResult = {}
        if txHash == "":
            txResult['error'] = "yes"
            txResult['msg'] = "ERROR: Please Enter a valid Tx Hash."
            return  txResult

        else:
            try:
                Result = self.turtlecoind.get_transaction(txHash)
                current_height = self.turtlecoind.get_height()['height']
                txResult['error'] = "no"
                txResult['result'] = Result
                txResult['current_height'] = current_height
                return  txResult

            except:
                txResult['error'] = "yes"
                txResult['msg'] = "ERROR: No Such Tx was found, or it's not been added to the chain yet."
                return  txResult

    def searchBlk(self, blkHash, *args):
        blkResult = {}
        if blkHash == "":
            blkResult['error'] = "yes"
            blkResult['msg'] = "ERROR: Please Enter a valid Block Hash."
            return blkResult
        else:
            try:
                Result = self.turtlecoind.get_block(blkHash)
                blkResult['error'] = "no"
                blkResult['result'] = Result
                return blkResult

            except:
                blkResult['error'] = "yes"
                blkResult['msg'] = "ERROR: No Such Block was found, please check your block hash."
                return blkResult

    def Kill_SubProcessTRTLDaemon(self, *args):
        self.Daemon.terminate()
        self.Daemon.kill()
