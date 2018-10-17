from kivy.config import Config
Config.set('kivy', 'desktop', '1')
Config.set('kivy', 'window_icon','img/turtlecoin_icon_color_16.png')
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '1250')
Config.set('graphics', 'height', '750')
Config.set('graphics', 'minimum_width', '1250')
Config.set('graphics', 'minimum_height', '750')

from kivy.core.window import Window
Window.clearcolor = (64/255,193/255,142/255,1)
#primary green = (0/255,133/255,61/255,1)
import kivy
kivy.require('1.10.1')

import time
import sys
import subprocess
import threading
import queue

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

from kivy.clock import Clock
from datetime import datetime
from turtlecoin import TurtleCoind


####################################---Screens---###########################################
class OnStartScreen(Screen):
    pass
class OnOpenWalletScreen(Screen):
    pass
class WalletScreen(Screen):
    pass
class TransactionScreen(Screen):
    pass
class BlockExplorerWithWalletScreen(Screen):
    pass
class BlockSearchWithWalletScreen(Screen):
    pass
class OnlyBlockExplorerScreen(Screen):
    pass
class OnlyBlockSearchScreen(Screen):
    pass
'''
class SettingScreen(Screen):
    pass
'''
class AboutScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass
##############################################################################################
class AboutPopup(Popup):
    pass

class StatusLabel(RelativeLayout):
    pass

class BigLabel(Label):
    pass
class SmallLabel(Label):
    blockHash = ""
    def setBlkHash (self, blkhash):
        self.blockHash = blkhash
    def goToSearch(self, instance, value):
        myApp.search_on_click("blk", self.blockHash)
    

class BlkSearchData(RelativeLayout):
    item1 = StringProperty()
    item2 = StringProperty()
    blkResultItem1 = ObjectProperty(None)
    blkResultItem2 = ObjectProperty(None)
    myHeight = ""
    def setText(self,item1text, item2text):
        self.item1 = item1text
        self.item2 = item2text
        self.blkResultItem1.text = self.item1
        self.blkResultItem2.text = self.item2
        self.blkResultItem1.bind(on_ref_press = self.goToSearch)
       
    def setMyHeight(self, blkHeight):
        self.myHeight = str(blkHeight)
        
    def goToSearch(self, instance, value):
        if value == '<':
            myApp.search_on_click("blk", str(int(self.myHeight)+1))#give clickability to arrows
        elif value == '>':
            self.myHeight = int(self.myHeight) -1 
            if self.myHeight < 0:
                self.myHeight = 0
            myApp.search_on_click("blk", str(self.myHeight))


class BlkSearchTx(RelativeLayout):
    hashText = StringProperty()
    feeText = StringProperty()
    totalAmountText = StringProperty()
    sizeText = StringProperty()
    forSearchHash = ""
    tx_hash = ObjectProperty(None)
    tx_fee = ObjectProperty(None)
    tx_totalAmount = ObjectProperty(None)
    tx_Size = ObjectProperty(None)
    def setText(self, hashtext, fee, totalamount, size, forsearchHash):
        self.hashText = hashtext
        self.feeText = fee
        self.totalAmountText = totalamount
        self.sizeText = size
        self.tx_hash.text = self.hashText
        self.tx_hash.markup = True
        self.tx_hash.bind(on_ref_press = self.goToSearch)
        self.tx_fee.text = self.feeText 
        self.tx_totalAmount.text = self.totalAmountText
        self.tx_Size.text = self.sizeText
        self.forSearchHash = forsearchHash
    def goToSearch(self, instance, value):
        myApp.search_on_click("tx", self.forSearchHash)
        
class TXInputs(RelativeLayout):
    In_amount = StringProperty()
    In_image = StringProperty()
    input_amount = ObjectProperty(None)
    input_image = ObjectProperty(None)

    def setText(self, amount, image):
        self.In_amount = amount
        self.In_image = image
        self.input_amount.text = self.In_amount
        self.input_image.text = self.In_image
    
class TXOutputs(RelativeLayout):
    Out_amount = StringProperty()
    Out_key = StringProperty()
    output_amount = ObjectProperty(None)
    output_key = ObjectProperty(None)
    def setText(self, amount, key):
        self.Out_amount = amount
        self.Out_key = key
        self.output_amount.text = self.Out_amount
        self.output_key.text = self.Out_key

class TxPoolData(RelativeLayout):
    itemText_amount = StringProperty()
    itemText_fee = StringProperty()
    itemText_size = StringProperty()
    itemText_hash = StringProperty()
    txp_amount = ObjectProperty(None)
    txp_fee = ObjectProperty(None)
    txp_size = ObjectProperty(None)
    txp_hash = ObjectProperty(None)

    def setText(self, amount, fee, size, hashhash):
        self.itemText_amount = amount
        self.itemText_fee = fee
        self.itemText_size = size
        self.itemText_hash = hashhash
        self.txp_amount.text = self.itemText_amount
        self.txp_fee.text = self.itemText_fee
        self.txp_size.text = self.itemText_size
        self.txp_hash.text = '[color=556b2f][ref='+self.itemText_hash+']'+self.itemText_hash+'[/ref][/color]'
        self.txp_hash.markup = True
        self.txp_hash.bind(on_ref_press = self.goToSearch)
    def goToSearch(self, instance, value):
        myApp.root.transition.direction = 'left'
        myApp.root.current = 'onlyblocksearchscreen'
        myApp.search_on_click("tx", self.itemText_hash)
        
class RecentBlockData(RelativeLayout):
    itemText_height = StringProperty()
    itemText_size = StringProperty()
    itemText_hash = StringProperty()
    itemText_difficulty = StringProperty()
    itemText_tx = StringProperty()
    itemText_datetime = StringProperty()
    rctblk_height = ObjectProperty(None)
    rctblk_size = ObjectProperty(None)
    rctblk_hash = ObjectProperty(None)
    rctblk_difficulty = ObjectProperty(None)
    rctblk_tx = ObjectProperty(None)
    rctblk_datetime = ObjectProperty(None)

    def setText(self, height, size, hashhash, difficulty, tx, datetime):
        self.itemText_height = height
        self.itemText_size = size
        self.itemText_hash = hashhash
        self.itemText_difficulty = difficulty
        self.itemText_tx = tx
        self.itemText_datetime = datetime
        
        self.rctblk_height.text = '[color=556b2f][ref='+self.itemText_height+']'+self.itemText_height+'[/ref][/color]'
        self.rctblk_height.markup = True
        self.rctblk_height.bind(on_ref_press = self.goToSearch_byHeight)
        
        self.rctblk_size.text = self.itemText_size 
        self.rctblk_hash.text = '[color=556b2f][ref='+self.itemText_hash+']'+self.itemText_hash+'[/ref][/color]'
        self.rctblk_hash.markup = True
        
        self.rctblk_hash.bind(on_ref_press = self.goToSearch_byHash)
        self.rctblk_difficulty.text = self.itemText_difficulty
        self.rctblk_tx.text = self.itemText_tx
        self.rctblk_datetime.text = self.itemText_datetime
        
    def goToSearch_byHash(self, instance, value):
        myApp.root.transition.direction = 'left'
        myApp.root.current = 'onlyblocksearchscreen'
        myApp.search_on_click("blk", self.itemText_hash)
            
    def goToSearch_byHeight(self, instance, value):
        myApp.root.transition.direction = 'left'
        myApp.root.current = 'onlyblocksearchscreen'
        height = self.itemText_height.replace(",","")
        myApp.search_on_click("blk", height)


##########################################################################################      


def retrieve_daemonInfo(*args):
    local_host = 'localhost'
    local_port = 11898
    turtlecoind = TurtleCoind(local_host, local_port)
    global threadRunning
    threadRunning = args
    while threadRunning:
        time.sleep(5)
        try:
            heightInfo = turtlecoind.get_height()['height']
            netHeight = turtlecoind.get_height()['network_height']
            if heightInfo >= netHeight:
                txPool = turtlecoind.get_transaction_pool()['result']['transactions']
                recentBlocks1 = turtlecoind.get_blocks(heightInfo-1)
                recentBlocks2 = turtlecoind.get_blocks(heightInfo-31)
                blocks = recentBlocks1['result']['blocks']+recentBlocks2['result']['blocks']
                daemon_q.put((heightInfo,netHeight,txPool,blocks))
            else:
                daemon_q.put((heightInfo,netHeight, [], []))
        except Exception as e:
            daemon_q.put((heightInfo,netHeight, [], []))
def killDaemon():
    global threadRunning
    threadRunning = False


def searchTx(txHash):
    local_host = 'localhost'
    local_port = 11898
    turtlecoind = TurtleCoind(local_host, local_port)
    txResult = {}
    if txHash == "":
        txResult['error'] = "yes"
        txResult['msg'] = "ERROR: Please Enter a valid Tx Hash."
        tx_search_q.put(txResult)
    else:
        try:
            Result = turtlecoind.get_transaction(txHash)
            current_height = turtlecoind.get_height()['height']
            txResult['error'] = "no"
            txResult['result'] = Result
            txResult['current_height'] = current_height
            tx_search_q.put(txResult)
        except:
            txResult['error'] = "yes"
            txResult['msg'] = "ERROR: No Such Tx was found, or it's not been added to the chain yet."
            tx_search_q.put(txResult)

def searchBlk(blkHash):
    local_host = 'localhost'
    local_port = 11898
    turtlecoind = TurtleCoind(local_host, local_port)
    blkResult = {}
    if blkHash == "":
        blkResult['error'] = "yes"
        blkResult['msg'] = "ERROR: Please Enter a valid Block Hash."
        blk_search_q.put(blkResult)
    else:
        try:
            Result = turtlecoind.get_block(blkHash)
            blkResult['error'] = "no"
            blkResult['result'] = Result
            blk_search_q.put(blkResult)
        except:
            blkResult['error'] = "yes"
            blkResult['msg'] = "ERROR: No Such Block was found, please check your block hash."
            blk_search_q.put(blkResult)


daemon_q = queue.Queue(maxsize = 1)
tx_search_q = queue.Queue(maxsize = 1)
blk_search_q = queue.Queue(maxsize = 1)
searchAvailable1 = Label(pos_hint = {"x":0.1, "y":0.5}, size_hint = (0.5,None),
                         color = (0,0,0,1))
searchAvailable1.text = "Search will be available when the daemon is synched."
searchAvailable2 = Label(pos_hint = {"x":0.1, "y":0.5}, size_hint = (0.5,None),
                         color = (0,0,0,1))
searchAvailable2.text = "Search will be available when the daemon is synched."

####################################################################################################################
class Turtle_Completo(App):
#-------------explorer parameters-------------------------------------------------------------------------------
    local_host = 'localhost'
    local_port = 11898
    turtlecoind = TurtleCoind(local_host, local_port)
    trtlDaemon = "turtleservices\\TurtleCoind.exe --enable_blockexplorer --rpc-bind-ip=0.0.0.0 --rpc-bind-port=11898"  #remove --rpc-bind-ip=0.0.0.0 if you don't want to be connected
#----------------------------------------------------------------------------------------------------------------
    appIsRunning = False
    status_text = StringProperty()
    daemon = None
    #acessing and add widgets inside a screen syntax:
    #appname(or slef).root.screenname.ids.actualyid.add_widget()
    
    #daemon info thread 
    trtl_chain_stat_thread = threading.Thread(target = retrieve_daemonInfo, args = (appIsRunning,))
    
    
    def on_start(self):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    def on_stop(self):
        if self.appIsRunning:
            Clock.unschedule(self.update_SynchStatus)
            Clock.unschedule(self.check_search_queue)
            killDaemon()
            global daemon
            daemon.terminate()
            daemon.kill()
            self.appIsRunning = False
        self.appIsRunning = False #This kills the daemon info retrieving loop

    def build(self):
        global myApp
        self.title = "Turtle Completo v0.1.0"
        self.status_text ="LOCAL:     \nNETWORK: "
###################################################################################################################
#get info from Queue update daemon sych status
    def update_SynchStatus(self, dt):
        if daemon_q.empty():
            pass
        else:
            try:
                Local, Network, TxPool, RecentBlk = daemon_q.get()
                if Local >= Network:
                    self.status_text = "LOCAL:       "+str(Local)+"\nNETWORK: "+str(Network)
                    self.update_Txpool(TxPool)
                    self.update_RecentBlocks(RecentBlk)
                    self.root.onlyblocksearchscreen.ids.searchtxbutton.disabled = False
                    self.root.onlyblocksearchscreen.ids.searchblkbutton.disabled = False
                else:
                    self.status_text = "SYNC...\n\nLOCAL:       "+str(Local)+"\nNETWORK: "+str(Network)
                    self.root.onlyblocksearchscreen.ids.searchtxbutton.disabled = True
                    self.root.onlyblocksearchscreen.ids.searchblkbutton.disabled = True
                    self.root.onlyblocksearchscreen.ids.txsearch_display.add_widget(searchAvailable1)
                    self.root.onlyblocksearchscreen.ids.blksearch_display.add_widget(searchAvailable2)
            except Exception as e:
                print("something wrong while updating status and txpool and blks")
                print(e)
        
#update recent blocks and txpool to gridview in a scroll view
    def update_Txpool(self, txpoolInfo):
        self.root.onlyblockexplorerscreen.ids.txp_datalistTemplate.clear_widgets()
        try:
            if txpoolInfo!=[]:
                for i in range(len(txpoolInfo)):
                    TxPoolData1 = TxPoolData()
                    if i%2!=1:
                        pass
                    else:
                        TxPoolData1.colors = (1,1,1,0.1)
                    amount = "{:,}".format(txpoolInfo[i]['amount_out']/100)
                    fee = "{:,}".format(txpoolInfo[i]['fee']/100)
                    size = "{:,}".format(txpoolInfo[i]['size'])
                    txhash = str(txpoolInfo[i]['hash'])
                    TxPoolData1.setText(amount,fee,size,txhash)
                    self.root.onlyblockexplorerscreen.ids.txp_datalistTemplate.add_widget(TxPoolData1)
            else:
                pass
        except Exception as e:
            print("something wrong in Txpool")
            print(e)

    def update_RecentBlocks(self, blocks):
        self.root.onlyblockexplorerscreen.ids.rctblk_datalistTemplate.clear_widgets()
        try:
            for i in range(len(blocks)):
                RecentBlockData1 = RecentBlockData()
                if i%2!=1:
                    pass
                else:
                    RecentBlockData1.colors = (1,1,1,0.1)
                height = "{:,}".format(blocks[i]['height'])
                size = "{:,}".format(blocks[i]['cumul_size'])
                blockhash = str(blocks[i]['hash'])
                difficulty = "{:,}".format(blocks[i]['difficulty'])
                txs = "{:,}".format(blocks[i]['tx_count'])
                dateTime = datetime.fromtimestamp(blocks[i]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                RecentBlockData1.setText(height,size,blockhash,difficulty,txs,dateTime,)
                self.root.onlyblockexplorerscreen.ids.rctblk_datalistTemplate.add_widget(RecentBlockData1)
        except Exception as e:
            print("something wrong in recentblks")
            print(e)
#-------------------------------------------------------------------------------------
    def update_TxSearchResult(self):
        self.root.onlyblocksearchscreen.ids.txsearch_display.clear_widgets()
        Result = tx_search_q.get()
        if Result["error"] == "yes":
            ErrorLabel = BigLabel(text = Result['msg'])
            self.root.onlyblocksearchscreen.ids.txsearch_display.add_widget(ErrorLabel)  
        elif Result["error"] == "no":
            current_h = Result['current_height']
            MyResult = Result['result']
            if current_h - MyResult['result']['block']['height'] <= 0:
                confirmation = 0
            else:
                confirmation = "{:,}".format(current_h - MyResult['result']['block']['height'])
            Firstconfirmation = datetime.fromtimestamp(MyResult['result']['block']['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            fee = "{:,}".format(MyResult['result']['txDetails']['fee']/100)
            sumOfOutputs = sum(amount['amount'] for amount in MyResult['result']['tx']['vout'])
            sumOfOutputs = "{:,}".format(sumOfOutputs/100)
            size = "{:,}".format(MyResult['result']['txDetails']['size'])
            mixin = "{:,}".format(MyResult['result']['txDetails']['mixin'])
            txHash = MyResult['result']['txDetails']['hash']
            blkHash = MyResult['result']['block']['hash']
            height = "{:,}".format(MyResult['result']['block']['height'])
            
            #text="[b]Transaction[/b]", size_hint= (1, None), height = 50,
            #              font_size = 25, color = (0,0,0,1),markup = True)
            TxLabel = BigLabel(text = "[b]TRANSACTION[/b]")
            txHashLabel = SmallLabel(text = "Hash: "+txHash)
            ConfirmLabel = SmallLabel(text = "Confirmations: " + confirmation +", First confirmation time: "+Firstconfirmation)
            feeLabel = SmallLabel(text = "Fee: " + fee + " TRTL")
            sumOutLabel = SmallLabel(text = "Sum of outputs: " + sumOfOutputs+ " TRTL")
            sizeLabel = SmallLabel(text = "Size: "+ size)
            mixinLabel = SmallLabel(text = "Mixin: "+ mixin)
            
            InBlockLabel = BigLabel(text = "[b]IN BLOCK[/b]" )
             #'[color=556b2f][ref='+self.hashText+']'+self.hashText+'[/ref][/color]'
            blkHashLabel = SmallLabel(text = "Hash: "+'[color=556b2f][ref='+blkHash+']'+blkHash+'[/ref][/color]')  #add click to hash search
            blkHashLabel.markup = True
            blkHashLabel.setBlkHash(blkHash)
            blkHashLabel.bind(on_ref_press = blkHashLabel.goToSearch)
            
            blkheighLabel = SmallLabel(text = "Height: " + height)
            timeLabel = SmallLabel(text = "Timestamp: " + Firstconfirmation)
            
            
            inputHeader = TXInputs()
            inputHeader.setText("Amount", "Image")
            inputHeader.colors = (0.5, 0.5, 0.5, 0.8)
            inputList = []
            if MyResult['result']['tx']['vin'][0]['type'] == 'ff': #check tx input counts
                inputCount = str(0)
            else:
                inputCount = "{:,}".format(len(MyResult['result']['tx']['vin']))
                for i in range(len(MyResult['result']['tx']['vin'])):
                    txinput = TXInputs()
                    if i%2!=1:
                        pass
                    else:
                        txinput.colors = (1,1,1,0.1)
                    inAmount = "{:,}".format(MyResult['result']['tx']['vin'][i]['value']['amount']/100)
                    txinput.setText(inAmount+" TRTL",
                                    str(MyResult['result']['tx']['vin'][i]['value']['k_image']))
                    inputList.append(txinput)
            InputLabel = BigLabel(text = "[b]INPUTS ("+inputCount+")[/b]" )
            paddingLabel1 = SmallLabel()
            paddingLabel2 = SmallLabel()
            LabelList = [TxLabel,txHashLabel,ConfirmLabel,feeLabel,sumOutLabel,
                        sizeLabel,mixinLabel, paddingLabel1,InBlockLabel, blkHashLabel,
                        blkheighLabel,timeLabel, paddingLabel2,InputLabel,inputHeader]
            LabelList = LabelList + inputList
               
            outputCount = "{:,}".format(len(MyResult['result']['tx']['vout']))
            OutputLabel = BigLabel(text = "[b]OUTPUTS ("+outputCount+")[/b]" )
            outputHeader = TXOutputs()
            outputHeader.setText("Amount", "Key")
            outputHeader.colors = (0.5, 0.5, 0.5, 0.8)
            
            outputList = [OutputLabel,outputHeader]
            for i in range(len(MyResult['result']['tx']['vout'])):
                txoutput = TXOutputs()
                if i%2!=1:
                    pass
                else:
                    txoutput.colors = (1,1,1,0.1)
                outAmount = "{:,}".format(MyResult['result']['tx']['vout'][i]['amount']/100)
                txoutput.setText(outAmount+" TRTL",
                                str(MyResult['result']['tx']['vout'][i]['target']['data']['key']))
                outputList.append(txoutput)
                    
            LabelList += outputList
            paddingLabel3 = BigLabel()
            LabelList.append(paddingLabel3)
            
            for lb in LabelList:
                self.root.onlyblocksearchscreen.ids.txsearch_display.add_widget(lb)
            LabelList = []
            
            
    def update_BlkSearchResult(self):
        self.root.onlyblocksearchscreen.ids.blksearch_display.clear_widgets()
        Result = blk_search_q.get()
        if Result["error"] == "yes":
            ErrorLabel = BigLabel(text = Result['msg'])
            self.root.onlyblocksearchscreen.ids.blksearch_display.add_widget(ErrorLabel)  
        elif Result["error"] == "no":
            Result = Result['result']['result']
            BlockTitleLabel = BigLabel(text = "[b]BLOCK[/b]", size_hint = (0.1,1), pos_hint={"x":0, "y":0},valign = 'bottom')
            blockHashLabel = SmallLabel(text = "[b]"+Result['block']['hash']+"[/b]",size_hint = (0.9,1), pos_hint={"x":0.08, "y":0},
                                        valign ='bottom', font_size = 16, color = (47/255,79/255,79/255,1))
            blkTitleandHashLabel = RelativeLayout(size_hint = (1,None), height = 30)
            blkTitleandHashLabel.add_widget(BlockTitleLabel)
            blkTitleandHashLabel.add_widget(blockHashLabel)
            paddingLabel1 = SmallLabel(height = 10)

            #1
            #'[color=556b2f][ref='+self.hashText+']'+self.hashText+'[/ref][/color]'
            heighAndTotalTxSizelabel = BlkSearchData()
            heighAndTotalTxSizelabel.setText("Height: {} {:,} {}".format("[b][size=20][color=556b2f][ref=<]<[/ref][/color][/size][/b]",Result['block']['height'],"[b][size=20][color=556b2f][ref=>]>[/ref][/color][/size][/b]"),
                                             "Total transaction size, bytes: {:,}".format(Result['block']['transactionsCumulativeSize']))
            heighAndTotalTxSizelabel.setMyHeight(Result['block']['height'])
            
            #2
            timeAndTotalblkSizelabel = BlkSearchData()
            if Result['block']['timestamp'] != 0:  #check if it is genesis block
                timeAndTotalblkSizelabel.setText("Timestamp: "+datetime.fromtimestamp(Result['block']['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                                            "Total block size, bytes: {:,}".format(Result['block']['blockSize']))
            else:
                timeAndTotalblkSizelabel.setText("Timestamp: ",
                                            "Total block size, bytes: {:,}".format(Result['block']['blockSize']))
            #3
            versionAndCurrentTxMedianLabel = BlkSearchData()
            versionAndCurrentTxMedianLabel.setText("Version: {}.{}".format(Result['block']['major_version'],Result['block']['minor_version']),
                                                    "Current txs median, bytes: {:,}".format(Result['block']['sizeMedian']))
            #4
            difficultyAndEffectiveTxMedianLabel = BlkSearchData()
            difficultyAndEffectiveTxMedianLabel.setText("Difficulty: {:,}".format(Result['block']['difficulty']),
                                                        "Effective txs median, bytes: {:,}".format(Result['block']['effectiveSizeMedian']))
            #5
            orphanAndRewardPenaltylabel = BlkSearchData()
            orphan = "No" if Result['block']['orphan_status'] == False else "Yes"
            orphanAndRewardPenaltylabel.setText("Orphan: {}".format(orphan),
                                                "Reward penalty: {:,}%".format(Result['block']['penalty']))
            #6
            txsAndBaserewardLabel = BlkSearchData()
            txsAndBaserewardLabel.setText("Transactions: {:,}".format(len(Result['block']['transactions'])),
                                            "Base reward: {:,} TRTL".format(Result['block']['baseReward']/100))
            #7
            totalCoinNetAndTxFeeLabel = BlkSearchData()
            totalCoinNetAndTxFeeLabel.setText("Total coins in the network: {:,} TRTL".format(int(Result['block']['alreadyGeneratedCoins'])/100),
                                              "Transactions fee: {:,} TRTL".format(Result['block']['totalFeeAmount']/100))
            #8
            totalTxsInNetAndReward = BlkSearchData()
            totalTxsInNetAndReward.setText("Total transactions in the network: {:,} TRTL".format(Result['block']['alreadyGeneratedTransactions']),
                                           "Reward: {:,} TRTL".format(Result['block']['reward']/100))
            paddingLabel2 = SmallLabel()
            TxsLabel = BigLabel(text = "[b]TRANSACTIONS[/b]")

            TxheaderLabel = BlkSearchTx()
            TxheaderLabel.colors = (0.5, 0.5, 0.5, 0.8)
            TxheaderLabel.setText("Hash", "Fee", "Total Amount", "Size", "ForSearchHash")

            blockInfoList = [blkTitleandHashLabel,paddingLabel1,heighAndTotalTxSizelabel,timeAndTotalblkSizelabel,
                             versionAndCurrentTxMedianLabel,difficultyAndEffectiveTxMedianLabel,orphanAndRewardPenaltylabel,
                             txsAndBaserewardLabel,totalCoinNetAndTxFeeLabel,totalTxsInNetAndReward,paddingLabel2,TxsLabel,
                             TxheaderLabel]
            tmpTxList = []
            for i in range(len(Result['block']['transactions'])):
                txLabel = BlkSearchTx()
                if i%2!=1:
                    pass
                else:
                    txLabel.colors = (1,1,1,0.1)
                #'[color=556b2f][ref='+self.hashText+']'+self.hashText+'[/ref][/color]'
                txLabel.setText('[color=556b2f][ref='+Result['block']['transactions'][i]['hash']+']'+Result['block']['transactions'][i]['hash']+'[/ref][/color]',
                                "{:,} TRTL".format(Result['block']['transactions'][i]['fee']/100),
                                "{:,} TRTL".format(Result['block']['transactions'][i]['amount_out']/100),
                                "{:,}".format(Result['block']['transactions'][i]['size']),
                                Result['block']['transactions'][i]['hash']) #last hash is for searching purpose
                tmpTxList.append(txLabel)

            blockInfoList+=tmpTxList
            paddingLabel3 = BigLabel()
            blockInfoList.append(paddingLabel3)
            for lb in blockInfoList:
                self.root.onlyblocksearchscreen.ids.blksearch_display.add_widget(lb)
            blockInfoList = []
        

    def TxSchThread(self):
        self.root.onlyblocksearchscreen.ids.txsearch_display.clear_widgets()
        txHash = self.root.onlyblocksearchscreen.ids.searchTx_inputText.text
        txsearchthread = threading.Thread(target = searchTx, args = (txHash,))
        txsearchthread.start()
        SearchingLabel = Label(text="Searching Transaction...", size_hint= (1, None), height = 50, font_size = 20,
                               color = (0,0,0,0.8))
        self.root.onlyblocksearchscreen.ids.txsearch_display.add_widget(SearchingLabel)

    def BlkSchThread(self):
        self.root.onlyblocksearchscreen.ids.blksearch_display.clear_widgets()
        blkHash = self.root.onlyblocksearchscreen.ids.searchBlk_inputText.text
        blkthread = threading.Thread(target = searchBlk, args = (blkHash,))
        blkthread.start()
        SearchingLabel = Label(text="Searching Block...", size_hint= (1, None), height = 50, font_size = 20,
                               color = (0,0,0,0.8))
        self.root.onlyblocksearchscreen.ids.blksearch_display.add_widget(SearchingLabel)

    def check_search_queue(self, dt):   #for checking search queue has something or not 
        if tx_search_q.empty():         #and then schedule this function on start
            pass
        else:
            self.update_TxSearchResult()
        if blk_search_q.empty():
            pass
        else:
            self.update_BlkSearchResult()
       
    def search_on_click(self, searchType, hashN):  #search by clicking on the live explorer data
        if searchType == 'tx':
            self.root.onlyblocksearchscreen.ids.txsearch_display.clear_widgets()
            self.root.onlyblocksearchscreen.ids.searchTx_inputText.text = hashN
            txsearchthread = threading.Thread(target = searchTx, args = (hashN,))
            txsearchthread.start()
            SearchingLabel = Label(text="Searching Transaction...", size_hint= (1, None), height = 50, font_size = 20,
                                   color = (0,0,0,0.8))
            self.root.onlyblocksearchscreen.ids.txsearch_display.add_widget(SearchingLabel)
        elif searchType == 'blk':
            self.root.onlyblocksearchscreen.ids.blksearch_display.clear_widgets()
            self.root.onlyblocksearchscreen.ids.searchBlk_inputText.text = hashN
            blkthread = threading.Thread(target = searchBlk, args = (hashN,))
            blkthread.start()
            SearchingLabel = Label(text="Searching Block...", size_hint= (1, None), height = 50, font_size = 20,
                                   color = (0,0,0,0.8))
            self.root.onlyblocksearchscreen.ids.blksearch_display.add_widget(SearchingLabel)
#---------------------------------------------------------------------------------------------------------------
    def start_on_onlyblockexplorer(self):
        global daemon
        self.root.transition.direction = 'left'
        self.root.current = 'onlyblockexplorerscreen'
        #start Daemon throught subprocess
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE #hide daemon console
        daemon = subprocess.Popen(self.trtlDaemon, startupinfo = startupinfo)

        #get synch status, txpool, recentblks in one thread
        self.trtl_chain_stat_thread.start()
        self.status_text ="SYNC...\n\nLOCAL:     \nNETWORK: "

        #searchable control
        self.root.onlyblocksearchscreen.ids.searchtxbutton.disabled = True
        self.root.onlyblocksearchscreen.ids.searchblkbutton.disabled = True

        self.root.onlyblocksearchscreen.ids.txsearch_display.add_widget(searchAvailable1)
        self.root.onlyblocksearchscreen.ids.blksearch_display.add_widget(searchAvailable2)
        
        #schedule status update every 5 sec
        Clock.schedule_interval(self.update_SynchStatus,5)
        Clock.schedule_interval(self.check_search_queue, 0.5)
        self.appIsRunning = True
        
    def quitApp(self):
        self.on_stop()
        App.get_running_app().stop()
        Window.close()
        
    def show_popup(self):
        p = AboutPopup()
        p.open()
    
if __name__ =="__main__":
    myApp = Turtle_Completo()
    myApp.run()
