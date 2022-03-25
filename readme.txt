1. 不同bot的资源文件分别放到bot_resources下的不同目录下。
2. bot_name参数值即为bot_resources下的某一目录名。
3. 更新intents.txt、priority.txt资源文件后，手动刷新后立即生效（refresh接口）。
4. 支持"Hello, I am Adam. How can I change password"。
5. 支持拼写纠错。
6. 支持频率优先级。
7. 支持most recently优先级。
8. 支持自定义常驻前置suggestion。
9. 支持全局匹配（全文检索实现，数据量大时使用异步）。
10. 支持拼音
11. 支持拼音纠错
12. 支持中文分词自定义词典


注：高并发时，采用gunicorn服务启动及部署方式，本web_service不支持高并发。
gunicorn -w 4 -k gevent -b 0.0.0.0:8088 --threads 100 --worker-connections 10000 web_service:app
gunicorn -b 0.0.0.0:8088 --threads 100 --worker-connections 10000 web_service:app


Redis安装：
https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/