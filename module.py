
class Module:
    ''' A python class to store the data of a verilog module '''

    def __init__(self, name ="", body=[], header = [], ports=[], parameters=[]):
        self.name = name # Name of module
        self.header = header # Tokens of module header, pre-processed
        self.body = body # Tokens of module body, pre-processed
        self.ports = ports # List of ports by name (str), in declaration order
        self.parameters = parameters # List of parameters by name (str)
        