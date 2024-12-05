from ldap3 import Connection, Server, Tls
import ssl
import psycopg2
from psycopg2.extensions import AsIs
import six.moves.configparser as ConfigParser
import sys

# Other connect info in pgpass or pg_service file
DBCONNECTSTR = "dbname='iam_reporting'"

FILTER = '(|(objectclass=user)(objectclass=person))'
ATTRIBUTES = ['samaccountname','lastlogontimestamp','mail','useraccountcontrol','department','pwdlastset','memberof','whencreated','whenchanged','accountexpires','sn','givenName']

def get_ad_config(domain):
  config_filename = f"{sys.argv[0].split('.')[0]}.conf"
  config = ConfigParser.ConfigParser()
  config.read(config_filename)
  ad_config = dict(config.items(domain))
  return (ad_config['searchbase'],ad_config['dc_hostname'],ad_config['binddn'], ad_config['password'] )

# Transform an Active Directory entry into a format that is useful
# for SQL queries.
# Store everything in a dictionary
def process_ad_record(rec):
    db_dict = {}
    if not 'attributes' in rec.keys():
        return None
    if rec['attributes']['samaccountname']:
        db_dict['dn'] = rec['dn']
        for attr in ATTRIBUTES:
            if rec['attributes'][attr]:
                if attr == 'useraccountcontrol':
                    db_dict['isdisabled'] = bool(int(rec['attributes'][attr]) & 2)
                elif attr in ['lastlogontimestamp','accountexpires','pwdlastset','whencreated','whenchanged']:
                    if (rec['attributes'][attr].year != 9999 and rec['attributes'][attr].year != 1601):
                        db_dict[attr] = rec['attributes'][attr]
                else:
                    db_dict[attr] = rec['attributes'][attr]
    return db_dict

def update_databases(conn,domain,data):
    trunc_str = f"DELETE FROM ad_user WHERE domain = '{domain}';"
    drop_idx = f"DROP INDEX ad_user_memberof_idx;"
    create_idx = f"CREATE INDEX ad_user_memberof_idx ON ad_user USING gin (memberof);"
    insert_str = 'INSERT INTO ad_user (%s) values %s;' % ("%s","%s")
    if len(data) > 0:
        cur = conn.cursor()
        print('Truncating entries from table ad_user.')
        cur.execute(trunc_str)
        cur.execute(drop_idx)
        cur.close()

        cur = conn.cursor()
        print('Inserting entries into table ad_user.')
        for entry in data:
            entry["domain"] = f"{domain}"
            columns = entry.keys()
            values = [entry[column] for column in columns]
            cur.execute(insert_str, (AsIs(','.join(columns)), tuple(values)))
            #print(cur.mogrify(insert_str, (AsIs(','.join(columns)), tuple(values))))

        conn.commit()
        cur.close()

        # Create the GIN index for the memberof array
        cur = conn.cursor()
        cur.execute(create_idx)
        conn.commit()
        cur.close()
    else:
        print(f"No data to update for table ad_user. Skipping.")

# Fetch all of the data we want from Active Directory and populate 
# data structures for insertion into the relational database.

if __name__ == "__main__":

    if not len(sys.argv) == 2:
        print(f"Usage: {sys.argv[0]} <domain>")
        quit()
    AD_DOMAIN = sys.argv[1]
    tls = Tls(validate=ssl.CERT_NONE)
    numentries = 0
    insert_list = []
    SEARCHBASE,AD_SERVER,BINDDN,PASSWD = get_ad_config(AD_DOMAIN)
    print('Opening connection to DC for',AD_DOMAIN)
    with Connection(Server(AD_SERVER, tls=tls), BINDDN, PASSWD, auto_referrals=False, auto_bind=True) as conn:
        cookie = ""
        print('Fetching AD data...')
        while True:
            conn.search(SEARCHBASE, FILTER, attributes=ATTRIBUTES, paged_size=999, paged_cookie = cookie)
            for entry in conn.response:
                db_dict = process_ad_record(entry)
                if db_dict:
                    insert_list.append(db_dict)
            cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            if not cookie:
                break
    conn.unbind()
    print('All done collecting AD data.')

    print('Connecting to PostgreSQL service.')
    try:
        pg_conn = psycopg2.connect(DBCONNECTSTR)
    except:
        print("I am unable to connect to the database.")

    print(f"Updating ad_user with {len(insert_list)} rows.")
    update_databases(pg_conn, AD_DOMAIN, insert_list)
    pg_conn.close()
