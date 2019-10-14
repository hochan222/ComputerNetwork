#!/usr/bin/env python
# coding: utf-8

# # Parsing HTTP Header lines
# HTTP server 구현에 필요한 module인 headers.py를 먼저 작성하자. Python starter code는 이 화면 메뉴에서 다음과 같이 download할 수 있다.
# ```
# File >> Download as >> Python (.py)
# ```
# Function ```parse_headers```와 ```to_bytes```를 완성하라.

# In[81]:


def parse_headers(rfile):
    """Read from rfile and parse header lines
    :param rfile: input file-like object
    :returns:     parsed header dict 
                  (Keys in the dict are capitalized for convention)
                  (also I dont use '':word'convention of HTTP/2.0 convention or  SPDY just use'word')
    """
    
    headers = {}
    ### Your code here    
    status = rfile.readline().decode("utf-8").split(' ')  # read status line
    headers['METHOD']=status[0]
    headers['PATH']=status[1]
    headers['VERSION']=status[2].replace('\r\n','')
    
    while True:
        line = rfile.readline().decode("utf-8").split(':')
        if line[0] == '\r\n':
            break
        else:
            headers[line[0].upper()]=line[1].strip().replace('\r\n','')
    return headers

def to_bytes(headers):
    """Convert headers dict into plain bytes separated by CRLF
    :param headers: header dict
    :returns:       bytes
    """
    text = ''
    text += 'GET /test/index.html HTTP/1.1\r\n'
    for k in headers:
        line = k+': '+headers[k]+'\r\n'
        text += line
    text += '\r\n'
    return bytes(text, 'utf-8')
    
    ### Your code here
#     return text.encode()

# Tester
if __name__ == '__main__':
    # read request message from an HTTP client
    import io
    request_msg = b'''GET /test/index.html HTTP/1.1\r
host: mclab.hufs.ac.kr\r
CONNECTION: close\r
\r
'''
    file = io.BytesIO(request_msg)
    request_headers = parse_headers(file)
    print('request_headers: ', request_headers)
    
    # Build response headers
    headers = {
        'Date': 'Thu, 27 Sep 2018 04:25:01 GMT', 
        'Server': 'Apache/2.2.22 (Ubuntu)', 
        'Last-modified': 'Tue, 19 Sep 2017 06:13:15 GMT', 
        'Etag': '"1e982f-569-55984c1337a5f"', 
        'Accept-ranges': 'bytes', 
        'Vary': 'Accept-Encoding',
        'Connection': 'close', 
              }
    headers['Content-type'] = 'text/html'
    headers['Content-length'] = '1385'
    header_lines = to_bytes(headers)
    print()
    print('header_lines: ', header_lines)
    print()
    file = io.BytesIO(header_lines)
    request_headers = parse_headers(file)
    print('request_headers: ', request_headers)


# In[ ]:




