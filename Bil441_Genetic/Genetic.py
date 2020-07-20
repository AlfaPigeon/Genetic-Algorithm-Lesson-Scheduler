import random
from pg import DB
import copy
import matplotlib.pyplot as plt
from joblib import dump, load
from multiprocessing import Pool, freeze_support
import time
from libgenetic import *
import numpy as np

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
        lesson.numofbranch = 0 if(i[6] == None) else int(i[6])
        lesson.maxQuota = int(i[3])
        lesson.priority = int(i[4])
        database.Lessons.append(lesson)

    query = db.query('Select * from public.\"Room\"')
    for i in query.getresult():
        room = Room()
        room.maxSize = 0 if i[2] == None else i[2]
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
    

    r1 = copy.copy(gen1)
    r2 = copy.copy(gen2)


    if(random.randint(0, 1) == 0):
        r1.days = gen1.days
        r2.days = gen2.days
    else:
        r1.days = gen2.days
        r2.days = gen1.days
    if(random.randint(0, 1) == 0):
        r1.times = gen1.times
        r2.times = gen2.times
    else:
        r1.times = gen2.times
        r2.times = gen1.times
    if(random.randint(0, 1) == 0):
        r1.rooms = gen1.rooms
        r2.rooms = gen2.rooms
    else:
        r1.rooms = gen2.rooms
        r2.rooms = gen1.rooms


    return (r1, r2)
def crossover_Genom_paralel(gen1, gen2):
    return crossover(gen1,gen2)

def crossover_Genom_p(genom1, genom2, cores):

    offs1 = Genom()
    offs2 = Genom()
    args = []
    for i in range(len(genom1.genes)):
        args.append((genom1.genes[i],genom1.genes[i]))

    p = Pool(cores)
    fit = p.starmap(crossover_Genom_paralel, args)

    p.close()
    p.join()   

    for (i,j) in fit:
        offs1.genes.append(i)
        offs2.genes.append(j)

    return (offs1,offs2)
def crossover_Genom(genom1, genom2):
    offs1 = Genom()
    offs2 = Genom()
    for i in range(len(genom1.genes)):
        if(genom1.genes[i].branch.id == genom2.genes[i].branch.id):
            g1,g2 = crossover(genom1.genes[i],genom2.genes[i])
            offs1.genes.append(g1)
            offs2.genes.append(g2)
        else:
            print("mismatched",genom1.genes[i].branch.id,genom2.genes[i].branch.id)
    return (offs1,offs2)

def gen_timehit_evaluate(gen1, gen2):
   
    fitness = 9
    for i in range(len(gen1.days)):
        for j in range(len(gen2.days)):
            if(gen1.days[i]==gen2.days[j]):
                g1time = gen1.times[i]
                g2time = gen2.times[j]
                start1 = int(g1time['begin'].split(":")[0])
                start2 = int(g2time['begin'].split(":")[0])
                end1 = int(g1time['end'].split(":")[0])
                end2 = int(g2time['end'].split(":")[0])
                if(max(start1,start2) <= min(end1,end2)):
                    fitness -= 3
    
    # iki genin aynı günlerde çakışması hesaplanır puan verilir 9 puandan başlanır her saat çakışma için 3 çıkarılır
    return fitness
def gen_teacherhit_evaluate(gen1, gen2):
    
    fitness = 6

    if(gen1.branch.teacher.id == gen2.branch.teacher.id):
        for i in range(len(gen1.days)):
            for j in range(len(gen2.days)):
                if(gen1.days[i]==gen2.days[j]):
                    g1time = gen1.times[i]
                    g2time = gen2.times[j]
                    start1 = int(g1time['begin'].split(":")[0])
                    start2 = int(g2time['begin'].split(":")[0])
                    end1 = int(g1time['end'].split(":")[0])
                    end2 = int(g2time['end'].split(":")[0])
                    if(max(start1,start2) <= min(end1,end2)):
                        fitness -= 3
    else:
        fitness += 3


    
    return fitness
def gen_teacherfreetime_evaluate(gen1, gen2):
    
    fitness = 0

    teacher1time = gen1.branch.teacher.timeIntervals['Free_Time']
    teacher2time = gen2.branch.teacher.timeIntervals['Free_Time']

    for i in range(len(gen1.days)):
        for j in teacher1time:
            if(j['day'] == gen1.days[i]):
                start1 = int(j['begin'].split(":")[0])
                start2 = int(j['begin'].split(":")[0])
                end1 = int(j['end'].split(":")[0])
                end2 = int(j['end'].split(":")[0])
                if(set((range(start1,end1))).issubset(range(start2,end2))):
                    fitness += 2         

    for i in range(len(gen2.days)):
        for j in teacher2time:
            if(j['day'] == gen2.days[i]):
                start1 = int(j['begin'].split(":")[0])
                start2 = int(j['begin'].split(":")[0])
                end1 = int(j['end'].split(":")[0])
                end2 = int(j['end'].split(":")[0])
                if(set((range(start1,end1))).issubset(range(start2,end2))):
                    fitness += 2  




    return fitness
def gen_roomhit_evaluate(gen1, gen2):

    fitness = 10
    for i in range(len(gen1.days)):
        for j in range(len(gen2.days)):
            if(gen1.days[i]==gen2.days[j] and gen1.rooms[i].id == gen2.rooms[j].id):
                g1time = gen1.times[i]
                g2time = gen2.times[j]
                start1 = int(g1time['begin'].split(":")[0])
                start2 = int(g2time['begin'].split(":")[0])
                end1 = int(g1time['end'].split(":")[0])
                end2 = int(g2time['end'].split(":")[0])
                if(max(start1,start2) <= min(end1,end2)):
                    fitness -= 3     
   

    for room in gen1.rooms:
        if(room.maxSize < gen1.branch.size):
            fitness -= 2

    for room in gen2.rooms:
        if(room.maxSize < gen2.branch.size):
            fitness -= 2


    return fitness
def gen_break_evaluate(gen1, gen2):
    fitness = 0
    #launch break
    for t in gen1.times:
        start = int(t['begin'].split(":")[0])
        end = int(t['end'].split(":")[0])
        if(max(start,12) >= min(end,13)):
            fitness += 1

    for i in range(len(gen1.days)):
        for j in range(len(gen2.days)):
            if(gen1.days[i] == gen2.days[j]):
                g1time = gen1.times[i]
                g2time = gen2.times[j]
                start1 = int(g1time['begin'].split(":")[0])
                start2 = int(g2time['begin'].split(":")[0])
                end1 = int(g1time['end'].split(":")[0])
                end2 = int(g2time['end'].split(":")[0])
                if(max(start1,start2) > min(end1,end2)):
                    distance = abs(start1 - end2)
                    fitness += distance/gen1.branch.lesson.priority                 
    return fitness
def evaluate_paralel(gen, genes, beta):
    gen.set_fitness(0)
    for gen2 in genes:
        gen.add_fitness(gen_timehit_evaluate(gen, gen2)/(gen.branch.lesson.priority*beta))
        gen.add_fitness(gen_teacherhit_evaluate(gen, gen2)/(gen.branch.lesson.priority*beta))
        gen.add_fitness(gen_roomhit_evaluate(gen, gen2)/(gen.branch.lesson.priority*beta))
        gen.add_fitness(gen_teacherfreetime_evaluate(gen, gen2)/(gen.branch.lesson.priority*beta))
        gen.add_fitness(gen_break_evaluate(gen, gen2)/(gen.branch.lesson.priority*beta))
    return gen.fitness

def evaluate_p(genom,cores,beta):

    # Derslerin kendi aralarında çakışmaları puanlanır
    # Aynı hocanın aynı zamanda farklı yerlerde olmamalarına dikkat edilir
    # Aynı sınıfın aynı zamanda iki farklı ders için atanmadığına dikkat edilir
    # Hocaların boş zamanları ile ders zamanları uyumları kontrol edilir

    total_fitness = 0
    args=[]
    for gen in genom.genes:
        args.append((gen, genom.genes, beta))
    
    p = Pool(cores)
    fit = p.starmap(evaluate_paralel, args)


    p.close()
    p.join()

    time.sleep(0.1)

    
    for f in fit:
        total_fitness += f

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


def init_Branches(database):
    # Gereken branch sayısını yaratır. Hocanın zamanını ve dersi almak isteyen öğrenci sayısını göz önünde bulundurur.
    branches = []
    for t in database.Teachers:
        for lesson in t.lessons:
            opened = 0
            for bcont in range(lesson.numofbranch):
                if(t.free_hour >= lesson.weeklyHour and lesson.maxQuota > 0):
                    t.free_hour -= lesson.weeklyHour
                    branch = Branch()
                    branch.branchNumber = len(lesson.branches)
                    branch.id = "B_"+str(branch.branchNumber)+"_L_"+str(lesson.id)
                    branch.teacher = t
                    size = int(lesson.maxQuota/(lesson.numofbranch+len(lesson.branches)))
                    branch.size = size if(lesson.maxQuota-size >= 0) else lesson.maxQuota
                    lesson.maxQuota -= branch.size
                    branch.lesson = lesson
                    branch.lessonid = lesson.id
                    opened += 1
                    lesson.branches.append(branch)
                    branches.append(branch)
            lesson.numofbranch -= opened
    database.Branches = branches


fitness_data = []
def init_Genetic(db, pool, pool_size, iteration, cores, beta):

    importDB(db)
    init_Branches(db)
    pool = generate_randPool(db, pool_size)

    pool[0] = load("data/p10i3000_wipe_m1.d")#pretrained
    #pool[1] = load("p50i840_m2.d")#pretrained

    maxf_old = -1
    maxf = -1
    stuckcounter = 0
    for i in range(iteration):

        print("iteration:",i+1,"fit:",maxf)

        for genom_index in range(len(pool)):
            fit = evaluate_p(pool[genom_index],cores,beta)        
            maxf = max(fit,maxf)
        fitness_data.append(maxf)

        if( maxf == maxf_old ):
            stuckcounter += 1 
        maxf_old = maxf

        pool.sort(key=lambda x: x.fitness, reverse=True)
        c1, c2 = crossover_Genom(pool[0], pool[1])
        c3, c4 = crossover_Genom(random.choice(pool), random.choice(pool))

        pool.pop()
        pool.pop()
        pool.pop()
        pool.pop()

        pool.append(c1)
        pool.append(c2)
        pool.append(c3)
        pool.append(c4)

        if(stuckcounter > 5):
            fittest = pool[0]
            pool = generate_randPool(db, pool_size)#Wipe everyone
            pool[0] = fittest 
            stuckcounter = 0
    
    for genom_index in range(len(pool)):
        fit = evaluate_p(pool[genom_index],cores,beta)        
        maxf = max(fit,maxf)
    pool.sort(key=lambda x: x.fitness, reverse=True)
    return (pool[0],pool[1])        


db = Database()
pool_size = 15
branch_size = 120
iteration = 5
cores = 20
beta = 1000
pool = []
(m1,m2) = init_Genetic(db, pool, pool_size, iteration, cores, beta)


#dump(m1, 'data/p10i3000_wipe_m1.d')
#dump(m2, 'data/p10i3000_wipe_m2.d')

#print(fitness_data)

plt.plot(fitness_data)
#plt.savefig('data/p10i3000_wipe.png')

plt.show()

