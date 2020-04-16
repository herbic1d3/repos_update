import os
import requests
import time
from datetime import datetime

from prometheus_client.core import InfoMetricFamily, CounterMetricFamily, REGISTRY
from prometheus_client import start_http_server


class ReposUpdate(object):

    def __init__(self):
        self.url = "https://sdk.dfinity.org/manifest.json"
        self.cache = {}
        self.time = time.time()
        self.cache_timeout = float(os.environ.get('CACHE_TIMEOUT', 600))

    def collect(self):
        name = "dfinity"

        if time.time() - self.time > self.cache_timeout:
            self.cache = {}
            self.time = time.time()

        if name not in self.cache:
            try:
                response = requests.get(url=self.url, verify=False, stream=False, timeout=5)
            except requests.Timeout:
                pass
            except requests.ConnectionError:
                pass

            self.cache[name] = response.json()

        metric_counter = CounterMetricFamily(
            "repo__{}__tags_".format(name),
            "Repo `{}` tags total".format(name),
            labels=['tags']
        )
        metric_counter.add_metric([name], len(self.cache[name]["versions"]))
        yield metric_counter

        metric_info = InfoMetricFamily(
            "repo__{}__tag".format(name),
            "Repo `{}` tag".format(name)
        )
        metric_info.add_metric(["tag"], {'name': self.cache[name]["tags"]["latest"]})
        yield metric_info


if __name__ == "__main__":
    start_http_server(9855)
    REGISTRY.register(ReposUpdate())
    while True:
        time.sleep(600)
