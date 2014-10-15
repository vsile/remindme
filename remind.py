#!/usr/bin/env python
# -*- coding: utf-8 -*-
# RemindMe v1.1 created by Dennis Smal' in 2014 godgrace@mail.ru

import commands
import string
import re
import sys

def get_args_cmd():
    args = string.join(sys.argv[1:],'\\ ') # получаем переменную из соседнего файла bash
    return args if args else "Через\ 15\ минут\ "

def main():
    filltext = get_args_cmd()
    loop = True
    while loop:
        op='zenity --entry --title="Напоминалка" --text="Введите напоминание" --entry-text=%s --width=400' % filltext
        get = commands.getstatusoutput(op)[1] # получаем текст
        text = get+' ' # добавляем в конец пробел, чтобы отрабатывать уведомления типа "напомнить мне через 10 минут". Если бы пробела не было, параметр clock был бы пуст. В параметре clock после слова "час" тоже стоит пробел, чтобы различать поиск "час" и "часов".
        find = re.findall('ерез [0-9]+|В [0-9:-]+|в [0-9:-]+|ерез час',text)
        day = re.findall('завтра|понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье',text)
        datex = re.findall('[0-9][0-9][.,-][0-9][0-9][.,-][0-9][0-9][0-9][0-9]|[0-9][.,-][0-9][0-9][.,-][0-9][0-9][0-9][0-9]',text) # ищем дату в формате 19.08.2014 или 19-08-2014 или 19,08,2014


        if get: # убеждаемся, заполнено ли поле ввода
            if find: # убеждаемся, указано ли время напоминания
                what = find[0].split()
                timex = what[1].replace('-',':').replace('час','1')
                day = re.findall('завтра|Завтра|в понедельник|понедельник|во вторник|вторник|в среду|среду|в четверг|четверг|в пятницу|пятницу|в субботу|субботу|в воскресенье|воскресенье',text)
                clock = re.findall('минуты |часа |дня |минуту |часов |день |минут |час |дней ',text)

                if len(timex) > 2: # заменяет выражения типа "в 10" на "в 10:00"
                    time = timex
                else:
                    time = timex+':00'	

                def replace_all(t, d): # общая функция для подмены переменных
                    for i, j in d.iteritems():
                        t = t.replace(i, j, 1)
                    return t

                if datex: # смотрим, есть ли указание на день недели
                    date = datex[0].replace('-','.').replace(',','.') # преобразуем дату в формат 19.08.2014
                    whatdate = date
                    delwhatdate = datex[0]+' '
                else:
                    whatdate = ''
                    delwhatdate = ''

                if day: # смотрим, есть ли указание на конкретную дату
                    ind = {'завтра':'tomorrow', 'Завтра':'tomorrow', 'понедельник':'mon', 'вторник':'tue', 'среду':'wed', 'четверг':'thu', 'пятницу':'fri', 'субботу':'sat', 'воскресенье':'sun', 'в понедельник':'mon', 'во вторник':'tue', 'в среду':'wed', 'в четверг':'thu', 'в пятницу':'fri', 'в субботу':'sat', 'в воскресенье':'sun'}
                    when = replace_all(day[0], ind)
                    delday = day[0]+' '
                else:
                    when = ''
                    delday = ''


                if clock: # смотрим, есть ли указание на часы, минуты, дни
                    clockbank = {'минут ':'min', 'час ':'hour', 'дней ':'days', 'минуту ':'min', 'часа ':'hours', 'дня ':'days', 'минуты ':'min', 'часов ':'hours', 'день ':'days'}
                    how = replace_all(clock[0], clockbank)
                    delclock = clock[0]

                else:
                    how = ''
                    delclock = ''

                reps = {'ерез':'at now + %s %s' % (timex,how),'В':'at %s %s %s' % (time,when,whatdate),'в':'at %s %s %s' % (time,when,whatdate)}
                wors = {'Через %s %s' % (what[1],delclock):'','через %s %s' % (what[1],delclock):'','В %s ' % what[1]:'','в %s ' % what[1]:'', '%s' % delday:'', 'Через час':'', 'через час':'', '%s' % delwhatdate:'',} # какие слова мы будем удалять
                x = replace_all(what[0], reps) # это время, на которое запланировано появление напоминания
                out = replace_all(text, wors) # это текст напоминания
                com = commands.getstatusoutput('echo DISPLAY=:0 ~/remindme/task %s | %s' % (out,x))
                #для отладки, чтобы долго не ждать
                #com = commands.getstatusoutput('echo DISPLAY=:0 ~/remindme/task %s | at now + 0 min' % out) 
                loop = False

            else:
                error = commands.getstatusoutput('zenity --warning --text="Попробуйте ещё раз.."')
        else:
            loop = False

if __name__ == "__main__":
    main()
