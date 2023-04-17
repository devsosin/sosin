import os
import email
import imaplib
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header

from os.path import basename

import time
from datetime import datetime

import traceback

def is_ascii(s):
    '''
    ASCII 체크 함수
    '''
    return all(ord(c) < 128 for c in s)

def get_subject(subject):
    '''
    메일의 제목 반환
    '''
    s, encoding = decode_header(subject)[0]
    if encoding:
        return str(s, encoding, 'replace')
    else:
        return s

def get_body(msg):
    '''
    메일 내용 반환
    '''
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def get_email(email_id, email_pw, header_subjects:list=[], header_since:str=None,
                header_from:str=None, label:str=None, mail_server:str='naver', 
                encode_type='utf-8', save_path:str=None, remove_email=True
                ) -> list[dict]:
    '''
    메일 제목에 특정 문자열이 있거나 특정 발송인의 이메일 반환
    **필수값**
    email_id, email_pw: 메일서버 계정정보
    header_str : 검색할 제목 (non-ascii) | header_from : 발송인
    **선택값**
    mail_server : naver, gmail
    save_path : 첨부 파일 저장 경로
    return list[dict]
    [
        {
            'subject': subject,
            'date': date
            'content': mail_content,
            'attaches': [str]
        }
    ]
    '''

    # 메일 검색어 ASCII 체크
    if header_subjects:
        assert all([is_ascii(header_str) for header_str in header_subjects]), 'In ASCII 문자열만 입력해주세요 (영문, 기호)'
    assert header_subjects or header_from or header_since or label, '메일 제목이나 발신인, 날짜, 라벨을 추가해주세요.'

    IMAP_SERVER = f"imap.{mail_server.lower().strip()}.com" 
    IMAP_PORT = 993

    email_result = []

    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        imap.login(email_id, email_pw)
        imap.select('inbox') if not label else imap.select(label)
        search_list = []
        if header_subjects:
            if len(header_subjects) == 1:
                search_list.append(f'(Header Subject "{header_subjects[0]}")')
            else:
                # 230315 업데이트
                search_list.append('OR ' * (len(header_subjects)-1) + ' '.join([f'Subject "{hs}"' for hs in header_subjects]) if header_subjects else '')
        
        if header_from:
            search_list.append(f'(from "{header_from}")' if header_from else '')
            
        if header_since:
            search_list.append(f'(SINCE "{header_since}")')

        if search_list:
            _, data = imap.uid('search', None, *search_list)
        else:
            _, data = imap.uid('search', None, 'All')

        for target_uid in data[0].split():
            try:
                _, data = imap.uid('fetch', target_uid, '(RFC822)')
                try:
                    email_message = email.message_from_string(data[0][1].decode(encode_type))
                except:
                    email_message = email.message_from_string(data[0][1].decode('cp949')) #euc-kr

                # 메일 제목
                subject = get_subject(email_message['subject'])

                # 메일 내용
                try:
                    mail_content = get_body(email_message).decode(encode_type).strip()
                except:
                    # print(target_uid, subject)
                    mail_content = get_body(email_message).decode('cp949').strip()

                # 수신 일시
                timestamp = (time.mktime(email.utils.parsedate(email_message['Date'])))
                mail_time = datetime.fromtimestamp(timestamp)

                # 첨부 파일
                file_list = []
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    try:
                        filename = part.get_filename()
                        s, encoding = decode_header(filename)[0]
                        if encoding:
                            filename = str(s, encoding, 'replace')

                        file_list.append({
                            'name': filename,
                            'file': part.get_payload(decode=True)
                        })
                    except:
                        pass

                saved_files = []

                # 첨부파일 저장여부
                if save_path:
                    os.makedirs(save_path, exist_ok=True)
                    for eval_file in file_list:
                        att_path = os.path.join(save_path, eval_file['name'])
                        saved_files.append(str(att_path))
                        if not os.path.isfile(att_path):
                            with open(att_path, 'wb') as fp:
                                fp.write(eval_file['file'])

                # 이메일 지우기(지울 메세지의 uid)
                if remove_email:
                    imap.uid('store', target_uid, '+FLAGS', '(\\Deleted)')
                    # 메일함 정리하기
                    imap.expunge()

                email_result.append({
                    'subject':subject,
                    'date': mail_time,
                    'content': mail_content,
                    'attaches': saved_files,
                })
            except:
                with open('./email_error', 'a') as f:
                    f.write('에러 발생, ' + str(target_uid) + '\n')

    except Exception as e:
        print(e)
        traceback.print_exc()
    finally:
        imap.close()
        imap.logout()
        
    return email_result

# 이메일 발송 함수
def send_email(email_id, email_pw, 
                from_user:str, to_users:list, subject:str, content:str, # contents -> (content, 'html'), (content, 'plain')
                mail_server:str='naver', attachments:list=[], cc_targets=[]
                ) -> bool:
    '''
    메일을 발송하는 함수입니다.
    **필수값**
    email_id, email_pw: 메일서버 계정정보
    from_user: 보내는 사람의 이메일 주소
    to_users: 받는 사람의 이메일 주소들 (list)
    subject: 메일 제목
    content: 메일 내용
    **선택**
    mail_server: 메일 서버 (naver, gmail)
    attachments: 첨부 파일들 (파일경로 리스트)
    cc_targets: 참조 이메일 주소들 (list)
    '''

    SMTP_SERVER = f'smtp.{mail_server.lower()}.com'
    SMTP_PORT = 465

    try:
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        smtp.login(email_id, email_pw)

        msg = MIMEMultipart('alternative')

        if attachments:
            msg = MIMEMultipart('mixed')

            for attachment in attachments:
                email_file = MIMEBase('application', 'octet-stream')

                with open(attachment, 'rb') as f:
                    file_data = f.read()

                email_file.set_payload(file_data)
                encoders.encode_base64(email_file)

                file_name = basename(attachment)
                email_file.add_header('Content-Disposition', 'attachment',
                    filename=file_name)

                msg.attach(email_file)

        msg['From'] = from_user
        msg['To'] = ','.join(set(to_users))
        if cc_targets:
            msg['CC'] = ','.join(cc_targets)
        msg['Subject'] = subject

        text = MIMEText(content)
        msg.attach(text)

        smtp.sendmail(from_user, set(to_users+cc_targets), msg.as_string())
        print('이메일 발송 성공 !')
        return True

    except Exception as e:
        print(e)
    finally:
        smtp.close()
    
    return False