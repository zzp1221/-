---
title: 电子邮件协议SMTP-POP3-IMAP
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [SMTP, POP3, IMAP, 电子邮件, MIME, 邮件传输]
aliases: [Simple Mail Transfer Protocol, Post Office Protocol, Internet Message Access Protocol]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 5321 (SMTP), RFC 1939 (POP3), RFC 3501 (IMAP)
updated_at: 2026-05-02

---

## 核心定义

电子邮件系统由三个核心应用层协议组成，分别负责邮件发送、投递和接收的不同环节。SMTP（Simple Mail Transfer Protocol，简单邮件传输协议）负责从发送方的邮件客户端向发送方邮件服务器发送邮件，以及在邮件服务器之间中继转发邮件，使用TCP 25端口（明文）或587/465端口（加密提交）。POP3（Post Office Protocol version 3，邮局协议）负责将邮件从服务器下载到本地客户端，默认"拉取即删除"模式下邮件下载到本地后服务器会删除副本，使用TCP 110端口（明文）或995端口（SSL/TLS）。IMAP（Internet Message Access Protocol，互联网消息访问协议）也负责邮件接收，但设计为在线操作模式——邮件保留在服务器上，客户端只下载邮件的元数据（发件人、主题、大小等），按需下载邮件正文和附件，支持服务器端的文件夹管理、邮件标记和搜索。IMAP比POP3更适合多设备同步（手机+电脑+Webmail）。邮件的编码格式由MIME（Multipurpose Internet Mail Extensions）标准定义，支持在纯文本邮件中嵌入图片、附件、多语言字符集等多媒体内容。

## 关键结论

- 邮件系统的完整投递链路：发送方MUA（邮件用户代理，如Outlook/Thunderbird）→ SMTP → 发送方MTA（邮件传输代理，如发件人邮箱服务器）→ SMTP（服务器间中继）→ 接收方MTA→ MDA（邮件投递代理）→ 邮件存储 → POP3/IMAP → 接收方MUA
- SMTP只负责"推"——只能发送（push），不支持从服务器拉取（pull）邮件。POP3和IMAP负责"拉"。这三个协议分工明确，共同构成完整的邮件系统
- POP3的缺点和IMAP的优势：POP3默认下载后从服务器删除，邮件仅存在一台设备上，多设备场景下邮件状态不同步。IMAP将邮件保留在服务器——任何设备看到的都是同一份数据，支持搜索服务器端邮件、部分下载大附件和服务器端文件夹。IMAP需要持续网络连接（除离线缓存外），对服务器存储和带宽要求更高
- SMTP的命令-应答模式：EHLO/HELO（打招呼）、MAIL FROM（发件人）、RCPT TO（收件人，可多次指定多个收件人）、DATA（邮件正文，以只包含句点"."的行结束）、QUIT（结束会话）。SMTP使用7位ASCII，8位内容通过MIME编码为7位可打印格式传输
- MIME扩展了SMTP的功能，允许邮件携带：非ASCII文本（UTF-8等字符集，通过Content-Type中的charset声明）、多部分混合内容（multipart/mixed，如文本+图片+附件）、二进制附件（Base64编码为7位ASCII传输）和特定格式的文件（application/pdf等通过Content-Type声明）

## 易错点

1. **SMTP、POP3和IMAP使用不同的TCP端口**：SMTP标准端口25（服务器间和传统客户端提交）被众多ISP封锁以阻止垃圾邮件转发，因此RFC 6409定义了port 587作为邮件提交端口（要求认证）；IMAP标准端口143（明文）和993（IMAPS）；POP3端口110（明文）995（POP3S）。端口号易混淆。

2. **SMTP的"接力"传输链**：一封邮件从发件人到收件人可能经过多个MTA（发件方服务器→中继→接收方服务器），每个MTA在转发时会在邮件头添加Received字段。分析邮件头中的Received链可以追踪邮件的传输路径，这也是判断垃圾邮件来源的重要取证手段。

3. **POP3的"下载后删除"不是强制行为**：POP3客户端可以设置为"在服务器上保留副本"（如保留7天），但POP3本身不提供服务器端邮件状态同步——即便保留副本，如果在一个POP3客户端标记了某一封为已读，另一个客户端（或Webmail）上不知道这一状态变化。

4. **IMAP的离线模式不等于数据下载了**：很多IMAP客户端提供"离线缓存"或"完整下载"，但IMAP协议的核心设计是服务器为邮件主要存储。如果IMAP客户端配置了定期清理服务器邮件，那它就不再体现IMAP的传统优势——在这种配置下行为类似POP3。

## 例题

**例题1**：使用Webmail（网页邮件，如Gmail Web）不需要POP3或IMAP客户端。解释Webmail如何通过SMTP发送邮件，以及网页界面如何获取服务器上的邮件列表。

**解答**：Webmail系统是一个运行在服务器端的Web应用程序。用户通过浏览器填写邮件后，Web应用程序在服务器端调用SMTP库或SMTP服务（通常通过localhost:25）将邮件发送出去。获取邮件列表时，Web应用程序在服务器端通过文件系统/专用API直接访问邮件存储后端（而非通过POP3/IMAP），将邮件数据渲染为HTML后通过HTTP/HTTPS发给浏览器。整个过程中POP3和IMAP都不参与——它们仅用于桌面/移动邮件客户端通过互联网连接服务器。

**例题2**：POP3和IMAP的混合使用场景：用户在办公室电脑用Thunderbird（IMAP配置）和在家用Outlook（POP3配置，设置为保留副本7天）访问同一邮箱。分析在这种配置下用户可能遇到的数据一致性问题。

**解答思路**：IMAP客户端在服务器上管理文件夹、标记已读状态等；POP3客户端每次下载邮件副本（但保留原版在服务器7天）。问题：（1）POP3客户端读过的邮件在IMAP上仍显示未读（读状态不能跨协议同步）；（2）POP3客户端在本地删除了某邮件，但服务器上依然存在（POP3本地操作不影响服务器）；（3）POP3客户端设置的7天保留期满后服务器自动删除该邮件副本，但IMAP客户端可能仍需要这份邮件；（4）POP3客户端发送的邮件放在本地已发送文件夹，IMAP客户端上看不到。解决：统一使用IMAP协议。

## 代码示例

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP发送邮件示例
def send_email(smtp_server, port, username, password, to_addr, subject, body):
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()  # TLS加密
        server.login(username, password)
        server.send_message(msg)

# 使用示例
# send_email('smtp.gmail.com', 587, 'user@gmail.com', 
#            'password', 'to@example.com', '测试主题', '邮件正文')

# IMAP接收邮件示例
# import imaplib, email
# mail = imaplib.IMAP4_SSL('imap.gmail.com')
# mail.login('user@gmail.com', 'password')
# mail.select('inbox')
# result, data = mail.search(None, 'ALL')
# for num in data[0].split():
#     result, msg_data = mail.fetch(num, '(RFC822)')
#     msg = email.message_from_bytes(msg_data[0][1])
#     print(f"发件人: {msg['From']}, 主题: {msg['Subject']}")
```

## 关联页面

[[应用层-DNS]] [[应用层-FTP]] [[应用层-HTTP]] [[SSL-TLS]]
