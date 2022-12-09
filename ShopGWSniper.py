from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
from time import sleep
from datetime import datetime, timedelta

VERBOSE = True # Will print status of script
TESTING_MODE = True # Will keep chrome open post run and will NOT confirm bid
BASE_URL = "https://shopgoodwill.com/"
CONFIG_FILE = "config.json"
TIME_LEFT_UNTIL_BID = 15 #seconds

# LOAD IN CONFIG FILE VALUES
data = {}
with open(CONFIG_FILE, "r") as jsonfile:
    data = json.load(jsonfile)

ITEMS = data["ITEMS"]
EMAIL = data["EMAIL"]
PASSWORD = data["PASSWORD"]

# TAKE A USERNAME AND PASSWORD AND SIGN-IN TO SHOPGOODWILL IN BROWSER
def SignIn(browser, username: str, password: str) -> None:
    # SIGNING IN PAGE TAKES TIME TO LOAD SO KEEP TRYING TO SIGN IN UNTIL WE GET REDIRECTED
    while browser.current_url == BASE_URL + "signin":
        # KEEP TRYING, IF A ELEMENT HASN'T LOADED IN YET RETRY
        try:
            if VERBOSE:
                print("Attempting to sign in...")
            usernameInput = browser.find_element(By.ID, "txtUserName")
            usernameInput.clear()
            usernameInput.send_keys(username)
            passwordInput = browser.find_element(By.ID, "txtPassword")
            passwordInput.clear()
            passwordInput.send_keys(password)
            signInBtn = browser.find_element(By.XPATH, "//button[text()='Sign In']")
            signInBtn.click()
            if VERBOSE:
                print("Signed In")
        except:
            pass

# TAKE A ITEM ID AND MAX BID AND BID ON ITEM
def PlaceBid(browser, item_id: int, bid: float) -> None:
    browser.get(BASE_URL + "item/" + str(item_id))
    while(True):
        try:
            if VERBOSE:
                print("Attempting to make bid...")
            app_root = browser.find_element(By.CSS_SELECTOR, "app-root")
            app_layout = app_root.find_element(By.CSS_SELECTOR, "app-layout")

            minBidDiv = app_layout.find_element(By.CLASS_NAME, "px-0")
            minBid = minBidDiv.find_element(By.XPATH, "//p[contains(text(), '$')]").text
            minBid = float(minBid[1:])

            if bid >= minBid:
                currentBidInput = app_layout.find_element(By.ID, "currentBid")
                currentBidInput.clear()
                currentBidInput.send_keys(str(bid))

                placeBidBtn = app_layout.find_element(By.XPATH, "//*[contains(text(), 'Place My Bid')]")
                placeBidBtn.click()

                confirmBidModal = app_layout.find_element(By.CLASS_NAME, "p-dialog-footer")
                modalPlaceBidBtn = confirmBidModal.find_element(By.CLASS_NAME, "btn-primary")
                if not TESTING_MODE:
                    modalPlaceBidBtn.click()
                if VERBOSE:
                    print("Bid made! :)")
            else:
                if VERBOSE:
                    print(f"Mininium bid ({minBid}) was higher than max bid ({bid}) :(")
            break
        except:
            break

def main():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    signedIn = False
    
    while(True):
        sleep(5)
        items_to_remove = []
        for i in range(0, len(ITEMS)):
            item = ITEMS[i]
            now = datetime.now()
            end_time = datetime.strptime(item["END_TIME"], '%m/%d/%Y %H:%M:%S %p PT')

            if now + timedelta(seconds=TIME_LEFT_UNTIL_BID) >= end_time:
                if not signedIn:
                    browser= webdriver.Chrome(options=chrome_options)
                    browser.get('https://shopgoodwill.com/signin')

                    try:
                        acceptCookiesBtn = browser.find_element(By.CLASS_NAME, "cc-dismiss")
                        acceptCookiesBtn.click()
                    except:
                        print("Failed to click accept cookies button...")

                    SignIn(browser, EMAIL, PASSWORD)
                    signedIn = True
                
                if VERBOSE:
                    print(f"Biding on item #" + str(item["ID"]))
                PlaceBid(browser, item["ID"], item["MAX_BID"])
                items_to_remove.append(i)

        for item_num in items_to_remove:
            ITEMS.pop(item_num)

if __name__ == "__main__":
    main()