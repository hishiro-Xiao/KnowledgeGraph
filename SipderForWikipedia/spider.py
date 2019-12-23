import json
import random
from time import sleep

import requests
from pyquery import PyQuery as pq


class Spider:
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 "
        "Safari/535.20",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 "
        "LBBROWSER",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 "
        "LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
        "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; "
        "360SE)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) "
        "Version/5.0.2 "
        "Mobile/8C148 Safari/6533.18.5",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
    ]
    header = {
        'User-Agent': USER_AGENTS[random.randint(0, 12)],
    }
    # 维基百科的根目录
    root_url = 'https://en.wikipedia.org'
    weapons_info_lists = []

    # 获取一个网页的pyquery对象
    def get_web_content_as_pyquery(self, u: str):
        try:
            r = requests.get(u, self.header)

            # if r.status_code == 200:
            #     sleep(1)
            #     r.encoding = 'utf-8'
            #     return pq(r.text)
            # else:
            #     self.save_comtent('weapons_info_lists.json', self.weapons_info_lists)
            #     exit('Connection Error')

            r.encoding = 'utf-8'
            return pq(r.text, parser='html')
        except:
            # 如果发生异常，及时保存当前已经保存的信息
            print('An error happened.')
            json_str = json.dumps(self.weapons_info_lists)
            self.save_comtent('weapon_info_lists_error.json', json_str)
            return False
        

    # 将指定对象保存到filepath文件中（需指定文件类型）
    def save_comtent(self, filepath: str, content: str, append='False'):
        f = open(filepath, 'w', 100, 'utf-8')
        f.write(str(content))
        f.close()

    # 获取所有的武器信息
    # 维基百科按照武器类型对所有武器分了类，所以第一步是获取各个类别的链接type_lists
    # type_lists中保存着哥各个类别武器的链接，每次从中获取一个链接，获取某个类别的所有武器的链接weapons_lists
    # 每次从weapons_lists中获取一个武器的链接，获取该武器的页面，提取页面信息
    def get_type_lists(self):
        url = 'https://en.wikipedia.org/wiki/Lists_of_weapons'
        html = self.get_web_content_as_pyquery(url)

        # 获取按照武器类型分类一栏中的所有链接，利用pyquery对DOM元素进行获取
        type_lists = []
        for a in html("#mw-content-text div h2:eq(1) +ul:first li a").items():
            type_lists.append(self.root_url + a.attr('href'))

        # for u in type_lists:
        #     self.get_weapon_lists_from(u)

    # 从一个武器条目中获取武器的信息（武器信息是存放在表格中的）
    def get_weapon_info(self, u: str):
        html = self.get_web_content_as_pyquery(u)
        if html == False:
            return False
        # info_table = html('#mw-content-text').children('div').children('table.infobox.vcard tbody')
        info_table = html('#mw-content-text').children('div').children('table.infobox').children('tbody')

        # 从表格中对数据进行读取并格式化
        weapon_name = info_table('tr:first').text()
        # weapon_name = html('#mw-content-text').children('div').children('table.infobox').children('caption').text()
        if weapon_name == '':
            return None

        weapon_info = {}
        for info in info_table('tr:gt(1)').items():
            # 如果没有td标签，说明是标题
            if info('th').text() != '' and info('td').text() != '':
                weapon_info[info('th').text()] = info('td').text()
        return {weapon_name: weapon_info}

    # 从武器类型的列表中，读取每一个武器的条目
    # 注：维基百科中,有些页面是ul和li放置一条信息，有些是tr和td放置，因此要做分类处理
    # 我一条条看了一下，只有三个页面是列表，其他都是表格，这就好办了
    def get_weapon_lists_from(self, u: str):
        type_name = u[u.index('List'):]
        html = self.get_web_content_as_pyquery(u)
        # 原本是html('#mw-content-text').children('div').children('ul').find('li a')
        # 改称下面是式子是因为有些条目是这样的：导弹link1（另见对空武器link2）
        # 在这种情况下，原本的式子会获取两个链接，所以改成每次只从li中拿第一个链接，防止以上情况的发生
        d = html('#mw-content-text').children('div').children('ul').find('li').find('a:first')

        # 存放某一种武器的全部武器链接
        weapon_lists = []
        for a in d.items():
            weapon_lists.append(self.root_url + a.attr('href'))
        # json_str = json.dumps(weapon_lists)
        print('Type of weapon: ' + type_name + ' have ' + str(len(weapon_lists)) + ' entries')

        for weapon in weapon_lists:
            weapon_info = self.get_weapon_info(weapon)
            if weapon_info == False:
                continue
            if weapon_info is not None:
                self.weapons_info_lists.append(weapon_info)
            print(str(weapon_lists.index(weapon)) + ' has been processed')

        json_str = json.dumps(self.weapons_info_lists)

        self.save_comtent(type_name + '.json', json_str)
        print(type_name + ' completed.')

    # 从按照表格存放武器条目的页面中爬取数据
    # 和上面仅仅是查询式的区别，其他完全一样，但是如何区分两种页面没有时间写了，所以就分开写
    def get_weapon_lists_from_2(self, u: str):
        # 该武器类型
        type_name = u[u.index('List'):]
        html = self.get_web_content_as_pyquery(u)
        d = html('#mw-content-text .wikitable tr').find('td:nth-child(1) a')
        # d = html('#mw-content-text .wikitable tr').find('td:eq(0)')

        weapon_list = []
        for a in d.items():
            weapon_list.append(self.root_url + a.attr('href'))
        
        self.save_comtent('link.json', json.dumps(weapon_list))
        print('Type of weapon: ' + type_name + ' have ' + str(len(weapon_list)) + ' entries')

        for weapon in weapon_list:
            weapon_info = self.get_weapon_info(weapon)
            if weapon_info == False:
                continue
            if weapon_info is not None:
                self.weapons_info_lists.append(weapon_info)
            print(str(weapon_list.index(weapon)) + ' has been processed')

        json_str = json.dumps(self.weapons_info_lists)

        self.save_comtent(type_name + '.json', json_str)
        print(type_name + ' completed.')


if __name__ == '__main__':

    # try:
    #      spider = Spider()
    #      spider.get_weapon_lists_from('https://en.wikipedia.org/wiki/List_of_anti-aircraft_weapons')
    #      # spider.get_weapon_lists_from_2('https://en.wikipedia.org/wiki/List_of_anti-aircraft_weapons')
    # except:
    #     spider.save_comtent('last_save_content.json', json.dumps(spider.weapons_info_lists))
   
    spider = Spider()
    # spider.get_weapon_lists_from('https://en.wikipedia.org/wiki/List_of_militaries_by_country')
    spider.get_weapon_lists_from_2('https://en.wikipedia.org/wiki/List_of_modern_armament_manufacturers')
