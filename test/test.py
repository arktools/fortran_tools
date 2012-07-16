'''
Created on Jul 15, 2012

@author: jgoppert
'''
import unittest
import sys
import os
from fortran_tools import Fixed2Free
        
class Test(unittest.TestCase):


    def fixed2free(self):
        filename='subryw'
        Fixed2Free.from_argv(['', os.path.join('data', filename+'.f'), filename+'.f90', '--style'])

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv = ['', 'Test.fixed2free']
    unittest.main()