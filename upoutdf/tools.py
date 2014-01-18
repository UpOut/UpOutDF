# coding: utf-8

from datetime import date

def yearrange(year):
    days_in = date(year,1,1)
    end = date(year+1,1,1)
    delta = end - days_in
    return (1,delta.days)