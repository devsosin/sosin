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
'AUD',
'USD',
'JPY',
]

symbol_to_name = {
    'AUD': '호주',
    'USD': '미국',
    'JPY': '일본',
}
name_to_symbol = {
    v: k
    for k, v in symbol_to_name.items()
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
