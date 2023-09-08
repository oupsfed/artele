

def check_paginator(paginators_btns, page):
    callback_prev = paginators_btns[0].callback_data.split(':')
    callback_next = paginators_btns[1].callback_data.split(':')
    assert paginators_btns[0].text == '⬅️', (
        'Кнопка назад не существует или имеет неправильный текст'
    )
    assert paginators_btns[1].text == '➡️', (
        'Кнопка вперед не существует или имеет неправильный текст'
    )
    assert 'list' in callback_prev[1], (
        'кнопка назад возвращает неправильную callback_data_action'
    )
    assert 'list' in callback_next[1], (
        'кнопка вперед возвращает неправильную callback_data_action'
    )
    assert int(callback_prev[3]) == page - 1, (
        'кнопка назад возвращает неправильную callback_data_page'
    )
    assert int(callback_next[3]) == page + 1, (
        'кнопка вперед возвращает неправильную callback_data_page'
    )
