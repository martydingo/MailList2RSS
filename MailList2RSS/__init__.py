from office365.graph_client import GraphClient
from pprint import pprint
from feedgen.feed import FeedGenerator
import datetime
import markdown
import datetime
import time
import asyncio
from fastapi import Response, FastAPI
from yaml import safe_load

# from .API


class MailList2RSS:
    def __init__(self, configuration) -> None:
        method = configuration["method"]
        self.configuration = configuration[method]
        if method == "office365":
            self.__start_polling_o365__()

    def __setup_office365__(self):
        self.client = GraphClient.with_client_secret(
            tenant=self.configuration["tenant_id"],
            client_id=self.configuration["client_id"],
            client_secret=self.configuration["client_secret"],
        )

    def __start_polling_o365__(self):
        self.__setup_office365__()
        print("Running initial poll")
        self.__poll_office365__()
        while True:
            if datetime.datetime.now().minute % 10 == 0:
                print(f"{datetime.datetime.now()}: Polling O365")
                self.__poll_office365__()

    def __poll_office365__(self):
        messages = (
            self.client.users[self.configuration["inbox"]]
            .mail_folders[self.configuration["folder_id"]]
            .messages.get_all()
            .execute_query()
        )
        rss_feed = FeedGenerator()
        for message in messages:
            rss_entry = rss_feed.add_entry()
            try:
                mailingListSubjectList = message.subject.split("[")[1].split("]")
                mailingListTopic = mailingListSubjectList[0]
                mailingListSubject = (
                    mailingListSubjectList[1].replace("Re:", "").strip()
                )
            except:
                mailingListTopic = "Unknown"
                mailingListSubject = message.subject

            rss_entry.id(message.web_link)
            rss_entry.link({"href": message.web_link})
            rss_entry.title(message.subject)
            rss_entry.pubDate(
                message.created_datetime.replace(tzinfo=datetime.timezone.utc)
            )
            if message.body.contentType == "text":
                rss_entry.content(markdown.markdown(str(message.body.content)))
            else:
                rss_entry.content(str(message.body.content))
            rss_entry.category({"term": mailingListTopic})
            rss_entry.author = {
                "name": message.sender.emailAddress.name,
                "email": message.sender.emailAddress.address,
            }
            rss_entry.summary = str(message.body_preview)

            contributors = []
            contributors.append(
                {
                    "name": message.sender.emailAddress.name,
                    "email": message.sender.emailAddress.address,
                }
            )
            for contributor in message.to_recipients:
                contributors.append(
                    {
                        "name": contributor.emailAddress.name,
                        "email": contributor.emailAddress.address,
                    }
                )
            for contributor in message.cc_recipients:
                contributors.append(
                    {
                        "name": contributor.emailAddress.name,
                        "email": contributor.emailAddress.address,
                    }
                )
            rss_entry.contributor(contributors)
            # print(rss_entry.__dict__)
            # print(mailingListTopic)
            # print(mailingListSubject)
            # print(contributors)
        rss_feed.title("Mailing Lists")
        rss_feed.description("...")
        rss_feed.link({"href": "dingo.foo"})
        # rssfeed = rss_feed.rss_str(pretty=True)
        # print(rssfeed)
        rssfeed_file = rss_feed.rss_file("mailing-list.rss")
