# A-Soul Comment database

```text
Please Notice that all copyright belongs to ByteDance Inc.,
take care when dealing with the data you get/receive while using this repo. 
```

## Notice:

### React developer wanted!

This repo is requesting react developer to join us `@Github/Asoul-au` origination.

Currently, it's using `Typescript & React` to create a modern web page using `@microsoft/fluentui`

The web page is still under development in private repo, you'll be able to see it after joining us!

### Python backend developer... wanted!

We are currently working on a `server-backend` using python (in this repo, see `server.py`)

Python developer with FastAPI experience is wanted.

### Contact Info:

If you are interested in joining us, contact me at `tiankaima@163.com`.

We would prefer experienced developer, but as the project is still at its early age, you can join us to make this
project better.

## Instructions:

### Setup guide:

First make sure you have `python>=3.7` installed with `pip>=20.0`, install dependencies
using `pip install -r requirements.txt`

Then fetch the data from `bilibili` using this command: `python3 main.py --fetch`

This will automatically fetch all data from the server and integrate it into the `storage.db` file.

Notice on branch `build`, the `storage.db` is provided, so you can simply `git checkout build`

Now you can start running other commands:

### Update database:

`python3 main.py --update`, this will update the `storage.db` file with the following rules:

1. fetch all video list and dynamic list from uids registered in `uids` defined in `tools/fetch.py`
2. check the `time` attribute in the list, if the video/dynamic is posted a week ago, skip it.
   > this is to reduce stress on the server, you can instead run `--update-all` to override this rule
3. fetch all comments from the videos/dynamic list, and copy them into the `storage.db`
   > existing comments would be updated with the new-fetched data, however if it's deleted, we can't tell

### Run API server:

`python3 main.py --start-server`, this would start a `uvicorn` server running default at `127.0.0.1:8000`
, change it using`--ip` and `--port` options.

### Run QQ bot:

`python3 main.py --start-bot`, a QQ bot is started with config files provided in `\bot` dir.

### Test commands:

`python3 main.py --test`, remained for testing purposes, not for debug reasons.