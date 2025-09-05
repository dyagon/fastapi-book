use std::thread;
use std::time::Instant;
use sha2::{Digest, Sha256};

// CPU-intensive task: repeatedly calculate SHA-256 hashes
fn cpu_intensive_task() {
    let mut hasher = Sha256::new();
    let mut data = b"a long string of initial data to make it a bit more work".to_vec();
    // Loop many times to ensure the task is CPU-bound
    for _ in 0..500_000 {
        hasher.update(&data);
        data = hasher.finalize_reset().to_vec();
    }
}
// Run tasks sequentially
fn run_tasks_sequential(num_tasks: usize) {
    let start_time = Instant::now();
    for _ in 0..num_tasks {
        cpu_intensive_task();
    }
    let duration = start_time.elapsed();
    println!(
        "Rust: Sequentially completed {} tasks in: {:.2} seconds",
        num_tasks,
        duration.as_secs_f64()
    );
}

// Run tasks with multiple threads
fn run_tasks_threads(num_tasks: usize) {
    let start_time = Instant::now();
    let mut handles = vec![];

    for _ in 0..num_tasks {
        let handle = thread::spawn(|| {
            cpu_intensive_task();
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let duration = start_time.elapsed();
    println!(
        "Rust: Multi-threaded completion of {} tasks in: {:.2} seconds",
        num_tasks,
        duration.as_secs_f64()
    );
}

fn main() {
    // Set the number of tasks to run concurrently, ideally equal to the number of CPU cores
    let num_tasks = num_cpus::get();
    println!(
        "Rust (multi-threading) experiment: Running {} tasks on {} CPU cores.",
        num_tasks, num_tasks
    );

    run_tasks_sequential(num_tasks);
    run_tasks_threads(num_tasks);
}
