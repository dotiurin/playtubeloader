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


def collect(doc_lxml):
    new_soup = doc_lxml.find_all("a", class_='pl-video-title-link yt-uix-tile-link yt-uix-sessionlink spf-link ')[:]
    links_list = []
    for link in new_soup:
        final_link = link.get("href")
        links_list.append(final_link)
    final_link = links_list
    return final_link


def get_lxml_page(playlink):
    sauce = urllib.request.urlopen(playlink).read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
    return soup


def create_folder(doc_lxml):
    soup_title = doc_lxml.title.text.replace(' - YouTube', "")
    soup_title = "--" + soup_title
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
    if not os.path.exists('mp3 - '+soup_title+'/'+ylink+'.mp3'):
        try:
            clip = mp.VideoFileClip(soup_title+'/'+ylink+'.mp4')
        except OSError:
            clip = mp.VideoFileClip(soup_title+'/'+ylink+'.webm')
        clip.audio.write_audiofile('mp3 - '+soup_title+'/'+ylink+'.mp3', progress_bar=False, verbose=False)


def get_threads(item):
    threadcoef = int(len(item)/5)  # кол-во потоков
    threads = list(range(len(item)))[::threadcoef]
    return threads


def starter(soup_title, adress_list):
    for addr in adress_list:
        try:
            youlink = 'https://www.youtube.com' + addr
            ylink = urllib.request.urlopen(youlink).read()
            ylink = bs.BeautifulSoup(ylink, 'lxml')
            ylink = ylink.title.text.replace(' - YouTube', "")
            ylink = safe_filename(ylink)
            if not os.path.exists(soup_title + '/' + ylink + '.mp4') | (os.path.exists(soup_title + '/' + ylink + '.webm')):
                YouTube(youlink).streams.first().download(soup_title)
            convert_mp3(soup_title, ylink)
        except urllib.error.URLError:
            pass
        except pytube.exceptions.AgeRestrictionError:
            pass
        except pytube.exceptions.RegexMatchError:
            pass


def get_threads_lists(threads):
    zzz = zip(threads, threads[1:])
    for z in zzz:
        z = list(range(z[0], z[1]))
        yield(z)


def get_iteration_list(threads_list, elements_youtube_list):
    for iter_thead in threads_list:
        final_list = []
        for each in iter_thead:
            final_list.append(elements_youtube_list[each])
        yield(final_list)


playlist_link = 'https://www.youtube.com/playlist?list=PL9tY0BWXOZFvN_9mCk7b8h33NrlxiPTx1'
lxml_doc = get_lxml_page(playlist_link)
playlist_name = create_folder(lxml_doc)
video_hrefs_list = collect(lxml_doc)

threads_iter_lists = get_threads(video_hrefs_list)
threads_ls = get_threads_lists(threads_iter_lists)
threads_ls = get_iteration_list(threads_ls, video_hrefs_list)
for thread in threads_ls:
    t = threading.Thread(target=starter, args=(playlist_name, thread))
    threads_iter_lists.append(t)
    t.start()
