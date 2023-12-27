# Arduino Lib registry Overview
# this collects all data
# tokens are needed below! search for token

# 2023 Stephan Martin designer2k2.at

import requests
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
from numpy import random
import re
import time
from ast import literal_eval
from datetime import datetime
import json
from os.path import exists
import os
import pandas as pd
import plotly.express as px


def getregistry():
    url = "https://raw.githubusercontent.com/arduino/library-registry/main/repositories.txt"
    r = requests.get(url, allow_redirects=True)
    open("repositories.txt", "wb").write(r.content)
    print(r.headers)


def simplestats():
    # read in the file
    file1 = open("repositories.txt", "r")
    Lines = file1.readlines()
    Lines2 = [item.replace(".git", "") for item in Lines]
    # do we have duplicate entrys?
    dupes = [item for item, count in Counter(Lines2).items() if count > 1]
    print(f"Dupes: {dupes}")
    # count different base urls and "owners":
    cnt = Counter()
    cnt2 = Counter()
    for line in Lines:
        domain = line.rsplit("/")[2]
        cnt[domain] += 1
        owner = line.rsplit("/")[3]
        cnt2[owner] += 1
    print(cnt)
    print(cnt2)
    # sort from high to low:
    sorted = OrderedDict(cnt2.most_common())
    fig, ax = plt.subplots()
    # bar_container = ax.bar(sorted.keys(), sorted.values())
    # ax.bar_label(bar_container, fmt="{:,.0f}")
    # plt.show()
    bar_container = ax.barh(list(sorted.keys())[:10], list(sorted.values())[:10])
    ax.bar_label(bar_container, fmt="{:,.0f}")
    plt.gca().invert_yaxis()
    ax.set(xlabel="Librarys", title="Owner")
    plt.show()


def runardlog():
    print("test")
    # reads repos
    # read in the file
    # file1 = open("repositories.txt", "r")
    file1 = open("maybe404.txt", "r")
    Lines = file1.readlines()
    file1.close()
    # count different base urls and "owners":
    result = open("repositories2_.txt", "w")
    count = 0
    for line in Lines:
        count += 1
        if count >= 0:  # used for restarting at failure points
            lstr = line.rstrip("\n")
            scan = arduinologcheck(lstr)
            if scan == -1:
                print(f"Something failed, stopping at: {count}")
                break
            result.write(f"{lstr} ,{scan}\n")
            # time.sleep(random.uniform(3.5, 5.5))  # be polite here
        if count % 50 == 0:
            print(f"Progress: {count}")
            # break   # use this for testing
    result.close()
    # runs every repo against arduino lib log
    # stores it in new repo csv file with: URL,[RULES]


def arduinologcheck(url=None):
    if url is None:
        url = "https://github.com/arduino-libraries/Servo"
    # fetch the html
    urlf = transform_source_url(url)
    # print(urlf)
    try:
        r = requests.get(urlf, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"{urlf}:{e}")
        return -1
    # extract the rules, and ensure every rule is only once given
    rules = list(dict.fromkeys(extract_rules(r.text)))
    rcount = count_releases(r.text)
    # print([rcount, rules])
    return [rcount, rules]


def count_releases(text):
    # Use regular expression to find lines containing "Release" followed by a version
    release_pattern = re.compile(r"Release (\S+)")
    releases = release_pattern.findall(text)
    return len(releases)


def extract_rules(text):
    # Use regular expression to find lines containing "Rule" followed by a code
    stext = text.split("Release")[-1]
    rule_pattern = re.compile(r"(Rule [A-Z]+\d+)")
    rules = rule_pattern.findall(stext)
    rules = [s.replace("Rule ", "") for s in rules]
    return rules


def transform_source_url(original_url):
    # Split the URL to extract the username and repository name
    inter = re.sub("\\.git$", "", original_url)
    inter = re.sub("/$", "", inter)
    parts = inter.split("/")
    # Construct the transformed URL
    transformed_url = (
        f"https://downloads.arduino.cc/libraries/logs/{'/'.join(parts[2:])}/"
    )
    return transformed_url


def apiquerylist():
    # run the list and query all apis:
    # read in the file
    file1 = open("repositories.txt", "r")
    Lines = file1.readlines()
    count = 0
    for line in Lines:
        count += 1
        if "github.com" in line:
            if githubapiquery(line.rstrip("\n")) == 1:
                time.sleep(1)
        if "gitlab.com" in line:
            if gitlabapiquery(line.rstrip("\n")) == 1:
                time.sleep(1)
        if count % 50 == 0:
            print(f"Progress: {count}")
            # break   # use this for testing


def gitlabapiquery(url=None):
    if url is None:
        url = "https://gitlab.com/Ama_De/as5200l-arduino"
    url = inter = re.sub("\\.git$", "", url)
    url = re.sub("/$", "", url)
    filestorename = filestorenameconverter(url)
    if exists(filestorename):
        print(f"Skip: {url}")
        return 0
    parts = url.split("/")
    # Construct the transformed URL
    transformed_url = f"https://gitlab.com/api/v4/projects/{'%2F'.join(parts[3:])}"
    token = "glpat-ccccccccccccc" # token needed!

    login = requests.get(transformed_url, headers={"PRIVATE-TOKEN": token}, timeout=10)
    # print(login.json())
    try:
        with open(filestorename, "w") as outfile:
            outfile.write(json.dumps(login.json()))
    except Exception as e:
        print(f"{url}, {e}")
        return -1
    return 1


def githubapiquery(url=None):
    if url is None:
        url = "https://api.github.com/repos/designer2k2/EMUcan"
    # print("fetch github")
    url = re.sub("\\.git$", "", url)
    url = re.sub("/$", "", url)
    filestorename = filestorenameconverter(url)
    if exists(filestorename):
        print(f"Skip: {url}")
        return 0
    # store individual json from github api
    # get it with api key, to have enough querys
    # also check on api usage while doing so.
    # read in the file
    parts = url.split("/")
    # Construct the transformed URL
    transformed_url = f"https://api.github.com/repos/{'/'.join(parts[3:])}"
    token = "github_pat_tokenisneeded"
    username = "yourusername"

    login = requests.get(transformed_url, auth=(username, token), timeout=10)
    # print(login.json())
    try:
        with open(filestorename, "w") as outfile:
            outfile.write(json.dumps(login.json()))
    except Exception as e:
        print(f"{url}, {e}")
        return -1
    if int(login.headers["X-RateLimit-Remaining"]) % 100 == 0:
        print(login.headers)
        resettime = datetime.utcfromtimestamp(
            int(login.headers["X-RateLimit-Reset"])
        ).strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"Querys left: {login.headers['X-RateLimit-Remaining']}, Reset at: {resettime}"
        )
    return 1


def apistats():
    print("apistats")
    # run all jsons and extract
    name = []
    age = []
    stars = []
    lastedit = []
    issues = []
    count = 0
    for file_path in os.listdir("arduinojson"):
        count += 1
        if count % 500 == 0:
            print(count)
        # print(file_path)
        f = open(os.path.join("arduinojson", file_path))
        data = json.load(f)
        try:
            if "github" in file_path:
                # print("github")
                name.append(data["full_name"])
                stars.append(data["stargazers_count"])
                age.append(data["created_at"])
                lastedit.append(data["updated_at"])
                issues.append(data["open_issues_count"])
            if "gitlab" in file_path:
                # print("gitlab")
                name.append(data["name_with_namespace"])
                stars.append(data["star_count"])
                age.append(data["created_at"])
                lastedit.append(data["last_activity_at"])
                issues.append(data["open_issues_count"])
        except KeyError as e:
            # print(f"Not working {file_path}: {e}")
            if "'full_name'" not in str(e):
                print(f"oha {e}")
        f.close()
    DataToUse = pd.DataFrame(
        {
            "name": name,
            "stars": stars,
            "age": age,
            "lastedit": lastedit,
            "issues": issues,
        }
    )
    print("yehas")
    fig = px.scatter(DataToUse, x="age", y="lastedit", hover_data=["name"])
    fig.show()


def filestorenameconverter(url):
    filestorename = url.replace("https://", "").replace("/", ".")
    filestorename = f"arduinojson/{filestorename}.json"
    return filestorename


def combinedstats():
    print("combostats")
    # this merges the lint with the api jsons
    # as it takes some time, the dataframe is stored and reloaded if it exists
    dfpickle = "arduino_lib_api_df.pkl"
    if os.path.exists(dfpickle):
        DataToUse = pd.read_pickle(dfpickle)
    else:
        file1 = open("repositories2.txt", "r")
        Lines = file1.readlines()
        name = []
        age = []
        stars = []
        lastedit = []
        issues = []
        releases = []
        lint = []
        # count different releases and issues
        for line in Lines:
            url = line.rsplit(" ,")[0]
            lintdata = literal_eval(line.rsplit(" ,")[1].replace("\n", ""))
            try:
                f = open(filestorenameconverter(url))
                data = json.load(f)
                f.close()
                # name.append(url)
                if "github" in url:
                    # print("github")
                    name.append(data["full_name"])
                    stars.append(data["stargazers_count"])
                    age.append(data["created_at"])
                    lastedit.append(data["updated_at"])
                    issues.append(data["open_issues_count"])
                if "gitlab" in url:
                    # print("gitlab")
                    name.append(data["name_with_namespace"])
                    stars.append(data["star_count"])
                    age.append(data["created_at"])
                    lastedit.append(data["last_activity_at"])
                    issues.append(data["open_issues_count"])
                releases.append(lintdata[0])
                lint.append((lintdata[1]))
            except Exception as e:
                # print(f"nono {e} at {url}")
                pass
        print("ui")
        DataToUse = pd.DataFrame(
            {
                "name": name,
                "stars": stars,
                "age": age,
                "lastedit": lastedit,
                "issues": issues,
                "lint": lint,
                "releases": releases,
            }
        )
        DataToUse.to_pickle(dfpickle)
    # calculate extra with how many lint errors:
    DataToUse["lintlen"] = DataToUse["lint"].str.len()

    FilterData = DataToUse[DataToUse["releases"] == 0]

    # Filter for a specific Lint error:
    FilterData = DataToUse.loc[("LD005" in c for c in DataToUse["lint"])]
    FilterData.sort_values("stars", ascending=False)

    print("done")
    fig = px.scatter(
        FilterData,
        x="age",
        y="lastedit",
        color="lintlen",
        hover_data=["name", "lint", "stars", "issues", "releases"],
        color_continuous_scale=px.colors.qualitative.Dark2,
    )
    fig.update_layout(
        title="Arduino Library Register",
        yaxis_title="Last change",
        xaxis_title="Creation date",
        coloraxis_colorbar_title_text="Errors",
    )
    fig.show()
    # this should have with lintlen green for 0, yellow for 1-3 and red for 4 up


if __name__ == "__main__":
    # getregistry()
    # simplestats()
    # runardlog()
    # apiquerylist()
    # apistats()
    combinedstats()
