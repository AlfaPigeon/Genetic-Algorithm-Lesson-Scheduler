import SmartPlannerUtils.*;
import java.util.*;

public class Main {


    private static ArrayList<Teacher> teacherList;
    private static ArrayList<Room> roomList;
    private static ArrayList<Lesson> lessonList;

    private static PriorityQueue<Lesson> lessonPriorityQueue;
    public static void main(String[]args){

        Setup();
        BackTrackingFit();
    }



    private static void Setup(){
        teacherList= new ArrayList<Teacher>();
        roomList= new ArrayList<Room>();
        lessonList= new ArrayList<Lesson>();

        getTeachers();
        getRooms();
        getLessons();

        lessonPriorityQueue = new PriorityQueue<Lesson>(){
            @Override
            public Comparator<? super Lesson> comparator() {
                return new Comparator<Lesson>() {
                    public int compare(Lesson o1, Lesson o2) {
                        return o1.maxQuota/o1.priority - o2.maxQuota/o2.priority;
                    }
                };}};

        lessonPriorityQueue.addAll(lessonList);



    }

    private static void BackTrackingFit() {

        // Burdan aynı isimle bir recursive arama yapılcak

    }
    private static void getTeachers(){

        // Hocalar listeye yerleştirilicek

    }
    private static void getRooms(){

        // Sınıflar listeye yerleştirilicek

    }
    private static void getLessons(){

        // Dersler listeye yerleştirilicek

    }

}
