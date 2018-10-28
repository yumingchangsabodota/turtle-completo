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
from explorer_completo import Turtle_Explorer
from wallet_completo import Turtle_Wallet
from functools import partial


####################################---Screens---###########################################
class OnStartScreen(Screen):
    pass
class OnOpenWalletScreen(Screen):
    pass
class WalletScreen(Screen):
    pass
class TransactionScreen(Screen):
    pass

class BlockExplorerScreen(Screen):
    pass
class BlockSearchScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass
##############################################################################################
####################################---Popup windows---#######################################
class AboutPopup(Popup):
    pass

class WalletPrompt(Popup):
    pass

class ChooseWalletPrompt(Popup):
    pass

class StatusLabel(RelativeLayout):
    pass
##############################################################################################
####################################---data layouts---########################################

class WalletStatusLabel(RelativeLayout):
    pass

class BigLabel(Label):
    pass
class SmallLabel(Label):
    blockHash = ""
    def setBlkHash (self, blkhash):
        self.blockHash = blkhash
    def goToSearch(self, instance, value):
        myApp.search_on_click("blk", self.blockHash)


class walletTxData(RelativeLayout):
    transferType = StringProperty()
    txhash_payId = StringProperty('Hash\n{}\nPaymentId\n{}')
    txamount = StringProperty('Amount\n{}')
    txfee = StringProperty('Fee\n{}')
    txtime = StringProperty('Time\n{}')
    
    wtransferType = ObjectProperty(None)
    wTxhash_andpaymentId = ObjectProperty(None)
    wTxamount = ObjectProperty(None)
    wTxfee = ObjectProperty(None)
    wTxtime = ObjectProperty(None)
    forsearchhash = ""
    def setText(self, transferType,txhash, paymentId, txamountt, txfeee, txtimee):
        self.transferType = transferType
        self.forsearchhash = str(txhash)
        self.txhash_payId = self.txhash_payId.format('[color=556b2f][ref='+txhash+']'+txhash+'[/ref][/color]', paymentId)
        self.txamount = self.txamount.format(txamountt)
        self.txfee = self.txfee.format(txfeee)
        self.txtime = self.txtime.format(txtimee)

        self.wtransferType.text = self.transferType
        self.wTxhash_andpaymentId.text = self.txhash_payId
        self.wTxhash_andpaymentId.markup = True
        self.wTxhash_andpaymentId.bind(on_ref_press = self.goToSearch)
        
        self.wTxamount.text = self.txamount
        self.wTxfee.text = self.txfee
        self.wTxtime.text = self.txtime
    def goToSearch(self, instance, value):
        myApp.root.transition.direction = 'left'
        myApp.root.current = 'blocksearchscreen'
        myApp.search_on_click("tx", self.forsearchhash)
    
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
        self.myHeight = str(blkHeight)  #store blk height value for search on click
        
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
        myApp.root.current = 'blocksearchscreen'
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
        myApp.root.current = 'blocksearchscreen'
        myApp.search_on_click("blk", self.itemText_hash)
            
    def goToSearch_byHeight(self, instance, value):
        myApp.root.transition.direction = 'left'
        myApp.root.current = 'blocksearchscreen'
        height = self.itemText_height.replace(",","")
        myApp.search_on_click("blk", height)
##############################################################################################
#these functions calls the search function in the explorer
# then puts the result data into Queue

def searchBlk_q(HashN):
    blk_search_q.put(Turtle_Explorer().searchBlk(HashN))  

def searchTx_q(HashN):
    tx_search_q.put(Turtle_Explorer().searchTx(HashN))

##########################################################################################
#some global variable that is used

tx_search_q = queue.Queue(maxsize = 1)
blk_search_q = queue.Queue(maxsize = 1)
searchAvailable1 = Label(pos_hint = {"x":0.1, "y":0.5}, size_hint = (0.5,None),
                         color = (0,0,0,1))
searchAvailable1.text = "Search will be available when the daemon is synched."
searchAvailable2 = Label(pos_hint = {"x":0.1, "y":0.5}, size_hint = (0.5,None),
                         color = (0,0,0,1))
searchAvailable2.text = "Search will be available when the daemon is synched."

###########################################################################################
class Turtle_Completo(App):

    status_text = StringProperty("DAEMON STATUS\nSYNC...\n\nLOCAL: \nNETWORK: \nPEERS: ")
    wallet_status_text = StringProperty("WALLETD STATUS\nNo Wallet\n\nLOCAL: \nNETWORK: \nPEERS: ")
    walletPathError = StringProperty()
    publicAddress = StringProperty()
    walletFeeText = StringProperty("fee: TRTL")
    unlockedbalance = StringProperty("Available Balance:  TRTL")
    lockedbalance = StringProperty("Locked Balance:  TRTL")
    
    TRTLdaemon = None       #turtle daemon object
    WalltOpened = False     #bool value checking is a wallet service is open or not
    wp = None               #this stores the wallet opening popup window
    chF = None              # this stores the file choosing prompt window when click browse on the wallet opening popup
    myTRTLWallet = None     # turtle wallet object
    
    #acessing and add widgets inside a screen syntax:
    #appname(or self).root.screenname.ids.actualyid.add_widget()
    
    def on_start(self):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    def on_stop(self):
        Clock.unschedule(self.update_SynchStatus)
        Clock.unschedule(self.check_search_queue)
        self.TRTLdaemon.Kill_SubProcessTRTLDaemon()
        self.myTRTLWallet.Kill_SubProcessWalletd()   #needs to check how to properly kill both wallet and daemon threads when closing
        #killDaemon()
        #global daemon
        #daemon.terminate()
        #daemon.kill()

    def build(self):
        global myApp
        TRTLdaemon = None
        self.title = "Turtle Completo v0.1.0"
###################################################################################################################
#get info from Queue update daemon sych status
    def update_SynchStatus(self, dt):
        dheight = self.TRTLdaemon.heightInfo
        nheight = self.TRTLdaemon.netHeight
        peers = self.TRTLdaemon.peers
        pool = self.TRTLdaemon.txPool
        blocks = self.TRTLdaemon.blocks
        
        if dheight == None or nheight == None:
            self.status_text = "DAEMON STATUS\nSYNC...\n\nLOCAL: \nNETWORK: \nPEERS: "
        elif dheight != nheight:
            self.status_text = "DAEMON STATUS\nSYNC...\n\nLOCAL: {}\nNETWORK: {}\nPEERS: {}".format(str(dheight),str(nheight),str(peers))
            self.root.blocksearchscreen.ids.searchtxbutton.disabled = True
            self.root.blocksearchscreen.ids.searchblkbutton.disabled = True
        else:
            self.status_text = "DAEMON STATUS\n\nLOCAL: {}\nNETWORK: {}\nPEERS: {}".format(str(dheight),str(nheight),str(peers))
            self.root.blocksearchscreen.ids.searchtxbutton.disabled = False
            self.root.blocksearchscreen.ids.searchblkbutton.disabled = False

        if pool == None or blocks == None:
            pass
        else:
            self.update_Txpool(pool)
            self.update_RecentBlocks(blocks)

#-------------------------------------------------------------------------------------
#update recent blocks and txpool to gridview in a scroll view
    def update_Txpool(self, txpoolInfo):
        #This part and updates tx pool info on the app
        self.root.blockexplorerscreen.ids.txp_datalistTemplate.clear_widgets()
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
                    self.root.blockexplorerscreen.ids.txp_datalistTemplate.add_widget(TxPoolData1)
            else:
                pass
        except Exception as e:
            print("something wrong in Txpool")
            print(e)

    def update_RecentBlocks(self, blocks):
        #This part and updates recent blocks info on the app
        self.root.blockexplorerscreen.ids.rctblk_datalistTemplate.clear_widgets()
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
                self.root.blockexplorerscreen.ids.rctblk_datalistTemplate.add_widget(RecentBlockData1)
        except Exception as e:
            print("something wrong in recentblks")
            print(e)
#-------------------------------------------------------------------------------------
    def update_TxSearchResult(self):
        #This part formats and construct the search transaction results then display them in labels
        self.root.blocksearchscreen.ids.txsearch_display.clear_widgets()
        #get tx search result from queue
        Result = tx_search_q.get()
        #if there is error display error msg, if not construct and display search result
        if Result["error"] == "yes":
            ErrorLabel = BigLabel(text = Result['msg'])
            self.root.blocksearchscreen.ids.txsearch_display.add_widget(ErrorLabel)  
        elif Result["error"] == "no":
            current_h = Result['current_height']
            MyResult = Result['result']['result']
            #calculate confirmation from block height
            if current_h - MyResult['block']['height'] <= 0:
                confirmation = 0
            else:
                confirmation = "{:,}".format(current_h - MyResult['block']['height'])
            #first confirmation timestamp
            Firstconfirmation = datetime.fromtimestamp(MyResult['block']['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            
            #calculate sum of the outputs
            sumOfOutputs = sum(amount['amount'] for amount in MyResult['tx']['vout'])
            sumOfOutputs = "{:,}".format(sumOfOutputs/100)

            #get block hash, used for on click search
            blkHash = MyResult['block']['hash']

            TxLabel = BigLabel(text = "[b]TRANSACTION[/b]")
            #get transaction hash
            txHashLabel = SmallLabel(text = "Hash: "+MyResult['txDetails']['hash'])
            #confirmation and first confirmation time
            ConfirmLabel = SmallLabel(text = "Confirmations: " + confirmation +", First confirmation time: "+Firstconfirmation)
            #fee
            feeLabel = SmallLabel(text = "Fee: " + "{:,}".format(MyResult['txDetails']['fee']/100) + " TRTL")
            #sum of outputs
            sumOutLabel = SmallLabel(text = "Sum of outputs: " + sumOfOutputs+ " TRTL")
            #transaction size
            sizeLabel = SmallLabel(text = "Size: "+ "{:,}".format(MyResult['txDetails']['size']))
            #mixin count
            mixinLabel = SmallLabel(text = "Mixin: "+ "{:,}".format(MyResult['txDetails']['mixin']))
            
            InBlockLabel = BigLabel(text = "[b]IN BLOCK[/b]" )
             #'[color=556b2f][ref='+self.hashText+']'+self.hashText+'[/ref][/color]'
            #in block info, add on_click_search behavior for block hash
            blkHashLabel = SmallLabel(text = "Hash: "+'[color=556b2f][ref='+blkHash+']'+blkHash+'[/ref][/color]')  #add click to hash search
            blkHashLabel.markup = True
            blkHashLabel.setBlkHash(blkHash)
            blkHashLabel.bind(on_ref_press = blkHashLabel.goToSearch)

            #block height
            blkheighLabel = SmallLabel(text = "Height: " + "{:,}".format(MyResult['block']['height']))
            timeLabel = SmallLabel(text = "Timestamp: " + Firstconfirmation)

            #input header
            inputHeader = TXInputs()
            inputHeader.setText("Amount", "Image")
            inputHeader.colors = (0.5, 0.5, 0.5, 0.8)
            #loop through input data and save to list
            inputList = []
            if MyResult['tx']['vin'][0]['type'] == 'ff': #check tx input counts
                inputCount = str(0)
            else:
                inputCount = "{:,}".format(len(MyResult['tx']['vin']))
                for i in range(len(MyResult['tx']['vin'])):
                    txinput = TXInputs()
                    if i%2!=1:
                        pass
                    else:
                        txinput.colors = (1,1,1,0.1)
                    inAmount = "{:,}".format(MyResult['tx']['vin'][i]['value']['amount']/100)
                    txinput.setText(inAmount+" TRTL",
                                    str(MyResult['tx']['vin'][i]['value']['k_image']))
                    inputList.append(txinput)
            #input big label
            InputLabel = BigLabel(text = "[b]INPUTS ("+inputCount+")[/b]" )
            #add 2 padding label
            paddingLabel1 = SmallLabel()
            paddingLabel2 = SmallLabel()
            #save above constructors into a list
            LabelList = [TxLabel,txHashLabel,ConfirmLabel,feeLabel,sumOutLabel,
                        sizeLabel,mixinLabel, paddingLabel1,InBlockLabel, blkHashLabel,
                        blkheighLabel,timeLabel, paddingLabel2,InputLabel,inputHeader]
            #append inputs to the big list
            LabelList = LabelList + inputList

            #get output count
            outputCount = "{:,}".format(len(MyResult['tx']['vout']))
            #output title lable
            OutputLabel = BigLabel(text = "[b]OUTPUTS ("+outputCount+")[/b]" )
            #output header
            outputHeader = TXOutputs()
            outputHeader.setText("Amount", "Key")
            outputHeader.colors = (0.5, 0.5, 0.5, 0.8)
            #loop through outputs and save to a list
            outputList = [OutputLabel,outputHeader]
            for i in range(len(MyResult['tx']['vout'])):
                txoutput = TXOutputs()
                if i%2!=1:
                    pass
                else:
                    txoutput.colors = (1,1,1,0.1)
                outAmount = "{:,}".format(MyResult['tx']['vout'][i]['amount']/100)
                txoutput.setText(outAmount+" TRTL",
                                str(MyResult['tx']['vout'][i]['target']['data']['key']))
                outputList.append(txoutput)
            #append outputlist to big list
            LabelList += outputList
            paddingLabel3 = BigLabel()
            LabelList.append(paddingLabel3)
            #add labels in big list to container widget
            for lb in LabelList:
                self.root.blocksearchscreen.ids.txsearch_display.add_widget(lb)
            LabelList = []
            
    def update_BlkSearchResult(self):
        #This part formats and construct the search block results then display them in labels
        self.root.blocksearchscreen.ids.blksearch_display.clear_widgets()
        #get result hash table from queue
        Result = blk_search_q.get()
        #if there is error, display error msg, if not, display search block result
        if Result["error"] == "yes":
            ErrorLabel = BigLabel(text = Result['msg'])
            self.root.blocksearchscreen.ids.blksearch_display.add_widget(ErrorLabel)  
        elif Result["error"] == "no":
            Result = Result['result']['result']
            
            #big labels are for titles, small labels for content
            BlockTitleLabel = BigLabel(text = "[b]BLOCK[/b]", size_hint = (0.1,1), pos_hint={"x":0, "y":0},valign = 'bottom')
            blockHashLabel = SmallLabel(text = "[b]"+Result['block']['hash']+"[/b]",size_hint = (0.9,1), pos_hint={"x":0.08, "y":0},
                                        valign ='bottom', font_size = 16, color = (47/255,79/255,79/255,1))
            blkTitleandHashLabel = RelativeLayout(size_hint = (1,None), height = 30)
            blkTitleandHashLabel.add_widget(BlockTitleLabel)
            blkTitleandHashLabel.add_widget(blockHashLabel)
            #add padding
            paddingLabel1 = SmallLabel(height = 10)

            #1 block height and total transaction size  
            #'[color=556b2f][ref='+self.hashText+']'+self.hashText+'[/ref][/color]'
            heighAndTotalTxSizelabel = BlkSearchData()
            heighAndTotalTxSizelabel.setText("Height: {} {:,} {}".format("[b][size=20][color=556b2f][ref=<]<[/ref][/color][/size][/b]",Result['block']['height'],"[b][size=20][color=556b2f][ref=>]>[/ref][/color][/size][/b]"),
                                             "Total transaction size, bytes: {:,}".format(Result['block']['transactionsCumulativeSize']))
            heighAndTotalTxSizelabel.setMyHeight(Result['block']['height'])
            
            #2 time and total block size
            timeAndTotalblkSizelabel = BlkSearchData()
            #the genesis block returns 0 in the timestamp, set genesis timestamp to nothing
            if Result['block']['timestamp'] != 0:  #check if it is genesis block
                timeAndTotalblkSizelabel.setText("Timestamp: "+datetime.fromtimestamp(Result['block']['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                                            "Total block size, bytes: {:,}".format(Result['block']['blockSize']))
            else:
                timeAndTotalblkSizelabel.setText("Timestamp: ",
                                            "Total block size, bytes: {:,}".format(Result['block']['blockSize']))
            #3 version and block size median
            versionAndCurrentTxMedianLabel = BlkSearchData()
            versionAndCurrentTxMedianLabel.setText("Version: {}.{}".format(Result['block']['major_version'],Result['block']['minor_version']),
                                                    "Current txs median, bytes: {:,}".format(Result['block']['sizeMedian']))
            #4 difficulty and effective tx median
            difficultyAndEffectiveTxMedianLabel = BlkSearchData()
            difficultyAndEffectiveTxMedianLabel.setText("Difficulty: {:,}".format(Result['block']['difficulty']),
                                                        "Effective txs median, bytes: {:,}".format(Result['block']['effectiveSizeMedian']))
            #5 Orphan status and reward penalty
            orphanAndRewardPenaltylabel = BlkSearchData()
            orphan = "No" if Result['block']['orphan_status'] == False else "Yes"
            orphanAndRewardPenaltylabel.setText("Orphan: {}".format(orphan),
                                                "Reward penalty: {:,}%".format(Result['block']['penalty']))
            #6 transactions and base reward
            txsAndBaserewardLabel = BlkSearchData()
            txsAndBaserewardLabel.setText("Transactions: {:,}".format(len(Result['block']['transactions'])),
                                            "Base reward: {:,} TRTL".format(Result['block']['baseReward']/100))
            #7 total coins in the network and transaction fee
            totalCoinNetAndTxFeeLabel = BlkSearchData()
            totalCoinNetAndTxFeeLabel.setText("Total coins in the network: {:,} TRTL".format(int(Result['block']['alreadyGeneratedCoins'])/100),
                                              "Transactions fee: {:,} TRTL".format(Result['block']['totalFeeAmount']/100))
            #8 total transactions in the network and reward
            totalTxsInNetAndReward = BlkSearchData()
            totalTxsInNetAndReward.setText("Total transactions in the network: {:,} TRTL".format(Result['block']['alreadyGeneratedTransactions']),
                                           "Reward: {:,} TRTL".format(Result['block']['reward']/100))
            #add padding in the search result display
            paddingLabel2 = SmallLabel()
            TxsLabel = BigLabel(text = "[b]TRANSACTIONS[/b]")
            
            #add tx header in the block to the result display
            TxheaderLabel = BlkSearchTx()
            TxheaderLabel.colors = (0.5, 0.5, 0.5, 0.8)
            TxheaderLabel.setText("Hash", "Fee", "Total Amount", "Size", "ForSearchHash")

            #append the above data to a list
            blockInfoList = [blkTitleandHashLabel,paddingLabel1,heighAndTotalTxSizelabel,timeAndTotalblkSizelabel,
                             versionAndCurrentTxMedianLabel,difficultyAndEffectiveTxMedianLabel,orphanAndRewardPenaltylabel,
                             txsAndBaserewardLabel,totalCoinNetAndTxFeeLabel,totalTxsInNetAndReward,paddingLabel2,TxsLabel,
                             TxheaderLabel]
            #loop through block transaction data and construct a display label object and append to a list
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
                
            #append the tx data to the bigger list that has the general info
            blockInfoList+=tmpTxList
            #add last padding
            paddingLabel3 = BigLabel()
            blockInfoList.append(paddingLabel3)
            #loop through the label list and add all the labels in the search result display
            for lb in blockInfoList:
                self.root.blocksearchscreen.ids.blksearch_display.add_widget(lb)
            blockInfoList = []

    #this is initiates the tx searching thread
    def TxSchThread(self):
        self.root.blocksearchscreen.ids.txsearch_display.clear_widgets()
        txHash = self.root.blocksearchscreen.ids.searchTx_inputText.text
        
        txThread = threading.Thread(target = searchTx_q, args = (txHash,))
        txThread.start()
        
        SearchingLabel = Label(text="Searching Transaction...", size_hint= (1, None), height = 50, font_size = 20,
                               color = (0,0,0,0.8))
        self.root.blocksearchscreen.ids.txsearch_display.add_widget(SearchingLabel)
    #this is initiates the blk searching thread
    def BlkSchThread(self):
        self.root.blocksearchscreen.ids.blksearch_display.clear_widgets()
        blkHash = self.root.blocksearchscreen.ids.searchBlk_inputText.text
        
        blkthread = threading.Thread(target = searchBlk_q, args = (blkHash,))
        blkthread.start()
        
        SearchingLabel = Label(text="Searching Block...", size_hint= (1, None), height = 50, font_size = 20,
                               color = (0,0,0,0.8))
        self.root.blocksearchscreen.ids.blksearch_display.add_widget(SearchingLabel)

    def check_search_queue(self, dt):   #for checking search queue has something or not 
        if tx_search_q.empty():         #and this function is scheduled on start
            pass
        else:
            self.update_TxSearchResult()
        if blk_search_q.empty():
            pass
        else:
            self.update_BlkSearchResult()
       
    def search_on_click(self, searchType, hashN):  #search by clicking on the live explorer data
        if searchType == 'tx':
            self.root.blocksearchscreen.ids.txsearch_display.clear_widgets()
            self.root.blocksearchscreen.ids.searchTx_inputText.text = hashN
            
            txThread = threading.Thread(target = searchTx_q, args = (hashN,))
            txThread.start()
            
            SearchingLabel = Label(text="Searching Transaction...", size_hint= (1, None), height = 50, font_size = 20,
                                   color = (0,0,0,0.8))
            self.root.blocksearchscreen.ids.txsearch_display.add_widget(SearchingLabel)
        elif searchType == 'blk':
            self.root.blocksearchscreen.ids.blksearch_display.clear_widgets()
            self.root.blocksearchscreen.ids.searchBlk_inputText.text = hashN

            blkthread = threading.Thread(target = searchBlk_q, args = (hashN,))
            blkthread.start()
            
            SearchingLabel = Label(text="Searching Block...", size_hint= (1, None), height = 50, font_size = 20,
                                   color = (0,0,0,0.8))
            self.root.blocksearchscreen.ids.blksearch_display.add_widget(SearchingLabel)
#---------------------------------------------------------------------------------------------------------------
    #this function is called when we click the turtle completo button on start screen
    # it start the explorer basically but not the wallet yet
    def start_on_blockexplorer(self): 
        self.root.transition.direction = 'left'
        self.root.current = 'blockexplorerscreen'

        self.TRTLdaemon = Turtle_Explorer()
        self.TRTLdaemon.daemon = True
        self.TRTLdaemon.start()

        #self.status_text ="DAEMON STATUS\nSYNC...\n\nLOCAL: \nNETWORK: \nPEERS: "

        #searchable control
        self.root.blocksearchscreen.ids.searchtxbutton.disabled = True
        self.root.blocksearchscreen.ids.searchblkbutton.disabled = True

        self.root.blocksearchscreen.ids.txsearch_display.add_widget(searchAvailable1)
        self.root.blocksearchscreen.ids.blksearch_display.add_widget(searchAvailable2)
        
        #schedule status update every 20 sec
        Clock.schedule_interval(self.update_SynchStatus,20)
        Clock.schedule_interval(self.check_search_queue, 2)
        self.appIsRunning = True
        
    def quitApp(self):
        self.on_stop()
        App.get_running_app().stop()
        Window.close()

    #about pop up window
    def show_popup(self):
        p = AboutPopup()
        p.open()
#-------------------------------------------
    #when click wallet button on side bar, if the wallet is not opened
    # popup will show
    #else nothing
    def ToWallet(self):
        self.root.current = 'walletscreen'
        if self.WalltOpened:
            pass
        else:
            self.wp = WalletPrompt()
            self.wp.open()
            
    #this is called when we open a wallet on the popup
    def openWallet(self):
        #check if the path is a .wallet file
        path = self.wp.ids.wallet_path.text
        self.wp.ids.wallet_path.text = ""
        tmpfile = path.split('.')

        #if the path does not end with wallet, then shows an error
        if tmpfile[-1]!='wallet':
            self.walletPathError = "Please provide a valid .wallet file"
        else:
            path = path.replace('\\',"\\\\")
            path = '"'+path+'"'
      
            password = self.wp.ids.wallet_password1.text
            walletd_arg = ['turtleservices\\turtle-service','-w',path,'-p',password,'--daemon-address localhost --daemon-port 11898 --rpc-password']
            self.myTRTLWallet = Turtle_Wallet(walletd_arg)
            self.myTRTLWallet.daemon = True
            self.myTRTLWallet.start()
            self.wp.dismiss()
            Clock.schedule_interval(self.updateWalletdStat,5)
            self.root.walletscreen.ids.sendtxbutton.disabled = True
            self.WalltOpened = True

    #this function is called and scheduled when a wallet file is opened
    #it updated the wallet info on display
    def updateWalletdStat(self, dt):
        Address = self.myTRTLWallet.walletAddress
        availableB = self.myTRTLWallet.AvailableBalance
        lockedB = self.myTRTLWallet.lockedBalance
        wpeers = self.myTRTLWallet.wpeers
        wnheight = self.myTRTLWallet.walletNetBlock
        wdheight = self.myTRTLWallet.walletLocalBlock
        wFee = self.myTRTLWallet.wFee
        walletTx = self.myTRTLWallet.walletTx
        self.root.walletscreen.ids.wallettransaction.clear_widgets()
        if Address != None:
            self.publicAddress = Address
            self.walletFeeText = "Node fee: {} TRTL     *The node fee will be automatically added to the send amount".format(wFee)
    
        if wdheight == None or wnheight == None:
            self.wallet_status_text = "WALLETD STATUS\nSYNC...\n\nLOCAL: \nNETWORK: \nPEERS: "
        elif wdheight < wnheight-1:
            self.wallet_status_text = "WALLETD STATUS\nSYNC...\n\nLOCAL: {}\nNETWORK: {}\nPEERS: {}".format(str(wdheight),str(wnheight),str(wpeers))
            if lockedB == None or availableB == None:
                pass
            else:
                self.unlockedbalance = "Available Balance: {} TRTL      Correct balance will be displayed when walletd-service is fully synched...".format(availableB)
                self.lockedbalance = "Locked Balance: {} TRTL".format(lockedB)
        else:
            self.wallet_status_text = "WALLETD STATUS\n\nLOCAL: {}\nNETWORK: {}\nPEERS: {}".format(str(wdheight),str(wnheight),str(wpeers))
            if lockedB == None or availableB == None:
                pass
            else:
                self.unlockedbalance = "Available Balance: {} TRTL".format(availableB)
                self.lockedbalance = "Locked Balance: {} TRTL".format(lockedB)
            self.root.walletscreen.ids.sendtxbutton.disabled = False

        if walletTx != None:
            i = 0
            walletTx = reversed(walletTx)
            for tx in walletTx:
                wTx = walletTxData()
                if i%2!=1:
                    pass
                else:
                    wTx.colors = (1,1,1,0.1)
                
                txfee = round(tx['transactions'][0]['fee']/100,2)
                txamount = round(tx['transactions'][0]['amount']/100,2)
                if txamount < 0:
                    txamount = round((tx['transactions'][0]['amount']/100 + txfee)*-1,2)
                    transfertype = '[b]OUT[/b]'
                else:
                    transfertype = '[b]IN[/b]'
                txhash = tx['transactions'][0]['transactionHash']
                payId = tx['transactions'][0]['paymentId']
                txTime = datetime.fromtimestamp(tx['transactions'][0]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                wTx.setText(transfertype,txhash, payId, txamount, txfee, txTime)
                self.root.walletscreen.ids.wallettransaction.add_widget(wTx)
                i+=1
                #datetime.fromtimestamp(Result['block']['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    #see to do list
    def createWallet(self):
        global myApp
        self.WalltOpened = True
        self.wp.dismiss()
    #see to do list
    def importWallet(self):
        global myApp
        self.WalltOpened = True
        self.wp.dismiss()
    #this function opens the choosing wallet file prompt
    def browseWalletPath(self):
        self.chF = ChooseWalletPrompt()
        self.chF.open()
    #this is function gets the chosen file path  
    def getWalletPath(self):
        path = str(self.chF.ids.file_icon_view.selection[0])
        self.wp.ids.wallet_path.text = path
        self.chF.dismiss()
    #see to do list
    def sendTx(self):
        address = self.root.walletscreen.ids.sendTxAddress.text
        amount = self.root.walletscreen.ids.sendTxAmount.text  
        paymentId = self.root.walletscreen.ids.sendTxPaymentId.text

        if address=='' or amount == '' :
            print("please check transaction info")
        else:
            amount = float(amount)*100
            self.root.walletscreen.ids.sendTxAddress.text = ''
            self.root.walletscreen.ids.sendTxAmount.text = ''
            self.root.walletscreen.ids.sendTxPaymentId.text = ''
            self.myTRTLWallet.sendTransaction(address, amount, paymentId)

       
if __name__ =="__main__":
    myApp = Turtle_Completo()
    myApp.run()
