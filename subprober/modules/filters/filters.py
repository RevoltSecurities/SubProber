import re

async def filter_by_code(response, code_list=None) -> bool:
    if not code_list: 
        return True
    for code in code_list:
        if int(response.status_code) == int(code):
            return False
    return True

async def filter_code_range(response, code=None) -> bool:
    if code is None:
        return True
    min_code,max_code = map(int, code.split("-"))
    if min_code is None or max_code is None:
        return True
    if min_code <= response.status_code <= max_code:
        return False
    return True

async def filter_url_path_contains(response, paths=None) -> bool:
    if not paths: 
        return True
    for path in paths:
        if str(path) in str(response.url.path):
            return False
    return True

async def filter_word_body(response, words=None) -> bool:
    if not words: 
        return True
    for word in words:
        if str(word) in response.text:
            return False
    return True

async def filter_by_ints(requested_code, code_list=None) -> bool:
    if not code_list: 
        return True
    for code in code_list:
        if int(requested_code) == int(code):
            return False
    return True

async def filter_by_regex(response, regexes=None) -> bool:
    if not regexes: 
        return True
    for regex in regexes:
        if re.search(regex, response.text):
            return False
    return True

async def filter_response_time(response, max_time=None) -> bool:
    if max_time is None:
        return True
    if float(response.elapsed.total_seconds()) > float(max_time):
        return False
    return True
