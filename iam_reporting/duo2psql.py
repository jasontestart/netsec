import my_duo_client
import datetime
import psycopg2

#Some 'globals'
ATTRIBUTES = ['username','is_enrolled','status','created','last_login','phones']
PHONE_ATTRIBUTES = ['number', 'capabilities', 'platform', 'type']
IGNORE_ACCOUNTS = '!~'
DBCONNECTSTR = "dbname='iam_reporting'"
TRUNCSTR = 'TRUNCATE ONLY duo_user;'
INSERTSTR = 'INSERT INTO duo_user (username,is_enrolled,status,created,last_login) values (%(username)s,%(is_enrolled)s,%(status)s,%(created)s,%(last_login)s);'
PHONE_TRUNCSTR = 'TRUNCATE ONLY duo_phone;'
PHONE_INSERTSTR = 'INSERT INTO duo_phone (number, username, capabilities, platform, type) values (%(number)s,%(username)s,%(capabilities)s,%(platform)s,%(type)s);'

print('Fetching Duo user database via Duo Admin API.')
admin_api = my_duo_client.my_admin_api()
admin_api.set_proxy('myproxy.example.com',3128)
users = admin_api.get_users()
print('Done.')

print('Processing attributes I care about.')

insertions = []
phones = []
for user in users:
    user_dict = {}
    if user['status'] == 'active' and user['username'][0] not in IGNORE_ACCOUNTS:
        for key in ATTRIBUTES:
            if user[key]:
                if key in ['created','last_login']:
                    user_dict[key] =  datetime.datetime.fromtimestamp(user[key])
                elif key == 'phones':
                    for dev in user['phones']:
                        phone_dict = {}
                        phone_dict['username'] = user['username']
                        for dev_key in PHONE_ATTRIBUTES:
                            phone_dict[dev_key] = dev[dev_key]
                        phones.append(phone_dict)
                else:
                    user_dict[key] = user[key]
            else:
                user_dict[key] = None
        insertions.append(user_dict)
print('Done.')

print('Connecting to PostgreSQL database.')
try:
    conn = psycopg2.connect(DBCONNECTSTR)
except:
    print("I am unable to connect to the database.")

if len(insertions) > 0:
    print('Updating database with Duo user data.')
    cur = conn.cursor()
    cur.execute(TRUNCSTR)
    cur.close()

    cur = conn.cursor()
    cur.executemany(INSERTSTR,insertions)
    cur.close()

if len(phones) > 0:
    print('Updating database with Duo phone data.')
    cur = conn.cursor()
    cur.execute(PHONE_TRUNCSTR)
    cur.close()

    cur = conn.cursor()
    cur.executemany(PHONE_INSERTSTR,phones)
    cur.close()
else:
    print('Nothing to update.')

conn.commit()
conn.close()

print('All done!')
