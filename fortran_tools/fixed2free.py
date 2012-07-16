'''
Created on Jul 15, 2012

@author: jgoppert
'''

import argparse
import sys
import re
        
class Fixed2Free(object):
    '''
    This class converts fixed format fortran code to free format.
    '''

    def __init__(self,input_filename,output_filename,style):
        '''
        Constructor
        '''
        self.input_filename=input_filename
        self.output_filename=output_filename
        self.style=style
        
        #regex's
        self.re_line_continuation = re.compile('(^\s\s\s\s\s)([^\s])([\s]*)')
        self.re_hollerith = re.compile('[\s,]((\d+)H)')
        
        self.re_var_end = re.compile('.*[A-Za-z0-9]+$')
        self.re_var_begin = re.compile('(^\s\s\s\s\s)([^\s])([\s]*)([A-Za-z]+[0-9]?)+')
        
        self.re_number_end = re.compile('.*[\d.eE]+$')
        self.re_number_begin = re.compile('(^\s\s\s\s\s)([^\s])([\s]*)[\d.eE]+')
        
        self.re_exponent_old = re.compile('([\d.]E)[\s]([\d]+)')
        
        self.process()
        
    def process(self):
        
        #read source
        with open(self.input_filename, 'rb') as f:
            source = f.readlines()

        #fix source code
        for i in xrange(len(source)):
            self.remove_new_lines(source, i)
            self.truncate_extra_linewidth(source, i)
            self.fix_comments(source,i)
            self.fix_line_continuation(source, i)
            self.fix_exponents(source, i)
            
        #write new source
        with open(self.output_filename, 'wb') as f:
            for line in source:
                f.write(line+'\n')
                        
    def remove_new_lines(self,source,i):
        source[i] = re.sub('[\r\n]','', source[i])
        
    def truncate_extra_linewidth(self,source,i):
        if len(source[i]) > 72:
            source[i] = source[i][:72]
            
    def fix_comments(self,source,i):
        if len(source[i]) > 0 and source[i][0] == 'C':
          source[i] = re.sub('^C','!', source[i], count=1)
            
    def fix_line_continuation(self,source,i):
        continuation_type = self.find_continuation_type(source,i)
        
        #if no line continuation found, return
        if not continuation_type:
            return
        
        #debug
        if continuation_type != "generic":
            print "continuation_type:", continuation_type
            print "source lines: \n",source[i-1]+'\n',source[i]+'\n'
        
        #add continuation to last line
        source[i-1] = source[i-1] + '&'
        
        #add appropriate continuation to current line
        if continuation_type == "hollerith":
            source[i] = self.re_line_continuation.sub('\g<1> &\g<3>', source[i], count=1)
        elif continuation_type == "var" or continuation_type == "number" :
            source[i] = self.re_line_continuation.sub('\g<1> \g<3>&', source[i], count=1)
        elif continuation_type == "generic":
            source[i] = self.re_line_continuation.sub('\g<1> &\g<3>', source[i], count=1)
        else:
            raise Exception("unknown continuation type")
        
    def fix_exponents(self,source,i):
        source[i] = self.re_exponent_old.sub('\g<1>+\g<2>', source[i])
        
    def find_continuation_type(self,source,i):
        '''
        Finds line continuation type: hollerith, number, or generic
        if not a line continuation, return None
        '''
        if not (len(source[i]) > 5 and self.re_line_continuation.match(source[i]) and i>0):
            return None
        
        # test for hollerith continuation
        for hollerith in self.re_hollerith.finditer(source[i-1]):
            hollerith_end = hollerith.end(1)+int(hollerith.group(2))+1
            prev_line_length = len(source[i-1])-1
            #print "hollerith wrap detected"
            #print "\tline number:", i # note this is prev line number (i-1)+1 since starts at 0
            #print "\tline length:", prev_line_length
            #print "\thollerith end:", hollerith_end
            if (hollerith_end > prev_line_length):
#                print "hollerith wrap detected"
#                print "\tline number:", i # note this is prev line number (i-1)+1 since starts at 0
#                print "\tline length:", prev_line_length
#                print "\thollerith end:", hollerith_end
                return "hollerith"
                
        #var continuation
        if self.re_var_begin.match(source[i]) and self.re_var_end.match(source[i-1]):
            return "var"
        
        #number continuation
        if self.re_number_begin.match(source[i]) and self.re_number_end.match(source[i-1]):
            return "number"
        
        return "generic"
        
    @classmethod
    def from_argv(cls,argv):
        '''
        Constructor from command line arguments
        '''
        sys.argv = argv
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('input_filename', metavar='input_file', help='the input filename')
        parser.add_argument('output_filename', metavar='output_file', help='the output filename')
        parser.add_argument('--style', dest='style', action='store_const',
                            const=True,default="test", help='style option')
        args = parser.parse_args()
        return cls(args.input_filename,args.output_filename,args.style)
         
if __name__ == '__main__':
    Fixed2Free.from_argv(sys.argv)