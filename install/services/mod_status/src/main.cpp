#include <httplib.h>
#include <iostream>
#include <csignal>
#include <memory>
#include <microtools/microtools.h>

std::unique_ptr<mt::Logger> logger;
std::unique_ptr<mt::Redis> redis_conn;
std::string db_dsn;
httplib::Server* g_server = nullptr;
volatile sig_atomic_t shutdown_requested = 0;

void signal_handler(int signal) {
  if (logger) {
    logger->info("Shutdown signal received");
  }
  shutdown_requested = 1;
  if (g_server) {
    g_server->stop();
  }
}

void handle_info(const httplib::Request &req, httplib::Response &res) {
  std::string jsonResponse;
  try {
    std::string cached = redis_conn->get("app_status");
    if (!cached.empty()) {
      if (logger) {
        logger->info("Cache hit: returning app_status from Redis");
      }
      jsonResponse = cached;
    } else {
      if (logger) {
        logger->info("Cache miss: reading app_status from database");
      }
      mt::DB db;
      db.connect(db_dsn);
      mt::Record record = db.select("SELECT id, version, created_at, updated_at FROM app_status WHERE id = 1");
      db.disconnect();
      if (record.empty()) {
        res.set_content("{\"error\":\"app_status record not found\"}", "application/json");
        res.status = 404;
        return;
      }
      jsonResponse = mt::Json::encode(record);
      redis_conn->set("app_status", jsonResponse);
      if (logger) {
        logger->info("Stored app_status in Redis cache");
      }
    }
    res.set_content(jsonResponse, "application/json");
    res.status = 200;
  } catch (const std::exception &e) {
    if (logger) {
      logger->error("Error in handle_info: " + std::string(e.what()));
    }
    mt::Record error;
    error["error"] = std::string(e.what());
    res.set_content(mt::Json::encode(error), "application/json");
    res.status = 500;
  }
}

int main(int argc, char* argv[]) {
  logger = std::make_unique<mt::Logger>("mod_status", "/workspace/logs/mod_status.log");
  logger->info("Service starting...");
  signal(SIGINT, signal_handler);
  signal(SIGTERM, signal_handler);
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
    std::cerr << "Failed to connect to Redis: " << e.what() << std::endl;
    return 1;
  }
  httplib::Server server;
  g_server = &server;
  server.Get("/api/status/info", handle_info);
  server.set_logger([&](const httplib::Request &req, const httplib::Response &res) {
    std::string logMessage = "[" + req.method + "] " + req.path + " - " + std::to_string(res.status);
    std::cout << logMessage << std::endl;
    if (logger) {
      if (res.status >= 500) {
        logger->error(logMessage);
      } else if (res.status >= 400) {
        logger->warn(logMessage);
      } else {
        logger->info(logMessage);
      }
    }
  });
  logger->info("Service started on " + host + ":" + std::to_string(port));
  logger->info("Database DSN: " + db_dsn);
  if (!server.listen(host.c_str(), port)) {
    logger->error("Failed to start server on " + host + ":" + std::to_string(port));
    std::cerr << "Failed to start server on " << host << ":" << port << std::endl;
    redis_conn->disconnect();
    return 1;
  }
  logger->info("Server stopped");
  redis_conn->disconnect();
  logger->info("Disconnected from Redis");
  return 0;
}
