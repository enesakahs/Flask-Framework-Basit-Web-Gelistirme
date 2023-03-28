from flask import Flask
from flask import render_template
from flask import flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt 
from functools import wraps

#KULLANICI GİRİS DECORATOR (Cıkıs yapan kullanıcı URL adresi girip gitmek istedigi sayfaya erisim engeli icin)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu Sayfayı Görüntülemek İcin Giris Yapınız.","danger")
            return redirect(url_for("login"))
    return decorated_function


#Kayıt Formu
class RegisterForm(Form):
    name=StringField("İsim Soyisim: ",validators=[validators.Length(min=4,max=25)])
    username=StringField("Kullanıcı Adı: ",validators=[validators.Length(min=5,max=25)])
    email=StringField("Email Adresi: ",validators=[validators.Email("Lütfen Gecerli Email Adresi Giriniz..")])
    password=PasswordField("Parola: ",validators=[
        validators.data_required("Lütfen Paralo Belirleyiniz.."),
        validators.EqualTo(fieldname="confirm",message=("Parolanız Uyusmuyor"))
    ])
    confirm=PasswordField("Parola Dogrula")
    
#Giris Formu
class LoginForm(Form):
    username=StringField("Kullanıcı Adı: ")
    password=PasswordField("Sifrenizi Giriniz: ")

app=Flask(__name__) # Flask uygulamasını oluşturur. "name" argümanı, uygulamanın adını belirler ve aynı zamanda uygulamanın nerede çalıştığını belirlemek için kullanılır.
app.secret_key="ybblog"

mysql=MySQL(app) #flask ile mysql arası iliski tanımlandı

# MySQL veritabanı bağlantı yapılandırması:
app.config["MYSQL_HOST"]="localhost" # veritabanının konumu
app.config["MYSQL_USER"]="root"      # veritabanına bağlanmak için kullanılacak kullanıcı adı
app.config["MYSQL_PASSWORD"]=""      # veritabanına bağlanmak için kullanılacak şifre
app.config["MYSQL_DB"]="ybblog"      # MySQL veritabanının adı
app.config["MYSQL_CURSORCLASS"]="DictCursor" # bir sözlük olarak her satırı döndüren bir imleç sınıfı



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

#MAKALE SAYFASI
@app.route("/articles")
def articles():
    cursor=mysql.connection.cursor()

    #tüm makaleleri görmek icin
    sorgu="SELECT * FROM articles"

    result=cursor.execute(sorgu)

    #db de veri var result > 0
    if result > 0 :
        articles=cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")


#KONTROL PANELİ
@app.route("/dashboard")
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM articles WHERE author=%s"
    result=cursor.execute(sorgu,(session["username"],))

    if result>0:
        articles=cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:
        return render_template("dashboard.html")


#KAYIT OL
@app.route("/register",methods=["GET","POST"])
def register():
    form=RegisterForm(request.form)

    if request.method=="POST" and form.validate():
        name=form.name.data
        username=form.username.data
        email=form.email.data
        password=sha256_crypt.encrypt(form.password.data)

        cursor=mysql.connection.cursor()
        sorgu="INSERT INTO users(name,email,username,password) VALUES (%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("KAYIT İSLEMİ BASARILI","success")
        return redirect(url_for("login"))
    else: 
        return render_template("register.html", form=form)


#GİRİS YAP 
@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        username=form.username.data
        password_entered=form.password.data

        cursor=mysql.connection.cursor()

        sorgu="SELECT * FROM users WHERE username=%s"

        result=cursor.execute(sorgu,(username,))
        if result>0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("GİRİS BASARILI","success")

                session["logged_in"]=True
                session["username"]=username


                return redirect(url_for("index"))
            else:
                flash("PAROLANIZI KONTROL EDİNİZ","danger")
                return redirect(url_for("login"))

        else:
            flash("KULLANICI BULUNAMADI..","danger")
            return redirect(url_for("login"))
        

    return render_template("login.html",form=form)


#CIKIS YAP
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


#DETAY SAYFASI
@app.route("/article/<string:id>")
def article(id):
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM articles WHERE id=%s"
    result=cursor.execute(sorgu,(id,))

    if result>0:
        article=cursor.fetchone()
        return render_template("article.html",article=article)
    else:
        return render_template("article.html")


#MAKALE EKLE
@app.route("/addarticle",methods = ["GET","POST"])
def addarticle():
    #addarticle urlsine giris yapmadan yönlenmek isteyen kullanıcıyı giris ekranına yönlendiriyor
    if "username" not in session:
        flash("Lütfen giriş yapın","danger")
        return redirect(url_for("login"))
    
    form=ArticleForm(request.form)
    if request.method=="POST" and form.validate():
        title=form.title.data
        content=form.content.data

        cursor=mysql.connection.cursor()
        sorgu="INSERT INTO articles(title,author,content) VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username"],content))

        mysql.connection.commit()
        cursor.close()

        flash("MAKALE BASARIYLA EKLENDİ","success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html",form=form)


#MAKALE OLUSTUR 
class ArticleForm(Form):
    title=StringField("Makale Baslıgı",validators=[validators.length(min=5,max=100)])
    content=TextAreaField("Makale İceriği",validators=[validators.length(min=10)])


#MAKALE SİL
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM articles WHERE author=%s and id=%s"
    result=cursor.execute(sorgu,(session["username"],id))

    if result>0:
       sorgu_2="DELETE FROM articles WHERE id=%s"
       cursor.execute(sorgu_2,(id,))
       mysql.connection.commit()
       return redirect(url_for("dashboard"))
    else:
        flash("Böyle Bir Makale Bulunamadı / Bu İsleme Yetkili Degilsiniz","danger")
        return redirect(url_for("index"))


#MAKALE GÜNCELLEME
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
   if request.method == "GET":
       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where id = %s and author = %s"
       result = cursor.execute(sorgu,(id,session["username"]))

       if result == 0:
           flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
           return redirect(url_for("index"))
       else:
           article = cursor.fetchone()
           form = ArticleForm()

           form.title.data = article["title"]
           form.content.data = article["content"]
           return render_template("update.html",form = form)

   else:
       # POST REQUEST
       form = ArticleForm(request.form)

       newTitle = form.title.data
       newContent = form.content.data

       sorgu2 = "Update articles Set title = %s,content = %s where id = %s "

       cursor = mysql.connection.cursor()

       cursor.execute(sorgu2,(newTitle,newContent,id))

       mysql.connection.commit()

       flash("Makale başarıyla güncellendi","success")

       return redirect(url_for("dashboard"))

       pass
   

#ARAMA
@app.route("/search",methods = ["GET","POST"])
def search():
   if request.method == "GET":
       return redirect(url_for("index"))
   else:
       keyword = request.form.get("keyword")

       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where title like '%" + keyword +"%'"

       result = cursor.execute(sorgu)

       if result == 0:
           flash("Aranan kelimeye uygun makale bulunamadı...","warning")
           return redirect(url_for("articles"))
       else:
           articles = cursor.fetchall()

           return render_template("articles.html",articles = articles)


if __name__=="__main__":
    app.run(debug=True) # Uygulamayı çalıştırır ve debug modunu etkinleştirir.
