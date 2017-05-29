import sys
sys.path.insert(0, r'/home/jterstall/Documents/Afstudeerproject_AI/Code/My_Code')
import ICP_decorator
import goodbye

class A:
    @ICP_decorator.ICP_decorator
    def call_b(self):
        B().greet()


class B:
    @ICP_decorator.ICP_decorator
    def greet(self):
        pass

# COMMENT
@ICP_decorator.ICP_decorator
# Comment
def greetings(greet):
    pass
    # COMMENT?


@ICP_decorator.ICP_decorator
def main():
    A().call_b()
    greetings("Greetings")
    goodbye.goodbye("You")


if __name__ == '__main__':
    main()
