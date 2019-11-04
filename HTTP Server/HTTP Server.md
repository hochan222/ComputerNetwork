## Tips for writing HTTP server
```
# ## Web server에 있는 파일 위치와 읽기
# Web server는 contents가 저장된 root directory를 지정할 수 있다. 편의상 source program과 같은 directory로 하자. Request line에서 `/test/index.html` 이라는 path가 있다면, web server는 `./test/index.html` 파일을 찾아 읽으면 된다. 
# 
# Response message의 첫 줄, status line은 
#   - if the file exists, `HTTP/1.1 200 OK`
#   - otherwise, `HTTP/1.1 404 Not found`
# 
# 파일은 binary mode로 읽어야 한다(읽은 결과는 `bytes` type이다.
# 
# ## Response message의 header들  정의  
# `Date`, `Server`, `Connection` header는 반드시 만들어야 한다. Request message의 `Connection` header에 따라 Response의 `Connection` header를 `keep-alive`(default) 또는 `close`로 설정해야 한다.
# 
# File이 존재할 경우 `Accept-range`, `Content-type`, `Content-length` header를 삽입해야 한다.


# ## `socketserver` module 활용해서 server 구축하기
# 
# `socketserver.TCPServer` class를 이용하면, socket programming detail을 몰라도 구현할 수 있다. 이때 여러분은 `StreamRequestHandler` class를 상속받아 `handle` method만 implement하면 충분하다.
# 
# `TCPServer` class에서 `accept`한 connected socket을 `makefile`로 만들어 아래 `HTTPHandler` class로 pass해 준다. File-like stream object은 다음과 같이 access할 수 있다.
#   - incoming stream: `self.rfile`
#   - outgoing stream: `self.wfile`
#     - 예) `self.wfile.write(message)
# 
# AS-1에서 작성한 headers.py 파일을 import해서 header를 처리하라.
```

```python
import socketserver
import time         # to know current time
import mimetypes    # to map filenames to MIME types
import headers      # your module 'headers.py'
import io

class HTTPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        # read a request message
        # print(self.client_address[0])
        import os

        buffer = self.request.recv(1024).strip()
        file = io.BytesIO(buffer)
        request_headers = headers.parse_headers(file)
        # print('request_headers: ', request_headers)
        PATH = ''
        PATH = request_headers['PATH']
        KeepAlive = ''

        if 'Keep-Alive' in request_headers:
            KeepAlive = request_headers['Keep-Alive']
        
        if request_headers['CONNECTION']:
            CONNECTION = request_headers['CONNECTION'] 
        else:
            CONNECTION = 'keep-alive'

        print(PATH, CONNECTION)        
        pass
        senddata=b'\r\n'

        # read content from file name: '.' + path
        if PATH == '/test/index.html':
            f = open('./test/index.html', 'rb')
        elif PATH:
            if os.path.exists("." + PATH):
                if PATH == '/test' or PATH == '/test/':
                    f = open('./test/404.html', 'rb')
                else:
                    f = open('.'+PATH, 'rb')
            else:
                f = open('./test/404.html', 'rb')

        data = f.read(1024)

        while data:
            senddata+=data
            data = f.read(1024)
        f.close()        

        pass


        # Build the response message
        import mimetypes
        import time

        text = ''

        res_headers = {}
        res_headers['Date'] = time.asctime()
        res_headers['Server'] = 'MyServer/1.0'
        res_headers['Accept-range'] = 'bytes'

        if CONNECTION == 'keep-alive':
            res_headers['Connection'] = 'keep-alive'
            if KeepAlive == '':
                res_headers['Keep-Alive'] = 'timeout=10, max=100'
            else:
                KeepAlive = list(KeepAlive.split(', '))
                if int(KeepAlive[1]) -1 == 0:
                    res_headers['Connection'] = 'close'
                else:    
                    KeepAlive[1] = int(KeepAlive[0][4:]) - 1
                    KeepAlive = ', '.join(KeepAlive)
                    res_headers['Keep-Alive'] = KeepAlive

        elif CONNECTION == 'close':
            res_headers['Connection'] = 'close'

        if PATH == '/test/index.html':
            res_headers['Content-type'] = 'text/html'
            res_headers['Content-Length'] = str(os.path.getsize('./test'+'/index.html'))

            text += 'HTTP/1.1 200 OK\r\n'

        elif PATH:
            if os.path.exists("." + PATH):
                if PATH == '/test' or PATH == '/test/':
                    res_headers['Content-type'] = 'text/html'
                    res_headers['Content-Length'] = str(os.path.getsize('./test'+'/404.html'))
            
                    text += 'HTTP/1.1 200 OK\r\n'
                else:
                    res_headers['Content-type'] = mimetypes.guess_type(PATH)[0]
                    res_headers['Content-Length'] = str(os.path.getsize('.'+PATH))
                
                    text += 'HTTP/1.1 200 OK\r\n'

            else:
                res_headers['Content-type'] = 'text/html'
                res_headers['Content-Length'] = str(os.path.getsize('./test'+'/404.html'))

                text += 'HTTP/1.1 404 Not found'

        for k in res_headers:
            line = k+': '+res_headers[k]+'\r\n'
            text += line

        sbuff = text.encode()
        sbuff+=senddata
        self.wfile.write(sbuff)
        pass
        self.wfile.flush()  # Flush-out output buffer for immediate sending
    
# create a TCPServer object with your handler class
http_server = socketserver.TCPServer(('', 8001), HTTPHandler)
http_server.serve_forever()
```

## Testing your HTTP server
```
# 먼저 HTTP server를 실행한 후에, client로서 browser나 `urllib.request.urlopen` 함수를 사용할 수 있다.
# ### Browser에서
# Chrome browser에서 '개발자 도구'를 띄우고 다음과 같이 url을 입력하자.
# ```http://localhost:8080/test/index.html
# ```
# 
#  Browser는 base html file을 `GET`한 후, 이를 parsing하고, 연속해서 image object들을 fetch하기 위해 `GET` request message를 자동적으로  생성하여 송신한다. 여러분은 server에서 읽은 request message를 print해서 확인할 수 있을 것이다. 이때, `Connection` header는 keep-alive (Persistent connection mode)임을 확인 할 수 있다.
#  
# ### urllib module 활용
# ```Python
# from urllib.request import urlopen
# 
# f = urlopen(url)
# content = f.read()
# ```
# 
# 위 방법은 request header는 `Connection: close`로 설정하여 non-persistent mode로 연결 요청하는 방식이다. 이후 각각의 image들에 대해 같은 방법으로 fetch해 오는 code를 작성해야 한다.
```

## Output

### index.html
![output](index_html.PNG)
![output](network.PNG)
![output](header.PNG)

### 404 page
![output](test.PNG)
![output](test_.PNG)
![output](404.PNG)