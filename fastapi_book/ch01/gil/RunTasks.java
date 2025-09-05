package fastapi_book.ch01.gil;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class RunTasks {

    // CPU-intensive task: sum up to a large number
    private static void cpuIntensiveTask() {
        long sumVal = 0;
        for (long i = 0; i < 1_000_000_000L; i++) {
            sumVal += i;
        }
    }

    // Run tasks sequentially
    private static void runTasksSequential(int numTasks) {
        long startTime = System.currentTimeMillis();

        for (int i = 0; i < numTasks; i++) {
            cpuIntensiveTask();
        }

        long duration = System.currentTimeMillis() - startTime;
        System.out.printf("Java: Sequentially completed %d tasks in: %.2f seconds%n", numTasks, duration / 1000.0);
    }

    // Run tasks with multiple threads
    private static void runTasksThreads(int numTasks) throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(numTasks);
        long startTime = System.currentTimeMillis();

        // Create and start the specified number of threads
        for (int i = 0; i < numTasks; i++) {
            executor.submit(RunTasks::cpuIntensiveTask);
        }

        // Wait for all threads to complete
        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.MINUTES);

        long duration = System.currentTimeMillis() - startTime;
        System.out.printf("Java: Multi-threaded completion of %d tasks in: %.2f seconds%n", numTasks, duration / 1000.0);
    }

    public static void main(String[] args) throws InterruptedException {
        // Set the number of tasks to run concurrently, ideally equal to the number of CPU cores
        int numTasks = Runtime.getRuntime().availableProcessors();
        System.out.printf("Java (multi-threading) experiment: Running %d tasks on %d CPU cores.%n", numTasks, numTasks);

        runTasksSequential(numTasks);
        runTasksThreads(numTasks);
    }
}
