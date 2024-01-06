import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask,render_template,request,redirect,url_for
from cloudant.client import Cloudant

app=Flask(__name__)
client = Cloudant.iam("3f24adf1-9d5a-4f71-a351-620941bec846-bluemix", "hR0_2YUDAjlwMRj97IukFm3WheYNpBsK_U_5GF1aQiS-", connect=True)
my_database = client['my_database']

model=load_model("updated-xception-diabetic-retinopathy.h5")
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/predict')
def predict():
    return render_template('prediction.html')

@app.route('/afterlogin',methods=['POST'])
def afterlogin():
    user=request.form['usr']
    passw=request.form['psw']
    print(user,passw)
    query={'name':{'$eq':user}}
    docs=my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if(len(docs.all())==0):
        return render_template('login.html',pred='Username not found')
    else:
        if((user==docs[0][0]['name'] and passw==docs[0][0]['pwd'])):
            return redirect(url_for('predict'))
        else:
            print ('Invalid user')
        #return render_template('register.html',pred='You are already a member please login using your details')


@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/afterreg',methods=['POST'])
def afterreg():
    x=[x for x in request.form.values()]
    print(x)
    data={
        '_id':x[1],
        'name':x[0],
        'pwd':x[2]
    }
    print(data)
    query={'_id':{'$eq':data['_id']}}
    
    docs=my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if(len(docs.all())==0):
        url=my_database.create_document(data)
        return render_template('register.html',pred='Registration successful please login using your details')
    else:
        return render_template('register.html',pred='You are already a member please login using your details')
    
@app.route('/predict',methods=['GET','POST'])
def upload():
    if request.method=='POST':
        f=request.files['image']
        basepath=os.path.dirname(__file__)
        filepath=os.path.join(basepath,'diabetes',f.filename)
        f.save(filepath)
        img=image.load_img(filepath,target_size=(299,299))
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)
        pred=np.argmax(model.predict(x),axis=1)
        index=['0','1','2','3','4']
        text="The Classified types : " +str(index[pred[0]])
    return text

if __name__=='__main__':
    app.run()