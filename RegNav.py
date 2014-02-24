#!/bin/python

import ntpath
import re
import _winreg as winreg

class RegistryError(Exception):

    error_codes = {
        1:  "Unable to connect to remote registry.",
        2:  "Access is denied.",
        3:  "Requested key does not exist in registry.",
        4:  "Requested value does not exist under given key.",
        5:  "Cannot open requested key.",
        21: "Unknown registry handle key.",
        22: "No open key to query data from.",
        99: "Unknown registry error.",
    }

    def __init__(self, *args):
        self.args = [i for i in args]
        self.errno = args[0]
        self.strerr = self.error_codes[self.errno]
        self.extended_info = args[1]

    def __str__(self):
        return repr(self.strerr)

class RegNav(object):

    handle_key_list = {
        "HKCR": winreg.HKEY_CLASSES_ROOT,
        "HKCC": winreg.HKEY_CURRENT_CONFIG,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKDD": winreg.HKEY_DYN_DATA,
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKPD": winreg.HKEY_PERFORMANCE_DATA,
        "HKUS": winreg.HKEY_USERS,
    }

    def __init__(self, computer, handle_key="HKLM"):
        self.computer = computer
        self.handle_key_short = handle_key
        try:
            self.handle_key = self.handle_key_list[handle_key]
        except KeyError:
            raise RegistryError(21, (handle_key))
        try:
            self.registry = winreg.ConnectRegistry(
                r"\\" + computer,
                winreg.HKEY_LOCAL_MACHINE)
        except WindowsError, (errno, strerr):
            if errno == 53:
                raise RegistryError(1, (computer, None, None))
            elif errno == 5:
                raise RegistryError(2, (computer, None, None))
            else:
                raise RegistryError(99, (computer, errno, strerr))

    def normalizeKey(self, key):
        return ntpath.normpath(key)

    def fullKey(self):
        try:
            keypath = "{handle}/{key}".format(
                handle=self.handle_key_short,
                key=self.current_key,
            )
        except AttributeError:
            raise RegistryError(22, (self.computer, self.current_key, value))
        return self.normalizeKey(keypath)

    def doesKeyExist(self, key):
        key = self.normalizeKey(key)
        try:
            winreg.OpenKey(self.registry, key)
        except WindowsError:
            return False
        return True

    def openKey(self, key):
        self.current_key = self.normalizeKey(key)
        try:
            self.open_key = winreg.OpenKey(
                self.registry, 
                self.current_key)
        except WindowsError:
            raise RegistryError(3, (self.computer, key, None))
        return True

    def getDataFromValue(self, value):
        try:
            wvalue = winreg.QueryValueEx(self.open_key, value)
        except AttributeError:
            raise RegistryError(22, (self.computer, self.current_key, value))
        except WindowsError:
            raise RegistryError(4, (self.computer, self.current_key, value))
        return wvalue

    def __str__(self):
        return self.computer
