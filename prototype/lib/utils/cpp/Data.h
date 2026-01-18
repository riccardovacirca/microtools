#pragma once

#include <map>
#include <string>
#include <variant>
#include <vector>

namespace mt {
typedef std::variant<int, long, double, bool, std::string> Field;
typedef std::vector<Field> Array;
typedef std::map<std::string, Field> Record;
typedef std::vector<Record> Recordset;
} // namespace mt
