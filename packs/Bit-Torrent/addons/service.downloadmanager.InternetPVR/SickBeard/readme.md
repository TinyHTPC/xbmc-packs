# Sickbeard for Torrents

This is a fork of the incredible [Sick Beard](https://github.com/midgetspy/Sick-Beard), with some additions regarding torrent support and some other areas.  
Specifically it includes
* Integrated torrent client (provided python-libtorrent is available).  Enable it by selecting Config -> Search Settings -> Torrent Method -> Integrated.  [See here for more info](http://brickybox.com/2013/05/09/sickbeard-with-integrated-torrent-client).
* Support for Custom RSS Torrent feeds.  [See here for more info](http://brickybox.com/2013/04/24/sickbeard-manual-rss-custom-torrent-providers).
* Support for the [ShowRSS](http://showrss.karmorra.info/) torrent feed (with backlog support).
* Support for [PublicHD](http://publichd.se/).
* Support for iPlayer downloads (via the [get_iplayer perl script](http://www.infradead.org/get_iplayer/html/get_iplayer.html)). [See here for how to set this up](http://brickybox.com/2013/03/05/sickbeard-iplayer-requirements).
* A UI for adding custom (local) scene exception names.
* Use of twitter, tpb, and feedburner rss feeds as fallbacks when ezrss fails.
* Support for the [Kickass Torrents](http://kickass.to/) torrent site (including backlog).  Searches verified torrents only.
* Support for scene numbering at the episode level.  If scene numbering does not agree with tvdb numbering (as is often the case) the show will still be downloaded and saved correctly.
* Support for magnet links.

Requires Python 2.5, 2.6, or 2.7.

[Installation Instructions](https://github.com/bricky/Sick-Beard/wiki/How-To-Install-Sickbeard-for-Torrents)

See [here](http://brickybox.com/2012/09/24/sickbeard-fork-feature-summary) for some further info.  


* * *

*The original readme from Sick Beard is available [here](https://github.com/midgetspy/Sick-Beard/blob/master/readme.md).*

* * *

