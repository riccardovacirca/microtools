#include "DB.h"

#include <nanodbc/nanodbc.h>
#include <stdexcept>

namespace mt {

static Field result_to_field(nanodbc::result &result, short col_index) {
  if (result.is_null(col_index)) {
    return std::string("");
  }
  int sql_type = result.column_datatype(col_index);
  if (sql_type == -5 || sql_type == 4 || sql_type == 5 || sql_type == -6) {
    return result.get<long>(col_index);
  } else if (sql_type == 6 || sql_type == 7 || sql_type == 8 || sql_type == 3 ||
             sql_type == 2) {
    return result.get<double>(col_index);
  } else if (sql_type == -7) {
    // BIT type: convert to bool via int
    return static_cast<bool>(result.get<int>(col_index));
  } else {
    return result.get<std::string>(col_index);
  }
}

DB::DB() {
  connection_ = nullptr;
  cursor_ = nullptr;
  cursor_first_call_ = true;
  cursor_has_data_ = false;
}

DB::~DB() {
  if (cursor_) {
    cursor_close();
  }
  if (connection_) {
    disconnect();
  }
}

void DB::connect(const std::string &connection_string) {
  try {
    connection_ = std::make_unique<nanodbc::connection>(connection_string);
    if (!connection_->connected()) {
      connection_ = nullptr;
      throw std::runtime_error("Failed to connect to database");
    }
  } catch (const nanodbc::database_error &e) {
    throw std::runtime_error(std::string("Database error: ") + e.what());
  }
}

void DB::disconnect() {
  if (cursor_) {
    cursor_close();
  }
  if (connection_) {
    connection_->disconnect();
    connection_ = nullptr;
  }
}

bool DB::is_connected() const {
  return connection_ && connection_->connected();
}

int DB::query(const std::string &sql) {
  if (!is_connected()) {
    throw std::runtime_error("Database not connected");
  }
  try {
    nanodbc::result result = nanodbc::execute(*connection_, sql);
    return static_cast<int>(result.affected_rows());
  } catch (const nanodbc::database_error &e) {
    throw std::runtime_error(std::string("Query error: ") + e.what());
  }
}

Record DB::select(const std::string &sql) {
  Record rec;
  if (!is_connected()) {
    throw std::runtime_error("Database not connected");
  }
  try {
    nanodbc::result result = nanodbc::execute(*connection_, sql);
    if (!result.next()) {
      return rec;
    }
    short num_cols = result.columns();
    for (short i = 0; i < num_cols; ++i) {
      std::string col_name = result.column_name(i);
      rec[col_name] = result_to_field(result, i);
    }
    return rec;
  } catch (const nanodbc::database_error &e) {
    throw std::runtime_error(std::string("Select error: ") + e.what());
  }
}

Recordset DB::select_all(const std::string &sql) {
  Recordset rs;
  if (!is_connected()) {
    throw std::runtime_error("Database not connected");
  }
  try {
    nanodbc::result result = nanodbc::execute(*connection_, sql);
    while (result.next()) {
      Record rec;
      short num_cols = result.columns();
      for (short i = 0; i < num_cols; ++i) {
        std::string col_name = result.column_name(i);
        rec[col_name] = result_to_field(result, i);
      }
      rs.push_back(rec);
    }
    return rs;
  } catch (const nanodbc::database_error &e) {
    throw std::runtime_error(std::string("Select all error: ") + e.what());
  }
}

void DB::cursor_open(const std::string &sql) {
  if (!is_connected()) {
    throw std::runtime_error("Database not connected");
  }
  if (cursor_) {
    throw std::runtime_error("Cursor already open");
  }
  try {
    cursor_ =
        std::make_unique<nanodbc::result>(nanodbc::execute(*connection_, sql));
    cursor_first_call_ = true;
    cursor_has_data_ = false;
  } catch (const nanodbc::database_error &e) {
    throw std::runtime_error(std::string("Cursor open error: ") + e.what());
  }
}

bool DB::cursor_has_next() {
  if (!cursor_) {
    return false;
  }
  if (cursor_first_call_) {
    cursor_has_data_ = cursor_->next();
    cursor_first_call_ = false;
  }
  return cursor_has_data_;
}

Record DB::cursor_next() {
  Record rec;
  if (!cursor_) {
    throw std::runtime_error("Cursor not open");
  }
  if (cursor_first_call_) {
    cursor_has_data_ = cursor_->next();
    cursor_first_call_ = false;
  }
  if (!cursor_has_data_) {
    return rec;
  }
  short num_cols = cursor_->columns();
  for (short i = 0; i < num_cols; ++i) {
    std::string col_name = cursor_->column_name(i);
    rec[col_name] = result_to_field(*cursor_, i);
  }
  cursor_has_data_ = cursor_->next();
  return rec;
}

void DB::cursor_close() {
  if (cursor_) {
    cursor_ = nullptr;
    cursor_first_call_ = true;
    cursor_has_data_ = false;
  }
}

} // namespace mt
