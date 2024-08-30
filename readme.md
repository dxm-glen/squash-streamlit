pip install -r requirements.txt

pip install --upgrade numpy pandas


sudo yum install nginx

sudo systemctl start nginx

sudo systemctl enable nginx

```shell
$ wget http://www.cs.toronto.edu/~soheil/csc309/nginx.tar.gz && tar -xvzf nginx.tar.gz
```

/etc/nginx/nginx.conf 파일을 niginx.conf로 교체

sudo cp nginx.conf /etc/nginx/nginx.conf

sudo service nginx restart
