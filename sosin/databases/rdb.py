import pymysql
import traceback

class MariaDB:

    def __init__(self, db_config:dict, cursor_type="tuple") -> None:
        '''
        생성자 메서드
        인스턴스 생성 시 db_config를 전달받아 DB에 연결합니다.
        
        **db_config**
            host=데이터베이스 서버 주소
            port=포트번호
            user=사용자 이름
            password=사용자 암호
            database=데이터베이스 이름
            charset=문자 인코딩
        '''

        db_config['port'] = int(db_config.get('port', '3306'))
        self.DB = pymysql.connect(**db_config)

        if cursor_type == 'dict':
            self.cursor_type = pymysql.cursors.DictCursor
        else:
            self.cursor_type = None
            
        return

    def __del__(self):
        '''
        인스턴스 소멸 시 DB 연결을 해제합니다.
        '''
        self.DB.close()
        return
    
    def custom_select(self, sql_qr:str, only_one=False) -> tuple:
        with self.DB.cursor() as cur:
            cur.execute(sql_qr)
            return cur.fetchone() if only_one else cur.fetchall()

    def select(self, column_qry:str, table:str, limit=None, offset=None, order_by=None, where_condition=list[tuple]) -> tuple:
        """
        Select
        예시) 
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

    def insert(self, table:str, columns: str, value: tuple) -> bool:
        """
        Insert Data
        예시)
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
            return False
    
    # values는 list 형식으로 넣었음, args로 함
    def insert_many(self, table:str, columns: str, values: list) -> bool:
        """
        Insert Many Datas
        예시)
        table = "Students"
        columns = "name, email, phone"
        values = [
            ('이름', '이메일', '번호'),
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
            return False



    def update(self, table:str, set_column:str, set_value, where_column:str, where_value) -> bool:
        """
        Update
        예시)
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
            return False
    
    def delete(self, table:str, where_column:str, where_value) -> bool:
        """
        Delete
        예시)
        table = "Students"
        where_column = "id"
        where_value = "1"
        """
        sql = """DELETE FROM {0} WHERE {1}={2}""".format(table, where_column, where_value)
        try:
            with self.DB.cursor() as cur:
                cur.execute(sql)
                self.DB.commit()
            return True
        except:
            return False

    @staticmethod
    def make_columns(data: dict) -> str:
        """
        dictionary 객체에서 키를 칼럼 문자열로 변경
        """
        return ','.join(data.keys())
    
    @staticmethod
    def make_values(data: dict) -> tuple:
        """
        dictionary 객체에서 value를 tuple로 변경
        """
        return tuple(data.values())
