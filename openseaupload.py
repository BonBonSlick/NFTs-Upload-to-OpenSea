import tkinter
import subprocess
from tkinter import *
from tkinter import filedialog
import os
import sys
import pickle
import time
import datetime
import string, random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service

def randomStringOfLength(length = 32):
   return ''.join(random.choice(string.hexdigits) for char in range(length))

def removeFile(fileNamePath):
      if os.path.exists(fileNamePath):
            print('Removing File! ', fileNamePath)
            os.remove(fileNamePath)

def writeLog(Error):
    print('=======================')
    print('=======================')
    print('=======================')
    print('======================= EXCEPTION =======================')
    print('=======================')
    print('=======================')
    print('=======================')
    log = open("log.txt", "a")
    log.write('EXCEPTION! ' +
              '[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '] : '
              + str(Error)
              )
    log.close()


rootWindow = Tk()
rootWindow.geometry('500x400')
rootWindow.title("NFTs Upload to OpenSea  ")
inputNFTFolder = ["NFTs folder :", 0, 0, 0, 0, 0, 0, 0, 0]
pathScriptFile = sys.path[0]
pathMainDir = os.path.join(pathScriptFile)

def openChromeProfile():
    subprocess.Popen(
        [
            "start",
            "chrome",
            "--remote-debugging-port=8989",
            "--user-data-dir=" + pathMainDir + "/chrome_profile",
        ],
        shell=True,
    )

def saveFormFilePath():
    return os.path.join(pathScriptFile, "saved_form_inputs.cloud")

# ask for directory on clicking button, changes button name.
def absoluteFilePaths(sortByDate = True):
    paths = []
    for root, dirs, files in os.walk(os.path.abspath(pathNFTFolder)):
        for file in files:
            paths.append(os.path.join(root, file))

    if True == sortByDate:
        paths.sort(key=os.path.getctime)
    
    return paths

def initNFTFolderPath():
    global pathNFTFolder
    pathNFTFolder = filedialog.askdirectory()
    updateNFTFolderPath(pathNFTFolder)


def updateNFTFolderPath(upload_folder_input):
    upload_folder_input_button["text"] = upload_folder_input


class InputField:
    def __init__(self, label, row_io, column_io, pos, master=rootWindow):
        self.master = master
        self.input_field = Entry(self.master)
        self.input_field.label = Label(master, text=label)
        self.input_field.label.grid(row=row_io, column=column_io)
        self.input_field.grid(row=row_io, column=column_io + 1)
        try:
            with open(saveFormFilePath(), "rb") as infile:
                new_dict = pickle.load(infile)
                self.updateInput(new_dict[pos])
        except FileNotFoundError:
            pass

    def updateInput(self, text):
        self.input_field.delete(0, "end")
        self.input_field.insert(0, text)

    def saveInput(self, pos):
        inputNFTFolder.insert(pos, self.input_field.get())
        with open(saveFormFilePath(), "wb") as outfile:
            pickle.dump(inputNFTFolder, outfile)


###input objects###
collection_link_input = InputField("OpenSea Collection Link (required):", 2, 0, 1)
price = InputField("Price (default 0.00095):", 3, 0, 4)
description = InputField("Description (optional):", 5, 0, 6)
external_link = InputField("External link (optional):", 6, 0, 8)

###save inputs###

def save():
    inputNFTFolder.insert(0, pathNFTFolder)
    collection_link_input.saveInput(1)
    price.saveInput(4)
    description.saveInput(6)
    external_link.saveInput(8)


# _____MAIN_CODE_____
def main():
    try:
    
        print('=======================')
        print('======================= Uploading process started...')
        print('=======================')
        print('=======================')
        print('======================= WARNING uploaded NFT files will be REMOVED from local device after it was uploaded!')
        print('=======================')
        ###START###
        collectionLink = str(collection_link_input.input_field.get()) or ''
        loopPrice = float(price.input_field.get()) or 0.00095
        loopExternalLink = str(external_link.input_field.get()) or ''
        loopDdescription = str(description.input_field.get()) or ''

        # chrome options
        chromeService = Service(pathMainDir + "/chromedriver.exe")
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option("debuggerAddress", "localhost:8989")
        driver = webdriver.Chrome(service=chromeService, options=chromeOptions)
        wait = WebDriverWait(driver, 60)

        # wait for methods
        def waitCssSelectorRendered(code):
            print('Searching for DOM element by selecor : ' + code)
            time.sleep(1)
            wait.until(ExpectedConditions.presence_of_element_located((By.CSS_SELECTOR, code)))

        def waitCssSelectorClickable(code):
            print('Waiting for element selector to be visible and clickable : ' + code)
            time.sleep(1)
            wait.until(ExpectedConditions.elementToBeClickable((By.CSS_SELECTOR, code)))

        def waitXpath(code):
            print('Waiting for element selector to be rendered, added to DOM : ' + code)
            time.sleep(1)
            wait.until(ExpectedConditions.presence_of_element_located((By.XPATH, code)))

        files = absoluteFilePaths()
        for fileAbsolutePathName in files:
            print("Start creating NFT " + fileAbsolutePathName)
            driver.get(collectionLink)
            time.sleep(3)

            waitXpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
            createTab = driver.find_element(by=By.XPATH, value='//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
            createTab.click()
            time.sleep(1)

            waitXpath('//*[@id="media"]')
            imageUpload = driver.find_element(by=By.XPATH, value='//*[@id="media"]')
            imageUpload.send_keys(fileAbsolutePathName)

            inputName = driver.find_element(by=By.XPATH, value='//*[@id="name"]')
            inputName.send_keys(randomStringOfLength())
            time.sleep(1)

            inputExternalLink = driver.find_element(by=By.XPATH, value='//*[@id="external_link"]')
            inputExternalLink.send_keys(loopExternalLink)
            time.sleep(1)

            inputDescription = driver.find_element(by=By.XPATH, value='//*[@id="description"]')
            inputDescription.send_keys(loopDdescription)
            time.sleep(1)

            btnCreateNFT = driver.find_element(by=By.XPATH, value='//*[@id="__next"]/div[1]/main/div/div/section/div[2]/form/div/div[1]/span/button')
            driver.execute_script("arguments[0].click();", btnCreateNFT)
            time.sleep(1)

            waitCssSelectorRendered("i[aria-label='Close']")
            modalCloseIco = driver.find_element(by=By.CSS_SELECTOR, value="i[aria-label='Close']")
            modalCloseIco.click()
            time.sleep(1)

            main_page = driver.current_window_handle

            waitXpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
            sellBtn = driver.find_element(by=By.XPATH, value='//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
            sellBtn.click()

            waitCssSelectorRendered("input[placeholder='Amount']")
            amountInputField = driver.find_element(by=By.CSS_SELECTOR, value="input[placeholder='Amount']")
            amountInputField.send_keys(str(loopPrice))

            waitCssSelectorRendered("button[type='submit']")
            submitSellBtn = driver.find_element(by=By.CSS_SELECTOR, value="button[type='submit']")
            submitSellBtn.click()
            time.sleep(5)

            waitCssSelectorRendered("button[class='Blockreact__Block-sc-1xf18x6-0 Buttonreact__StyledButton-sc-glfma3-0 bhqEJb kCijbX']")
            signSell = driver.find_element(by=By.CSS_SELECTOR, value="button[class='Blockreact__Block-sc-1xf18x6-0 Buttonreact__StyledButton-sc-glfma3-0 bhqEJb kCijbX']")
            signSell.click()
            time.sleep(2)

            for handle in driver.window_handles:
                if handle != main_page:
                    login_page = handle

            # change the control to signin page
            driver.switch_to.window(login_page)

            waitCssSelectorRendered("button[data-testid='request-signature__sign']")
            sign2 = driver.find_element(by=By.CSS_SELECTOR, value="button[data-testid='request-signature__sign']")
            sign2.click()
            time.sleep(1)

            # change control to main page
            driver.switch_to.window(main_page)
            time.sleep(1)

            removeFile(fileAbsolutePathName)

            print('=======================')
            print('======================= NFT uploads finished! =======================')
            print('=======================')

    except Exception as Error:
        writeLog(Error)
        time.sleep(15)
        main()


#####BUTTON ZONE#######
button_save = tkinter.Button(rootWindow, width=20, text="Save Form", command=save)
button_save.grid(row=23, column=1)
button_start = tkinter.Button(rootWindow, width=20, bg="green", fg="white", text="Start", command=main)
button_start.grid(row=25, column=1)
open_browser = tkinter.Button(rootWindow, width=20,  text="Open Chrome Browser", command=openChromeProfile)
open_browser.grid(row=22, column=1)
upload_folder_input_button = tkinter.Button(rootWindow, width=20, text="Add NFTs Folder", command=initNFTFolderPath)
upload_folder_input_button.grid(row=21, column=1)

try:
    with open(saveFormFilePath(), "rb") as infile:
        new_dict = pickle.load(infile)
        global pathNFTFolder
        updateNFTFolderPath(new_dict[0])
        pathNFTFolder = new_dict[0]
except Exception as Error:
    writeLog(Error)
    time.sleep(30)
    pass
#####BUTTON ZONE END#######

rootWindow.mainloop()
