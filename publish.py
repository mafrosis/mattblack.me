#! /usr/bin/env python

import sys
from argparse import ArgumentParser
import dokuwikixmlrpc

# global content and position index vars
wiki = ""
index = 20

def process_title(ht):
    global wiki, index
    marker = ''
    for i in range(0, 7-ht):
        marker += '='
    pos = wiki.find(marker+" ", index)
    pos2 = wiki.find(" "+marker, pos)
    title = wiki[pos+len(marker)+1:pos2].replace(' ', '&nbsp;')
    index = pos2+len(marker)
    return '<h'+str(ht)+'>'+title+'</h'+str(ht)+'>\n'

def process_bullets(content):
    html = ''
    lines = content.split('\n')
    for line in lines:
        item = line[4:].strip()
        if(len(item) > 0):
            if(item.startswith('[[')):
                html += '<li><a href="'+item[2:-2]+'" target="_blank">'+item[2:-2]+'</a></li>'
            else:
                html += '<li>'+item+'</li>'
    return '<ul class="bullets">'+html+'</ul>\n'

def process_skillz():
    global wiki, index
    title = process_title(2)
    end = wiki.find("===== ", index)    # find end of this section
    skillz = ''
    while(index <= end):
        skillz += process_single_skill()
    index = end
    return title+skillz

def process_single_skill():
    global wiki, index
    title = process_title(3)
    
    # get experience
    pos = wiki.find("//", index)
    pos2 = wiki.find("//", pos+2)
    exp = '<p class="alignright">'+wiki[pos+2:pos2]+'</p>\n'
    
    # get list of skills
    pos = wiki.find("==== ", pos2)
    skillzlist = wiki[pos2+2:pos]
    skillz = process_bullets(skillzlist)
    
    index = pos
    return title+exp+skillz

def process_edu():
    global wiki, index
    title = process_title(2)

    edu = '<table>'
    pos = wiki.find("===== ", index)
    edulist = wiki[index:pos]
    lines = edulist.split('\n')
    for line in lines:
        item = line[4:].strip()
        if(len(item) > 0):
            chunks = item.split('/')
            if(chunks[0][0:2] == "**"):
                edu += '<tr><td class="strong">'+chunks[0][2:].strip()+'</td><td class="strong">'+chunks[1][0:-2].strip()+'</td></tr>'
            else:
                edu += '<tr><td>'+chunks[0].strip()+'</td><td>'+chunks[1].strip()+'</td></tr>'
    edu += '</table>'

    index = pos
    return title+edu

def process_exp():
    global wiki, index
    title = process_title(2)
    end = wiki.find("===== ", index)    # find end of this section
    exp = ''
    while(index <= end):
        exp += process_single_exp()
    index = end
    return title+exp

def process_single_exp():
    global wiki, index
    title = process_title(3)

    # title, type & speil
    pos = wiki.find("//", index)
    pos2 = wiki.find("//", pos+2)
    jtitle = '<p class="alignright">'+wiki[pos+2:pos2]+'</p>\n'
    pos = wiki.find("//", pos2+2)
    pos2 = wiki.find("//", pos+2)
    jtype = '<p class="strong clear">'+wiki[pos+2:pos2]+'</p>\n'
    pos = wiki.find("===", pos2+2)
    spiel = '<p class="spiel">'+wiki[pos2+2:pos].strip()+'</p>\n'
    index = pos

    # acheivements
    ach = process_title(4)
    pos = wiki.find("==== ", index)
    achlist = wiki[index+3:pos]
    ach += process_bullets(achlist)
    
    index = pos
    return title+jtitle+jtype+spiel+ach

def process_refs():
    global wiki, index
    title = process_title(2)
    
    reflist = wiki[index+3:]
    ref = process_bullets(reflist)
    return title+ref


def process_cv(username, password):
    global wiki

    # load raw wiki content
    dwc = dokuwikixmlrpc.DokuWikiClient("https://wiki.mafro.co.uk", username, password)
    wiki = dwc.page("cv")

    # process wiki into HTML
    dev = process_skillz()
    edu = process_edu()
    exp = process_exp()
    refs = process_refs()

    # replace placeholders in CV template and publish
    f = open("files/cv.tmpl", "r")
    data = f.read()
    f.close()
    output = data.format(dev=dev, edu=edu, exp=exp, refs=refs)
    f = open("files/cv.htm", "w")
    f.write(output)
    f.close()


def process_command_line(argv):
    parser = ArgumentParser()
    parser.add_argument("username", action="store", help="Username for dokuwiki")
    parser.add_argument("password", action="store", help="Password for dokuwiki")
    return parser.parse_args(argv)


def main(argv=None):
    """
    Application entry and exit point
    """
    args = process_command_line(sys.argv[1:])
    process_cv(args.username, args.password)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
