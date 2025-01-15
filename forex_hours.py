from datetime import datetime, timedelta
import pytz
import time

# Forex market sessions, their time zones, and UTC hours
sessions = {
    "Sydney": {"timezone": "Australia/Sydney", "open": 20, "close": 5},   # 8:00 PM - 5:00 AM UTC, 2:30 AM - 11:30 AM UTC+630
    "Tokyo": {"timezone": "Asia/Tokyo", "open": 0, "close": 9},           # 12:00 AM - 9:00 PM UTC, 6:30 AM - 3:30 PM UTC+630
    "London": {"timezone": "Europe/London", "open": 8, "close": 17},      # 8:00 AM - 5:00 PM UTC, 2:30 PM - 11:30 PM UTC+630
    "New York": {"timezone": "America/New_York", "open": 13, "close": 22} # 1:00 PM - 10:00 PM UTC, 7:30 PM - 4:30 AM UTC+630
}

def get_trading_volume_status(current_utc_time):
    if 7 <= current_utc_time.hour < 19:
        return "High"
    elif (19 <= current_utc_time.hour < 21) or (1 <= current_utc_time.hour < 3):
        return "Medium"
    else:
        return "Low"

def display_forex_market_sessions():
    while True:
        local_timezone = datetime.now().astimezone().tzinfo
        current_local_time = datetime.now(local_timezone)
        current_local_time_str = current_local_time.strftime("%I:%M %p %Z")
        current_utc_time = datetime.now().astimezone(pytz.utc)
        trading_volume_status = get_trading_volume_status(current_utc_time)

        print("\nCurrent Local Time:", current_local_time_str)
        print("Current UTC Time:", current_utc_time.strftime("%I:%M:%S %p %Z"))
        print("Trading Volume Usually:", trading_volume_status)
        print("\nForex Market Session Hours:")

        active_sessions = []
        
        for session, info in sessions.items():
            market_timezone = pytz.timezone(info["timezone"])
            
            # Convert open and close times to the market's timezone
            open_hour = info["open"] if isinstance(info["open"], int) else int(info["open"])
            open_minute = 0
            close_hour = info['close'] if isinstance(info["close"], int) else int(info["close"])
            close_minute = 0

            if isinstance(info["open"], float):
                open_hour = int(info["open"])
                open_minute = int((info["open"] - open_hour) * 60)
            else:
                open_minute = 0
            
            if isinstance(info["close"], float):
                close_hour = int(info["close"])
                close_minute = int((info["close"] - close_hour) * 60)
            else:
                close_minute = 0
            open_time_utc = datetime.now().replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
            close_time_utc = datetime.now().replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)
            
            open_time_market = open_time_utc.replace(tzinfo=pytz.utc).astimezone(market_timezone)
            close_time_market = close_time_utc.replace(tzinfo=pytz.utc).astimezone(market_timezone)
            
            # Convert to local timezone
            open_time_local = open_time_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)
            close_time_local = close_time_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)
            
            # Adjust close time to the next day if it crosses midnight
            if info["close"] < info["open"]:
                close_time_market += timedelta(days=1)
                close_time_local += timedelta(days=1)
            
            # Display session hours in local and market time
            # print(f"{session} Session:")
            # print(f"  Market Time: {open_time_market.strftime('%I:%M %p %Z')} - {close_time_market.strftime('%I:%M %p %Z')}")
            # print(f"  Local Time:  {open_time_local.strftime('%I:%M %p %Z')} - {close_time_local.strftime('%I:%M %p %Z')}")

            # Check if the current local time is within the session hours
            if open_time_local <= current_local_time < close_time_local:
                current_market_time = datetime.now(market_timezone).strftime('%I:%M %p %Z')
                open_time_str = open_time_market.strftime('%I:%M %p %Z')
                close_time_str = close_time_market.strftime('%I:%M %p %Z')
                active_sessions.append((session, f"{current_market_time} [{open_time_str} - {close_time_str}]"))

        # Display active sessions with the actual current time in the city's local timezone
        if active_sessions:
            print("\nCurrently Active Session(s):")
            for session, market_time in active_sessions:
                print(f"  {session} - {market_time}")
        else:
            print("\nNo Forex market sessions are currently active.")

        time.sleep(1)
        print('\033c', end='')


display_forex_market_sessions()
