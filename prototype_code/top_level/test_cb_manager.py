from libs.callback_handling.callback_manager import CallbackManager

class CBMTest:
    def __init__(self):
        print("Creating CBMTest Class")
        self.cbm = CallbackManager(['instruction_read', 'instruction_executed'], self)
        
        self.cbm.add_instruction_read_callback(self.t1)
        self.add_instruction_read_callback(self.t2)

    def t1(self):
        print("I am t1")

    def t2(self):
        print("I am t2")

if __name__ == '__main__':
    cbmt = CBMTest()
    import pdb; pdb.set_trace()
