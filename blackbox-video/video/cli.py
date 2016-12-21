from . import Video, process_frames
from .postprocess import PostProcessor
import multiprocessing
import math, time

import click

@click.command('video')
@click.option('-vf', default="input.mp4")
@click.option('-df', default="input.csv")
@click.option('-o', default="output.avi")
@click.option('-c', default=1)
def main(vf,df,o, c):
    start = time.time()

    video = Video(vf)

    processes = min(int(c), multiprocessing.cpu_count())
    print("Using {} processes".format(processes))

    total_frames = video.frames
    frames_per_process = math.ceil(float(total_frames) / float(processes))
    print("Handling {} frames per process".format(frames_per_process))

    frame_batches = [(int(x),int(x+frames_per_process-1) if x+frames_per_process-1 <= total_frames else total_frames) for x in range(0,total_frames,int(frames_per_process))]
    print("batches")
    print(frame_batches)

    processes =[]
    output_files =[]
    for i,batch in enumerate(frame_batches):
        filename = vf
        output_filename = '{}-{}_tmp.avi'.format(o,i)
        output_files.append(output_filename)
    #
        print("Start processing {} -> {}, from frame {} to frame {}".format(filename,output_filename,batch[0],batch[1]))
        p = multiprocessing.Process(target=process_frames, args=(filename,output_filename,df,batch[0],batch[1]))
        processes.append(p)
        p.start()

    for i,p in enumerate(processes):
        p.join()

    post = PostProcessor(vf,output_files)
    post.process(o)

    end = time.time()

    print("\n\n Total duration = {} min".format(float(end-start) / 60.0))