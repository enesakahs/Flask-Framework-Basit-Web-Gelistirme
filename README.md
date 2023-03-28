# Flask-Framework-Basit-Web-Gelistirme

Kod, kayıt, giriş ve gösterge paneli işlevlerini sağlayan bir Flask web uygulamasıdır. Veritabanı olarak MySQL kullanılmakta ve veritabanı ile iletişim kurmak için flask_mysqldb kullanılmaktadır. Uygulamanın  yönlendirmeleri asağıdaki gibidir:

/: ana sayfa.
/about: hakkımızda sayfasını gösterir.
/articles: tüm makaleleri gösterir.
/dashboard: kullanıcı oturum açtıysa kullanıcının gösterge panelini gösterir.
/register: kullanıcının kaydolmasına izin verir.
/login: kullanıcının giriş yapmasına izin verir.
Uygulamanın iki formu vardır: KayıtFormu ve GirişFormu, sırasıyla kayıt ve giriş için kullanılır. 
KayıtFormu şu alanlara sahiptir: ad, kullanıcı adı, e-posta, şifre ve şifreyi onayla. 
GirişFormu şu alanlara sahiptir: kullanıcı adı ve şifre.

/login_required dekoratörü, /dashboard route yönlendirmesine erişimi kısıtlamak için kullanılır. Sadece oturum açmış kullanıcılar bu yönlendirmeye erişebilirler. Kullanıcı oturum açmadıysa ve bu yönlendirmeye erişmeye çalışırsa, giriş sayfasına yönlendirilir.
