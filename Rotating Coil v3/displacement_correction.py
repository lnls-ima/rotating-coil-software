'''
Created on 20 de jul de 2018

@author: vps
'''

import sqlite3
import numpy as np


def db_displacement_correction():
    """Corrects displacement signal in measurements prior to 2018/07/20
    10:30 am"""
    #loads db entries checking id
    _con = sqlite3.connect('measurements_data.db')
    _cur = _con.cursor()
    _id_f = 13596
    _cur.execute("""SELECT magnetic_center_x, magnetic_center_y
                    FROM measurements WHERE id < {0}""".format(_id_f))
    _center_0 = np.array(_cur.fetchall())
    _center_f = (-1*_center_0).tolist()
    for i in range(_id_f-1):
        _cur.execute("""UPDATE measurements SET magnetic_center_x = ?,
                        magnetic_center_y = ? WHERE id = ?""",
                        (_center_f[i][0], _center_f[i][1], i+1))
    _con.commit()
    _con.close()

db_displacement_correction()
