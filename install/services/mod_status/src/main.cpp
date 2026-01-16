#include <atomic>
#include <condition_variable>
#include <csignal>
#include <mutex>
#include <queue>
#include <thread>
#include <unordered_map>
#include <uwebsockets/App.h>
#include <microtools/microtools.h>

std::unique_ptr<mt::Logger> logger;
std::unique_ptr<mt::Redis> redis_conn;
std::string db_dsn;
std::atomic<bool> running{true};
std::mutex queue_mtx;
std::condition_variable queue_cv;
std::queue<std::string> job_queue;
std::mutex clients_mtx;
typedef uWS::WebSocket<false, true, std::string> WS;
std::unordered_map<std::string, WS*> clients;
std::unordered_map<std::string, std::string> pending_results;
uWS::Loop *uws_loop = nullptr;
us_listen_socket_t *listen_socket = nullptr;
constexpr size_t MAX_QUEUE = 1000;
std::atomic<uint64_t> job_counter{0};

void handle_signal(int) {
  running = false;
  queue_cv.notify_all();
  if (logger) {
    logger->warn("Shutdown requested (SIGTERM/SIGINT)");
  }
  if (uws_loop && listen_socket) {
    uws_loop->defer([&]() {
      us_listen_socket_close(0, listen_socket);
    });
  }
}

std::string generate_job_id() {
  uint64_t id = job_counter.fetch_add(1);
  return "job_" + std::to_string(id);
}

bool enqueue_job(const std::string &job_id) {
  std::lock_guard<std::mutex> lock(queue_mtx);
  if (job_queue.size() >= MAX_QUEUE) {
    logger->warn("Job queue full");
    return false;
  }
  job_queue.push(job_id);
  return true;
}

std::string get_app_status() {
  std::string cached = redis_conn->get("app_status");
  if (!cached.empty()) {
    logger->info("Cache hit: returning app_status from Redis");
    return cached;
  }
  logger->info("Cache miss: reading app_status from database");
  mt::DB db;
  db.connect(db_dsn);
  mt::Record record = db.select("SELECT id, version, created_at, updated_at FROM app_status WHERE id = 1");
  db.disconnect();
  if (record.empty()) {
    mt::Record error;
    error["error"] = std::string("app_status record not found");
    return mt::Json::encode(error);
  }
  std::string json_response = mt::Json::encode(record);
  redis_conn->set("app_status", json_response);
  logger->info("Stored app_status in Redis cache");
  return json_response;
}

void notify_done(const std::string &job_id, const std::string &result) {
  std::lock_guard<std::mutex> lock(clients_mtx);
  std::unordered_map<std::string, WS*>::iterator it = clients.find(job_id);
  if (it == clients.end()) {
    logger->info("Client not yet registered for " + job_id + ", storing result");
    pending_results[job_id] = result;
    return;
  }
  WS *ws = it->second;
  clients.erase(it);
  uws_loop->defer([ws, result]() {
    ws->send(result, uWS::OpCode::TEXT);
  });
}

void worker_thread(int id) {
  logger->info("Worker " + std::to_string(id) + " started");
  while (running) {
    std::string job_id;
    {
      std::unique_lock<std::mutex> lock(queue_mtx);
      queue_cv.wait(lock, []() { return !job_queue.empty() || !running; });
      if (!running && job_queue.empty()) {
        break;
      }
      if (job_queue.empty()) {
        continue;
      }
      job_id = job_queue.front();
      job_queue.pop();
    }
    try {
      logger->info("Worker " + std::to_string(id) + " processing " + job_id);
      std::string result = get_app_status();
      notify_done(job_id, result);
    } catch (const std::exception &e) {
      logger->error("Job failed: " + job_id + " - " + std::string(e.what()));
      mt::Record error;
      error["error"] = std::string(e.what());
      notify_done(job_id, mt::Json::encode(error));
    }
  }
  logger->info("Worker " + std::to_string(id) + " shutdown");
}

int main() {
  logger = std::make_unique<mt::Logger>("mod_status", "/workspace/logs/mod_status.log");
  logger->info("Service starting...");
  signal(SIGTERM, handle_signal);
  signal(SIGINT, handle_signal);
  mt::Env env;
  std::string host = std::get<std::string>(env.get("MICROSERVICE_MOD_STATUS_HOST"));
  int port = std::stoi(std::get<std::string>(env.get("MICROSERVICE_MOD_STATUS_PORT")));
  std::string redis_host = std::get<std::string>(env.get("REDIS_HOST"));
  int redis_port = std::stoi(std::get<std::string>(env.get("REDIS_PORT")));
  db_dsn = std::get<std::string>(env.get("DB_DSN"));
  try {
    redis_conn = std::make_unique<mt::Redis>(redis_host, redis_port);
    redis_conn->connect();
    logger->info("Connected to Redis at " + redis_host + ":" + std::to_string(redis_port));
  } catch (const std::exception &e) {
    logger->error("Failed to connect to Redis: " + std::string(e.what()));
    return 1;
  }
  int workers = std::thread::hardware_concurrency();
  if (workers < 1) {
    workers = 2;
  }
  std::vector<std::thread> pool;
  for (int i = 0; i < workers; ++i) {
    pool.emplace_back(worker_thread, i);
  }
  logger->info("Started " + std::to_string(workers) + " worker threads");
  uWS::App()
    .ws<std::string>("/ws", {
      .open = [](WS *ws) {
        logger->info("WS client connected");
      },
      .message = [](WS *ws, std::string_view message, uWS::OpCode) {
        std::string job_id(message);
        std::lock_guard<std::mutex> lock(clients_mtx);
        std::unordered_map<std::string, std::string>::iterator pending_it = pending_results.find(job_id);
        if (pending_it != pending_results.end()) {
          std::string result = pending_it->second;
          pending_results.erase(pending_it);
          logger->info("Sending pending result for " + job_id);
          ws->send(result, uWS::OpCode::TEXT);
          return;
        }
        clients[job_id] = ws;
        logger->info("WS client registered for " + job_id);
      },
      .close = [](WS *ws, int, std::string_view) {
        std::lock_guard<std::mutex> lock(clients_mtx);
        for (std::unordered_map<std::string, WS*>::iterator it = clients.begin(); it != clients.end(); ) {
          if (it->second == ws) {
            it = clients.erase(it);
          } else {
            ++it;
          }
        }
        logger->info("WS client disconnected");
      }
    })
    .post("/api/status/info", [](uWS::HttpResponse<false> *res, uWS::HttpRequest *) {
      std::string job_id = generate_job_id();
      if (!enqueue_job(job_id)) {
        res->writeStatus("503 Service Unavailable")
           ->writeHeader("Content-Type", "application/json")
           ->end("{\"error\":\"Service unavailable\"}");
        return;
      }
      queue_cv.notify_one();
      res->writeHeader("Content-Type", "application/json")
         ->end("{\"job_id\":\"" + job_id + "\"}");
    })
    .listen(host, port, [&](auto *token) {
      if (token) {
        listen_socket = token;
        uws_loop = uWS::Loop::get();
        logger->info("Service started on " + host + ":" + std::to_string(port));
        logger->info("Database DSN: " + db_dsn);
      } else {
        logger->error("Failed to start server on " + host + ":" + std::to_string(port));
        running = false;
        queue_cv.notify_all();
      }
    })
    .run();
  for (std::thread &t : pool) {
    t.join();
  }
  redis_conn->disconnect();
  logger->info("Disconnected from Redis");
  logger->info("Service stopped cleanly");
  return 0;
}
