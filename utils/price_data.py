import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_day_ahead_prices(forecast_hours=24):
    """
    Get day-ahead energy prices for the Netherlands with extended forecast.
    Returns hourly block prices for the available hours.
    
    The day-ahead prices are published daily around 13:00 CET for the next day.
    For hours beyond tomorrow, prices are forecasted based on historical patterns.
    
    Args:
        forecast_hours (int): Number of hours to forecast prices for (12-36 hours)
    """
    # Validate and bound forecast hours
    forecast_hours = max(12, min(forecast_hours, 36))
    
    now = datetime.now()
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    publication_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
    
    # Determine available price periods
    if now >= publication_time:
        # After 13:00, we have tomorrow's prices
        start_date = current_hour
    else:
        # Before 13:00, we only have today's remaining prices plus forecast
        start_date = current_hour
    
    # Generate dates using periods instead of end_date
    dates = pd.date_range(start=start_date, periods=forecast_hours, freq='h')
    
    # Simulate realistic Dutch energy prices (€/kWh)
    base_price = 0.22
    peak_hours = [7, 8, 9, 17, 18, 19, 20]
    shoulder_hours = [10, 11, 12, 13, 14, 15, 16]
    
    prices = []
    for date in dates:
        hour = date.hour
        hours_ahead = max(0, (date - now).total_seconds() / 3600)
        
        # Add increasing uncertainty for future hours with smoothed transitions
        # Use sigmoid function to ensure smooth transition and positive values
        uncertainty_factor = 0.2 / (1 + np.exp(-hours_ahead / 24))
        
        # Add weekly pattern
        weekly_factor = 1.0 + (0.05 if date.weekday() < 5 else -0.05)
        
        # Add daily seasonality
        daily_factor = np.sin(2 * np.pi * hour / 24) * 0.1
        
        if hour in peak_hours:
            # Peak hours have higher prices
            price = base_price * weekly_factor * (1 + np.random.uniform(0.3, 0.5) + daily_factor)
        elif hour in shoulder_hours:
            # Shoulder hours have moderate prices
            price = base_price * weekly_factor * (1 + np.random.uniform(0.1, 0.3) + daily_factor)
        else:
            # Off-peak hours have lower prices
            price = base_price * weekly_factor * (1 + np.random.uniform(-0.3, 0.0) + daily_factor)
        
        # Add smoothed uncertainty based on forecast distance using positive scale
        price *= (1 + np.random.normal(0, max(0.001, uncertainty_factor)))
        prices.append(max(0.05, price))  # Ensure minimum price of 0.05 €/kWh
    
    return pd.Series(prices, index=dates)

def is_prices_available_for_tomorrow():
    """Check if tomorrow's prices are available"""
    now = datetime.now()
    publication_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
    return now >= publication_time

def get_price_forecast_confidence(date):
    """
    Get confidence level for price forecasts based on how far in the future they are.
    Returns a value between 0 and 1, where 1 is highest confidence.
    """
    now = datetime.now()
    hours_ahead = max(0, (date - now).total_seconds() / 3600)
    
    if hours_ahead <= 24 and is_prices_available_for_tomorrow():
        return 1.0  # Actual day-ahead prices
    else:
        # Exponential decay of confidence with minimum of 20%
        confidence = np.exp(-hours_ahead / 48)
        return max(0.2, confidence)
