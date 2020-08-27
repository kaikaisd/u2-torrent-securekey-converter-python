#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import requests
import time
import os
from urllib.parse import urlparse

text_message = """
##################################
#    U2 torrent key conventer    #
#       Written by kaikaisd      #
##################################

"""
base_url = "https://u2.dmhy.org/jsonrpc_torrentkey.php"

print(text_message)
apikey = input(
    "請輸入您在U2的apikey (https://u2.dmhy.org/jsonrpc_torrentkey.php?apikey=) : ")
path = input("請輸入你的rtorrent的.sessions的路徑 : ")
headers = {
    'Cache-Control': 'no-store, no-cache, must-revalidate',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache'
}

new_tracker = b"daydream.dmhy.best"
old_tracker = b"tracker.dmhy.org"


def get_torrent_hash():
    u2_torrent = []
    for file in os.listdir(path):
        if file.endswith('.torrent'):
            with open(path+file, 'r+b') as f:
                if 'dmhy' in str(f.read()):
                    u2_torrent.append(file.replace(".torrent", ""))
    u2_torrent.sort()
    return u2_torrent


def request_new_securekey(torrent_hash=get_torrent_hash()):
    print(torrent_hash)
    data = []
    finished_data = []
    for index, torrent in enumerate(torrent_hash):
        print(f'正在處理第 {index+1} 個種子 , 共 {len(torrent_hash)} 個')
        data = {
            "jsonrpc": "2.0",
            "method": "query",
            "params": [torrent],
            "id": index+1,
        }
        req = requests.post(
            base_url, params={"apikey": apikey}, json=data, headers=headers)
        if req.status_code == 403:
            print("API 無效, 請檢查你的APIKEY\nAPI failed, please check your apikey")
            exit()

        if req.status_code == 503:
            while req.status_code == 503:
                wait_sec = int(req.headers["Retry-After"])+5
                print(f"Request too fast, retry in {wait_sec} s")
                time.sleep(wait_sec)
                req = requests.post(
                    base_url, params={"apikey": apikey}, json=data, headers=headers)

        if req.status_code != 200:
            print(f"Error : {req.status_code} Failed")

        rep = req.json()
        print(rep)

        if rep.get('error'):
            print(rep.get('error'))
        else:
            finished_data.append(rep)

    return finished_data


def change_tracker_and_key():
    hash_id = get_torrent_hash()
    change_secure = request_new_securekey()
    result = [u['result'] for u in change_secure]

    for i in range(0, len(hash_id)):
        with open(path+hash_id[i]+".torrent", 'rb+') as file:
            tmp = file.read()
            if old_tracker in tmp:
                tmp.replace(old_tracker, new_tracker)
            get_link = tmp.split(b":")
            old_key = get_link.query.split(b":")[0]
            old_key.replace(old_key, "secure="+result[i])
            file.close()


if __name__ == "__main__":
    change_tracker_and_key()
