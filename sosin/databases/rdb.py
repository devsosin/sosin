import pymysql
import traceback

from typing import Iterable, Union

class MariaDB:
    """
    MariaDB
    """

    def __init__(self, db_config:dict, cursor_type="tuple") -> None:
        """
        생성자 메서드
        인스턴스 생성 시 db_config를 전달받아 DB에 연결합니다.
        
        **db_config**
            host=database host (localhost)
            port=port (3306)
            user=username (root)
            password=password (1q2w3e)
            database=database name (testdb)
            charset=charcter encoding (utf8mb4)
        
        """

        db_config['port'] = int(db_config.get('port', '3306'))
        self.DB = pymysql.connect(**db_config)

        if cursor_type == 'dict':
            self.cursor_type = pymysql.cursors.DictCursor
        else:
            self.cursor_type = None
            
        return

    def __del__(self):
        """
        인스턴스 소멸 시 DB 연결을 해제합니다.
        """
        self.DB.close()
        return
    
    def create_table(self, tb_name:str, fields:list, foreign_keys:list=[], auto_pk=True):
        """
        create table
        
        *required
        tb_name = 'tableA'
        fields = [
            # nullable, auto_increment, is_key can be omissible
            # nullable ~ is_key : type = boolean
            ('LastName', 'VARCHAR(255)', nullable, auto_increment, is_key), 
            
        ]
        foreign_keys = [
            ('column_name', 'target_table', 'target_column')
        ]
        """
        assert (sum([field[4] for field in fields if len(field) == 5]) + auto_pk) == 1, 'len(pk) to be 1'

        columns = ['id INT PRIMARY KEY' if auto_pk else '']
        for field in fields:
            if len(field) > 2:
                field[2] = 'NULL' if field[2] else 'NOT NULL'
            if len(field) > 3:
                field[3] = 'AUTO_INCREMENT' if field[3] else ''
            if len(field) > 4:
                field[4] = 'PRIMARY KEY' if field[4] else ''
            columns.append(' '.join(field))
        
        constraints = []
        for fk in foreign_keys:
            fk_column = fk[0]
            fk_t_table = fk[1]
            fk_t_column = fk[2]
            constraints.append(f', FOREIGN KEY ({fk_column}) REFERENCES {fk_t_table} ({fk_t_column})')

        try:
            # foreign_keys -> sql 문 생성
            with self.DB.cursor() as cursor:
                sql = 'CREATE TABLE %s ('%tb_name + \
                ', '.join(columns) + \
                ''.join(constraints) + \
                ');'
                cursor.execute(sql)
                self.DB.commit()
                return True
        except:
            traceback.print_exc()
            self.DB.rollback()
            return False
    
    def drop_table(self, tables:Iterable[str], forcing=True) -> bool:
        """
        drop table

        *required
        tables = ('tableA', 'tableB')
        """

        try:
            with self.DB.cursor() as cursor:
                sql = 'DROP TABLE %s;'%(', '.join(tables))
                cursor.execute(sql)
                self.DB.commit()
                return True
        except:
            traceback.print_exc()
            self.DB.rollback()
            return False
    
    def get_tables(self) -> list:
        """
        get table names
        """
        with self.DB.cursor() as cursor:
            sql_qr = 'show tables;'
            cursor.execute(sql_qr)
            result = cursor.fetchall()
        return [t[0] for t in result]
    
    def get_table_columns(self, table:str) -> list[dict]:
        """
        get table column infos
        """
        with self.DB.cursor() as cursor:
            sql_qr = 'SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name=%s'
            cursor.execute(sql_qr, table)
            
            return [{'idx': field[4], 'name': field[3], 'type': field[7],
                     'null': field[6] != 'NO', 'PK': field[16]=='PRI', 'FK': field[16]=='MUL'
                     } for field in cursor.fetchall()]
    
    def custom_select(self, sql_qr:str, only_one=False) -> tuple:
        with self.DB.cursor() as cur:
            cur.execute(sql_qr)
            return cur.fetchone() if only_one else cur.fetchall()

    def select(self, column_qry:str, table:str, limit=None, offset=None, order_by=None, where_condition=[]) -> tuple:
        """
        Select
        
        example) 
        column_qry = "*"
        column_qry = "id, name, email"
        table = "Students"
        """
        sql_qr = "SELECT {0} FROM {1}".format(column_qry, table)
        if limit:
            sql_qr += ' LIMIT {}'.format(limit)
        if offset:
            sql_qr += ' OFFSET {}'.format(offset)
        if order_by:
            sql_qr += ' ORDER BY {}'.format(order_by)
        if where_condition:
            for i, (col, eq, val) in enumerate(where_condition):
                is_equal = '=' if eq else '!='
                is_multiple = ' AND' if i > 1 else ' WHERE'
                sql_qr += f'{is_multiple} {col}{is_equal}{val}'


        with self.DB.cursor() as cur:
            cur.execute(sql_qr)
            return cur.fetchall()

    def insert(self, table:str, columns: str, value: tuple) -> Union[int, bool]:
        """
        Insert Data
        
        example)
        table = "Students"
        columns = "name, email, phone"
        values = ('이름', '이메일', '번호')
        """

        sql_qr = f"INSERT INTO {table}({columns}) " \
                  "VALUES (" +','.join(["%s"]*len(value)) +")"
        # args = values
        
        try:
            with self.DB.cursor() as cur:
                cur.execute(sql_qr, value)
                self.DB.commit()
            return cur.lastrowid
        except:
            traceback.print_exc()
            self.DB.rollback()
            return False
    
    # values는 list 형식으로 넣었음, args로 함
    def insert_many(self, table:str, columns: str, values: list) -> bool:
        """
        Insert Many Datas
        
        example)
        table = "Students"
        columns = "name, email, phone"
        values = [
            ('hong gildong', 'hgd123@gmail.com', '01012345678'),
            ...
        ]
        """
        sql = f"INSERT INTO {table}({columns}) " \
                  "VALUES ("  + ','.join(["%s"]*len(values[0])) + ");"
        try:
            with self.DB.cursor() as cur:
                cur.executemany(sql, values)
                self.DB.commit()
            return True
        except:
            traceback.print_exc()
            self.DB.rollback()
            return False

    def update(self, table:str, set_column:str, set_value, where_column:str, where_value) -> bool:
        """
        Update
        
        example)
        table = "Students"
        set_column = "name"
        set_value = "jason"
        where_column = "id"
        where_value = "1"
        """
        sql = "UPDATE {0}" \
            "SET {1}={2}" \
            "WHERE {3}={4};".format(table, set_column, set_value, where_column, where_value)
        try:
            with self.DB.cursor() as cur:
                cur.execute(sql)
                self.DB.commit()
            return True
        except:
            traceback.print_exc()
            self.DB.rollback()
            return False
    
    def delete(self, table:str, where_column:str, where_value) -> bool:
        """
        Delete
        
        example)
        table = "Students"
        where_column = "id"
        where_value = "1"
        """
        sql = 'DELETE FROM {0} WHERE {1}={2}'.format(table, where_column, where_value)
        try:
            with self.DB.cursor() as cur:
                cur.execute(sql)
                self.DB.commit()
            return True
        except:
            traceback.print_exc()
            self.DB.rollback()
            return False
    
    def truncate(self, table:str, forcing=True) -> bool:
        """
        truncate table
        """
        try:
            with self.DB.cursor() as cursor:
                cursor.execute(f'SET FOREIGN_KEY_CHECKS = {int(forcing)}; TRUNCATE TABLE {table};')
                self.DB.commit()
                return True
        except:
            return False

    @staticmethod
    def make_columns(data: dict) -> str:
        """
        dictionary keys to columns str
        """
        return ','.join(data.keys())
    
    @staticmethod
    def make_values(data: dict) -> tuple:
        """
        dictionary values to tuple
        """
        return tuple(data.values())

if __name__ == '__main__':
    my_db = MariaDB({'host': 'localhost', 'port': 3306, 'user':'root', 'password': 'ppww', 'database': 'test'})

    my_db.get_tables()
    
    fields = [
        ('name', 'VARCHAR(255)'),
        ('address', 'VARCHAR(255)'),
        ('phone', 'VARCHAR(32)'),
    ]
    my_db.create_table('tb_student', fields)

    fields = [
        ('student_id', 'INT'),
        ('math', 'INT'),
        ('science', 'INT'),
        ('english', 'INT'),
    ]
    foreign_keys = [
        ('student_id', 'tb_student', 'id')
    ]
    my_db.create_table('tb_grade', fields, foreign_keys)

    grade_columns = my_db.get_table_columns('tb_grade')
    print(grade_columns)

    my_db.drop_table(['tb_student', 'tb_grade'])