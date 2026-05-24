from github import Github
import os


def get_github_client():

    token = os.environ["GITHUB_TOKEN"]

    return Github(token)
