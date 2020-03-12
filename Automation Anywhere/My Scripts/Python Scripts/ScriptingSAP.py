import logging
import logging.handlers
import os
import subprocess
import sys
import time

import win32com.client
from win32api import *
from win32com import *
from win32com.client import *

# Use Python standard logging module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler('rpa_log.txt')
handler.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - (%(filename)s:%(funcName)s:%(lineno)d) >>> %(message)s')
handler.setFormatter(formatter)
streamHadendler.setFormatter(formatter)

# add the file handler to the logger
logger.addHandler(handler)
logger.addHandler(streamHandler)

#Verifying a SAP Object Exist
def verify(session=None, control=None):
    while True:
        try:
            session.FindById(control)
            return session.FindById(control)
        except:
            # Do something else here if needed
            logger.error("in '%s', SAP Object Not Exist ...", control)
            return False

#Return SAP Connection Name
def get_sap_connection_name(vSystemID):

    vName = ""

    if vSystemID == "GMP":
        vName = "01. ECC Logistics System"
    elif vSystemID == "GFP":
        vName = "02. ECC Finance System"
    elif vSystemID == "GBP":
        vName = "03. BI System"
    elif vSystemID == "GPP":
        vName = "04. PI System"
    elif vSystemID == "GIP":
        vName = "05. Standard Process and Information System"
    elif vSystemID == "GMR":
        vName = "GMR"
    elif vSystemID == "GMQ":
        vName = "GMQ"
    elif vSystemID == "GFR":
        vName = "GFR"
    else:
        vName = vSystemID

    return vName

#SAP LogOn


def sap_login(vConnection, vID, vPW):
    #登录
    logger.debug("로그인에서 SAP 실행")
    path = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
    subprocess.Popen(path)
    # subprocess.check_call(['C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe', '-system=GFR', '-client=100', '-user=RPA.CREAT05', '-pw=poiuy5432!!'])
    time.sleep(10)

    # SAPguiAPP = win32com.client.Dispatch(“Sapgui.ScriptingCtrl.1”)
    # Connection = SAPguiAPP.OpenConnection(“75 – NSP – Production Simple SAP Access”,1)
    # Session1 = Connection.Children(0)


    SapGuiAuto = win32com.client.GetObject('SAPGUI')
    if not type(SapGuiAuto) == win32com.client.CDispatch:
        logger.error("SapGuiAuto error...")
        return
    # SAPguiAPP = win32com.client.Dispatch("Sapgui.ScriptingCtrl.1")
    logger.debug("로그인에서 SAP GUI Object 획득...")

    application = SapGuiAuto.GetScriptingEngine
    if not type(application) == win32com.client.CDispatch:
        SapGuiAuto = None
        logger.error("application error...")
        return
    logger.debug("로그인에서 SapGuiAuto.GetScriptingEngine Object 획득...")

    try:
        connection = application.OpenConnection(vConnection, True)
    # connection = SAPguiAPP.OpenConnection(vConnection,1)
    except:
        logger.error("In sap_login, Connection Name : [%s]connection error...",vConnection)
        logger.error("In sap_login, Connection error : %s ", sys.exc_info()[0])
        logger.exception('Got exception on main handler')
        application = None
        SapGuiAuto = None
        return
    logger.debug("로그인에서 application.OpenConnection(%s, True) Object 획득...",vConnection)

    session = connection.Children(0)
    if not type(session) == win32com.client.CDispatch:
        connection = None
        application = None
        SapGuiAuto = None
        logger.error("session error...")
        return

    session.findById("wnd[0]/usr/txtRSYST-BNAME").text = vID
    session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = vPW
    session.findById("wnd[0]").sendVKey(0)

    #verify(session, 'wnd[0]/tbar[1]/btn[6]').Press()
    if verify(session, 'wnd[1]'):
        if session.findById("wnd[1]").Text == "License Information for Multiple Logon":
            if session.findById("wnd[1]/usr/radMULTI_LOGON_OPT2").Selected == False:
                session.findById("wnd[1]/usr/radMULTI_LOGON_OPT2").Select()
                session.findById("wnd[0]").sendVKey(0)

    return session

#SAP LogOut
def sap_logout(session):
    if not type(session) == win32com.client.CDispatch:
        logger.error("in sap_logout, session error...")
        return

    # session.findById("wnd[0]/tbar[0]/btn[15]").press()
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]").close()
    if verify(session, 'wnd[1]/usr/btnSPOP-OPTION1'):
        session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()

    return True

#SAP Choose TCode
def choose_tcode(session, vTcode):
    try:
        session.findById("wnd[0]/tbar[0]/okcd").text = vTcode
        session.findById("wnd[0]").sendVKey(0)
        return True
    except:
        logger.error("in choose_tcode, error...")
        return False

#Define each business sub function
def download_fbl3n_report(session):
    # 'Dynamic Selection 클릭, Business Area = AP01
    session.findById("wnd[0]/tbar[1]/btn[16]").press()
    session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/ctxt%%DYN012-LOW").text = "AP01"
    # 'GL Account=21016901 입력, 'Open Items 에 오늘 날짜 입력
    session.findById("wnd[0]/usr/ctxtSD_SAKNR-LOW").text = "21016901"
    session.findById("wnd[0]/usr/ctxtSD_BUKRS-LOW").text = "C100"
    # 'List Layout에서 '/RPA ADV CLR' 입력
    session.findById("wnd[0]/usr/ctxtPA_VARI").text = "/RPA ADV CLR"

    # 'In SAP Screen Menu, Program -> Excute F8 Click
    session.findById("wnd[0]").sendVKey(8)
    # 'Continue Enter
    session.findById("wnd[1]/tbar[0]/btn[0]").press()

    # 'In SAP Screen Menu, List -> Export -> Spreadsheet... Shift + F4 Click
    session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

    # 'In SAP Screen Select Spreadsheet, Formats -> Select from All Available Formats -> Office 2007 - XML for Excel | .XSLX Click
    session.findById("wnd[1]/usr/radRB_OTHERS").setFocus()
    session.findById("wnd[1]/usr/radRB_OTHERS").select()
    session.findById("wnd[1]/usr/cmbG_LISTBOX").setFocus()
    session.findById("wnd[1]/usr/cmbG_LISTBOX").key = "10"
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\phs\Documents\Python Scripts"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "FBL3N_LIST.xlsx"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 15
    # ''Generate button click
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    # ''Replace button click
    session.findById("wnd[1]/tbar[0]/btn[11]").press()

# 로그인 하면으로 전환
# session.findById("wnd[0]/tbar[0]/okcd").Text = "/n"
# session.findById("wnd[0]").sendVKey(0)


#Define each business main function
def main(vConnection, vID, vPW):

    logger.info("작업시작...")

    if sys.argv[1] == "":
        vConnection = "GFR"
        vID = "RPA.CREAT05"
        vPW = "poiuy5432!!"
    else:
        vConnection = sys.argv[1]
        vID = sys.argv[2]
        vPW = sys.argv[3]
    
    logger.debug("vConnection : %s vID : %s vPW : %s", vConnection, vID, vPW)

    vConnection_Name = get_sap_connection_name(vConnection)

    session = sap_login(vConnection_Name, vID, vPW)
    if not type(session) == win32com.client.CDispatch:
        logger.error("in main, session error...")
        return

    # session.findById("wnd[0]/tbar[0]/okcd").text = "FBL3N"
    # session.findById("wnd[0]").sendVKey(0)
    if not choose_tcode(session, "FBL3N"):
        logger.error("in main, tcode error...")
        return

    download_fbl3n_report(session)


    if sap_logout(session):
        logger.debug("in main, Logout success...")

    logger.info("작업종료...")


if __name__ == "__main__":
    # 실행시 인수로 SAP 접속시스템명, 로그인 ID, 비밀번호를 받는다.
    # 필요에 따라 인수는 sys.argv[4], sys.argv[5] 등 으로 추가 될 수 있다.
    main(sys.argv[1], sys.argv[2], sys.argv[3])
