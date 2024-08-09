from fastapi import FastAPI, Response


class API:
    api = FastAPI()

    @api.get("/")
    async def root():
        try:
            rssfeed = open("mailing-list.rss")
            return Response(content=rssfeed.read(), media_type="application/xml")
        except FileNotFoundError as e:
            return {"FileNotFound": f"{e}"}
