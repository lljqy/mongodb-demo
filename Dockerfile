# DockerFile没有自测，可能需要改动
# 使用官方的 CentOS 7 基础镜像
FROM centos:7

# 设置工作目录
WORKDIR /app

# 安装依赖包
RUN yum install -y epel-release && \
    yum install -y python-pip && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# 安装 Python 3.9.13
RUN python-pip install --upgrade python==3.9.13

# 安装 MongoDB 7.0.2
RUN yum install -y mongodb-community-release-ta35-1.noarch-py3913
RUN yum install -y mongodb-org
RUN systemctl start mongod

# 将项目源码复制到工作目录
COPY . /app

# 暴露容器端口
EXPOSE 27017

# 设置环境变量
ENV MONGO_URI=mongodb://127.0.0.1:27017/myapp

# 运行命令
CMD ["python3", "manage.py"]
