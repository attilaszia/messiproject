import _mysql
import re
import urllib2

db = _mysql.connect("localhost","root","messi","messi")

def list_entries():
    db.query("""SELECT * from matches""")
    r = db.store_result()
    print r.fetch_row()

def populate_from_url(url):
    response = urllib2.urlopen(url)
    html = response.read()
    found = re.findall("[A-Za-z() ]+ - [A-Za-z() ]+.+[0-9]{1,2}\.[0-9]{2}.+",html)
    for m in found:
        #print "----"
        #print m
        teams = re.search("([A-Za-z() ]+) - ([A-Za-z() ]+)", m)
        team_a = teams.group(1)
        team_b =  teams.group(2)
        odds = re.findall("([0-9]{1,2}\.[0-9]{2})", m)
        odds_list = odds[:3]
        odds_list.sort()
        winnerodd = re.search("best-betrate\" data-odd=\"([0-9]{1,2}\.[0-9]{2})", m)
        if winnerodd:
            win_odd = winnerodd.group(1)
            #print win_odd
            #print team_a
            #print team_b
            #print odds_list
            win_index = odds_list.index(win_odd)
            #print win_index
            league = re.findall("/([a-z0-9A-Z-]+)/results",url)
            #print league
            query = "INSERT INTO matches (league, leastodd, middleodd, biggestodd, teama, teamb, win_index)\
                                  VALUES (\"%s\", %s, %s, %s, \"%s\", \"%s\", %d )\
                                   " % (league[0], odds_list[0], odds_list[1], odds_list[2], team_a, team_b, win_index)
            #print query
            db.query(query)

def dispatch_stages(url):
    response = urllib2.urlopen(url)
    html = response.read()
    stages = re.findall("\?stage=[a-zA-Z0-9]+",html)
    if len(stages) > 0:
        for stage in stages:
            full_url = url+stage
            print full_url
            populate_from_url(url)
    else:
        populate_from_url(url)

def dispatch_urls(url_and_league):
    datalist = url_and_league.split(";")
    url = datalist[0]
    league = datalist[1]
    print url
    print league
    response = urllib2.urlopen(url)
    html = response.read()
    found = re.findall("href=\"(.+)\">%s</a>" % league,html)
    for stuff in found:
        url_to_fetch = "http://www.betexplorer.com%sresults/" % stuff
        print url_to_fetch
        dispatch_stages(url_to_fetch)

f = open("./urls.txt","r")
data = f.readlines()
for line in data:
    url_and_league = line[:-1]
    dispatch_urls(url_and_league)
