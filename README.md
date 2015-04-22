This program, written by F5XS, downloads wallpapers from Konachan and 4Chan (for now), checks its dimensions if it is in an accordance with the user's preferred aspect ratio (16:9 by default), checks other properties such as minimalism and size, and downloads the wallpaper into a given directory.


Features:

* It downloads wallpapers! Yay! It downloads them from Konachan and 4Chan (/w/ and /wg/)
* You can select which aspect ratio is preferred.
* You can set the minimum size of an image in terms of pixel area (pixels sqrd).
* You can toggle downloading minimalist* wallpapers to on and off (variable is "delete_minimals")
* Stores download information and queue to a file so that the program can be continued at a different time


Cons:

* Automatic CLI. Not much interactivity.
* May produce unexpected results when computer is full in memory
* This program does not distinguish pornography so if you're asking why there's porn in your wallpapers, don't. It should be wise for the user to check all the downloaded wallpapers first before using them.
* This is an unfinished project. I have no time to finish this especially when there is academics to follow.


Unimplemented features:

* Some highly technical coding stuff.
* Interactivity
* Download from more websites (like Reddit, 8Chan, WallpapersWide, etc.)


Required external modules:

* Python Image Library's (PIL) fork module, Pillow
* Requests


How it works:

* scans the websites for new posted wallpapers
    * if the website also posted the resolution of the wallpaper, the wallpaper may already be judged by its size and dimensions
    * adds to queue if the wallpaper passed the size and dimension criteria
* downloads the wallpapers to memory
* checks the wallpapers if it passes the size, dimensions, and minimalism criteria
* if passed, saves the file; otherwise, discards it


\* Minimalism

> a given wallpaper is said to be minimalist if the wallpaper has a given color that takes up at least 12.5% (this threshold is editable, named as "freq_threshold") of the wallpaper. The wallpaper may or may not actually be minimalist. ![Example 1](http://i.imgur.com/i5Vb1SL.png) ![Example 2](http://i.imgur.com/T48SiJJ.jpg)

I just don't like minimal wallpapers