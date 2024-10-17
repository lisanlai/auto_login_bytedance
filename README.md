# 脚本说明
> 支持字节各种乱七八糟系统的滑块验证，可实现自动登录

## 1. 安装依赖
``` 
pip install DrissionPage 
pip install opencv-python
```
## 2. 可能需要修改的配置 config.ini
```
[page]
# 百应团长登录页面
role_select_page = https://buyin.jinritemai.com/mpa/account/institution-role-select

[login]
# 要登录的团长名称
target_account = *
# 团长账号和密码
username = *
password = *
```

## 3. 运行demo
```python auto_login_demo.py```

## 4. 注意事项
> - 脚本默认是用登录抖音团长作为示例的，如果你要登录其他系统，你需要更换登录页面配置
> - 脚本默认的浏览器配置，可根据自己需要修改，例如headless模式等等 
> - 脚本在做滑块验证的时候，需要下载验证码图片到本地，建议放图片的磁盘空间给大一点，或者定期清理，不建议清理掉，会影响登录速度