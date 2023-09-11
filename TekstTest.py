class Primitive:
    def __init__(self,name,id,*args):
        self.punkty = args
        self.id = id
        self.name = name
        if len(args) >= 3:
            self.p1 = args[0]
            self.p2 = args[1]
            self.p3 = args[2]
        if len(args) >= 4:
            self.p4 = args[3]

    def __str__(self):
        return f"{self.name}_{self.id}"

    def get_id(self):
        return self.id
    
    def get_points(self):
        if len(self.punkty) == 3:
            return self.p1, self.p2, self.p3
        elif len(self.punkty) == 4:
            return self.p1, self.p2, self.p3, self.p4


Box = Primitive("box",123,1,2,3,4)
print(Box)