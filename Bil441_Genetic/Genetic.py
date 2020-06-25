import random


class Lesson(object):
    name = ""
    id = ""
    weeklyHour = 2
    maxQuota = 0
    priority = 0
    branches = []


class Room(object):
    maxSize = 0
    id = ""
    name = ""


class Teacher(object):
    name = ""
    id = ""
    lessons = []
    timeIntervals = {}
    free_hour = 0


class Branch(object):
    id = ""
    size = 0
    branchNumber = 0
    teacher = Teacher()
    timeIntervals = {}
    room = Room()


class Branch_gen(object):
    fitness = 0
    branch = Branch()
    days = []
    times = []
    rooms = []


class Genom(object):
    fitness = 0
    genes = []


class Database(object):
    Teachers = []
    Branches = []
    Rooms = []
    Lessons = []


def importDB(database):
    # postGreSQL server ile
    # Put dummy data here

    # Import Lessons
    fiz101 = Lesson()
    fiz101.id = "id_fiz101"
    fiz101.name = "Fiz 101"
    fiz101.weeklyHour = 4
    fiz101.maxQuota = 200
    fiz101.priority = 2

    # Import Rooms
    amfi3 = Room()
    amfi3.id = "id_Amfi3"
    amfi3.name = "Amfi 3"
    amfi3.maxSize = 100

    b11 = Room()
    b11.id = "b11"
    b11.name = "b11"
    b11.maxSize = 70

    # Import Teachers
    ahmet_nuri = Teacher()
    ahmet_nuri.timeIntervals = {"Free_Time": [{"day": "thursday", "begin": "15:30", "end": "18:30"}, {
        "day": "friday", "begin": "9:30", "end": "12:30"}]}
    ahmet_nuri.id = "29f7b70b-6f7a-40fc-bb52-f2fca8c395ac"
    ahmet_nuri.lessons = [fiz101]
    ahmet_nuri.name = "Ahmet Nuri Akay"
    for time in ahmet_nuri.timeIntervals['Free_Time']:
        ahmet_nuri.free_hour += int(time['end'].split(":")[0]) - \
            int(time['begin'].split(":")[0])
    # ===
    database.Lessons.append(fiz101)
    database.Rooms.append(amfi3)
    database.Rooms.append(b11)
    database.Teachers.append(ahmet_nuri)

    return


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


def evaluate(gen_pool):
    # Bir Branch gen listesi gelir. Tüm genler puanlanır ve fitness'a atama yapılır.
    # Eğer imkansız durum var ise o gen direkt 0 puan alır.
    # En son tüm gen puanları toplanır ve havuza genel bir fitness puanı verilir.

    return 0


def show_gen(gen):
    print(gen.days, gen.times, gen.rooms)


def init_Branches(database, quota):
    # Gereken branch sayısını yaratır. Hocanın zamanını ve dersi almak isteyen öğrenci sayısını göz önünde bulundurur.

    # id = ""
    # size = 0
    # branchNumber = 0
    # teacher = Teacher()
    # timeIntervals = {}
    # room = Room()

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
    init_Branches(db, branch_size)

    # Aşağısı test için
    print(db.Branches[0])

    branch = Branch()
    branch.id = "3162"
    gen1 = Branch_gen()
    gen2 = Branch_gen()
    gen1.branch = branch
    gen2.branch = branch

    gen1.days = ['monday', 'tuesday']
    gen2.days = ['wednesday', 'thursday']

    gen1.times = ['time1', 'time2']
    gen2.times = ['time3', 'time4']

    gen1.rooms = ['b10', 'b11']
    gen2.rooms = ['b12', 'b13']

    show_gen(gen1)
    show_gen(gen2)

    print("==CrossOver==========")
    crossover(gen1, gen2)

    show_gen(gen1)
    show_gen(gen2)


db = Database()
pool_size = 100
branch_size = 100
pool = []
init_Genetic(db, pool, pool_size, branch_size)
