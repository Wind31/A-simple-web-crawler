#-*-coding:utf-8-*- 
from __future__ import unicode_literals
import urllib2
import gzip
import zlib
import StringIO
import re
import sys  
import os
reload(sys)  
sys.setdefaultencoding('utf8') 

def download(url,user_agent='wswp',try_num=2):
    headers={'User-agent':user_agent,'Accept-encoding':'gzip'}
    requeset=urllib2.Request(url,headers=headers)
    try:
        opener = urllib2.build_opener()
        response = opener.open(requeset)
        html = response.read()
        gzipped = response.headers.get('Content-Encoding')
        if gzipped:
            html = zlib.decompress(html, 16+zlib.MAX_WBITS)
    except urllib2.URLError as e:
        print 'Error:',e.reason
        html=None
        if(try_num>0):
            if hasattr(e,'code') and 500<=e.code<600:
                return download(url,try_num-1)
    return html

def getLinks(url):
    links=[]
    html=download(url)
    if not html:
        try:
            sys.exit(0)
        except:
            print 'Fail to get links'
    r=re.compile(r'<ul>(.*?)</ul>',re.DOTALL)
    ul=r.findall(html)
    r=re.compile(r'href=\"(.*?)\"',re.DOTALL)
    for i in ul:
        li=r.findall(i)
        for j in li:
            link=str(url)+str(j)
            links.append(link)
    print 'get '+str(len(links))+' links totally'
    return links

def getChapters(links):
    count = 0
    filenames=[]
    for url in links:
        count=count+1
        filename=str(count)+'.txt'
        html=download(url)
        if not html:
            print 'fail to download chapter'+str(count)
            continue
        with open(filename,'w') as f:
            try:
                f.write(html.decode('gbk').encode('utf-8'))
            except:
                f.seek(0, os.SEEK_SET)
                try:
                    f.write(html.decode('gb18030').encode('utf-8'))
                except:
                    f.seek(0, os.SEEK_SET)
                    f.write(html)
            finally:
                print 'success to download chapter'+str(count)
                filenames.append(filename)
    return filenames


def getText(filenames):
    for i in filenames:
        with open(i,'r') as f:
            try:
                html=f.read().decode('utf-8').encode('utf-8')
            except:
                f.seek(0, os.SEEK_SET)
                try:
                    html=f.read().decode('gbk').encode('utf-8')
                except:
                    f.seek(0, os.SEEK_SET)
                    html=f.read().decode('gb18030').encode('utf-8')
        if not html:
            try:
                sys.exit(0)
            except:
                print 'Fail to read '+i
        r=re.compile(r'<H1>.*</a>(.*?)</H1>',re.DOTALL)
        title=r.findall(html)[0]
        r=re.compile(r'</table>.{0,2}<br>(.*?)</div>',re.DOTALL)
        text=r.findall(html)[0]
        text=text.replace('&nbsp;',' ')
        text=text.replace('<br />','\n')
        with open(i,'w') as f:
            f.write(title)
            f.write('\n')
            f.write(text)
    return filenames


def getResult(filenames):
    with open('result.txt','w') as f:
        for i in filenames:
            with open(i,'r') as f1:
                t=f1.read()
                f.write(t)
                f.write('\n\n')
            os.remove(i)

if __name__=='__main__':
    url=raw_input('Please input the index url:')
    links=getLinks(url)
    filenames=getChapters(links)
    getText(filenames)
    getResult(filenames)



