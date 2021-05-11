import scrapy
import logging
import json

from scrapy.loader import ItemLoader
from scrapy.http import FormRequest
from scrapy.exceptions import CloseSpider
from ..items import FbcrawlItem, CommentsItem, parse_date, parse_date2
from datetime import datetime, timedelta
from scrapy.utils.response import open_in_browser


class FacebookSpider(scrapy.Spider):
    '''
    Parse FB pages (needs credentials)
    '''
    name = 'fb'
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['source', 'shared_from', 'date', 'text', \
                               'reactions', 'likes', 'ahah', 'love', 'wow', \
                               'sigh', 'grrr', 'comments', 'post_id', 'url'],
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1
    }

    def __init__(self, *args, **kwargs):
        # turn off annoying logging, set LOG_LEVEL=DEBUG in settings.py to see more logs
        logger = logging.getLogger('scrapy.middleware')
        logger.setLevel(logging.WARNING)

        super().__init__(*args, **kwargs)

        # email & pass need to be passed as attributes!
        # if 'email' not in kwargs or 'password' not in kwargs:
        #     raise AttributeError('You need to provide valid email and password:\n'
        #                          'scrapy fb -a email="EMAIL" -a password="PASSWORD"')
        # else:
        #     self.logger.info('Email and password provided, will be used to log in')

        if 'keyword' not in kwargs:
            self.keyword = ''
        else:
            self.keyword = kwargs['keyword'].lower()

        if 'campaign' in kwargs:
            self.campaign = kwargs['campaign']
        else:
            self.campaign = "test"

        # page name parsing (added support for full urls)
        if 'page' in kwargs:
            if self.page.find('/groups/') != -1:
                self.group = 1
            else:
                self.group = 0
            if self.page.find('https://www.facebook.com/') != -1:
                self.page = self.page[25:]
            elif self.page.find('https://mbasic.facebook.com/') != -1:
                self.page = self.page[28:]
            elif self.page.find('https://m.facebook.com/') != -1:
                self.page = self.page[23:]

        # parse date
        if 'starttime' not in kwargs:
            self.logger.info('Date attribute not provided, scraping date set to 2004-02-04 (fb launch date)')
            self.start_time = datetime(2004, 2, 4)
        else:
            self.start_time = datetime.strptime(kwargs['starttime'], '%Y-%m-%d')
            self.logger.info('Date attribute provided, fbcrawl will stop crawling at {}'.format(kwargs['starttime']))
        self.year = self.start_time.year

        if 'endtime' not in kwargs:
            self.logger.info('Date attribute not provided, scraping date set to now')
            self.end_time = datetime.now()
        else:

            self.end_time = datetime.strptime(kwargs['endtime'], '%Y-%m-%d') + timedelta(days=1)
            self.logger.info('Date attribute provided, fbcrawl will start crawling at {}'.format(kwargs['endtime']))

        # parse lang, if not provided (but is supported) it will be guessed in parse_home
        if 'lang' not in kwargs:
            self.logger.info('Language attribute not provided, fbcrawl will try to guess it from the fb interface')
            self.logger.info('To specify, add the lang parameter: scrapy fb -a lang="LANGUAGE"')
            self.logger.info('Currently choices for "LANGUAGE" are: "en", "es", "fr", "it", "pt"')
            self.lang = 'vn'
        elif self.lang == 'en' or self.lang == 'es' or self.lang == 'fr' or self.lang == 'it' or self.lang == 'pt':
            self.logger.info('Language attribute recognized, using "{}" for the facebook interface'.format(self.lang))
        else:
            self.logger.info('Lang "{}" not currently supported'.format(self.lang))
            self.logger.info('Currently supported languages are: "en", "es", "fr", "it", "pt"')
            self.logger.info('Change your interface lang from facebook settings and try again')
            raise AttributeError('Language provided not currently supported')

        # max num of posts to crawl
        if 'max' not in kwargs:
            self.max = int(10e5)
        else:
            self.max = int(kwargs['max'])

        # current year, this variable is needed for proper parse_page recursion
        self.k = datetime.now().year
        # count number of posts, used to enforce DFS and insert posts orderly in the csv
        self.count = 0
        self.stop = 0
        self.start_urls = ['https://mbasic.facebook.com']

    def parse(self, response):

        return FormRequest.from_response(
            response,
            formxpath='//form[contains(@action, "login")]',
            formdata={'email': self.email, 'pass': self.password},
            callback=self.parse_home
        )

    def parse_home(self, response):
        '''
        This method has multiple purposes:
        1) Handle failed logins due to facebook 'save-device' redirection
        2) Set language interface, if not already provided
        3) Navigate to given page 
        '''
        # handle 'save-device' redirection
        # open_in_browser(response)
        if response.xpath("//div/a[contains(@href,'save-device')]"):
            self.logger.info('Going through the "save-device" checkpoint')
            return FormRequest.from_response(
                response,
                formdata={'name_action_selected': 'dont_save'},
                callback=self.parse_home
            )

        # set language interface
        if self.lang == '_':
            if response.xpath("//input[@placeholder='Search Facebook']"):
                self.logger.info('Language recognized: lang="en"')
                self.lang = 'en'
            elif response.xpath("//input[@placeholder='Buscar en Facebook']"):
                self.logger.info('Language recognized: lang="es"')
                self.lang = 'es'
            elif response.xpath("//input[@placeholder='Rechercher sur Facebook']"):
                self.logger.info('Language recognized: lang="fr"')
                self.lang = 'fr'
            elif response.xpath("//input[@placeholder='Cerca su Facebook']"):
                self.logger.info('Language recognized: lang="it"')
                self.lang = 'it'
            elif response.xpath("//input[@placeholder='Pesquisa no Facebook']"):
                self.logger.info('Language recognized: lang="pt"')
                self.lang = 'pt'
            else:
                raise AttributeError('Language not recognized\n'
                                     'Change your interface lang from facebook '
                                     'and try again')

        # navigate to provided page
        href = response.urljoin(self.page).replace("/login", "").replace("/checkpoint", "")
        self.logger.info('Scraping facebook page {}'.format(href))
        return scrapy.Request(url=href, callback=self.parse_page, meta={'index': 1})

    def parse_page(self, response):
        post_nums = 0
        # from scrapy.utils.response import open_in_browser
        # open_in_browser(response)
        # select all posts
        for post in response.xpath("//article[contains(@data-ft,'top_level_post_id')]"):
            post_nums += 1
            many_features = post.xpath('./@data-ft').get()
            date = []
            date.append(many_features)
            date = parse_date(date, {'lang': self.lang})
            post_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S') if date is not None else date

            if post_date is None:
                date_string = post.xpath('.//abbr/text()').get()
                date = parse_date2([date_string], {'lang': self.lang})
                post_date = date if date is not None else None

            if self.end_time < post_date:
                continue

            # if 'start_time' argument is reached stop crawling
            if self.start_time > post_date:
                self.stop = 1
                break
                # raise CloseSpider('Reached date: {}'.format(self.date))

            new = ItemLoader(item=FbcrawlItem(), selector=post)
            if abs(self.count) + 1 > self.max:
                raise CloseSpider('Reached max num of post: {}. Crawling finished'.format(abs(self.count)))
            self.logger.info('Parsing post n = {}, post_date = {}'.format(abs(self.count) + 1, date))

            new.add_value('campaign', self.campaign)
            # count = 0
            # for comments_num in response.xpath('//article/footer/div[2]/a[1]/text()').extract():
            #     # print(comments_num)
            #     if comments_num.rfind('bình luậ') != -1:
            #         comments_num = comments_num.rstrip(' bình luậ')
            #     count += 1
            #     if count == post_nums:
            #         new.add_xpath('comments_num', comments_num)
            #         break
            new.add_value('date', date)
            new.add_xpath('post_id', './@data-ft')
            new.add_xpath('url', ".//a[contains(@href,'footer')]/@href")
            post_id = self.id_strip(post.xpath("./@data-ft").extract())
            # returns full post-link in a list
            post = post.xpath(".//a[contains(@href,'footer')]/@href").extract()
            temp_post = response.urljoin(post[0])
            self.count -= 1
            yield scrapy.Request(temp_post, self.parse_post, priority=self.count,
                                 meta={'item': new, 'index': 1, 'post_id': post_id})

            # load following page, try to click on "more"
        # after few pages have been scraped, the "more" link might disappears
        # if not present look for the highest year not parsed yet
        # click once on the year and go back to clicking "more"

        # if not self.stop:
        #     # new_page is different for groups
        #     if self.group == 1:
        #         new_page = response.xpath("//div[contains(@id,'stories_container')]/div[2]/a/@href").extract()
        #     else:
        #         new_page = response.xpath(
        #             "//div[2]/a[contains(@href,'timestart=') and not(contains(text(),'ent')) and not(contains(text(),number()))]/@href").extract()
        #         # this is why lang is needed                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^
        #
        #     if not new_page:
        #         self.logger.info('[!] "more" link not found, will look for a "year" link')
        #         # self.k is the year link that we look for
        #         if 'flag' in response.meta:
        #             if response.meta['flag'] == self.k and self.k >= self.year:
        #                 xpath = "//div/a[contains(@href,'time') and contains(text(),'" + str(self.k) + "')]/@href"
        #                 new_page = response.xpath(xpath).extract()
        #                 if new_page:
        #                     new_page = response.urljoin(new_page[0])
        #                     self.k -= 1
        #                     self.logger.info('Found a link for year "{}", new_page = {}'.format(self.k, new_page))
        #                     yield scrapy.Request(new_page, callback=self.parse_page, meta={'flag': self.k})
        #                 else:
        #                     while not new_page:  # sometimes the years are skipped this handles small year gaps
        #                         self.logger.info(
        #                             'Link not found for year {}, trying with previous year {}'.format(self.k,
        #                                                                                               self.k - 1))
        #                         self.k -= 1
        #                         if self.k < self.year:
        #                             raise CloseSpider('Reached date: {}. Crawling finished'.format(self.date))
        #                         xpath = "//div/a[contains(@href,'time') and contains(text(),'" + str(
        #                             self.k) + "')]/@href"
        #                         new_page = response.xpath(xpath).extract()
        #                     self.logger.info('Found a link for year "{}", new_page = {}'.format(self.k, new_page))
        #                     new_page = response.urljoin(new_page[0])
        #                     self.k -= 1
        #                     yield scrapy.Request(new_page, callback=self.parse_page, meta={'flag': self.k})
        #             else:
        #                 self.logger.info('Crawling has finished with no errors!')
        #     else:
        #         new_page = response.urljoin(new_page[0])
        #         if 'flag' in response.meta:
        #             self.logger.info('Page scraped, clicking on "more"! new_page = {}'.format(new_page))
        #             yield scrapy.Request(new_page, callback=self.parse_page, meta={'flag': response.meta['flag']})
        #         else:
        #             self.logger.info('First page scraped, clicking on "more"! new_page = {}'.format(new_page))
        #             yield scrapy.Request(new_page, callback=self.parse_page, meta={'flag': self.k})

    def parse_post(self, response):
        post_id = response.meta['post_id']
        try:
            new = ItemLoader(item=FbcrawlItem(), response=response, parent=response.meta['item'])
            new.context['lang'] = self.lang
            new.add_xpath('source',
                          "//td/div/h3/strong/a/text() | //span/strong/a/text() | //div/div/div/a[contains(@href,'post_id')]/strong/text()")
            new.add_xpath('shared_from',
                          '//div[contains(@data-ft,"top_level_post_id") and contains(@data-ft,\'"isShare":1\')]/div/div[3]//strong/a/text()')
            new.add_xpath('text', '//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()')

            text = response.xpath(
                '//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()').extract()
            fulltext = "".join(text).lower()
            if self.keyword not in fulltext:
                logging.info("Not includes keyword. Post discarded")
                return

            # yield new.load_item()
            # check reactions for old posts
            # open_in_browser(response)
            check_reactions = response.xpath("//a[contains(@href,'reaction/profile')]/div/div/text()").get()
            if not check_reactions:
                yield new.load_item()
            else:
                try:
                    new.add_xpath('reactions', "//a[contains(@href,'reaction/profile')]/div/div/text()")
                    reactions = response.xpath(
                        "//div[contains(@id,'sentence')]/a[contains(@href,'reaction/profile')]/@href")
                    reactions = response.urljoin(reactions[0].extract())
                    yield scrapy.Request(reactions, callback=self.parse_reactions, meta={'item': new}, errback=self.save_item)
                except:
                    print('except')
                    yield new.load_item()
        except:
            pass

        # load replied-to comments pages
        # select nested comment one-by-one matching with the index: response.meta['index']
        path = './/div[string-length(@class) = 2 and count(@id)=1 and contains("0123456789", substring(@id,1,1)) and .//div[contains(@id,"comment_replies")]]' + '[' + str(
            response.meta['index']) + ']'
        group_flag = response.meta['group'] if 'group' in response.meta else None

        for reply in response.xpath(path):
            source = reply.xpath('.//h3/a/text()').extract()
            answer = reply.xpath('.//a[contains(@href,"repl")]/@href').extract()
            ans = response.urljoin(answer[::-1][0])
            # self.logger.info('{} nested comment'.format(str(response.meta['index'])))
            yield scrapy.Request(ans,
                                 callback=self.parse_reply,
                                 priority=1000,
                                 meta={'reply_to': source,
                                       'url': response.url,
                                       'index': response.meta['index'],
                                       'flag': 'init',
                                       'group': group_flag,
                                       'post_id': post_id})
        # load regular comments
        if not response.xpath(path):  # prevents from exec
            path2 = './/div[string-length(@class) = 2 and count(@id)=1 and contains("0123456789", substring(@id,1,1)) and not(.//div[contains(@id,"comment_replies")])]'
            for i, reply in enumerate(response.xpath(path2)):
                text = response.xpath('.//div[h3]/div[1]//text()').extract()
                if text is None or not text:
                    continue
                self.logger.info('{} regular comment'.format(i + 1))
                new = ItemLoader(item=CommentsItem(), selector=reply)
                new.context['lang'] = self.lang
                new.add_value('post_id', post_id)
                new.add_xpath('date', './/abbr/text()')
                new.add_xpath('text', './/div[h3]/div[1]//text()')
                yield new.load_item()

        # new comment page
        if not response.xpath(path):
            # for groups
            next_xpath = './/div[contains(@id,"see_next")]'
            prev_xpath = './/div[contains(@id,"see_prev")]'
            if not response.xpath(next_xpath) or group_flag == 1:
                for next_page in response.xpath(prev_xpath):
                    new_page = next_page.xpath('.//@href').extract()
                    new_page = response.urljoin(new_page[0])
                    # self.logger.info('New page to be crawled {}'.format(new_page))
                    yield scrapy.Request(new_page,
                                         callback=self.parse_post,
                                         meta={'index': 1,
                                               'group': 1,
                                               'post_id': post_id})
            else:
                for next_page in response.xpath(next_xpath):
                    new_page = next_page.xpath('.//@href').extract()
                    new_page = response.urljoin(new_page[0])
                    # self.logger.info('New page to be crawled {}'.format(new_page))
                    yield scrapy.Request(new_page,
                                         callback=self.parse_post,
                                         meta={'index': 1,
                                               'group': group_flag,
                                               'post_id': post_id})

    def parse_reactions(self, response):
        try:
            new = ItemLoader(item=FbcrawlItem(), response=response, parent=response.meta['item'])
            new.context['lang'] = self.lang
            new.add_xpath('like', "//a[contains(@href,'reaction_type=1')]/span/text()")
            new.add_xpath('haha', "//a[contains(@href,'reaction_type=4')]/span/text()")
            new.add_xpath('love', "//a[contains(@href,'reaction_type=2')]/span/text()")
            new.add_xpath('wow', "//a[contains(@href,'reaction_type=3')]/span/text()")
            new.add_xpath('sad', "//a[contains(@href,'reaction_type=7')]/span/text()")
            new.add_xpath('angry', "//a[contains(@href,'reaction_type=8')]/span/text()")
            new.add_xpath('care', "//a[contains(@href,'reaction_type=16')]/span/text()")
            yield new.load_item()
        except:
            new = ItemLoader(item=FbcrawlItem(), parent=response.meta['item'])
            new.context['lang'] = self.lang
            yield new.load_item()

    def parse_reply(self, response):
        post_id = response.meta['post_id']
        if response.meta['flag'] == 'init':
            # parse root comment
            for root in response.xpath(
                    '//div[contains(@id,"root")]/div/div/div[count(@id)!=1 and contains("0123456789", substring(@id,1,1))]'):
                text = response.xpath('.//div[h3]/div[1]//text()').extract()
                if text is None or not text:
                    continue
                new = ItemLoader(item=CommentsItem(), selector=root)
                new.context['lang'] = self.lang
                new.add_xpath('text', './/div[1]//text()')
                new.add_xpath('date', './/abbr/text()')
                new.add_value('post_id', post_id)
                yield new.load_item()

            back = response.xpath('//div[contains(@id,"comment_replies_more_1")]/a/@href').extract()
            if back:
                # self.logger.info('Back found, more nested comments')
                back_page = response.urljoin(back[0])
                yield scrapy.Request(back_page,
                                     callback=self.parse_reply,
                                     priority=1000,
                                     meta={'reply_to': response.meta['reply_to'],
                                           'flag': 'back',
                                           'url': response.meta['url'],
                                           'index': response.meta['index'],
                                           'group': response.meta['group'],
                                           'post_id': post_id})

            else:
                next_reply = response.meta['url']
                # self.logger.info(
                #     'Nested comments crawl finished, heading to proper page: {}'.format(response.meta['url']))
                yield scrapy.Request(next_reply,
                                     callback=self.parse_post,
                                     meta={'index': response.meta['index'] + 1,
                                           'group': response.meta['group'],
                                           'post_id': post_id})

        elif response.meta['flag'] == 'back':
            next_reply = response.meta['url']
            # self.logger.info('Nested comments crawl finished, heading to home page: {}'.format(response.meta['url']))
            yield scrapy.Request(next_reply,
                                 callback=self.parse_post,
                                 meta={'index': response.meta['index'] + 1,
                                       'group': response.meta['group'],
                                       'post_id': post_id})

    def id_strip(self, post_id):
        d = json.loads(post_id[::-1][0])  # nested dict of features
        return str(d['top_level_post_id'])

    def save_item(self, response):
        new = response.request.meta['item']
        new.context['lang'] = self.lang
        yield new.load_item()