import sys
sys.path.insert(0, r'/home/jterstall/Documents/Afstudeerproject_AI/Code/My_Code')
import ICP_decorator
@ICP_decorator.ICP_decorator
def goodbye(name):
    print "Goodbye: %s" % name
