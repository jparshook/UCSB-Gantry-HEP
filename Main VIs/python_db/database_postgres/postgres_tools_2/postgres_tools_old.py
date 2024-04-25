import os, csv, sys
import asyncio, asyncpg
import numpy as np
from database_postgres.postgres_tools.conn import host, database, user, password
# host, database, user, password = 1,1,1,1

def get_query(table_name):
    if table_name == 'module_assembly':
        pre_query = f""" 
        INSERT INTO {table_name} 
        (module_name, geometry, resolution, proto_name, hxb_name, position, region, ass_tray_id, hxb_tray_id, hxb_put_id, tape_batch, glue_batch, run_date, time_begin, time_end, operator)
        VALUES """
    elif table_name == 'proto_assembly':
        pre_query = f""" 
        INSERT INTO {table_name} 
        (proto_name, geometry, resolution, bp_name, sen_name, position, region, ass_tray_id, sen_tray_id, sen_put_id, tape_batch, run_date, time_begin, time_end, operator)
        VALUES  """
    data_placeholder = ', '.join(['${}'.format(i) for i in range(1, len(pre_query.split(','))+1)])
    query = f"""{pre_query} {'({})'.format(data_placeholder)}"""
    return query

async def upload_PostgreSQL(table_name, db_upload_data):
    conn = await asyncpg.connect(
        host=host,
        database=database,
        user=user,
        password=password)
    
    print('Connection successful. \n')

    schema_name = 'public'
    table_exists_query = """
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = $1 
        AND table_name = $2
    );
    """
    table_exists = await conn.fetchval(table_exists_query, schema_name, table_name)  ### Returns True/False
    if table_exists:
        query = get_query(table_name)
        await conn.execute(query, *db_upload_data)
        print(f'Executing query: {query}')
        print(f'Data successfully uploaded to the {table_name}!')
    else:
        print(f'Table {table_name} does not exist in the database.')
    await conn.close()
    return 'Upload Success'

def get_query_read(component_type):
    if component_type == 'protomodule':
        query = """SELECT proto_name, thickness, geometry, resolution FROM proto_inspect WHERE geometry = 'full'"""    
    elif component_type == 'hexaboard':
        query = """SELECT hxb_name, thickness, geometry, resolution FROM hxb_inspect WHERE geometry = 'full'"""
    elif component_type == 'baseplate':
        query = """SELECT bp_name, thickness, geometry, resolution FROM bp_inspect WHERE geometry = 'full'"""
    else:
        query = None
        print('Table not found. Check argument.')
    return query

comptable = {'baseplate':{'prefix': 'bp'},'hexaboard':{'prefix': 'hxb'},'protomodule':{'prefix': 'proto'},'module':{'prefix': 'module'}}
def get_query_read(component_type, part_name = None, comptable=comptable):
    if part_name is None:
        query = f"""SELECT {comptable[component_type]['prefix']}_name FROM {comptable[component_type]['prefix']}_inspect ORDER BY {comptable[component_type]['prefix']}_row_no DESC LIMIT 10;"""
    else:
        query = f"""SELECT hexplot FROM {comptable[component_type]['prefix']}_inspect WHERE {comptable[component_type]['prefix']}_name = '{part_name}'"""
    return query

async def fetch_PostgreSQL(query):
    conn = await asyncpg.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    value = await conn.fetch(query)
    await conn.close()
    return value

async def request_PostgreSQL(component_type, bp_name = None):
    result = await fetch_PostgreSQL(get_query_read(component_type, bp_name ))
    return result