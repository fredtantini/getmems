import requests
import sys
import bs4 as bs

def getUserPageWithNumber(user, npage):
    r = requests.get("http://www.memrise.com/user/"+user+"/?page="+str(npage))
    return r

def getUserPage(user):
    r = requests.get("http://www.memrise.com/user/"+user)
    return r

def getNumberOfPage(user):
    r = getUserPage(user)
    soup = bs.BeautifulSoup(r.text, "lxml")
    n = soup.find('div', attrs={'class': 'pagination pagination-centered'})\
        .findAll('a')[-2].text
    return int(n)

def getMemsFromPage(request):
    mems_line = [line.strip() for line in request.text.split('\n') if line.strip().startswith('mems:')][0]
    true = True
    false = False
    null = []
    result = eval(mems_line[7:-1])
    if isinstance(result,dict):
        #only 1 mem -> 1 dict
        return (result,)
    #more mems -> tuple of dicts
    return result

def getInfoFromMem(memdict):
    d = {'lesson':memdict['pool']['id'], 'mem':memdict['text']}
    for c in memdict['pool']['columns']:
        if c in memdict['thing']['columns']:
            d.update({c:
                      (memdict['pool']['columns'][c]['label'],
                       memdict['thing']['columns'][c]['val'])})
    return d

def getDictFromAllMems(user):
    npage = getNumberOfPage(user)
    lesson_dict = {}
    print >>sys.stderr, "scanning"
    for p in range(npage):
        print >>sys.stderr, "page "+str(p+1)+ "/"+str(npage)
        page = getUserPageWithNumber(user, p)
        mems = getMemsFromPage(page)
        for m in mems:
            if 'pool' in m:
                id_lesson = getInfoFromMem(m)['lesson']
                lesson_list = lesson_dict.setdefault(id_lesson,[])
                lesson_list.append(getInfoFromMem(m))
    return lesson_dict


def printAllMems(user):
    lesson_dict = getDictFromAllMems(user)
    for lesson in lesson_dict:
        list_mems = lesson_dict[lesson]
        print "* "+str(lesson)
        for mem in list_mems:
            k = sorted(mem.keys())
            first, rest = k[0],k[1:]
            print "** "+mem[first][1]
            for r in rest:
                if r not in('lesson','mem'):
                    print "*** "+ str(mem[r][1])+" ("+ str(mem[r][1])+")"
            print "*** "+mem['mem']
                    
if __name__ == '__main__':
    if len(sys.argv)<2:
        print "getMems.py username"
    else:
        printAllMems(sys.argv[1])
