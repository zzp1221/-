---
title: Go并发模型
course: 程序设计
chapter: 并发编程
difficulty: INTERMEDIATE
tags: [程序设计, Go, Goroutine, Channel, CSP, 并发]
aliases: [Goroutine, Go Channel, CSP模型]
source:
  - Go官方文档（go.dev/doc）
  - 《Go语言设计与实现》
  - Tony Hoare CSP论文
updated_at: 2026-05-03
---

## 核心定义

Go语言的并发模型基于CSP（Communicating Sequential Processes）理论，核心思想是"不要通过共享内存通信，而要通过通信共享内存"。Go的并发原语：(1)Goroutine：轻量级协程，初始栈仅2-8KB（可动态增长），由Go运行时调度器管理（M:N调度模型，M个goroutine映射到N个OS线程）。(2)Channel：类型安全的通信管道，支持无缓冲（同步）和有缓冲（异步）两种模式。发送和接收操作都会阻塞直到对端就绪（无缓冲）或缓冲区满/空（有缓冲）。(3)select语句：多路复用多个channel操作，类似IO多路复用。(4)sync包：提供Mutex、WaitGroup、Once、Pool等传统同步原语。Go运行时调度器GMP模型：G（Goroutine）→ M（Machine/OS Thread）→ P（Processor/逻辑处理器，数量等于GOMAXPROCS）。P持有本地运行队列，M从P的队列中取G执行，当G阻塞时M可以切换到其他G。

## 关键结论

- Goroutine的创建和切换开销远小于OS线程（栈KB级 vs 线程MB级，切换ns级 vs 线程μs级）
- Channel是Go推荐的并发通信方式，但不是唯一方式：共享内存+Mutex在某些场景更高效
- GOMAXPROCS默认等于CPU核心数，限制了并行执行的OS线程数
- Go的defer、panic、recover机制与goroutine配合，简化了并发错误处理
- Go的race detector（go run -race）可以检测数据竞争，是并发编程的重要调试工具

## 易错点

1. Goroutine泄漏是Go最常见的并发bug：goroutine阻塞在channel上无人接收，永远不会退出
2. 无缓冲channel的发送和接收都会阻塞：如果只有发送方没有接收方，发送方会永久阻塞
3. select的default分支是立即返回的，不要在循环中使用select+default做忙等待（浪费CPU）

## 例题

**例1：** 使用Go实现一个生产者-消费者模式，3个生产者和2个消费者，缓冲区大小为10。

**解答：**
```go
func main() {
    ch := make(chan int, 10)
    var wg sync.WaitGroup
    // 3个生产者
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for j := 0; j < 100; j++ {
                ch <- id*100 + j
            }
        }(i)
    }
    // 2个消费者
    var wg2 sync.WaitGroup
    for i := 0; i < 2; i++ {
        wg2.Add(1)
        go func(id int) {
            defer wg2.Done()
            for v := range ch {
                fmt.Printf("消费者%d处理%d\n", id, v)
            }
        }(i)
    }
    wg.Wait()
    close(ch) // 所有生产者完成后关闭channel
    wg2.Wait()
}
```
关键点：close(ch)通知消费者不再有新数据，range ch自动退出循环。

## 关联页面

[[协程原理与实现]] [[并发编程]] [[并发模型对比-线程vs协程vsActor]]
