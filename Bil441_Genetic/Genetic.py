import random
from pg import DB
import threading
import copy
import matplotlib.pyplot as plt
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
        if(lesson.weeklyHour == None):
            lesson.weeklyHour = 0
        if(lesson.weeklyHour%2 == 1):
            lesson.weeklyHour = lesson.weeklyHour + 1
        lesson.weeklyHour = min(lesson.weeklyHour,6)

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
        teacher.timeIntervals = i[2]
        teacher.free_hour = 0
        for i in teacher.timeIntervals['Free_Time']:
            teacher.free_hour += int(i['end'].split(":")[0])-int(i['begin'].split(":")[0])
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

def crossover_Genom_paralel(genom1, genom2, start, end):
    for i in range(start,end):
        crossover(genom1.genes[i],genom2.genes[i]) 


def crossover_Genom_p(genom1, genom2, batch_size):
    threads = []
    index = 0
    while(index < len(genom1.genes)):
        if(index + batch_size > len(genom1.genes)):
            end =  len(genom1.genes)
        else:
            end = index + batch_size

        t = threading.Thread(target=crossover_Genom_paralel,args=(genom1,genom2,index,end))
        threads.append(t)
        t.start()
        index += batch_size
    for t in threads:
        t.join()
def crossover_Genom(genom1, genom2):
    for i in range(len(genom1.genes)):
        crossover(genom1.genes[i],genom2.genes[i])

def gen_timehit_evaluate(gen1, gen2):
   
    fitness_1 = 10
    i = 0
    while(i < len(gen1.days)):
        if(gen1.days[i] == gen2.days[i]):
            fitness_1 = fitness_1-1
        i = i+1 
    # iki genin aynı günlerde çakışması hesaplanır puan verilir 10 puandan başlanır her saat çakışma için 1 çıkarılır
    
    return fitness_1


def gen_teacherhit_evaluate(gen1, gen2):
    
    fitness_1 = 0
    i = 0
    if(gen1.branch.teacher != gen2.branch.teacher):
        fitness_1 = 1
    else:
        while(i < len(gen1.days)):
            if(gen1.days[i] == gen2.days[i]):
                fitness_1 = 2
                begin_1 = int(gen1.times[i]['begin'].split(':')[0])
                begin_2 = int(gen2.times[i]['begin'].split(':')[0])
                if(begin_1 > begin_2):
                    if(begin_1-begin_2 < 2):
                        fitness_1 = 0
                        break
                elif(begin_2 > begin_1):
                    if(begin_2-begin_1 < 2):
                        fitness_1 = 0
                        break
                elif(begin_1 == begin_2):
                        fitness_1 = 0
                        break
            i = i+1
    # hocalar farklıysa 10 puan verilir, hocalar aynıyda ve çakışma yoksa 20, hocalar aynı ve çakışma varsa 0
    
    return fitness_1


def gen_roomhit_evaluate(gen1, gen2):

    fitness_1 = 0
    i = 0
    room_same = [0, 0, 0]
    while(i < len(gen1.rooms)):
        if(gen1.rooms[i] == gen2.rooms[i]):
            room_same[i] = 1
        i += 1
    i = 0
    while(i < len(room_same)):
        if(room_same[i] == 0):
            fitness_1 = fitness_1 + 1
        i = i+1
    i = 0
    while(i < len(room_same)):

        if(room_same[i] == 1):
            fitness_1 = fitness_1 + 2
            begin_1 = int(gen1.times[i]['begin'].split(':')[0])
            begin_2 = int(gen2.times[i]['begin'].split(':')[0])
            if(begin_1 > begin_2):
                if(begin_1-begin_2 < 2):
                    fitness_1 = fitness_1 - 2
                    i += 1
                    continue
            elif(begin_2 > begin_1):
                if(begin_2-begin_1 < 2):
                    fitness_1 = fitness_1 - 2
                    i += 1
                    continue
            elif(begin_1 == begin_2):
                fitness_1 = fitness_1 - 2
                i += 1
                continue
        i = i+1
    # odalar farklıysa 10 puan verilir, odalar aynıyda ve çakışma yoksa 20, odalar aynı ve çakışma varsa 0
    return fitness_1

def evaluate_paralel(gen, genes ):
    
    for gen2 in genes:
        gen.fitness += gen_timehit_evaluate(gen, gen2)/100
        gen.fitness += gen_teacherhit_evaluate(gen, gen2)/100
        gen.fitness += gen_roomhit_evaluate(gen, gen2)/100


def evaluate_p(genom):

    # Derslerin kendi aralarında çakışmaları puanlanır
    # Aynı hocanın aynı zamanda farklı yerlerde olmamalarına dikkat edilir
    # Aynı sınıfın aynı zamanda iki farklı ders için atanmadığına dikkat edilir
    # Hocaların boş zamanları ile ders zamanları uyumları kontrol edilir
    
    for gen in genom.genes:
        threading.Thread(target=evaluate_paralel,args=(gen, genom.genes)).start()

    total_fitness = 0
    for gen in genom.genes:
        total_fitness += gen.fitness

    genom.fitness = total_fitness

    return total_fitness


def evaluate(genom):

    # Derslerin kendi aralarında çakışmaları puanlanır
    # Aynı hocanın aynı zamanda farklı yerlerde olmamalarına dikkat edilir
    # Aynı sınıfın aynı zamanda iki farklı ders için atanmadığına dikkat edilir
    # Hocaların boş zamanları ile ders zamanları uyumları kontrol edilir
    
    for gen in genom.genes:
        for gen2 in genom.genes:
            gen.fitness += gen_timehit_evaluate(gen, gen2)/10000000
            gen.fitness += gen_teacherhit_evaluate(gen, gen2)/10000000
            gen.fitness += gen_roomhit_evaluate(gen, gen2)/10000000

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
                branch.id = "B_"+str(branch.branchNumber)+"_L_"+str(lesson.id)
                branch.teacher = t
                branch.size = quota if(
                    lesson.maxQuota-quota >= 0) else lesson.maxQuota
                lesson.maxQuota -= branch.size

                lesson.branches.append(branch)
                branches.append(branch)

    database.Branches = branches

fitness_data = []
def init_Genetic(db, pool, pool_size, branch_size, iteration):

    importDB(db)
    init_Branches(db, branch_size)
    pool = generate_randPool(db, pool_size)
    max1 = None
    for i in range(iteration):
        max1 = pool[0]
        max2 = pool[1]
        min1 = pool[2]
        min2 = pool[3]
        maxf = 0
        for genom_index in range(len(pool)):
            fit = evaluate(pool[genom_index])
            if(fit >= max1.fitness):
                max1 = pool[genom_index]
            elif(fit >= max2.fitness):
                max2 = pool[genom_index]
            elif(fit <= min1.fitness):
                min1 = pool[genom_index]
            elif (fit >= min2.fitness):
                min2 = pool[genom_index]
            maxf = max(fit,maxf)
        fitness_data.append(maxf)
        c1 = copy.deepcopy(max1)
        c2 = copy.deepcopy(max2)    
        crossover_Genom(c1,c2)
        pool.remove(min1)
        pool.remove(min2)
        pool.append(c1)
        pool.append(c2)
    return max1        


db = Database()
pool_size = 25
branch_size = 100
iteration = 100
pool = []
init_Genetic(db, pool, pool_size, branch_size, iteration)

print(fitness_data)

plt.plot(fitness_data)
plt.show()