#-*-coding:utf-8-*-
from flask import Flask, render_template, request, url_for

## Flask 객체를 app에 할당
app = Flask(__name__, static_url_path='/static')

## GET 방식으로 값을 전달받음. 
## 아무 값도 넘겨받지 않는 경우도 있으므로 비어 있는 url도 함께 mapping해주는 것이 필요함
## app 객체를 이용해 라우팅 경로를 설정

@app.route('/')
def home(result=None):
  return render_template('home.html')


@app.route('/result', methods=['POST', 'GET'])
def result():
    ## 어떤 http method를 이용해서 전달받았는지를 아는 것이 필요함
    ## 아래에서 보는 바와 같이 어떤 방식으로 넘어왔느냐에 따라서 읽어들이는 방식이 달라짐
    if request.method == 'POST':
        #temp1 = request.form['ip']
        #temp2 = request.form['port']
        #return render_template('home.html', ip=temp1, port=temp2)

        #result = request.form
        #return render_template("result.html",result = result)
        pass
    elif request.method == 'GET': 
        temp1 = request.args.get('ip')
        temp2 = request.args.get('port')
        temp3 = request.args.get('field')
        temp4 = request.args.get('timefield')
        temp5 = request.args.get('idfield')
        temp6 = request.args.get('metric')

        # import subprocess
        # subprocess.call('python FILE2TSDB.py '+temp3+' '+temp4+' "none" '+temp5+' 1 '+' 1 '+temp1+' '+temp2, shell=True)

        import os
        os.system('nohup python FILE2TSDB.py '+temp1+' '+temp2+' \"'+temp3+'\" \"'+temp4+'\" \"'+temp5+'\" '+temp6+' &')

        result = 'OK'

        ## 넘겨받은 값을 원래 페이지로 리다이렉트
        return render_template('result.html', result=result)
    ## else 로 하지 않은 것은 POST, GET 이외에 다른 method로 넘어왔을 때를 구분하기 위함

## localhost:5000/txt 로 접근하면 다음 부분이 수행됨 
@app.route('/log')
def read_txt():
    f = open('./static/run_log.log', 'r')
    ## 단 리턴되는 값이 list형태의 타입일 경우 문제가 발생할 수 있음.
    ## 또한 \n이 아니라 </br>으로 처리해야 이해함
    ## 즉 파일을 읽더라도 이 파일을 담을 html template를 만들어두고, render_template 를 사용하는 것이 더 좋음
    return "</br>".join(f.readlines())

if __name__ == '__main__':
    # threaded=True 로 넘기면 multiple plot이 가능해짐
    app.run(host='0.0.0.0', port=5003, debug=True, threaded=True)
