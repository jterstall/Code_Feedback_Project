import sys
sys.path.insert(0, r'/home/jterstall/Documents/Afstudeerproject_AI/Code/My_Code')
import ICP_decorator
import hello
import numpy

@ICP_decorator.ICP_decorator
def main():
    for _ in range(2):
        hello.main()

if __name__ == '__main__':
    main()
ICP_decorator.pass_result()
