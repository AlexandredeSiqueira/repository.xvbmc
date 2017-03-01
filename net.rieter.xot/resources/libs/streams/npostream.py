#===============================================================================
# LICENSE Retrospect-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================
import os
import time

from helpers.jsonhelper import JsonHelper
from streams.m3u8 import M3u8
from helpers.subtitlehelper import SubtitleHelper
from streams.mms import Mms
from urihandler import UriHandler
from logger import Logger
from regexer import Regexer
from proxyinfo import ProxyInfo


class NpoStream:
    def __init__(self):
        pass

    @staticmethod
    def GetStreamsFromNpo(url, streamId, cacheDir, proxy=None, headers=None):
        # type: (Union[str, None], str, str, ProxyInfo, Dict[str, str]) -> List[Tuple[str, int]]
        """ Retrieve NPO Player Live streams from a different number of stream urls.

        @param url:               (String) The url to download
        @param cacheDir:          (String) The cache dir where to find the 'uzg-i.js' file.
        @param headers:           (dict) Possible HTTP Headers
        @param proxy:             (Proxy) The proxy to use for opening

        Can be used like this:

            part = item.CreateNewEmptyMediaPart()
            for s, b in NpoStream.GetStreamsFromNpo(m3u8Url, self.proxy):
                item.complete = True
                # s = self.GetVerifiableVideoUrl(s)
                part.AppendMediaStream(s, b)

        """

        if url:
            Logger.Info("Determining streams for url: %s", url)
        elif streamId:
            Logger.Info("Determining streams for VideoId: %s", streamId)
        else:
            Logger.Error("No url or streamId specified!")
            return []

        results = []
        token = NpoStream.GetNpoToken(proxy, cacheDir)

        # first try M3U8, the others
        streamUrls = [
            "http://ida.omroep.nl/odi/?prid=%s&puboptions=adaptive&adaptive=yes&part=1&token=%s" % (streamId, token,),
            "http://ida.omroep.nl/odi/?prid=%s&puboptions=h264_bb,h264_sb,h264_std&adaptive=no&part=1&token=%s" % (streamId, token,)
        ]
        Logger.Debug("Trying to fetch the adaptive & progressive streams")
        for streamUrl in streamUrls:
            streamData = UriHandler.Open(streamUrl, proxy=proxy, additionalHeaders=headers)
            streamInfo = JsonHelper(streamData)
            Logger.Info("Found '%s' stream", streamInfo.GetValue("family"))
            for subStreamUrl in streamInfo.GetValue("streams"):
                subStreamData = UriHandler.Open(subStreamUrl, proxy)
                subSreamInfo = JsonHelper(subStreamData)
                if "errorstring" in subSreamInfo.json:
                    Logger.Warning("Could not find streams: %s", subSreamInfo.json["errorstring"])
                    continue

                url = subSreamInfo.GetValue("url")
                if "m3u8" in url:
                    Logger.Debug("Found M3U8 stream: %s", url)
                    for s, b in M3u8.GetStreamsFromM3u8(url, proxy):
                        results.append((s, b))

                    # No more need to look further for this stream
                    continue

                Logger.Debug("Found MP4/M4V stream: %s", url)
                if "h264_bb" in subStreamUrl:
                    bitrate = 500
                elif "h264_sb" in subStreamUrl:
                    bitrate = 220
                elif "h264_std" in subStreamUrl:
                    bitrate = 1000
                else:
                    bitrate = None

                if "?odiredirecturl" in url:
                    url = url[:url.index("?odiredirecturl")]
                results.append((url, bitrate))

            if results:
                return results

        # no results so far
        streamUrl = "http://e.omroep.nl/metadata/%s" % (streamId,)
        Logger.Info("Atttemting old school URL: %s", url)
        streamData = UriHandler.Open(streamUrl, proxy=proxy, additionalHeaders=headers)
        streamInfo = JsonHelper(streamData)
        for stream in streamInfo.GetValue("streams"):
            quality = stream.get("kwaliteit", 0)
            if quality == 1:
                bitrate = 180
            elif quality == 2:
                bitrate = 1000
            elif quality == 3:
                bitrate = 1500
            else:
                bitrate = 0

            if "formaat" in stream and stream["formaat"] == "h264":
                bitrate += 1

            url = stream['url']
            url = Mms.GetMmsFromAsx(url, proxy)
            results.append((url, bitrate))
        return results

    @staticmethod
    def GetSubtitle(streamId, proxy=None):
        # type: (str, Proxy) -> str
        subTitleUrl = "http://e.omroep.nl/tt888/%s" % (streamId,)
        return SubtitleHelper.DownloadSubtitle(subTitleUrl, streamId + ".srt", format='srt', proxy=proxy)

    @staticmethod
    def GetLiveStreamsFromNpo(url, cacheDir, proxy=None, headers=None):
        """ Retrieve NPO Player Live streams from a different number of stream urls.

        @param url:               (String) The url to download
        @param cacheDir:          (String) The cache dir where to find the 'uzg-i.js' file.
        @param headers:           (dict) Possible HTTP Headers
        @param proxy:             (Proxy) The proxy to use for opening

        Can be used like this:

            part = item.CreateNewEmptyMediaPart()
            for s, b in NpoStream.GetStreamsFromNpo(m3u8Url, self.proxy):
                item.complete = True
                # s = self.GetVerifiableVideoUrl(s)
                part.AppendMediaStream(s, b)

        """

        Logger.Info("Determining streams for: %s", url)

        if url.startswith("http://ida.omroep.nl/aapi/"):
            Logger.Debug("Already found an IDA data url '%s'. Using it to fetch the streams.", url)
            # we already have the m3u8
            actualStreamData = UriHandler.Open(
                url,
                proxy=proxy,
                additionalHeaders=headers)

            url = NpoStream.__FetchActualStream(actualStreamData, proxy)

        elif url.endswith("m3u8"):
            Logger.Debug("Found a stream url '%s'. Using a call to IDA to determine the actual streams.", url)
            hashCode = NpoStream.GetNpoToken(proxy, cacheDir)
            actualStreamData = UriHandler.Open(
                "http://ida.omroep.nl/aapi/?stream=%s&token=%s" % (url, hashCode),
                proxy=proxy,
                additionalHeaders=headers)
            url = NpoStream.__FetchActualStream(actualStreamData, proxy)

        elif url.startswith("http://e.omroep.nl/metadata/"):
            Logger.Debug("Found a metadata url '%s'. Determining the actual stream url's", url)
            jsonData = UriHandler.Open(url, proxy=proxy)
            json = JsonHelper(jsonData, Logger.Instance())
            streams = []
            for stream in json.GetValue("streams"):
                if "type" not in stream:
                    Logger.Warning("No compatible streams found: %s", stream)
                    continue

                if stream['type'] != "hls":
                    continue
                url = stream['url']

                Logger.Trace("Found HLS stream: '%s'", url)
                for k, v in NpoStream.GetLiveStreamsFromNpo(url, cacheDir, proxy=proxy, headers=headers):
                    streams.append((k, v))
            return streams
        else:
            Logger.Warning("None-stream url found: %s", url)
            return []

        return M3u8.GetStreamsFromM3u8(url, proxy=proxy)

    @staticmethod
    def GetNpoToken(proxy, cacheDir):
        tokenUrl = "http://ida.omroep.nl/npoplayer/i.js"
        tokenExpired = True
        tokenFile = "uzg-i.js"
        tokenPath = os.path.join(cacheDir, tokenFile)

        # determine valid token
        if os.path.exists(tokenPath):
            mTime = os.path.getmtime(tokenPath)
            timeDiff = time.time() - mTime
            maxTime = 30 * 60  # if older than 15 minutes, 30 also seems to work.
            Logger.Debug("Found token '%s' which is %s seconds old (maxAge=%ss)", tokenFile,
                         timeDiff, maxTime)
            if timeDiff > maxTime:
                Logger.Debug("Token expired.")
                tokenExpired = True
            elif timeDiff < 0:
                Logger.Debug("Token modified time is in the future. Ignoring token.")
                tokenExpired = True
            else:
                tokenExpired = False
        else:
            Logger.Debug("No Token Found.")

        if tokenExpired:
            Logger.Debug("Fetching a Token.")
            tokenData = UriHandler.Open(tokenUrl, proxy=proxy, noCache=True)
            tokenHandle = file(tokenPath, 'w')
            tokenHandle.write(tokenData)
            tokenHandle.close()
            Logger.Debug("Token saved for future use.")
        else:
            Logger.Debug("Reusing an existing Token.")
            # noinspection PyArgumentEqualDefault
            tokenHandle = file(tokenPath, 'r')
            tokenData = tokenHandle.read()
            tokenHandle.close()

        token = Regexer.DoRegex('npoplayer.token = "([^"]+)', tokenData)[-1]
        actualToken = NpoStream.__SwapToken(token)
        Logger.Info("Found NOS token: %s\n          was: %s\n", actualToken, token)
        return actualToken

    @staticmethod
    def __FetchActualStream(idaData, proxy):
        actualStreamJson = JsonHelper(idaData, Logger.Instance())
        m3u8Url = actualStreamJson.GetValue('stream')
        Logger.Debug("Fetching redirected stream for: %s", m3u8Url)

        # now we have the m3u8 URL, but it will do a HTML 302 redirect
        (headData, m3u8Url) = UriHandler.Header(m3u8Url, proxy=proxy)  # : @UnusedVariables

        Logger.Debug("Found redirected stream: %s", m3u8Url)
        return m3u8Url

    @staticmethod
    def __SwapToken(token):
        """ Swaps some chars of the token to make it a valid one. NPO introduced this in july 2015

        @param token: the original token from their file.

        @return: the swapped version

        """

        first = -1
        second = -1
        startAt = 5
        Logger.Debug("Starting Token swap at position in: %s %s %s", token[0:startAt],
                     token[startAt:len(token) - startAt], token[len(token) - startAt:])
        for i in range(startAt, len(token) - startAt, 1):
            # Logger.Trace("Checking %s", token[i])
            if token[i].isdigit():
                if first < 0:
                    first = i
                    Logger.Trace("Storing first digit at position %s: %s", first, token[i])
                elif second < 0:
                    second = i
                    Logger.Trace("Storing second digit at position %s: %s", second, token[i])
                    break

        # swap them
        newToken = list(token)
        if first < 0 or second < 0:
            Logger.Debug("No number combo found in range %s. Swapping middle items",
                         token[startAt:len(token) - startAt])
            first = 12
            second = 13

        Logger.Debug("Swapping position %s with %s", first, second)
        newToken[first] = token[second]
        newToken[second] = token[first]
        newToken = ''.join(newToken)
        return newToken

if __name__ == "__main__":
    from debug.initdebug import DebugInitializer
    DebugInitializer()
    cacheDir = os.path.join("..", "..", "..", "..", "..", "net.rieter.xot.userdata", "cache")

    # Live
    # url = "http://livestreams.omroep.nl/live/regionaal/l1/l1tv/l1tv.isml/l1tv.m3u8"
    url = "http://e.omroep.nl/metadata/LI_NEDERLAND3_136696"
    # token = NpoStream.GetNpoToken(DebugInitializer.Proxy, cacheDir)
    # url = "http://ida.omroep.nl/aapi/?stream=http://livestreams.omroep.nl/live/npo/tvlive/ned3/ned3.isml/ned3.m3u8&token=%s" % (token, )
    results = NpoStream.GetLiveStreamsFromNpo(url, cacheDir, proxy=DebugInitializer.Proxy)  # non live

    # url = "http://e.omroep.nl/metadata/urn:vpro:media:program:69816735"
    # url = "http://e.omroep.nl/metadata/POMS_AT_3106978"
    # results = NpoStream.GetStreamsFromNpo(url, cacheDir, proxy=DebugInitializer.Proxy)

    results.sort(lambda x, y: cmp(int(x[1]), int(y[1])))
    for s, b in results:
        if s.count("://") > 1:
            raise Exception("Duplicate protocol in url: %s", s)
        print "%s - %s" % (b, s)
        Logger.Info("%s - %s", b, s)

    # some test cases
    tokenTests = {
        "kouansr1o89hu1u0lnr20b6f60": "kouansr8o19hu1u0lnr20b6f60",
        "h05npjekmn478nhfqft7g2i6q1": "h05npjekmn748nhfqft7g2i6q1",
        "ncjamt9gu2d9qmg4dpu1plqd37": "ncjamt2gu9d9qmg4dpu1plqd37",
        "m9mvj51ittnuglub3ibgoptvi4": "m9mvj15ittnuglub3ibgoptvi4",
        "vgkn9j8r3135a7vf0e6992vmi1": "vgkn9j3r8135a7vf0e6992vmi1",
        "eqn86lpcdadda9ajrceedcpef3": "eqn86lpcdadd9aajrceedcpef3",
        "vagiq9ejnqbmcodtncp77uomj1": "vagiq7ejnqbmcodtncp97uomj1",
    }

    for inputToken, outputToken in tokenTests.iteritems():
        # noinspection PyUnresolvedReferences,PyProtectedMember
        token = NpoStream._NpoStream__SwapToken(inputToken)
        if token != outputToken:
            raise Exception("Token mismatch:\nInput:   %s\nOutput:  %s\nShould be: %s")

    Logger.Instance().CloseLog()
