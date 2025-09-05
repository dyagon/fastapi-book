package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

// CPU 密集型任务：累加到一个很大的数
func cpuIntensiveTask() {
	sum := 0
	for i := range 1000000000 {
		sum += i
	}
}

func run_tasks_sequential(numTasks int) {
	startTime := time.Now()
	for range numTasks {
		cpuIntensiveTask()
	}
	duration := time.Since(startTime)
	fmt.Printf("Go (Sequential) 实验完成，总耗时: %s\n", duration)
}

func run_tasks_concurrent(numTasks int) {
	var wg sync.WaitGroup
	startTime := time.Now()

	// 启动指定数量的 Goroutine
	for range numTasks {
		wg.Add(1) // WaitGroup 计数器加 1
		go func() {
			defer wg.Done() // Goroutine 完成时，计数器减 1
			cpuIntensiveTask()
		}()
	}

	// 等待所有 Goroutine 完成
	wg.Wait()

	duration := time.Since(startTime)
	fmt.Printf("Go (Concurrent) 实验完成，总耗时: %s\n", duration)
}

func main() {
	// 设置要并发执行的任务数量
	numTasks := runtime.NumCPU() // 理想情况下，设置为 CPU 核心数
	fmt.Printf("Go 实验：将在 %d 个 CPU 核心上运行 %d 个并发任务。\n", runtime.NumCPU(), numTasks)

	run_tasks_concurrent(numTasks)
	run_tasks_sequential(numTasks)

}
