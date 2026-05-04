---
title: FTP文件传输协议
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [FTP, 文件传输, 控制连接, 数据连接, 主动模式, 被动模式, TFTP]
aliases: [File Transfer Protocol, FTP Active Mode, FTP Passive Mode, PORT, PASV]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 959
updated_at: 2026-05-02

---

## 核心定义

FTP（File Transfer Protocol，文件传输协议）是TCP/IP协议栈中用于在客户端和服务器之间进行文件传输的标准应用层协议。FTP的独特之处在于它使用"带外控制"架构：以两个独立的TCP连接来完成文件传输任务——控制连接（Control Connection，端口21）用于传输FTP命令和服务器的响应（命令通道），数据连接（Data Connection，端口20（主动模式）或随机端口）用于实际的文件和目录列表传输（数据通道）。这种"控制与数据分离"的设计使得在文件传输的同时仍能通过控制连接发送命令（如中断传输）。FTP支持两种工作模式——主动模式（Active/PORT）和被动模式（Passive/PASV），以适应不同的防火墙和NAT环境。FTP提供丰富的目录操作命令（LIST/RETR/STOR/DELE/RENAME/MKD/RMD等）、传输模式设置和用户认证功能。匿名FTP曾是互联网文件共享的重要方式。SFTP（SSH File Transfer Protocol，基于SSH协议）和FTPS（FTP over SSL/TLS）分别从不同角度解决了FTP明文传输的安全问题。

## 关键结论

- FTP的双连接架构：控制连接（TCP 21）用于发送FTP命令和接收应答（命令-应答模式），在整个FTP会话期间始终保持连接。数据连接是根据需要动态创建和释放的，专门用于文件数据、目录列表的传输。这种设计允许在长文件传输中同时执行中断命令
- FTP主动模式（PORT模式）：客户端通过控制连接发出PORT命令告诉服务器自己在哪个IP:端口上监听；服务器从自身的端口20主动连接客户端的指定端口建立数据连接。问题：如果客户端在NAT/防火墙后面，服务器主动发起的连接可能被阻止
- FTP被动模式（PASV模式）：客户端发出PASV命令请求被动模式，服务器回复一个IP:端口（如227 Entering Passive Mode (h1,h2,h3,h4,p1,p2)即IP=h1.h2.h3.h4, Port=p1*256+p2）；客户端主动连接服务器的该端口建立数据连接。PASV模式解决了NAT/防火墙问题
- FTP传输模式：ASCII模式（传输文本文件时自动转换换行符——Windows的CRLF与Unix的LF的转换）、二进制模式（Binary/Image，原样传输任意二进制文件）。如果二进制文件用ASCII模式传输会损坏文件（如行结束符被错误转换）。FTP默认ASCII模式是个历史遗留的坑
- FTP安全性：FTP协议设计中安全性极度缺乏——所有数据（包括用户名和密码）明文传输，PORT命令可以被滥用做端口扫描攻击（FTP Bounce Attack）。FTPS（FTP over TLS）和SFTP（基于SSH的完全独立协议）是更安全的选择

## 易错点

1. **FTP是双连接不是双通道**：虽然有一说"双通道协议"，但准确地说是两个独立的TCP连接（而不是一个物理通道上的不同逻辑通道）。数据连接的端口号必须在传输前动态协商，不同于固定端口通信的常规服务器模型。

2. **主动模式与被动模式的端口方向**：主动模式数据连接是服务器→客户端（服务器20→客户端随机端口），防火墙或NAT后的客户端会接收不到；被动模式数据连接是客户端→服务器（客户端随机端口→服务器随机端口），对NAT友好的多。PASV模式下服务器的数据端口范围需要预先在防火墙开放，否则依然会连接失败。

3. **SFTP不等于FTPS**：SFTP是基于SSH协议的文件传输，端口22，全程加密；FTPS是在FTP上添加TLS/SSL层（类似于HTTPS之于HTTP），仍使用双连接结构。两者底层完全不同，不兼容。许多人错误地将安全FTP统称为SFTP。

4. **FTP的匿名访问不等于开放**：匿名FTP用户通常被限制只能访问特定目录（chroot/文件系统沙箱），不能浏览服务器的全局文件系统。Anonymous登录名通常为"anonymous"或"ftp"，密码为空或任意字符串。现代已经很罕见。

## 例题

**例题1**：客户端（FTP Client）位于NAT后面，服务器（FTP Server）有公网IP。选择哪种FTP模式可以实现文件传输？说明理由。

**解答**：必须使用被动模式（PASV）。原因：主动模式下服务器需要主动连接NAT后面的客户端数据端口，NAT会因为没有对应的转换表项而阻止服务器的SYN包。被动模式下客户端主动连接服务器（客户端→服务器），防火墙上客户端的出站连接通常被允许（有状态过滤自动生成回程规则），因此数据连接成功建立。这也是现代FTP客户端（浏览器、FTP下载工具）基本默认PASV模式的原因。

**例题2**：FTP服务器上有一个README.md文件，内容包含若干行，其中每行以CRLF（\r\n，Windows格式）结尾。客户端（Unix/Linux系统）以ASCII模式下载该文件，最终文件中的换行符是什么？

**解答**：FTP ASCII传输模式下，发送方将本地系统的换行符转换为标准的CRLF（\r\n）在网络中传输。服务器在发送时将文件中的CRLF转为标准CRLF发送，接收方（Unix客户端）收到CRLF后将其转换为本机换行符——即LF（\n）。所以最终下载到Linux系统的文件中每行的换行符是\n（Unix格式）。如果以二进制模式下载，换行符保持不变（仍是\r\n）。

## 代码示例

```python
from ftplib import FTP

# Python FTP客户端示例
ftp = FTP('ftp.example.com')
ftp.login(user='username', passwd='password')

# 列出目录
ftp.retrlines('LIST')
files = ftp.nlst()
print(f"文件列表: {files}")

# 下载文件
with open('downloaded_file.txt', 'wb') as f:
    ftp.retrbinary('RETR remote_file.txt', f.write)

# 上传文件
with open('local_file.txt', 'rb') as f:
    ftp.storbinary('STOR remote_file.txt', f)

# 切换目录
ftp.cwd('/subdir')

# 获取当前目录
print(f"当前目录: {ftp.pwd()}")

ftp.quit()
```

```bash
# Linux命令行FTP客户端
ftp ftp.example.com
# 交互命令：
# ls / dir     - 列出文件
# cd <dir>     - 切换目录
# get <file>   - 下载文件
# put <file>   - 上传文件
# binary       - 切换为二进制模式
# ascii        - 切换为ASCII模式
# passive      - 切换被动模式
# quit         - 退出
```

## 关联页面

[[应用层-SMTP-POP3-IMAP]] [[应用层-HTTP]] [[SSL-TLS]] [[TCP三次握手]]
