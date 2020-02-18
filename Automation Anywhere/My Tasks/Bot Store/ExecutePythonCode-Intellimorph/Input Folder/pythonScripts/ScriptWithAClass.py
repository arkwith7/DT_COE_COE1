import sys

class clsMathematicalOperations:

    @staticmethod
    def multiply():
        return int(sys.argv[1]) * int(sys.argv[2])

    def returnFixedValue(self):
        return 100


print(clsMathematicalOperations.multiply())