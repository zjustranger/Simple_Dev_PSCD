class Bird:
    def __init__(self):
        self.hungry = True
    def eat(self):
        if self.hungry:
            print('delicious!')
            self.hungry = False
        else:
            print('no, thanks')
            self.hungry = True

class SingBird(Bird):
    def __init__(self):
        super().__init__()
    def sing(self):
        print('Squawk!')


# b = SingBird()
# b.sing()
# b.eat()
# b.eat()
# b.eat()
# b.eat()

class A:
    def __init__(self):
        print('A was called once.')

class B(A):
    def __init__(self):
        super().__init__()
        self.p1 = 'p1'
    def action1(self):
        print(self.p2)
    def action2(self):
        print(self.p2)

class C(A):
    def __init__(self):
        super().__init__()
        self.p2 = 'p2'
    def action1(self):
        print(self.p2)
    def action2(self):
        print(self.p2)
class D(B, C):
    def __init__(self):
        super().__init__()

d = D()
d.action1()
d.action2()

