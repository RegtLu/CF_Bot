import cf_api
import json
from peewee import *

db = SqliteDatabase('db/codeforces.sqlite')

class BaseModel(Model):
    class Meta:
        database = db

class Config(BaseModel):
    last_update=DateTimeField()

class Problems(BaseModel):
    contestId=IntegerField(null=True)
    c_index=CharField(null=True)
    name=CharField()
    rating=IntegerField(null=True)
    tags=TextField()
    class Meta:
        primary_key = CompositeKey('contestId', 'c_index')

class Members(BaseModel):
    name=CharField()
    cf_id=CharField()
    rating=IntegerField()
    max_rating=IntegerField()

def init_db():
    """
    初始化数据库
    """
    db.connect()
    db.create_tables([Config,Problems,Members])

def update_problem_db():
    """
    更新题库数据
    """
    def process_json_list(json_list):
        processed_data = []
        for json_data in json_list:
            data = {
                "contestId": json_data.get("contestId"),
                "index": json_data.get("index"),
                "name": json_data.get("name"),
                "rating": json_data.get("rating"),
                "tags": ", ".join(json_data.get("tags", []))
            }
            processed_data.append(data)
        return processed_data
    datas = process_json_list(cf_api.get_problems())
    with db.atomic():
        for batch in chunked(datas, 100):
            Problems.insert_many(batch).execute()

def add_member(name:str,cf_id:str):
    """
    添加成员(暂时无验证;允许一人多id)
    """
    maxrating,rating=cf_api.get_user_rating(cf_id)
    Members.insert(name=name,cf_id=cf_id,max_rating=maxrating,rating=rating).execute()

def update_members():
    """
    更新所有成员的 rating 和 max_rating
    """
    members = Members.select()
    for member in members:
        maxrating, rating = cf_api.get_user_rating(member.cf_id)
        Members.update(
            rating=rating,
            max_rating=maxrating
        ).where(Members.id == member.id).execute()

def get_user_record(name: str,time:int=60 * 60 * 24 * 7):
    """
    获取最近的过题数
    """
    cf_id=Members.select().where(Members.name == name).order_by(Members.cf_id).first().cf_id    #仅获取name对应的第一个cf_id
    total_count, average_rating =cf_api.get_user_problems(cf_id,time)
    return total_count, average_rating

def get_all_members_records(time: int = 60 * 60 * 24 * 7):
    """
    返回所有成员的 name, cf_id, total_count, average_rating 的列表
    :param time: 时间范围,默认是最近7天
    :return: 一个包含所有成员记录的列表，每个记录是一个字典
    """
    members_records = []
    members = Members.select()
    for member in members:
        cf_id = member.cf_id
        total_count, average_rating = cf_api.get_user_problems_by_time(cf_id, time)
        members_records.append([member.name,cf_id,total_count,average_rating])
    return members_records


init_db()
print(get_all_members_records())