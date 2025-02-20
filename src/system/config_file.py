# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import json


class ConfigFile:
    class CheckError(Exception):
        pass

    class UnexpectedKeyValueError(CheckError):
        def __init__(self, key, expected, current=None):
            super().__init__(
                f"Expected to have {key}='{expected}', but was '{current}'."
                if current
                else f"Expected to have {key}='{expected}', but none was found."
            )

    class UnexpectedKeyValuesError(CheckError):
        def __init__(self, key, expected, current=None):
            super().__init__(
                f"Expected to have {key}=any of {expected}, but was '{current}'."
                if current
                else f"Expected to have {key}=any of {expected}, but none was found."
            )

    @property
    def data(self):
        return self.__data

    @classmethod
    def from_file(cls, path):
        with open(path, "r") as f:
            return cls(json.load(f))

    def __init__(self, data=None):
        if type(data) is str:
            self.__data = json.loads(data)
        elif type(data) is dict:
            self.__data = data
        elif data is not None:
            raise TypeError()
        else:
            self.__data = {}

    def get_value(self, key, default_value=None):
        try:
            return self.__data[key]
        except KeyError:
            return default_value

    def check_value(self, key, expected):
        try:
            value = self.__data[key]
            if value != expected:
                raise ConfigFile.UnexpectedKeyValueError(key, expected, value)
        except KeyError:
            raise ConfigFile.UnexpectedKeyValueError(key, expected)

    def check_value_in(self, key, expected):
        try:
            value = self.__data[key]
            if value not in expected:
                raise ConfigFile.UnexpectedKeyValuesError(key, expected, value)
        except KeyError:
            if None not in expected:
                raise ConfigFile.UnexpectedKeyValuesError(key, expected)
