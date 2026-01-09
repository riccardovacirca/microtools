#include <httplib.h>
#include <iostream>
#include <csignal>
#include <memory>
#include <microtools/microtools.h>

// Global logger instance
std::unique_ptr<mt::Logger> logger;

// Global Redis and DB connections
std::unique_ptr<mt::Redis> redis_conn;
std::string db_dsn;

// Signal handler for graceful shutdown
volatile sig_atomic_t shutdown_requested = 0;

void signal_handler(int signal) {
  if (logger) {
    logger->info("Shutdown signal received");
  }
  shutdown_requested = 1;
}

// GET /api/status/info - Runtime information with Redis cache and DB fallback
void handle_info(const httplib::Request& req, httplib::Response& res) {
  std::string jsonResponse;

  try {
    // Step 1: Check if "app_status" key exists in Redis
    std::string cached = redis_conn->get("app_status");

    if (!cached.empty()) {
      // Cache hit: return cached JSON directly
      if (logger) {
        logger->info("Cache hit: returning app_status from Redis");
      }
      jsonResponse = cached;
    } else {
      // Cache miss: read from database
      if (logger) {
        logger->info("Cache miss: reading app_status from database");
      }

      // Step 2: Connect to database and read record
      mt::DB db;
      db.connect(db_dsn);

      mt::Record record = db.select("SELECT id, version, created_at, updated_at FROM app_status WHERE id = 1");

      db.disconnect();

      // Check if record was found
      if (record.empty()) {
        res.set_content("{\"error\":\"app_status record not found\"}", "application/json");
        res.status = 404;
        return;
      }

      // Step 3: Serialize record to JSON
      jsonResponse = mt::Json::encode(record);

      // Step 4: Store in Redis for future requests
      redis_conn->set("app_status", jsonResponse);

      if (logger) {
        logger->info("Stored app_status in Redis cache");
      }
    }

    // Return JSON response
    res.set_content(jsonResponse, "application/json");
    res.status = 200;

  } catch (const std::exception& e) {
    // Handle errors
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
  // Initialize logger (creates /workspace/logs/mod_status.log)
  logger = std::make_unique<mt::Logger>("mod_status", "/workspace/logs/mod_status.log");
  logger->info("Service starting...");

  // Setup signal handlers
  signal(SIGINT, signal_handler);
  signal(SIGTERM, signal_handler);

  // Load configuration using microtools Env
  mt::Env env;
  std::string host = "127.0.0.1";
  int port = 9001;
  std::string redis_host = "127.0.0.1";
  int redis_port = 6379;

  if (env.has("MOD_STATUS_HOST")) {
    host = std::get<std::string>(env.get("MOD_STATUS_HOST"));
  }
  if (env.has("MOD_STATUS_PORT")) {
    port = std::stoi(std::get<std::string>(env.get("MOD_STATUS_PORT")));
  }

  // Get Redis configuration
  if (env.has("REDIS_HOST")) {
    redis_host = std::get<std::string>(env.get("REDIS_HOST"));
  }
  if (env.has("REDIS_PORT")) {
    redis_port = std::stoi(std::get<std::string>(env.get("REDIS_PORT")));
  }

  // Get database DSN (ODBC connection string)
  db_dsn = "DSN=hola_sqlite"; // Default SQLite3 DSN
  if (env.has("DB_DSN")) {
    db_dsn = std::get<std::string>(env.get("DB_DSN"));
  }

  // Initialize Redis connection
  try {
    redis_conn = std::make_unique<mt::Redis>(redis_host, redis_port);
    redis_conn->connect();
    logger->info("Connected to Redis at " + redis_host + ":" + std::to_string(redis_port));
  } catch (const std::exception& e) {
    logger->error("Failed to connect to Redis: " + std::string(e.what()));
    std::cerr << "Failed to connect to Redis: " << e.what() << std::endl;
    return 1;
  }

  // Create HTTP server
  httplib::Server server;

  // Register route
  server.Get("/api/status/info", handle_info);

  // Request logger using microtools Logger
  server.set_logger([&](const httplib::Request& req, const httplib::Response& res) {
    // Log to both console and file
    std::string logMessage = "[" + req.method + "] " + req.path + " - " + std::to_string(res.status);

    // Console output
    std::cout << logMessage << std::endl;

    // File logging via microtools Logger
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

  // Log startup
  logger->info("Service started on " + host + ":" + std::to_string(port));
  logger->info("Database DSN: " + db_dsn);

  // Start server (blocking call)
  if (!server.listen(host.c_str(), port)) {
    logger->error("Failed to start server on " + host + ":" + std::to_string(port));
    std::cerr << "Failed to start server on " << host << ":" << port << std::endl;
    redis_conn->disconnect();
    return 1;
  }

  // Cleanup
  logger->info("Server stopped");
  redis_conn->disconnect();
  logger->info("Disconnected from Redis");

  return 0;
}
