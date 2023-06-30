import requests
import json


def get_data(url):
    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        }
        req = requests.get(url, headers, timeout=3.1)
        if req:
            res = json.loads(req.text)
        else:
            res = {}
    except requests.exceptions.ConnectTimeout:
        res = {}
    except requests.exceptions.ReadTimeout:
        res = {}
    return res


def get_data_no_timeout(url):
    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        }
        req = requests.get(url, headers)
        if req:
            res = json.loads(req.text)
        else:
            res = {}
    except requests.exceptions.ConnectTimeout:
        res = {}
    except requests.exceptions.ReadTimeout:
        res = {}
    return res


def post_data_no_timeout(url):
    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        }
        req = requests.post(url, headers)
        if req:
            res = json.loads(req.text)
        else:
            res = {}
    except requests.exceptions.ConnectTimeout:
        res = {}
    except requests.exceptions.ReadTimeout:
        res = {}
    return res
