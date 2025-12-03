(function () {
    "use strict";

    const isNavigatorDefined = typeof navigator !== "undefined";
    const userAgent = isNavigatorDefined
        ? navigator.userAgentData &&
          Array.isArray(navigator.userAgentData.brands)
            ? navigator.userAgentData.brands
                  .map(
                      (brand) => `${brand.brand.toLowerCase()} ${brand.version}`
                  )
                  .join(" ")
            : navigator.userAgent.toLowerCase()
        : "some useragent";
    const platform = isNavigatorDefined
        ? navigator.userAgentData &&
          typeof navigator.userAgentData.platform === "string"
            ? navigator.userAgentData.platform.toLowerCase()
            : navigator.platform.toLowerCase()
        : "some platform";
    const isFirefox = false;
    userAgent.includes("vivaldi");
    userAgent.includes("yabrowser");
    const isOpera = userAgent.includes("opr") || userAgent.includes("opera");
    const isEdge = userAgent.includes("edg");
    const isWindows = platform.startsWith("win");
    const isMacOS = platform.startsWith("mac");
    const isMobile =
        isNavigatorDefined && navigator.userAgentData
            ? navigator.userAgentData.mobile
            : userAgent.includes("mobile") || false;
    (isNavigatorDefined &&
        navigator.userAgentData &&
        ["Linux", "Android"].includes(navigator.userAgentData.platform)) ||
        platform.startsWith("linux");
    const chromiumVersion = (() => {
        const m = userAgent.match(/chrom(?:e|ium)(?:\/| )([^ ]+)/);
        if (m && m[1]) {
            return m[1];
        }
        return "";
    })();
    (() => {
        const m = userAgent.match(/(?:firefox|librewolf)(?:\/| )([^ ]+)/);
        if (m && m[1]) {
            return m[1];
        }
        return "";
    })();
    (() => {
        try {
            document.querySelector(":defined");
            return true;
        } catch (err) {
            return false;
        }
    })();
    function compareChromeVersions($a, $b) {
        const a = $a.split(".").map((x) => parseInt(x));
        const b = $b.split(".").map((x) => parseInt(x));
        for (let i = 0; i < a.length; i++) {
            if (a[i] !== b[i]) {
                return a[i] < b[i] ? -1 : 1;
            }
        }
        return 0;
    }
    const isXMLHttpRequestSupported = typeof XMLHttpRequest === "function";
    const isFetchSupported = typeof fetch === "function";
    const isCSSColorSchemePropSupported = (() => {
        try {
            if (typeof document === "undefined") {
                return false;
            }
            const el = document.createElement("div");
            if (!el || typeof el.style !== "object") {
                return false;
            }
            if (typeof el.style.colorScheme === "string") {
                return true;
            }
            el.setAttribute("style", "color-scheme: dark");
            return el.style.colorScheme === "dark";
        } catch (e) {
            return false;
        }
    })();

    function parse24HTime(time) {
        return time.split(":").map((x) => parseInt(x));
    }
    function compareTime(time1, time2) {
        if (time1[0] === time2[0] && time1[1] === time2[1]) {
            return 0;
        }
        if (
            time1[0] < time2[0] ||
            (time1[0] === time2[0] && time1[1] < time2[1])
        ) {
            return -1;
        }
        return 1;
    }
    function nextTimeInterval(time0, time1, date = new Date()) {
        const a = parse24HTime(time0);
        const b = parse24HTime(time1);
        const t = [date.getHours(), date.getMinutes()];
        if (compareTime(a, b) > 0) {
            return nextTimeInterval(time1, time0, date);
        }
        if (compareTime(a, b) === 0) {
            return null;
        }
        if (compareTime(t, a) < 0) {
            date.setHours(a[0]);
            date.setMinutes(a[1]);
            date.setSeconds(0);
            date.setMilliseconds(0);
            return date.getTime();
        }
        if (compareTime(t, b) < 0) {
            date.setHours(b[0]);
            date.setMinutes(b[1]);
            date.setSeconds(0);
            date.setMilliseconds(0);
            return date.getTime();
        }
        return new Date(
            date.getFullYear(),
            date.getMonth(),
            date.getDate() + 1,
            a[0],
            a[1]
        ).getTime();
    }
    function isInTimeIntervalLocal(time0, time1, date = new Date()) {
        const a = parse24HTime(time0);
        const b = parse24HTime(time1);
        const t = [date.getHours(), date.getMinutes()];
        if (compareTime(a, b) > 0) {
            return compareTime(a, t) <= 0 || compareTime(t, b) < 0;
        }
        return compareTime(a, t) <= 0 && compareTime(t, b) < 0;
    }
    function isInTimeIntervalUTC(time0, time1, timestamp) {
        if (time1 < time0) {
            return timestamp <= time1 || time0 <= timestamp;
        }
        return time0 < timestamp && timestamp < time1;
    }
    function getDuration(time) {
        let duration = 0;
        if (time.seconds) {
            duration += time.seconds * 1000;
        }
        if (time.minutes) {
            duration += time.minutes * 60 * 1000;
        }
        if (time.hours) {
            duration += time.hours * 60 * 60 * 1000;
        }
        if (time.days) {
            duration += time.days * 24 * 60 * 60 * 1000;
        }
        return duration;
    }
    function getDurationInMinutes(time) {
        return getDuration(time) / 1000 / 60;
    }
    function getSunsetSunriseUTCTime(latitude, longitude, date) {
        const dec31 = Date.UTC(date.getUTCFullYear(), 0, 0, 0, 0, 0, 0);
        const oneDay = getDuration({days: 1});
        const dayOfYear = Math.floor((date.getTime() - dec31) / oneDay);
        const zenith = 90.83333333333333;
        const D2R = Math.PI / 180;
        const R2D = 180 / Math.PI;
        const lnHour = longitude / 15;
        function getTime(isSunrise) {
            const t = dayOfYear + ((isSunrise ? 6 : 18) - lnHour) / 24;
            const M = 0.9856 * t - 3.289;
            let L =
                M +
                1.916 * Math.sin(M * D2R) +
                0.02 * Math.sin(2 * M * D2R) +
                282.634;
            if (L > 360) {
                L -= 360;
            } else if (L < 0) {
                L += 360;
            }
            let RA = R2D * Math.atan(0.91764 * Math.tan(L * D2R));
            if (RA > 360) {
                RA -= 360;
            } else if (RA < 0) {
                RA += 360;
            }
            const Lquadrant = Math.floor(L / 90) * 90;
            const RAquadrant = Math.floor(RA / 90) * 90;
            RA += Lquadrant - RAquadrant;
            RA /= 15;
            const sinDec = 0.39782 * Math.sin(L * D2R);
            const cosDec = Math.cos(Math.asin(sinDec));
            const cosH =
                (Math.cos(zenith * D2R) - sinDec * Math.sin(latitude * D2R)) /
                (cosDec * Math.cos(latitude * D2R));
            if (cosH > 1) {
                return {
                    alwaysDay: false,
                    alwaysNight: true,
                    time: 0
                };
            } else if (cosH < -1) {
                return {
                    alwaysDay: true,
                    alwaysNight: false,
                    time: 0
                };
            }
            const H =
                (isSunrise
                    ? 360 - R2D * Math.acos(cosH)
                    : R2D * Math.acos(cosH)) / 15;
            const T = H + RA - 0.06571 * t - 6.622;
            let UT = T - lnHour;
            if (UT > 24) {
                UT -= 24;
            } else if (UT < 0) {
                UT += 24;
            }
            return {
                alwaysDay: false,
                alwaysNight: false,
                time: Math.round(UT * getDuration({hours: 1}))
            };
        }
        const sunriseTime = getTime(true);
        const sunsetTime = getTime(false);
        if (sunriseTime.alwaysDay || sunsetTime.alwaysDay) {
            return {
                alwaysDay: true,
                alwaysNight: false,
                sunriseTime: 0,
                sunsetTime: 0
            };
        } else if (sunriseTime.alwaysNight || sunsetTime.alwaysNight) {
            return {
                alwaysDay: false,
                alwaysNight: true,
                sunriseTime: 0,
                sunsetTime: 0
            };
        }
        return {
            alwaysDay: false,
            alwaysNight: false,
            sunriseTime: sunriseTime.time,
            sunsetTime: sunsetTime.time
        };
    }
    function isNightAtLocation(latitude, longitude, date = new Date()) {
        const time = getSunsetSunriseUTCTime(latitude, longitude, date);
        if (time.alwaysDay) {
            return false;
        } else if (time.alwaysNight) {
            return true;
        }
        const sunriseTime = time.sunriseTime;
        const sunsetTime = time.sunsetTime;
        const currentTime =
            date.getUTCHours() * getDuration({hours: 1}) +
            date.getUTCMinutes() * getDuration({minutes: 1}) +
            date.getUTCSeconds() * getDuration({seconds: 1}) +
            date.getUTCMilliseconds();
        return isInTimeIntervalUTC(sunsetTime, sunriseTime, currentTime);
    }
    function nextTimeChangeAtLocation(latitude, longitude, date = new Date()) {
        const time = getSunsetSunriseUTCTime(latitude, longitude, date);
        if (time.alwaysDay) {
            return date.getTime() + getDuration({days: 1});
        } else if (time.alwaysNight) {
            return date.getTime() + getDuration({days: 1});
        }
        const [firstTimeOnDay, lastTimeOnDay] =
            time.sunriseTime < time.sunsetTime
                ? [time.sunriseTime, time.sunsetTime]
                : [time.sunsetTime, time.sunriseTime];
        const currentTime =
            date.getUTCHours() * getDuration({hours: 1}) +
            date.getUTCMinutes() * getDuration({minutes: 1}) +
            date.getUTCSeconds() * getDuration({seconds: 1}) +
            date.getUTCMilliseconds();
        if (currentTime <= firstTimeOnDay) {
            return Date.UTC(
                date.getUTCFullYear(),
                date.getUTCMonth(),
                date.getUTCDate(),
                0,
                0,
                0,
                firstTimeOnDay
            );
        }
        if (currentTime <= lastTimeOnDay) {
            return Date.UTC(
                date.getUTCFullYear(),
                date.getUTCMonth(),
                date.getUTCDate(),
                0,
                0,
                0,
                lastTimeOnDay
            );
        }
        return Date.UTC(
            date.getUTCFullYear(),
            date.getUTCMonth(),
            date.getUTCDate() + 1,
            0,
            0,
            0,
            firstTimeOnDay
        );
    }

    function cachedFactory(factory, size) {
        const cache = new Map();
        return (key) => {
            if (cache.has(key)) {
                return cache.get(key);
            }
            const value = factory(key);
            cache.set(key, value);
            if (cache.size > size) {
                const first = cache.keys().next().value;
                cache.delete(first);
            }
            return value;
        };
    }

    function getURLHostOrProtocol($url) {
        const url = new URL($url);
        if (url.host) {
            return url.host;
        } else if (url.protocol === "file:") {
            return url.pathname;
        }
        return url.protocol;
    }
    function compareURLPatterns(a, b) {
        return a.localeCompare(b);
    }
    function isURLInList(url, list) {
        for (let i = 0; i < list.length; i++) {
            if (isURLMatched(url, list[i])) {
                return true;
            }
        }
        return false;
    }
    function isURLMatched(url, urlTemplate) {
        if (isRegExp(urlTemplate)) {
            const regexp = createRegExp(urlTemplate);
            return regexp ? regexp.test(url) : false;
        }
        return matchURLPattern(url, urlTemplate);
    }
    const URL_CACHE_SIZE = 32;
    const prepareURL = cachedFactory((url) => {
        let parsed;
        try {
            parsed = new URL(url);
        } catch (err) {
            return null;
        }
        const {hostname, pathname, protocol, port} = parsed;
        const hostParts = hostname.split(".").reverse();
        const pathParts = pathname.split("/").slice(1);
        if (!pathParts[pathParts.length - 1]) {
            pathParts.splice(pathParts.length - 1, 1);
        }
        return {
            hostParts,
            pathParts,
            port,
            protocol
        };
    }, URL_CACHE_SIZE);
    const URL_MATCH_CACHE_SIZE = 32 * 1024;
    const preparePattern = cachedFactory((pattern) => {
        if (!pattern) {
            return null;
        }
        const exactStart = pattern.startsWith("^");
        const exactEnd = pattern.endsWith("$");
        if (exactStart) {
            pattern = pattern.substring(1);
        }
        if (exactEnd) {
            pattern = pattern.substring(0, pattern.length - 1);
        }
        let protocol = "";
        const protocolIndex = pattern.indexOf("://");
        if (protocolIndex > 0) {
            protocol = pattern.substring(0, protocolIndex + 1);
            pattern = pattern.substring(protocolIndex + 3);
        }
        const slashIndex = pattern.indexOf("/");
        const host =
            slashIndex < 0 ? pattern : pattern.substring(0, slashIndex);
        let hostName = host;
        let isIPv6 = false;
        let ipV6End = -1;
        if (host.startsWith("[")) {
            ipV6End = host.indexOf("]");
            if (ipV6End > 0) {
                isIPv6 = true;
            }
        }
        let port = "*";
        const portIndex = host.lastIndexOf(":");
        if (portIndex >= 0 && (!isIPv6 || ipV6End < portIndex)) {
            hostName = host.substring(0, portIndex);
            port = host.substring(portIndex + 1);
        }
        if (isIPv6) {
            try {
                const ipV6URL = new URL(`http://${hostName}`);
                hostName = ipV6URL.hostname;
            } catch (err) {}
        }
        const hostParts = hostName.split(".").reverse();
        const path = slashIndex < 0 ? "" : pattern.substring(slashIndex + 1);
        const pathParts = path.split("/");
        if (!pathParts[pathParts.length - 1]) {
            pathParts.splice(pathParts.length - 1, 1);
        }
        return {
            hostParts,
            pathParts,
            port,
            exactStart,
            exactEnd,
            protocol
        };
    }, URL_MATCH_CACHE_SIZE);
    function matchURLPattern(url, pattern) {
        const u = prepareURL(url);
        const p = preparePattern(pattern);
        if (
            !(u && p) ||
            p.hostParts.length > u.hostParts.length ||
            (p.exactStart && p.hostParts.length !== u.hostParts.length) ||
            (p.exactEnd && p.pathParts.length !== u.pathParts.length) ||
            (p.port !== "*" && p.port !== u.port) ||
            (p.protocol && p.protocol !== u.protocol)
        ) {
            return false;
        }
        for (let i = 0; i < p.hostParts.length; i++) {
            const pHostPart = p.hostParts[i];
            const uHostPart = u.hostParts[i];
            if (pHostPart !== "*" && pHostPart !== uHostPart) {
                return false;
            }
        }
        if (
            p.hostParts.length >= 2 &&
            p.hostParts.at(-1) !== "*" &&
            (p.hostParts.length < u.hostParts.length - 1 ||
                (p.hostParts.length === u.hostParts.length - 1 &&
                    u.hostParts.at(-1) !== "www"))
        ) {
            return false;
        }
        if (p.pathParts.length === 0) {
            return true;
        }
        if (p.pathParts.length > u.pathParts.length) {
            return false;
        }
        for (let i = 0; i < p.pathParts.length; i++) {
            const pPathPart = p.pathParts[i];
            const uPathPart = u.pathParts[i];
            if (pPathPart !== "*" && pPathPart !== uPathPart) {
                return false;
            }
        }
        return true;
    }
    function isRegExp(pattern) {
        return (
            pattern.startsWith("/") &&
            pattern.endsWith("/") &&
            pattern.length > 2
        );
    }
    const REGEXP_CACHE_SIZE = 1024;
    const createRegExp = cachedFactory((pattern) => {
        if (pattern.startsWith("/")) {
            pattern = pattern.substring(1);
        }
        if (pattern.endsWith("/")) {
            pattern = pattern.substring(0, pattern.length - 1);
        }
        try {
            return new RegExp(pattern);
        } catch (err) {
            return null;
        }
    }, REGEXP_CACHE_SIZE);
    function isPDF(url) {
        try {
            const {hostname, pathname} = new URL(url);
            if (pathname.includes(".pdf")) {
                if (
                    (hostname.match(/(wikipedia|wikimedia)\.org$/i) &&
                        pathname.match(/^\/.*\/[a-z]+\:[^\:\/]+\.pdf/i)) ||
                    (hostname.match(/timetravel\.mementoweb\.org$/i) &&
                        pathname.match(/^\/reconstruct/i) &&
                        pathname.match(/\.pdf$/i)) ||
                    (hostname.match(/dropbox\.com$/i) &&
                        pathname.match(/^\/s\//i) &&
                        pathname.match(/\.pdf$/i))
                ) {
                    return false;
                }
                if (pathname.endsWith(".pdf")) {
                    for (let i = pathname.length; i >= 0; i--) {
                        if (pathname[i] === "=") {
                            return false;
                        } else if (pathname[i] === "/") {
                            return true;
                        }
                    }
                } else {
                    return false;
                }
            }
        } catch (e) {}
        return false;
    }
    function isURLEnabled(
        url,
        userSettings,
        {isProtected, isInDarkList, isDarkThemeDetected},
        isAllowedFileSchemeAccess = true
    ) {
        if (isLocalFile(url) && !isAllowedFileSchemeAccess) {
            return false;
        }
        if (isProtected && !userSettings.enableForProtectedPages) {
            return false;
        }
        if (isPDF(url)) {
            return userSettings.enableForPDF;
        }
        const isURLInDisabledList = isURLInList(url, userSettings.disabledFor);
        const isURLInEnabledList = isURLInList(url, userSettings.enabledFor);
        if (!userSettings.enabledByDefault) {
            return isURLInEnabledList;
        }
        if (isURLInEnabledList) {
            return true;
        }
        if (
            isInDarkList ||
            (userSettings.detectDarkTheme && isDarkThemeDetected)
        ) {
            return false;
        }
        return !isURLInDisabledList;
    }
    function isFullyQualifiedDomain(candidate) {
        return (
            /^[a-z0-9\.\-]+$/i.test(candidate) && candidate.indexOf("..") === -1
        );
    }
    function isFullyQualifiedDomainWildcard(candidate) {
        if (!candidate.includes("*") || !/^[a-z0-9\.\-\*]+$/i.test(candidate)) {
            return false;
        }
        const labels = candidate.split(".");
        for (const label of labels) {
            if (label !== "*" && !/^[a-z0-9\-]+$/i.test(label)) {
                return false;
            }
        }
        return true;
    }
    function fullyQualifiedDomainMatchesWildcard(wildcard, candidate) {
        const wildcardLabels = wildcard.toLowerCase().split(".");
        const candidateLabels = candidate.toLowerCase().split(".");
        if (candidateLabels.length < wildcardLabels.length) {
            return false;
        }
        while (wildcardLabels.length) {
            const wildcardLabel = wildcardLabels.pop();
            const candidateLabel = candidateLabels.pop();
            if (wildcardLabel !== "*" && wildcardLabel !== candidateLabel) {
                return false;
            }
        }
        return true;
    }
    function isLocalFile(url) {
        return Boolean(url) && url.startsWith("file:///");
    }

    function canInjectScript(url) {
        if (url === "about:blank") {
            return false;
        }
        if (isEdge) {
            return Boolean(
                url &&
                    !url.startsWith("chrome") &&
                    !url.startsWith("data") &&
                    !url.startsWith("devtools") &&
                    !url.startsWith("edge") &&
                    !url.startsWith("https://chrome.google.com/webstore") &&
                    !url.startsWith("https://chromewebstore.google.com/") &&
                    !url.startsWith(
                        "https://microsoftedge.microsoft.com/addons"
                    ) &&
                    !url.startsWith("view-source")
            );
        }
        return Boolean(
            url &&
                !url.startsWith("chrome") &&
                !url.startsWith("https://chrome.google.com/webstore") &&
                !url.startsWith("https://chromewebstore.google.com/") &&
                !url.startsWith("data") &&
                !url.startsWith("devtools") &&
                !url.startsWith("view-source")
        );
    }
    async function readSyncStorage(defaults) {
        return new Promise((resolve) => {
            chrome.storage.sync.get(null, (sync) => {
                if (chrome.runtime.lastError) {
                    console.error(chrome.runtime.lastError.message);
                    resolve(null);
                    return;
                }
                for (const key in sync) {
                    if (!sync[key]) {
                        continue;
                    }
                    const metaKeysCount = sync[key].__meta_split_count;
                    if (!metaKeysCount) {
                        continue;
                    }
                    let string = "";
                    for (let i = 0; i < metaKeysCount; i++) {
                        string += sync[`${key}_${i.toString(36)}`];
                        delete sync[`${key}_${i.toString(36)}`];
                    }
                    try {
                        sync[key] = JSON.parse(string);
                    } catch (error) {
                        console.error(
                            `sync[${key}]: Could not parse record from sync storage: ${string}`
                        );
                        resolve(null);
                        return;
                    }
                }
                sync = {
                    ...defaults,
                    ...sync
                };
                resolve(sync);
            });
        });
    }
    async function readLocalStorage(defaults) {
        return new Promise((resolve) => {
            chrome.storage.local.get(defaults, (local) => {
                if (chrome.runtime.lastError) {
                    console.error(chrome.runtime.lastError.message);
                    resolve(defaults);
                    return;
                }
                resolve(local);
            });
        });
    }
    function prepareSyncStorage(values) {
        for (const key in values) {
            const value = values[key];
            const string = JSON.stringify(value);
            const totalLength = string.length + key.length;
            if (totalLength > chrome.storage.sync.QUOTA_BYTES_PER_ITEM) {
                const maxLength =
                    chrome.storage.sync.QUOTA_BYTES_PER_ITEM -
                    key.length -
                    1 -
                    2;
                const minimalKeysNeeded = Math.ceil(string.length / maxLength);
                for (let i = 0; i < minimalKeysNeeded; i++) {
                    values[`${key}_${i.toString(36)}`] = string.substring(
                        i * maxLength,
                        (i + 1) * maxLength
                    );
                }
                values[key] = {
                    __meta_split_count: minimalKeysNeeded
                };
            }
        }
        return values;
    }
    async function writeSyncStorage(values) {
        return new Promise((resolve, reject) => {
            const packaged = prepareSyncStorage(values);
            chrome.storage.sync.set(packaged, () => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                    return;
                }
                resolve();
            });
        });
    }
    async function writeLocalStorage(values) {
        return new Promise((resolve) => {
            chrome.storage.local.set(values, () => {
                resolve();
            });
        });
    }
    async function removeSyncStorage(keys) {
        return new Promise((resolve) => {
            chrome.storage.sync.remove(keys, () => {
                resolve();
            });
        });
    }
    async function removeLocalStorage(keys) {
        return new Promise((resolve) => {
            chrome.storage.local.remove(keys, () => {
                resolve();
            });
        });
    }
    async function getCommands() {
        return new Promise((resolve) => {
            if (!chrome.commands) {
                resolve([]);
                return;
            }
            chrome.commands.getAll((commands) => {
                if (commands) {
                    resolve(commands);
                } else {
                    resolve([]);
                }
            });
        });
    }

    function getUILanguage() {
        let code;
        if (
            "i18n" in chrome &&
            "getUILanguage" in chrome.i18n &&
            typeof chrome.i18n.getUILanguage === "function"
        ) {
            code = chrome.i18n.getUILanguage();
        } else {
            code = navigator.language.split("-")[0];
        }
        if (code.endsWith("-mac")) {
            return code.substring(0, code.length - 4);
        }
        return code;
    }

    const BLOG_URL = "https://darkreader.org/blog/";
    const NEWS_URL = "https://darkreader.org/blog/posts.json";
    const UNINSTALL_URL = "https://darkreader.org/goodluck/";
    const HELP_URL = "https://darkreader.org/help";
    const CONFIG_URL_BASE =
        "https://raw.githubusercontent.com/darkreader/darkreader/main/src/config";
    const helpLocales = [
        "be",
        "cs",
        "de",
        "en",
        "es",
        "fr",
        "it",
        "ja",
        "nl",
        "pt",
        "ru",
        "sr",
        "tr",
        "zh-CN",
        "zh-TW"
    ];
    function getHelpURL() {
        if (isEdge && isMobile) {
            return `${HELP_URL}/mobile/`;
        }
        const locale = getUILanguage();
        const matchLocale =
            helpLocales.find((hl) => hl === locale) ||
            helpLocales.find((hl) => locale.startsWith(hl)) ||
            "en";
        return `${HELP_URL}/${matchLocale}/`;
    }
    function getBlogPostURL(postId) {
        return `${BLOG_URL}${postId}/`;
    }

    const isSystemDarkModeEnabled = () =>
        matchMedia("(prefers-color-scheme: dark)").matches;

    var MessageTypeUItoBG;
    (function (MessageTypeUItoBG) {
        MessageTypeUItoBG["GET_DATA"] = "ui-bg-get-data";
        MessageTypeUItoBG["GET_DEVTOOLS_DATA"] = "ui-bg-get-devtools-data";
        MessageTypeUItoBG["SUBSCRIBE_TO_CHANGES"] =
            "ui-bg-subscribe-to-changes";
        MessageTypeUItoBG["UNSUBSCRIBE_FROM_CHANGES"] =
            "ui-bg-unsubscribe-from-changes";
        MessageTypeUItoBG["CHANGE_SETTINGS"] = "ui-bg-change-settings";
        MessageTypeUItoBG["SET_THEME"] = "ui-bg-set-theme";
        MessageTypeUItoBG["TOGGLE_ACTIVE_TAB"] = "ui-bg-toggle-active-tab";
        MessageTypeUItoBG["MARK_NEWS_AS_READ"] = "ui-bg-mark-news-as-read";
        MessageTypeUItoBG["MARK_NEWS_AS_DISPLAYED"] =
            "ui-bg-mark-news-as-displayed";
        MessageTypeUItoBG["LOAD_CONFIG"] = "ui-bg-load-config";
        MessageTypeUItoBG["APPLY_DEV_DYNAMIC_THEME_FIXES"] =
            "ui-bg-apply-dev-dynamic-theme-fixes";
        MessageTypeUItoBG["RESET_DEV_DYNAMIC_THEME_FIXES"] =
            "ui-bg-reset-dev-dynamic-theme-fixes";
        MessageTypeUItoBG["APPLY_DEV_INVERSION_FIXES"] =
            "ui-bg-apply-dev-inversion-fixes";
        MessageTypeUItoBG["RESET_DEV_INVERSION_FIXES"] =
            "ui-bg-reset-dev-inversion-fixes";
        MessageTypeUItoBG["APPLY_DEV_STATIC_THEMES"] =
            "ui-bg-apply-dev-static-themes";
        MessageTypeUItoBG["RESET_DEV_STATIC_THEMES"] =
            "ui-bg-reset-dev-static-themes";
        MessageTypeUItoBG["START_ACTIVATION"] = "ui-bg-start-activation";
        MessageTypeUItoBG["RESET_ACTIVATION"] = "ui-bg-reset-activation";
        MessageTypeUItoBG["COLOR_SCHEME_CHANGE"] = "ui-bg-color-scheme-change";
        MessageTypeUItoBG["HIDE_HIGHLIGHTS"] = "ui-bg-hide-highlights";
    })(MessageTypeUItoBG || (MessageTypeUItoBG = {}));
    var MessageTypeBGtoUI;
    (function (MessageTypeBGtoUI) {
        MessageTypeBGtoUI["CHANGES"] = "bg-ui-changes";
    })(MessageTypeBGtoUI || (MessageTypeBGtoUI = {}));
    var DebugMessageTypeBGtoUI;
    (function (DebugMessageTypeBGtoUI) {
        DebugMessageTypeBGtoUI["CSS_UPDATE"] = "debug-bg-ui-css-update";
        DebugMessageTypeBGtoUI["UPDATE"] = "debug-bg-ui-update";
    })(DebugMessageTypeBGtoUI || (DebugMessageTypeBGtoUI = {}));
    var MessageTypeBGtoCS;
    (function (MessageTypeBGtoCS) {
        MessageTypeBGtoCS["ADD_CSS_FILTER"] = "bg-cs-add-css-filter";
        MessageTypeBGtoCS["ADD_DYNAMIC_THEME"] = "bg-cs-add-dynamic-theme";
        MessageTypeBGtoCS["ADD_STATIC_THEME"] = "bg-cs-add-static-theme";
        MessageTypeBGtoCS["ADD_SVG_FILTER"] = "bg-cs-add-svg-filter";
        MessageTypeBGtoCS["CLEAN_UP"] = "bg-cs-clean-up";
        MessageTypeBGtoCS["FETCH_RESPONSE"] = "bg-cs-fetch-response";
        MessageTypeBGtoCS["UNSUPPORTED_SENDER"] = "bg-cs-unsupported-sender";
    })(MessageTypeBGtoCS || (MessageTypeBGtoCS = {}));
    var DebugMessageTypeBGtoCS;
    (function (DebugMessageTypeBGtoCS) {
        DebugMessageTypeBGtoCS["RELOAD"] = "debug-bg-cs-reload";
    })(DebugMessageTypeBGtoCS || (DebugMessageTypeBGtoCS = {}));
    var MessageTypeCStoBG;
    (function (MessageTypeCStoBG) {
        MessageTypeCStoBG["COLOR_SCHEME_CHANGE"] = "cs-bg-color-scheme-change";
        MessageTypeCStoBG["DARK_THEME_DETECTED"] = "cs-bg-dark-theme-detected";
        MessageTypeCStoBG["DARK_THEME_NOT_DETECTED"] =
            "cs-bg-dark-theme-not-detected";
        MessageTypeCStoBG["FETCH"] = "cs-bg-fetch";
        MessageTypeCStoBG["DOCUMENT_CONNECT"] = "cs-bg-document-connect";
        MessageTypeCStoBG["DOCUMENT_FORGET"] = "cs-bg-document-forget";
        MessageTypeCStoBG["DOCUMENT_FREEZE"] = "cs-bg-document-freeze";
        MessageTypeCStoBG["DOCUMENT_RESUME"] = "cs-bg-document-resume";
    })(MessageTypeCStoBG || (MessageTypeCStoBG = {}));
    var DebugMessageTypeCStoBG;
    (function (DebugMessageTypeCStoBG) {
        DebugMessageTypeCStoBG["LOG"] = "debug-cs-bg-log";
    })(DebugMessageTypeCStoBG || (DebugMessageTypeCStoBG = {}));
    var MessageTypeCStoUI;
    (function (MessageTypeCStoUI) {
        MessageTypeCStoUI["EXPORT_CSS_RESPONSE"] = "cs-ui-export-css-response";
    })(MessageTypeCStoUI || (MessageTypeCStoUI = {}));
    var MessageTypeUItoCS;
    (function (MessageTypeUItoCS) {
        MessageTypeUItoCS["EXPORT_CSS"] = "ui-cs-export-css";
    })(MessageTypeUItoCS || (MessageTypeUItoCS = {}));

    function parseArray(text) {
        return text
            .replace(/\r/g, "")
            .split("\n")
            .map((s) => s.trim())
            .filter((s) => s);
    }
    function formatArray(arr) {
        return arr.concat("").join("\n");
    }
    function getStringSize(value) {
        return value.length * 2;
    }
    function getParenthesesRange(input, searchStartIndex = 0) {
        return getOpenCloseRange(input, searchStartIndex, "(", ")", []);
    }
    function getOpenCloseRange(
        input,
        searchStartIndex,
        openToken,
        closeToken,
        excludeRanges
    ) {
        let indexOf;
        if (excludeRanges.length === 0) {
            indexOf = (token, pos) => input.indexOf(token, pos);
        } else {
            indexOf = (token, pos) =>
                indexOfExcluding(input, token, pos, excludeRanges);
        }
        const {length} = input;
        let depth = 0;
        let firstOpenIndex = -1;
        for (let i = searchStartIndex; i < length; i++) {
            if (depth === 0) {
                const openIndex = indexOf(openToken, i);
                if (openIndex < 0) {
                    break;
                }
                firstOpenIndex = openIndex;
                depth++;
                i = openIndex;
            } else {
                const closeIndex = indexOf(closeToken, i);
                if (closeIndex < 0) {
                    break;
                }
                const openIndex = indexOf(openToken, i);
                if (openIndex < 0 || closeIndex <= openIndex) {
                    depth--;
                    if (depth === 0) {
                        return {start: firstOpenIndex, end: closeIndex + 1};
                    }
                    i = closeIndex;
                } else {
                    depth++;
                    i = openIndex;
                }
            }
        }
        return null;
    }
    function indexOfExcluding(input, search, position, excludeRanges) {
        const i = input.indexOf(search, position);
        const exclusion = excludeRanges.find((r) => i >= r.start && i < r.end);
        if (exclusion) {
            return indexOfExcluding(
                input,
                search,
                exclusion.end,
                excludeRanges
            );
        }
        return i;
    }
    function splitExcluding(input, separator, excludeRanges) {
        const parts = [];
        let commaIndex = -1;
        let currIndex = 0;
        while (
            (commaIndex = indexOfExcluding(
                input,
                separator,
                currIndex,
                excludeRanges
            )) >= 0
        ) {
            parts.push(input.substring(currIndex, commaIndex).trim());
            currIndex = commaIndex + 1;
        }
        parts.push(input.substring(currIndex).trim());
        return parts;
    }

    const excludedSelectors = [
        "pre",
        "pre *",
        "code",
        '[aria-hidden="true"]',
        '[class*="fa-"]',
        ".fa",
        ".fab",
        ".fad",
        ".fal",
        ".far",
        ".fas",
        ".fass",
        ".fasr",
        ".fat",
        ".icofont",
        '[style*="font-"]',
        '[class*="icon"]',
        '[class*="Icon"]',
        '[class*="symbol"]',
        '[class*="Symbol"]',
        ".glyphicon",
        '[class*="material-symbol"]',
        '[class*="material-icon"]',
        "mu",
        '[class*="mu-"]',
        ".typcn",
        '[class*="vjs-"]'
    ];
    function createTextStyle(config) {
        const lines = [];
        lines.push(`*:not(${excludedSelectors.join(", ")}) {`);
        if (config.useFont && config.fontFamily) {
            lines.push(`  font-family: ${config.fontFamily} !important;`);
        }
        if (config.textStroke > 0) {
            lines.push(
                `  -webkit-text-stroke: ${config.textStroke}px !important;`
            );
            lines.push(`  text-stroke: ${config.textStroke}px !important;`);
        }
        lines.push("}");
        return lines.join("\n");
    }

    function isArrayLike(items) {
        return items.length != null;
    }
    function forEach(items, iterator) {
        if (isArrayLike(items)) {
            for (let i = 0, len = items.length; i < len; i++) {
                iterator(items[i]);
            }
        } else {
            for (const item of items) {
                iterator(item);
            }
        }
    }
    function push(array, addition) {
        forEach(addition, (a) => array.push(a));
    }

    function formatSitesFixesConfig(fixes, options) {
        const lines = [];
        fixes.forEach((fix, i) => {
            push(lines, fix.url);
            options.props.forEach((prop) => {
                const command = options.getPropCommandName(prop);
                const value = fix[prop];
                if (options.shouldIgnoreProp(prop, value)) {
                    return;
                }
                lines.push("");
                lines.push(command);
                const formattedValue = options.formatPropValue(prop, value);
                if (formattedValue) {
                    lines.push(formattedValue);
                }
            });
            if (i < fixes.length - 1) {
                lines.push("");
                lines.push("=".repeat(32));
                lines.push("");
            }
        });
        lines.push("");
        return lines.join("\n");
    }

    function scale(x, inLow, inHigh, outLow, outHigh) {
        return ((x - inLow) * (outHigh - outLow)) / (inHigh - inLow) + outLow;
    }
    function clamp(x, min, max) {
        return Math.min(max, Math.max(min, x));
    }
    function multiplyMatrices(m1, m2) {
        const result = [];
        for (let i = 0, len = m1.length; i < len; i++) {
            result[i] = [];
            for (let j = 0, len2 = m2[0].length; j < len2; j++) {
                let sum = 0;
                for (let k = 0, len3 = m1[0].length; k < len3; k++) {
                    sum += m1[i][k] * m2[k][j];
                }
                result[i][j] = sum;
            }
        }
        return result;
    }

    function createFilterMatrix(config) {
        let m = Matrix.identity();
        if (config.sepia !== 0) {
            m = multiplyMatrices(m, Matrix.sepia(config.sepia / 100));
        }
        if (config.grayscale !== 0) {
            m = multiplyMatrices(m, Matrix.grayscale(config.grayscale / 100));
        }
        if (config.contrast !== 100) {
            m = multiplyMatrices(m, Matrix.contrast(config.contrast / 100));
        }
        if (config.brightness !== 100) {
            m = multiplyMatrices(m, Matrix.brightness(config.brightness / 100));
        }
        if (config.mode === 1) {
            m = multiplyMatrices(m, Matrix.invertNHue());
        }
        return m;
    }
    function applyColorMatrix([r, g, b], matrix) {
        const rgb = [[r / 255], [g / 255], [b / 255], [1], [1]];
        const result = multiplyMatrices(matrix, rgb);
        return [0, 1, 2].map((i) =>
            clamp(Math.round(result[i][0] * 255), 0, 255)
        );
    }
    const Matrix = {
        identity() {
            return [
                [1, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]
            ];
        },
        invertNHue() {
            return [
                [0.333, -0.667, -0.667, 0, 1],
                [-0.667, 0.333, -0.667, 0, 1],
                [-0.667, -0.667, 0.333, 0, 1],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]
            ];
        },
        brightness(v) {
            return [
                [v, 0, 0, 0, 0],
                [0, v, 0, 0, 0],
                [0, 0, v, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]
            ];
        },
        contrast(v) {
            const t = (1 - v) / 2;
            return [
                [v, 0, 0, 0, t],
                [0, v, 0, 0, t],
                [0, 0, v, 0, t],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]
            ];
        },
        sepia(v) {
            return [
                [
                    0.393 + 0.607 * (1 - v),
                    0.769 - 0.769 * (1 - v),
                    0.189 - 0.189 * (1 - v),
                    0,
                    0
                ],
                [
                    0.349 - 0.349 * (1 - v),
                    0.686 + 0.314 * (1 - v),
                    0.168 - 0.168 * (1 - v),
                    0,
                    0
                ],
                [
                    0.272 - 0.272 * (1 - v),
                    0.534 - 0.534 * (1 - v),
                    0.131 + 0.869 * (1 - v),
                    0,
                    0
                ],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]
            ];
        },
        grayscale(v) {
            return [
                [
                    0.2126 + 0.7874 * (1 - v),
                    0.7152 - 0.7152 * (1 - v),
                    0.0722 - 0.0722 * (1 - v),
                    0,
                    0
                ],
                [
                    0.2126 - 0.2126 * (1 - v),
                    0.7152 + 0.2848 * (1 - v),
                    0.0722 - 0.0722 * (1 - v),
                    0,
                    0
                ],
                [
                    0.2126 - 0.2126 * (1 - v),
                    0.7152 - 0.7152 * (1 - v),
                    0.0722 + 0.9278 * (1 - v),
                    0,
                    0
                ],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]
            ];
        }
    };

    const INDEX_CACHE_CLEANUP_INTERVAL_IN_MS = 60000;
    function parseSitesFixesConfig(text, options) {
        const sites = [];
        const blocks = text.replace(/\r/g, "").split(/^\s*={2,}\s*$/gm);
        blocks.forEach((block) => {
            const lines = block.split("\n");
            const commandIndices = [];
            lines.forEach((ln, i) => {
                if (ln.match(/^[A-Z]+(\s[A-Z]+){0,2}$/)) {
                    commandIndices.push(i);
                }
            });
            if (commandIndices.length === 0) {
                return;
            }
            const siteFix = {
                url: parseArray(lines.slice(0, commandIndices[0]).join("\n"))
            };
            commandIndices.forEach((commandIndex, i) => {
                const command = lines[commandIndex].trim();
                const valueText = lines
                    .slice(
                        commandIndex + 1,
                        i === commandIndices.length - 1
                            ? lines.length
                            : commandIndices[i + 1]
                    )
                    .join("\n");
                const prop = options.getCommandPropName(command);
                if (!prop) {
                    return;
                }
                const value = options.parseCommandValue(command, valueText);
                siteFix[prop] = value;
            });
            sites.push(siteFix);
        });
        return sites;
    }
    function getDomain(url) {
        try {
            return new URL(url).hostname.toLowerCase();
        } catch (error) {
            return url.split("/")[0].toLowerCase();
        }
    }
    function encodeOffsets(offsets) {
        return offsets
            .map(([offset, length]) => {
                const stringOffset = offset.toString(36);
                const stringLength = length.toString(36);
                return (
                    "0".repeat(4 - stringOffset.length) +
                    stringOffset +
                    "0".repeat(3 - stringLength.length) +
                    stringLength
                );
            })
            .join("");
    }
    function decodeOffset(offsets, index) {
        const base = (4 + 3) * index;
        const offset = parseInt(offsets.substring(base + 0, base + 4), 36);
        const length = parseInt(offsets.substring(base + 4, base + 4 + 3), 36);
        return [offset, offset + length];
    }
    function addLabel(set, label, index) {
        if (!set[label]) {
            set[label] = [index];
        } else if (!set[label].includes(index)) {
            set[label].push(index);
        }
    }
    function extractDomainLabelsFromFullyQualifiedDomainWildcard(
        fullyQualifiedDomainWildcard
    ) {
        const postfixStart = fullyQualifiedDomainWildcard.lastIndexOf("*");
        const postfix = fullyQualifiedDomainWildcard.substring(
            postfixStart + 2
        );
        if (postfixStart < 0 || postfix.length === 0) {
            return fullyQualifiedDomainWildcard.split(".");
        }
        const labels = [postfix];
        const prefix = fullyQualifiedDomainWildcard.substring(0, postfixStart);
        prefix
            .split(".")
            .filter(Boolean)
            .forEach((l) => labels.concat(l));
        return labels;
    }
    function indexConfigURLs(urls) {
        const domains = {};
        const domainLabels = {};
        const nonstandard = [];
        const domainLabelFrequencies = {};
        const domainLabelMembers = [];
        for (let index = 0; index < urls.length; index++) {
            const block = urls[index];
            const blockDomainLabels = new Set();
            for (const url of block) {
                const domain = getDomain(url);
                if (isFullyQualifiedDomain(domain)) {
                    addLabel(domains, domain, index);
                } else if (isFullyQualifiedDomainWildcard(domain)) {
                    const labels =
                        extractDomainLabelsFromFullyQualifiedDomainWildcard(
                            domain
                        );
                    domainLabelMembers.push({labels, index});
                    labels.forEach((l) => blockDomainLabels.add(l));
                } else {
                    nonstandard.push(index);
                    break;
                }
            }
            for (const label of blockDomainLabels) {
                if (domainLabelFrequencies[label]) {
                    domainLabelFrequencies[label]++;
                } else {
                    domainLabelFrequencies[label] = 1;
                }
            }
        }
        for (const {labels, index} of domainLabelMembers) {
            let label = labels[0];
            for (const currLabel of labels) {
                if (
                    domainLabelFrequencies[currLabel] <
                    domainLabelFrequencies[label]
                ) {
                    label = currLabel;
                }
            }
            addLabel(domainLabels, label, index);
        }
        return {domains, domainLabels, nonstandard};
    }
    function processSiteFixesConfigBlock(
        text,
        offsets,
        recordStart,
        recordEnd,
        urls
    ) {
        const block = text.substring(recordStart, recordEnd);
        const lines = block.split("\n");
        const commandIndices = [];
        lines.forEach((ln, i) => {
            if (ln.match(/^[A-Z]+(\s[A-Z]+){0,2}$/)) {
                commandIndices.push(i);
            }
        });
        if (commandIndices.length === 0) {
            return;
        }
        offsets.push([recordStart, recordEnd - recordStart]);
        const urls_ = parseArray(lines.slice(0, commandIndices[0]).join("\n"));
        urls.push(urls_);
    }
    function extractURLsFromSiteFixesConfig(text) {
        const urls = [];
        const offsets = [];
        let recordStart = 0;
        const delimiterRegex = /^\s*={2,}\s*$/gm;
        let delimiter;
        while ((delimiter = delimiterRegex.exec(text))) {
            const nextDelimiterStart = delimiter.index;
            const nextDelimiterEnd = delimiter.index + delimiter[0].length;
            processSiteFixesConfigBlock(
                text,
                offsets,
                recordStart,
                nextDelimiterStart,
                urls
            );
            recordStart = nextDelimiterEnd;
        }
        processSiteFixesConfigBlock(
            text,
            offsets,
            recordStart,
            text.length,
            urls
        );
        return {urls, offsets};
    }
    function indexSitesFixesConfig(text) {
        const {urls, offsets} = extractURLsFromSiteFixesConfig(text);
        const {domains, domainLabels, nonstandard} = indexConfigURLs(urls);
        return {
            offsets: encodeOffsets(offsets),
            domains,
            domainLabels,
            nonstandard,
            cacheDomainIndex: {},
            cacheSiteFix: {},
            cacheCleanupTimer: null
        };
    }
    function lookupConfigURLsInDomainLabels(
        domain,
        recordIds,
        currRecordIds,
        getAllRecordURLs
    ) {
        for (const recordId of currRecordIds) {
            const recordURLs = getAllRecordURLs(recordId);
            for (const ruleUrl of recordURLs) {
                const wildcard = getDomain(ruleUrl);
                if (
                    isFullyQualifiedDomainWildcard(wildcard) &&
                    fullyQualifiedDomainMatchesWildcard(wildcard, domain)
                ) {
                    recordIds.push(recordId);
                }
            }
        }
    }
    function lookupConfigURLs(domain, index, getAllRecordURLs) {
        const labels = domain.split(".");
        let recordIds = [];
        if (index.domainLabels.hasOwnProperty("*")) {
            recordIds = recordIds.concat(index.domainLabels["*"]);
        }
        for (const label of labels) {
            if (index.domainLabels.hasOwnProperty(label)) {
                const currRecordIds = index.domainLabels[label];
                lookupConfigURLsInDomainLabels(
                    domain,
                    recordIds,
                    currRecordIds,
                    getAllRecordURLs
                );
            }
        }
        for (let i = 0; i < labels.length; i++) {
            const substring = labels.slice(i).join(".");
            if (index.domains.hasOwnProperty(substring)) {
                recordIds = recordIds.concat(index.domains[substring]);
            }
            if (index.domainLabels.hasOwnProperty(substring)) {
                const currRecordIds = index.domainLabels[substring];
                lookupConfigURLsInDomainLabels(
                    domain,
                    recordIds,
                    currRecordIds,
                    getAllRecordURLs
                );
            }
        }
        if (index.nonstandard) {
            for (const currRecordId of index.nonstandard) {
                const urls = getAllRecordURLs(currRecordId);
                if (urls.some((url) => isURLMatched(domain, getDomain(url)))) {
                    recordIds.push(currRecordId);
                    continue;
                }
            }
        }
        recordIds = Array.from(new Set(recordIds));
        return recordIds;
    }
    function getSiteFix(text, index, options, id) {
        if (index.cacheSiteFix.hasOwnProperty(id)) {
            return index.cacheSiteFix[id];
        }
        const [blockStart, blockEnd] = decodeOffset(index.offsets, id);
        const block = text.substring(blockStart, blockEnd);
        const fix = parseSitesFixesConfig(block, options)[0];
        index.cacheSiteFix[id] = fix;
        return fix;
    }
    function scheduleCacheCleanup(index) {
        clearTimeout(index.cacheCleanupTimer);
        index.cacheCleanupTimer = setTimeout(() => {
            index.cacheCleanupTimer = null;
            index.cacheDomainIndex = {};
            index.cacheSiteFix = {};
        }, INDEX_CACHE_CLEANUP_INTERVAL_IN_MS);
    }
    function getSitesFixesFor(url, text, index, options) {
        const records = [];
        const domain = getDomain(url);
        if (!index.cacheDomainIndex[domain]) {
            index.cacheDomainIndex[domain] = lookupConfigURLs(
                domain,
                index,
                (recordId) => getSiteFix(text, index, options, recordId).url
            );
        }
        const recordIds = index.cacheDomainIndex[domain];
        for (const recordId of recordIds) {
            const fix = getSiteFix(text, index, options, recordId);
            records.push(fix);
        }
        scheduleCacheCleanup(index);
        return records;
    }
    function indexSiteListConfig(text) {
        const urls = parseArray(text);
        const urls2D = urls.map((u) => [u]);
        const {domains, domainLabels, nonstandard} = indexConfigURLs(urls2D);
        return {domains, domainLabels, nonstandard, urls};
    }
    function getSiteListFor(url, index) {
        const domain = getDomain(url);
        const recordIds = lookupConfigURLs(domain, index, (recordId) => [
            index.urls[recordId]
        ]);
        const result = [];
        for (const recordId of recordIds) {
            result.push(index.urls[recordId]);
        }
        return result;
    }
    function isURLInSiteList(url, index) {
        if (index === null) {
            return false;
        }
        const urls = getSiteListFor(url, index);
        return isURLInList(url, urls);
    }

    var FilterMode;
    (function (FilterMode) {
        FilterMode[(FilterMode["light"] = 0)] = "light";
        FilterMode[(FilterMode["dark"] = 1)] = "dark";
    })(FilterMode || (FilterMode = {}));
    function hasPatchForChromiumIssue501582() {
        return Boolean(
            compareChromeVersions(chromiumVersion, "81.0.4035.0") >= 0
        );
    }
    function hasFirefoxNewRootBehavior() {
        return Boolean(isFirefox);
    }
    function createCSSFilterStyleSheet(config, url, isTopFrame, fixes, index) {
        const filterValue = getCSSFilterValue(config);
        const reverseFilterValue = "invert(100%) hue-rotate(180deg)";
        return cssFilterStyleSheetTemplate(
            "html",
            filterValue,
            reverseFilterValue,
            config,
            url,
            isTopFrame,
            fixes,
            index
        );
    }
    function cssFilterStyleSheetTemplate(
        filterRoot,
        filterValue,
        reverseFilterValue,
        config,
        url,
        isTopFrame,
        fixes,
        index
    ) {
        const fix = getInversionFixesFor(url, fixes, index);
        const lines = [];
        lines.push("@media screen {");
        if (filterValue && isTopFrame) {
            lines.push("");
            lines.push("/* Leading rule */");
            lines.push(createLeadingRule(filterRoot, filterValue));
        }
        if (config.mode === FilterMode.dark) {
            lines.push("");
            lines.push("/* Reverse rule */");
            lines.push(createReverseRule(reverseFilterValue, fix));
        }
        if (config.useFont || config.textStroke > 0) {
            lines.push("");
            lines.push("/* Font */");
            lines.push(createTextStyle(config));
        }
        lines.push("");
        lines.push("/* Text contrast */");
        lines.push("html {");
        lines.push("  text-shadow: 0 0 0 !important;");
        lines.push("}");
        lines.push("");
        lines.push("/* Full screen */");
        [":-webkit-full-screen", ":-moz-full-screen", ":fullscreen"].forEach(
            (fullScreen) => {
                lines.push(`${fullScreen}, ${fullScreen} * {`);
                lines.push("  -webkit-filter: none !important;");
                lines.push("  filter: none !important;");
                lines.push("}");
            }
        );
        if (isTopFrame) {
            const light = [255, 255, 255];
            const bgColor =
                !hasPatchForChromiumIssue501582() &&
                !hasFirefoxNewRootBehavior() &&
                config.mode === FilterMode.dark
                    ? applyColorMatrix(light, createFilterMatrix(config)).map(
                          Math.round
                      )
                    : light;
            lines.push("");
            lines.push("/* Page background */");
            lines.push("html {");
            lines.push(`  background: rgb(${bgColor.join(",")}) !important;`);
            lines.push("}");
        }
        if (fix.css && fix.css.length > 0 && config.mode === FilterMode.dark) {
            lines.push("");
            lines.push("/* Custom rules */");
            lines.push(fix.css);
        }
        lines.push("");
        lines.push("}");
        return lines.join("\n");
    }
    function getCSSFilterValue(config) {
        const filters = [];
        if (config.mode === FilterMode.dark) {
            filters.push("invert(100%) hue-rotate(180deg)");
        }
        if (config.brightness !== 100) {
            filters.push(`brightness(${config.brightness}%)`);
        }
        if (config.contrast !== 100) {
            filters.push(`contrast(${config.contrast}%)`);
        }
        if (config.grayscale !== 0) {
            filters.push(`grayscale(${config.grayscale}%)`);
        }
        if (config.sepia !== 0) {
            filters.push(`sepia(${config.sepia}%)`);
        }
        if (filters.length === 0) {
            return null;
        }
        return filters.join(" ");
    }
    function createLeadingRule(filterRoot, filterValue) {
        return [
            `${filterRoot} {`,
            `  -webkit-filter: ${filterValue} !important;`,
            `  filter: ${filterValue} !important;`,
            "}"
        ].join("\n");
    }
    function joinSelectors(selectors) {
        return selectors.map((s) => s.replace(/\,$/, "")).join(",\n");
    }
    function createReverseRule(reverseFilterValue, fix) {
        const lines = [];
        if (fix.invert.length > 0) {
            lines.push(`${joinSelectors(fix.invert)} {`);
            lines.push(`  -webkit-filter: ${reverseFilterValue} !important;`);
            lines.push(`  filter: ${reverseFilterValue} !important;`);
            lines.push("}");
        }
        if (fix.noinvert.length > 0) {
            lines.push(`${joinSelectors(fix.noinvert)} {`);
            lines.push("  -webkit-filter: none !important;");
            lines.push("  filter: none !important;");
            lines.push("}");
        }
        if (fix.removebg.length > 0) {
            lines.push(`${joinSelectors(fix.removebg)} {`);
            lines.push("  background: white !important;");
            lines.push("}");
        }
        return lines.join("\n");
    }
    function getInversionFixesFor(url, fixes, index) {
        const inversionFixes = getSitesFixesFor(url, fixes, index, {
            commands: Object.keys(inversionFixesCommands),
            getCommandPropName: (command) => inversionFixesCommands[command],
            parseCommandValue: (command, value) => {
                if (command === "CSS") {
                    return value.trim();
                }
                return parseArray(value);
            }
        });
        const common = {
            url: inversionFixes[0].url,
            invert: inversionFixes[0].invert || [],
            noinvert: inversionFixes[0].noinvert || [],
            removebg: inversionFixes[0].removebg || [],
            css: inversionFixes[0].css || ""
        };
        if (url) {
            const matches = inversionFixes
                .slice(1)
                .filter((s) => isURLInList(url, s.url))
                .sort((a, b) => b.url[0].length - a.url[0].length);
            if (matches.length > 0) {
                const found = matches[0];
                return {
                    url: found.url,
                    invert: common.invert.concat(found.invert || []),
                    noinvert: common.noinvert.concat(found.noinvert || []),
                    removebg: common.removebg.concat(found.removebg || []),
                    css: [common.css, found.css].filter((s) => s).join("\n")
                };
            }
        }
        return common;
    }
    const inversionFixesCommands = {
        "INVERT": "invert",
        "NO INVERT": "noinvert",
        "REMOVE BG": "removebg",
        "CSS": "css"
    };
    function parseInversionFixes(text) {
        return parseSitesFixesConfig(text, {
            commands: Object.keys(inversionFixesCommands),
            getCommandPropName: (command) => inversionFixesCommands[command],
            parseCommandValue: (command, value) => {
                if (command === "CSS") {
                    return value.trim();
                }
                return parseArray(value);
            }
        });
    }
    function formatInversionFixes(inversionFixes) {
        const fixes = inversionFixes
            .slice()
            .sort((a, b) => compareURLPatterns(a.url[0], b.url[0]));
        return formatSitesFixesConfig(fixes, {
            props: Object.values(inversionFixesCommands),
            getPropCommandName: (prop) =>
                Object.entries(inversionFixesCommands).find(
                    ([, p]) => p === prop
                )[0],
            formatPropValue: (prop, value) => {
                if (prop === "css") {
                    return value.trim().replace(/\n+/g, "\n");
                }
                return formatArray(value).trim();
            },
            shouldIgnoreProp: (prop, value) => {
                if (prop === "css") {
                    return !value;
                }
                return !(Array.isArray(value) && value.length > 0);
            }
        });
    }

    const detectorHintsCommands = {
        "TARGET": "target",
        "MATCH": "match",
        "NO DARK THEME": "noDarkTheme",
        "SYSTEM THEME": "systemTheme",
        "IFRAME": "iframe"
    };
    const detectorParserOptions = {
        commands: Object.keys(detectorHintsCommands),
        getCommandPropName: (command) => detectorHintsCommands[command],
        parseCommandValue: (command, value) => {
            if (command === "TARGET") {
                return value.trim();
            }
            if (command === "NO DARK THEME" || command === "SYSTEM THEME") {
                return true;
            }
            return parseArray(value);
        }
    };
    function getDetectorHintsFor(url, text, index) {
        const fixes = getSitesFixesFor(url, text, index, detectorParserOptions);
        if (fixes.length === 0) {
            return null;
        }
        return fixes;
    }

    const cssCommentsRegex = /\/\*[\s\S]*?\*\//g;
    function removeCSSComments(cssText) {
        return cssText.replace(cssCommentsRegex, "");
    }

    function parseCSS(cssText) {
        cssText = removeCSSComments(cssText);
        cssText = cssText.trim();
        if (!cssText) {
            return [];
        }
        const rules = [];
        const excludeRanges = getTokenExclusionRanges(cssText);
        const bracketRanges = getAllOpenCloseRanges(
            cssText,
            "{",
            "}",
            excludeRanges
        );
        let ruleStart = 0;
        bracketRanges.forEach((brackets) => {
            const key = cssText.substring(ruleStart, brackets.start).trim();
            const content = cssText.substring(
                brackets.start + 1,
                brackets.end - 1
            );
            if (key.startsWith("@")) {
                const typeEndIndex = key.search(/[\s\(]/);
                const rule = {
                    type:
                        typeEndIndex < 0 ? key : key.substring(0, typeEndIndex),
                    query:
                        typeEndIndex < 0
                            ? ""
                            : key.substring(typeEndIndex).trim(),
                    rules: parseCSS(content)
                };
                rules.push(rule);
            } else {
                const rule = {
                    selectors: parseSelectors(key),
                    declarations: parseDeclarations(content)
                };
                rules.push(rule);
            }
            ruleStart = brackets.end;
        });
        return rules;
    }
    function getAllOpenCloseRanges(
        input,
        openToken,
        closeToken,
        excludeRanges = []
    ) {
        const ranges = [];
        let i = 0;
        let range;
        while (
            (range = getOpenCloseRange(
                input,
                i,
                openToken,
                closeToken,
                excludeRanges
            ))
        ) {
            ranges.push(range);
            i = range.end;
        }
        return ranges;
    }
    function getTokenExclusionRanges(cssText) {
        const singleQuoteGoesFirst =
            cssText.indexOf("'") < cssText.indexOf('"');
        const firstQuote = singleQuoteGoesFirst ? "'" : '"';
        const secondQuote = singleQuoteGoesFirst ? '"' : "'";
        const excludeRanges = getAllOpenCloseRanges(
            cssText,
            firstQuote,
            firstQuote
        );
        excludeRanges.push(
            ...getAllOpenCloseRanges(
                cssText,
                secondQuote,
                secondQuote,
                excludeRanges
            )
        );
        excludeRanges.push(
            ...getAllOpenCloseRanges(cssText, "[", "]", excludeRanges)
        );
        excludeRanges.push(
            ...getAllOpenCloseRanges(cssText, "(", ")", excludeRanges)
        );
        return excludeRanges;
    }
    function parseSelectors(selectorText) {
        const excludeRanges = getTokenExclusionRanges(selectorText);
        return splitExcluding(selectorText, ",", excludeRanges);
    }
    function parseDeclarations(cssDeclarationsText) {
        const declarations = [];
        const excludeRanges = getTokenExclusionRanges(cssDeclarationsText);
        splitExcluding(cssDeclarationsText, ";", excludeRanges).forEach(
            (part) => {
                const colonIndex = part.indexOf(":");
                if (colonIndex > 0) {
                    const importantIndex = part.indexOf("!important");
                    declarations.push({
                        property: part.substring(0, colonIndex).trim(),
                        value: part
                            .substring(
                                colonIndex + 1,
                                importantIndex > 0
                                    ? importantIndex
                                    : part.length
                            )
                            .trim(),
                        important: importantIndex > 0
                    });
                }
            }
        );
        return declarations;
    }
    function isParsedStyleRule(rule) {
        return "selectors" in rule;
    }

    function formatCSS(cssText) {
        const parsed = parseCSS(cssText);
        return formatParsedCSS(parsed);
    }
    function formatParsedCSS(parsed) {
        const lines = [];
        const tab = "    ";
        function formatRule(rule, indent) {
            if (isParsedStyleRule(rule)) {
                formatStyleRule(rule, indent);
            } else {
                formatAtRule(rule, indent);
            }
        }
        function formatAtRule({type, query, rules}, indent) {
            lines.push(`${indent}${type} ${query} {`);
            rules.forEach((child) => formatRule(child, `${indent}${tab}`));
            lines.push(`${indent}}`);
        }
        function formatStyleRule({selectors, declarations}, indent) {
            const lastSelectorIndex = selectors.length - 1;
            selectors.forEach((selector, i) => {
                lines.push(
                    `${indent}${selector}${i < lastSelectorIndex ? "," : " {"}`
                );
            });
            const sorted = sortDeclarations(declarations);
            sorted.forEach(({property, value, important}) => {
                lines.push(
                    `${indent}${tab}${property}: ${value}${important ? " !important" : ""};`
                );
            });
            lines.push(`${indent}}`);
        }
        clearEmptyRules(parsed);
        parsed.forEach((rule) => formatRule(rule, ""));
        return lines.join("\n");
    }
    function sortDeclarations(declarations) {
        const prefixRegex = /^-[a-z]-/;
        return [...declarations].sort((a, b) => {
            var _a, _b, _c, _d;
            const aProp = a.property;
            const bProp = b.property;
            const aPrefix =
                (_b =
                    (_a = aProp.match(prefixRegex)) === null || _a === void 0
                        ? void 0
                        : _a[0]) !== null && _b !== void 0
                    ? _b
                    : "";
            const bPrefix =
                (_d =
                    (_c = bProp.match(prefixRegex)) === null || _c === void 0
                        ? void 0
                        : _c[0]) !== null && _d !== void 0
                    ? _d
                    : "";
            const aNorm = aPrefix ? aProp.replace(prefixRegex, "") : aProp;
            const bNorm = bPrefix ? bProp.replace(prefixRegex, "") : bProp;
            if (aNorm === bNorm) {
                return aPrefix.localeCompare(bPrefix);
            }
            return aNorm.localeCompare(bNorm);
        });
    }
    function clearEmptyRules(rules) {
        for (let i = rules.length - 1; i >= 0; i--) {
            const rule = rules[i];
            if (isParsedStyleRule(rule)) {
                if (rule.declarations.length === 0) {
                    rules.splice(i, 1);
                }
            } else {
                clearEmptyRules(rule.rules);
                if (rule.rules.length === 0) {
                    rules.splice(i, 1);
                }
            }
        }
    }

    const dynamicThemeFixesCommands = {
        "INVERT": "invert",
        "CSS": "css",
        "IGNORE INLINE STYLE": "ignoreInlineStyle",
        "IGNORE IMAGE ANALYSIS": "ignoreImageAnalysis"
    };
    function parseDynamicThemeFixes(text) {
        return parseSitesFixesConfig(text, {
            commands: Object.keys(dynamicThemeFixesCommands),
            getCommandPropName: (command) => dynamicThemeFixesCommands[command],
            parseCommandValue: (command, value) => {
                if (command === "CSS") {
                    return value.trim();
                }
                return parseArray(value);
            }
        });
    }
    function formatDynamicThemeFixes(dynamicThemeFixes) {
        const fixes = dynamicThemeFixes
            .slice()
            .sort((a, b) => compareURLPatterns(a.url[0], b.url[0]));
        return formatSitesFixesConfig(fixes, {
            props: Object.values(dynamicThemeFixesCommands),
            getPropCommandName: (prop) =>
                Object.entries(dynamicThemeFixesCommands).find(
                    ([, p]) => p === prop
                )[0],
            formatPropValue: (prop, value) => {
                if (prop === "css") {
                    return formatCSS(value);
                }
                return formatArray(value).trim();
            },
            shouldIgnoreProp: (prop, value) => {
                if (prop === "css") {
                    return !value;
                }
                return !(Array.isArray(value) && value.length > 0);
            }
        });
    }
    function getDynamicThemeFixesFor(
        url,
        isTopFrame,
        text,
        index,
        enabledForPDF
    ) {
        const fixes = getSitesFixesFor(url, text, index, {
            commands: Object.keys(dynamicThemeFixesCommands),
            getCommandPropName: (command) => dynamicThemeFixesCommands[command],
            parseCommandValue: (command, value) => {
                if (command === "CSS") {
                    return value.trim();
                }
                return parseArray(value);
            }
        });
        if (fixes.length === 0 || fixes[0].url[0] !== "*") {
            return null;
        }
        if (enabledForPDF) {
            const commonFix = {...fixes[0]};
            const pdfFixes = [commonFix, ...fixes.slice(1)];
            const inversionFix =
                '\nembed[type="application/pdf"][src="about:blank"] { filter: invert(100%) contrast(90%); }';
            if (!commonFix.css.endsWith(inversionFix)) {
                commonFix.css += inversionFix;
            }
            if (
                ["drive.google.com", "mail.google.com"].includes(getDomain(url))
            ) {
                const nestedInversionFix =
                    'div[role="dialog"] div[role="document"]';
                if (commonFix.invert.at(-1) !== nestedInversionFix) {
                    commonFix.invert.push(nestedInversionFix);
                }
            }
            return pdfFixes;
        }
        return fixes;
    }

    const darkTheme = {
        neutralBg: [16, 20, 23],
        neutralText: [167, 158, 139],
        redBg: [64, 12, 32],
        redText: [247, 142, 102],
        greenBg: [32, 64, 48],
        greenText: [128, 204, 148],
        blueBg: [32, 48, 64],
        blueText: [128, 182, 204],
        fadeBg: [16, 20, 23, 0.5],
        fadeText: [167, 158, 139, 0.5]
    };
    const lightTheme = {
        neutralBg: [255, 242, 228],
        neutralText: [0, 0, 0],
        redBg: [255, 85, 170],
        redText: [140, 14, 48],
        greenBg: [192, 255, 170],
        greenText: [0, 128, 0],
        blueBg: [173, 215, 229],
        blueText: [28, 16, 171],
        fadeBg: [0, 0, 0, 0.5],
        fadeText: [0, 0, 0, 0.5]
    };
    function rgb([r, g, b, a]) {
        if (typeof a === "number") {
            return `rgba(${r}, ${g}, ${b}, ${a})`;
        }
        return `rgb(${r}, ${g}, ${b})`;
    }
    function mix(color1, color2, t) {
        return color1.map((c, i) => Math.round(c * (1 - t) + color2[i] * t));
    }
    function createStaticStylesheet(
        config,
        url,
        isTopFrame,
        staticThemes,
        staticThemesIndex
    ) {
        const srcTheme = config.mode === 1 ? darkTheme : lightTheme;
        const theme = Object.entries(srcTheme).reduce((t, [prop, color]) => {
            const [r, g, b, a] = color;
            t[prop] = applyColorMatrix(
                [r, g, b],
                createFilterMatrix({...config, mode: 0})
            );
            if (a !== undefined) {
                t[prop].push(a);
            }
            return t;
        }, {});
        const commonTheme = getCommonTheme(staticThemes, staticThemesIndex);
        const siteTheme = getThemeFor(url, staticThemes, staticThemesIndex);
        const lines = [];
        if (!siteTheme || !siteTheme.noCommon) {
            lines.push("/* Common theme */");
            lines.push(...ruleGenerators.map((gen) => gen(commonTheme, theme)));
        }
        if (siteTheme) {
            lines.push(`/* Theme for ${siteTheme.url.join(" ")} */`);
            lines.push(...ruleGenerators.map((gen) => gen(siteTheme, theme)));
        }
        if (config.useFont || config.textStroke > 0) {
            lines.push("/* Font */");
            lines.push(createTextStyle(config));
        }
        return lines.filter((ln) => ln).join("\n");
    }
    function createRuleGen(
        getSelectors,
        generateDeclarations,
        modifySelector = (s) => s
    ) {
        return (siteTheme, themeColors) => {
            const selectors = getSelectors(siteTheme);
            if (selectors == null || selectors.length === 0) {
                return null;
            }
            const lines = [];
            selectors.forEach((s, i) => {
                let ln = modifySelector(s);
                if (i < selectors.length - 1) {
                    ln += ",";
                } else {
                    ln += " {";
                }
                lines.push(ln);
            });
            const declarations = generateDeclarations(themeColors);
            declarations.forEach((d) => lines.push(`    ${d} !important;`));
            lines.push("}");
            return lines.join("\n");
        };
    }
    const mx = {
        bg: {
            hover: 0.075,
            active: 0.1
        },
        fg: {
            hover: 0.25,
            active: 0.5
        },
        border: 0.5
    };
    const ruleGenerators = [
        createRuleGen(
            (t) => t.neutralBg,
            (t) => [`background-color: ${rgb(t.neutralBg)}`]
        ),
        createRuleGen(
            (t) => t.neutralBgActive,
            (t) => [`background-color: ${rgb(t.neutralBg)}`]
        ),
        createRuleGen(
            (t) => t.neutralBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.neutralBg, [255, 255, 255], mx.bg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.neutralBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.neutralBg, [255, 255, 255], mx.bg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.neutralText,
            (t) => [`color: ${rgb(t.neutralText)}`]
        ),
        createRuleGen(
            (t) => t.neutralTextActive,
            (t) => [`color: ${rgb(t.neutralText)}`]
        ),
        createRuleGen(
            (t) => t.neutralTextActive,
            (t) => [
                `color: ${rgb(mix(t.neutralText, [255, 255, 255], mx.fg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.neutralTextActive,
            (t) => [
                `color: ${rgb(mix(t.neutralText, [255, 255, 255], mx.fg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.neutralBorder,
            (t) => [
                `border-color: ${rgb(mix(t.neutralBg, t.neutralText, mx.border))}`
            ]
        ),
        createRuleGen(
            (t) => t.redBg,
            (t) => [`background-color: ${rgb(t.redBg)}`]
        ),
        createRuleGen(
            (t) => t.redBgActive,
            (t) => [`background-color: ${rgb(t.redBg)}`]
        ),
        createRuleGen(
            (t) => t.redBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.redBg, [255, 0, 64], mx.bg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.redBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.redBg, [255, 0, 64], mx.bg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.redText,
            (t) => [`color: ${rgb(t.redText)}`]
        ),
        createRuleGen(
            (t) => t.redTextActive,
            (t) => [`color: ${rgb(t.redText)}`]
        ),
        createRuleGen(
            (t) => t.redTextActive,
            (t) => [
                `color: ${rgb(mix(t.redText, [255, 255, 0], mx.fg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.redTextActive,
            (t) => [
                `color: ${rgb(mix(t.redText, [255, 255, 0], mx.fg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.redBorder,
            (t) => [`border-color: ${rgb(mix(t.redBg, t.redText, mx.border))}`]
        ),
        createRuleGen(
            (t) => t.greenBg,
            (t) => [`background-color: ${rgb(t.greenBg)}`]
        ),
        createRuleGen(
            (t) => t.greenBgActive,
            (t) => [`background-color: ${rgb(t.greenBg)}`]
        ),
        createRuleGen(
            (t) => t.greenBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.greenBg, [128, 255, 182], mx.bg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.greenBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.greenBg, [128, 255, 182], mx.bg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.greenText,
            (t) => [`color: ${rgb(t.greenText)}`]
        ),
        createRuleGen(
            (t) => t.greenTextActive,
            (t) => [`color: ${rgb(t.greenText)}`]
        ),
        createRuleGen(
            (t) => t.greenTextActive,
            (t) => [
                `color: ${rgb(mix(t.greenText, [182, 255, 224], mx.fg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.greenTextActive,
            (t) => [
                `color: ${rgb(mix(t.greenText, [182, 255, 224], mx.fg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.greenBorder,
            (t) => [
                `border-color: ${rgb(mix(t.greenBg, t.greenText, mx.border))}`
            ]
        ),
        createRuleGen(
            (t) => t.blueBg,
            (t) => [`background-color: ${rgb(t.blueBg)}`]
        ),
        createRuleGen(
            (t) => t.blueBgActive,
            (t) => [`background-color: ${rgb(t.blueBg)}`]
        ),
        createRuleGen(
            (t) => t.blueBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.blueBg, [0, 128, 255], mx.bg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.blueBgActive,
            (t) => [
                `background-color: ${rgb(mix(t.blueBg, [0, 128, 255], mx.bg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.blueText,
            (t) => [`color: ${rgb(t.blueText)}`]
        ),
        createRuleGen(
            (t) => t.blueTextActive,
            (t) => [`color: ${rgb(t.blueText)}`]
        ),
        createRuleGen(
            (t) => t.blueTextActive,
            (t) => [
                `color: ${rgb(mix(t.blueText, [182, 224, 255], mx.fg.hover))}`
            ],
            (s) => `${s}:hover`
        ),
        createRuleGen(
            (t) => t.blueTextActive,
            (t) => [
                `color: ${rgb(mix(t.blueText, [182, 224, 255], mx.fg.active))}`
            ],
            (s) => `${s}:active, ${s}:focus`
        ),
        createRuleGen(
            (t) => t.blueBorder,
            (t) => [
                `border-color: ${rgb(mix(t.blueBg, t.blueText, mx.border))}`
            ]
        ),
        createRuleGen(
            (t) => t.fadeBg,
            (t) => [`background-color: ${rgb(t.fadeBg)}`]
        ),
        createRuleGen(
            (t) => t.fadeText,
            (t) => [`color: ${rgb(t.fadeText)}`]
        ),
        createRuleGen(
            (t) => t.transparentBg,
            () => ["background-color: transparent"]
        ),
        createRuleGen(
            (t) => t.noImage,
            () => ["background-image: none"]
        ),
        createRuleGen(
            (t) => t.invert,
            () => ["filter: invert(100%) hue-rotate(180deg)"]
        )
    ];
    const staticThemeCommands = {
        "NO COMMON": "noCommon",
        "NEUTRAL BG": "neutralBg",
        "NEUTRAL BG ACTIVE": "neutralBgActive",
        "NEUTRAL TEXT": "neutralText",
        "NEUTRAL TEXT ACTIVE": "neutralTextActive",
        "NEUTRAL BORDER": "neutralBorder",
        "RED BG": "redBg",
        "RED BG ACTIVE": "redBgActive",
        "RED TEXT": "redText",
        "RED TEXT ACTIVE": "redTextActive",
        "RED BORDER": "redBorder",
        "GREEN BG": "greenBg",
        "GREEN BG ACTIVE": "greenBgActive",
        "GREEN TEXT": "greenText",
        "GREEN TEXT ACTIVE": "greenTextActive",
        "GREEN BORDER": "greenBorder",
        "BLUE BG": "blueBg",
        "BLUE BG ACTIVE": "blueBgActive",
        "BLUE TEXT": "blueText",
        "BLUE TEXT ACTIVE": "blueTextActive",
        "BLUE BORDER": "blueBorder",
        "FADE BG": "fadeBg",
        "FADE TEXT": "fadeText",
        "TRANSPARENT BG": "transparentBg",
        "NO IMAGE": "noImage",
        "INVERT": "invert"
    };
    function parseStaticThemes($themes) {
        return parseSitesFixesConfig($themes, {
            commands: Object.keys(staticThemeCommands),
            getCommandPropName: (command) => staticThemeCommands[command],
            parseCommandValue: (command, value) => {
                if (command === "NO COMMON") {
                    return true;
                }
                return parseArray(value);
            }
        });
    }
    function camelCaseToUpperCase(text) {
        return text.replace(/([a-z])([A-Z])/g, "$1 $2").toUpperCase();
    }
    function formatStaticThemes(staticThemes) {
        const themes = staticThemes
            .slice()
            .sort((a, b) => compareURLPatterns(a.url[0], b.url[0]));
        return formatSitesFixesConfig(themes, {
            props: Object.values(staticThemeCommands),
            getPropCommandName: camelCaseToUpperCase,
            formatPropValue: (prop, value) => {
                if (prop === "noCommon") {
                    return "";
                }
                return formatArray(value).trim();
            },
            shouldIgnoreProp: (prop, value) => {
                if (prop === "noCommon") {
                    return !value;
                }
                return !(Array.isArray(value) && value.length > 0);
            }
        });
    }
    function getCommonTheme(staticThemes, staticThemesIndex) {
        const length = parseInt(
            staticThemesIndex.offsets.substring(4, 4 + 3),
            36
        );
        const staticThemeText = staticThemes.substring(0, length);
        return parseStaticThemes(staticThemeText)[0];
    }
    function getThemeFor(url, staticThemes, staticThemesIndex) {
        const themes = getSitesFixesFor(url, staticThemes, staticThemesIndex, {
            commands: Object.keys(staticThemeCommands),
            getCommandPropName: (command) => staticThemeCommands[command],
            parseCommandValue: (command, value) => {
                if (command === "NO COMMON") {
                    return true;
                }
                return parseArray(value);
            }
        });
        const sortedBySpecificity = themes
            .slice(1)
            .map((theme) => {
                return {
                    specificity: isURLInList(url, theme.url)
                        ? theme.url[0].length
                        : 0,
                    theme
                };
            })
            .filter(({specificity}) => specificity > 0)
            .sort((a, b) => b.specificity - a.specificity);
        if (sortedBySpecificity.length === 0) {
            return null;
        }
        return sortedBySpecificity[0].theme;
    }

    function createSVGFilterStylesheet(config, url, isTopFrame, fixes, index) {
        let filterValue;
        let reverseFilterValue;
        {
            filterValue = "url(#dark-reader-filter)";
            reverseFilterValue = "url(#dark-reader-reverse-filter)";
        }
        const filterRoot = "html";
        return cssFilterStyleSheetTemplate(
            filterRoot,
            filterValue,
            reverseFilterValue,
            config,
            url,
            isTopFrame,
            fixes,
            index
        );
    }
    function toSVGMatrix(matrix) {
        return matrix
            .slice(0, 4)
            .map((m) => m.map((m) => m.toFixed(3)).join(" "))
            .join(" ");
    }
    function getSVGFilterMatrixValue(config) {
        return toSVGMatrix(createFilterMatrix(config));
    }
    function getSVGReverseFilterMatrixValue() {
        return toSVGMatrix(Matrix.invertNHue());
    }

    var ThemeEngine;
    (function (ThemeEngine) {
        ThemeEngine["cssFilter"] = "cssFilter";
        ThemeEngine["svgFilter"] = "svgFilter";
        ThemeEngine["staticTheme"] = "staticTheme";
        ThemeEngine["dynamicTheme"] = "dynamicTheme";
    })(ThemeEngine || (ThemeEngine = {}));

    var AutomationMode;
    (function (AutomationMode) {
        AutomationMode["NONE"] = "";
        AutomationMode["TIME"] = "time";
        AutomationMode["SYSTEM"] = "system";
        AutomationMode["LOCATION"] = "location";
    })(AutomationMode || (AutomationMode = {}));

    function debounce(delay, fn) {
        let timeoutId = null;
        return (...args) => {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
            timeoutId = setTimeout(() => {
                timeoutId = null;
                fn(...args);
            }, delay);
        };
    }

    class PromiseBarrier {
        constructor() {
            this.resolves = [];
            this.rejects = [];
            this.wasResolved = false;
            this.wasRejected = false;
        }
        async entry() {
            if (this.wasResolved) {
                return Promise.resolve(this.resolution);
            }
            if (this.wasRejected) {
                return Promise.reject(this.reason);
            }
            return new Promise((resolve, reject) => {
                this.resolves.push(resolve);
                this.rejects.push(reject);
            });
        }
        async resolve(value) {
            if (this.wasRejected || this.wasResolved) {
                return;
            }
            this.wasResolved = true;
            this.resolution = value;
            this.resolves.forEach((resolve) => resolve(value));
            this.resolves = [];
            this.rejects = [];
            return new Promise((resolve) => setTimeout(() => resolve()));
        }
        async reject(reason) {
            if (this.wasRejected || this.wasResolved) {
                return;
            }
            this.wasRejected = true;
            this.reason = reason;
            this.rejects.forEach((reject) => reject(reason));
            this.resolves = [];
            this.rejects = [];
            return new Promise((resolve) => setTimeout(() => resolve()));
        }
        isPending() {
            return !this.wasResolved && !this.wasRejected;
        }
        isFulfilled() {
            return this.wasResolved;
        }
        isRejected() {
            return this.wasRejected;
        }
    }

    var StateManagerImplState;
    (function (StateManagerImplState) {
        StateManagerImplState[(StateManagerImplState["INITIAL"] = 0)] =
            "INITIAL";
        StateManagerImplState[(StateManagerImplState["LOADING"] = 1)] =
            "LOADING";
        StateManagerImplState[(StateManagerImplState["READY"] = 2)] = "READY";
        StateManagerImplState[(StateManagerImplState["SAVING"] = 3)] = "SAVING";
        StateManagerImplState[(StateManagerImplState["SAVING_OVERRIDE"] = 4)] =
            "SAVING_OVERRIDE";
        StateManagerImplState[(StateManagerImplState["ONCHANGE_RACE"] = 5)] =
            "ONCHANGE_RACE";
        StateManagerImplState[(StateManagerImplState["RECOVERY"] = 6)] =
            "RECOVERY";
    })(StateManagerImplState || (StateManagerImplState = {}));

    class StateManager {
        constructor(localStorageKey, parent, defaults, logWarn) {}
        async saveState() {
            if (this.stateManager) {
                return this.stateManager.saveState();
            }
        }
        async loadState() {
            if (this.stateManager) {
                return this.stateManager.loadState();
            }
        }
    }

    async function queryTabs(query = {}) {
        return new Promise((resolve) => chrome.tabs.query(query, resolve));
    }
    async function getActiveTab() {
        let tab = (
            await queryTabs({
                active: true,
                lastFocusedWindow: true,
                windowType: "normal"
            })
        )[0];
        if (!tab) {
            tab = (
                await queryTabs({
                    active: true,
                    lastFocusedWindow: true,
                    windowType: "app"
                })
            )[0];
        }
        if (!tab) {
            tab = (
                await queryTabs({
                    active: true,
                    windowType: "normal"
                })
            )[0];
        }
        if (!tab) {
            tab = (
                await queryTabs({
                    active: true,
                    windowType: "app"
                })
            )[0];
        }
        return tab || null;
    }

    const DEFAULT_COLORS = {
        darkScheme: {
            background: "#181a1b",
            text: "#e8e6e3"
        },
        lightScheme: {
            background: "#dcdad7",
            text: "#181a1b"
        }
    };
    const DEFAULT_THEME = {
        mode: 1,
        brightness: 100,
        contrast: 100,
        grayscale: 0,
        sepia: 0,
        useFont: false,
        fontFamily: isMacOS
            ? "Helvetica Neue"
            : isWindows
              ? "Segoe UI"
              : "Open Sans",
        textStroke: 0,
        engine: ThemeEngine.dynamicTheme,
        stylesheet: "",
        darkSchemeBackgroundColor: DEFAULT_COLORS.darkScheme.background,
        darkSchemeTextColor: DEFAULT_COLORS.darkScheme.text,
        lightSchemeBackgroundColor: DEFAULT_COLORS.lightScheme.background,
        lightSchemeTextColor: DEFAULT_COLORS.lightScheme.text,
        scrollbarColor: "",
        selectionColor: "auto",
        styleSystemControls: !isCSSColorSchemePropSupported,
        lightColorScheme: "Default",
        darkColorScheme: "Default",
        immediateModify: false
    };
    const DEFAULT_COLORSCHEME = {
        light: {
            Default: {
                backgroundColor: DEFAULT_COLORS.lightScheme.background,
                textColor: DEFAULT_COLORS.lightScheme.text
            }
        },
        dark: {
            Default: {
                backgroundColor: DEFAULT_COLORS.darkScheme.background,
                textColor: DEFAULT_COLORS.darkScheme.text
            }
        }
    };
    const filterModeSites = [
        "*.officeapps.live.com",
        "*.sharepoint.com",
        "docs.google.com",
        "onedrive.live.com"
    ];
    const DEFAULT_SETTINGS = {
        schemeVersion: 0,
        enabled: true,
        fetchNews: true,
        theme: DEFAULT_THEME,
        presets: [],
        customThemes: filterModeSites.map((url) => {
            const engine = ThemeEngine.cssFilter;
            return {
                url: [url],
                theme: {...DEFAULT_THEME, engine},
                builtIn: true
            };
        }),
        enabledByDefault: true,
        enabledFor: [],
        disabledFor: [],
        changeBrowserTheme: false,
        syncSettings: true,
        syncSitesFixes: false,
        automation: {
            enabled: isEdge && isMobile ? true : false,
            mode:
                isEdge && isMobile
                    ? AutomationMode.SYSTEM
                    : AutomationMode.NONE,
            behavior: "OnOff"
        },
        time: {
            activation: "18:00",
            deactivation: "9:00"
        },
        location: {
            latitude: null,
            longitude: null
        },
        previewNewDesign: false,
        previewNewestDesign: false,
        enableForPDF: true,
        enableForProtectedPages: false,
        enableContextMenus: false,
        detectDarkTheme: true
    };

    const SEPERATOR = "=".repeat(32);
    const backgroundPropertyLength = "background: ".length;
    const textPropertyLength = "text: ".length;
    const humanizeNumber = (number) => {
        if (number > 3) {
            return `${number}th`;
        }
        switch (number) {
            case 0:
                return "0";
            case 1:
                return "1st";
            case 2:
                return "2nd";
            case 3:
                return "3rd";
        }
    };
    const isValidHexColor = (color) => {
        return /^#([0-9a-fA-F]{3}){1,2}$/.test(color);
    };
    function parseColorSchemeConfig(config) {
        const sections = config.split(`${SEPERATOR}\n\n`);
        const definedColorSchemeNames = new Set();
        let lastDefinedColorSchemeName = "";
        const definedColorSchemes = {
            light: {},
            dark: {}
        };
        let interrupt = false;
        let error = null;
        const throwError = (message) => {
            if (!interrupt) {
                interrupt = true;
                error = message;
            }
        };
        sections.forEach((section) => {
            if (interrupt) {
                return;
            }
            const lines = section.split("\n");
            const name = lines[0];
            if (!name) {
                throwError("No color scheme name was found.");
                return;
            }
            if (definedColorSchemeNames.has(name)) {
                throwError(
                    `The color scheme name "${name}" is already defined.`
                );
                return;
            }
            if (
                lastDefinedColorSchemeName &&
                lastDefinedColorSchemeName !== "Default" &&
                name.localeCompare(lastDefinedColorSchemeName) < 0
            ) {
                throwError(
                    `The color scheme name "${name}" is not in alphabetical order.`
                );
                return;
            }
            lastDefinedColorSchemeName = name;
            definedColorSchemeNames.add(name);
            if (lines[1]) {
                throwError(
                    `The second line of the color scheme "${name}" is not empty.`
                );
                return;
            }
            const checkVariant = (lineIndex, isSecondVariant) => {
                const variant = lines[lineIndex];
                if (!variant) {
                    throwError(
                        `The third line of the color scheme "${name}" is not defined.`
                    );
                    return;
                }
                if (
                    variant !== "LIGHT" &&
                    variant !== "DARK" &&
                    isSecondVariant &&
                    variant === "Light"
                ) {
                    throwError(
                        `The ${humanizeNumber(lineIndex)} line of the color scheme "${name}" is not a valid variant.`
                    );
                    return;
                }
                const firstProperty = lines[lineIndex + 1];
                if (!firstProperty) {
                    throwError(
                        `The ${humanizeNumber(lineIndex + 1)} line of the color scheme "${name}" is not defined.`
                    );
                    return;
                }
                if (!firstProperty.startsWith("background: ")) {
                    throwError(
                        `The ${humanizeNumber(lineIndex + 1)} line of the color scheme "${name}" is not background-color property.`
                    );
                    return;
                }
                const backgroundColor = firstProperty.slice(
                    backgroundPropertyLength
                );
                if (!isValidHexColor(backgroundColor)) {
                    throwError(
                        `The ${humanizeNumber(lineIndex + 1)} line of the color scheme "${name}" is not a valid hex color.`
                    );
                    return;
                }
                const secondProperty = lines[lineIndex + 2];
                if (!secondProperty) {
                    throwError(
                        `The ${humanizeNumber(lineIndex + 2)} line of the color scheme "${name}" is not defined.`
                    );
                    return;
                }
                if (!secondProperty.startsWith("text: ")) {
                    throwError(
                        `The ${humanizeNumber(lineIndex + 2)} line of the color scheme "${name}" is not text-color property.`
                    );
                    return;
                }
                const textColor = secondProperty.slice(textPropertyLength);
                if (!isValidHexColor(textColor)) {
                    throwError(
                        `The ${humanizeNumber(lineIndex + 2)} line of the color scheme "${name}" is not a valid hex color.`
                    );
                    return;
                }
                return {
                    backgroundColor,
                    textColor,
                    variant
                };
            };
            const firstVariant = checkVariant(2, false);
            const isFirstVariantLight = firstVariant.variant === "LIGHT";
            delete firstVariant.variant;
            if (interrupt) {
                return;
            }
            let secondVariant = null;
            let isSecondVariantLight = false;
            if (lines[6]) {
                secondVariant = checkVariant(6, true);
                isSecondVariantLight = secondVariant.variant === "LIGHT";
                delete secondVariant.variant;
                if (interrupt) {
                    return;
                }
                if (lines.length > 11 || lines[9] || lines[10]) {
                    throwError(
                        `The color scheme "${name}" doesn't end with 1 new line.`
                    );
                    return;
                }
            } else if (lines.length > 7) {
                throwError(
                    `The color scheme "${name}" doesn't end with 1 new line.`
                );
                return;
            }
            if (secondVariant) {
                if (isFirstVariantLight === isSecondVariantLight) {
                    throwError(
                        `The color scheme "${name}" has the same variant twice.`
                    );
                    return;
                }
                if (isFirstVariantLight) {
                    definedColorSchemes.light[name] = firstVariant;
                    definedColorSchemes.dark[name] = secondVariant;
                } else {
                    definedColorSchemes.light[name] = secondVariant;
                    definedColorSchemes.dark[name] = firstVariant;
                }
            } else if (isFirstVariantLight) {
                definedColorSchemes.light[name] = firstVariant;
            } else {
                definedColorSchemes.dark[name] = firstVariant;
            }
        });
        return {result: definedColorSchemes, error: error};
    }

    function isBoolean(x) {
        return typeof x === "boolean";
    }
    function isPlainObject(x) {
        return typeof x === "object" && x != null && !Array.isArray(x);
    }
    function isArray(x) {
        return Array.isArray(x);
    }
    function isString(x) {
        return typeof x === "string";
    }
    function isNonEmptyString(x) {
        return x && isString(x);
    }
    function isNonEmptyArrayOfNonEmptyStrings(x) {
        return (
            Array.isArray(x) &&
            x.length > 0 &&
            x.every((s) => isNonEmptyString(s))
        );
    }
    function isRegExpMatch(regexp) {
        return (x) => {
            return isString(x) && x.match(regexp) != null;
        };
    }
    const isTime = isRegExpMatch(
        /^((0?[0-9])|(1[0-9])|(2[0-3])):([0-5][0-9])$/
    );
    function isNumber(x) {
        return typeof x === "number" && !isNaN(x);
    }
    function isNumberBetween(min, max) {
        return (x) => {
            return isNumber(x) && x >= min && x <= max;
        };
    }
    function isOneOf(...values) {
        return (x) => values.includes(x);
    }
    function hasRequiredProperties(obj, keys) {
        return keys.every((key) => obj.hasOwnProperty(key));
    }
    function createValidator() {
        const errors = [];
        function validateProperty(obj, key, validator, fallback) {
            if (!obj.hasOwnProperty(key) || validator(obj[key])) {
                return;
            }
            errors.push(
                `Unexpected value for "${key}": ${JSON.stringify(obj[key])}`
            );
            obj[key] = fallback[key];
        }
        function validateArray(obj, key, validator) {
            if (!obj.hasOwnProperty(key)) {
                return;
            }
            const wrongValues = new Set();
            const arr = obj[key];
            for (let i = 0; i < arr.length; i++) {
                if (!validator(arr[i])) {
                    wrongValues.add(arr[i]);
                    arr.splice(i, 1);
                    i--;
                }
            }
            if (wrongValues.size > 0) {
                errors.push(
                    `Array "${key}" has wrong values: ${Array.from(wrongValues)
                        .map((v) => JSON.stringify(v))
                        .join("; ")}`
                );
            }
        }
        return {validateProperty, validateArray, errors};
    }
    function validateSettings(settings) {
        if (!isPlainObject(settings)) {
            return {
                errors: ["Settings are not a plain object"],
                settings: DEFAULT_SETTINGS
            };
        }
        const {validateProperty, validateArray, errors} = createValidator();
        const isValidPresetTheme = (theme) => {
            if (!isPlainObject(theme)) {
                return false;
            }
            const {errors: themeErrors} = validateTheme(theme);
            return themeErrors.length === 0;
        };
        validateProperty(settings, "schemeVersion", isNumber, DEFAULT_SETTINGS);
        validateProperty(settings, "enabled", isBoolean, DEFAULT_SETTINGS);
        validateProperty(settings, "fetchNews", isBoolean, DEFAULT_SETTINGS);
        validateProperty(settings, "theme", isPlainObject, DEFAULT_SETTINGS);
        const {errors: themeErrors} = validateTheme(settings.theme);
        errors.push(...themeErrors);
        validateProperty(settings, "presets", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "presets", (preset) => {
            const presetValidator = createValidator();
            if (
                !(
                    isPlainObject(preset) &&
                    hasRequiredProperties(preset, [
                        "id",
                        "name",
                        "urls",
                        "theme"
                    ])
                )
            ) {
                return false;
            }
            presetValidator.validateProperty(
                preset,
                "id",
                isNonEmptyString,
                preset
            );
            presetValidator.validateProperty(
                preset,
                "name",
                isNonEmptyString,
                preset
            );
            presetValidator.validateProperty(
                preset,
                "urls",
                isNonEmptyArrayOfNonEmptyStrings,
                preset
            );
            presetValidator.validateProperty(
                preset,
                "theme",
                isValidPresetTheme,
                preset
            );
            return presetValidator.errors.length === 0;
        });
        validateProperty(settings, "customThemes", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "customThemes", (custom) => {
            if (
                !(
                    isPlainObject(custom) &&
                    hasRequiredProperties(custom, ["url", "theme"])
                )
            ) {
                return false;
            }
            const presetValidator = createValidator();
            presetValidator.validateProperty(
                custom,
                "url",
                isNonEmptyArrayOfNonEmptyStrings,
                custom
            );
            presetValidator.validateProperty(
                custom,
                "theme",
                isValidPresetTheme,
                custom
            );
            return presetValidator.errors.length === 0;
        });
        validateProperty(settings, "enabledFor", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "enabledFor", isNonEmptyString);
        validateProperty(settings, "disabledFor", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "disabledFor", isNonEmptyString);
        validateProperty(
            settings,
            "enabledByDefault",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "changeBrowserTheme",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(settings, "syncSettings", isBoolean, DEFAULT_SETTINGS);
        validateProperty(
            settings,
            "syncSitesFixes",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "automation",
            (automation) => {
                if (!isPlainObject(automation)) {
                    return false;
                }
                const automationValidator = createValidator();
                automationValidator.validateProperty(
                    automation,
                    "enabled",
                    isBoolean,
                    automation
                );
                automationValidator.validateProperty(
                    automation,
                    "mode",
                    isOneOf(
                        AutomationMode.SYSTEM,
                        AutomationMode.TIME,
                        AutomationMode.LOCATION,
                        AutomationMode.NONE
                    ),
                    automation
                );
                automationValidator.validateProperty(
                    automation,
                    "behavior",
                    isOneOf("OnOff", "Scheme"),
                    automation
                );
                return automationValidator.errors.length === 0;
            },
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            AutomationMode.TIME,
            (time) => {
                if (!isPlainObject(time)) {
                    return false;
                }
                const timeValidator = createValidator();
                timeValidator.validateProperty(
                    time,
                    "activation",
                    isTime,
                    time
                );
                timeValidator.validateProperty(
                    time,
                    "deactivation",
                    isTime,
                    time
                );
                return timeValidator.errors.length === 0;
            },
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            AutomationMode.LOCATION,
            (location) => {
                if (!isPlainObject(location)) {
                    return false;
                }
                const locValidator = createValidator();
                const isValidLoc = (x) => x === null || isNumber(x);
                locValidator.validateProperty(
                    location,
                    "latitude",
                    isValidLoc,
                    location
                );
                locValidator.validateProperty(
                    location,
                    "longitude",
                    isValidLoc,
                    location
                );
                return locValidator.errors.length === 0;
            },
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "previewNewDesign",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "previewNewestDesign",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(settings, "enableForPDF", isBoolean, DEFAULT_SETTINGS);
        validateProperty(
            settings,
            "enableForProtectedPages",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "enableContextMenus",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "detectDarkTheme",
            isBoolean,
            DEFAULT_SETTINGS
        );
        return {errors, settings};
    }
    function validateTheme(theme) {
        if (!isPlainObject(theme)) {
            return {
                errors: ["Theme is not a plain object"],
                theme: DEFAULT_THEME
            };
        }
        const {validateProperty, errors} = createValidator();
        validateProperty(theme, "mode", isOneOf(0, 1), DEFAULT_THEME);
        validateProperty(
            theme,
            "brightness",
            isNumberBetween(0, 200),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "contrast",
            isNumberBetween(0, 200),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "grayscale",
            isNumberBetween(0, 100),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "sepia",
            isNumberBetween(0, 100),
            DEFAULT_THEME
        );
        validateProperty(theme, "useFont", isBoolean, DEFAULT_THEME);
        validateProperty(theme, "fontFamily", isNonEmptyString, DEFAULT_THEME);
        validateProperty(
            theme,
            "textStroke",
            isNumberBetween(0, 1),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "engine",
            isOneOf("dynamicTheme", "staticTheme", "cssFilter", "svgFilter"),
            DEFAULT_THEME
        );
        validateProperty(theme, "stylesheet", isString, DEFAULT_THEME);
        validateProperty(
            theme,
            "darkSchemeBackgroundColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "darkSchemeTextColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "lightSchemeBackgroundColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "lightSchemeTextColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "scrollbarColor",
            (x) => x === "" || isRegExpMatch(/^(auto)|(#[0-9a-f]{6})$/i)(x),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "selectionColor",
            isRegExpMatch(/^(auto)|(#[0-9a-f]{6})$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "styleSystemControls",
            isBoolean,
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "lightColorScheme",
            isNonEmptyString,
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "darkColorScheme",
            isNonEmptyString,
            DEFAULT_THEME
        );
        validateProperty(theme, "immediateModify", isBoolean, DEFAULT_THEME);
        return {errors, theme};
    }

    function logInfo(...args) {}
    function logWarn(...args) {}
    function logAssert(...args) {}
    function ASSERT(description, condition) {
        if (!condition) {
            logAssert(description);
        }
    }

    var _a$1;
    const SAVE_TIMEOUT = 1000;
    class UserStorage {
        static async loadSettings() {
            if (!_a$1.settings) {
                _a$1.settings = await _a$1.loadSettingsFromStorage();
            }
        }
        static fillDefaults(settings) {
            settings.theme = {...DEFAULT_THEME, ...settings.theme};
            settings.time = {...DEFAULT_SETTINGS.time, ...settings.time};
            settings.presets.forEach((preset) => {
                preset.theme = {...DEFAULT_THEME, ...preset.theme};
            });
            settings.customThemes.forEach((site) => {
                site.theme = {...DEFAULT_THEME, ...site.theme};
            });
            if (settings.customThemes.length === 0) {
                settings.customThemes = DEFAULT_SETTINGS.customThemes;
            }
        }
        static migrateAutomationSettings(settings) {
            if (typeof settings.automation === "string") {
                const automationMode = settings.automation;
                const automationBehavior = settings.automationBehaviour;
                if (settings.automation === "") {
                    settings.automation = {
                        enabled: false,
                        mode: automationMode,
                        behavior: automationBehavior
                    };
                } else {
                    settings.automation = {
                        enabled: true,
                        mode: automationMode,
                        behavior: automationBehavior
                    };
                }
                delete settings.automationBehaviour;
            }
        }
        static migrateSiteListsV2(deprecated) {
            var _b, _c, _d;
            const settings = {};
            settings.enabledByDefault = !deprecated.applyToListedOnly;
            if (settings.enabledByDefault) {
                settings.disabledFor =
                    (_b = deprecated.siteList) !== null && _b !== void 0
                        ? _b
                        : [];
                settings.enabledFor =
                    (_c = deprecated.siteListEnabled) !== null && _c !== void 0
                        ? _c
                        : [];
            } else {
                settings.disabledFor = [];
                settings.enabledFor =
                    (_d = deprecated.siteList) !== null && _d !== void 0
                        ? _d
                        : [];
            }
            return settings;
        }
        static migrateBuiltInSVGFilterToCSSFilter(settings) {
            var _b;
            (_b =
                settings === null || settings === void 0
                    ? void 0
                    : settings.customThemes) === null || _b === void 0
                ? void 0
                : _b.forEach((c) => {
                      var _b, _c;
                      if (
                          ((_b =
                              c === null || c === void 0 ? void 0 : c.theme) ===
                              null || _b === void 0
                              ? void 0
                              : _b.engine) === ThemeEngine.svgFilter &&
                          (c.builtIn ||
                              ((_c = c.url) === null || _c === void 0
                                  ? void 0
                                  : _c.includes("docs.google.com")))
                      ) {
                          c.theme.engine = ThemeEngine.cssFilter;
                      }
                  });
        }
        static async loadSettingsFromStorage() {
            if (_a$1.loadBarrier) {
                return await _a$1.loadBarrier.entry();
            }
            _a$1.loadBarrier = new PromiseBarrier();
            let local = await readLocalStorage(DEFAULT_SETTINGS);
            if (local.schemeVersion < 2) {
                const sync = await readSyncStorage({schemeVersion: 0});
                if (!sync || sync.schemeVersion < 2) {
                    const deprecatedDefaults = {
                        siteList: [],
                        siteListEnabled: [],
                        applyToListedOnly: false
                    };
                    const localDeprecated =
                        await readLocalStorage(deprecatedDefaults);
                    const localTransformed =
                        _a$1.migrateSiteListsV2(localDeprecated);
                    await writeLocalStorage({
                        schemeVersion: 2,
                        ...localTransformed
                    });
                    await removeLocalStorage(Object.keys(deprecatedDefaults));
                    const syncDeprecated =
                        await readSyncStorage(deprecatedDefaults);
                    const syncTransformed =
                        _a$1.migrateSiteListsV2(syncDeprecated);
                    await writeSyncStorage({
                        schemeVersion: 2,
                        ...syncTransformed
                    });
                    await removeSyncStorage(Object.keys(deprecatedDefaults));
                    local = await readLocalStorage(DEFAULT_SETTINGS);
                }
            }
            const {errors: localCfgErrors} = validateSettings(local);
            localCfgErrors.forEach((err) => logWarn(err));
            if (local.syncSettings == null) {
                local.syncSettings = DEFAULT_SETTINGS.syncSettings;
            }
            if (!local.syncSettings) {
                _a$1.migrateAutomationSettings(local);
                _a$1.migrateBuiltInSVGFilterToCSSFilter(local);
                _a$1.fillDefaults(local);
                _a$1.loadBarrier.resolve(local);
                return local;
            }
            const $sync = await readSyncStorage(DEFAULT_SETTINGS);
            if (!$sync) {
                local.syncSettings = false;
                _a$1.set({syncSettings: false});
                _a$1.saveSyncSetting(false);
                _a$1.loadBarrier.resolve(local);
                return local;
            }
            const {errors: syncCfgErrors} = validateSettings($sync);
            syncCfgErrors.forEach((err) => logWarn(err));
            _a$1.migrateAutomationSettings($sync);
            _a$1.migrateBuiltInSVGFilterToCSSFilter($sync);
            _a$1.fillDefaults($sync);
            _a$1.loadBarrier.resolve($sync);
            return $sync;
        }
        static async saveSettings() {
            if (!_a$1.settings) {
                return;
            }
            await _a$1.saveSettingsIntoStorage();
        }
        static async saveSyncSetting(sync) {
            const obj = {syncSettings: sync};
            await writeLocalStorage(obj);
            try {
                await writeSyncStorage(obj);
            } catch (err) {
                logWarn(
                    "Settings synchronization was disabled due to error:",
                    chrome.runtime.lastError
                );
                _a$1.set({syncSettings: false});
            }
        }
        static set($settings) {
            if (!_a$1.settings) {
                return;
            }
            const filterSiteList = (siteList) => {
                if (!Array.isArray(siteList)) {
                    const list = [];
                    for (const key in siteList) {
                        const index = Number(key);
                        if (!isNaN(index)) {
                            list[index] = siteList[key];
                        }
                    }
                    siteList = list;
                }
                return siteList.filter((pattern) => {
                    let isOK = false;
                    try {
                        isURLMatched("https://google.com/", pattern);
                        isURLMatched("[::1]:1337", pattern);
                        isOK = true;
                    } catch (err) {}
                    return isOK && pattern !== "/";
                });
            };
            const {enabledFor, disabledFor} = $settings;
            const updatedSettings = {..._a$1.settings, ...$settings};
            if (enabledFor) {
                updatedSettings.enabledFor = filterSiteList(enabledFor);
            }
            if (disabledFor) {
                updatedSettings.disabledFor = filterSiteList(disabledFor);
            }
            _a$1.settings = updatedSettings;
        }
    }
    _a$1 = UserStorage;
    UserStorage.saveSettingsIntoStorage = debounce(SAVE_TIMEOUT, async () => {
        if (_a$1.saveStorageBarrier) {
            await _a$1.saveStorageBarrier.entry();
            return;
        }
        _a$1.saveStorageBarrier = new PromiseBarrier();
        const settings = _a$1.settings;
        if (settings.syncSettings) {
            try {
                await writeSyncStorage(settings);
            } catch (err) {
                logWarn(
                    "Settings synchronization was disabled due to error:",
                    chrome.runtime.lastError
                );
                _a$1.set({syncSettings: false});
                await _a$1.saveSyncSetting(false);
                await writeLocalStorage(settings);
            }
        } else {
            await writeLocalStorage(settings);
        }
        _a$1.saveStorageBarrier.resolve();
        _a$1.saveStorageBarrier = null;
    });

    async function getOKResponse(url, mimeType, origin) {
        const credentials =
            origin && url.startsWith(`${origin}/`) ? undefined : "omit";
        const response = await fetch(url, {
            cache: "force-cache",
            credentials,
            referrer: origin
        });
        if (
            mimeType &&
            !response.headers.get("Content-Type").startsWith(mimeType)
        ) {
            throw new Error(`Mime type mismatch when loading ${url}`);
        }
        if (!response.ok) {
            throw new Error(
                `Unable to load ${url} ${response.status} ${response.statusText}`
            );
        }
        return response;
    }
    async function loadAsDataURL(url, mimeType) {
        const response = await getOKResponse(url, mimeType);
        return await readResponseAsDataURL(response);
    }
    async function readResponseAsDataURL(response) {
        const blob = await response.blob();
        const dataURL = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        });
        return dataURL;
    }
    async function loadAsText(url, mimeType, origin) {
        const response = await getOKResponse(url, mimeType, origin);
        return await response.text();
    }

    async function readText(params) {
        return new Promise((resolve, reject) => {
            if (isXMLHttpRequestSupported) {
                const request = new XMLHttpRequest();
                request.overrideMimeType("text/plain");
                request.open("GET", params.url, true);
                request.onload = () => {
                    if (request.status >= 200 && request.status < 300) {
                        resolve(request.responseText);
                    } else {
                        reject(
                            new Error(
                                `${request.status}: ${request.statusText}`
                            )
                        );
                    }
                };
                request.onerror = () =>
                    reject(
                        new Error(`${request.status}: ${request.statusText}`)
                    );
                if (params.timeout) {
                    request.timeout = params.timeout;
                    request.ontimeout = () =>
                        reject(
                            new Error("File loading stopped due to timeout")
                        );
                }
                request.send();
            } else if (isFetchSupported) {
                let abortController;
                let signal;
                let timedOut = false;
                if (params.timeout) {
                    abortController = new AbortController();
                    signal = abortController.signal;
                    setTimeout(() => {
                        abortController.abort();
                        timedOut = true;
                    }, params.timeout);
                }
                fetch(params.url, {signal})
                    .then((response) => {
                        if (response.status >= 200 && response.status < 300) {
                            resolve(response.text());
                        } else {
                            reject(
                                new Error(
                                    `${response.status}: ${response.statusText}`
                                )
                            );
                        }
                    })
                    .catch((error) => {
                        if (timedOut) {
                            reject(
                                new Error("File loading stopped due to timeout")
                            );
                        } else {
                            reject(error);
                        }
                    });
            } else {
                reject(
                    new Error(
                        `Neither XMLHttpRequest nor Fetch API are accessible!`
                    )
                );
            }
        });
    }
    class LimitedCacheStorage {
        constructor() {
            this.bytesInUse = 0;
            this.records = new Map();
            chrome.alarms.onAlarm.addListener(async (alarm) => {
                if (alarm.name === LimitedCacheStorage.ALARM_NAME) {
                    LimitedCacheStorage.alarmIsActive = false;
                    this.removeExpiredRecords();
                }
            });
        }
        static ensureAlarmIsScheduled() {
            if (!this.alarmIsActive) {
                chrome.alarms.create(LimitedCacheStorage.ALARM_NAME, {
                    delayInMinutes: 1
                });
                this.alarmIsActive = true;
            }
        }
        has(url) {
            return this.records.has(url);
        }
        get(url) {
            if (this.records.has(url)) {
                const record = this.records.get(url);
                record.expires = Date.now() + LimitedCacheStorage.TTL;
                this.records.delete(url);
                this.records.set(url, record);
                return record.value;
            }
            return null;
        }
        set(url, value) {
            LimitedCacheStorage.ensureAlarmIsScheduled();
            const size = getStringSize(value);
            if (size > LimitedCacheStorage.QUOTA_BYTES) {
                return;
            }
            for (const [url, record] of this.records) {
                if (this.bytesInUse + size > LimitedCacheStorage.QUOTA_BYTES) {
                    this.records.delete(url);
                    this.bytesInUse -= record.size;
                } else {
                    break;
                }
            }
            if (this.records.size === 0) {
                this.bytesInUse = 0;
            }
            const expires = Date.now() + LimitedCacheStorage.TTL;
            this.records.set(url, {url, value, size, expires});
            this.bytesInUse += size;
        }
        removeExpiredRecords() {
            const now = Date.now();
            for (const [url, record] of this.records) {
                if (record.expires < now) {
                    this.records.delete(url);
                    this.bytesInUse -= record.size;
                } else {
                    break;
                }
            }
            if (this.records.size === 0) {
                this.bytesInUse = 0;
            } else {
                LimitedCacheStorage.ensureAlarmIsScheduled();
            }
        }
    }
    LimitedCacheStorage.QUOTA_BYTES =
        (navigator.deviceMemory || 4) * 16 * 1024 * 1024;
    LimitedCacheStorage.TTL = getDuration({minutes: 10});
    LimitedCacheStorage.ALARM_NAME = "network";
    LimitedCacheStorage.alarmIsActive = false;
    function createLimiter() {
        const loadingUrls = new Set();
        const awaitingUrls = new Map();
        function loading(url) {
            const result = loadingUrls.has(url);
            loadingUrls.add(url);
            return result;
        }
        async function wait(url) {
            return new Promise((resolve) => {
                var _a;
                if (!awaitingUrls.has(url)) {
                    awaitingUrls.set(url, new Set());
                }
                (_a = awaitingUrls.get(url)) === null || _a === void 0
                    ? void 0
                    : _a.add(resolve);
            });
        }
        async function loaded(url, data) {
            loadingUrls.delete(url);
            if (awaitingUrls.has(url)) {
                const response = {data};
                awaitingUrls.get(url).forEach((callback) => callback(response));
                awaitingUrls.delete(url);
            }
        }
        async function failed(url, error) {
            loadingUrls.delete(url);
            if (awaitingUrls.has(url)) {
                const response = {error};
                awaitingUrls.get(url).forEach((callback) => callback(response));
                awaitingUrls.delete(url);
            }
        }
        return {loading, wait, loaded, failed};
    }
    function createFileLoader() {
        const caches = {
            "data-url": new LimitedCacheStorage(),
            "text": new LimitedCacheStorage()
        };
        const loaders = {
            "data-url": loadAsDataURL,
            "text": loadAsText
        };
        const limiters = {
            "data-url": createLimiter(),
            "text": createLimiter()
        };
        async function get({url, responseType, mimeType, origin}) {
            const cache = caches[responseType];
            const load = loaders[responseType];
            const limiter = limiters[responseType];
            if (cache.has(url)) {
                const data = cache.get(url);
                return {data};
            }
            if (limiter.loading(url)) {
                return limiter.wait(url);
            }
            try {
                const data = await load(url, mimeType, origin);
                cache.set(url, data);
                limiter.loaded(url, data);
                return {data};
            } catch (error) {
                limiter.failed(url, error);
                return {error};
            }
        }
        return {get};
    }

    const CONFIG_URLs = {
        darkSites: {
            remote: `${CONFIG_URL_BASE}/dark-sites.config`,
            local: "../config/dark-sites.config"
        },
        dynamicThemeFixes: {
            remote: `${CONFIG_URL_BASE}/dynamic-theme-fixes.config`,
            local: "../config/dynamic-theme-fixes.config"
        },
        inversionFixes: {
            remote: `${CONFIG_URL_BASE}/inversion-fixes.config`,
            local: "../config/inversion-fixes.config"
        },
        staticThemes: {
            remote: `${CONFIG_URL_BASE}/static-themes.config`,
            local: "../config/static-themes.config"
        },
        colorSchemes: {
            remote: `${CONFIG_URL_BASE}/color-schemes.drconf`,
            local: "../config/color-schemes.drconf"
        },
        detectorHints: {
            remote: `${CONFIG_URL_BASE}/detector-hints.config`,
            local: "../config/detector-hints.config"
        }
    };
    const REMOTE_TIMEOUT_MS = getDuration({seconds: 10});
    class ConfigManager {
        static async loadConfig({name, local, localURL, remoteURL}) {
            let $config;
            const loadLocal = async () => await readText({url: localURL});
            if (local) {
                $config = await loadLocal();
            } else {
                try {
                    $config = await readText({
                        url: `${remoteURL}?nocache=${Date.now()}`,
                        timeout: REMOTE_TIMEOUT_MS
                    });
                } catch (err) {
                    console.error(`${name} remote load error`, err);
                    $config = await loadLocal();
                }
            }
            return $config;
        }
        static async loadColorSchemes({local}) {
            const $config = await ConfigManager.loadConfig({
                name: "Color Schemes",
                local,
                localURL: CONFIG_URLs.colorSchemes.local,
                remoteURL: CONFIG_URLs.colorSchemes.remote
            });
            ConfigManager.raw.colorSchemes = $config;
            ConfigManager.handleColorSchemes();
        }
        static async loadDarkSites({local}) {
            const sites = await ConfigManager.loadConfig({
                name: "Dark Sites",
                local,
                localURL: CONFIG_URLs.darkSites.local,
                remoteURL: CONFIG_URLs.darkSites.remote
            });
            ConfigManager.raw.darkSites = sites;
            ConfigManager.handleDarkSites();
        }
        static async loadDetectorHints({local}) {
            const $config = await ConfigManager.loadConfig({
                name: "Detector Hints",
                local,
                localURL: CONFIG_URLs.detectorHints.local,
                remoteURL: CONFIG_URLs.detectorHints.remote
            });
            ConfigManager.raw.detectorHints = $config;
            ConfigManager.handleDetectorHints();
        }
        static async loadDynamicThemeFixes({local}) {
            const fixes = await ConfigManager.loadConfig({
                name: "Dynamic Theme Fixes",
                local,
                localURL: CONFIG_URLs.dynamicThemeFixes.local,
                remoteURL: CONFIG_URLs.dynamicThemeFixes.remote
            });
            ConfigManager.raw.dynamicThemeFixes = fixes;
            ConfigManager.handleDynamicThemeFixes();
        }
        static async loadInversionFixes({local}) {
            const fixes = await ConfigManager.loadConfig({
                name: "Inversion Fixes",
                local,
                localURL: CONFIG_URLs.inversionFixes.local,
                remoteURL: CONFIG_URLs.inversionFixes.remote
            });
            ConfigManager.raw.inversionFixes = fixes;
            ConfigManager.handleInversionFixes();
        }
        static async loadStaticThemes({local}) {
            const themes = await ConfigManager.loadConfig({
                name: "Static Themes",
                local,
                localURL: CONFIG_URLs.staticThemes.local,
                remoteURL: CONFIG_URLs.staticThemes.remote
            });
            ConfigManager.raw.staticThemes = themes;
            ConfigManager.handleStaticThemes();
        }
        static async load(config) {
            if (!config) {
                await UserStorage.loadSettings();
                config = {
                    local: !UserStorage.settings.syncSitesFixes
                };
            }
            await Promise.all([
                ConfigManager.loadColorSchemes(config),
                ConfigManager.loadDarkSites(config),
                ConfigManager.loadDetectorHints(config),
                ConfigManager.loadDynamicThemeFixes(config),
                ConfigManager.loadInversionFixes(config),
                ConfigManager.loadStaticThemes(config)
            ]).catch((err) => console.error("Fatality", err));
        }
        static handleColorSchemes() {
            const $config = ConfigManager.raw.colorSchemes;
            const {result, error} = parseColorSchemeConfig($config || "");
            if (error) {
                ConfigManager.COLOR_SCHEMES_RAW = DEFAULT_COLORSCHEME;
                return;
            }
            ConfigManager.COLOR_SCHEMES_RAW = result;
        }
        static handleDarkSites() {
            const $sites =
                ConfigManager.overrides.darkSites ||
                ConfigManager.raw.darkSites;
            ConfigManager.DARK_SITES_INDEX = indexSiteListConfig($sites || "");
        }
        static handleDetectorHints() {
            const $hints =
                ConfigManager.overrides.detectorHints ||
                ConfigManager.raw.detectorHints ||
                "";
            ConfigManager.DETECTOR_HINTS_INDEX = indexSitesFixesConfig($hints);
            ConfigManager.DETECTOR_HINTS_RAW = $hints;
        }
        static handleDynamicThemeFixes() {
            const $fixes =
                ConfigManager.overrides.dynamicThemeFixes ||
                ConfigManager.raw.dynamicThemeFixes ||
                "";
            ConfigManager.DYNAMIC_THEME_FIXES_INDEX =
                indexSitesFixesConfig($fixes);
            ConfigManager.DYNAMIC_THEME_FIXES_RAW = $fixes;
        }
        static handleInversionFixes() {
            const $fixes =
                ConfigManager.overrides.inversionFixes ||
                ConfigManager.raw.inversionFixes ||
                "";
            ConfigManager.INVERSION_FIXES_INDEX = indexSitesFixesConfig($fixes);
            ConfigManager.INVERSION_FIXES_RAW = $fixes;
        }
        static handleStaticThemes() {
            const $themes =
                ConfigManager.overrides.staticThemes ||
                ConfigManager.raw.staticThemes ||
                "";
            ConfigManager.STATIC_THEMES_INDEX = indexSitesFixesConfig($themes);
            ConfigManager.STATIC_THEMES_RAW = $themes;
        }
        static isURLInDarkList(url) {
            return isURLInSiteList(url, ConfigManager.DARK_SITES_INDEX);
        }
    }
    ConfigManager.raw = {
        darkSites: null,
        detectorHints: null,
        dynamicThemeFixes: null,
        inversionFixes: null,
        staticThemes: null,
        colorSchemes: null
    };
    ConfigManager.overrides = {
        darkSites: null,
        detectorHints: null,
        dynamicThemeFixes: null,
        inversionFixes: null,
        staticThemes: null
    };

    class PersistentStorageWrapper {
        constructor() {
            this.cache = {};
        }
        async get(key) {
            if (key in this.cache) {
                return this.cache[key];
            }
            return new Promise((resolve) => {
                chrome.storage.local.get(key, (result) => {
                    if (key in this.cache) {
                        resolve(this.cache[key]);
                        return;
                    }
                    if (chrome.runtime.lastError) {
                        console.error(
                            "Failed to query DevTools data",
                            chrome.runtime.lastError
                        );
                        resolve(null);
                        return;
                    }
                    this.cache[key] = result[key];
                    resolve(result[key]);
                });
            });
        }
        async set(key, value) {
            this.cache[key] = value;
            return new Promise((resolve) =>
                chrome.storage.local.set({[key]: value}, () => {
                    if (chrome.runtime.lastError) {
                        console.error(
                            "Failed to write DevTools data",
                            chrome.runtime.lastError
                        );
                    } else {
                        resolve();
                    }
                })
            );
        }
        async remove(key) {
            this.cache[key] = null;
            return new Promise((resolve) =>
                chrome.storage.local.remove(key, () => {
                    if (chrome.runtime.lastError) {
                        console.error(
                            "Failed to delete DevTools data",
                            chrome.runtime.lastError
                        );
                    } else {
                        resolve();
                    }
                })
            );
        }
        async has(key) {
            return Boolean(await this.get(key));
        }
    }
    class TempStorage {
        constructor() {
            this.map = new Map();
        }
        async get(key) {
            return this.map.get(key) || null;
        }
        set(key, value) {
            this.map.set(key, value);
        }
        remove(key) {
            this.map.delete(key);
        }
        async has(key) {
            return this.map.has(key);
        }
    }
    class DevTools {
        static init(onChange) {
            if (
                typeof chrome.storage.local !== "undefined" &&
                chrome.storage.local !== null
            ) {
                DevTools.store = new PersistentStorageWrapper();
            } else {
                DevTools.store = new TempStorage();
            }
            DevTools.loadConfigOverrides();
            DevTools.onChange = onChange;
        }
        static async loadConfigOverrides() {
            const [dynamicThemeFixes, inversionFixes, staticThemes] =
                await Promise.all([
                    DevTools.getSavedDynamicThemeFixes(),
                    DevTools.getSavedInversionFixes(),
                    DevTools.getSavedStaticThemes()
                ]);
            ConfigManager.overrides.dynamicThemeFixes =
                dynamicThemeFixes || null;
            ConfigManager.overrides.inversionFixes = inversionFixes || null;
            ConfigManager.overrides.staticThemes = staticThemes || null;
        }
        static async getSavedDynamicThemeFixes() {
            return DevTools.store.get(DevTools.KEY_DYNAMIC);
        }
        static saveDynamicThemeFixes(text) {
            DevTools.store.set(DevTools.KEY_DYNAMIC, text);
        }
        static async getDynamicThemeFixesText() {
            let rawFixes = await DevTools.getSavedDynamicThemeFixes();
            if (!rawFixes) {
                await ConfigManager.load();
                rawFixes = ConfigManager.DYNAMIC_THEME_FIXES_RAW || "";
            }
            const fixes = parseDynamicThemeFixes(rawFixes);
            return formatDynamicThemeFixes(fixes);
        }
        static resetDynamicThemeFixes() {
            DevTools.store.remove(DevTools.KEY_DYNAMIC);
            ConfigManager.overrides.dynamicThemeFixes = null;
            ConfigManager.handleDynamicThemeFixes();
            DevTools.onChange();
        }
        static applyDynamicThemeFixes(text) {
            try {
                const formatted = formatDynamicThemeFixes(
                    parseDynamicThemeFixes(text)
                );
                ConfigManager.overrides.dynamicThemeFixes = formatted;
                ConfigManager.handleDynamicThemeFixes();
                DevTools.saveDynamicThemeFixes(formatted);
                DevTools.onChange();
                return null;
            } catch (err) {
                return err;
            }
        }
        static async getSavedInversionFixes() {
            return this.store.get(DevTools.KEY_FILTER);
        }
        static saveInversionFixes(text) {
            this.store.set(DevTools.KEY_FILTER, text);
        }
        static async getInversionFixesText() {
            let rawFixes = await DevTools.getSavedInversionFixes();
            if (!rawFixes) {
                await ConfigManager.load();
                rawFixes = ConfigManager.INVERSION_FIXES_RAW || "";
            }
            const fixes = parseInversionFixes(rawFixes);
            return formatInversionFixes(fixes);
        }
        static resetInversionFixes() {
            DevTools.store.remove(DevTools.KEY_FILTER);
            ConfigManager.overrides.inversionFixes = null;
            ConfigManager.handleInversionFixes();
            DevTools.onChange();
        }
        static applyInversionFixes(text) {
            try {
                const formatted = formatInversionFixes(
                    parseInversionFixes(text)
                );
                ConfigManager.overrides.inversionFixes = formatted;
                ConfigManager.handleInversionFixes();
                DevTools.saveInversionFixes(formatted);
                DevTools.onChange();
                return null;
            } catch (err) {
                return err;
            }
        }
        static async getSavedStaticThemes() {
            return DevTools.store.get(DevTools.KEY_STATIC);
        }
        static saveStaticThemes(text) {
            DevTools.store.set(DevTools.KEY_STATIC, text);
        }
        static async getStaticThemesText() {
            let rawThemes = await DevTools.getSavedStaticThemes();
            if (!rawThemes) {
                await ConfigManager.load();
                rawThemes = ConfigManager.STATIC_THEMES_RAW || "";
            }
            const themes = parseStaticThemes(rawThemes);
            return formatStaticThemes(themes);
        }
        static resetStaticThemes() {
            DevTools.store.remove(DevTools.KEY_STATIC);
            ConfigManager.overrides.staticThemes = null;
            ConfigManager.handleStaticThemes();
            DevTools.onChange();
        }
        static applyStaticThemes(text) {
            try {
                const formatted = formatStaticThemes(parseStaticThemes(text));
                ConfigManager.overrides.staticThemes = formatted;
                ConfigManager.handleStaticThemes();
                DevTools.saveStaticThemes(formatted);
                DevTools.onChange();
                return null;
            } catch (err) {
                return err;
            }
        }
    }
    DevTools.KEY_DYNAMIC = "dev_dynamic_theme_fixes";
    DevTools.KEY_FILTER = "dev_inversion_fixes";
    DevTools.KEY_STATIC = "dev_static_themes";

    class IconManager {
        static onStartup() {}
        static handleUpdate() {
            {
                return;
            }
        }
        static setIcon({
            isActive = this.iconState.active,
            colorScheme = "dark",
            tabId
        }) {
            if (!chrome.browserAction.setIcon) {
                return;
            }
            if (tabId) {
                return;
            }
            this.iconState.active = isActive;
            let path = this.ICON_PATHS.activeDark;
            if (isActive) {
                path = IconManager.ICON_PATHS.activeDark;
            } else {
                path = IconManager.ICON_PATHS.activeLight;
            }
            chrome.browserAction.setIcon({path});
        }
        static showBadge(text) {
            IconManager.iconState.badgeText = text;
            chrome.browserAction.setBadgeBackgroundColor({color: "#e96c4c"});
            chrome.browserAction.setBadgeText({text});
        }
        static hideBadge() {
            IconManager.iconState.badgeText = "";
            chrome.browserAction.setBadgeText({text: ""});
        }
    }
    IconManager.ICON_PATHS = {
        activeDark: {
            19: "../icons/dr_active_19.png",
            38: "../icons/dr_active_38.png"
        },
        activeLight: {
            19: "../icons/dr_active_light_19.png",
            38: "../icons/dr_active_light_38.png"
        }
    };
    IconManager.iconState = {
        badgeText: "",
        active: true
    };

    class Messenger {
        static init(adapter) {
            Messenger.adapter = adapter;
            Messenger.changeListenerCount = 0;
            chrome.runtime.onMessage.addListener(Messenger.messageListener);
        }
        static messageListener(message, sender, sendResponse) {
            const allowedSenderURL = [
                chrome.runtime.getURL("/ui/popup/index.html"),
                chrome.runtime.getURL("/ui/devtools/index.html"),
                chrome.runtime.getURL("/ui/options/index.html"),
                chrome.runtime.getURL("/ui/stylesheet-editor/index.html")
            ];
            if (allowedSenderURL.includes(sender.url) || false) {
                Messenger.onUIMessage(message, sendResponse);
                return [
                    MessageTypeUItoBG.GET_DATA,
                    MessageTypeUItoBG.GET_DEVTOOLS_DATA
                ].includes(message.type);
            }
        }
        static firefoxPortListener(port) {
            ASSERT(
                "Messenger.firefoxPortListener() is used only on Firefox",
                isFirefox
            );
            {
                return;
            }
        }
        static onUIMessage({type, data}, sendResponse) {
            switch (type) {
                case MessageTypeUItoBG.GET_DATA:
                    Messenger.adapter
                        .collect()
                        .then((data) => sendResponse({data}));
                    break;
                case MessageTypeUItoBG.GET_DEVTOOLS_DATA:
                    Messenger.adapter
                        .collectDevToolsData()
                        .then((data) => sendResponse({data}));
                    break;
                case MessageTypeUItoBG.SUBSCRIBE_TO_CHANGES:
                    Messenger.changeListenerCount++;
                    break;
                case MessageTypeUItoBG.UNSUBSCRIBE_FROM_CHANGES:
                    Messenger.changeListenerCount--;
                    break;
                case MessageTypeUItoBG.CHANGE_SETTINGS:
                    Messenger.adapter.changeSettings(data);
                    break;
                case MessageTypeUItoBG.SET_THEME:
                    Messenger.adapter.setTheme(data);
                    break;
                case MessageTypeUItoBG.TOGGLE_ACTIVE_TAB:
                    Messenger.adapter.toggleActiveTab();
                    break;
                case MessageTypeUItoBG.MARK_NEWS_AS_READ:
                    Messenger.adapter.markNewsAsRead(data);
                    break;
                case MessageTypeUItoBG.MARK_NEWS_AS_DISPLAYED:
                    Messenger.adapter.markNewsAsDisplayed(data);
                    break;
                case MessageTypeUItoBG.LOAD_CONFIG:
                    Messenger.adapter.loadConfig(data);
                    break;
                case MessageTypeUItoBG.APPLY_DEV_DYNAMIC_THEME_FIXES: {
                    const error =
                        Messenger.adapter.applyDevDynamicThemeFixes(data);
                    sendResponse({error: error ? error.message : undefined});
                    break;
                }
                case MessageTypeUItoBG.RESET_DEV_DYNAMIC_THEME_FIXES:
                    Messenger.adapter.resetDevDynamicThemeFixes();
                    break;
                case MessageTypeUItoBG.APPLY_DEV_INVERSION_FIXES: {
                    const error =
                        Messenger.adapter.applyDevInversionFixes(data);
                    sendResponse({error: error ? error.message : undefined});
                    break;
                }
                case MessageTypeUItoBG.RESET_DEV_INVERSION_FIXES:
                    Messenger.adapter.resetDevInversionFixes();
                    break;
                case MessageTypeUItoBG.APPLY_DEV_STATIC_THEMES: {
                    const error = Messenger.adapter.applyDevStaticThemes(data);
                    sendResponse({error: error ? error.message : undefined});
                    break;
                }
                case MessageTypeUItoBG.RESET_DEV_STATIC_THEMES:
                    Messenger.adapter.resetDevStaticThemes();
                    break;
                case MessageTypeUItoBG.START_ACTIVATION:
                    Messenger.adapter.startActivation(data.email, data.key);
                    break;
                case MessageTypeUItoBG.RESET_ACTIVATION:
                    Messenger.adapter.resetActivation();
                    break;
                case MessageTypeUItoBG.HIDE_HIGHLIGHTS:
                    Messenger.adapter.hideHighlights(data);
                    break;
            }
        }
        static reportChanges(data) {
            if (Messenger.changeListenerCount > 0) {
                chrome.runtime.sendMessage({
                    type: MessageTypeBGtoUI.CHANGES,
                    data
                });
            }
        }
    }

    class Newsmaker {
        static init() {
            if (Newsmaker.initialized) {
                return;
            }
            Newsmaker.initialized = true;
            Newsmaker.stateManager = new StateManager(
                Newsmaker.LOCAL_STORAGE_KEY,
                this,
                {latest: [], latestTimestamp: null},
                logWarn
            );
            Newsmaker.latest = [];
            Newsmaker.latestTimestamp = null;
        }
        static onUpdate() {
            Newsmaker.init();
            const latestNews =
                Newsmaker.latest.length > 0 && Newsmaker.latest[0];
            if (
                latestNews &&
                latestNews.badge &&
                !latestNews.read &&
                !latestNews.displayed
            ) {
                IconManager.showBadge(latestNews.badge);
                return;
            }
            IconManager.hideBadge();
        }
        static async getLatest() {
            Newsmaker.init();
            await Newsmaker.stateManager.loadState();
            return Newsmaker.latest;
        }
        static subscribe() {
            Newsmaker.init();
            if (
                Newsmaker.latestTimestamp === null ||
                Newsmaker.latestTimestamp + Newsmaker.UPDATE_INTERVAL <
                    Date.now()
            ) {
                Newsmaker.updateNews();
            }
            chrome.alarms.onAlarm.addListener(Newsmaker.alarmListener);
            chrome.alarms.create(Newsmaker.ALARM_NAME, {
                periodInMinutes: Newsmaker.UPDATE_INTERVAL
            });
        }
        static unSubscribe() {
            chrome.alarms.onAlarm.removeListener(Newsmaker.alarmListener);
            chrome.alarms.clear(Newsmaker.ALARM_NAME);
        }
        static async updateNews() {
            Newsmaker.init();
            const news = await Newsmaker.getNews();
            if (Array.isArray(news)) {
                Newsmaker.latest = news;
                Newsmaker.latestTimestamp = Date.now();
                Newsmaker.onUpdate();
                await Newsmaker.stateManager.saveState();
            }
        }
        static async getReadNews() {
            Newsmaker.init();
            const [sync, local] = await Promise.all([
                readSyncStorage({readNews: []}),
                readLocalStorage({readNews: []})
            ]);
            return Array.from(
                new Set([
                    ...(sync ? sync.readNews : []),
                    ...(local ? local.readNews : [])
                ])
            );
        }
        static async getDisplayedNews() {
            Newsmaker.init();
            const [sync, local] = await Promise.all([
                readSyncStorage({displayedNews: []}),
                readLocalStorage({displayedNews: []})
            ]);
            return Array.from(
                new Set([
                    ...(sync ? sync.displayedNews : []),
                    ...(local ? local.displayedNews : [])
                ])
            );
        }
        static async getNews() {
            Newsmaker.init();
            try {
                const response = await fetch(NEWS_URL, {cache: "no-cache"});
                const $news = await response.json();
                const readNews = await Newsmaker.getReadNews();
                const displayedNews = await Newsmaker.getDisplayedNews();
                const news = $news.map((n) => {
                    const url = getBlogPostURL(n.id);
                    const read = Newsmaker.wasRead(n.id, readNews);
                    const displayed = Newsmaker.wasDisplayed(
                        n.id,
                        displayedNews
                    );
                    return {...n, url, read, displayed};
                });
                for (let i = 0; i < news.length; i++) {
                    const date = new Date(news[i].date);
                    if (isNaN(date.getTime())) {
                        throw new Error(`Unable to parse date ${date}`);
                    }
                }
                return news;
            } catch (err) {
                console.error(err);
                return null;
            }
        }
        static async markAsRead(ids) {
            Newsmaker.init();
            const readNews = await Newsmaker.getReadNews();
            const results = readNews.slice();
            let changed = false;
            ids.forEach((id) => {
                if (readNews.indexOf(id) < 0) {
                    results.push(id);
                    changed = true;
                }
            });
            if (changed) {
                Newsmaker.latest = Newsmaker.latest.map((n) => {
                    const read = Newsmaker.wasRead(n.id, results);
                    return {...n, read};
                });
                Newsmaker.onUpdate();
                const obj = {readNews: results};
                await Promise.all([
                    writeLocalStorage(obj),
                    writeSyncStorage(obj),
                    Newsmaker.stateManager.saveState()
                ]);
            }
        }
        static async markAsDisplayed(ids) {
            Newsmaker.init();
            const displayedNews = await Newsmaker.getDisplayedNews();
            const results = displayedNews.slice();
            let changed = false;
            ids.forEach((id) => {
                if (displayedNews.indexOf(id) < 0) {
                    results.push(id);
                    changed = true;
                }
            });
            if (changed) {
                Newsmaker.latest = Newsmaker.latest.map((n) => {
                    const displayed = Newsmaker.wasDisplayed(n.id, results);
                    return {...n, displayed};
                });
                Newsmaker.onUpdate();
                const obj = {displayedNews: results};
                await Promise.all([
                    writeLocalStorage(obj),
                    writeSyncStorage(obj),
                    Newsmaker.stateManager.saveState()
                ]);
            }
        }
        static wasRead(id, readNews) {
            return readNews.includes(id);
        }
        static wasDisplayed(id, displayedNews) {
            return displayedNews.includes(id);
        }
    }
    Newsmaker.UPDATE_INTERVAL = getDurationInMinutes({hours: 4});
    Newsmaker.ALARM_NAME = "newsmaker";
    Newsmaker.LOCAL_STORAGE_KEY = "Newsmaker-state";
    Newsmaker.alarmListener = (alarm) => {
        Newsmaker.init();
        if (alarm.name === Newsmaker.ALARM_NAME) {
            Newsmaker.updateNews();
        }
    };

    function isPanel(sender) {
        return (
            typeof sender === "undefined" ||
            typeof sender.tab === "undefined" ||
            (isOpera && sender.tab.index === -1)
        );
    }

    var DocumentState;
    (function (DocumentState) {
        DocumentState[(DocumentState["ACTIVE"] = 0)] = "ACTIVE";
        DocumentState[(DocumentState["PASSIVE"] = 1)] = "PASSIVE";
        DocumentState[(DocumentState["HIDDEN"] = 2)] = "HIDDEN";
        DocumentState[(DocumentState["FROZEN"] = 3)] = "FROZEN";
        DocumentState[(DocumentState["TERMINATED"] = 4)] = "TERMINATED";
        DocumentState[(DocumentState["DISCARDED"] = 5)] = "DISCARDED";
    })(DocumentState || (DocumentState = {}));
    class TabManager {
        static init({
            getConnectionMessage,
            onColorSchemeChange,
            getTabMessage
        }) {
            TabManager.stateManager = new StateManager(
                TabManager.LOCAL_STORAGE_KEY,
                this,
                {tabs: {}, timestamp: 0},
                logWarn
            );
            TabManager.tabs = {};
            TabManager.onColorSchemeChange = onColorSchemeChange;
            TabManager.getTabMessage = getTabMessage;
            chrome.runtime.onMessage.addListener(
                (message, sender, sendResponse) => {
                    switch (message.type) {
                        case MessageTypeCStoBG.DOCUMENT_CONNECT: {
                            TabManager.onColorSchemeMessage(message, sender);
                            const reply = (
                                tabURL,
                                url,
                                isTopFrame,
                                topFrameHasDarkTheme
                            ) => {
                                getConnectionMessage(
                                    tabURL,
                                    url,
                                    isTopFrame,
                                    topFrameHasDarkTheme
                                ).then((response) => {
                                    if (!response) {
                                        return;
                                    }
                                    response.scriptId = message.scriptId;
                                    TabManager.sendDocumentMessage(
                                        sender.tab.id,
                                        sender.documentId,
                                        response,
                                        sender.frameId
                                    );
                                });
                            };
                            if (isPanel(sender)) {
                                {
                                    sendResponse("unsupportedSender");
                                }
                                return false;
                            }
                            const {frameId} = sender;
                            const isTopFrame =
                                frameId === 0 || message.data.isTopFrame;
                            const url = sender.url;
                            const tabId = sender.tab.id;
                            const scriptId = message.scriptId;
                            const tabURL = isTopFrame ? url : sender.tab.url;
                            const documentId = sender.documentId || null;
                            TabManager.stateManager.loadState().then(() => {
                                var _a, _b;
                                TabManager.addFrame(
                                    tabId,
                                    frameId,
                                    documentId,
                                    scriptId,
                                    url,
                                    isTopFrame
                                );
                                const topFrameHasDarkTheme = isTopFrame
                                    ? false
                                    : (_b =
                                            (_a = TabManager.tabs[tabId]) ===
                                                null || _a === void 0
                                                ? void 0
                                                : _a[0]) === null ||
                                        _b === void 0
                                      ? void 0
                                      : _b.darkThemeDetected;
                                reply(
                                    tabURL,
                                    url,
                                    isTopFrame,
                                    topFrameHasDarkTheme
                                );
                                TabManager.stateManager.saveState();
                            });
                            break;
                        }
                        case MessageTypeCStoBG.DOCUMENT_FORGET:
                            if (!sender.tab) {
                                break;
                            }
                            ASSERT("Has a scriptId", () =>
                                Boolean(message.scriptId)
                            );
                            TabManager.removeFrame(
                                sender.tab.id,
                                sender.frameId
                            );
                            break;
                        case MessageTypeCStoBG.DOCUMENT_FREEZE: {
                            TabManager.stateManager.loadState().then(() => {
                                const info =
                                    TabManager.tabs[sender.tab.id][
                                        sender.frameId
                                    ];
                                info.state = DocumentState.FROZEN;
                                info.url = null;
                                TabManager.stateManager.saveState();
                            });
                            break;
                        }
                        case MessageTypeCStoBG.DOCUMENT_RESUME: {
                            TabManager.onColorSchemeMessage(message, sender);
                            const tabId = sender.tab.id;
                            const tabURL = sender.tab.url;
                            const frameId = sender.frameId;
                            const url = sender.url;
                            const documentId = sender.documentId || null;
                            const isTopFrame =
                                frameId === 0 || message.data.isTopFrame;
                            TabManager.stateManager.loadState().then(() => {
                                if (
                                    TabManager.tabs[tabId][frameId].timestamp <
                                    TabManager.timestamp
                                ) {
                                    const response = TabManager.getTabMessage(
                                        tabURL,
                                        url,
                                        isTopFrame
                                    );
                                    response.scriptId = message.scriptId;
                                    TabManager.sendDocumentMessage(
                                        tabId,
                                        documentId,
                                        response,
                                        frameId
                                    );
                                }
                                TabManager.tabs[sender.tab.id][sender.frameId] =
                                    {
                                        documentId,
                                        scriptId: message.scriptId,
                                        url,
                                        isTop: isTopFrame || undefined,
                                        state: DocumentState.ACTIVE,
                                        darkThemeDetected: false,
                                        timestamp: TabManager.timestamp
                                    };
                                TabManager.stateManager.saveState();
                            });
                            break;
                        }
                        case MessageTypeCStoBG.DARK_THEME_DETECTED: {
                            const tabId = sender.tab.id;
                            const frames = TabManager.tabs[tabId];
                            if (!frames) {
                                break;
                            }
                            for (const entry of Object.entries(frames)) {
                                const frameId = Number(entry[0]);
                                const frame = entry[1];
                                frame.darkThemeDetected = true;
                                const {documentId, scriptId} = frame;
                                if (documentId) {
                                    const message = {
                                        type: MessageTypeBGtoCS.CLEAN_UP,
                                        scriptId
                                    };
                                    TabManager.sendDocumentMessage(
                                        tabId,
                                        documentId,
                                        message,
                                        frameId
                                    );
                                }
                                if (frameId === 0) {
                                    IconManager.setIcon({
                                        tabId,
                                        isActive: false
                                    });
                                }
                            }
                            break;
                        }
                        case MessageTypeCStoBG.FETCH: {
                            const id = message.id;
                            const sendResponse = (response) => {
                                TabManager.sendDocumentMessage(
                                    sender.tab.id,
                                    sender.documentId,
                                    {
                                        type: MessageTypeBGtoCS.FETCH_RESPONSE,
                                        id,
                                        ...response
                                    },
                                    sender.frameId
                                );
                            };
                            const {url, responseType, mimeType, origin} =
                                message.data;
                            if (!TabManager.fileLoader) {
                                TabManager.fileLoader = createFileLoader();
                            }
                            TabManager.fileLoader
                                .get({url, responseType, mimeType, origin})
                                .then((response) => {
                                    var _a;
                                    if (response.error) {
                                        const err = response.error;
                                        sendResponse({
                                            error:
                                                (_a =
                                                    err === null ||
                                                    err === void 0
                                                        ? void 0
                                                        : err.message) !==
                                                    null && _a !== void 0
                                                    ? _a
                                                    : err
                                        });
                                    } else {
                                        sendResponse({data: response.data});
                                    }
                                });
                            return true;
                        }
                        case MessageTypeUItoBG.COLOR_SCHEME_CHANGE:
                        case MessageTypeCStoBG.COLOR_SCHEME_CHANGE:
                            TabManager.onColorSchemeMessage(message, sender);
                            break;
                    }
                    return false;
                }
            );
            chrome.tabs.onRemoved.addListener(async (tabId) =>
                TabManager.removeFrame(tabId, 0)
            );
        }
        static sendDocumentMessage(tabId, documentId, message, frameId) {
            var _a, _b, _c, _d, _e;
            if (frameId === 0) {
                const themeMessageTypes = [
                    MessageTypeBGtoCS.ADD_CSS_FILTER,
                    MessageTypeBGtoCS.ADD_DYNAMIC_THEME,
                    MessageTypeBGtoCS.ADD_STATIC_THEME,
                    MessageTypeBGtoCS.ADD_SVG_FILTER
                ];
                if (themeMessageTypes.includes(message.type)) {
                    IconManager.setIcon({
                        tabId,
                        isActive: true,
                        colorScheme: (
                            (_b =
                                (_a = message.data) === null || _a === void 0
                                    ? void 0
                                    : _a.theme) === null || _b === void 0
                                ? void 0
                                : _b.mode
                        )
                            ? "dark"
                            : "light"
                    });
                } else if (message.type === MessageTypeBGtoCS.CLEAN_UP) {
                    const isActive =
                        (_e =
                            (_d =
                                (_c = TabManager.tabs[tabId]) === null ||
                                _c === void 0
                                    ? void 0
                                    : _c[0]) === null || _d === void 0
                                ? void 0
                                : _d.url) === null || _e === void 0
                            ? void 0
                            : _e.startsWith("https://darkreader.org/");
                    IconManager.setIcon({tabId, isActive});
                }
            }
            {
                chrome.tabs.sendMessage(
                    tabId,
                    message,
                    documentId ? {documentId} : {frameId}
                );
                return;
            }
        }
        static onColorSchemeMessage(message, sender) {
            ASSERT("TabManager.onColorSchemeMessage is set", () =>
                Boolean(TabManager.onColorSchemeChange)
            );
            if (sender && sender.frameId === 0) {
                TabManager.onColorSchemeChange(message.data.isDark);
            }
        }
        static addFrame(tabId, frameId, documentId, scriptId, url, isTop) {
            let frames;
            if (TabManager.tabs[tabId]) {
                frames = TabManager.tabs[tabId];
            } else {
                frames = {};
                TabManager.tabs[tabId] = frames;
            }
            frames[frameId] = {
                documentId,
                scriptId,
                url,
                isTop: isTop || undefined,
                state: DocumentState.ACTIVE,
                darkThemeDetected: false,
                timestamp: TabManager.timestamp
            };
        }
        static async removeFrame(tabId, frameId) {
            await TabManager.stateManager.loadState();
            if (frameId === 0) {
                delete TabManager.tabs[tabId];
            }
            if (TabManager.tabs[tabId] && TabManager.tabs[tabId][frameId]) {
                delete TabManager.tabs[tabId][frameId];
            }
            TabManager.stateManager.saveState();
        }
        static async cleanState() {
            await TabManager.stateManager.loadState();
            const actualTabs = await queryTabs({});
            const tabIds = Object.keys(TabManager.tabs).map((id) => Number(id));
            const staleTabs = new Set(tabIds);
            actualTabs.forEach((actualTab) => {
                const tabId = actualTab.id;
                if (tabId) {
                    staleTabs.delete(tabId);
                }
            });
            staleTabs.forEach((staleTabId) => {
                if (TabManager.tabs[staleTabId]) {
                    delete TabManager.tabs[staleTabId];
                }
            });
            TabManager.stateManager.saveState();
        }
        static async getTabURL(tab) {
            return (tab && tab.url) || "about:blank";
        }
        static async updateContentScript(options) {
            (await queryTabs({discarded: false}))
                .filter(
                    (tab) =>
                        options.runOnProtectedPages || canInjectScript(tab.url)
                )
                .filter((tab) => !TabManager.tabs[tab.id])
                .forEach((tab) => {
                    {
                        chrome.tabs.executeScript(tab.id, {
                            runAt: "document_start",
                            file: "/inject/index.js",
                            allFrames: true,
                            matchAboutBlank: true
                        });
                    }
                });
        }
        static async registerMailDisplayScript() {
            await chrome.messageDisplayScripts.register({
                js: [{file: "/inject/fallback.js"}, {file: "/inject/index.js"}]
            });
        }
        static async sendMessage(onlyUpdateActiveTab = false) {
            TabManager.timestamp++;
            const activeTabHostname = onlyUpdateActiveTab
                ? getURLHostOrProtocol(await TabManager.getActiveTabURL())
                : null;
            (await queryTabs({discarded: false}))
                .filter((tab) => Boolean(TabManager.tabs[tab.id]))
                .forEach((tab) => {
                    const frames = TabManager.tabs[tab.id];
                    Object.entries(frames)
                        .filter(
                            ([, {state}]) =>
                                state === DocumentState.ACTIVE ||
                                state === DocumentState.PASSIVE
                        )
                        .forEach(
                            async ([
                                id,
                                {url, documentId, scriptId, isTop}
                            ]) => {
                                const frameId = Number(id);
                                const tabURL = await TabManager.getTabURL(tab);
                                if (
                                    onlyUpdateActiveTab &&
                                    getURLHostOrProtocol(tabURL) !==
                                        activeTabHostname
                                ) {
                                    return;
                                }
                                const message = TabManager.getTabMessage(
                                    tabURL,
                                    url,
                                    isTop || false
                                );
                                message.scriptId = scriptId;
                                if (tab.active && isTop) {
                                    TabManager.sendDocumentMessage(
                                        tab.id,
                                        documentId,
                                        message,
                                        frameId
                                    );
                                } else {
                                    setTimeout(() => {
                                        TabManager.sendDocumentMessage(
                                            tab.id,
                                            documentId,
                                            message,
                                            frameId
                                        );
                                    });
                                }
                                if (TabManager.tabs[tab.id][frameId]) {
                                    TabManager.tabs[tab.id][frameId].timestamp =
                                        TabManager.timestamp;
                                }
                            }
                        );
                });
        }
        static canAccessTab(tab) {
            return (tab && Boolean(TabManager.tabs[tab.id])) || false;
        }
        static getTabDocumentId(tab) {
            return (
                tab &&
                TabManager.tabs[tab.id] &&
                TabManager.tabs[tab.id][0] &&
                TabManager.tabs[tab.id][0].documentId
            );
        }
        static isTabDarkThemeDetected(tab) {
            return (
                (tab &&
                    TabManager.tabs[tab.id] &&
                    TabManager.tabs[tab.id][0] &&
                    TabManager.tabs[tab.id][0].darkThemeDetected) ||
                null
            );
        }
        static async getActiveTabURL() {
            return TabManager.getTabURL(await getActiveTab());
        }
    }
    TabManager.fileLoader = null;
    TabManager.LOCAL_STORAGE_KEY = "TabManager-state";

    const proposedHighlights = ["anniversary"];
    const KEY_UI_HIDDEN_HIGHLIGHTS = "ui-hidden-highlights";
    async function getHiddenHighlights() {
        const options = await readLocalStorage({
            [KEY_UI_HIDDEN_HIGHLIGHTS]: []
        });
        return options[KEY_UI_HIDDEN_HIGHLIGHTS];
    }
    async function getHighlightsToShow() {
        const hiddenHighlights = await getHiddenHighlights();
        return proposedHighlights.filter((h) => !hiddenHighlights.includes(h));
    }
    async function hideHighlights(keys) {
        const hiddenHighlights = await getHiddenHighlights();
        const update = Array.from(new Set([...hiddenHighlights, ...keys]));
        await writeLocalStorage({[KEY_UI_HIDDEN_HIGHLIGHTS]: update});
    }
    async function restoreHighlights(keys) {
        const hiddenHighlights = await getHiddenHighlights();
        const update = Array.from(
            new Set([...hiddenHighlights.filter((h) => !keys.includes(h))])
        );
        await writeLocalStorage({[KEY_UI_HIDDEN_HIGHLIGHTS]: update});
    }
    var UIHighlights = {
        getHighlightsToShow,
        hideHighlights,
        restoreHighlights
    };

    function evalMath(expression) {
        const rpnStack = [];
        const workingStack = [];
        let lastToken;
        for (let i = 0, len = expression.length; i < len; i++) {
            const token = expression[i];
            if (!token || token === " ") {
                continue;
            }
            if (operators.has(token)) {
                const op = operators.get(token);
                while (workingStack.length) {
                    const currentOp = operators.get(workingStack[0]);
                    if (!currentOp) {
                        break;
                    }
                    if (op.lessOrEqualThan(currentOp)) {
                        rpnStack.push(workingStack.shift());
                    } else {
                        break;
                    }
                }
                workingStack.unshift(token);
            } else if (!lastToken || operators.has(lastToken)) {
                rpnStack.push(token);
            } else {
                rpnStack[rpnStack.length - 1] += token;
            }
            lastToken = token;
        }
        rpnStack.push(...workingStack);
        const stack = [];
        for (let i = 0, len = rpnStack.length; i < len; i++) {
            const op = operators.get(rpnStack[i]);
            if (op) {
                const args = stack.splice(0, 2);
                stack.push(op.exec(args[1], args[0]));
            } else {
                stack.unshift(parseFloat(rpnStack[i]));
            }
        }
        return stack[0];
    }
    class Operator {
        constructor(precedence, method) {
            this.precendce = precedence;
            this.execMethod = method;
        }
        exec(left, right) {
            return this.execMethod(left, right);
        }
        lessOrEqualThan(op) {
            return this.precendce <= op.precendce;
        }
    }
    const operators = new Map([
        ["+", new Operator(1, (left, right) => left + right)],
        ["-", new Operator(1, (left, right) => left - right)],
        ["*", new Operator(2, (left, right) => left * right)],
        ["/", new Operator(2, (left, right) => left / right)]
    ]);

    const hslaParseCache = new Map();
    const rgbaParseCache = new Map();
    function parseColorWithCache($color) {
        $color = $color.trim();
        if (rgbaParseCache.has($color)) {
            return rgbaParseCache.get($color);
        }
        if ($color.includes("calc(")) {
            $color = lowerCalcExpression($color);
        }
        const color = parse($color);
        if (color) {
            rgbaParseCache.set($color, color);
            return color;
        }
        return null;
    }
    function parseToHSLWithCache(color) {
        if (hslaParseCache.has(color)) {
            return hslaParseCache.get(color);
        }
        const rgb = parseColorWithCache(color);
        if (!rgb) {
            return null;
        }
        const hsl = rgbToHSL(rgb);
        hslaParseCache.set(color, hsl);
        return hsl;
    }
    function hslToRGB({h, s, l, a = 1}) {
        if (s === 0) {
            const [r, b, g] = [l, l, l].map((x) => Math.round(x * 255));
            return {r, g, b, a};
        }
        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
        const m = l - c / 2;
        const [r, g, b] = (
            h < 60
                ? [c, x, 0]
                : h < 120
                  ? [x, c, 0]
                  : h < 180
                    ? [0, c, x]
                    : h < 240
                      ? [0, x, c]
                      : h < 300
                        ? [x, 0, c]
                        : [c, 0, x]
        ).map((n) => Math.round((n + m) * 255));
        return {r, g, b, a};
    }
    function rgbToHSL({r: r255, g: g255, b: b255, a = 1}) {
        const r = r255 / 255;
        const g = g255 / 255;
        const b = b255 / 255;
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const c = max - min;
        const l = (max + min) / 2;
        if (c === 0) {
            return {h: 0, s: 0, l, a};
        }
        let h =
            (max === r
                ? ((g - b) / c) % 6
                : max === g
                  ? (b - r) / c + 2
                  : (r - g) / c + 4) * 60;
        if (h < 0) {
            h += 360;
        }
        const s = c / (1 - Math.abs(2 * l - 1));
        return {h, s, l, a};
    }
    function toFixed(n, digits = 0) {
        const fixed = n.toFixed(digits);
        if (digits === 0) {
            return fixed;
        }
        const dot = fixed.indexOf(".");
        if (dot >= 0) {
            const zerosMatch = fixed.match(/0+$/);
            if (zerosMatch) {
                if (zerosMatch.index === dot + 1) {
                    return fixed.substring(0, dot);
                }
                return fixed.substring(0, zerosMatch.index);
            }
        }
        return fixed;
    }
    function rgbToString(rgb) {
        const {r, g, b, a} = rgb;
        if (a != null && a < 1) {
            return `rgba(${toFixed(r)}, ${toFixed(g)}, ${toFixed(b)}, ${toFixed(a, 2)})`;
        }
        return `rgb(${toFixed(r)}, ${toFixed(g)}, ${toFixed(b)})`;
    }
    function rgbToHexString({r, g, b, a}) {
        return `#${(a != null && a < 1
            ? [r, g, b, Math.round(a * 255)]
            : [r, g, b]
        )
            .map((x) => {
                return `${x < 16 ? "0" : ""}${x.toString(16)}`;
            })
            .join("")}`;
    }
    const rgbMatch = /^rgba?\([^\(\)]+\)$/;
    const hslMatch = /^hsla?\([^\(\)]+\)$/;
    const hexMatch = /^#[0-9a-f]+$/i;
    const supportedColorFuncs = [
        "color",
        "color-mix",
        "hwb",
        "lab",
        "lch",
        "oklab",
        "oklch"
    ];
    function parse($color) {
        const c = $color.trim().toLowerCase();
        if (c.includes("(from ")) {
            if (c.indexOf("(from") !== c.lastIndexOf("(from")) {
                return null;
            }
            return domParseColor(c);
        }
        if (c.match(rgbMatch)) {
            if (c.startsWith("rgb(#") || c.startsWith("rgba(#")) {
                if (c.lastIndexOf("rgb") > 0) {
                    return null;
                }
                return domParseColor(c);
            }
            return parseRGB(c);
        }
        if (c.match(hslMatch)) {
            return parseHSL(c);
        }
        if (c.match(hexMatch)) {
            return parseHex(c);
        }
        if (knownColors.has(c)) {
            return getColorByName(c);
        }
        if (systemColors.has(c)) {
            return getSystemColor(c);
        }
        if (c === "transparent") {
            return {r: 0, g: 0, b: 0, a: 0};
        }
        if (
            c.endsWith(")") &&
            supportedColorFuncs.some(
                (fn) =>
                    c.startsWith(fn) &&
                    c[fn.length] === "(" &&
                    c.lastIndexOf(fn) === 0
            )
        ) {
            return domParseColor(c);
        }
        if (c.startsWith("light-dark(") && c.endsWith(")")) {
            const match = c.match(
                /^light-dark\(\s*([a-z]+(\(.*\))?),\s*([a-z]+(\(.*\))?)\s*\)$/
            );
            if (match) {
                const schemeColor = isSystemDarkModeEnabled()
                    ? match[3]
                    : match[1];
                return parse(schemeColor);
            }
        }
        return null;
    }
    function getNumbers($color) {
        const numbers = [];
        let prevPos = 0;
        let isMining = false;
        const startIndex = $color.indexOf("(");
        $color = $color.substring(startIndex + 1, $color.length - 1);
        for (let i = 0; i < $color.length; i++) {
            const c = $color[i];
            if ((c >= "0" && c <= "9") || c === "." || c === "+" || c === "-") {
                isMining = true;
            } else if (isMining && (c === " " || c === "," || c === "/")) {
                numbers.push($color.substring(prevPos, i));
                isMining = false;
                prevPos = i + 1;
            } else if (!isMining) {
                prevPos = i + 1;
            }
        }
        if (isMining) {
            numbers.push($color.substring(prevPos, $color.length));
        }
        return numbers;
    }
    function getNumbersFromString(str, range, units) {
        const raw = getNumbers(str);
        const unitsList = Object.entries(units);
        const numbers = raw
            .map((r) => r.trim())
            .map((r, i) => {
                let n;
                const unit = unitsList.find(([u]) => r.endsWith(u));
                if (unit) {
                    n =
                        (parseFloat(r.substring(0, r.length - unit[0].length)) /
                            unit[1]) *
                        range[i];
                } else {
                    n = parseFloat(r);
                }
                if (range[i] > 1) {
                    return Math.round(n);
                }
                return n;
            });
        return numbers;
    }
    const rgbRange = [255, 255, 255, 1];
    const rgbUnits = {"%": 100};
    function parseRGB($rgb) {
        const [r, g, b, a = 1] = getNumbersFromString($rgb, rgbRange, rgbUnits);
        if (r == null || g == null || b == null || a == null) {
            return null;
        }
        return {r, g, b, a};
    }
    const hslRange = [360, 1, 1, 1];
    const hslUnits = {"%": 100, "deg": 360, "rad": 2 * Math.PI, "turn": 1};
    function parseHSL($hsl) {
        const [h, s, l, a = 1] = getNumbersFromString($hsl, hslRange, hslUnits);
        if (h == null || s == null || l == null || a == null) {
            return null;
        }
        return hslToRGB({h, s, l, a});
    }
    function parseHex($hex) {
        const h = $hex.substring(1);
        switch (h.length) {
            case 3:
            case 4: {
                const [r, g, b] = [0, 1, 2].map((i) =>
                    parseInt(`${h[i]}${h[i]}`, 16)
                );
                const a =
                    h.length === 3 ? 1 : parseInt(`${h[3]}${h[3]}`, 16) / 255;
                return {r, g, b, a};
            }
            case 6:
            case 8: {
                const [r, g, b] = [0, 2, 4].map((i) =>
                    parseInt(h.substring(i, i + 2), 16)
                );
                const a =
                    h.length === 6 ? 1 : parseInt(h.substring(6, 8), 16) / 255;
                return {r, g, b, a};
            }
        }
        return null;
    }
    function getColorByName($color) {
        const n = knownColors.get($color);
        return {
            r: (n >> 16) & 255,
            g: (n >> 8) & 255,
            b: (n >> 0) & 255,
            a: 1
        };
    }
    function getSystemColor($color) {
        const n = systemColors.get($color);
        return {
            r: (n >> 16) & 255,
            g: (n >> 8) & 255,
            b: (n >> 0) & 255,
            a: 1
        };
    }
    function lowerCalcExpression(color) {
        let searchIndex = 0;
        const replaceBetweenIndices = (start, end, replacement) => {
            color =
                color.substring(0, start) + replacement + color.substring(end);
        };
        while ((searchIndex = color.indexOf("calc(")) !== -1) {
            const range = getParenthesesRange(color, searchIndex);
            if (!range) {
                break;
            }
            let slice = color.slice(range.start + 1, range.end - 1);
            const includesPercentage = slice.includes("%");
            slice = slice.split("%").join("");
            const output = Math.round(evalMath(slice));
            replaceBetweenIndices(
                range.start - 4,
                range.end,
                output + (includesPercentage ? "%" : "")
            );
        }
        return color;
    }
    const knownColors = new Map(
        Object.entries({
            aliceblue: 0xf0f8ff,
            antiquewhite: 0xfaebd7,
            aqua: 0x00ffff,
            aquamarine: 0x7fffd4,
            azure: 0xf0ffff,
            beige: 0xf5f5dc,
            bisque: 0xffe4c4,
            black: 0x000000,
            blanchedalmond: 0xffebcd,
            blue: 0x0000ff,
            blueviolet: 0x8a2be2,
            brown: 0xa52a2a,
            burlywood: 0xdeb887,
            cadetblue: 0x5f9ea0,
            chartreuse: 0x7fff00,
            chocolate: 0xd2691e,
            coral: 0xff7f50,
            cornflowerblue: 0x6495ed,
            cornsilk: 0xfff8dc,
            crimson: 0xdc143c,
            cyan: 0x00ffff,
            darkblue: 0x00008b,
            darkcyan: 0x008b8b,
            darkgoldenrod: 0xb8860b,
            darkgray: 0xa9a9a9,
            darkgrey: 0xa9a9a9,
            darkgreen: 0x006400,
            darkkhaki: 0xbdb76b,
            darkmagenta: 0x8b008b,
            darkolivegreen: 0x556b2f,
            darkorange: 0xff8c00,
            darkorchid: 0x9932cc,
            darkred: 0x8b0000,
            darksalmon: 0xe9967a,
            darkseagreen: 0x8fbc8f,
            darkslateblue: 0x483d8b,
            darkslategray: 0x2f4f4f,
            darkslategrey: 0x2f4f4f,
            darkturquoise: 0x00ced1,
            darkviolet: 0x9400d3,
            deeppink: 0xff1493,
            deepskyblue: 0x00bfff,
            dimgray: 0x696969,
            dimgrey: 0x696969,
            dodgerblue: 0x1e90ff,
            firebrick: 0xb22222,
            floralwhite: 0xfffaf0,
            forestgreen: 0x228b22,
            fuchsia: 0xff00ff,
            gainsboro: 0xdcdcdc,
            ghostwhite: 0xf8f8ff,
            gold: 0xffd700,
            goldenrod: 0xdaa520,
            gray: 0x808080,
            grey: 0x808080,
            green: 0x008000,
            greenyellow: 0xadff2f,
            honeydew: 0xf0fff0,
            hotpink: 0xff69b4,
            indianred: 0xcd5c5c,
            indigo: 0x4b0082,
            ivory: 0xfffff0,
            khaki: 0xf0e68c,
            lavender: 0xe6e6fa,
            lavenderblush: 0xfff0f5,
            lawngreen: 0x7cfc00,
            lemonchiffon: 0xfffacd,
            lightblue: 0xadd8e6,
            lightcoral: 0xf08080,
            lightcyan: 0xe0ffff,
            lightgoldenrodyellow: 0xfafad2,
            lightgray: 0xd3d3d3,
            lightgrey: 0xd3d3d3,
            lightgreen: 0x90ee90,
            lightpink: 0xffb6c1,
            lightsalmon: 0xffa07a,
            lightseagreen: 0x20b2aa,
            lightskyblue: 0x87cefa,
            lightslategray: 0x778899,
            lightslategrey: 0x778899,
            lightsteelblue: 0xb0c4de,
            lightyellow: 0xffffe0,
            lime: 0x00ff00,
            limegreen: 0x32cd32,
            linen: 0xfaf0e6,
            magenta: 0xff00ff,
            maroon: 0x800000,
            mediumaquamarine: 0x66cdaa,
            mediumblue: 0x0000cd,
            mediumorchid: 0xba55d3,
            mediumpurple: 0x9370db,
            mediumseagreen: 0x3cb371,
            mediumslateblue: 0x7b68ee,
            mediumspringgreen: 0x00fa9a,
            mediumturquoise: 0x48d1cc,
            mediumvioletred: 0xc71585,
            midnightblue: 0x191970,
            mintcream: 0xf5fffa,
            mistyrose: 0xffe4e1,
            moccasin: 0xffe4b5,
            navajowhite: 0xffdead,
            navy: 0x000080,
            oldlace: 0xfdf5e6,
            olive: 0x808000,
            olivedrab: 0x6b8e23,
            orange: 0xffa500,
            orangered: 0xff4500,
            orchid: 0xda70d6,
            palegoldenrod: 0xeee8aa,
            palegreen: 0x98fb98,
            paleturquoise: 0xafeeee,
            palevioletred: 0xdb7093,
            papayawhip: 0xffefd5,
            peachpuff: 0xffdab9,
            peru: 0xcd853f,
            pink: 0xffc0cb,
            plum: 0xdda0dd,
            powderblue: 0xb0e0e6,
            purple: 0x800080,
            rebeccapurple: 0x663399,
            red: 0xff0000,
            rosybrown: 0xbc8f8f,
            royalblue: 0x4169e1,
            saddlebrown: 0x8b4513,
            salmon: 0xfa8072,
            sandybrown: 0xf4a460,
            seagreen: 0x2e8b57,
            seashell: 0xfff5ee,
            sienna: 0xa0522d,
            silver: 0xc0c0c0,
            skyblue: 0x87ceeb,
            slateblue: 0x6a5acd,
            slategray: 0x708090,
            slategrey: 0x708090,
            snow: 0xfffafa,
            springgreen: 0x00ff7f,
            steelblue: 0x4682b4,
            tan: 0xd2b48c,
            teal: 0x008080,
            thistle: 0xd8bfd8,
            tomato: 0xff6347,
            turquoise: 0x40e0d0,
            violet: 0xee82ee,
            wheat: 0xf5deb3,
            white: 0xffffff,
            whitesmoke: 0xf5f5f5,
            yellow: 0xffff00,
            yellowgreen: 0x9acd32
        })
    );
    const systemColors = new Map(
        Object.entries({
            "ActiveBorder": 0x3b99fc,
            "ActiveCaption": 0x000000,
            "AppWorkspace": 0xaaaaaa,
            "Background": 0x6363ce,
            "ButtonFace": 0xffffff,
            "ButtonHighlight": 0xe9e9e9,
            "ButtonShadow": 0x9fa09f,
            "ButtonText": 0x000000,
            "CaptionText": 0x000000,
            "GrayText": 0x7f7f7f,
            "Highlight": 0xb2d7ff,
            "HighlightText": 0x000000,
            "InactiveBorder": 0xffffff,
            "InactiveCaption": 0xffffff,
            "InactiveCaptionText": 0x000000,
            "InfoBackground": 0xfbfcc5,
            "InfoText": 0x000000,
            "Menu": 0xf6f6f6,
            "MenuText": 0xffffff,
            "Scrollbar": 0xaaaaaa,
            "ThreeDDarkShadow": 0x000000,
            "ThreeDFace": 0xc0c0c0,
            "ThreeDHighlight": 0xffffff,
            "ThreeDLightShadow": 0xffffff,
            "ThreeDShadow": 0x000000,
            "Window": 0xececec,
            "WindowFrame": 0xaaaaaa,
            "WindowText": 0x000000,
            "-webkit-focus-ring-color": 0xe59700
        }).map(([key, value]) => [key.toLowerCase(), value])
    );
    let canvas;
    let context;
    function domParseColor($color) {
        if (!context) {
            canvas = document.createElement("canvas");
            canvas.width = 1;
            canvas.height = 1;
            context = canvas.getContext("2d", {willReadFrequently: true});
        }
        context.fillStyle = $color;
        context.fillRect(0, 0, 1, 1);
        const d = context.getImageData(0, 0, 1, 1).data;
        const color = `rgba(${d[0]}, ${d[1]}, ${d[2]}, ${(d[3] / 255).toFixed(2)})`;
        return parseRGB(color);
    }

    const registeredColors = new Map();
    function getRegisteredVariableValue(type, registered) {
        return `var(${registered[type].variable}, ${registered[type].value})`;
    }
    function getRegisteredColor(type, parsed) {
        const hex = rgbToHexString(parsed);
        const registered = registeredColors.get(hex);
        if (
            registered === null || registered === void 0
                ? void 0
                : registered[type]
        ) {
            return getRegisteredVariableValue(type, registered);
        }
        return null;
    }
    function registerColor(type, parsed, value) {
        var _a;
        const hex = rgbToHexString(parsed);
        let registered;
        if (registeredColors.has(hex)) {
            registered = registeredColors.get(hex);
        } else {
            const parsed = parseColorWithCache(hex);
            registered = {parsed};
            registeredColors.set(hex, registered);
        }
        const variable = `--darkreader-${type}-${hex.replace("#", "")}`;
        registered[type] = {variable, value};
        if ((_a = void 0) === null || _a === void 0 ? void 0 : _a.style) {
            (void 0).style.setProperty(variable, value);
        }
        return getRegisteredVariableValue(type, registered);
    }

    function getBgPole(theme) {
        const isDarkScheme = theme.mode === 1;
        const prop = isDarkScheme
            ? "darkSchemeBackgroundColor"
            : "lightSchemeBackgroundColor";
        return theme[prop];
    }
    function getFgPole(theme) {
        const isDarkScheme = theme.mode === 1;
        const prop = isDarkScheme
            ? "darkSchemeTextColor"
            : "lightSchemeTextColor";
        return theme[prop];
    }
    const colorModificationCache = new Map();
    const rgbCacheKeys = ["r", "g", "b", "a"];
    const themeCacheKeys = [
        "mode",
        "brightness",
        "contrast",
        "grayscale",
        "sepia",
        "darkSchemeBackgroundColor",
        "darkSchemeTextColor",
        "lightSchemeBackgroundColor",
        "lightSchemeTextColor"
    ];
    function getCacheId(rgb, theme) {
        let resultId = "";
        rgbCacheKeys.forEach((key) => {
            resultId += `${rgb[key]};`;
        });
        themeCacheKeys.forEach((key) => {
            resultId += `${theme[key]};`;
        });
        return resultId;
    }
    function modifyColorWithCache(
        rgb,
        theme,
        modifyHSL,
        poleColor,
        anotherPoleColor
    ) {
        let fnCache;
        if (colorModificationCache.has(modifyHSL)) {
            fnCache = colorModificationCache.get(modifyHSL);
        } else {
            fnCache = new Map();
            colorModificationCache.set(modifyHSL, fnCache);
        }
        const id = getCacheId(rgb, theme);
        if (fnCache.has(id)) {
            return fnCache.get(id);
        }
        const hsl = rgbToHSL(rgb);
        const pole = poleColor == null ? null : parseToHSLWithCache(poleColor);
        const anotherPole =
            anotherPoleColor == null
                ? null
                : parseToHSLWithCache(anotherPoleColor);
        const modified = modifyHSL(hsl, pole, anotherPole);
        const {r, g, b, a} = hslToRGB(modified);
        const matrix = createFilterMatrix({...theme, mode: 0});
        const [rf, gf, bf] = applyColorMatrix([r, g, b], matrix);
        const color =
            a === 1
                ? rgbToHexString({r: rf, g: gf, b: bf})
                : rgbToString({r: rf, g: gf, b: bf, a});
        fnCache.set(id, color);
        return color;
    }
    function modifyAndRegisterColor(type, rgb, theme, modifier) {
        const registered = getRegisteredColor(type, rgb);
        if (registered) {
            return registered;
        }
        const value = modifier(rgb, theme);
        return registerColor(type, rgb, value);
    }
    function modifyLightSchemeColor(rgb, theme) {
        const poleBg = getBgPole(theme);
        const poleFg = getFgPole(theme);
        return modifyColorWithCache(
            rgb,
            theme,
            modifyLightModeHSL,
            poleFg,
            poleBg
        );
    }
    function modifyLightModeHSL({h, s, l, a}, poleFg, poleBg) {
        const isDark = l < 0.5;
        let isNeutral;
        if (isDark) {
            isNeutral = l < 0.2 || s < 0.12;
        } else {
            const isBlue = h > 200 && h < 280;
            isNeutral = s < 0.24 || (l > 0.8 && isBlue);
        }
        let hx = h;
        let sx = s;
        if (isNeutral) {
            if (isDark) {
                hx = poleFg.h;
                sx = poleFg.s;
            } else {
                hx = poleBg.h;
                sx = poleBg.s;
            }
        }
        const lx = scale(l, 0, 1, poleFg.l, poleBg.l);
        return {h: hx, s: sx, l: lx, a};
    }
    const MAX_BG_LIGHTNESS = 0.4;
    function modifyBgHSL({h, s, l, a}, pole) {
        const isDark = l < 0.5;
        const isBlue = h > 200 && h < 280;
        const isNeutral = s < 0.12 || (l > 0.8 && isBlue);
        if (isDark) {
            const lx = scale(l, 0, 0.5, 0, MAX_BG_LIGHTNESS);
            if (isNeutral) {
                const hx = pole.h;
                const sx = pole.s;
                return {h: hx, s: sx, l: lx, a};
            }
            return {h, s, l: lx, a};
        }
        let lx = scale(l, 0.5, 1, MAX_BG_LIGHTNESS, pole.l);
        if (isNeutral) {
            const hx = pole.h;
            const sx = pole.s;
            return {h: hx, s: sx, l: lx, a};
        }
        let hx = h;
        const isYellow = h > 60 && h < 180;
        if (isYellow) {
            const isCloserToGreen = h > 120;
            if (isCloserToGreen) {
                hx = scale(h, 120, 180, 135, 180);
            } else {
                hx = scale(h, 60, 120, 60, 105);
            }
        }
        if (hx > 40 && hx < 80) {
            lx *= 0.75;
        }
        return {h: hx, s, l: lx, a};
    }
    function _modifyBackgroundColor(rgb, theme) {
        if (theme.mode === 0) {
            return modifyLightSchemeColor(rgb, theme);
        }
        const pole = getBgPole(theme);
        return modifyColorWithCache(rgb, theme, modifyBgHSL, pole);
    }
    function modifyBackgroundColor(
        rgb,
        theme,
        shouldRegisterColorVariable = true
    ) {
        if (!shouldRegisterColorVariable) {
            return _modifyBackgroundColor(rgb, theme);
        }
        return modifyAndRegisterColor(
            "background",
            rgb,
            theme,
            _modifyBackgroundColor
        );
    }
    const MIN_FG_LIGHTNESS = 0.55;
    function modifyBlueFgHue(hue) {
        return scale(hue, 205, 245, 205, 220);
    }
    function modifyFgHSL({h, s, l, a}, pole) {
        const isLight = l > 0.5;
        const isNeutral = l < 0.2 || s < 0.24;
        const isBlue = !isNeutral && h > 205 && h < 245;
        if (isLight) {
            const lx = scale(l, 0.5, 1, MIN_FG_LIGHTNESS, pole.l);
            if (isNeutral) {
                const hx = pole.h;
                const sx = pole.s;
                return {h: hx, s: sx, l: lx, a};
            }
            let hx = h;
            if (isBlue) {
                hx = modifyBlueFgHue(h);
            }
            return {h: hx, s, l: lx, a};
        }
        if (isNeutral) {
            const hx = pole.h;
            const sx = pole.s;
            const lx = scale(l, 0, 0.5, pole.l, MIN_FG_LIGHTNESS);
            return {h: hx, s: sx, l: lx, a};
        }
        let hx = h;
        let lx;
        if (isBlue) {
            hx = modifyBlueFgHue(h);
            lx = scale(l, 0, 0.5, pole.l, Math.min(1, MIN_FG_LIGHTNESS + 0.05));
        } else {
            lx = scale(l, 0, 0.5, pole.l, MIN_FG_LIGHTNESS);
        }
        return {h: hx, s, l: lx, a};
    }
    function _modifyForegroundColor(rgb, theme) {
        if (theme.mode === 0) {
            return modifyLightSchemeColor(rgb, theme);
        }
        const pole = getFgPole(theme);
        return modifyColorWithCache(rgb, theme, modifyFgHSL, pole);
    }
    function modifyForegroundColor(
        rgb,
        theme,
        shouldRegisterColorVariable = true
    ) {
        if (!shouldRegisterColorVariable) {
            return _modifyForegroundColor(rgb, theme);
        }
        return modifyAndRegisterColor(
            "text",
            rgb,
            theme,
            _modifyForegroundColor
        );
    }
    function modifyBorderHSL({h, s, l, a}, poleFg, poleBg) {
        const isDark = l < 0.5;
        const isNeutral = l < 0.2 || s < 0.24;
        let hx = h;
        let sx = s;
        if (isNeutral) {
            if (isDark) {
                hx = poleFg.h;
                sx = poleFg.s;
            } else {
                hx = poleBg.h;
                sx = poleBg.s;
            }
        }
        const lx = scale(l, 0, 1, 0.5, 0.2);
        return {h: hx, s: sx, l: lx, a};
    }
    function _modifyBorderColor(rgb, theme) {
        if (theme.mode === 0) {
            return modifyLightSchemeColor(rgb, theme);
        }
        const poleFg = getFgPole(theme);
        const poleBg = getBgPole(theme);
        return modifyColorWithCache(
            rgb,
            theme,
            modifyBorderHSL,
            poleFg,
            poleBg
        );
    }
    function modifyBorderColor(rgb, theme, shouldRegisterColorVariable = true) {
        if (!shouldRegisterColorVariable) {
            return _modifyBorderColor(rgb, theme);
        }
        return modifyAndRegisterColor("border", rgb, theme, _modifyBorderColor);
    }

    const themeColorTypes = {
        accentcolor: "bg",
        button_background_active: "text",
        button_background_hover: "text",
        frame: "bg",
        icons: "text",
        icons_attention: "text",
        ntp_background: "bg",
        ntp_text: "text",
        popup: "bg",
        popup_border: "bg",
        popup_highlight: "bg",
        popup_highlight_text: "text",
        popup_text: "text",
        sidebar: "bg",
        sidebar_border: "border",
        sidebar_text: "text",
        tab_background_text: "text",
        tab_line: "bg",
        tab_loading: "bg",
        tab_selected: "bg",
        textcolor: "text",
        toolbar: "bg",
        toolbar_bottom_separator: "border",
        toolbar_field: "bg",
        toolbar_field_border: "border",
        toolbar_field_border_focus: "border",
        toolbar_field_focus: "bg",
        toolbar_field_separator: "border",
        toolbar_field_text: "text",
        toolbar_field_text_focus: "text",
        toolbar_text: "text",
        toolbar_top_separator: "border",
        toolbar_vertical_separator: "border"
    };
    const $colors = {
        accentcolor: "#111111",
        frame: "#111111",
        ntp_background: "white",
        ntp_text: "black",
        popup: "#cccccc",
        popup_text: "black",
        sidebar: "#cccccc",
        sidebar_border: "#333",
        sidebar_text: "black",
        tab_background_text: "white",
        tab_loading: "#23aeff",
        textcolor: "white",
        toolbar: "#707070",
        toolbar_field: "lightgray",
        toolbar_field_text: "black"
    };
    function setWindowTheme(theme) {
        const colors = Object.entries($colors).reduce((obj, [key, value]) => {
            const type = themeColorTypes[key];
            const modify = {
                bg: modifyBackgroundColor,
                text: modifyForegroundColor,
                border: modifyBorderColor
            }[type];
            const rgb = parseColorWithCache(value);
            const modified = modify(rgb, theme, false);
            obj[key] = modified;
            return obj;
        }, {});
        if (
            typeof browser !== "undefined" &&
            browser.theme &&
            browser.theme.update
        ) {
            browser.theme.update({colors});
        }
    }
    function resetWindowTheme() {
        if (
            typeof browser !== "undefined" &&
            browser.theme &&
            browser.theme.reset
        ) {
            browser.theme.reset();
        }
    }

    var _a;
    class Extension {
        static init() {
            if (_a.initialized) {
                return;
            }
            _a.initialized = true;
            DevTools.init(_a.onSettingsChanged);
            Messenger.init(_a.getMessengerAdapter());
            TabManager.init({
                getConnectionMessage: _a.getConnectionMessage,
                getTabMessage: _a.getTabMessage,
                onColorSchemeChange: _a.onColorSchemeChange
            });
            _a.startBarrier = new PromiseBarrier();
            _a.stateManager = new StateManager(
                _a.LOCAL_STORAGE_KEY,
                _a,
                {
                    autoState: "",
                    wasEnabledOnLastCheck: null,
                    registeredContextMenus: null
                },
                logWarn
            );
            chrome.alarms.onAlarm.addListener(_a.alarmListener);
            if (chrome.commands) {
                {
                    chrome.commands.onCommand.addListener(
                        async (command, tab) =>
                            _a.onCommand(
                                command,
                                (tab && tab.id) || null,
                                0,
                                null
                            )
                    );
                }
            }
            if (chrome.permissions.onRemoved) {
                chrome.permissions.onRemoved.addListener((permissions) => {
                    var _b;
                    if (
                        !((_b =
                            permissions === null || permissions === void 0
                                ? void 0
                                : permissions.permissions) === null ||
                        _b === void 0
                            ? void 0
                            : _b.includes("contextMenus"))
                    ) {
                        _a.registeredContextMenus = false;
                    }
                });
            }
        }
        static async MV3syncSystemColorStateManager(isDark) {
            {
                return;
            }
        }
        static isExtensionSwitchedOn() {
            return (
                _a.autoState === "turn-on" ||
                _a.autoState === "scheme-dark" ||
                _a.autoState === "scheme-light" ||
                (_a.autoState === "" && UserStorage.settings.enabled)
            );
        }
        static updateAutoState() {
            const {mode, behavior, enabled} = UserStorage.settings.automation;
            let isAutoDark;
            let nextCheck;
            switch (mode) {
                case AutomationMode.TIME: {
                    const {time} = UserStorage.settings;
                    isAutoDark = isInTimeIntervalLocal(
                        time.activation,
                        time.deactivation
                    );
                    nextCheck = nextTimeInterval(
                        time.activation,
                        time.deactivation
                    );
                    break;
                }
                case AutomationMode.SYSTEM:
                    isAutoDark =
                        _a.wasLastColorSchemeDark === null
                            ? isSystemDarkModeEnabled()
                            : _a.wasLastColorSchemeDark;
                    break;
                case AutomationMode.LOCATION: {
                    const {latitude, longitude} = UserStorage.settings.location;
                    if (latitude != null && longitude != null) {
                        isAutoDark = isNightAtLocation(latitude, longitude);
                        nextCheck = nextTimeChangeAtLocation(
                            latitude,
                            longitude
                        );
                    }
                    break;
                }
                case AutomationMode.NONE:
                    break;
            }
            let state = "";
            if (enabled) {
                if (behavior === "OnOff") {
                    state = isAutoDark ? "turn-on" : "turn-off";
                } else if (behavior === "Scheme") {
                    state = isAutoDark ? "scheme-dark" : "scheme-light";
                }
            }
            _a.autoState = state;
            if (nextCheck) {
                if (nextCheck < Date.now()) {
                    logWarn(
                        `Alarm is set in the past: ${nextCheck}. The time is: ${new Date()}. ISO: ${new Date().toISOString()}`
                    );
                } else {
                    chrome.alarms.create(_a.ALARM_NAME, {when: nextCheck});
                }
            }
        }
        static runWakeDetector() {
            const WAKE_CHECK_INTERVAL = getDuration({minutes: 1});
            const WAKE_CHECK_INTERVAL_ERROR = getDuration({seconds: 10});
            if (this.wakeInterval >= 0) {
                clearInterval(this.wakeInterval);
            }
            let lastRun = Date.now();
            this.wakeInterval = setInterval(() => {
                const now = Date.now();
                if (
                    now - lastRun >
                    WAKE_CHECK_INTERVAL + WAKE_CHECK_INTERVAL_ERROR
                ) {
                    _a.handleAutomationCheck();
                }
                lastRun = now;
            }, WAKE_CHECK_INTERVAL);
        }
        static async start() {
            _a.init();
            await TabManager.cleanState();
            await Promise.all([
                ConfigManager.load({local: true}),
                _a.MV3syncSystemColorStateManager(null),
                UserStorage.loadSettings()
            ]);
            if (
                UserStorage.settings.enableContextMenus &&
                !_a.registeredContextMenus
            ) {
                chrome.permissions.contains(
                    {permissions: ["contextMenus"]},
                    (permitted) => {
                        if (permitted) {
                            _a.registerContextMenus();
                        }
                    }
                );
            }
            if (UserStorage.settings.syncSitesFixes) {
                await ConfigManager.load({local: false});
            }
            _a.updateAutoState();
            _a.runWakeDetector();
            _a.onAppToggle();
            logInfo("loaded", UserStorage.settings);
            {
                TabManager.updateContentScript({
                    runOnProtectedPages:
                        UserStorage.settings.enableForProtectedPages
                });
            }
            UserStorage.settings.fetchNews && Newsmaker.subscribe();
            _a.startBarrier.resolve();
        }
        static getMessengerAdapter() {
            return {
                collect: async () => {
                    return await _a.collectData();
                },
                collectDevToolsData: async () => {
                    return await _a.collectDevToolsData();
                },
                changeSettings: _a.changeSettings,
                setTheme: _a.setTheme,
                toggleActiveTab: _a.toggleActiveTab,
                markNewsAsRead: Newsmaker.markAsRead,
                markNewsAsDisplayed: Newsmaker.markAsDisplayed,
                loadConfig: ConfigManager.load,
                applyDevDynamicThemeFixes: DevTools.applyDynamicThemeFixes,
                resetDevDynamicThemeFixes: DevTools.resetDynamicThemeFixes,
                applyDevInversionFixes: DevTools.applyInversionFixes,
                resetDevInversionFixes: DevTools.resetInversionFixes,
                applyDevStaticThemes: DevTools.applyStaticThemes,
                resetDevStaticThemes: DevTools.resetStaticThemes,
                startActivation: _a.startActivation,
                resetActivation: _a.resetActivation,
                hideHighlights: UIHighlights.hideHighlights
            };
        }
        static registerContextMenus() {
            chrome.contextMenus.onClicked.addListener(
                async ({menuItemId, frameId, frameUrl, pageUrl}, tab) =>
                    _a.onCommand(
                        menuItemId,
                        (tab && tab.id) || null,
                        frameId || null,
                        frameUrl || pageUrl || null
                    )
            );
            chrome.contextMenus.removeAll(() => {
                _a.registeredContextMenus = false;
                chrome.contextMenus.create(
                    {
                        id: "DarkReader-top",
                        title: "Dark Reader"
                    },
                    () => {
                        if (chrome.runtime.lastError) {
                            return;
                        }
                        const msgToggle =
                            chrome.i18n.getMessage("toggle_extension");
                        const msgAddSite = chrome.i18n.getMessage(
                            "toggle_current_site"
                        );
                        const msgSwitchEngine = chrome.i18n.getMessage(
                            "theme_generation_mode"
                        );
                        chrome.contextMenus.create({
                            id: "toggle",
                            parentId: "DarkReader-top",
                            title: msgToggle || "Toggle everywhere"
                        });
                        chrome.contextMenus.create({
                            id: "addSite",
                            parentId: "DarkReader-top",
                            title: msgAddSite || "Toggle for current site"
                        });
                        chrome.contextMenus.create({
                            id: "switchEngine",
                            parentId: "DarkReader-top",
                            title: msgSwitchEngine || "Switch engine"
                        });
                        _a.registeredContextMenus = true;
                    }
                );
            });
        }
        static async getShortcuts() {
            const commands = await getCommands();
            return commands.reduce(
                (map, cmd) => Object.assign(map, {[cmd.name]: cmd.shortcut}),
                {}
            );
        }
        static async collectData() {
            await _a.loadData();
            const [
                news,
                shortcuts,
                activeTab,
                isAllowedFileSchemeAccess,
                uiHighlights
            ] = await Promise.all([
                Newsmaker.getLatest(),
                _a.getShortcuts(),
                _a.getActiveTabInfo(),
                new Promise((r) =>
                    chrome.extension.isAllowedFileSchemeAccess(r)
                ),
                UIHighlights.getHighlightsToShow()
            ]);
            return {
                isEnabled: _a.isExtensionSwitchedOn(),
                isReady: true,
                isAllowedFileSchemeAccess,
                settings: UserStorage.settings,
                news,
                shortcuts,
                colorScheme: ConfigManager.COLOR_SCHEMES_RAW,
                forcedScheme:
                    _a.autoState === "scheme-dark"
                        ? "dark"
                        : _a.autoState === "scheme-light"
                          ? "light"
                          : null,
                activeTab,
                uiHighlights
            };
        }
        static async collectDevToolsData() {
            const [dynamicFixesText, filterFixesText, staticThemesText] =
                await Promise.all([
                    DevTools.getDynamicThemeFixesText(),
                    DevTools.getInversionFixesText(),
                    DevTools.getStaticThemesText()
                ]);
            return {
                dynamicFixesText,
                filterFixesText,
                staticThemesText
            };
        }
        static async getActiveTabInfo() {
            await _a.loadData();
            const tab = await getActiveTab();
            const url = await TabManager.getTabURL(tab);
            const {isInDarkList, isProtected} = _a.getTabInfo(url);
            const isInjected = TabManager.canAccessTab(tab);
            const documentId = TabManager.getTabDocumentId(tab);
            let isDarkThemeDetected = null;
            if (UserStorage.settings.detectDarkTheme) {
                isDarkThemeDetected = TabManager.isTabDarkThemeDetected(tab);
            }
            const id = (tab && tab.id) || null;
            return {
                id,
                documentId,
                url,
                isInDarkList,
                isProtected,
                isInjected,
                isDarkThemeDetected
            };
        }
        static async getConnectionMessage(
            tabURL,
            url,
            isTopFrame,
            topFrameHasDarkTheme
        ) {
            await _a.loadData();
            return _a.getTabMessage(
                tabURL,
                url,
                isTopFrame,
                topFrameHasDarkTheme
            );
        }
        static async loadData() {
            _a.init();
            await Promise.all([
                _a.stateManager.loadState(),
                UserStorage.loadSettings()
            ]);
        }
        static async changeSettings($settings, onlyUpdateActiveTab = false) {
            const promises = [];
            const prev = {...UserStorage.settings};
            UserStorage.set($settings);
            if (
                prev.enabled !== UserStorage.settings.enabled ||
                prev.automation.enabled !==
                    UserStorage.settings.automation.enabled ||
                prev.automation.mode !== UserStorage.settings.automation.mode ||
                prev.automation.behavior !==
                    UserStorage.settings.automation.behavior ||
                prev.time.activation !== UserStorage.settings.time.activation ||
                prev.time.deactivation !==
                    UserStorage.settings.time.deactivation ||
                prev.location.latitude !==
                    UserStorage.settings.location.latitude ||
                prev.location.longitude !==
                    UserStorage.settings.location.longitude
            ) {
                _a.updateAutoState();
                _a.onAppToggle();
            }
            if (prev.syncSettings !== UserStorage.settings.syncSettings) {
                const promise = UserStorage.saveSyncSetting(
                    UserStorage.settings.syncSettings
                );
                promises.push(promise);
            }
            if (
                _a.isExtensionSwitchedOn() &&
                $settings.changeBrowserTheme != null &&
                prev.changeBrowserTheme !== $settings.changeBrowserTheme
            ) {
                if ($settings.changeBrowserTheme) {
                    setWindowTheme(UserStorage.settings.theme);
                } else {
                    resetWindowTheme();
                }
            }
            if (prev.fetchNews !== UserStorage.settings.fetchNews) {
                UserStorage.settings.fetchNews
                    ? Newsmaker.subscribe()
                    : Newsmaker.unSubscribe();
            }
            if (
                prev.enableContextMenus !==
                UserStorage.settings.enableContextMenus
            ) {
                if (UserStorage.settings.enableContextMenus) {
                    _a.registerContextMenus();
                } else {
                    chrome.contextMenus.removeAll();
                }
            }
            const promise = _a.onSettingsChanged(onlyUpdateActiveTab);
            promises.push(promise);
            await Promise.all(promises);
        }
        static setTheme($theme) {
            UserStorage.set({
                theme: {...UserStorage.settings.theme, ...$theme}
            });
            if (
                _a.isExtensionSwitchedOn() &&
                UserStorage.settings.changeBrowserTheme
            ) {
                setWindowTheme(UserStorage.settings.theme);
            }
            _a.onSettingsChanged();
        }
        static async reportChanges() {
            const info = await _a.collectData();
            Messenger.reportChanges(info);
        }
        static async toggleActiveTab() {
            const settings = UserStorage.settings;
            const tab = await _a.getActiveTabInfo();
            if (!tab) {
                return;
            }
            const {url} = tab;
            const isInDarkList = ConfigManager.isURLInDarkList(url);
            const host = getURLHostOrProtocol(url);
            function getToggledList(sourceList) {
                const list = sourceList.slice();
                let index = list.indexOf(host);
                if (index < 0 && host.startsWith("www.")) {
                    const noWwwHost = host.substring(4);
                    index = list.indexOf(noWwwHost);
                }
                if (index < 0) {
                    list.push(host);
                } else {
                    list.splice(index, 1);
                }
                return list;
            }
            const darkThemeDetected =
                settings.enabledByDefault &&
                settings.detectDarkTheme &&
                tab.isDarkThemeDetected;
            if (
                !settings.enabledByDefault ||
                isInDarkList ||
                darkThemeDetected
            ) {
                const toggledList = getToggledList(settings.enabledFor);
                _a.changeSettings({enabledFor: toggledList}, true);
                return;
            }
            if (
                settings.enabledByDefault &&
                settings.enabledFor.includes(host)
            ) {
                const enabledFor = getToggledList(settings.enabledFor);
                const disabledFor = getToggledList(settings.disabledFor);
                _a.changeSettings({enabledFor, disabledFor}, true);
                return;
            }
            const toggledList = getToggledList(settings.disabledFor);
            _a.changeSettings({disabledFor: toggledList}, true);
        }
        static onAppToggle() {
            if (_a.isExtensionSwitchedOn()) {
                IconManager.setIcon({
                    isActive: true,
                    colorScheme: UserStorage.settings.theme.mode
                        ? "dark"
                        : "light"
                });
            } else {
                IconManager.setIcon({
                    isActive: false,
                    colorScheme: UserStorage.settings.theme.mode
                        ? "dark"
                        : "light"
                });
            }
            if (UserStorage.settings.changeBrowserTheme) {
                if (
                    _a.isExtensionSwitchedOn() &&
                    _a.autoState !== "scheme-light"
                ) {
                    setWindowTheme(UserStorage.settings.theme);
                } else {
                    resetWindowTheme();
                }
            }
        }
        static async onSettingsChanged(onlyUpdateActiveTab = false) {
            await _a.loadData();
            _a.wasEnabledOnLastCheck = _a.isExtensionSwitchedOn();
            TabManager.sendMessage(onlyUpdateActiveTab);
            _a.saveUserSettings();
            _a.reportChanges();
            IconManager.setIcon({
                colorScheme: UserStorage.settings.theme.mode ? "dark" : "light"
            });
            _a.stateManager.saveState();
        }
        static async startActivation(email, key) {
            const delay = 2000 + Math.round(Math.random() * 2000);
            const checkEmail = (email) => email && email.trim().includes("@");
            const checkKey = (key) =>
                key.replaceAll("-", "").length === 25 &&
                key.toLocaleLowerCase().startsWith("dr") &&
                key.replaceAll("-", "").match(/^[0-9a-z]{25}$/i);
            setTimeout(async () => {
                await writeLocalStorage({
                    activationEmail: email,
                    activationKey: key
                });
                if (checkEmail(email) && checkKey(key)) {
                    await UIHighlights.hideHighlights(["anniversary"]);
                }
                _a.reportChanges();
            }, delay);
        }
        static async resetActivation() {
            await removeLocalStorage(["activationEmail", "activationKey"]);
            await UIHighlights.restoreHighlights(["anniversary"]);
            _a.reportChanges();
        }
        static getTabInfo(tabURL) {
            const isInDarkList = ConfigManager.isURLInDarkList(tabURL);
            const isProtected = !canInjectScript(tabURL);
            return {
                isInDarkList,
                isProtected
            };
        }
        static async saveUserSettings() {
            await UserStorage.saveSettings();
            logInfo("saved", UserStorage.settings);
        }
    }
    _a = Extension;
    Extension.autoState = "";
    Extension.wasEnabledOnLastCheck = null;
    Extension.registeredContextMenus = null;
    Extension.wasLastColorSchemeDark = null;
    Extension.startBarrier = null;
    Extension.stateManager = null;
    Extension.ALARM_NAME = "auto-time-alarm";
    Extension.LOCAL_STORAGE_KEY = "Extension-state";
    Extension.SYSTEM_COLOR_LOCAL_STORAGE_KEY = "system-color-state";
    Extension.initialized = false;
    Extension.isFirstLoad = false;
    Extension.alarmListener = (alarm) => {
        if (alarm.name === _a.ALARM_NAME) {
            _a.loadData().then(() => _a.handleAutomationCheck());
        }
    };
    Extension.wakeInterval = -1;
    Extension.onCommandInternal = async (command, tabId, frameId, frameURL) => {
        if (_a.startBarrier.isPending()) {
            await _a.startBarrier.entry();
        }
        _a.stateManager.loadState();
        switch (command) {
            case "toggle":
                _a.changeSettings({
                    enabled: !_a.isExtensionSwitchedOn(),
                    automation: {
                        ...UserStorage.settings.automation,
                        ...{enabled: false}
                    }
                });
                break;
            case "addSite": {
                async function scriptPDF(tabId, frameId) {
                    if (
                        !(Number.isInteger(tabId) && Number.isInteger(frameId))
                    ) {
                        return false;
                    }
                    function detectPDF() {
                        if (document.body.childElementCount !== 1) {
                            return false;
                        }
                        const {nodeName, type} = document.body.childNodes[0];
                        return (
                            nodeName === "EMBED" && type === "application/pdf"
                        );
                    }
                    {
                        return new Promise((resolve) =>
                            chrome.tabs.executeScript(
                                tabId,
                                {
                                    frameId,
                                    code: `(${detectPDF.toString()})()`
                                },
                                (results) =>
                                    resolve(
                                        results === null || results === void 0
                                            ? void 0
                                            : results[0]
                                    )
                            )
                        );
                    }
                }
                const pdf = async () =>
                    isPDF(frameURL || (await TabManager.getActiveTabURL()));
                if ((await scriptPDF(tabId, frameId)) || (await pdf())) {
                    _a.changeSettings({
                        enableForPDF: !UserStorage.settings.enableForPDF
                    });
                } else {
                    _a.toggleActiveTab();
                }
                break;
            }
            case "switchEngine": {
                const engines = Object.values(ThemeEngine);
                const index = engines.indexOf(
                    UserStorage.settings.theme.engine
                );
                const next = engines[(index + 1) % engines.length];
                _a.setTheme({engine: next});
                break;
            }
        }
    };
    Extension.onCommand = debounce(75, _a.onCommandInternal);
    Extension.onColorSchemeChange = async (isDark) => {
        if (_a.wasLastColorSchemeDark === isDark) {
            return;
        }
        _a.wasLastColorSchemeDark = isDark;
        _a.MV3syncSystemColorStateManager(isDark);
        await _a.loadData();
        if (UserStorage.settings.automation.mode !== AutomationMode.SYSTEM) {
            return;
        }
        _a.handleAutomationCheck();
    };
    Extension.handleAutomationCheck = () => {
        _a.updateAutoState();
        const isSwitchedOn = _a.isExtensionSwitchedOn();
        if (
            _a.wasEnabledOnLastCheck === null ||
            _a.wasEnabledOnLastCheck !== isSwitchedOn ||
            _a.autoState === "scheme-dark" ||
            _a.autoState === "scheme-light"
        ) {
            _a.wasEnabledOnLastCheck = isSwitchedOn;
            _a.onAppToggle();
            TabManager.sendMessage();
            _a.reportChanges();
            _a.stateManager.saveState();
        }
    };
    Extension.getTabMessage = (
        tabURL,
        url,
        isTopFrame,
        topFrameHasDarkTheme
    ) => {
        const settings = UserStorage.settings;
        const tabInfo = _a.getTabInfo(tabURL);
        if (
            _a.isExtensionSwitchedOn() &&
            isURLEnabled(tabURL, settings, tabInfo) &&
            !topFrameHasDarkTheme
        ) {
            const custom = settings.customThemes.find(({url: urlList}) =>
                isURLInList(tabURL, urlList)
            );
            const preset = custom
                ? null
                : settings.presets.find(({urls}) => isURLInList(tabURL, urls));
            let theme = custom
                ? custom.theme
                : preset
                  ? preset.theme
                  : settings.theme;
            if (
                _a.autoState === "scheme-dark" ||
                _a.autoState === "scheme-light"
            ) {
                const mode = _a.autoState === "scheme-dark" ? 1 : 0;
                theme = {...theme, mode};
            }
            const detectorHints = settings.detectDarkTheme
                ? getDetectorHintsFor(
                      url,
                      ConfigManager.DETECTOR_HINTS_RAW,
                      ConfigManager.DETECTOR_HINTS_INDEX
                  )
                : null;
            const detectDarkTheme =
                settings.detectDarkTheme &&
                (isTopFrame ||
                    (detectorHints === null || detectorHints === void 0
                        ? void 0
                        : detectorHints.some((h) => h.iframe))) &&
                !isURLInList(tabURL, settings.enabledFor) &&
                !isPDF(tabURL);
            logInfo(`Custom theme ${custom ? "was found" : "was not found"}, Preset theme ${preset ? "was found" : "was not found"}
            The theme(${custom ? "custom" : preset ? "preset" : "global"} settings) used is: ${JSON.stringify(theme)}`);
            switch (theme.engine) {
                case ThemeEngine.cssFilter: {
                    return {
                        type: MessageTypeBGtoCS.ADD_CSS_FILTER,
                        data: {
                            css: createCSSFilterStyleSheet(
                                theme,
                                url,
                                isTopFrame,
                                ConfigManager.INVERSION_FIXES_RAW,
                                ConfigManager.INVERSION_FIXES_INDEX
                            ),
                            detectDarkTheme,
                            detectorHints,
                            theme
                        }
                    };
                }
                case ThemeEngine.svgFilter: {
                    return {
                        type: MessageTypeBGtoCS.ADD_SVG_FILTER,
                        data: {
                            css: createSVGFilterStylesheet(
                                theme,
                                url,
                                isTopFrame,
                                ConfigManager.INVERSION_FIXES_RAW,
                                ConfigManager.INVERSION_FIXES_INDEX
                            ),
                            svgMatrix: getSVGFilterMatrixValue(theme),
                            svgReverseMatrix: getSVGReverseFilterMatrixValue(),
                            detectDarkTheme,
                            detectorHints,
                            theme
                        }
                    };
                }
                case ThemeEngine.staticTheme: {
                    return {
                        type: MessageTypeBGtoCS.ADD_STATIC_THEME,
                        data: {
                            css:
                                theme.stylesheet && theme.stylesheet.trim()
                                    ? theme.stylesheet
                                    : createStaticStylesheet(
                                          theme,
                                          url,
                                          isTopFrame,
                                          ConfigManager.STATIC_THEMES_RAW,
                                          ConfigManager.STATIC_THEMES_INDEX
                                      ),
                            detectDarkTheme: settings.detectDarkTheme,
                            detectorHints,
                            theme
                        }
                    };
                }
                case ThemeEngine.dynamicTheme: {
                    const fixes = getDynamicThemeFixesFor(
                        url,
                        isTopFrame,
                        ConfigManager.DYNAMIC_THEME_FIXES_RAW,
                        ConfigManager.DYNAMIC_THEME_FIXES_INDEX,
                        UserStorage.settings.enableForPDF
                    );
                    return {
                        type: MessageTypeBGtoCS.ADD_DYNAMIC_THEME,
                        data: {
                            theme,
                            fixes,
                            isIFrame: !isTopFrame,
                            detectDarkTheme,
                            detectorHints
                        }
                    };
                }
                default:
                    throw new Error(`Unknown engine ${theme.engine}`);
            }
        }
        return {
            type: MessageTypeBGtoCS.CLEAN_UP
        };
    };

    function makeChromiumHappy() {
        chrome.runtime.onMessage.addListener(
            (message, sender, sendResponse) => {
                if (
                    ![
                        MessageTypeUItoBG.GET_DATA,
                        MessageTypeUItoBG.GET_DEVTOOLS_DATA,
                        MessageTypeUItoBG.APPLY_DEV_DYNAMIC_THEME_FIXES,
                        MessageTypeUItoBG.APPLY_DEV_INVERSION_FIXES,
                        MessageTypeUItoBG.APPLY_DEV_STATIC_THEMES
                    ].includes(message.type) &&
                    (message.type !== MessageTypeCStoBG.DOCUMENT_CONNECT ||
                        !isPanel(sender))
                ) {
                    sendResponse({type: "¯\\_(ツ)_/¯"});
                }
            }
        );
    }

    Extension.start();
    const welcome = `  /''''\\
 (0)==(0)
/__||||__\\
Welcome to Dark Reader!`;
    console.log(welcome);
    {
        chrome.runtime.onInstalled.addListener(({reason}) => {
            if (reason === "install") {
                chrome.tabs.create({url: getHelpURL()});
            }
        });
        chrome.runtime.setUninstallURL(UNINSTALL_URL);
    }
    makeChromiumHappy();
    function writeInstallationVersion(storage, details) {
        storage.get({installation: {version: ""}}, (data) => {
            var _a, _b;
            if (
                (_a =
                    data === null || data === void 0
                        ? void 0
                        : data.installation) === null || _a === void 0
                    ? void 0
                    : _a.version
            ) {
                return;
            }
            storage.set({
                installation: {
                    date: Date.now(),
                    reason: details.reason,
                    version:
                        (_b = details.previousVersion) !== null && _b !== void 0
                            ? _b
                            : chrome.runtime.getManifest().version
                }
            });
        });
    }
    chrome.runtime.onInstalled.addListener((details) => {
        writeInstallationVersion(chrome.storage.local, details);
        writeInstallationVersion(chrome.storage.sync, details);
    });
})();
