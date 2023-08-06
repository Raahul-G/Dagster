from dagster import asset
from dagster import ResourceParam
from github import Github

@asset
def github_stargazers(github_api: ResourceParam[Github]):
    return list(
        github_api.get_repo("dagster-io/dagster").get_stargazers_with_dates()
    )

import pandas as pd
from datetime import timedelta

@asset()
def github_stargazers_by_week(github_stargazers):
    df = pd.DataFrame(
        [
            {
                "users": stargazer.user.login,
                "week": stargazer.starred_at.date()
                + timedelta(days=6 - stargazer.starred_at.weekday()),
            }
            for stargazer in github_stargazers
        ]
    )
    return df.groupby("week").count().sort_values(by="week")

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import pickle
import jupytext

@asset()
def github_stars_notebook(github_stargazers_by_week):
    markdown = f"""
# Github Stars

```python
import pickle
github_stargazers_by_week = pickle.loads({pickle.dumps(github_stargazers_by_week)!r})

## Github Stars by Week, last 52 weeks

github_stargazers_by_week.tail(52).reset_index().plot.bar(x="week", y="users")

    """
    nb = jupytext.reads(markdown, "md")
    ExecutePreprocessor().preprocess(nb)
    return nbformat.writes(nb)

from github import InputFileContent

@asset()
def github_stars_notebook_gist(context, github_api: ResourceParam[Github], github_stars_notebook):
    gist = github_api.get_user().create_gist(
        public=False,
        files={
            "github_stars.ipynb": InputFileContent(github_stars_notebook),
        },
    )
    context.log.info(f"Notebook created at {gist.html_url}")
    return gist.html_url