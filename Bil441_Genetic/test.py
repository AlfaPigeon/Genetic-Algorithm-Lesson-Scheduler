import random
from pg import DB
import copy
import matplotlib.pyplot as plt
from joblib import dump, load
from multiprocessing import Pool, freeze_support
import time
from libgenetic import *


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

def evaluate_paralel(gen, genes):
    gen.set_fitness(0)
    for gen2 in genes:
        gen.add_fitness(gen_timehit_evaluate(gen, gen2))
        gen.add_fitness(gen_teacherhit_evaluate(gen, gen2))
        gen.add_fitness(gen_roomhit_evaluate(gen, gen2))
        gen.add_fitness(gen_teacherfreetime_evaluate(gen, gen2))

    time.sleep(0.0001)
    return gen.fitness

def evaluate_p(genom,cores):

    # Derslerin kendi aralarında çakışmaları puanlanır
    # Aynı hocanın aynı zamanda farklı yerlerde olmamalarına dikkat edilir
    # Aynı sınıfın aynı zamanda iki farklı ders için atanmadığına dikkat edilir
    # Hocaların boş zamanları ile ders zamanları uyumları kontrol edilir

    args=[]
    for gen in genom.genes:
        args.append((gen, genom.genes))
    
    p = Pool(cores)
    fit = p.starmap(evaluate_paralel, args)


    p.close()
    p.join()

    time.sleep(0.1)

    total_fitness = 0
    for f in fit:
        total_fitness += f

    genom.fitness = total_fitness

    return total_fitness
m1 = load("p50i840_m1.d")
m2 = load("p50i840_m2.d")

ev = evaluate_p(m1,12)
print(ev)