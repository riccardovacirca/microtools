#pragma once

#include "Data.h"

namespace mt {

/**
 * @brief JSON encoding and decoding utilities (stateless)
 */
class Json {
public:
  /**
   * @brief Encodes a Record to JSON string
   * @param data Record to encode
   * @return JSON string representation
   */
  static std::string encode(const Record &data);
  /**
   * @brief Encodes a Recordset to JSON array string
   * @param data Recordset to encode
   * @return JSON array string representation
   */
  static std::string encode_array(const Recordset &data);
  /**
   * @brief Decodes a JSON string to Record
   * @param json_str JSON string to decode
   * @return Record containing decoded data
   */
  static Record decode(const std::string &json_str);
  /**
   * @brief Decodes a JSON array string to Recordset
   * @param json_str JSON array string to decode
   * @return Recordset containing decoded data
   */
  static Recordset decode_array(const std::string &json_str);
};

}  // namespace mt
