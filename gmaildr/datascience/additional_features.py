"""
We want to add the following features for analysis, clustering, classification, etc:

# Email Related Features

* Date and Time Related Features
    * Hour of Day as a float between 0 and 24
    * Time of Day Sine and Cosine
        * First convert the time to a float between 0 and 2 pi (including hour, minute, second)
        * Then calculate the sine and cosine of the time
    * Day of Week as an integer between 1 and 7
    * Day of Week Sine and Cosine
        * First convert the day of week to a float between 0 and 2 pi
        * Then calculate the sine and cosine of the day of week
    * Day of Year as an integer between 1 and 365 unless it is a leap year, then it is 366
    * Day of Year Sine and Cosine
        * First convert the day of year to a float between 0 and 2 pi (for leap year, 366 should be 2 pi)
        * Then calculate the sine and cosine of the day of year
    



"""
