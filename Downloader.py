import youtube_dl
import os
def downloading_status(d):
	if(d['status']=='finished'): 
		print('...................................File Downloaded................................')
def downloader(url):
	print("..............................Downloading..............................")
	yt={
		'format':'bestaudio/best','outtmpl':'/Songs/%(title)s.%(ext)s',
		'postprocessor':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'128'}],
		'progess_hooks':[downloading_status]
	}
	with youtube_dl.YoutubeDL(yt) as y:
		y.download([url]) 
		video_info=y.extract_info(url,download=False)
		video_title=video_info.get('title',None)
		print("Downloading video {}".format(video_title))
		return video_title