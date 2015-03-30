#!/usr/bin/env python

import boto

# Exports LIMIT records from each DynamoDB table into separate CSV files along with headers
# Author Eugene Taranov <eugene@taranov.me>

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

LIMIT = 100

def main():
    if AWS_SECRET_ACCESS_KEY != '' and AWS_ACCESS_KEY_ID != '':
        conn = boto.connect_dynamodb(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    else:
        conn = boto.connect_dynamodb()
    tables = conn.list_tables()

    for table in tables:
        res = conn.get_table(table).scan().response

        rows = res['Items'][0:LIMIT]
        headers = []

        # creating full list of headers
        for row in rows:
            for key in row.keys():
                if key not in headers:
                    headers.append(key)

        # adding missing keys to the rows
        for row in rows:
            for header in headers:
                if header not in row.keys():
                    row[header] = ''

        lines = []
        for row in rows:
            line = []
            for header in headers:
                line.append(str(row[header]))
            lines.append(line)

        with open('%s.csv' % table, 'w') as f:
            f.write( '"%s"\n' % '", "'.join( headers ) )
            for line in lines:
                f.write('"%s"\n' % '", "'.join( line ))


if __name__ == '__main__':
    main()
