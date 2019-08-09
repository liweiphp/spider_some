#coding:utf-8

import os
import requests
from PIL import Image
import math
import json
import base64
import time

def imagesget():
    if not os.path.exists('images'):
        os.mkdir('images')
    count=0
    while True:
        img=requests.get('https://qypassport.xin.com/Account/GenerateVerificationCode?time=0.880897894436119').content
        with open('images/%s.jpeg'%count,'wb') as imgfile:
            imgfile.write(img)
        count+=1
        if(count==100):
            break

def convert_image(image):
    image=image.convert('L')
    image2=Image.new('L',image.size,255)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pix=image.getpixel((x,y))
            if pix<120:
                image2.putpixel((x,y),0)
    return image2

#裁切验证码
def cut_image(image,isLimit=False):
    inletter=False
    foundletter=False
    letters=[]
    start=0
    end=0
    if isLimit:
        minLen = image.size[0]/6
        maxLen = image.size[0]/3
    for x in range(image.size[0]):#遍历x轴
        for y in range(image.size[1]):#遍历y轴
            pix=image.getpixel((x,y))
            if(pix==0):
                inletter=True
        if foundletter==False and inletter ==True:
            foundletter=True
            start=x
        if foundletter==True and inletter==False:
            if isLimit:
                if x-start<=minLen or x-start>=maxLen:
                    continue
            end=x
            letters.append((start,end))
            foundletter=False
        inletter=False
    images=[]

    for letter in letters:
        img=image.crop((letter[0],0,letter[1],image.size[1]))#左上右下
        images.append(img)
    return images


def saveImg():
    count = 0
    if not os.path.exists('items'):
        os.mkdir('items')
    for img in os.listdir('./images'):
        image=Image.open('./images/%s' % img)
        image = convert_image(image)
        images = cut_image(image,True)
        for i in images:
            i.save('./items/%s.jpeg' % count)
            count = count+1


def buildvector(image):
    result={}
    count=0
    for i in image.getdata():
        result[count]=i
        count+=1
    return result

def base64Img(path):
    with open(path,"rb") as f:#转为二进制格式
        base64_data = base64.b64encode(f.read())#使用base64进行加密
        f.close()
    return base64_data

def getCapcha(session):
    session.get('https://qypassport.xin.com/?returnUrl=http%3a%2f%2fqy.xin.com%2f').text
    img=session.get('https://qypassport.xin.com/Account/GenerateVerificationCode?time=%s' % time.time()).content
    with open('captcha.jpeg','wb') as imgfile:
        imgfile.write(img)

def baiduRecognize():
    api = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=nPM1aGoU27TOVjnxhKVs55BH&client_secret=UaEKB7dcyda4PP9SS0cy9ABlDCpqxRlL'
    result = requests.get(api)
    token = json.loads(result.text)
    img = base64Img('captcha.jpeg')
    recognize_api = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=%s' % token['access_token']
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    params = {'image':img}
    result = requests.post(recognize_api,params,headers=headers).text
    print(result)
    word = json.loads(result)
    if not word['words_result']:
        return False
    return word['words_result'][0]['words']


class CaptchaRecognize:
    def __init__(self):
        self.letters=['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        self.loadSet()

    def loadSet(self):
        path, filename = os.path.split(os.path.abspath(__file__)) 
        self.imgset=[]
        for letter in self.letters:
            temp=[]
            for img in os.listdir('%s/icon/%s'%(path,letter)):
                temp.append(buildvector(Image.open('%s/icon/%s/%s'%(path,letter,img))))
            self.imgset.append({letter:temp})

    #计算矢量大小
    def magnitude(self,concordance):
        total = 0
        for word,count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    #计算矢量之间的 cos 值
    def relation(self,concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))

    def recognise(self,image):
        image=convert_image(image)
        images=cut_image(image,False)
        vectors=[]
        for img in images:
            vectors.append(buildvector(img))
        result=[]
        for vector in vectors:
            guess=[]
            for image in self.imgset:
                for letter,temp in image.items():
                    relevance=0
                    num=0
                    for img in temp:
                        relevance+=self.relation(vector,img)#验证码 比较码
                        num+=1
                    relevance=relevance/num
                    guess.append((relevance,letter))
            guess.sort(reverse=True)
            result.append(guess[0])
        return result
    def recogniseBaidu(self,session):
        getCapcha(session)
        word = baiduRecognize()
        data = []
        if not word:
            return self.recogniseBaidu(session)
        for w in word:
            w = w.upper()
            if w in self.letters:
                data.append(w)
        if len(data)!=4:
            return self.recogniseBaidu(session)
        return data

if __name__=='__main__':
    pass
    imageRecognize=CaptchaRecognize()
    str = imageRecognize.recogniseBaidu()
    print(str)
    # image=Image.open('images/1.jpeg')
    # result=imageRecognize.recognise(image)
    # string=[''.join(item[1]) for item in result]
    # print(string)
