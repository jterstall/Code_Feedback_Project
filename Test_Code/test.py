import sys
sys.path.insert(0, r'/home/jterstall/Documents/Afstudeerproject_AI/Code/My_Code')
import ICP_decorator
import hello

@ICP_decorator.ICP_decorator
def main():
    hello.main()

if __name__ == '__main__':
    main()
ICP_decorator.pass_result()
