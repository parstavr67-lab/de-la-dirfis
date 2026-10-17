"""One-time importer: SQLite de_la_dirfis.db -> hosted PostgreSQL.
Run only after creating the hosted app/database and backing up the SQLite file.
This importer copies rows from known tables and preserves IDs; it does not delete or modify the SQLite source.
"""
import os, sys, sqlite3
import psycopg
from psycopg import sql

TABLE_ORDER=['dogs','trainings','matings','litters','puppies','clients','transactions']

def main():
    if len(sys.argv)<2:
        print('Usage: python migrate_sqlite_to_postgres.py path\\to\\de_la_dirfis.db')
        raise SystemExit(2)
    source=os.path.abspath(sys.argv[1])
    if not os.path.isfile(source): raise SystemExit(f'Δεν βρέθηκε η βάση: {source}')
    if not os.environ.get('DATABASE_URL'):
        raise SystemExit('Πρώτα όρισε τη μεταβλητή περιβάλλοντος DATABASE_URL με το connection string της νέας βάσης.')
    # Values below only allow importing the app module for its schema initializer; they are not used to log in.
    os.environ.setdefault('SECRET_KEY', 'migration-only-secret-key-do-not-use-for-hosting-123456789')
    os.environ.setdefault('APP_USERNAME', 'migration-only')
    os.environ.setdefault('APP_PASSWORD', 'migration-only-not-for-hosting')
    from app import TABLES, DDL, DATABASE_URL, init_db
    init_db()
    sqlite=sqlite3.connect(f'file:{source}?mode=ro',uri=True)
    sqlite.row_factory=sqlite3.Row
    with psycopg.connect(DATABASE_URL.replace('postgres://','postgresql://',1),sslmode='require') as pg:
        for table in TABLE_ORDER:
            names={r['name'] for r in sqlite.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if table not in names:
                print(f'{table}: δεν υπάρχει στην πηγή, παράλειψη')
                continue
            rows=sqlite.execute(f'SELECT * FROM "{table}"').fetchall()
            if not rows:
                print(f'{table}: 0 εγγραφές')
                continue
            columns=list(rows[0].keys())
            pg.execute(sql.SQL('TRUNCATE TABLE {} RESTART IDENTITY').format(sql.Identifier(table)))
            stmt=sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,columns)),sql.SQL(',').join(sql.Placeholder()*len(columns)))
            with pg.cursor() as cur:
                cur.executemany(stmt,[tuple(row[c] for c in columns) for row in rows])
            pg.execute(sql.SQL("SELECT setval(pg_get_serial_sequence(%s, 'id'), GREATEST(COALESCE((SELECT MAX(id) FROM {}), 1), 1), true)").format(sql.Identifier(table)),(table,))
            print(f'{table}: αντιγράφηκαν {len(rows)} εγγραφές')
    sqlite.close()
    print('Ολοκληρώθηκε η αντιγραφή. Το αρχικό SQLite αρχείο δεν τροποποιήθηκε.')
if __name__=='__main__': main()
