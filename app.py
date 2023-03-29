from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///finance.db"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

app.config['SQLALCHEMY_BINDS'] = {
    'second': 'sqlite:///second.db'
}

db=SQLAlchemy(app)

class data(db.Model):
    SNO= db.Column(db.Integer, primary_key=True)
    Amount=db.Column(db.Integer, nullable=False)
    Expense=db.Column(db.String(100), nullable=False)
    Date=db.Column(db.Date, default=(datetime.now()).date())

    def __repr__(self) -> str:
        return f'{self.Amount} :- {self.Expense}'

class Money(db.Model):
    __bind_key__ = 'second'
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, default=0)
    balance = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f'{self.total} :- {self.balance}'
    

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        amount=request.form['Amount']
        reason=request.form['Expense']
        temp = data(Amount=int(amount), Expense=reason)
        db.session.add(temp)
        db.session.commit()
        money = Money.query.first()
        money.balance=money.balance-int(amount)
        db.session.commit()

    content=data.query.all()
    wallet =Money.query.all()
    if len(wallet)==0:
        temp=Money()
        db.session.add(temp)
        db.session.commit()

    print(wallet)
    return render_template('index.html', content=content, balance=wallet)

@app.route('/delete/<int:sno>')
def delete(sno):
    content = data.query.filter_by(SNO=sno).first()
    db.session.delete(content)
    db.session.commit()
    prevamt = content.Amount
    money=Money.query.first()
    money.balance = money.balance + prevamt
    db.session.commit()


    return redirect('/')

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        amount=request.form['Amount']
        reason=request.form['Expense']
        content = data.query.filter_by(SNO=sno).first()
        prevamt = content.Amount

        if(prevamt!=amount):
            diff=int(prevamt)-int(amount)
            money=Money.query.first()
            money.balance = money.balance + diff
            db.session.commit()

        content.Amount=amount
        content.Expense=reason
        db.session.add(content)
        db.session.commit()
        return redirect('/')

    content = data.query.filter_by(SNO=sno).first()
    return render_template('update.html', content=content)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method=='POST':
        dep=request.form['Amount']
        money=Money.query.first()
        money.balance = money.balance + int(dep)
        money.total = money.total + int(dep)
        db.session.commit()
        return redirect('/')
    
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method=='POST':
        dep=request.form['Amount']
        money=Money.query.first()
        money.balance = money.balance - int(dep)
        money.total = money.total - int(dep)
        db.session.commit()
        return redirect('/')
    
    return render_template('withdraw.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    content_=data.query.all()
    for i in content_:
            content = data.query.filter_by(SNO = i.SNO).first()
            db.session.delete(content)
            db.session.commit()

    money= Money.query.first()
    money.balance=0
    money.total=0
    db.session.commit()
    return redirect('/')

@app.route('/home')
def home():
    return redirect('/')

@app.route('/about')
def about():
    return render_template('aboutme.html')

@app.route('/stories')
def stories():
    return render_template('stories.html')

if __name__ == '__main__':
    app.run(debug=True)