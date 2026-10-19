import time
from jnius import autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass('android.content.Context')
UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
Calendar = autoclass('java.util.Calendar')

def check_usage():
    activity = PythonActivity.mActivity
    if not activity:
        return
        
    mUsageStatsManager = activity.getSystemService(Context.USAGE_STATS_SERVICE)
    if not mUsageStatsManager:
        return
        
    calendar = Calendar.getInstance()
    end_time = calendar.getTimeInMillis()
    calendar.add(Calendar.DAY_OF_MONTH, -1)
    start_time = calendar.getTimeInMillis()
    
    stats = mUsageStatsManager.queryUsageStats(UsageStatsManager.INTERVAL_DAILY, start_time, end_time)
    if stats:
        for usageStats in stats:
            pkg_name = usageStats.getPackageName()
            total_time_ms = usageStats.getTotalTimeInForeground()
            total_time_sec = total_time_ms / 1000.0
            
            # Here you can compare total_time_sec with user-defined limits
            # If limit exceeded, trigger edge light overlay

if __name__ == '__main__':
    while True:
        try:
            check_usage()
        except Exception as e:
            print(f"Service error: {e}")
        time.sleep(10)