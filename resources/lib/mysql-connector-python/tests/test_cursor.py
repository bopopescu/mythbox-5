# MySQL Connector/Python - MySQL driver written in Python.
# Copyright 2009 Sun Microsystems, Inc. All rights reserved
# Use is subject to license terms. (See COPYING)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# 
# There are special exceptions to the terms and conditions of the GNU
# General Public License as it is applied to this software. View the
# full text of the exception in file EXCEPTIONS-CLIENT in the directory
# of this software distribution or see the FOSS License Exception at
# www.mysql.com.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Unittests for mysql.connector.cursor
"""

from decimal import Decimal
import time
import datetime
import inspect

import tests
from mysql.connector import mysql, connection, cursor, conversion, protocol, utils, errors, constants

class TestsCursor(tests.MySQLConnectorTests):
    
    def tearDown(self):
        if hasattr(self,'c') and isinstance(self.c,cursor.MySQLCursor):
            self.c.close()
        if hasattr(self,'db') and isinstance(self.db,mysql.MySQL):
            self.db.close()
    
    def _test_execute_setup(self,db,tbl="myconnpy_cursor",engine="MyISAM"):
        
        self._test_execute_cleanup(db,tbl)
        stmt_create = """CREATE TABLE %s 
            (col1 INT, col2 VARCHAR(30), PRIMARY KEY (col1))
            ENGINE=%s""" % (tbl,engine)

        try:
            cursor = db.cursor()
            cursor.execute(stmt_create)
        except (StandardError), e:
            self.fail("Failed setting up test table; %s" % e)
        cursor.close()
    
    def _test_execute_cleanup(self,db,tbl="myconnpy_cursor"):
        
        stmt_drop = """DROP TABLE IF EXISTS %s""" % (tbl)
        
        try:
            cursor = db.cursor()
            cursor.execute(stmt_drop)
        except (StandardError), e:
            self.fail("Failed cleaning up test table; %s" % e)
        cursor.close()

class CursorBaseTests(tests.MySQLConnectorTests):
    
    def setUp(self):
        self.c = cursor.CursorBase()
    
    def test_description(self):
        """CursorBase object description-attribute"""
        self.checkAttr(self.c,'description',None)
    
    def test_rowcount(self):
        """CursorBase object rowcount-attribute"""
        self.checkAttr(self.c,'rowcount',-1)

    def test_arraysize(self):
        """CursorBase object arraysize-attribute"""
        self.checkAttr(self.c,'arraysize',1)

    def test_callproc(self):
        """CursorBase object callproc()-method"""
        self.checkMethod(self.c,'callproc')
        
        try:
            self.c.callproc('foo', args=(1,2,3))
        except (SyntaxError, TypeError):
            self.fail("Cursor callproc(): wrong arguments")
            
    def test_close(self):
        """CursorBase object close()-method"""
        self.checkMethod(self.c,'close')
        
    def test_execute(self):
        """CursorBase object execute()-method"""
        self.checkMethod(self.c,'execute')
            
        try:
            self.c.execute('select', params=(1,2,3))
        except (SyntaxError, TypeError):
            self.fail("Cursor execute(): wrong arguments")
            
    def test_executemany(self):
        """CursorBase object executemany()-method"""
        self.checkMethod(self.c,'executemany')
        
        try:
            self.c.executemany('select', [()])
        except (SyntaxError, TypeError):
            self.fail("Cursor executemany(): wrong arguments")

    def test_fetchone(self):
        """CursorBase object fetchone()-method"""
        self.checkMethod(self.c,'fetchone')
        
    def test_fetchmany(self):
        """CursorBase object fetchmany()-method"""
        self.checkMethod(self.c,'fetchmany')
        
        try:
            self.c.fetchmany(size=1)
        except (SyntaxError, TypeError):
            self.fail("Cursor fetchmany(): wrong arguments")
        
    def test_fetchall(self):
        """CursorBase object fetchall()-method"""
        self.checkMethod(self.c,'fetchall')
        
    def test_nextset(self):
        """CursorBase object nextset()-method"""
        self.checkMethod(self.c,'nextset')
        
    def test_setinputsizes(self):
        """CursorBase object setinputsizes()-method"""
        self.checkMethod(self.c,'setinputsizes')
            
        try:
            self.c.setinputsizes((1,))
        except (SyntaxError, TypeError):
            self.fail("CursorBase setinputsizes(): wrong arguments")
            
    def test_setoutputsize(self):
        """CursorBase object setoutputsize()-method"""
        self.checkMethod(self.c,'setoutputsize')

        try:
            self.c.setoutputsize(1,column=None)
        except (SyntaxError, TypeError):
            self.fail("CursorBase setoutputsize(): wrong arguments")

class MySQLCursorTests(TestsCursor):
    
    def setUp(self):
        self.c = cursor.MySQLCursor(db=None)
        self.db = None
            
    def test_init(self):
        """MySQLCursor object init"""
        try:
            c = cursor.MySQLCursor(db=None)
        except (SyntaxError, TypeError), e:
            self.fail("Failed initializing MySQLCursor; %s" % e)
        
        self.assertRaises(errors.InterfaceError,cursor.MySQLCursor,db='foo')

    def test__result(self):
        """MySQLCursor object warnings-attribute"""
        self.checkAttr(self.c,'_result',[])

    def test__nextrow(self):
        """MySQLCursor object _nextrow-attribute"""
        self.checkAttr(self.c,'_nextrow',(None,None))

    def test_lastrowid(self):
        """MySQLCursor object lastrowid-attribute"""
        self.checkAttr(self.c,'lastrowid',None)

    def test__warnings(self):
        """MySQLCursor object warnings-attribute"""
        self.checkAttr(self.c,'_warnings',None)
    
    def test__valid_protocol(self):
        """MySQLCursor object _valid_protocol-method"""
        self.checkMethod(self.c,'_valid_protocol')
        
        self.assertRaises(errors.InterfaceError, self.c._valid_protocol, 'foo')
        self.db = mysql.MySQLBase()
        self.assertRaises(errors.InterfaceError, self.c._valid_protocol, self.db)
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.assertEqual(True,self.c._valid_protocol(self.db))
        self.c.close()
        
    def test_set_connection(self):
        """MySQLCursor object set_connection()-method"""
        self.checkMethod(self.c,'set_connection')
        
        self.assertRaises(errors.InterfaceError, self.c.set_connection, 'foo')
        self.db = mysql.MySQLBase()
        self.assertRaises(errors.InterfaceError, self.c.set_connection, self.db)
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.c.set_connection(self.db)
        self.c.close()
        
    def test__reset_result(self):
        """MySQLCursor object _reset_result()-method"""
        self.checkMethod(self.c,'_reset_result')
        
        self.c._reset_result()
        self.assertEqual([], self.c._result,
            "_result is not reset to empty list")
        self.assertEqual((None,None), self.c._nextrow,
            "_nextrow is not reset to 0")
        self.assertEqual(None, self.c._warnings,
            "_warnings is not reset to empty list")
        self.assertEqual(0, self.c._warning_count,
            "_warning_count is not reset to 0")
        self.assertEqual((), self.c._fields,
            "_fields is not reset to empty tuple")
        
    def test_next(self):
        """MySQLCursor object next()-method"""
        self.checkMethod(self.c,'next')
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.c = cursor.MySQLCursor(self.db)
        self.assertRaises(StopIteration,self.c.next)
        self.c.execute("SELECT SHA1('myconnpy')")
        exp = (u'c5e24647dbb63447682164d81b34fe493a83610b',)
        self.assertEqual(exp,self.c.next())
        self.c.close()
        
    def test_close(self):
        """MySQLCursor object close()-method"""
        self.checkMethod(self.c,'close')

        self.assertEqual(False, self.c.close(),
            "close() should return False with no connection")

        db1 = mysql.MySQL(**self.getMySQLConfig())
        self.assertEqual([],db1.cursors,
            "New MySQL-object should have no cursors.")
        c1 = cursor.MySQLCursor(db1)
        self.assertEqual([c1],db1.cursors)
        self.assertEqual(True, c1.close(),
            "close() should return True when succesful")
        self.assertEqual([],db1.cursors,
            "Closing last cursor MySQL-object should leave list empty.")

        c1 = cursor.MySQLCursor(db1)
        db1.remove_cursor(c1)
        self.assertEqual(False, c1.close())
    

            
    def test__process_params(self):
        """MySQLCursor object _process_params()-method"""
        self.checkMethod(self.c,'_process_params')
        
        self.assertRaises(errors.ProgrammingError,self.c._process_params,'foo')
        self.assertRaises(errors.ProgrammingError,self.c._process_params,())

        st_now = time.localtime()
        data = (
            None,
            int(128),
            long(1281288),
            float(3.14),
            Decimal('3.14'),
            'back\slash',
            'newline\n',
            'return\r',
            "'single'",
            '"double"',
            'windows\032',
            str("Strings are sexy"),
            u'\u82b1',
            datetime.datetime(2008, 5, 7, 20, 01, 23),
            datetime.date(2008, 5, 7),
            datetime.time(20, 03, 23),
            st_now,
            datetime.timedelta(hours=40,minutes=30,seconds=12),
        )
        exp = (
            'NULL',
            '128',
            '1281288',
            '3.14',
            "'3.14'",
            "'back\\\\slash'",
            "'newline\\n'",
            "'return\\r'",
            "'\\'single\\''",
            '\'\\"double\\"\'',
            "'windows\\\x1a'",
            "'Strings are sexy'",
            "'\xe8\x8a\xb1'",
            "'2008-05-07 20:01:23'",
            "'2008-05-07'",
            "'20:03:23'",
            "'%s'" % time.strftime('%Y-%m-%d %H:%M:%S',st_now),
            "'40:30:12'",
        )
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.c = self.db.cursor()
        self.assertEqual((),self.c._process_params(()),
            "_process_params() should return a tuple")
        res = self.c._process_params(data)
        map(self.assertEqual,exp,res)
        self.c.close()

    def test__process_params_dict(self):
        """MySQLCursor object _process_params_dict()-method"""
        self.checkMethod(self.c,'_process_params')

        self.assertRaises(errors.ProgrammingError,self.c._process_params,'foo')
        self.assertRaises(errors.ProgrammingError,self.c._process_params,())

        st_now = time.localtime()
        data = {
            'a' : None,
            'b' : int(128),
            'c' : long(1281288),
            'd' : float(3.14),
            'e' : Decimal('3.14'),
            'f' : 'back\slash',
            'g' : 'newline\n',
            'h' : 'return\r',
            'i' : "'single'",
            'j' : '"double"',
            'k' : 'windows\032',
            'l' : str("Strings are sexy"),
            'm' : u'\u82b1',
            'n' : datetime.datetime(2008, 5, 7, 20, 01, 23),
            'o' : datetime.date(2008, 5, 7),
            'p' : datetime.time(20, 03, 23),
            'q' : st_now,
            'r' : datetime.timedelta(hours=40,minutes=30,seconds=12),
        }
        exp = {
            'a' : 'NULL',
            'b' : '128',
            'c' : '1281288',
            'd' : '3.14',
            'e' : "'3.14'",
            'f' : "'back\\\\slash'",
            'g' : "'newline\\n'",
            'h' : "'return\\r'",
            'i' : "'\\'single\\''",
            'j' : '\'\\"double\\"\'',
            'k' : "'windows\\\x1a'",
            'l' : "'Strings are sexy'",
            'm' : "'\xe8\x8a\xb1'",
            'n' : "'2008-05-07 20:01:23'",
            'o' : "'2008-05-07'",
            'p' : "'20:03:23'",
            'q' : "'%s'" % time.strftime('%Y-%m-%d %H:%M:%S',st_now),
            'r' : "'40:30:12'",
        }
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.c = self.db.cursor()
        self.assertEqual({},self.c._process_params_dict({}),
            "_process_params_dict() should return a dict")
        self.assertEqual(exp,self.c._process_params_dict(data))
        self.c.close()
        
    def test__get_description(self):
        """MySQLCursor object _get_description()-method"""
        self.checkMethod(self.c,'_get_description')

        self.assertEqual(None,self.c._get_description(None))
        self.assertRaises(errors.ProgrammingError,self.c._get_description,
            (1,['foo',]))
        self.assertRaises(errors.ProgrammingError,self.c._get_description,1)
        
        pkt = protocol.FieldPacket(None)
        pkt.catalog = 'def'
        pkt.db = 'somedb'
        pkt.table = 'sometbl'
        pkt.org_table = ''
        pkt.name = "somecol"
        pkt.org_name = ''
        pkt.charset = 33
        pkt.length = 231
        pkt.type = constants.FieldType.VAR_STRING
        pkt.flags = constants.FieldFlag.NOT_NULL
        
        exp = [('somecol', 253, None, None, None, None, 0, 1)]
        self.assertEqual(exp,self.c._get_description((1,[pkt])))

    def test__fetch_warnings(self):
        """MySQLCursor object _fetch_warnings()-method"""
        self.checkMethod(self.c,'_fetch_warnings')

        self.assertRaises(errors.ProgrammingError,self.c._fetch_warnings)
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.db.set_getwarnings(True)
        self.c = self.db.cursor()
        self.c.execute("SELECT 'a' + 'b'")
        self.c.fetchone()
        exp = [
            (u'Warning', 1292L, u"Truncated incorrect DOUBLE value: 'a'"),
            (u'Warning', 1292L, u"Truncated incorrect DOUBLE value: 'b'")
            ]
        self.assertEqual(exp, self.c._fetch_warnings())
        self.assertEqual(len(exp), self.c._warning_count)
    
    def test__handle_noresultset(self):
        """MySQLCursor object _handle_noresultset()-method"""
        self.checkMethod(self.c,'_handle_noresultset')

        self.assertRaises(errors.ProgrammingError,self.c._handle_noresultset,None)
        pkt = protocol.OKResultPacket(None)
        data = (1,10,100)
        pkt.affected_rows, pkt.insert_id, pkt.warning_count = data
        self.c._handle_noresultset(pkt)
        self.assertEqual(data, (self.c.rowcount,self.c.lastrowid,
            self.c._warning_count))
        self.c.close()
        
    def test_execute(self):
        """MySQLCursor object execute()-method"""
        self.checkMethod(self.c,'execute')
        
        self.assertEqual(0,self.c.execute(None,None))
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.db.set_getwarnings(True)
        self.c = self.db.cursor()
        
        self.assertRaises(errors.InterfaceError,self.c.execute,
            'SELECT %s,%s,%s', ('foo','bar',))
        self.assertRaises(errors.InterfaceError,self.c.execute,
            'SELECT %s,%s', ('foo','bar','foobar'))
        
        self.c.execute("SELECT 'a' + 'b'")
        self.c.fetchone()
        exp = [
            (u'Warning', 1292L, u"Truncated incorrect DOUBLE value: 'a'"),
            (u'Warning', 1292L, u"Truncated incorrect DOUBLE value: 'b'")
            ]
        self.assertEqual(exp, self.c._warnings)
        
        self.c.execute("SELECT SHA1('myconnpy')")
        exp = [(u'c5e24647dbb63447682164d81b34fe493a83610b',)]
        self.assertEqual(exp, self.c.fetchall())
        self.c.close()
        
        tbl = 'myconnpy_cursor'
        self._test_execute_setup(self.db,tbl)
        stmt_insert = "INSERT INTO %s (col1,col2) VALUES (%%s,%%s)" % (tbl)
        
        self.c = self.db.cursor()
        res = self.c.execute(stmt_insert, (1,100))
        self.assertEqual(1,res,"Return value of execute() is wrong.")
        stmt_select = "SELECT col1,col2 FROM %s ORDER BY col1" % (tbl)
        self.c.execute(stmt_select)
        self.assertEqual([(1L, u'100')],
            self.c.fetchall(),"Insert test failed")
            
        data = {'id': 2}
        stmt = "SELECT * FROM %s WHERE col1 <= %%(id)s" % tbl
        self.c.execute(stmt, data)
        self.assertEqual([(1L, u'100')],self.c.fetchall())
            
        self._test_execute_cleanup(self.db,tbl)
        self.c.close()
    
    def test_executemany(self):
        """MySQLCursor object executemany()-method"""
        self.checkMethod(self.c,'executemany')
        
        self.assertEqual(0,self.c.executemany(None,[]))
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.db.set_getwarnings(True)
        self.c = self.db.cursor()
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'foo',None)
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'foo','foo')
        self.assertEqual(0,self.c.executemany('foo',[]))
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'foo',['foo'])
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'SELECT %s', [('foo',),'foo'])

        self.c.executemany("SELECT SHA1(%s)", [('foo',),('bar',)])
        self.assertEqual(None,self.c.fetchone())
        self.c.close()
        
        tbl = 'myconnpy_cursor'
        self._test_execute_setup(self.db,tbl)
        stmt_insert = "INSERT INTO %s (col1,col2) VALUES (%%s,%%s)" % (tbl)
        stmt_select = "SELECT col1,col2 FROM %s ORDER BY col1" % (tbl)
        
        self.c = self.db.cursor()

        res = self.c.executemany(stmt_insert,[(1,100),(2,200),(3,300)])
        self.assertEqual(3,res,
            "Return value of executemany() is wrong w/o result.")

        res = self.c.executemany("SELECT %s",[('f',),('o',),('o',)])
        self.assertEqual(3,res)
        
        data = [{'id':2},{'id':3}]
        stmt = "SELECT * FROM %s WHERE col1 <= %%(id)s" % tbl
        self.assertEqual(5,self.c.executemany(stmt, data))

        self.c.execute(stmt_select)
        self.assertEqual([(1L, u'100'), (2L, u'200'), (3L, u'300')],
            self.c.fetchall(),"Multi insert test failed")
        self._test_execute_cleanup(self.db,tbl)
        self.c.close()
    
    def test_fetchwarnings(self):
        """MySQLCursor object fetchwarnings()-method"""
        self.checkMethod(self.c,'fetchwarnings')
        
        self.assertEqual(None,self.c.fetchwarnings(),
            "There should be no warnings after initiating cursor.")
        
        exp = ['A warning']
        self.c._warnings = exp
        self.c._warning_count = len(self.c._warnings)
        self.assertEqual(exp,self.c.fetchwarnings())
        self.c.close()

    def _test_callproc_setup(self,db,prc="myconnpy_callproc"):

        self._test_callproc_cleanup(db,prc)
        stmt_create = """CREATE PROCEDURE %s(IN pFac1 INT, IN pFac2 INT, OUT pProd INT)
            BEGIN SET pProd := pFac1 * pFac2;
            END;""" % (prc)

        try:
            cursor = db.cursor()
            cursor.execute(stmt_create)
        except errors.Error, e:
            self.fail("Failed setting up test stored routine; %s" % e)
        cursor.close()

    def _test_callproc_cleanup(self,db,prc="myconnpy_callproc"):

        stmt_drop = """DROP PROCEDURE IF EXISTS %s""" % (prc)

        try:
            cursor = db.cursor()
            cursor.execute(stmt_drop)
        except errors.Error, e:
            self.fail("Failed cleaning up test stored routine; %s" % e)
        cursor.close()

    def test_callproc(self):
        """MySQLCursor object callproc()-method"""
        self.checkMethod(self.c,'callproc')
        
        self.assertRaises(errors.ProgrammingError,self.c.callproc,None,None)
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.db.set_getwarnings(True)
        prc = 'myconnpy_callproc'
        self._test_callproc_setup(self.db,prc)
        self.c = self.db.cursor()
        self.c.callproc(prc,(5,5,0))
        self.assertEqual(('5', '5', 25L),self.c.fetchone())
        self._test_callproc_cleanup(self.db,prc)
        self.c.close()
    
    def test_fetchone(self):
        """MySQLCursor object fetchone()-method"""
        self.checkMethod(self.c,'fetchone')
        
        self.assertEqual(None,self.c.fetchone())
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.c = self.db.cursor()
        self.c.execute("SELECT SHA1('myconnpy')")
        exp = (u'c5e24647dbb63447682164d81b34fe493a83610b',)
        self.assertEqual(exp, self.c.fetchone())
        self.assertEqual(None,self.c.fetchone())
        self.c.close()
    
    def test_fetchmany(self):
        """MySQLCursor object fetchmany()-method"""
        self.checkMethod(self.c,'fetchmany')
        
        self.assertEqual([],self.c.fetchmany())
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        tbl = 'myconnpy_fetch'
        self._test_execute_setup(self.db,tbl)
        stmt_insert = "INSERT INTO %s (col1,col2) VALUES (%%s,%%s)" % (tbl)
        stmt_select = "SELECT col1,col2 FROM %s ORDER BY col1 DESC" % (tbl)
        
        self.c = self.db.cursor()
        nrRows = 10
        data = [ (i,"%s" % (i*100)) for i in range(0,nrRows)]
        self.c.executemany(stmt_insert,data)
        self.c.execute(stmt_select)
        exp = [(9L, u'900'), (8L, u'800'), (7L, u'700'), (6L, u'600')]
        rows = self.c.fetchmany(4)
        self.assertEqual(exp,rows,"Fetching first 4 rows test failed.")
        exp = [(5L, u'500'), (4L, u'400'), (3L, u'300')]
        rows = self.c.fetchmany(3)
        self.assertEqual(exp,rows,"Fetching next 3 rows test failed.")
        exp = [(2L, u'200'), (1L, u'100'), (0L, u'0')]
        rows = self.c.fetchmany(3)
        self.assertEqual(exp,rows,"Fetching next 3 rows test failed.")
        self.assertEqual([],self.c.fetchmany())
        self._test_execute_cleanup(self.db,tbl)
        self.c.close()
    
    def test_fetchall(self):
        """MySQLCursor object fetchall()-method"""
        self.checkMethod(self.c,'fetchall')
        
        self.assertRaises(errors.InterfaceError,self.c.fetchall)
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        tbl = 'myconnpy_fetch'
        self._test_execute_setup(self.db,tbl)
        stmt_insert = "INSERT INTO %s (col1,col2) VALUES (%%s,%%s)" % (tbl)
        stmt_select = "SELECT col1,col2 FROM %s ORDER BY col1 ASC" % (tbl)
        
        self.c = self.db.cursor()
        self.c.execute("SELECT * FROM %s" % tbl)
        self.assertEqual([],self.c.fetchall(),
            "fetchall() with empty result should return []")
        nrRows = 10
        data = [ (i,"%s" % (i*100)) for i in range(0,nrRows) ]
        self.c.executemany(stmt_insert,data)
        self.c.execute(stmt_select)
        self.assertEqual(data,self.c.fetchall(),
            "Fetching all rows failed.")
        self.assertEqual(None,self.c.fetchone())
        self._test_execute_cleanup(self.db,tbl)
        self.c.close()
    
    def test__unicode__(self):
        """MySQLCursor object __unicode__()-method"""
        self.assertEqual("MySQLCursor: (Nothing executed yet)",
            "%s" % self.c.__unicode__())
        
        self.db = mysql.MySQL(**self.getMySQLConfig())
        self.c = self.db.cursor()
        self.c.execute("SELECT VERSION()")
        self.c.fetchone()
        self.assertEqual("MySQLCursor: SELECT VERSION()",
            "%s" % self.c.__unicode__())
        stmt= "SELECT VERSION(),USER(),CURRENT_TIME(),NOW(),SHA1('myconnpy')"
        self.c.execute(stmt)
        self.c.fetchone()
        self.assertEqual("MySQLCursor: %s.." % stmt[:30],
            "%s" % self.c.__unicode__())
        self.c.close()
    
    def test__str__(self):
        self.assertEqual("'MySQLCursor: (Nothing executed yet)'",
            "%s" % self.c.__str__())

class MySQLCursorBufferedTests(TestsCursor):

    def setUp(self):
        self.c = cursor.MySQLCursorBuffered(db=None)
        self.db = None

    def test_init(self):
        """MySQLCursorBuffered object init"""
        try:
            c = cursor.MySQLCursorBuffered(db=None)
        except (SyntaxError, TypeError), e:
            self.fail("Failed initializing MySQLCursorBuffered; %s" % e)
        
        self.assertRaises(errors.InterfaceError,cursor.MySQLCursorBuffered,db='foo')
        
    def test__next_row(self):
        """MySQLCursorBuffered object _next_row-attribute"""
        self.checkAttr(self.c,'_next_row',0)
    
    def test__rows(self):
        """MySQLCursorBuffered object _rows-attribute"""
        self.checkAttr(self.c,'_rows',[])

    def test_execute(self):
        """MySQLCursorBuffered object execute()-method
        """
        self.checkMethod(self.c,'execute')

        self.assertEqual(0,self.c.execute(None,None))

        config = self.getMySQLConfig()
        config['buffered'] = True
        self.db = mysql.MySQL(**config)
        self.db.set_getwarnings(True)
        self.c = self.db.cursor()

        self.assertEqual(True,isinstance(self.c,cursor.MySQLCursorBuffered))

        self.c.execute("SELECT 'a' + 'b'")
        exp = [
            (u'Warning', 1292L, u"Truncated incorrect DOUBLE value: 'a'"),
            (u'Warning', 1292L, u"Truncated incorrect DOUBLE value: 'b'")
            ]
        self.assertEqual(exp, self.c._warnings)

        self.c.execute("SELECT SHA1('myconnpy')")
        self.assertEqual(0,self.c._next_row)
        exp = [['c5e24647dbb63447682164d81b34fe493a83610b']]
        self.assertEqual(exp, self.c._rows)
        exp = [(u'c5e24647dbb63447682164d81b34fe493a83610b',)]
        self.assertEqual(exp, self.c.fetchall())
        
        tbl = 'myconnpy_cursor'
        self._test_execute_setup(self.db,tbl)
        stmt_insert = "INSERT INTO %s (col1,col2) VALUES (%%s,%%s)" % (tbl)
        
        data = [(1,100),(2,200),(3,300)]
        for rec in data:
            self.c.execute(stmt_insert, rec)
        
        self.c.execute("SELECT * FROM %s" % (tbl))
        self.assertEqual(0,self.c._next_row)
        self.c.fetchone()
        self.assertEqual(1,self.c._next_row)
        self.c.fetchmany(2)
        self.assertEqual(3,self.c._next_row)
        
        self._test_execute_cleanup(self.db,tbl)
        self.c.close()
        
    def test_executemany(self):
        """MySQLCursorBuffered object executemany()-method"""
        self.checkMethod(self.c,'executemany')

        self.assertEqual(0,self.c.executemany(None,[]))

        config = self.getMySQLConfig()
        config['buffered'] = True
        self.db = mysql.MySQL(**config)
        self.db.set_getwarnings(True)
        self.c = self.db.cursor()
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'foo',None)
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'foo','foo')
        self.assertEqual(0,self.c.executemany('foo',[]))
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'foo',['foo'])
        self.assertRaises(errors.InterfaceError,self.c.executemany,
            'SELECT %s', [('foo',),'foo'])

        self.c.executemany("SELECT SHA1(%s)", [('foo',),('bar',)])
        self.assertEqual(None,self.c.fetchone())
        self.c.close()

        tbl = 'myconnpy_cursor'
        self._test_execute_setup(self.db,tbl)
        stmt_insert = "INSERT INTO %s (col1,col2) VALUES (%%s,%%s)" % (tbl)
        stmt_select = "SELECT col1,col2 FROM %s ORDER BY col1" % (tbl)

        self.c = self.db.cursor()

        res = self.c.executemany(stmt_insert,[(1,100),(2,200),(3,300)])
        self.assertEqual(3,res,
            "Return value of executemany() is wrong w/o result.")

        res = self.c.executemany("SELECT %s",[('f',),('o',),('o',)])
        self.assertEqual(3,res)

        data = [{'id':2},{'id':3}]
        stmt = "SELECT * FROM %s WHERE col1 <= %%(id)s" % tbl
        self.assertEqual(5,self.c.executemany(stmt, data))

        self.c.execute(stmt_select)
        self.assertEqual([(1L, u'100'), (2L, u'200'), (3L, u'300')],
            self.c.fetchall(),"Multi insert test failed")
        self._test_execute_cleanup(self.db,tbl)
        self.c.close()
