import random
from pg import DB
import copy
import matplotlib.pyplot as plt
from joblib import dump, load
from multiprocessing import Pool, freeze_support
import time
from libgenetic import *
import uuid


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
def hit_count(genom):
    branchcount = 0
    hit = 0
    for g1 in genom.genes:

        if(len(g1.times) == 0):
            continue
        else:
            print(g1.times)
            branchcount += 1

        for g2 in genom.genes:
            for i in range(3):
                for j in range(3):
                    if(g1.days[i]==g2.days[j]):
                        start1 = int(g1.times[i]['begin'].split(":")[0])
                        start2 = int(g2.times[j]['begin'].split(":")[0])
                        end1 = int(g1.times[i]['end'].split(":")[0])
                        end2 = int(g2.times[j]['end'].split(":")[0])
                        if(max(start1,start2) < min(end1,end2)):
                            hit += 1

    print(len(genom.genes),branchcount)
    return (hit/branchcount)*100/branchcount   
def hit_countDB():
    hit = 0
    db = DB(dbname='Bil_441', host='localhost', port=5432, user='postgres', passwd='123')
    branches = db.query("SELECT id FROM public.\"Branch\"")
    for branch1 in branches.getresult():
        for branch2 in branches.getresult():
            time1 = db.query("SELECT \"time-interval\" FROM public.\"Branch\" where id=\'"+branch1[0]+"\'").getresult()[0][0]
            time2 = db.query("SELECT \"time-interval\" FROM public.\"Branch\" where id=\'"+branch2[0]+"\'").getresult()[0][0]
            for t1 in time1['Time']:
                for t2 in time2['Time']:
                    if(t1['day']==t2['day']):
                        start1 = int(t1['begin'].split(":")[0])
                        start2 = int(t1['begin'].split(":")[0])
                        end1 = int(t1['end'].split(":")[0])
                        end2 = int(t2['end'].split(":")[0])
                        if(max(start1,start2) < min(end1,end2)):
                            hit += 1

    raw = hit / len(branches.getresult())
    return (raw*100)/len(branches.getresult())
def exportDB(Genom):
    db = DB(dbname='Bil_441', host='localhost', port=5432, user='postgres', passwd='123')

    for gen in Genom.genes:
        id = uuid.uuid4()
        teacherid = gen.branch.teacher.id
        time = {"Time":[]}
        rooms = []
        size = gen.branch.size
        lessonid = gen.branch.lesson.id
        weeklyHour = int(db.query('SELECT \"weekly-hour\" FROM public.\"Lesson\" where id=\''+str(gen.branch.lesson.id)+'\'').getresult()[0][0])
        
        if(weeklyHour % 2 == 1):
            weeklyHour += 1
        if(weeklyHour > 6):
            weeklyHour = 6
        for i in range(int(weeklyHour/2)):
            time['Time'].append({"day":gen.days[i],"begin":gen.times[i]['begin'],"end":gen.times[i]['end']})
            rooms.append(str(gen.rooms[i].id))
        
        db.query("INSERT INTO public.\"Branch\"(size, \"teacher-id\", \"time-interval\", \"rooms-id\", id, \"lesson-id\") VALUES ("+str(size)+", \'"+str(teacherid)+"\', \'"+str(time).replace("\'","\"")+"\', \'"+str(rooms).replace("[","{").replace("]","}").replace("\'","\"")+"\', \'"+str(id)+"\',\'"+str(lessonid)+"\')")

    


m1 = load("data/p10i3000_wipe_m1.d")

exportDB(m1)

#print(hit_countDB())