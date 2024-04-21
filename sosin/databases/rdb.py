try:
    import pymysql
except:
    print('you need to install pymysql\n$ : python -m pip install pymysql')
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
        with self.DB.cursor(self.cursor_type) as cursor:
            sql_qr = 'show tables;'
            cursor.execute(sql_qr)
            result = cursor.fetchall()
        return [t[0] for t in result]
    
    def get_table_columns(self, table:str) -> list[dict]:
        """
        get table column infos
        """
        with self.DB.cursor(self.cursor_type) as cursor:
            sql_qr = 'SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name=%s'
            cursor.execute(sql_qr, table)
            
            return [{'idx': field[4], 'name': field[3], 'type': field[7],
                     'null': field[6] != 'NO', 'PK': field[16]=='PRI', 'FK': field[16]=='MUL'
                     } for field in cursor.fetchall()]
    
    def custom_select(self, sql_qr:str, only_one=False) -> tuple:
        with self.DB.cursor(self.cursor_type) as cur:
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
        if where_condition:
            for i, (col, eq, val) in enumerate(where_condition):
                is_equal = '=' if eq else '!='
                is_multiple = ' AND' if i > 1 else ' WHERE'
                sql_qr += f'{is_multiple} {col}{is_equal}{val}'
        if order_by:
            sql_qr += ' ORDER BY {}'.format(order_by)
        if limit:
            sql_qr += ' LIMIT {}'.format(limit)
        if offset:
            sql_qr += ' OFFSET {}'.format(offset)


        with self.DB.cursor(self.cursor_type) as cur:
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
    def insert_many(self, table:str, columns: str, values: list, ignore:bool=False) -> bool:
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
        ignore_sql = 'IGNORE ' if ignore else ''
        sql = f"INSERT {ignore_sql} INTO {table}({columns}) " \
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

    def update(self, table:str, set_columns:list[str], set_values:list[str], where_column:str, where_value) -> bool:
        """
        Update
        
        example)
        table = "Students"
        set_column = ["name"]
        set_value = ["jason"]
        where_column = "id"
        where_value = "1"
        """

        set_statement = ', '.join('{}="{}"'.format(sc, sv) for sc, sv in zip(set_columns, set_values))
        sql = "UPDATE {0} " \
            "SET {1} " \
            "WHERE {2}={3};".format(table, set_statement, where_column, where_value)
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
        
    # Procedure
    # unavailable
    def make_procedure(self, sp_name:str, inputs:list[tuple], outputs: list[tuple], variables:list[tuple], queries:list[tuple],):
        """
        inputs: [(input_name, dtype)]
        outputs: [(output_name, dtype)]
        varaibles: [(var_name, dtype)]
        """
        return None
        # ASSERT variables IN inputs

        input_str = ', '.join([' '.join(ip) for ip in inputs])
        if not [out for out in outputs if out[0] == 'RESULT']:
            outputs += [('RESULT', 'INT')]
        output_str = (', ' + ', '.join(['OUT ' + ' '.join(out) for out in outputs])) if outputs else ''
        variable_str = '\n'.join('DECLARE {} {};'.format(*var) for var in variables)

        query_strs = []
        for query in queries:
            if query[0].lower() == 'select':
                # select query
                query_strs.append(f'SELECT {query[1]} INTO {query[4]} FROM {query[2]} WHERE {query[3]} LIMIT 1;')
            elif query[0].lower() == 'insert':
                # insert query
                query_strs.append(f'INSERT INTO {query[2]}({query[1]}) VALUES ({query[3]});')
        
        query_str = '\n'.join(query_strs)
        
        query = f"""DELIMITER $$
        CREATE PROCEDURE `{sp_name}`({input_str}{output_str})
        BEGIN
            {variable_str}
            DECLARE exit handler for SQLEXCEPTION
            BEGIN
                ROLLBACK;
                SET RESULT = 0;  
            END;
        
        START TRANSACTION;
            {query_str}
            COMMIT;
            SET RESULT = 1;
        END$$"""
        
        with self.DB.cursor(self.cursor_type) as cursor:
            # do not work
            cursor.execute(query)
            self.DB.commit()
        return query
    # sample
    # self.make_procedure('sp_insert_order2', 
    # inputs=[('_oc_id', 'INT'), ('_commerce_id', 'TINYINT'), ('_sub_id', 'VARCHAR(32)'), ('_order_date', 'DATETIME'), 
    # ('_progress', 'VARCHAR(32)'), ('_quantity', 'INT'), ('_total_amount', 'INT'), ('_cal_amount', 'INT'), ('_buyer_name', 'VARCHAR(32)'), 
    # ('_buyer_phone', 'VARCHAR(32)'), ('_receiver_name', 'VARCHAR(32)'), ('_receiver_phone', 'VARCHAR(32)'), ('_receiver_address', 'VARCHAR(32)'), 
    # ('_PCC', 'VARCHAR(32)'), ('_product_id', 'VARCHAR(32)')], outputs=[], variables=[('_sp_id', 'INT')], 
    # queries=[('select', 'id', 'StoreProduct', 'sub_id=_product_id', '_sp_id'), 
    # ('insert', 'oc_id,sp_id,commerce_id,sub_id,order_date,progress,quantity,total_amount,cal_amount,buyer_name,buyer_phone,\
    # receiver_name,receiver_phone,receiver_address,PCC', 'OrderDetail', '_oc_id, _sp_id, _commerce_id, _sub_id, _order_date,\
    # _progress, _quantity, _total_amount, _cal_amount,_buyer_name,_buyer_phone, _receiver_name, _receiver_phone, \
    # _receiver_address, _PCC')])
    
    def call_procedure(self, sp_name:str, inputs:list, outputs:list[str]=['RESULT']):
        output_str = (',' + ','.join(['@'+output for output in outputs])) if outputs else ''

        with self.DB.cursor(self.cursor_type) as cursor:
            result = cursor.executemany(f'CALL {sp_name}('+','.join(["%s"]*len(inputs[0])) + output_str +');', 
                                        [self.make_values(o) for o in inputs])
        return result

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