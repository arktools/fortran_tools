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
    
    #misc regex's
    re_line_continuation = re.compile('^(\s\s\s\s\s)([^\s])([\s]*)')
    re_hollerith = re.compile('[\s,]((\d+)H)')
    re_number_spacing = re.compile('([^A-Za-z][\d.]+)[\s]([\d.]+[^A-Za-z])')
    re_f77_comment = re.compile('^[cC]')
    re_f90_comment = re.compile('^!')
    
    #variable regex
    re_var_end = re.compile('.*[A-Za-z0-9]+$')
    re_var_begin = re.compile('(^\s\s\s\s\s)([^\s])([\s]*)([A-Za-z]+[0-9]?)+')
    
    #number regex
    re_number_end = re.compile('.*[\d.eE]+$')
    re_number_begin = re.compile('(^\s\s\s\s\s)([^\s])([\s]*)[\d.eE]+')
    
    #exponent regex
    re_exponent_old = re.compile('([\d.]E)[\s]([\d]+)')

    def __init__(self,input_filename,output_filename,style):
        '''
        Constructor
        '''
        self.input_filename=input_filename
        self.output_filename=output_filename
        self.style=style
        

        
        self.process()
        
    def process(self):
        
        #read source
        with open(self.input_filename, 'rb') as f:
            source = f.readlines()

        #fix source code
        for i in xrange(len(source)):
            line = source[i]
            line = self.remove_new_line(line)
            line = self.fix_comment(line)
            line = self.truncate_extra_linewidth(line)
            line = self.fix_exponents(line)
            
            if self.is_line_continuation(line):
                prev_line_index = self.find_prev_line(source,i)
                prev_line = source[prev_line_index]
                line,prev_line = self.fix_line_continuation(line,prev_line)
                source[prev_line_index] = prev_line
            
            line = self.fix_number_spacing(line)
            source[i] = line
            
        #write new source
        with open(self.output_filename, 'wb') as f:
            for line in source:
                f.write(line+'\n')
                        
    @staticmethod
    def is_line_continuation(line):
        if len(line) > 5 and Fixed2Free.re_line_continuation.match(line):
            return True
        return False
    
    @staticmethod
    def find_prev_line(source,i):
        '''  
        find first non-commented previous line
        '''
        if i>0:
            for j in range(i-1, -1, -1): # -1 since python uses [i-1,-1)
                if not Fixed2Free.is_f90_comment(source[j]):
                    return j
        return None
        
    @staticmethod
    def remove_new_line(line):
        return re.sub('[\r\n]','', line)
        
    @staticmethod
    def truncate_extra_linewidth(line):
        if len(line) > 72:
            line = line[:72]
        return line
            
    @staticmethod
    def is_f77_comment(line):
        return Fixed2Free.re_f77_comment.match(line)
        
    @staticmethod
    def is_f90_comment(line):
        return Fixed2Free.re_f90_comment.match(line)
            
    @staticmethod
    def fix_comment(line):
        if Fixed2Free.is_f77_comment(line):
            line = re.sub('^[Cc]','!', line, count=1)
        return line
            
    @staticmethod
    def fix_line_continuation(line,prev_line):
        continuation_type = Fixed2Free.find_continuation_type(line,prev_line)
        
        #if no line continuation found, return
        if not continuation_type:
            return (line,prev_line)
        
        #debug
#        if continuation_type != "generic":
#            print "continuation_type:", continuation_type
#            print "source lines: \n",prev_line+'\n',line+'\n'
        
        #add appropriate continuation to current line
        if continuation_type == "hollerith":
            line = Fixed2Free.re_line_continuation.sub('\g<1>&\g<3>', line, count=1)
        elif continuation_type == "var" or continuation_type == "number" :
            line = Fixed2Free.re_line_continuation.sub('\g<1>\g<3>&', line, count=1)
        elif continuation_type == "generic":
            line = Fixed2Free.re_line_continuation.sub('\g<1>&\g<3>', line, count=1)
        else:
            raise Exception("unknown continuation type")
        
        #add line continuation to previous line
        prev_line = prev_line + '&'
        
        return (line,prev_line)
        
    @staticmethod
    def fix_exponents(line):
        return Fixed2Free.re_exponent_old.sub('\g<1>+\g<2>', line)
    
    @staticmethod
    def fix_number_spacing(line):
        return Fixed2Free.re_number_spacing.sub('\g<1>\g<2>', line)
        
    @staticmethod
    def find_continuation_type(line,prev_line):
        '''
        Finds line continuation type: hollerith, number, or generic
        if not a line continuation, return None
        '''
        if not Fixed2Free.is_line_continuation(line):
            return None
        
        # test for hollerith continuation
        for hollerith in Fixed2Free.re_hollerith.finditer(prev_line):
            hollerith_end = hollerith.end(1)+int(hollerith.group(2))+1
            prev_line_length = len(prev_line)-1
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
        if Fixed2Free.re_var_begin.match(line) and Fixed2Free.re_var_end.match(prev_line):
            return "var"
        
        #number continuation
        if Fixed2Free.re_number_begin.match(line) and Fixed2Free.re_number_end.match(prev_line):
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