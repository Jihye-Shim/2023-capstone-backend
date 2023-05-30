import requests
from bs4 import BeautifulSoup
import time

# 알림을 받을 홈페이지의 URL
an_url = 'http://board.sejong.ac.kr/boardlist.do?bbsConfigFK=333'
univ_url = 'http://board.sejong.ac.kr/boardlist.do?bbsConfigFK=335'

# 이전에 확인한 공지사항 리스트?! - 뭘로 저장해두지?
previous_notices = []

def check_for_new_notice(url):
    global previous_notices
    
    # 홈페이지 HTML
    response = requests.get(url)
    html = response.text
    
    # BeautifulSoup -> HTML을 파싱
    soup = BeautifulSoup(html, 'html.parser')
    notices = []
    # 공지사항 요소
    for i in range(1, 11):
        notice_elements = soup.select(f'body > div > table > tbody > tr:nth-child({i}) > td.subject > a')  # 공지사항 링크 요소를 선택합니다
        current_notices = [element.text.strip() for element in notice_elements]
        notice = current_notices[0]
        notices.append(notice)
    
    # 공지사항이 없는 경우, 이전 공지사항 리스트를 초기화하고 함수 종료
    #if len(notice_elements) == 0:
    #    previous_notices = []
    #    return
    
    # 현재 공지사항 리스트
    current_notices = [element.text.strip() for element in notice_elements]
    
    # 새로운 공지사항 판별
    #new_notices = [notice for notice in current_notices if notice not in previous_notices]

    #if new_notices:
    #    current_notices.append(new_notices)
    '''
    if new_notices:
        # 새로운 공지사항 추가, 알림 출력
        print('새로운 공지사항이 추가되었습니다:')
        for notice in new_notices:
            # 가장 최근 공지 10개?
            print(notice)
            print('-------------------------------')
        
        # 이전 공지사항 리스트를 업데이트
        previous_notices = current_notices
    
    else:
        print('추가내용이 없습니다')
    '''
    print(notices)
    return notices

# 일정 간격으로 공지사항을 확인
#while True:
#    check_for_new_notice()
#    time.sleep(10) #지금은 10초

def check_recent_announcement():
    r1 = check_for_new_notice(an_url)
    r2 = check_for_new_notice(univ_url)
    result1 = {}
    result2 = {}
    n = 1
    for i in r1:
        result1[f"{n}"] = i
        n+=1
    n = 1
    for i in r2:
        result2[f"{n}"] = i
        n+=1
    return {"공지": result1, "학사공지": result2}