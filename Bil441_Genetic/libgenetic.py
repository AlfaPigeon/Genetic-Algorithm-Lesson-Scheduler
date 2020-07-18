class Lesson(object):
    def __init__(self):
        self.name = ""
        self.id = ""
        self.weeklyHour = 2
        self.maxQuota = 0
        self.priority = 0
        self.numofbranch = 0
        self.branches = []


class Room(object):
    def __init__(self):
        self.maxSize = 0
        self.id = ""
        self.name = ""


class Teacher(object):
    def __init__(self):
        self.name = ""
        self.id = ""
        self.lessons = []
        self.timeIntervals = {}
        self.free_hour = 0


class Branch(object):
    def __init__(self):
        self.id = ""
        self.size = 0
        self.branchNumber = 0
        self.teacher = Teacher()
        self.timeIntervals = {}
        self.room = Room()
        self.lesson = None

class Branch_gen(object):
    def __init__(self):
        self.fitness = 0
        self.branch = Branch()
        self.days = []
        self.times = []
        self.rooms = []
    def set_fitness(self,fit):
        self.fitness = fit
    def add_fitness(self,fit):
        self.fitness += fit
class Genom(object):
    def __init__(self):
        self.fitness = 0
        self.genes = []


class Database(object):
    def __init__(self):
        self.Teachers = []
        self.Branches = []
        self.Rooms = []
        self.Lessons = []
