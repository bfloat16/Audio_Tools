import base64
import json
import requests
import sys
import threading

from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo
from volcengine.base.Service import Service

ACCESS_KEY = ''
SECRET_KEY = ''
APPKEY = ''
AUTH_VERSION = 'volc-auth-v1'

class SAMIService(Service):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(SAMIService, "_instance"):
            with SAMIService._instance_lock:
                if not hasattr(SAMIService, "_instance"):
                    SAMIService._instance = object.__new__(cls)
        return SAMIService._instance

    def __init__(self):
        self.service_info = SAMIService.get_service_info()
        self.api_info = SAMIService.get_api_info()
        super(SAMIService, self).__init__(self.service_info, self.api_info)

    @staticmethod
    def get_service_info():
        api_url = 'open.volcengineapi.com'
        service_info = ServiceInfo(api_url, {}, Credentials('', '', 'sami', 'cn-north-1'), 10, 10)
        return service_info

    @staticmethod
    def get_api_info():
        api_info = {"GetToken": ApiInfo("POST", "/", {"Action": "GetToken", "Version": "2021-07-27"}, {}, {}),}
        return api_info

    def common_json_handler(self, api, body):
        params = dict()
        try:
            body = json.dumps(body)
            res = self.json(api, params, body)
            res_json = json.loads(res)
            return res_json
        except Exception as e:
            res = str(e)
            try:
                res_json = json.loads(res)
                return res_json
            except:
                raise Exception(str(e))


if __name__ == '__main__':
    sami_service = SAMIService()
    sami_service.set_ak(ACCESS_KEY)
    sami_service.set_sk(SECRET_KEY)

    req = {"appkey": APPKEY, "token_version": AUTH_VERSION, "expiration": 3600}
    resp = sami_service.common_json_handler("GetToken", req)
    try:
        token = resp["token"]
        print("response task_id=%s status_code=%d status_text=%s expires_at=%s\n\t token=%s" %(resp["task_id"], resp["status_code"], resp["status_text"],resp["expires_at"], token))
    except:
        print("get token failed, ", resp)
        sys.exit(1)

    model = "bs_4track_vocal"
    payload = json.dumps({"model": model})
    with open(r"C:\Users\bfloat16\Desktop\Music\only my railgun.flac", "rb") as f:
        data = f.read()
        data = base64.b64encode(data).decode('utf-8')
    req = {"appkey": "nMYMaXjBNo", "token": token, "namespace": "MusicSourceSeparate", "payload": payload, "data": data}
    resp = requests.post("https://sami.bytedance.com/api/v1/invoke", json=req)
    try:
        sami_resp = resp.json()
        if resp.status_code != 200:
            print(sami_resp)
            sys.exit(1)
    except:
        print(resp)
        sys.exit(1)

    print("response task_id=%s status_code=%d status_text=%s" %(sami_resp["task_id"], sami_resp["status_code"], sami_resp["status_text"]), end=" ")

    if "payload" in sami_resp and len(sami_resp["payload"]) > 0:
        print("payload=%s" % sami_resp["payload"], end=" ")

    if "data" in sami_resp and len(sami_resp["data"]) > 0:
        data = base64.b64decode(sami_resp["data"])
        print("data=[%d]bytes" % len(data))
        with open("output.wav", "wb") as f:
            f.write(data)