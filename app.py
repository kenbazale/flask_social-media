from flask import Flask,g,render_template,redirect,url_for,flash
from flask_login import  LoginManager,login_user,logout_user,login_required,current_user
from flask_bcrypt import check_password_hash

from form import RegisterForm,LoginForm,PostForm
import form
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.config['SECRET_KEY']='SDFSDFSJDFSD.DFDFDF'

loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = 'login'


@loginmanager.user_loader
def load_user(userid):
    try :
       return  models.User.get(models.User.id == userid)
    
    except models.DoesNotExist:
        return None



@app.before_request
def before_request():
    """ connect to DB b4 each requist"""
    g.db = models.DATABASE
    g.db.connect()
    g.user=current_user


@app.after_request
def after_request(response):
    """ close db after each request"""
    g.db.close()
    return response



@app.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash('registered','success')
        models.User.create_user(username=form.username.data,email=form.email.data,password=form.password.data)
        return redirect(url_for('login'))
    
    return render_template('register.html',form=form)



@app.route('/login',methods= ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try :
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash ('wrong email or password ','error')
        else:
            if check_password_hash(user.password,form.password.data):
                login_user(user)                
                flash('login','success')
                return redirect(url_for('index'))
            else :
                flash ('wrong email or password ','error')
    return render_template ('login.html',form=form)   


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out','success')
    return redirect(url_for('index'))


@app.route('/post',methods=['GET','POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),content = form.content.data.strip())
        flash('post created!','success')
        return redirect(url_for('index'))
    return render_template('post.html',form=form)





@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html',stream=stream)

@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        user = models.User.select().where(models.User.username**username).get()
        stream = user.posts.limit(100)
    else :
        stream = current_user.get_stream().limit(100)
        user =current_user
    if username:
        template = 'user_stream.html'
    return render_template(template,stream=stream,user=user)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
       to_user = models.User.get(models.User.username ** username)
    except models.DoesNotExist:
        pass
    else:
        try:
          models.Relationship.create(from_user=g.user._get_current_object(),to_user=to_user)
        except models.IntegrityError:
            pass
        else:
            flash('you are now following {}'.format(to_user.username,'success'))
    return redirect(url_for('stream',username=to_user.username))



@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
       to_username = models.User.get(models.User.username ** username)
    except models.DoesNotExist:
        pass
    else :
        try:
          models.Relationship.get(from_user=g.user._get_current_object(),to_user=to_user).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash('you  unfollowing {}'.format(to_user.username,'success'))
    return redirect(url_for('stream',username=to_user.username))


@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = models.Post.select().where(models.Post.id==post_id )
    return render_template('stream.html',stream=post)


if __name__ == "__main__":
    models.initialize()
    try:
        models.User.create_user(username = 'kenbazale',email = 'kenbazale@live.com',password='password',admin=True)
    except ValueError:
        pass

    app.run(debug=DEBUG,host=HOST,port=PORT)
    
    