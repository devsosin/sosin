try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except:
    print('you need to install psycopg2\n$ : python -m pip install psycopg2')

from typing import Iterable

from sosin.databases.db import Database

class PostgreSQL(Database):

    def __init__(self, db_config, cursor_type:str = None):
        """
        cursor_type = 'dict' or None
        """
        db_config['port'] = int(db_config.get('port', '5432'))
        db_config['dbname'] = db_config.pop('database')
        db_config.pop('charset', None)

        if cursor_type == 'dict':
            cursor_type = RealDictCursor
        else:
            cursor_type = None

        super().__init__(db_config, cursor_type)

    def connect(self):
        self.DB = psycopg2.connect(**self.db_config)
        self.cursor = self.DB.cursor(self.cursor_type)
        return self
    
    def custom_select(self, qry):
        return super().select(qry)
    
    def select(self, table, columns, where_info=None, order_by=None, page_info=None):
        """
        table -> should be schema_name.table_name
        """
        query = ''

        if not isinstance(columns, str) and isinstance(columns, Iterable):
            columns = ', '.join(map(str, columns))
        
        query += f'SELECT {columns} FROM {table}'

        if where_info:
            query += self.where(*where_info)

        if order_by:
            query += self.sort(order_by)

        if page_info:
            query += self.pagination(*page_info)

        return super().select(query)
    
    # where equal
    # where between
    # where in
    # where null / not null
    def where(self, column, value, option=None): 
        """
        option IN, IS, ...
        BETWEEN A AND B (VALUES)

        """
        if not option:
            option = '='

        return f'\nWHERE {column} {option} {value}'

    def sort(self, order_by):
        return f"\nORDER BY {order_by}"
    
    def pagination(self, page, size):
        return f'\nLIMIT {size} OFFSET {(page-1)*size}'

    def insert(self, table, columns, value) -> bool:
        if not isinstance(columns, str) and isinstance(columns, Iterable):
            columns = ', '.join(map(str, columns))
        
        assert len(value) == columns.count(',')+1, "칼럼 길이와 값의 길이가 다릅니다. ,를 확인해주세요"

        value_qry = ','.join(['%s'] * len(value))
        query = f'INSERT INTO {table}({columns}) VALUES ({value_qry});'

        return super().insert(query, value)
    
    def insert_many(self, table, columns, values):
        if not isinstance(columns, str) and isinstance(columns, Iterable):
            columns = ', '.join(map(str, columns))
        
        assert len(values[0]) == columns.count(',')+1, "칼럼 길이와 값의 길이가 다릅니다. ,를 확인해주세요"

        value_qry = ','.join(['%s'] * len(values[0]))
        query = f'INSERT INTO {table}({columns}) VALUES ({value_qry});'

        return super().insert_many(query, values)
    
    def update(self, table, columns, values, where_info) -> bool:
        assert len(columns) == len(values), "칼럼 길이와 값의 길이가 다릅니다."

        query = f'UPDATE {table}\nSET'
        set_query = '\n'.join(f'{column}=%s' for column in columns)
        query += set_query

        # where 도 %s로 안전하게?
        query += self.where(*where_info)
        query += ';'
        return super().update(query, values)

    def delete(self, table, where_info):
        query = f'DELETE FROM {table};'
        query += self.where(*where_info)
        query += ';'
        return super().delete(query)

if __name__ == '__main__':
    db = PostgreSQL({'host': '3.39.222.13', 'port': '5432', 'user':'tready', 'password': 'test', 'database': 'tready_db'})

    with db:
        result = db.select('tb_store', '*')

    print(result)
