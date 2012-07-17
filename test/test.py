'''
Created on Jul 15, 2012

@author: jgoppert
'''
import unittest
import sys
import os
from fortran_tools import Fixed2Free
import tempfile
print tempfile.gettempdir()

class Test(unittest.TestCase):

    def setUp(self):
        self.path = os.path.abspath(os.path.dirname(__file__))
        print self.path

    def test_outpt2(self):
        
        filenames=['airfol','atmos','auxout','fltcl','outpt2','subryw','supryw']
        
        print "current directory: ", os.path.abspath(os.path.curdir)
        
        for filename in filenames:
            
            input_path=os.path.join(self.path, 'input', filename+'.f')
            output_path=os.path.join(self.path, 'output', filename+'.f90')
            
                        
            print "checking file:", input_path
            
            Fixed2Free.from_argv(['', input_path, output_path, '--style'])
            
            expected_path=os.path.join(self.path, 'expected', filename+'.f90')
            
            with open(output_path, 'rb') as output_file:
                output = output_file.readlines()
            with open(expected_path, 'rb') as expected_file:
                expected = expected_file.readlines()
                
            for i in xrange(len(expected)):
                if output[i] != expected[i]:
                    raise Exception(output_path+": line " +str(i)+" does not match " + expected_path)

if __name__ == "__main__":
    #if len(sys.argv) == 1:
    sys.argv = ['', 'Test.testfixed2free']
    unittest.main()