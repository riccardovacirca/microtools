#include "Json.h"
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace mt {

std::string Json::encode(const Record &data) {
  json j;

  for (const auto& [key, value] : data) {
    std::visit([&](auto&& arg) {
      j[key] = arg;
    }, value);
  }

  return j.dump();
}

std::string Json::encode_array(const Recordset &data) {
  json j = json::array();

  for (const auto& record : data) {
    json obj;
    for (const auto& [key, value] : record) {
      std::visit([&](auto&& arg) {
        obj[key] = arg;
      }, value);
    }
    j.push_back(obj);
  }

  return j.dump();
}

Record Json::decode(const std::string &json_str) {
  Record record;

  try {
    json j = json::parse(json_str);

    for (auto& [key, value] : j.items()) {
      if (value.is_string()) {
        record[key] = value.get<std::string>();
      } else if (value.is_boolean()) {
        record[key] = value.get<bool>();
      } else if (value.is_number_integer()) {
        record[key] = value.get<long>();
      } else if (value.is_number_float()) {
        record[key] = value.get<double>();
      }
    }
  } catch (...) {
    // Return empty record on parse error
  }

  return record;
}

Recordset Json::decode_array(const std::string &json_str) {
  Recordset recordset;

  try {
    json j = json::parse(json_str);

    if (j.is_array()) {
      for (auto& elem : j) {
        Record record;
        for (auto& [key, value] : elem.items()) {
          if (value.is_string()) {
            record[key] = value.get<std::string>();
          } else if (value.is_boolean()) {
            record[key] = value.get<bool>();
          } else if (value.is_number_integer()) {
            record[key] = value.get<long>();
          } else if (value.is_number_float()) {
            record[key] = value.get<double>();
          }
        }
        recordset.push_back(record);
      }
    }
  } catch (...) {
    // Return empty recordset on parse error
  }

  return recordset;
}

} // namespace mt
