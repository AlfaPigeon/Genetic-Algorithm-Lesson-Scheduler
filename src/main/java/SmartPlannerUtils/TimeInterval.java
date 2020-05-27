package SmartPlannerUtils;

enum Day {Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday}
public class TimeInterval {
    /**
     * (time[0]:time[1],time[2]:time[3]) Day
     */
    protected int[] time = new int[4];
    Day day;
    public TimeInterval(){
        this.time[0]=0;
        this.time[1]=0;
        this.time[2]=0;
        this.time[3]=0;
        this.day = Day.Monday;
    }

    public TimeInterval(String timeBegin,String timeEnd,Day day){
        this.time[0]= Integer.parseInt(timeBegin.trim().split(":")[0]);
        this.time[1]= Integer.parseInt(timeBegin.trim().split(":")[1]);
        this.time[2]= Integer.parseInt(timeEnd.trim().split(":")[0]);
        this.time[3]= Integer.parseInt(timeEnd.trim().split(":")[1]);
        this.day = day;
    }
}
