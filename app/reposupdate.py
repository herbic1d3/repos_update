import os
import json
import requests
import time

from datetime import datetime

from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server


class ReposUpdate(object):

    def __init__(self):
        self.url = "https://api.github.com/repos/{0}/commits"
        self.repos = os.environ.get("REPOS").split(',')

    def collect(self):
        headers = {'Authorization': 'token {}'.format(os.environ.get("TOKEN", ""))}
        for repo in self.repos:
            try:
                response = requests.get(url=self.url.format(repo),headers=headers, verify=False, stream=False, timeout=5)
            except requests.Timeout:
                continue
            except requests.ConnectionError:
                continue

            data = response.json()
            name = repo.replace('/','_').replace('-', '_')
            commit = data[0]['commit']
            commit_datetime = datetime.strptime(commit['author']['date'], '%Y-%m-%dT%H:%M:%SZ')

            metric = GaugeMetricFamily(
                "repo__{}".format(name),
                "Repo `{}` last commit date".format(repo),
                labels=["commit"])
            metric.add_metric(['timestamp'], commit_datetime.timestamp())
            metric.add_metric(['deltatime'], (datetime.now()-commit_datetime).total_seconds())

            yield metric


if __name__ == "__main__":
    start_http_server(9853)
    REGISTRY.register(ReposUpdate())
    while True:
        time.sleep(1)
