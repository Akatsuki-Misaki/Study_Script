# 伪静态需求

```Apache
RewriteEngine on
RewriteBase /
RewriteCond $1 ^(index\.php)?$ [OR]
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d [OR]
RewriteCond %{REQUEST_FILENAME}  ^index\.php?$
RewriteRule ^(.*)$ - [S=1]
RewriteRule . /index.php [L]

```

```nginx
location / {
        try_files $uri $uri/ /index.php?$query_string;
}
```