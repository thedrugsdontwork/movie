import threading

import requests
from threading import Thread
from threading import RLock
from bs4 import BeautifulSoup
from lxml import  etree
import warnings
import time
import os
warnings.filterwarnings('ignore')
class dytt:
    def __init__(self):
        self.headers={'Host': 'www.ygdy8.net', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
        self.baseUrl=["https://www.ygdy8.net/html/gndy/dyzz/","https://www.ygdy8.net/html/gndy/china/","https://www.ygdy8.net/html/gndy/oumei/"]
        self.urlEnd=["list_23_%d.html","list_4_%d.html","list_7_%d.html"]
        self.total=[235,137,261]
        self.max=sum(self.total)
        self.pmax=0
        self.dmax=0
        self.count=0
        self.dcount=0
        self.pcount=0
        self.linkcount=0
        self.base="https://www.ygdy8.net/"
        self.path=["./html/mainpage/","./html/china/","./html/oumei/"]
        self.lock=RLock()
        self.encoding=['gb18030','gb2312','utf-1']
        self.errLis=[]
        self.links=[]
    def dispatch(self):
        tlis = []
        for j in range(3):
            border = self.total[j] // 8
            for i in range(0, 3, 1):
                tlis.append(Thread(target=self.getMainPage, args=(border * i, border * (i + 1),self.baseUrl[j],self.urlEnd[j],self.path[j])))
                tlis[-1].start()
            else:
                tlis.append(Thread(target=dytt1.getMainPage, args=(border * (i + 1), self.total[j],self.baseUrl[j],self.urlEnd[j],self.path[j])))
                tlis[-1].start()
        for i in tlis:
            i.join()

    def downloadMain(self,paths=None,lis=None):#ads path
        data=[]
        if paths:
            for path in paths:
                with open(path,"rt",encoding="utf-8") as fp:
                    temp=fp.read().split("\n")
                    data.extend([tuple(i[1:-1].split(",")) for i in temp])
        elif lis:
            data=lis
        self.dmax=len(data)
        tlis=[]
        border=self.dmax//9
        for i in range(8):
            tlis.append(Thread(target=self.downloadDetailPage,args=(data[i*border:(i+1)*border],"./html/detailpage/")))
            tlis[-1].start()
        else:
            tlis.append(
                Thread(target=self.downloadDetailPage, args=(data[(i + 1) * border:], "./html/detailpage/")))
            tlis[-1].start()
        for i in tlis:
            i.join()

    def parseMain(self):
        filepaths=[]
        tlis=[]
        fp=open("./html/links.txt","wt",encoding="utf-8")
        for path in self.path:
            filepaths.extend([path+i for i in os.listdir(path)])
        border=len(filepaths)//9
        self.pmax=len(filepaths)
        for i in range(8):
            tlis.append(Thread(target=self.parseMainPage,args=(filepaths[i*border:(i+1)*border],fp)))
            tlis[-1].start()
        else:
            tlis.append(Thread(target=self.parseMainPage, args=(filepaths[(i+1)* border:],fp)))
            tlis[-1].start()
        for i in tlis:
            i.join()
        fp.close()

    def downloadDetailPage(self,datas,path):
        title = lambda x: x[(lambda x: x.index("《") if "《" in x else 0)(x):(lambda x: x.index("》") if "》" in x else len(x))(
            x) + 1]
        for data in datas:
            res = requests.get(data[0], verify=False, headers=self.headers)
            with open(path+title(data[1]).replace("/","|")+".html","wt",encoding="utf-8") as fp:
                fp.write(res.content.decode("gb18030","ignore"))
                self.lock.acquire()
                self.dcount+=1
                self.lock.release()
                print("\r下载进度：[%d/%d]"%(self.dmax,self.dcount),end="")
    def getMainPage(self ,border,end,baseUrl,urlEnd,path):
        for i in range(border,end,1):
            res=requests.get(baseUrl+urlEnd%(i+1),verify=False,headers=self.headers)
            fp=open(path+urlEnd%(i+1),"wt",encoding="utf-8")
            for en in self.encoding:
                try:
                    fp.write(res.content.decode(en,'ignore'))
                    break
                except:
                    pass
            fp.close()
            time.sleep(0.2)
            self.lock.acquire()
            self.count+=1
            self.lock.release()

            print("\r[%d/%d] thread=9"%(self.max,self.count),end="")

    def getJddy(self):
        url=["https://www.ygdy8.net/html/gndy/jddy/20160320/50510.html","https://www.ygdy8.net/html/gndy/jddy/20160320/50510_2.html"]
        for i in url:
            res=requests.get(i,verify=False,headers=self.headers)
            fp = open("./html/jddy/"+i[-10:], "wt", encoding="utf-8")
            for en in self.encoding:
                try:
                    fp.write(res.content.decode(en, 'ignore'))
                    break
                except:
                    pass
            fp.close()
        print("get complete!")
    def parseMainPage(self,filepaths,Fp):#abs path list
        for filepath in filepaths:
            with open(filepath,"rb") as fp:
                bsobj=BeautifulSoup(fp.read().decode("utf-8","ignore"),'lxml')
                try:
                    res=bsobj.find('div',attrs={'class':'co_content8'}).find_all('a',attrs={'class':'ulink'})
                    for item in res:
                        href=item.get('href')
                        if href[-10:]=="index.html":
                            continue
                        self.lock.acquire()
                        self.linkcount += 1
                        s="(%s%s,%s)\n"%(self.base,href,item.get_text())
                        Fp.writelines(s)
                        self.lock.release()
                    self.pcount+=1
                    print("\r  [%d/%d] links:[%d]" % (  self.pmax, self.pcount, self.linkcount),
                          end="")
                except Exception as e:
                    self.errLis.append((filepath,e.args))

    def parseJddy(self,path):
        filenames=os.listdir(path)
        Fp=open("./html/jddylinks.txt","wt",encoding="utf-8")
        if ".DS_Store" in filenames:
            del filenames[filenames.index(".DS_Store")]
        for filename in filenames:
            with open(path+filename,"rb") as fp:
                bsobj=BeautifulSoup(fp.read().decode("gb18030",'ignore'))
                res=bsobj.find(attrs={'class':'co_content8'}).find_all('p')
                for item in res:
                    a=item.find("a")
                    if a is None:
                        continue
                    href=a.get('href')
                    a.decompose()
                    text=item.get_text()
                    if not text:
                        text=href[-10:]
                    s="(%s,%s)\n"%(href,text)
                    Fp.writelines(s)
        Fp.close()
        print("解析完成")


    def Log(self):
        print("\nerr count:[%d]"%len(self.errLis))
        print(self.errLis)


    def patch(self,paths):
        data = []
        for path in paths:
            with open(path, "rt", encoding="utf-8") as fp:
                temp = fp.read().split("\n")
                data.extend([tuple(i[1:-1].split(",")) for i in temp])

        title = lambda x: x[(lambda x: x.index("《") if "《" in x else 0)(x):(lambda x: x.index("》") if "》" in x else len(x))(x) + 1]
        lis = os.listdir("./html/detailpage/")
        download = []
        for i in data:
            try:
                item=title(i[1]).replace("/","|")+".html"
                if item not in lis:
                    download.append(i)
            except Exception as e:
                print(e.args)
        return download
    def parseLinks(self,paths):
        length=len(paths)
        count=0
        for path in paths:
            with open(path,"rt",encoding="utf-8") as fp:
                data=None
                html=fp.read()
                bsobj=BeautifulSoup(html,"lxml")
                try:
                    title=bsobj.find(attrs={"class":"title_all"}).get_text()
                    item=bsobj.find('div',attrs={'id':'Zoom'}).find('a')
                except:
                    title=path[:-5]
                if item is not None:
                    href=item.get('href')
                else:
                    continue
                if href is None:
                    pass
                else:
                    if href[0:3]=="ftp":
                        data=(title,"ftp",href)
                    elif href[0:6]=="magnet":
                        data = (title, "magnet", href)
                if data !=None:
                    self.lock.acquire()
                    self.links.append(data)
                    self.lock.release()
                count += 1
                print("\r%s parseing [%d/%d]"%(threading.current_thread().name,length,count),end="")

    def dispatchParse(self):
        paths = ["./html/detailpage/" + i for i in os.listdir('./html/detailpage/')]
        border=len(paths)//9
        tlis=[]
        for i in range(8):
            tlis.append(Thread(target=self.parseLinks,args=(paths[border*i:border*(i+1)],)))
            tlis[-1].start()
        else:
            tlis.append(Thread(target=self.parseLinks, args=(paths[border * (i + 1):],)))
            tlis[-1].start()
        for i in tlis:
            i.join()
        import json
        fp=open("./html/sources.txt","wt",encoding="utf-8")
        fp.write(json.dumps(self.links))
        fp.close()
        print("解析完成")



dytt1=dytt()
# dytt1.dispatch()
# dytt1.getJddy()
# dytt1.parseMain()
#dytt1.parseJddy("./html/jddy/")
# data=dytt1.patch(["./html/links.txt","./html/jddylinks.txt"])
# dytt1.downloadMain(lis=data)
dytt1.dispatchParse()
dytt1.Log()
print("抓取完成！")