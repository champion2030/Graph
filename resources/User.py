class User_Class:
    A = []
    u = []

    def take_matrix(self, B):
        self.A.clear()
        for line in B:
            self.A.append(line)

    def give_matrix(self):
        return self.A

    def setIdentificator(self, b):
        self.u.clear()
        self.u.append(b)

    def get_identificator(self):
        if len(self.u) == 0:
            return 3
        return self.u[0]
