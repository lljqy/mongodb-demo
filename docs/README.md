一. 环境
  1.1 环境要求： python3.9.13, mongodb7.0.2, windows10或者CentOS7.x操作系统
  1.2 安装python依赖包： pip install -r requirements.txt
  1.3 cd works/src && python manage.py 运行项目开启接口服务

二. 数据文档
  2.1 数据库采用单文档模式；
  数据模型如下：
class Products(Document):
    product_id = IntField(required=True)
    name = StringField(default='')
    description = StringField(default='')
    price = FloatField(default=0.0)
    category_id = IntField()
    add_time = DateTimeField(default=datetime.now())
   
class Categories(Document):
    category_id = IntField(required=True)
    category_name = StringField(default='')
    add_time = DateTimeField(default=datetime.now())
  2.2 商品表和类别表分开保存，主要是为了适应两表的数据灵活变更，同时categories表数据量比较小，分开存储没有数据冗余。

三. 数据清洗
  ETL的过程严格按照extract -> transform -> load的顺序执行
  源码在src/etl/data_processor.py中
  分离出公共抽象类 Processor用于定于抽象方法和公共方法
  细节1： 读取（extract）源文件时由于csv文件没有文件行数限制，可能会出现超大的csv文件，所有我们采取分块读取进行清洗，保证服务器资源不被大量占用
  细节2： 转换（transform）过程中封装了公共方法能够自动转换float, int, string常见类型，后面出现其它类型的数据可以在DFCleaner类中进行添加扩展
  细节3： 入库的时间数据库可能存在读写压力过大的情况，所以基于python装饰器我们入库做了3次尝试（后面这个入库的动作可以改成发送消息给消息组件，
         通过消费消息组件的消息来进行入库，实现数据不丢失） 
  架构优势：后面如果还有其它的业务表需要创建，只需要继承Processor类, 实现里面的接口即可，无须改动历史代码
  etl_scheduler.py中，所有继承Processor的子类统一在里面调度，利用多态的的思想来运行调用任务
  运行：cd works/src && python scheduler.py能够将data目录中的数据入库到mongodb

四. 接口设计
   1. 这个功能单一我们采用成熟且轻量级的Web框架Flask + flask_graphql + mongoengine + pymongo + jwt开源库来构建我们的服务，
   其中生成token的过程由jwt库来生成（根据用户的id和有效时间来判断用户访问权限）
   2. 2.2中提到两张表分开保存，两张表关联查询时会有性能问题， 我们给Categories建立复合索引（category_name， category_id），
      Products建立category_id单键索引，常用字段price和name建立单键索引（后面如果数据量的激增，可以考虑将搭建MongDB集群，做分片键将数据分片到多节点
      去查询）；
   3. 为了服务器稳定，应对高并发场景，单次数据接口的返回结果数限制450条以内
   4. demo.py文件里面给出了接口调用示例，需要在header请求头中传入sign: token键值对来给后端进行身份认证，同时用户需要
      根据需求修改query_string（GraphQL语句）变量，来查询商品数据

附录：
   注意事项：DockerFile没有自测，可能需要改动，