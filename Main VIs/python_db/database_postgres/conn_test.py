import asyncpg, asyncio
conn = asyncio.run(asyncpg.connect(
        host='cmsmac04.phys.cmu.edu',
        password='hgcal',
        database='postgres',
        user='postgres'
        ))
print('Connection succesful!')