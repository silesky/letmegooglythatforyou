from asyncpg import connect
from settings import *


async def connect_db():
    print('Attempting DB Connection...')
    connection = await connect(
        user=PGUSER,
        database=PGDB,
        host=DB_HOST,
        port=5432
    )
    print('DB Connected!')
    return connection


async def get_access_token_by_team_id(team_id):
    print('got access token by team id:', team_id)
    conn = await connect_db()
    query = "SELECT access_token FROM teams " \
            "WHERE team_id = Cast('{team_id}' as varchar) " \
            .format(team_id=team_id)
    record = await conn.fetch(query)
    if record:
        token = record[0]['access_token']
    else:
        token = False
    await conn.close()
    return token


async def update_or_insert_team_data(team_id, team_name, access_token):
    conn = await connect_db()
    # attempt to insert a new road -- if there's a team id conflict, update the access token
    query = "INSERT into teams(team_id, team_name, access_token) " \
        "VALUES ('{id}', '{name}', '{token}') " \
        "ON CONFLICT (team_id) " \
        "DO UPDATE SET access_token = Cast('{token}' as varchar) " \
            .format(id=team_id, name=team_name, token=access_token)
    response = await conn.execute(query)
    print(response)
    await conn.close()
    return response


async def store_team_data(team_id, team_name, access_token):
    print('store_team_data called.', team_id, team_name, access_token)
    res = await update_or_insert_team_data(team_id, team_name, access_token)
    return res
