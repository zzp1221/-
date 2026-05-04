---
title: RabbitMQ与AMQP
course: 分布式系统
chapter: 消息系统与协调
difficulty: BASIC
tags: [RabbitMQ, AMQP, 消息队列, 路由, 交换机, 消息代理]
aliases: [RabbitMQ, AMQP, 高级消息队列协议, Advanced Message Queuing Protocol]
source:
  - "RabbitMQ Official Documentation"
  - "AMQP 0-9-1 Specification"
  - "Enterprise Integration Patterns, Hohpe & Woolf (2003)"
updated_at: 2026-05-03
---

## 核心定义

RabbitMQ是使用最广泛的开源消息代理（Message Broker），实现了**AMQP 0-9-1**（Advanced Message Queuing Protocol）协议。与Kafka的设计理念不同，RabbitMQ侧重于**消息路由的灵活性**和**可靠投递**。

**AMQP核心组件**：
- **Producer**：发送消息到Exchange
- **Exchange**：接收消息并根据路由规则分发到Queue
- **Queue**：存储消息，等待消费者消费
- **Binding**：定义Exchange和Queue之间的路由规则
- **Consumer**：从Queue消费消息

**Exchange类型**：
- **Direct**：精确匹配routing_key，消息发送到binding_key完全匹配的Queue
- **Fanout**：广播模式，消息发送到所有绑定的Queue（忽略routing_key）
- **Topic**：模式匹配，支持通配符（*匹配一个词，#匹配零或多个词）
- **Headers**：根据消息头部属性匹配（很少使用）

**可靠性保证**：
- **Publisher Confirm**：生产者确认消息已被Broker接收
- **持久化（Durable）**：Queue和消息都设置为持久化，重启后不丢失
- **ACK机制**：消费者手动确认消息处理完成，Broker才删除消息
- **Prefetch**：限制消费者未确认消息的数量，实现背压控制

**与Kafka的对比**：
- RabbitMQ：**推模式（push）**，Broker主动推送消息给消费者，适合低延迟场景
- Kafka：**拉模式（pull）**，消费者主动拉取消息，适合高吞吐量场景
- RabbitMQ的消息消费后删除，Kafka的消息保留一段时间

## 关键结论

- RabbitMQ的**Exchange**机制提供了比Kafka更灵活的消息路由能力
- RabbitMQ的**推模式**适合低延迟的实时消息处理，Kafka的**拉模式**适合高吞吐量的批处理
- **消息确认（ACK）**是保证消息不丢失的关键——消费者处理完成后必须手动ACK
- RabbitMQ的**集群镜像队列（Mirrored Queue）**提供高可用，但性能有损耗。新版RabbitMQ使用**Quorum Queue**替代
- RabbitMQ适合**企业应用集成**、**任务队列**、**RPC**等场景

## 易错点

1. **忘记手动ACK**：消费者如果使用自动ACK（autoAck=true），消息在发送给消费者后就被删除。如果消费者处理失败，消息会丢失
2. **Queue未设置持久化**：非持久化的Queue在Broker重启后会丢失，队列中的消息也会丢失
3. **忽视消息积压**：RabbitMQ的推模式下，如果消费者处理慢，消息会在Queue中积压。需要设置prefetch限制

## 例题

**题目**：设计一个使用RabbitMQ的任务分发系统，要求：
1. 任务发送到不同的工作队列（高优先级、普通优先级）
2. 高优先级任务优先处理
3. 任务处理失败后重试3次，然后进入死信队列

**解答**：

**Exchange和Queue设计**：

```
Producer → Exchange(task_exchange, type=direct)
    ├── binding_key="high" → Queue(high_priority_queue)
    └── binding_key="normal" → Queue(normal_priority_queue)
```

**消费者设计**：
- 高优先级消费者：只消费high_priority_queue
- 普通消费者：可以同时消费两个Queue，但优先处理high_priority_queue

**重试和死信队列配置**：

```
# 死信Exchange
DLX Exchange(dl_exchange, type=direct) → DLX Queue(dead_letter_queue)

# 主Queue配置
high_priority_queue:
  x-dead-letter-exchange: dl_exchange
  x-dead-letter-routing-key: dead_letter

normal_priority_queue:
  x-dead-letter-exchange: dl_exchange
  x-dead-letter-routing-key: dead_letter
```

**消费者逻辑**：
```python
def callback(ch, method, properties, body):
    try:
        process_task(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        # 检查重试次数
        retry_count = properties.headers.get('x-retry-count', 0)
        if retry_count < 3:
            # 重新发布，增加重试计数
            properties.headers['x-retry-count'] = retry_count + 1
            ch.basic_publish(exchange='', routing_key=method.routing_key,
                           body=body, properties=properties)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # 超过重试次数，拒绝消息，进入死信队列
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

## 关联页面

[[消息队列原理]] [[Kafka架构详解]] [[幂等性设计]] [[熔断与降级]] [[ZooKeeper原理与应用]]
