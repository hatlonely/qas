#!/usr/bin/env python3


import json
import unittest
from .mysql_driver import *


class TestPymysql(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='keaiduo1',
            database='hatlonely',
            cursorclass=pymysql.cursors.DictCursor,
        )

    def test_create_table(self):
        with self.connection.cursor() as cursor:
            sql = """
CREATE TABLE `users` (
`id` int(11) NOT NULL AUTO_INCREMENT,
`email` varchar(255) COLLATE utf8_bin NOT NULL,
`password` varchar(255) COLLATE utf8_bin NOT NULL,
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
AUTO_INCREMENT=1;
"""
            cursor.execute(sql)
        self.connection.commit()

    def test_insert(self):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
            cursor.execute(sql, ('webmaster@python.org', 'very-secret'))
        self.connection.commit()

    def test_select(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
            cursor.execute(sql, ('webmaster@python.org',))
            result = cursor.fetchall()
            print(result)
        self.connection.commit()


if __name__ == '__main__':
    unittest.main()
