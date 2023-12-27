# Arduino Lib registry Overview
# this makes some charts

# 2023 Stephan Martin designer2k2.at

from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import re
import time
from ast import literal_eval
from datetime import datetime
import json
import pandas as pd
import plotly.express as px


def simplestats():
    # read in the file
    file1 = open("repositories.txt", "r")
    Lines = file1.readlines()
    Lines2 = [item.replace(".git", "") for item in Lines]
    # do we have duplicate entries?
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


def somestatsonlint():
    print("Lets get some lint stats")
    # number of releases, from 0 to max, use Counter
    # lint errors overall, use Counter
    file1 = open("repositories3.txt", "r")
    Lines = file1.readlines()
    # count different releases and issues
    cnt = Counter()
    cnt2 = Counter()
    cnt3 = Counter()
    emptys = list()
    for line in Lines:
        content = literal_eval(line.rsplit(" ,")[1])
        cnt[content[0]] += 1
        for x in content[1]:
            cnt2[x] += 1
        if content[0] == 0:
            emptys.append(line.rsplit(" ,")[0])
        if len(content[1]) > 1:
            cnt3["Error"] += 1
        else:
            cnt3["OK"] += 1
    print(cnt)
    print(cnt2)
    print(cnt3)
    print(f"404: {len(emptys)}: {emptys}")
    # sort from high to low:
    sorted = OrderedDict(cnt2.most_common())
    # plt.barh(list(sorted.keys()), sorted.values())
    # plt.gca().invert_yaxis()
    fig, ax = plt.subplots()
    # ax.pie(sorted.values(), labels=sorted.keys(), autopct="%1.1f%%")
    # ax.set(title="Lint check")
    # plt.show()

    bar_container = ax.barh(list(sorted.keys())[:10], list(sorted.values())[:10])
    ax.bar_label(bar_container, fmt="{:,.0f}")
    plt.gca().invert_yaxis()
    ax.set(xlabel="Librarys", title="Lint Errors")
    plt.show()


def combinedstats():
    print("combostats")
    # this merges the lint with the api jsons
    # as it takes some time, the dataframe is stored and reloaded if it exists
    dfpickle = "arduino_lib_api_df.pkl"
    DataToUse = pd.read_pickle(dfpickle)
    # calculate extra with how many lint errors:
    DataToUse["lintlen"] = DataToUse["lint"].str.len()

    FilterData = DataToUse[DataToUse["releases"] == 0]

    # Filter for a specific Lint error:
    FilterData = DataToUse.loc[("LD005" in c for c in DataToUse["lint"])]
    FilterData.sort_values("stars", ascending=False)

    print("done")
    fig = px.scatter(
        DataToUse,  # or use FilterData here
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
    simplestats()
    somestatsonlint()
    combinedstats()
