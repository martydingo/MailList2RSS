from argparse import ArgumentParser
from yaml import safe_load
from threading import Thread
import uvicorn
from .API import API
from . import MailList2RSS

argument_setup = ArgumentParser()
argument_setup.add_argument("-c", "--config", default="config.yaml")
arguments = argument_setup.parse_args()

configuration = safe_load(open(arguments.config))


def start_api():
    uvicorn.run(API.api)


def start_rss_generation(configuration):
    MailList2RSS(configuration)


apiThread = Thread(target=start_api)
rssThread = Thread(
    target=start_rss_generation, args=(), kwargs={"configuration": configuration}
)

rssThread.start()
apiThread.start()
