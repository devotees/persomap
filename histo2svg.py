#!/usr/bin/env python3

import sys
import svgwrite
import datetime
import dateutil.parser


# Timeline Grid Dimensions
left_grid = 50
weekday_right_grid = 500
weekend_left_grid = 600
right_grid = 950
top_grid = 100    # Today's date
bottom_grid = 900 # Date of birth
top_label_y = 75
event_line_x = right_grid+20

sqpx_per_hour = .001 # Amount of square pixels which represent a unit of time

# Time Range
top_date = None # Today's date
bottom_date = None # Date of birth
weekday_start_hour=8
weekday_end_hour=24

def weekday_hour(hr):
    '''
    Returns the x-axis coordinate for a weekday time.
    Args:
        hr (int): Represents the time in 24h notation (E.g. 9 --> '9h00').
    Returns:
        int: An x-axis coordinate.
    '''
    x_scale = (weekday_right_grid - left_grid)/(weekday_end_hour-weekday_start_hour)
    return left_grid + (hr-weekday_start_hour)*x_scale

def weekday(start_datestr, end_datestr, start_hour, end_hour, event_label, **kwargs):
    '''
    Draws a weekday event.
    Args:
        start_datestr(string): The event starting date in ISO format (YYYY-MM-DD).
        end_datestr(string): The event ending date in ISO format (YYYY-MM-DD).
        start_hour(int): The event starting time in 24h notation (E.g. 9 --> '9h00').
        end_hour (int): The event ending time in 24h notation (E.g. 21 --> '21h00').
        event_label (string): The name of the event.
        **kwargs: css styling
    '''
    # Coordinates
    y1 = parse_date(start_datestr)
    y2 = parse_date(end_datestr)
    x1 = weekday_hour(start_hour)
    x2 = weekday_hour(end_hour)
    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
    # Drawing
    dwg.add(dwg.polygon(points, **kwargs))
    text(x1, y1, event_label)

def weekend(start_datestr, end_datestr, num_hours, event_label, **kwargs):
    '''
    Draws a weekend event.
    Args:
        start_datestr(string): The event starting date in ISO format (YYYY-MM-DD).
        end_datestr(string): The event ending date in ISO format (YYYY-MM-DD).
        num_hours (int): The time invested in the event.
        event_label (string): The name of the event.
        **kwargs: css styling of main rectangle
    '''
    # Coordinates
    y1 = parse_date(start_datestr)
    y2 = parse_date(end_datestr)
    x1 = weekend_left_grid
    x2 = (y1-y2)/(num_hours*sqpx_per_hour) + x1
    assert x2 > weekday_right_grid, (x1, x2, weekday_right_grid)

    points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
    # Drawing
    dwg.add(dwg.polygon(points, **kwargs))
    text(x1, y1, event_label)

def event(start_datestr, end_datestr, event_label):
    #dwg.add(dwg.line((right_grid+20, top_grid), (right_grid+20, bottom_grid), stroke='grey'))
    #text(right_grid, top_label_y, 'Events')
    start_y = parse_date(start_datestr)
    end_y = parse_date(end_datestr)
    event_midpoint = (start_y+end_y)/2
    event_radius = start_y-end_y+5
    dwg.add(dwg.circle((event_line_x, event_midpoint), (end_y-start_y+5), fill='white', stroke='grey'))
    dwg.add(dwg.line((event_line_x+event_radius, event_midpoint), (event_line_x+event_radius+20, event_midpoint), stroke='grey'))
    text(event_line_x+event_radius+20, event_midpoint+8, event_label)

def text(x, y, label):
    dwg.add(dwg.text(str(label), x=[x+3], y=[y-5], style='color:black'))

def parse_date(datestr):
    '''
    Returns the y-axis coordinate for a date.
    Args:
        datestr (string): A date in ISO format (YYYY-MM-DD).
    Returns:
        int: y-axis coordinate.
    '''
    parsed_date = dateutil.parser.parse(datestr)
    days_alive = (top_date - bottom_date).days # Total days alive
    day_count = (top_date - parsed_date).days # Number of days into life at which event occurred
    scale = (bottom_grid - top_grid) / days_alive
    return bottom_grid - scale * (days_alive - day_count)

def residence(start_datestr, end_datestr, address, **kwargs):
    '''
    Draws a box of y-axis length = duration of stay at a residence.
    Args:
        start_datestr(string): The event starting date in ISO format (YYYY-MM-DD).
        end_datestr(string): The ending date of the timeline in ISO format (YYYY-MM-DD).
        address (string): Address of residence.
        **kwargs: css styling
    '''
    start_y = parse_date(start_datestr)
    end_y = parse_date(end_datestr)
    points = [(left_grid,start_y), (right_grid,start_y), (right_grid,end_y), (left_grid,end_y)]
    dwg.add(dwg.polygon(points, **kwargs))
    if address:
        text(weekday_right_grid, start_y, address)

def timespan(start_datestr, end_datestr):
    '''
    Draws the histomap grid.
    Args:
        start_datestr(string): The starting date of the timeline in ISO format (YYYY-MM-DD).
        end_datestr(string): The ending date of the timeline in ISO format (YYYY-MM-DD).
    '''
    # Set y-axis boundaries of grid
    global bottom_date, top_date
    top_date = dateutil.parser.parse(end_datestr)
    bottom_date = dateutil.parser.parse(start_datestr)

    # Set year ticks on y-axis
    for y in range(bottom_date.year, top_date.year+1):
        dt = parse_date('%s-01-01' % y)
        dwg.add(dwg.line((0, dt), (left_grid, dt), stroke='grey'))
        text(0,dt, y)

    # Set hour ticks on x-axis
    for h in range(weekday_start_hour, weekday_end_hour+1):
        x = weekday_hour(h)
        dwg.add(dwg.line((x, top_label_y), (x, top_grid), stroke='grey'))
        text(x,top_grid, h)
    text(left_grid,top_grid-45, 'Mon-Fri')
    text(weekend_left_grid,top_grid, 'Weekend')

   # Draw the event line
    dwg.add(dwg.line((event_line_x, top_grid), (event_line_x, bottom_grid), stroke='grey'))
    text(right_grid, top_label_y, 'Events')

def main(func, fnout):
    global dwg
    dwg = svgwrite.Drawing(fnout, preserveAspectRatio='xMidYMid meet')
    dwg.add_stylesheet('timeline.css', title='some title')
    func()
    dwg.save()
