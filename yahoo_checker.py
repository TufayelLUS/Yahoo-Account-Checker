import requests
import re
from tkinter import *
import tkinter.scrolledtext as scrolledtext
import threading
from time import sleep
from random import choice


# function for checking the availability
def userExists(username, s):
    print("Checking the availability of {}".format(username))
    link = 'https://login.yahoo.com/account/create?.intl=us&.lang=en-US&src=ym&activity=ybar-mail&pspid=2023538075&.done=https%3A%2F%2Fmail.yahoo.com%2Fd%3Fpspid%3D2023538075%26activity%3Dybar-mail&specId=yidReg&done=https%3A%2F%2Fmail.yahoo.com%2Fd%3Fpspid%3D2023538075%26activity%3Dybar-mail'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    try:
        resp = s.get(link, headers=headers).text
    except:
        print("Failed to open {}".format(link))
        return None
    specData = re.findall(r'value="(.*?)" name="specData"', resp)[0]
    crumb = re.findall(r'value="(.*?)" name="crumb"', resp)[0]
    acrumb = re.findall(r'value="(.*?)" name="acrumb"', resp)[0]
    sessionIndex = re.findall(r'value="(.*?)" name="sessionIndex"', resp)[0]
    link = "https://login.yahoo.com/account/module/create?validateField=yid"
    headers = {
        'Referer': 'https://login.yahoo.com/account/create?.intl=us&.lang=en-US&src=ym&activity=ybar-mail&pspid=2023538075&.done=https%3A%2F%2Fmail.yahoo.com%2Fd%3Fpspid%3D2023538075%26activity%3Dybar-mail&specId=yidReg&done=https%3A%2F%2Fmail.yahoo.com%2Fd%3Fpspid%3D2023538075%26activity%3Dybar-mail',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = {
        'browser-fp-data': '{"language":"en-US","colorDepth":24,"deviceMemory":8,"pixelRatio":1,"hardwareConcurrency":4,"timezoneOffset":-360,"timezone":"Asia/Dhaka","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"1","plugins":{"count":3,"hash":"e43a8bc708fc490225cde0663b28278c"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc. (Intel)~ANGLE (Intel, Intel(R) HD Graphics 520 Direct3D11 vs_5_0 ps_5_0, D3D11-20.19.15.4380)","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":49,"hash":"411659924ff38420049ac402a30466bc"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1624081774716,"render":1624081773747}}',
        'specId': 'yidregsimplified',
        'cacheStored': '',
        'crumb': crumb,
        'acrumb': acrumb,
        'sessionIndex': sessionIndex,
        'done': 'https://mail.yahoo.com/d?pspid=2023538075&activity=ybar-mail',
        'googleIdToken': '',
        'authCode': '',
        'attrSetIndex': '0',
        'specData': specData,
        'multiDomain': '',
        'tos0': 'oath_freereg|us|en-US',
        'firstName': '',
        'lastName': '',
        'userid-domain': 'yahoo',
        'userId': username,
        'password': '',
        'phone': '',
        'mm': '',
        'dd': '',
        'yyyy': '',
        'signup': '',
    }
    try:
        resp = s.post(link, headers=headers, data=data).json()
    except:
        print("Failed to open {}".format(link))
        return None
    print(resp)
    all_errors = resp.get('errors', [])
    if len(all_errors) == 0:
        return None
    for errors in all_errors:
        if errors.get('name') == "userId":
            # print(errors.get('error'))
            return True
    return False


# support function to create a separate thread from main thread
def startChecker2(textBox, proxy_textbox, status_label, submitBtn, s):
    all_lines = textBox.get('1.0', END).split('\n')
    all_proxies = proxy_textbox.get('1.0', END).split('\n')
    submitBtn.config(state=DISABLED)
    selected_proxy = choice(all_proxies)
    if selected_proxy.strip() != "":
        s.proxies = {
            'http': selected_proxy,
            'https': selected_proxy,
        }
    status_label.config(text="Checking ...")
    counter = 1
    valid = 0
    invalid = 0
    failed = 0
    for username in all_lines:
        if username.strip() == "":
            continue
        user_status = userExists(username, s)
        if user_status is None:
            print("No correct response returned")
            open("failed.txt", mode='a+', encoding='utf-8').write(username + "\n")
            failed += 1
        else:
            print("User {} exists".format(username)
                  if user_status else "User {} does not exists".format(username))
            if user_status:
                open("invalid.txt", mode='a+',
                     encoding='utf-8').write(username + "\n")
                invalid += 1
            else:
                open("valid.txt", mode='a+',
                     encoding='utf-8').write(username + "\n")
                valid += 1
        status_label.config(text="Processed {} line(s) and found {} valid, {} invalid and, {} failed".format(
            counter, valid, invalid, failed))
        counter += 1
    sleep(5)
    status_label.config(text="Processing Complete. Records are saved in invalid.txt, valid.txt and failed.txt")
    submitBtn.config(state=NORMAL)


# main program class definition
class YahooChecker():

    s = requests.Session()

    def __init__(self):
        self.createMainWindow()

    def createMainWindow(self):
        root = Tk()
        root.title("Yahoo Username Checker 2023 Edition - Made by Tufayel")
        root.resizable(False, False)
        root.geometry("800x550")

        main_frame = Frame(root)
        main_frame.pack(expand=True, fill='x')

        put_label = Label(
            main_frame, text="Type or paste your list of usernames below: ", font=('', 15, 'normal'))
        put_label.pack()

        textBox = scrolledtext.ScrolledText(main_frame, height=15, undo=True)
        textBox.pack(expand=True, fill='both', padx=10, pady=10)

        proxy_label = Label(
            main_frame, text="Type or paste your proxy list below(http://username:password@ip:port formats only): ", font=('', 15, 'normal'))
        proxy_label.pack()
        proxy_textbox = scrolledtext.ScrolledText(main_frame, height=5, undo=True)
        proxy_textbox.pack(expand=True, fill='both', padx=10, pady=10)

        submitBtn = Button(main_frame, text="Start Checking",
                           relief=GROOVE, font=('', 10, 'normal'), command=lambda: self.startChecker(textBox, proxy_textbox, status_label, submitBtn))
        submitBtn.pack(padx=10, pady=10)

        status_label = Label(root, text="Status: IDLE",
                             font=('', 10, 'normal'))
        status_label.config(fg='blue')
        status_label.pack(side=LEFT, padx=5, pady=5)

        root.mainloop()

    def startChecker(self, textBox, proxy_textbox, status_label, submitBtn):
        th = threading.Thread(target=startChecker2, args=(
            textBox, proxy_textbox, status_label, submitBtn, self.s))
        th.daemon = True
        th.start()


if __name__ == "__main__":
    # main program instance
    checker = YahooChecker()
