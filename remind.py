#!/usr/bin/env python
# -*- coding: utf-8 -*-
# RemindMe v1.2 created by Dennis Smal' in 2014 godgrace@mail.ru

from __future__ import print_function

import subprocess
import re
import sys

def replace_all(t, d):
    """Общая функция для подмены переменных"""
    for i, j in d.iteritems():
        t = t.replace(i, j, 1)
    return t

def get_datex(text):
    """Извлекает из текста дату и подстроку с датой, которую нужно удалить"""
    whatdate = ''
    delwhatdate = ''
    datex = re.findall(r'\d{2}[.,-]\d{2}[.,-]\d{4}|\d{1}[.,-]\d{2}[.,-]\d{4}',text) # ищем дату в формате 19.08.2014 или 19-08-2014 или 19,08,2014
    if datex:
        date = datex[0].replace('-','.').replace(',','.') # преобразуем дату в формат 19.08.2014
        whatdate = date
        delwhatdate = datex[0]+' '
    return whatdate, delwhatdate

def get_day(text):
    """Извлекает из текста день недели и подстроку, которую нужно удалить"""
    when = ''
    delday = ''

    day = re.findall('завтра|Завтра|в понедельник|понедельник|во вторник|вторник|в среду|среду|в четверг|четверг|в пятницу|пятницу|в субботу|субботу|в воскресенье|воскресенье',text)
    if day:
        ind = {'завтра':'tomorrow', 'Завтра':'tomorrow', 'понедельник':'mon', 'вторник':'tue', 'среду':'wed', 'четверг':'thu', 'пятницу':'fri', 'субботу':'sat', 'воскресенье':'sun', 'в понедельник':'mon', 'во вторник':'tue', 'в среду':'wed', 'в четверг':'thu', 'в пятницу':'fri', 'в субботу':'sat', 'в воскресенье':'sun'}
        when = replace_all(day[0], ind)
        delday = day[0]+' '
    return (when, delday)

def get_clock(text):
    """Извлекает из текста время и подстроку, которую нужно удалить"""
    how = ''
    delclock = ''
    clock = re.findall('минуты |часа |дня |минуту |часов |день |минут |час |дней ',text)
    if clock: # смотрим, есть ли указание на часы, минуты, дни
        clockbank = {'минут ':'min', 'час ':'hour', 'дней ':'days', 'минуту ':'min', 'часа ':'hours', 'дня ':'days', 'минуты ':'min', 'часов ':'hours', 'день ':'days'}
        how = replace_all(clock[0], clockbank)
        delclock = clock[0]
    return (how, delclock)

def add_task(out, x):
    """Добавляет напоминание в очередь at"""
    #для отладки, чтобы долго не ждать
    #x = 'at now'
    cmd = 'echo "DISPLAY=:0 ~/remindme/task %s" | %s' % (out, x)
    subprocess.Popen(cmd, shell=True)

def main(reminder="Через 15 минут "):
    warn_cmd = [
            'zenity',
            '--warning',
            '--text="Попробуйте ещё раз.."'
            ]
    cmd = [
            'zenity',
            '--entry',
            '--title=Напоминалка',
            '--text=Введите напоминание',
            '--entry-text={}'.format(reminder),
            '--width=400'
            ]

    loop = True
    while loop:
        get = subprocess.check_output(cmd) # получаем текст
        text = get+' ' # добавляем в конец пробел, чтобы отрабатывать уведомления типа "напомнить мне через 10 минут". Если бы пробела не было, параметр clock был бы пуст. В параметре clock после слова "час" тоже стоит пробел, чтобы различать поиск "час" и "часов".
        find = re.findall('ерез [0-9]+|В [0-9:-]+|в [0-9:-]+|ерез час',text)

        if get: # убеждаемся, заполнено ли поле ввода
            if find: # убеждаемся, указано ли время напоминания
                what = find[0].split()
                timex = what[1].replace('-',':').replace('час','1')

                if len(timex) > 2: # заменяет выражения типа "в 10" на "в 10:00"
                    time = timex
                else:
                    time = timex+':00'	
                
                whatdate, delwhatdate = get_datex(text)
                when, delday = get_day(text)
                how, delclock = get_clock(text)

                reps = {'ерез':'at now + %s %s' % (timex,how),'В':'at %s %s %s' % (time,when,whatdate),'в':'at %s %s %s' % (time,when,whatdate)}
                wors = {'Через %s %s' % (what[1],delclock):'','через %s %s' % (what[1],delclock):'','В %s ' % what[1]:'','в %s ' % what[1]:'', '%s' % delday:'', 'Через час':'', 'через час':'', '%s' % delwhatdate:'',} # какие слова мы будем удалять
                x = replace_all(what[0], reps) # это время, на которое запланировано появление напоминания
                out = replace_all(text, wors) # это текст напоминания

                add_task(out, x)
                loop = False

            else:
                error = subprocess.check_output(warn_cmd)
        else:
            loop = False

def usage():
    s = "Использование: {} [Время напоминания]".format(__file__)
    print(s)

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        main(*sys.argv[1:])
    else:
        usage()
