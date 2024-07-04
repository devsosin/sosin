import requests
try:
    from bs4 import BeautifulSoup
except:
    print('you need to install BeautifulSoup4\n$ : python -m pip install BeautifulSoup4')

country_list = [
    '미국', '유럽연합', '일본', '중국', '홍콩', '대만', '영국', '오만', '캐나다', 
    '스위스', '스웨덴', '호주', '뉴질랜드', '체코', '칠레', '터키', '몽골', '이스라엘', 
    '덴마크', '노르웨이', '사우디아라비아', '쿠웨이트', '바레인', '아랍에미리트', '요르단', 
    '이집트', '태국', '싱가포르', '말레이시아', '인도네시아', '카타르', '카자흐스탄', '브루나이', 
    '인도', '파키스탄', '방글라데시', '필리핀', '멕시코', '브라질', '베트남', '남아프리카', 
    '러시아', '헝가리', '폴란드', '스리랑카', '알제리', '케냐', '콜롬비아', '탄자니아', 
    '네팔', '루마니아', '리비아', '마카오', '미얀마', '에티오피아', '우즈베키스탄', '캄보디아', '피지'
]

symbols = [
'AUD', 'USD', 'JPY', 'CNY', 'HKD', 'TWD', 'NTD', 'GBP', 'OMR', 'CAD', 'CHF', 'SEK', 'AUD', 'NZD',
'CZK', 'CLP', 'TRY', 'MNT', 'ILS', 'DKK', 'NOK', 'SAR', 'KWD', 'BHD', 'AED', 'JOD', 'EGP', 'THB',
'SGD', 'MYR', 'IDR', 'QAR', 'KZT', 'BND', 'INR', 'PKR', 'BDT', 'PHP', 'MXN', 'BRL', 'VND', 'ZAR',
'RUB', 'HUF', 'PLN', 'LKR', 'DZD', 'KES', 'COP', 'TZS', 'NPR', 'RON', 'LYD', 'MOP', 'MMK', 'ETB',
'UZS', 'KHR', 'FJD',
]

name_to_symbol = {'미국': 'USD', '유럽연합': 'EUR', '일본': 'JPY', '중국': 'CNY', '홍콩': 'HKD',
                  '대만': 'NTD', '영국': 'GBP', '오만': 'OMR', '캐나다': 'CAD', '스위스': 'CHF',
                  '스웨덴': 'SEK', '호주': 'AUD', '뉴질랜드': 'NZD', '체코': 'CZK', '칠레': 'CLP',
                  '튀르키예': 'TRY', '몽골': 'MNT', '이스라엘': 'ILS', '덴마크': 'DKK', '노르웨이': 'NOK',
                  '사우디아라비아': 'SAR', '쿠웨이트': 'KWD', '바레인': 'BHD', '아랍에미리트': 'AED',
                  '요르단': 'JOD', '이집트': 'EGP', '태국': 'THB', '싱가포르': 'SGD', '말레이시아': 'MYR', 
                  '인도네시아': 'IDR', '카타르': 'QAR', '카자흐스탄': 'KZT', '브루나이': 'BND', '인도': 'INR',
                  '파키스탄': 'PKR', '방글라데시': 'BDT', '필리핀': 'PHP', '멕시코': 'MXN', '브라질': 'BRL',
                  '베트남': 'VND', '남아프리카 공화국': 'ZAR', '러시아': 'RUB', '헝가리': 'HUF', '폴란드': 'PLN',
                  '스리랑카': 'LKR', '알제리': 'DZD', '케냐': 'KES', '콜롬비아': 'COP', '탄자니아': 'TZS',
                  '네팔': 'NPR', '루마니아': 'RON', '리비아': 'LYD', '마카오': 'MOP', '미얀마': 'MMK', 
                  '에티오피아': 'ETB', '우즈베키스탄': 'UZS', '캄보디아': 'KHR', '피지': 'FJD'}

symbol_to_name = {
    v: k
    for k, v in name_to_symbol.items()
}

def get_currency(symbol):
    symbol = symbol.upper()
    if symbol == 'KRW'or symbol =='한국':
        return 1.0
    
    assert symbol in symbol_to_name or symbol in name_to_symbol, '유효하지 않은 symbol 입니다.'

    if symbol in symbol_to_name:
        name = symbol_to_name[symbol]
    else:
        name = name_to_symbol[symbol]
    r = requests.get(f'https://www.google.com/search?q={name}환율')
    sp = BeautifulSoup(r.text, 'html.parser')
    return float(sp.select_one('.BNeawe.iBp4i.AP7Wnd').text.split()[0].replace(',', ''))
