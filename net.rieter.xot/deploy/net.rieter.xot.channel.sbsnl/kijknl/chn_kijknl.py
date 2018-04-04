import datetime

import mediaitem
import chn_class

from streams.m3u8 import M3u8
from regexer import Regexer
from helpers.jsonhelper import JsonHelper
from helpers.datehelper import DateHelper
from logger import Logger
from urihandler import UriHandler
# from helpers.languagehelper import LanguageHelper


class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """

    def __init__(self, channelInfo):
        """Initialisation of the class.

        Arguments:
        channelInfo: ChannelInfo - The channel info object to base this channel on.

        All class variables should be instantiated here and this method should not
        be overridden by any derived classes.

        """

        chn_class.Channel.__init__(self, channelInfo)

        # ============== Actual channel setup STARTS here and should be overwritten from derived classes ===============
        # setup the urls
        self.baseUrl = "https://www.kijk.nl"
        # Just retrieve a single page with 500 items (should be all)
        self.mainListUri = "https://api.kijk.nl/v1/default/sections/programs-abc-0123456789abcdefghijklmnopqrstuvwxyz?limit=350&offset=0"

        self.__channelId = self.channelCode
        if self.channelCode == 'veronica':
            self.noImage = "veronicaimage.png"
            self.__channelId = "veronicatv"

        elif self.channelCode == 'sbs':
            self.noImage = "sbs6image.png"
            self.__channelId = "sbs6"

        elif self.channelCode == 'sbs9':
            self.noImage = "sbs9image.png"

        elif self.channelCode == 'net5':
            self.noImage = "net5image.png"

        else:
            self.noImage = "kijkimage.png"

        # setup the main parsing data
        self._AddDataParser("https://api.kijk.nl/v1/default/sections/programs-abc",
                            name="Mainlist Json", json=True,
                            preprocessor=self.AddOthers,
                            parser=("items", ), creator=self.CreateJsonEpisodeItem)

        self._AddDataParser("#lastweek",
                            name="Last week listing", json=True,
                            preprocessor=self.ListDates)

        self._AddDataParser("https://api.kijk.nl/v2/templates/page/missed/all/",
                            name="Day listing", json=True, preprocessor=self.ExtractDayItems)

        self._AddDataParser("https://api.kijk.nl/v1/default/searchresultsgrouped",
                            name="VideoItems Json", json=True,
                            parser=(), creator=self.CreateJsonSearchItem)

        self._AddDataParser("https://api.kijk.nl/v1/default/sections/series",
                            name="VideoItems Json", json=True,
                            parser=("items", ), creator=self.CreateJsonVideoItem)

        self._AddDataParser("https://api.kijk.nl/v2/default/sections/popular",
                            name="Popular items Json", json=True,
                            parser=("items", ), creator=self.CreateJsonPopularItem)

        self._AddDataParser("https://embed.kijk.nl/",
                            updater=self.UpdateJsonVideoItem)

        #===============================================================================================================
        # non standard items

        #===============================================================================================================
        # Test cases:
        #  Piets Weer: no clips
        #  Achter gesloten deuren: seizoenen
        #  Wegmisbruikers: episodes and clips and both pages
        #  Utopia: no clips

        # ====================================== Actual channel setup STOPS here =======================================
        return

    def AddOthers(self, data):
        """Performs pre-process actions for data processing/

        Arguments:
        data : string - the retrieve data that was loaded for the current item and URL.

        Returns:
        A tuple of the data and a list of MediaItems that were generated.


        Accepts an data from the ProcessFolderList method, BEFORE the items are
        processed. Allows setting of parameters (like title etc) for the channel.
        Inside this method the <data> could be changed and additional items can
        be created.

        The return values should always be instantiated in at least ("", []).

        """

        Logger.Info("Performing Pre-Processing")
        items = []

        others = mediaitem.MediaItem("\b.: Populair :.", "https://api.kijk.nl/v2/default/sections/popular_PopularVODs?offset=0")
        items.append(others)

        days = mediaitem.MediaItem("\b.: Deze week :.", "#lastweek")
        items.append(days)

        search = mediaitem.MediaItem("\b.: Zoeken :.", "searchSite")
        search.complete = True
        search.icon = self.icon
        search.thumb = self.noImage
        search.dontGroup = True
        search.HttpHeaders = {"X-Requested-With": "XMLHttpRequest"}
        items.append(search)

        Logger.Debug("Pre-Processing finished")
        return data, items

    # noinspection PyUnusedLocal
    def SearchSite(self, url=None):  # @UnusedVariable
        """Creates an list of items by searching the site

        Returns:
        A list of MediaItems that should be displayed.

        This method is called when the URL of an item is "searchSite". The channel
        calling this should implement the search functionality. This could also include
        showing of an input keyboard and following actions.

        """

        url = "https://api.kijk.nl/v1/default/searchresultsgrouped?search=%s"
        return chn_class.Channel.SearchSite(self, url)

    def ListDates(self, data):
        items = []

        # https://api.kijk.nl/v2/templates/page/missed/all/20180201
        days = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
        for i in range(0, 7):
            date = datetime.datetime.now() - datetime.timedelta(days=i)
            url = "https://api.kijk.nl/v2/templates/page/missed/all/{0}{1:02d}{2:02d}".format(date.year, date.month, date.day)
            if i == 0:
                # title = LanguageHelper.GetLocalizedString(LanguageHelper.Today)
                title = "Vandaag"
            elif i == 1:
                # title = LanguageHelper.GetLocalizedString(LanguageHelper.Yesterday)
                title = "Gisteren"
            elif i == 2:
                # title = LanguageHelper.GetLocalizedString(LanguageHelper.DayBeforeYesterday)
                title = "Eergisteren"
            else:
                day_name = days[date.weekday()]
                title = day_name

            date_item = mediaitem.MediaItem(title, url)
            date_item.SetDate(date.year, date.month, date.day)
            items.append(date_item)

        Logger.Debug("Pre-Processing finished")
        return data, items

    def ExtractDayItems(self, data):
        items = []
        json = JsonHelper(data)
        page_data = json.GetValue('components', fallback={})
        for page_item in page_data:
            if page_item['type'] != 'video_list':
                continue

            page_items = page_item['data']['items']
            for item in page_items:
                video_item = self.CreateJsonVideoItem(item, prepend_serie=True)
                if video_item:
                    items.append(video_item)
                else:
                    pass

        return data, items

    def CreateJsonSearchItem(self, resultSet):
        if 'type' in resultSet:
            item_type = resultSet['type']
            if item_type == 'series':
                return self.CreateJsonEpisodeItem(resultSet)
            elif item_type == 'episode' or item_type == 'clip':
                return self.CreateJsonVideoItem(resultSet, prepend_serie=True)
        return None

    def CreateJsonEpisodeItem(self, resultSet):
        Logger.Trace(resultSet)

        channelId = resultSet["channel"]
        if self.__channelId and channelId != self.__channelId:
            return None

        title = resultSet["title"]
        url = "https://api.kijk.nl/v1/default/sections/series-%(id)s_Episodes-season-0?limit=100&offset=0" % resultSet
        item = mediaitem.MediaItem(title, url)
        item.description = resultSet.get("synopsis", None)

        if "retina_image_pdp_header" in resultSet["images"]:
            item.fanart = resultSet["images"]["retina_image_pdp_header"]
        if "retina_image" in resultSet["images"]:
            item.thumb = resultSet["images"]["retina_image"]

        return item

    def CreateJsonPopularItem(self, resultSet):
        item = self.CreateJsonVideoItem(resultSet, prepend_serie=True)
        if item is None:
            return None

        item.name = "%s - %s" % (item.name, resultSet["seriesTitle"])
        return item

    def CreateJsonVideoItem(self, resultSet, prepend_serie=False):
        Logger.Trace(resultSet)

        if not resultSet.get("available", True):
            Logger.Warning("Item not available: %s", resultSet)
            return None

        item = self.CreateJsonEpisodeItem(resultSet)
        if item is None:
            return None

        if prepend_serie and 'seriesTitle' in resultSet:
            item.name = "{0} - {1}".format(item.name, resultSet['seriesTitle'])
        elif 'seriesTitle' in resultSet:
            item.name = resultSet['seriesTitle']

        item.type = "video"
        item.url = "https://embed.kijk.nl/api/video/%(id)s?id=kijkapp" % resultSet

        if 'subtitle' in resultSet:
            item.name = "{0} - {1}".format(item.name, resultSet['subtitle'])

        if "date" in resultSet:
            date = resultSet["date"].split("+")[0]
            # 2016-12-25T17:58:00+01:00
            timeStamp = DateHelper.GetDateFromString(date, "%Y-%m-%dT%H:%M:%S")
            item.SetDate(*timeStamp[0:6])

        return item

    def UpdateJsonVideoItem(self, item):
        data = UriHandler.Open(item.url, proxy=self.proxy)
        json = JsonHelper(data)
        m3u8Url = json.GetValue("playlist")

        if m3u8Url != "https://embed.kijk.nl/api/playlist/.m3u8":
            part = item.CreateNewEmptyMediaPart()
            for s, b in M3u8.GetStreamsFromM3u8(m3u8Url, self.proxy, appendQueryString=True):
                if "_enc_" in s:
                    Logger.Warning("Found encrypted stream. Skipping %s", s)
                    continue

                item.complete = True
                # s = self.GetVerifiableVideoUrl(s)
                part.AppendMediaStream(s, b)
            return item

        Logger.Warning("No M3u8 data found. Falling back to BrightCove")
        videoId = json.GetValue("vpakey")
        # videoId = json.GetValue("videoId") -> Not all items have a videoId
        url = "https://embed.kijk.nl/video/%s?width=868&height=491" % (videoId,)
        referer = "https://embed.kijk.nl/video/%s" % (videoId,)
        part = item.CreateNewEmptyMediaPart()

        # First try the new BrightCove JSON
        data = UriHandler.Open(url, proxy=self.proxy, referer=referer)
        brightCoveRegex = '<video[^>]+data-video-id="(?<videoId>[^"]+)[^>]+data-account="(?<videoAccount>[^"]+)'
        brightCoveData = Regexer.DoRegex(Regexer.FromExpresso(brightCoveRegex), data)
        if brightCoveData:
            Logger.Info("Found new BrightCove JSON data")
            brightCoveUrl = 'https://edge.api.brightcove.com/playback/v1/accounts/%(videoAccount)s/videos/%(videoId)s' % \
                            brightCoveData[0]
            headers = {
                "Accept": "application/json;pk=BCpkADawqM3ve1c3k3HcmzaxBvD8lXCl89K7XEHiKutxZArg2c5RhwJHJANOwPwS_4o7UsC4RhIzXG8Y69mrwKCPlRkIxNgPQVY9qG78SJ1TJop4JoDDcgdsNrg"}
            brightCoveData = UriHandler.Open(brightCoveUrl, proxy=self.proxy,
                                             additionalHeaders=headers)
            brightCoveJson = JsonHelper(brightCoveData)
            streams = filter(lambda d: d["container"] == "M2TS", brightCoveJson.GetValue("sources"))
            if streams:
                # noinspection PyTypeChecker
                streamUrl = streams[0]["src"]
                for s, b in M3u8.GetStreamsFromM3u8(streamUrl, self.proxy):
                    item.complete = True
                    part.AppendMediaStream(s, b)
                return item
