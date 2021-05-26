'''
Created on 9.9.2011

@author: japohjol
'''
from datetime import timedelta
from datetime import datetime


class TimeProsessing(object):
    """
    TimeProsessing is a test library for Robot Framework which is used for
    time operations.
    
    Author: jarkko.pohjola@nsn.com
    """
        
    def end_time(self):    
        """ Generates the ending time for aggregation testing.
        Ending time means the latest time (time_stamp) what tested
        PM data can has. At the moment ending time is the current time - 1 hour 
        """        
        end_time = datetime.now()
        end_time = end_time - timedelta(hours=1)
        minute_remainder = end_time.minute % 60
        second_remainder = end_time.second % 60
        microsecond_remainer = end_time.microsecond % 1000000    
        end_time = end_time - timedelta(minutes=minute_remainder)
        end_time = end_time - timedelta(seconds=second_remainder)
        end_time = end_time - timedelta(microseconds=microsecond_remainer)    
        return end_time    
       
    def start_time(self, end_time, days_backward):
        """ Generates the starting time for aggregation testing.
        Starting time means the earliest time (time_stamp) what tested
        PM data can has. Days backward is given by parameter
        days_backward and starting time is calculating from given
        end_time backward.
        Note that start_time is rounded to the nearest Monday 00:00:00 that
        is at the next to end_time - days_backward.   
        """        
        start_time = end_time - timedelta(days_backward)     
        hour_remainder = start_time.hour % 24
        start_time = start_time - timedelta(hours=hour_remainder)
      
        # let's next check what weekday is on question 
        week_day = start_time.weekday()

        # let's always start to calculate week aggregation from Monday forward 
        changed_days = 6 - (6 - week_day)

        # let's change date backward to previous Monday 
        start_time = start_time - timedelta(changed_days)
        minute_remainder = start_time.minute % 60
        second_remainder = start_time.second % 60
        microsecond_remainer = start_time.microsecond % 1000000    
        start_time = start_time - timedelta(minutes=minute_remainder)
        start_time = start_time - timedelta(seconds=second_remainder)
        start_time = start_time - timedelta(microseconds=microsecond_remainer)
        return start_time
    
    def increase_time(self, time, time_unit_raw):
        """ Increase the given time for e.g aggregation testing.
        Keyword has got three option for time increasing: WEEK, DAY and HOUR.
        Increased time is calculated from given time forward.   
        """            
        time_unit = time_unit_raw.upper()
        if time_unit == "HOUR":
            # set one hour period for raw data reading in DB
            time = time + timedelta(hours=1)
        elif time_unit == "DAY":
            time = time + timedelta(days=1)                 
        elif time_unit == "WEEK":
            time = time + timedelta(days=7)                    
        return time
    
    def fetch_aggregation_end_time(self, time_unit, time):
        """ Return the end time where to aggregations can be checked.
        End time depends on tested aggregation time target.   
        """
        if time_unit == "HOUR":
            # Move time one hour backward
            time = time - timedelta(hours=1)
        elif time_unit == "DAY":
            # Move time one day backward and furthermore back to the beginning of day 
            time = time - timedelta(hours=time.hour)                 
        elif time_unit == "WEEK":
            # Move time first one week backward and furthermore backward to previous
            # Monday from this and finally to the beginning of moved day            
            #time = time - timedelta(days=7)
            week_day = time.weekday()
            changed_days = 6 - (6 - week_day)
            time = time - timedelta(changed_days)
            time = time - timedelta(hours=time.hour)
        elif time_unit == "MONTH":
            # Move time first backward to the previous month and furthermore backward to the
            # beginning of moved (previous) month (meaning to the beginning of month's first day)            
            #time = time - timedelta(days=time.day+1)
            #time = time - timedelta(days=time.day-1)
            time = time - timedelta(days=time.day - 1)
            time = time - timedelta(hours=time.hour)
            
        # This is common part for all time target time handling     
        minute_remainder = time.minute % 60
        second_remainder = time.second % 60
        microsecond_remainer = time.microsecond % 1000000    
        time = time - timedelta(minutes=minute_remainder)
        time = time - timedelta(seconds=second_remainder)
        time = time - timedelta(microseconds=microsecond_remainer)
        return time
