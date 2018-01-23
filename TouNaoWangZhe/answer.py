# encoding=utf8
import time
#执行命令subprocess
import subprocess
import requests
import os
import random
from io import BytesIO
from PIL import Image
from aip import AipOcr



#答案坐标位置
config={
    '头脑王者':{
        'title':(80,500,1000,880),
        'answers':(80,960,1000,1720),
        'point':[
            (316,993,723,1078),
            (316,1174,723,1292),
            (316,1366,723,1469),
            (316,1570,723,1657),
        ]
    },
    '西瓜视频':{
        'box':(80,400,1000,1250)
    }
}

def get_screenshot():
    # 手机截图++++++++++++++++++++
    process = subprocess.Popen('adb shell screencap -p',shell=True, stdout=subprocess.PIPE)
    binary_screenshot = process.stdout.read()
    binary_screenshot = binary_screenshot.replace(b'\r\n', b'\n')
    with open('screenshot.png', 'wb') as f:
        f.write(binary_screenshot)
    #把图片写入内存
    img_fb=BytesIO()
    img_fb.write(binary_screenshot)
    #图片处理(切图处理 剩下可读关键性文字)
    img=Image.open(img_fb)
    #切图题目
    title_img=img.crop((80,500,1000,880))
    #切图答案
    answers_img=img.crop((80,960,1000,1720))
    #拼接图片
    new_img=Image.new('RGBA',(920,1140))
    new_img.paste(title_img,(0,0,920,380))
    new_img.paste(answers_img,(0,380,920,1140))
    #提取内存对象(截图)
    new_img_fb=BytesIO()
    new_img.save(new_img_fb,'png')
    with open('test.png','wb') as f:
        f.write(new_img_fb.getvalue())
    #内存对象内容
    return new_img_fb.getvalue()

def get_word_by_img(img):
    # 提取文字++++++++++++++++++++
    # 定义常量
    # 图片路径
    APP_ID = '10730416'
    API_KEY = '9oexlN08aSn0jHngt4fdXOqi'
    SECRET_KEY = 'YmNxGsWIaaIpGM47KVQD9iaPUaaGcdHH'
    # 初始化AipFace对象
    aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # 其他配置参数
    options = {
        'detect_direction': 'true',  # 检测图像朝向
        'language_type': 'CHN_ENG',  # 识别语言类型
    }
    # 调用通用文字识别接口
    result = aipOcr.basicGeneral(img,options)
    return result

def baidu(question,answers):
    # 百度搜索++++++++++++++++++++
    url='https://baidu.com/s'
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    data={
        'wd':question
    }
    res=requests.get(url=url,params=data,headers=headers)
    html=res.text
    #寻找答案次数最多
    for i in range(len(answers)):
        #返回三个参数(答案最多的条数,当前的答案,当前的索引)
        answers[i]=(html.count(answers[i]),answers[i],i)
    #排序
    answers.sort(reverse=True)
    return answers

def click(point):
    # 点击答案++++++++++++++++++++
    cmd='adb shell input swipe %s %s %s %s %s' %(
         point[0],
         point[1],
         point[0]+random.randint(0,3),
         point[1]+random.randint(0,3),
         200
    )
    os.system(cmd)

def run():
    print('准备答题...')
    while True:
        #根据回车之后往下执行代码
        input('请输入回车开始答题:')
        time.sleep(1)
        #获取手机截图
        img=get_screenshot()
        #提取文字
        info=get_word_by_img(img)
        if(info['words_result_num'])<5:
            continue
        #获取答案
        answers=[x['words'] for x in info['words_result'][-4:]]
        #获取问题
        question=''.join([x['words'] for x in info['words_result'][:-4]])
        print(question)
        print(answers)

        #搜索结果
        res=baidu(question,answers)
        print(res)
        print('正确答案:',[res[0]])
        #点击答案(res[2]2为正确答案的索引号)
        click(config['头脑王者']['point'][res[0][2]])


if __name__=='__main__':
    run()
