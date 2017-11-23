import moviepy.editor as mp
import urllib.error
import bs4 as bs
import urllib.request
import urllib
import pytube.exceptions
import os
import errno
from pytube import YouTube
from pytube.helpers import safe_filename
import threading


def collect(playlink):
    sauce = urllib.request.urlopen(playlink).read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
    new_soup = soup.find_all("a", class_='pl-video-title-link yt-uix-tile-link yt-uix-sessionlink spf-link ')[:]
    links_list = []
    for link in new_soup:
        final_link = link.get("href")
        links_list.append(final_link)
    final_link = links_list
    return final_link


def create_folder(playlink):
    sauce = urllib.request.urlopen(playlink).read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
    soup_title = soup.title.text.replace(' - YouTube', "")
    soup_title = safe_filename(soup_title)
    print(soup_title)
    try:
        os.makedirs(soup_title)
        return soup_title
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        return soup_title


def convert_mp3(soup_title, ylink):
    try:
        os.makedirs('mp3 - ' + soup_title)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    if not os.path.exists('mp3 - '+soup_title+'\\'+ylink+'.mp3'):
        try:
            clip = mp.VideoFileClip(soup_title+'\\'+ylink+'.mp4')
        except OSError:
            clip = mp.VideoFileClip(soup_title+'\\'+ylink+'.webm')

        clip.audio.write_audiofile('mp3 - '+soup_title+'//'+ylink+'.mp3', progress_bar=False)
        print(ylink+'.mp3 created')


def get_threads(item):
    threadcoef = int(len(item)/4)  # кол-во потоков
    threads = list(range(len(item)))[::threadcoef]
    print(threads)
    return threads


def starter(soup_title, item):
    for a in item:
        try:
            youlink = 'https://www.youtube.com' + a
            ylink = urllib.request.urlopen(youlink).read()
            ylink = bs.BeautifulSoup(ylink, 'lxml')
            ylink = ylink.title.text.replace(' - YouTube', "")
            ylink = safe_filename(ylink)
            if not os.path.exists(soup_title + '\\' + ylink + '.mp4') | (os.path.exists(soup_title + '\\' + ylink + '.webm')):
                YouTube(youlink).streams.first().download(soup_title)
                print("video downloaded "+ylink)
            else:
                print("video excists")
            convert_mp3(soup_title, ylink)
        except urllib.error.URLError:
            print('Connection error '+ylink)
        except pytube.exceptions.AgeRestrictionError:
            print('ADULT CONTENT '+ylink)
        except pytube.exceptions.RegexMatchError:
            print("pytube.exceptions.RegexMatchError")



playlink = 'https://www.youtube.com/playlist?list=PL9tY0BWXOZFvN_9mCk7b8h33NrlxiPTx1'
soup_title = create_folder(playlink)
item = collect(playlink)
threads = get_threads(item)
print(len(item))


def threads_lists(threads):
    zzz = zip(threads, threads[1:])
    for z in zzz:
        z = list(range(z[0], z[1]))
        yield(z)


threads_ls = threads_lists(threads)


def retarded_func(threads_ls, item):
    for thr in threads_ls:
        final_list = []
        for iter in thr:
            final_list.append(item[iter])
        yield(final_list)


threads_ls = retarded_func(threads_ls, item)

for thread in threads_ls:
    t = threading.Thread(target=starter, args=(soup_title, thread))
    threads.append(t)
    t.start()
