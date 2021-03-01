import os, sys, string
import sqlite3
import traceback

class ConnExcept(Exception):
    "self defined Exception for DB connect fail"
    def __str__(self):
        return "Cannot open and connect to database"

class SQLObj(object):
    def __init__(self, db='DEMO.db'):
        self.db_name = db
        self.connected = 0
        self.cur = None  # 游标对象
        self.conn = None  # 连接对象
        self._connect()

    def _connect(self):
        try:
            # print "connect to ", self.db_name
            self.conn = sqlite3.connect(self.db_name)
            self.cur = self.conn.cursor()
            self.connected = 1
        except:
            traceback.print_exc()
            self.connected = 0

    @property
    def is_connected(self):
        return self.connected != 0

    def _check_alive(self):
        if not self.is_connected:
            self._connect()
        if not self.is_connected:
            raise ConnExcept    # 如果尝试重新连接后还是没连上，抛出异常

            # 直接提取方法

    def query(self, sql, warning=1):
        self._check_alive()
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            cur.close()
        except:
            if warning:
                traceback.print_exc()
            return None
        return res

        # 特殊的提取方法，形成字典返回

    def dquery(self, sql, warning=1):
        self._check_alive()
        try:
            cur = self.conn.cursor()
            cur.execute(sql)

            des = cur.description  # 获取字段描述
            res = cur.fetchall()  # 获取字段内容
            ret = []
            if des:
                names = [x[0] for x in des]  # 从des中提取每个元素（列表）的第一个元素（字符串）
                for line in res:
                    ret.append(dict(zip(names, line)))  # dict是形成字典的工厂函数，zip用于多个列表循环(name, line是两个列表)
            else:
                ret = res
            cur.close()
        except:
            if warning:
                traceback.print_exc()
            return None
        return ret

    def execute(self, sql, warning=1):
        self._check_alive()
        try:
            cur = self.conn.cursor()
            rows = cur.execute(sql)
            self.conn.commit()
            cur.close()
            return rows
        except:
            if warning:
                traceback.print_exc()
            return -1

    def close(self):
        if self.connected == 0:
            return
        try:
            self.cur.close()
            self.conn.close()
            self.connected = 0
        except:
            pass

    def __del__(self):
        self.close()


def _lbsql_test_sqlite3():
    db = SQLObj()
    rlt = db.query("select * from sqlite_master")
    print(rlt)

if __name__ == "__main__":
    _lbsql_test_sqlite3()