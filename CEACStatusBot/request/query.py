import requests
from bs4 import BeautifulSoup
import base64
import os
import time

from CEACStatusBot.captcha import CaptchaHandle, OnnxCaptchaHandle

def query_status(location, application_num, captchaHandle:CaptchaHandle=OnnxCaptchaHandle("captcha.onnx")):

  
    isSuccess = False
    failCount = 0

    while not isSuccess and failCount<5:
        failCount += 1
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "ceac.state.gov",
        }


        session = requests.Session()
        ROOT = "https://ceac.state.gov"
        # if not os.path.exists("tmp"):
        #     os.mkdir("tmp")
        # -------NIV page------
        try:
            # 发送请求的代码
            r = session.get(url=f"{ROOT}/ceacstattracker/status.aspx?App=IV", headers=headers)
        
        except Exception as e:
            # 处理连接错误异常
            print(e)
       
            isSuccess = False
            continue
        # with open("tmp/NIV.html", "w") as f:
        #     f.write(r.text)
        soup = BeautifulSoup(r.text, features="lxml")

    
        # Find captcha image
        captcha = soup.find(name="img", id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage")
   
        image_url = ROOT + captcha["src"]
        #print("Captcha URL ="+ image_url)

        try:
            #img_resp = session.get(image_url)
            img_resp = session.get(url=image_url, headers=headers)
        except Exception as e:
            print(e)
            continue
       
      
        # with open("tmp/captcha.jpeg", "wb") as f:
        #     f.write(img_resp.content)
        # img_base64 = base64.b64encode(img_resp.content).decode("ascii")
       
        # Resolve captcha
        captcha_num = captchaHandle.solve(img_resp.content)
        #print(captcha_num)

        # Fill form
        def update_from_current_page(cur_page, name, data):
            ele = cur_page.find(name="input", attrs={"name": name})
            if ele:
                data[name] = ele["value"]

    
        data = {
            "ctl00$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btnSubmit",
            "ctl00_ToolkitScriptManager1_HiddenField": ";;AjaxControlToolkit, Version=4.1.40412.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-US:acfc7575-cdee-46af-964f-5d85d9cdcf92:de1feab2:f9cec9bc:a67c2700:f2c8e708:8613aea7:3202a5a2:ab09e3fe:87104b7c:be6fb298",
            "ctl00$ContentPlaceHolder1$Visa_Application_Type": "IV",
            "ctl00$ContentPlaceHolder1$Visa_Case_Number": location+application_num,
            "ctl00$ContentPlaceHolder1$Captcha": captcha_num,
            "LBD_VCID_c_status_ctl00_contentplaceholder1_defaultcaptcha": "",
            "LBD_BackWorkaround_c_status_ctl00_contentplaceholder1_defaultcaptcha": "0",
             "__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnSubmit",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": "H53X8HyfZcnPgYrD59A1zxQDNXGxidKWOmehTt7061j+HkbPpDDUkuGYueRbW0nxN6NUNZgIPGFW2ItF7HNqVNq1pfU94RKCWB6FCidje8BYJQy/LajOXmlBs0KYXQ8T",
            "__VIEWSTATEGENERATOR": "DBF1011F",
            "__VIEWSTATEENCRYPTED": "",
            "__ASYNCPOST": "true",
        }
        data["ctl00$ContentPlaceHolder1$Captcha"] = captcha_num
        fields_need_update = [
            "__VIEWSTATE",
            "__VIEWSTATEGENERATOR",
            "LBD_VCID_c_status_ctl00_contentplaceholder1_defaultcaptcha",
        ]
        for field in fields_need_update:
            update_from_current_page(soup, field, data)

        # logger.info(json.dumps(data, indent=4))
        # logger.info(f"{ROOT}/ceacstattracker/status.aspx")

        # -------Result page------
        try:
            # 发送请求的代码
            r = session.post(url=f"{ROOT}/ceacstattracker/status.aspx", headers=headers, data=data)
        except Exception as e:
            # 处理连接错误异常
            print(e)
            isSuccess = False
            continue
        # with open("tmp/RESULT.html", "w") as f:
        #     f.write(r.text)

        # Get useful data
        soup = BeautifulSoup(r.text, features="lxml")
        status_tag = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus")
  
        if not status_tag:
            isSuccess = False
            continue
            # return {"success": False}
       # print("status_tag OK")
        application_num_returned = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblCaseNo").string
        assert application_num_returned == location+application_num
        status = status_tag.string
        visa_type = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblAppName").string
        description = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblMessage").string

        isSuccess = True
        result = {
            "success": True,
            "time": str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
            "visa_type": visa_type,
            "status": status,
            "description": description,
            "application_num": application_num_returned,
            "application_num_origin":location+application_num
        }

    if not isSuccess:
        result = {
            "success": False,
        }
    return result