import requests
from typing import *
import json

def get_problems(tags:Union[None,List[str]]=None):
    if tags:
        res=requests.get(f'https://codeforces.com/api/problemset.problems?{';'.join(tags)}')
    else:
        res=requests.get('https://codeforces.com/api/problemset.problems')
    return res.json()['result']['problems']

def get_user_rating(id:str):
    res=requests.get(f'https://codeforces.com/api/user.rating?handle={id}')
    data=res.json()
    ratings = [contest["newRating"] for contest in data["result"]]
    current_rating = ratings[-1]
    max_rating = max(ratings)
    return (max_rating,current_rating)

def get_user_problems(cf_id: str, time: int=60 * 60 * 24 * 7):
    parsed_data = requests.get(
        f"https://codeforces.com/api/user.status?handle={cf_id}").json()
    results = parsed_data["result"]
    current_time = max(item["creationTimeSeconds"] for item in results)
    recent_submissions = [
        item
        for item in results
        if current_time - item["creationTimeSeconds"] <= time
        and item["verdict"] == "OK"
    ]
    recent_submissions = {
        (item["problem"]["contestId"], item["problem"]["index"]): item
        for item in recent_submissions
    }.values()
    total_count = len(recent_submissions)
    ratings = [
        item["problem"]["rating"]
        for item in recent_submissions
        if "rating" in item["problem"]
    ]
    average_rating = int(sum(ratings) / len(ratings) if ratings else None)
    return (total_count, average_rating if average_rating is not None else 0)