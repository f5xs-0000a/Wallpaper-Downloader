    This program, written by F5XS, downloads wallpapers from Konachan and 4Chan (for now), checks its dimensions if it
is in an accordance with the user's preferred aspect ratio (16:9 by default), checks other properties such as minimalism
and size, and downloads the wallpaper into a given directory.


Features:
1. It downloads wallpapers! Yay! It downloads them from Konachan and 4Chan (/w/ and /wg/)
2. You can select which aspect ratio is preferred.
3. You can set the minimum size of an image in terms of pixel area (pixels sqrd).
4. You can toggle downloading minimalist* wallpapers to on and off (variable is "delete_minimals")
5. Stores download information and queue to a file so that the program can be continued at a different time


Cons:
1. Automatic CLI. Not much interactivity.
2. May produce unexpected results when computer is full in memory
3. This program does not distinguish pornography so if you're asking why there's porn in your wallpapers, don't.
      It should be wise for the user to check all the downloaded wallpapers first before using them.
X. This is an unfinished project. I have no time to finish this especially when there is academics to follow.


Unimplemented features:
1. Some highly technical coding stuff.
2. Interactivity
3. Download from more websites (like Reddit, 8Chan, WallpapersWide, etc.)


Required external modules:
1. Python Image Library's (PIL) fork module, Pillow
2. Requests


How it works:
> scans the websites for new posted wallpapers
    > if the website also posted the resolution of the wallpaper, the wallpaper may already be judged by its size and
          dimensions
    > adds to queue if the wallpaper passed the size and dimension criteria
> downloads the wallpapers to memory
> checks the wallpapers if it passes the size, dimensions, and minimalism criteria
> if passed, saves the file; otherwise, discards it


* Minimalism - a given wallpaper is said to be minimalist if the wallpaper has a given color that takes up at least
                   12.5% (this threshold is editable, named as "freq_threshold") of the wallpaper. The wallpaper may
                   or may not actually be minimalist. Examples:
                       http://i.imgur.com/i5Vb1SL.png
                       http://i.imgur.com/T48SiJJ.jpg

               I just don't like minimal wallpapers