import random
from pg import DB

class Lesson(object):
    def __init__(self):
        self.name = ""
        self.id = ""
        self.weeklyHour = 2
        self.maxQuota = 0
        self.priority = 0
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


class Branch_gen(object):
    def __init__(self):
        self.fitness = 0
        self.branch = Branch()
        self.days = []
        self.times = []
        self.rooms = []


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


def importDB(database):
    # postGreSQL connection
    db = DB(dbname='Bil_441', host='localhost', port=5432, user='postgres', passwd='123')

    query = db.query('Select * from public.\"Lesson\"')
    for i in query.getresult():
        lesson = Lesson()
        lesson.name = i[1]
        lesson.id = i[0]
        lesson.weeklyHour = i[2]
        lesson.maxQuota = i[3]
        lesson.priority = i[4]
        database.Lessons.append(lesson)

    query = db.query('Select * from public.\"Room\"')
    for i in query.getresult():
        room = Room()
        room.maxSize = i[2]
        room.id = i[0]
        room.name = i[1]
        database.Rooms.append(room) 

    query = db.query('Select * from public.\"Teacher\"')
    for i in query.getresult():
        teacher = Teacher()
        teacher.name = i[0]
        teacher.id = i[1]
        teacher.lessons = [j for j in database.Lessons if (j.id in i[3])]
        teacher.timeIntervals = dict(i[2])# test et
        teacher.free_hour = 0# bura ayarlanıcak
        database.Teachers.append(teacher)

    return database


def crossover(gen1, gen2):
    if(gen1.branch.id != gen2.branch.id):
        return

    if(random.randint(0, 1) == 0):
        days = gen1.days
        gen1.days = gen2.days
        gen2.days = days
    if(random.randint(0, 1) == 0):
        times = gen1.times
        gen1.times = gen2.times
        gen2.times = times
    if(random.randint(0, 1) == 0):
        rooms = gen1.rooms
        gen1.rooms = gen2.rooms
        gen2.rooms = rooms


def gen_timehit_evaluate(gen1, gen2):
    # iki genin aynı günlerde çakışması hesaplanır puan verilir 10 puandan başlanır her saat çakışma için 1 çıkarılır
    return 0


def gen_teacherhit_evaluate(gen1, gen2):
    # hocalar farklıysa 10 puan verilir, hocalar aynıyda ve çakışma yoksa 20, hocalar aynı ve çakışma varsa 0
    return 0


def gen_roomhit_evaluate(gen1, gen2):
    # odalar farklıysa 10 puan verilir, odalar aynıyda ve çakışma yoksa 20, odalar aynı ve çakışma varsa 0
    return 0


def evaluate(genom):

    # Derslerin kendi aralarında çakışmaları puanlanır
    # Aynı hocanın aynı zamanda farklı yerlerde olmamalarına dikkat edilir
    # Aynı sınıfın aynı zamanda iki farklı ders için atanmadığına dikkat edilir
    # Hocaların boş zamanları ile ders zamanları uyumları kontrol edilir

    for gen in genom.genes:
        for gen2 in genom.genes:
            gen.fitness += gen_timehit_evaluate(gen, gen2)
            gen.fitness += gen_teacherhit_evaluate(gen, gen2)
            gen.fitness += gen_roomhit_evaluate(gen, gen2)

    total_fitness = 0
    for gen in genom.genes:
        total_fitness += gen.fitness

    genom.fitness = total_fitness

    return total_fitness


def show_gen(gen):
    print(gen.days, gen.times, gen.rooms)


def generate_randDays():
    list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    random.shuffle(list)
    result = []
    result.append(list.pop())
    result.append(list.pop())
    result.append(list.pop())
    return result


def generate_randTimes():
    list = [random.randint(8, 16), random.randint(
        8, 16), random.randint(8, 16)]
    return [{"begin": str(list[0])+":30", "end":str(list[0]+2)+":30"}, {"begin": str(list[1])+":30", "end":str(list[1]+2)+":30"}, {"begin": str(list[2])+":30", "end":str(list[2]+2)+":30"}]


def generate_randRooms(db):
    return[random.choice(db.Rooms), random.choice(db.Rooms), random.choice(db.Rooms)]


def generate_randPool(db, pool_size):
    result = []
    for i in range(pool_size):
        gen_map = Genom()
        result.append(gen_map)

    for i in range(pool_size):
        for branch in db.Branches:
            gen = Branch_gen()
            gen.branch = branch
            gen.days = generate_randDays()
            gen.times = generate_randTimes()
            gen.rooms = generate_randRooms(db)
            result[i].genes.append(gen)

    return result


def init_Branches(database, quota):
    # Gereken branch sayısını yaratır. Hocanın zamanını ve dersi almak isteyen öğrenci sayısını göz önünde bulundurur.

    branches = []
    for t in database.Teachers:
        # print(t.free_hour)
        for lesson in t.lessons:
            if(t.free_hour > 0 and lesson.maxQuota > 0):
                t.free_hour -= lesson.weeklyHour
                branch = Branch()
                branch.branchNumber = len(lesson.branches)
                branch.id = "B_"+str(branch.branchNumber)+"_L_"+lesson.id
                branch.teacher = t
                branch.size = quota if(
                    lesson.maxQuota-quota >= 0) else lesson.maxQuota
                lesson.maxQuota -= branch.size

                lesson.branches.append(branch)
                branches.append(branch)

    database.Branches = branches


def init_Genetic(db, pool, pool_size, branch_size):

    importDB(db)
    return
    init_Branches(db, branch_size)
    pool = generate_randPool(db, pool_size)


db = Database()

pool_size = 500
branch_size = 100
pool = []
init_Genetic(db, pool, pool_size, branch_size)


#0,[[0,],[0,],[0,],[0,],[0,]]
#[[0,],[0,],[0,],[0,],[0,]]
#[[0,],[0,],[0,],[0,],[0,]]
#[[0,],[0,],[0,],[0,],[0,]]
#[[0,],[0,],[0,],[0,],[0,]]
#..