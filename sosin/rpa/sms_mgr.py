import requests

class AligoManager:
    """
    Aligo Messages API

    https://smartsms.aligo.in/
    """

    def __init__(self, key, user_id, sender_phone, is_test) -> None:
        """
        Aligo configs
        key = API Key
        user_id = User ID
        sender_phone = phone number
        is_test = test Y/N
        """
        self.key = key 
        self.user_id = user_id 
        self.sender_phone = sender_phone 
        self.is_test = is_test 

    def send_sms(self, rec_list:list, msg_list:list, msg_type='LMS') -> int:
        """
        send messages (text)

        * required
        rec_list (receiver phone numbers)
        msg_list (messages)
        """
        mass_send_url = 'https://apis.aligo.in/send_mass/' 
        cnt = len(rec_list)
        data = {
            'key': self.key, 
            'userid': self.user_id, 
            'sender': self.sender_phone, 
            'cnt' : cnt, # 메세지 전송건수(번호,메세지 매칭건수)
            'msg_type' : msg_type, 
            'testmode_yn' : self.is_test
        }
        for i in range(1, cnt+1):
            data[f'rec_{i}'] = rec_list[i-1]
            data[f'msg_{i}'] = msg_list[i-1]

        return requests.post(mass_send_url, data=data).json()['success_cnt']
    
    def send_mms(self, rec:str, msg:str, image_path:str) -> int:
        """
        send messages (image)

        * required
        rec (receiver phone number)
        msg (message)
        image_path (image file)
        """
        send_url = 'https://apis.aligo.in/send/'
        data = {
            'key': self.key,
            'userid': self.user_id,
            'sender': self.sender_phone,
            'receiver': rec, # 수신번호 (,활용하여 1000명까지 추가 가능)
            'msg': msg, 
            'msg_type' : 'MMS',
            'testmode_yn' : self.is_test 
        }
        image_file = {'image' : open(image_path, 'rb')}

        return requests.post(send_url, data=data, files=image_file).json()['success_cnt']

if __name__ == '__main__':
    config = {
        'ALIGO_KEY': 'aligo-api-key',
        'ALIGO_ID': 'aligo-user-id',
        'ALIGO_HP': 'aligo-phone-number',
        'ALIGO_TEST': 'Y/N'
    }
    aligo_mgr = AligoManager(key=config['ALIGO_KEY'], user_id=config['ALIGO_ID'], 
                             sender_phone=config['ALIGO_HP'], is_test=config['ALIGO_TEST'])
    
    receiver_list = ['00012345678', '00023456789']
    message_list = ['Test 1', 'Test 2']
    success_count = aligo_mgr.send_sms(receiver_list, message_list)
    print('success: %d'%success_count)

    success_count = aligo_mgr.send_mms('00012345678', 'Test Image', './image.jpg')
    print('success: %d'%success_count)

