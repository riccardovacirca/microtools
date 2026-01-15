#include "Redis.h"
#include <hiredis/hiredis.h>
#include <stdexcept>

namespace mt {

Redis::Redis(const std::string &host, int port) {
  host_ = host;
  port_ = port;
  context_ = nullptr;
}

Redis::~Redis() {
  disconnect();
}

void Redis::connect() {
  redisContext *ctx = redisConnect(host_.c_str(), port_);
  if (ctx == nullptr || ctx->err) {
    std::string error = ctx ? ctx->errstr : "Connection failed";
    if (ctx) redisFree(ctx);
    throw std::runtime_error("Redis connection error: " + error);
  }
  context_ = ctx;
}

void Redis::disconnect() {
  if (context_) {
    redisFree(static_cast<redisContext*>(context_));
    context_ = nullptr;
  }
}

std::vector<std::string> Redis::keys(const std::string &pattern) {
  std::vector<std::string> result;
  if (!context_) throw std::runtime_error("Not connected to Redis");
  redisReply *reply = static_cast<redisReply*>(redisCommand(static_cast<redisContext*>(context_), "KEYS %s", pattern.c_str()));
  if (!reply) throw std::runtime_error("Redis KEYS command failed");
  if (reply->type == REDIS_REPLY_ARRAY) {
    for (size_t i = 0; i < reply->elements; i++) {
      result.push_back(reply->element[i]->str);
    }
  }
  freeReplyObject(reply);
  return result;
}

std::string Redis::get(const std::string &key) {
  if (!context_) throw std::runtime_error("Not connected to Redis");
  redisReply *reply = static_cast<redisReply*>(redisCommand(static_cast<redisContext*>(context_), "GET %s", key.c_str()));
  if (!reply) throw std::runtime_error("Redis GET command failed");
  std::string value;
  if (reply->type == REDIS_REPLY_STRING) {
    value = reply->str;
  }
  freeReplyObject(reply);
  return value;
}

void Redis::set(const std::string &key, const std::string &value) {
  if (!context_) throw std::runtime_error("Not connected to Redis");
  redisReply *reply = static_cast<redisReply*>(redisCommand(static_cast<redisContext*>(context_), "SET %s %s", key.c_str(), value.c_str()));
  if (!reply) throw std::runtime_error("Redis SET command failed");
  freeReplyObject(reply);
}

void Redis::del(const std::string &key) {
  if (!context_) throw std::runtime_error("Not connected to Redis");
  redisReply *reply = static_cast<redisReply*>(redisCommand(static_cast<redisContext*>(context_), "DEL %s", key.c_str()));
  if (!reply) throw std::runtime_error("Redis DEL command failed");
  freeReplyObject(reply);
}

}  // namespace mt
