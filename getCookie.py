# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.9.6 (default, Jun 27 2024, 17:58:20) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: getCookie.py

import os, re, sys, json, base64, sqlite3, random, configparser, logging, logging.config
from win32crypt import CryptUnprotectData
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from abc import abstractmethod, ABCMeta
NODE_ELK_TOKEN_ID = "elk_token_id"
NODE_PREFIX = "_YY_TID_"
NODE_WEB_TOKEN = "web_token"
NODE_ITEM = "item"
NODE_BROWSER = "browser"
NODE_DOMAIN = "domain"
NODE_TYPE = "type"
VALUE_OLD = "old"
VALUE_NEW = "new"
CONFIG_NODE_PROFILE = "Profile"
CONFIG_KEY_PATH = "path"

class CookieParser(metaclass=ABCMeta):

    @abstractmethod
    def get_elk_data(self, host):
        pass


class CookieParserBase(CookieParser):

    def get_elk_data(self, host_list):
        """
        从cookie数据中解析elk数据
        :param host: 网站域名，e.g. dvdfab.cn
        :return: 返回包含网站elk数据的字典
        """
        host_elk_data = list()
        for host in host_list:
            cookie_data_list = self.get_cookie_data(host)
            for cookie_data in cookie_data_list:
                if NODE_ELK_TOKEN_ID in cookie_data:
                    elk_old_data = dict()
                    elk_old_data[NODE_BROWSER] = self.get_browser_name()
                    elk_old_data[NODE_ITEM] = cookie_data[NODE_ELK_TOKEN_ID]
                    elk_old_data[NODE_DOMAIN] = host
                    elk_old_data[NODE_TYPE] = VALUE_OLD
                    host_elk_data.append(elk_old_data)
                keys = cookie_data.keys()
                for key in keys:
                    if key.startswith(NODE_PREFIX):
                        data = key.split("_", 3)
                        if len(data) == 4:
                            elk_new_data = dict()
                            elk_new_data[NODE_BROWSER] = self.get_browser_name()
                            elk_new_data[NODE_ITEM] = data[3]
                            elk_new_data[NODE_DOMAIN] = host
                            elk_new_data[NODE_TYPE] = VALUE_NEW
                            host_elk_data.append(elk_new_data)
                        elif re.match("_YY_V\\d{1,2}_TID_", key):
                            data = key.split("_", 4)
                            if len(data) == 5:
                                elk_new_data = dict()
                                elk_new_data[NODE_BROWSER] = self.get_browser_name()
                                elk_new_data[NODE_ITEM] = data[4]
                                elk_new_data[NODE_DOMAIN] = host
                                elk_new_data[NODE_TYPE] = data[2].lower()
                                host_elk_data.append(elk_new_data)

        return host_elk_data

    @abstractmethod
    def get_cookie_data(self, host):
        """
        获取host对应的cookie数据
        :param host: 网站域名，e.g. dvdfab.cn
        :return: 返回包含网站cookie数据的字典的list
        """
        pass

    @abstractmethod
    def get_sql(self, host):
        pass

    @abstractmethod
    def get_browser_name(self):
        pass

    have_log = False


class CookieParserFireFox(CookieParserBase):
    __doc__ = "从profiles.ini中获取cookies目录名称"

    def get_cookies_path_from_profile(self):
        profile_path_list = list()
        mozilla_profile = os.path.join(os.getenv("APPDATA"), "Mozilla\\Firefox")
        mozilla_profile_ini = os.path.join(mozilla_profile, "profiles.ini")
        if not os.path.exists(mozilla_profile_ini):
            logger.warning("Profile.ini file is not found.")
            return profile_path_list
        try:
            profile = configparser.ConfigParser()
            profile.read(mozilla_profile_ini)
            for i in range(10):
                profile_section = CONFIG_NODE_PROFILE + str(i)
                if profile.has_section(profile_section):
                    data_path = os.path.normpath(os.path.join(mozilla_profile, profile.get(profile_section, "Path")))
                    cookie_path = os.path.join(data_path, "cookies.sqlite")
                    profile_path_list.append(cookie_path)

        except Exception as e:
            try:
                logger.warning("Read profiles.ini failed {}".format(e))
            finally:
                e = None
                del e

        return profile_path_list

    def get_cookie_path(self):
        """
        获取浏览器cookies文件路径
        :return: cookie文件全路径
        """
        s_cookiepath_common = os.environ["APPDATA"] + "\\Mozilla\\Firefox\\Profiles"
        profile_path_list = list()
        if not os.path.exists(s_cookiepath_common):
            return profile_path_list
        profile_path_list = self.get_cookies_path_from_profile()
        if len(profile_path_list) == 0:
            l_folds_arr = os.listdir(s_cookiepath_common)
            l_folds_end = [os.path.splitext(s_file)[-1][1[:None]] for s_file in l_folds_arr]
            if "default-release" in l_folds_end:
                cookie_fold_index = l_folds_end.index("default-release")
            else:
                if "default" in l_folds_end:
                    cookie_fold_index = l_folds_end.index("default")
                else:
                    if random.randint(0, 100) == 50:
                        logger.error("Cannot find default folder: {}".format(str(l_folds_end)))
                        cookie_fold_index = l_folds_end.index("default")
                    else:
                        logger.error("Cannot find default folder: {}".format(str(l_folds_end)))
                        return profile_path_list
            cookie_fold = l_folds_arr[cookie_fold_index]
            cookie_path = os.path.join(s_cookiepath_common, cookie_fold)
            cookie_path = os.path.join(cookie_path, "cookies.sqlite")
            profile_path_list.append(cookie_path)
        return profile_path_list

    def get_sql(self, host):
        sql = "select host,name,value from moz_cookies where host='%s'" % host
        return sql

    def get_browser_name(self):
        return "FileFox"

    def get_cookie_data(self, host):
        cookie_data_list = list()
        cookie_path_list = self.get_cookie_path()
        for cookie_path in cookie_path_list:
            if not os.path.exists(cookie_path):
                continue
            if self.have_log == False:
                logger.info("Found cookies file, {}".format(cookie_path))
            sql = self.get_sql(host)
            try:
                with sqlite3.connect(cookie_path) as conn:
                    cur = conn.cursor()
                    d_cookie = dict()
                    res = cur.execute(sql).fetchall()
                    for host_key, name, value in res:
                        if name == "miniDialog":
                            continue
                        d_cookie[name] = value

                    if d_cookie:
                        cookie_data_list.append(d_cookie)
            except Exception as e:
                try:
                    logger.warning("occur exception: {}".format(e))
                finally:
                    e = None
                    del e

        self.have_log = True
        return cookie_data_list


class CookieParserGoogleChome(CookieParserBase):
    __doc__ = "负责解析google chrome 浏览器cookie数据"

    def get_local_state(self):
        """
        获取Local State文件路径
        :return: 文件全路径
        """
        s_path = "\\Google\\Chrome\\User Data\\Local State"
        s_local_state = os.environ["LOCALAPPDATA"] + s_path
        return s_local_state

    def get_cookie_path(self):
        """
               s_browser_name: 浏览器名称(Google Chrome, Microsoft Edge)
               s_host: 域名   例如： '.umeng.com'
        """
        s_cookie = "\\Google\\Chrome\\User Data\\Default\\Network\\Cookies"
        s_cookie_path = os.environ["LOCALAPPDATA"] + s_cookie
        return s_cookie_path

    def get_sql(self, host):
        sql = "select host_key,name,encrypted_value from cookies where host_key='%s'" % host
        return sql

    def get_browser_name(self):
        return "Chrome"

    def get_cookie_data(self, host):
        """
        根据Local State解析出加密key，根据key解密cookie数据
        :param host:
        :return:
        """
        cookie_data_list = list()
        s_cookie_path = self.get_cookie_path()
        if not os.path.exists(s_cookie_path):
            if self.have_log == False:
                logger.warning("The {} cookie files not found, {}".format(self.get_browser_name(), s_cookie_path))
                self.have_log = True
            return cookie_data_list
        sql = self.get_sql(host)
        s_local_state = self.get_local_state()
        try:
            with sqlite3.connect(s_cookie_path) as conn:
                p_cursor = conn.cursor()
                p_res = p_cursor.execute(sql).fetchall()
                p_cursor.close()
                key = self._CookieParserGoogleChome__pull_the_key(self._CookieParserGoogleChome__get_string(s_local_state))
                d_cookie = dict()
                for s_host_key, s_name, c_encrypted_value in p_res:
                    if c_encrypted_value[0[:3]] == b'v10':
                        d_cookie[s_name] = self._CookieParserGoogleChome__decrypt_string(key, c_encrypted_value)
                    else:
                        d_cookie[s_name] = CryptUnprotectData(c_encrypted_value)[1].decode()

                cookie_data_list.append(d_cookie)
        except Exception as e:
            try:
                logger.warning("occur exception: {}".format(e))
            finally:
                e = None
                del e

        return cookie_data_list

    def __get_string(self, s_local_state):
        with open(s_local_state, "r", encoding="utf-8") as f:
            s_encrtpted_key = json.load(f)["os_crypt"]["encrypted_key"]
        return s_encrtpted_key

    def __pull_the_key(self, base64_encrypted_key):
        c_encrypted_key_with_header = base64.b64decode(base64_encrypted_key)
        c_encrypted_key = c_encrypted_key_with_header[5[:None]]
        c_key = CryptUnprotectData(c_encrypted_key, None, None, None, 0)[1]
        return c_key

    def __decrypt_string(self, c_key, c_data):
        c_nonce, c_cipherbytes = c_data[3[:15]], c_data[15[:None]]
        aesgcm = AESGCM(c_key)
        c_plainbytes = aesgcm.decrypt(c_nonce, c_cipherbytes, None)
        s_plaintext = c_plainbytes.decode("utf-8")
        return s_plaintext


class CoolkieParserEdge(CookieParserGoogleChome):
    __doc__ = "负责解析Edge浏览器cookie数据 "

    def get_cookie_path(self):
        s_cookie = "\\Microsoft\\Edge\\User Data\\Default\\Network\\Cookies"
        s_cookie_path = os.environ["LOCALAPPDATA"] + s_cookie
        return s_cookie_path

    def get_local_state(self):
        s_path = "\\Microsoft\\Edge\\User Data\\Local State"
        s_local_state = os.environ["LOCALAPPDATA"] + s_path
        return s_local_state

    def get_browser_name(self):
        return "Edge"


def get_elk_data(host_list):
    """收集所有浏览器的elk数据"""
    data_dict = {'google_chrome':CookieParserGoogleChome(), 
     'edge':CoolkieParserEdge(), 
     'firefox':CookieParserFireFox()}
    total_data_dict = {}
    host_data_list = list()
    for key in data_dict:
        cookie_parser = data_dict.get(key)
        logger.info("Start get data for {} ...".format(key))
        host_data_list += cookie_parser.get_elk_data(host_list)
        logger.info("End get data for {} ...".format(key))

    total_data_dict[NODE_WEB_TOKEN] = host_data_list
    return total_data_dict


def save_elk_data(data_dict, file):
    try:
        json_string = json.dumps(data_dict)
        json_string = base64.b64encode(json_string.encode("utf-8"))
        with open(file, "wb") as f:
            f.write(json_string)
    except Exception as e:
        try:
            logging.error("save file exception: {}".format(e))
        finally:
            e = None
            del e


def init_logging():
    global logger
    logFilename = os.environ["TEMP"] + "\\devcon.log"
    logging.basicConfig(level=(logging.DEBUG),
      format="%(asctime)s-%(levelname)s-%(message)s",
      datefmt="%y-%m-%d %H:%M",
      filename=logFilename,
      filemode="w+")
    filehandler = logging.FileHandler(logFilename, encoding="utf-8")
    logging.getLogger().addHandler(filehandler)
    logger = logging.getLogger("devcon.log")


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python.exe output_file_path")
        sys.exit(1)
    init_logging()
    logger.info("App version: 2022-07-27-14-55")
    logger.info("Param: " + sys.argv[1])
    host_list = [
     '.dvdfab.cn', '.dvdfab.fr', '.dvdfab.at', '.dvdfab.co.jp', '.dvdfab.org', 
     '.streamfab.com', '.streamfab.jp', '.streamfab.de', '.streamfab.fr', 
     '.streamfab.tw']
    logger.info("Start get elk data ...")
    try:
        data_dic = get_elk_data(host_list)
    except Exception as e:
        try:
            logger.error("Get elk data exception: {}".format(e))
        finally:
            e = None
            del e

    logger.info("Start save elk data ...")
    file = sys.argv[1]
    save_elk_data(data_dic, file)
    logger.info("End")
