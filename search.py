import json
import re
fp=open("./html/sources.txt","rt",encoding="utf-8")
data=json.load(fp)
def searchR(data):
    Flag=True
    while Flag:
        key =input("*"*80+"\n*"+"please input key word:".center(78)+"*\n"+"*"*80+"\n:")
        lis=[]
        count=0
        print("*"*80)
        print("*"+"SEARCH RESULT".center(78)+"*")
        print("*"*80)
        for item in data:
            res=re.match("[\S \s]*"+key+"[\s \S]*",item[0])
            if res:
                lis.append(item)
                count+=1
                print("*"+"%04d".center(10)%count+"*"+"  %-s"%item[0].strip() )
                print("*" * 80)
        print("*" + "total".center(10) + "*" + "%04d".center(67) % len(lis) + "*")
        print("*" * 80)
        while True:
            try:
                index = input("0-[%d]*输入索引查看链接 enter.重新搜索 q.退出：\n"%len(lis))
                if index == 'q' or index == 'Q':
                    Flag=False
                    break
                if index=='':
                    break
                index=abs(int(index)-1)
                print(lis[index][2])
            except:
                print("输入有误请重新输入::",end="")
                pass
    print("登出成功！！！！")
print("*"*80)
print("*"+"MOVIE SEARCH".center(78)+"*")
print("*"+"####".center(78)+"*")
print("*"+" CREATED BY MONKEY".center(78)+"*")
print("*"+" DATE 2021-7-31 ".center(78)+"*")
print("*"*80)
print("\n\n")
searchR(data)