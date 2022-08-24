import json
import re
import threading
import time

import requests

from com.interface.base import BaseData


class GetNoFreeIp(BaseData):
    def __init__(self):
        super().__init__()
        self.time_kill = []
        self.http_ip = None

    def time_kill_thread(self, _time=5):
        _count = 0
        while _count < 2:
            time.sleep(_time)
            try:
                second = self.ping(self.http_ip, unit='ms', timeout=5)
                # print(second)
                if second and second > 1000.0:
                    self.time_kill.clear()
                    # print(self.http_ip, "挂了")
                    break
                elif not second:
                    self.time_kill.clear()
                    _count += 1
                elif second:
                    _count -= 1

            except Exception:
                self.time_kill.clear()
                break

    def get_nofree(self, url=None):
        """
        返回txt 格式：
        27.153.5.211:22271
        只支持单个
        """
        try:
            if self.time_kill:
                return self.time_kill[0]

            if url is None:
                url = self.api_url
                if not self.api_url:
                    return -1
            if not self.time_kill:
                time.sleep(0.8)
                reps = requests.get(url,
                                    headers=self.user_agent, verify=False, timeout=20)
                # 设置编码
                reps.encoding = "utf-8"
                re1 = reps.text
                # 正则表达式
                # 分别是IP，端口，类型，国家
                re_ip = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
                re_port = re.compile(r':(\d{2,6})')
                self.http_ip = re_ip.findall(re1)[0]
                http_port = re_port.findall(re1)[0]
                if not self.time_kill:
                    self.time_kill.append("{}://{}:{}".format("http", self.http_ip, http_port))
                    t = threading.Thread(target=self.time_kill_thread)
                    t.start()
                    return self.time_kill[0]
                else:
                    return -1
            else:
                return self.time_kill[0]

        except Exception as e:
            self.log_write(
                "异常问题，com-->ipS-->get_nofree.py: " + f'<em style="color: rgb(255, 0, 0); font-weight: bolder">{str(e)}</em>')