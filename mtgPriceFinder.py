################################################################################
#
# Magic: the Gathering Card Price Checker
#
# Author(s):    Gary Chan
# Version:      1.2.2
#
# Version History:
# Date          Version     Change
# 31/01/16      1.2.2       Move sites to array for rearranging
# 20/06/15      1.2.1       Re-added TimeVaultGames
#                           Changed timer constant
#                           Fixed split cards for Card Kingdom
# 16/05/15      1.2         Added timer constant
# 10/10/14      1.1.1       Removed TimeVaultGames
# 14/09/14      1.1         Added command-line options
# 13/09/14      1.0         Initial Release
#
################################################################################

# Imported Libraries
import argparse
import ctypes
import time
import webbrowser
from Tkinter import *

# Global variables
timer = 1
vendors = ['TCG Player',
           'Channel Fireball',
           'Time Vault Games',
           'Mugu Games',
           'Super Games',
           'Magic Stronghold',
           'Face to Face Games',
           'Star City Games',
           'Card Kingdom']
sites = ['http://magic.tcgplayer.com/db/magic_single_card.asp?cn=',
         'http://store.channelfireball.com/products/search?query=',
         'http://www.timevaultgames.com/products/search?query=',
         'http://www.mugugames.com/products/search?query=',
         'http://store.supergamesinc.com/products/search?q=',
         'http://www.magicstronghold.com/products/search?query=',
         'http://www.facetofacegames.com/products/search?query=',
         'http://sales.starcitygames.com/search.php?substring=',
         'http://cardkingdom.com/catalog/view?search=basic&filter[name]=']

# Input class for input
class Input(object):
    # Initialize
    def __init__(self, message):
        self.root = Tk()
        self.root.title(message)
        self.input = ''
        self.exit = True
        Label(self.root, text = message).pack()
        self.entry = Entry(self.root)
        self.entry.pack()
        self.entry.focus_set()
        self.okButton = Button(self.root, text = 'OK', command = self.confirm)
        self.okButton.pack()
        self.root.bind_all('<Return>', lambda event: self.confirm())
        self.root.bind_all('<Escape>', lambda event: self.cancel())
        self.root.focus_force()
    
    # Confirm and close
    def confirm(self):
        self.exit = False
        self.input = self.entry.get()
        self.root.destroy()
    
    # Cancel and close
    def cancel(self):
        self.root.destroy()
    
    # Start GUI (Called from outside the class)
    def run(self):
        self.root.mainloop()
        return not self.exit
    
    # Get input (Called from outside the class)
    def getInput(self):
        return self.input

# Menu class for selection menu
class Menu(object):
    # Initialize
    def __init__(self):
        self.root = Tk()
        self.exit = True
        self.listText = ['1. ' + vendors[0],
                         '2. ' + vendors[1],
                         '3. ' + vendors[2],
                         '4. ' + vendors[3],
                         '5. ' + vendors[4],
                         '6. ' + vendors[5],
                         '7. ' + vendors[6],
                         '8. ' + vendors[7],
                         '9. ' + vendors[8]]
        self.siteList = [0] * len(self.listText)
        self.checkbox = [0] * len(self.listText)
        self.message = Label(self.root,
                             text = 'Check the sites to search for prices')
        self.message.grid(row = 0)
        for i in range(0, len(self.siteList)):
            self.siteList[i] = IntVar()
            self.siteList[i].set(True)
            self.checkbox[i] = Checkbutton(self.root, text = self.listText[i],
                                           variable = self.siteList[i])
            self.checkbox[i].grid(row = i + 1, column = 0, sticky = W)
        self.okButton = Button(self.root, text = 'OK', command = self.confirm)
        self.okButton.grid(row = len(self.siteList), column = 2)
        self.root.bind_all('<Return>', lambda event: self.confirm())
        self.root.bind_all('<Escape>', lambda event: self.cancel())
        self.root.focus_force()
    
    # Confirm and close
    def confirm(self):
        self.exit = False
        self.root.destroy()
    
    # Cancel and close
    def cancel(self):
        self.root.destroy()
    
    # Start GUI (Called from outside the class)
    def run(self):
        self.root.mainloop()
        return not self.exit
    
    # Get checklist (Called from outside the class)
    def getList(self):
        for i in range(0, len(self.siteList)):
            if self.siteList[i].get():
                self.siteList[i] = True
            else:
                self.siteList[i] = False
        return self.siteList

# Message box function
# Styles:                                   Return Codes:
# 0x00 : OK                                 1
# 0x01 : OK     | Cancel                    1 |  2
# 0x02 : Abort  | Retry     | Ignore        3 |  4 |  5
# 0x03 : Yes    | No        | Cancel        6 |  7 |  2
# 0x04 : Yes    | No                        6 |  7
# 0x05 : Retry  | Cancel                    4 |  2
# 0x06 : Cancel | Try Again | Continue      2 | 10 | 11
#
# Icons:
# 0x10 : Error
# 0x20 : Question
# 0x30 : Warning
# 0x40 : Information
def mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

# Get arguments function
def getArguments():
    # Create parser
    parser = argparse.ArgumentParser()
    
    # Add arguments
    parser.add_argument('-l', '--list',
                        action  = 'store',
                        help    = 'Search prices for cards listed in text file')
    
    # Return parsed arguments
    return parser.parse_args()

# Construct URL function
def buildURL(card, idx):
    if vendors[idx] == 'TCG Player':
        card = card.replace('+', ' ')
    if vendors[idx] == 'Card Kingdom':
        card = card.replace('+//+', '-')
    
    return sites[idx] + card

# Search function
def search(card, siteList):
    card = card.replace(' ', '+')
    for i in range(len(vendors)):
        if siteList[i]:
            webbrowser.open_new_tab(buildURL(card, i))
            time.sleep(timer)

# Process list function
def processList(file, siteList):
    list = open(file)
    for card in list:
        search(card.strip(), siteList)
        rcode = mbox(u'Attention!', u'Search next card?', 0x24)
        if rcode == 7:
            return
    mbox(u'Attention!', u'End of list reached.\r\nClick OK to exit.', 0x40)

# Get cards function
def getCards(siteList):
    while True:
        card = ''
        while card == '':
            gui = Input('Enter card name')
            if gui.run():
                card = gui.getInput()
                
                # Check if input is valid
                if card == '':
                    mbox(u'Warning!', u'Please enter a card name.', 0x30)
                continue
            
            # Terminate
            rcode = mbox(u'Attention', u'Are you sure you want to quit?', 0x24)
            if rcode == 6:
                return
        
        # Search card
        search(card.strip(), siteList)
        
        # Prompt to continue
        rcode = mbox(u'Attention', u'Search another card?', 0x24)
        if rcode == 7:
            return

# Main function
def main():
    # Check sites
    siteList = [False]
    while True:
        gui = Menu()
        if gui.run():
            siteList = gui.getList()
            if any(siteList):
                break
        
        # Terminate
        rcode = mbox(u'Attention', u'Are you sure you want to quit?', 0x24)
        if rcode == 6:
            return
    
    # Parse arguments
    args = getArguments()
    if args.list:
        processList(args.list, siteList)
    else:
        getCards(siteList)

# Check if script is executed as main
if __name__ == '__main__':
    main()

