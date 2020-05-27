package SmartPlannerUtils;

public class Lesson {

    public String name;
    public String Id;
    public int weeklyHour;
    public int maxQuota;
    public int priority;

    class Branch{

        int size;
        int branchNumber;
        Teacher teacher;
        TimeInterval[] timeIntervals;
        Room room;


    }
}
