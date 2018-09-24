from flask import request, redirect, render_template, session, flash, url_for
import datetime
from models import User, Blog,db
from app import app
from libs.hashutils import make_pw_hash,check_pw_hash


@app.before_request
def require_login():
    if 'bootstrap' not in session:
        session['bootstrap'] = False
    print(request.endpoint)
    allowed_routes = ['login','register','bootstrap']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    
    page = request.args.get('page', 1, type=int)
    session['back'] = "/index?page="+str(page)
    blogs = Blog.get_paged(None,page)
    next_url = url_for('index',page=blogs.next_num) \
        if blogs.has_next else None
    prev_url = url_for('index',page=blogs.prev_num) \
        if blogs.has_prev else None
    print(blogs)
    if not blogs.has_prev and not blogs.has_next:
        page = None
        
    return render_template('index.html',title="Blogz",blogs=blogs.items,next_url=next_url,prev_url=prev_url,page=page)

@app.route('/new_post', methods=['POST','GET'])
def new_post():
    back = session['back']
    session['back'] = request.endpoint
    title = ""
    body = ""
    id = ""
    editing = False
    current_user = User.get_user(session['email'])
    if request.method == 'GET':
        try:
            id = request.args.get('id')
        except:
            pass
        if id:
            blog = Blog.get(None,id)
            title = blog.title
            body = blog.body
            id = blog.id
            editing = True

    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        try:
            editing = request.form['editing']
        except:
            pass
        if editing:
            id = request.form['id']
        
        
        if current_user and title and body:
            if not editing:
                blog = Blog(title,body,current_user,datetime.date.today().strftime('%b %d, %Y'))
            else:
                if id:
                    blog = Blog.get(None,id)
                    blog.title = title
                    blog.body = body
            Blog.add(blog)
            return redirect("/blog?blog-id="+str(blog.id))
        else:
            flash("Please fill out all fields","Error")

    return render_template("new_post.html",title=title,body=body,editing=editing,id=id,back=back)
@app.route("/blog", methods=['POST','GET'])
def title_route():
    
    #Open a page with the selected blog post displayed
    try:
        id = request.args.get('blog-id')
        session['back'] = 'blog?blog-id='+id
    except:
        return render_template("error.html")
    
    blog = Blog.get(None,id)
    user = User.get_user(None,blog.owner_id)

    return render_template("blog.html",blog=blog,user=user)

@app.route("/user", methods=['POST','GET'])
def user_blogs():
    user = User.get_user(None,request.args.get('id',session['id']))
    page = request.args.get('page', 1, type=int)
    session['back'] = 'user?id='+str(user.id)+"&page="+str(page)
    blogs = Blog.get_paged(user,page)
    next_url = url_for('user_blogs',id=request.args.get('id','1'),page=blogs.next_num) \
        if blogs.has_next else None
    prev_url = url_for('user_blogs',id=request.args.get('id','1'),page=blogs.prev_num) \
        if blogs.has_prev else None

    if not blogs.has_prev and not blogs.has_next:
        page = None

    return render_template("user.html",user=user,blogs=blogs.items,next_url=next_url,prev_url=prev_url,page=page)

@app.route("/users", methods=['POST','GET'])
def users():
    session['back'] = request.endpoint
    blogs = Blog.get_owners()
    users = []
    for blog in blogs:
        users.append(User.get_user(None,blog.owner_id))
        print(str(users[0].email))
    
    return render_template("users.html",users=users)

@app.route("/register", methods=['POST','GET'])
def register():
    session['back'] = "register"
    email = ""
    error = False
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not "@" in email or not "." in email:
            flash("Invalid Username","Error")
            return redirect("/register")
        if not password:
            flash('Must enter a password','Error')
            error = True
        if not password == verify:
            flash("Passwords do not match","Error")
            error = True

        existing_user = User.get_user(email)
        
        if not existing_user and not error:
            password = make_pw_hash(password)
            new_user = User(email,password)
            User.add(new_user)
            session['id'] = new_user.id
            session['email'] = email
            return redirect('/')
        elif existing_user:
            flash("User already exists","Error")
            
    return render_template("register.html",email=email)

@app.route('/logout')
def logout():
    del session['email']
    del session['id']
    return redirect('/')

@app.route('/login', methods=['POST','GET'])
def login():
    email=''
    session['back'] = request.endpoint
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if not email or '@' not in email or '.' not in email:
            flash('Invalid email','Error')
            return redirect('/login')
        if not password:
            flash('Invalid Password','Error')
            return render_template("login.html",email=email)
        user = User.get_user(email)
        if user and check_pw_hash(password,user.password):
            session['email'] = email
            session['id'] = user.id
            return redirect("/")
        else:
            flash("Password incorrect or User doesn't exist",'Error')

    return render_template("login.html",email=email)

@app.route('/bootstrap', methods=['POST','GET'])
def bootstrap():
    try:
        if session['bootstrap']:
            session['bootstrap'] = False
        else:
            session['bootstrap'] = True
    except:
        session['bootstrap'] = False
    print(session['back'])
    return redirect(session['back'])

if __name__ == '__main__':
    app.run()