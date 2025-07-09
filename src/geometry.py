class Point:
    def __init__(self,id,x,y,z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"ID: {self.id} [{self.x},{self.y},{self.z}]"

    def get_pos(self):
        return self.x, self.y, self.z
    
    def get_id(self):
        return self.id
    
class Rectangle:
    def __init__(self,id,p1,p2,p3,p4):
        self.id = id
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    def __str__(self):
        return f"quad_{self.id}"
    
    def BIG(self):
        return "SHELL_QUADRILATERAL"

    def get_id(self):
        return self.id
    
    def get_points(self):
        return self.p1, self.p2, self.p3, self.p4

class Triangle:
    def __init__(self,id,p1,p2,p3):
        self.id = id
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        
    def __str__(self):
        return f"tria_{self.id}"
    
    def BIG(self):
        return f"SHELL_TRIANGLE"
    
    def get_id(self):
        return self.id
    
    def get_points(self):
        return self.p1, self.p2, self.p3

class Primitive:
    def __init__(self,name,id,*args):
        self.id = id
        self.name = name.lower()
        self.node_num = len(args)
        if len(args) >= 3:
            self.p1 = args[0]
            self.p2 = args[1]
            self.p3 = args[2]
        if len(args) >= 4:
            self.p4 = args[3]

    def __str__(self):
        return f"{self.name}_{self.id}"
    
    def BIG(self):
        return f"SHELL_{self.name.upper()}"

    def get_id(self):
        return self.id

    def get_points(self):
        if self.node_num == 3:
            return self.p1, self.p2, self.p3
        if self.node_num == 4:
            return self.p1, self.p2, self.p3, self.p4
        else:
            return "Wrong number of vertices"