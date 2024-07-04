# interface

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, overload
try:
    from pymysql.connections import Connection
    from pymysql.cursors import Cursor, DictCursor
except:
    ...

try:
    from psycopg2._psycopg import connection, cursor
    from psycopg2.extras import RealDictCursor
except:
    ...

try:
    class ConnectionType(Connection, connection): ...
    class CursorType(DictCursor, RealDictCursor): ...
    class CursorKindType(Cursor, cursor): ...
except:
    class ConnectionType(): ...
    class CursorType(): ...
    class CursorKindType(): ...

class Database(ABC):
    """
    데이터베이스 추상클래스
    """

    DB: ConnectionType
    db_config: Dict[str, str]
    cursor: Optional[CursorType] = None
    cursor_type: Optional[CursorKindType]
    
    def __init__(self, db_config: Dict[str, str], cursor_type:Optional[CursorKindType]=None) -> None:
        """
        **db_config**
            host=database host (localhost)
            port=port (3306)
            user=username (root)
            password=password (1q2w3e)
            database=database name (testdb)
            charset=charcter encoding (utf8mb4)
        """
        self.db_config = db_config
        self.cursor_type = cursor_type

    def __enter__(self):
        """
        Usage:
        ```py
        db = Database(config)
        with db: # as db_object
            ...
        ```
        """
        return self.connect()

    def __del__(self) -> None:
        try:
            self.disconnect()
        except:
            ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    @abstractmethod
    def connect(self): ...

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        self.DB.close()

    def execute(self, query, args=None):
        self.cursor.execute(query, args)

    def executemany(self, query, args=None):
        self.cursor.executemany(query, args)

    def commit(self):
        self.DB.commit()
    
    @overload
    @abstractmethod
    def insert(self, 
               table: str, 
               columns: Union[str, List[str]], 
               value: Tuple
               ) -> bool: ...
    
    def insert(self, query, args=None) -> bool:
        try:
            self.execute(query, args)
            self.commit()
            return True
        except Exception as e:
            self.DB.rollback()
            print("INSERT ERR", e)
            return False

    @abstractmethod
    def insert_many(self, 
                    table: str, 
                    columns: Union[str, List[str]], 
                    values:List[Tuple]
                    ) -> bool: ...

    def insert_many(self, query, values) -> bool:
        try:
            self.executemany(query, values)
            self.commit()
            return True
        except Exception as e:
            self.DB.rollback()
            print("INSERT MANY ERR", e)
            return False

    @overload
    @abstractmethod
    def select(
        table: str, 
        columns: Union[str, Iterable], 
        where_info: Optional[Tuple[str, Any]]=None, 
        order_by: str=None, 
        page_info: Optional[Tuple[int, int]]=None): ...

    # not overloaded use just last function
    def select(self, query: str):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            return ("SELECT ERR", e)
    
    @abstractmethod
    def where(self, column: str, value: str, option: str=None): ...
    @abstractmethod
    def sort(self, order_by: str): ...
    @abstractmethod
    def pagination(self, page: int, size: int): ...

    @overload
    @abstractmethod
    def update(self, 
               table: str, 
               columns: List[str], 
               values: List, 
               where_info: Tuple[str, Any]
               ) -> bool: ...

    def update(self, query, args=None) -> bool:
        try:
            self.execute(query, args)
            self.commit()
            return True
        except Exception as e:
            self.DB.rollback()
            print("UPDATE ERR", e)
            return False

    @overload
    @abstractmethod
    def delete(self,
               table: str,
               where_info: Tuple[str, Any]
               ) -> bool: ...

    def delete(self, query, args=None) -> bool:
        try:
            self.execute(query, args)
            self.commit()
            return True
        except Exception as e:
            self.DB.rollback()
            print("DELETE ERR", e)
            return False
