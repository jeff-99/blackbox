import subprocess, sys, os
import uuid
import os
import glob


class PostProcessor(object):
    def __init__(self, original_file_path ,new_file_path):
        self.original_file_path = original_file_path
        self.new_file_path = new_file_path


    def get_new_file_path(self):
        if isinstance(self.new_file_path,list):
            filename = self._merge_files(self.new_file_path)
            self.new_file_path = filename

        return self.new_file_path

    @staticmethod
    def _merge_files(filepaths):
        with open('files.tmp.txt','w') as f:
            for fp in filepaths:
                f.write("file '{}'\n".format(fp))

        filename = "{}.tmp.mp4".format(uuid.uuid1().hex)
        command = "ffmpeg -y -f concat -i files.tmp.txt -c copy {}".format(filename)

        subprocess.call(command,stdout=sys.stdout, stderr=sys.stderr,cwd=os.getcwd(),shell=True)

        return filename

    def get_audio_file(self):
        audio_filename = self.original_file_path.rsplit('.',1)[0] + ".mp3"
        # if not os.path.exists(audio_filename):
        command = 'ffmpeg -y -i {0} {1}'.format(self.original_file_path, audio_filename)
        subprocess.call(command,stdout=sys.stdout, stderr=sys.stderr,cwd=os.getcwd(),shell=True)

        return audio_filename

    @staticmethod
    def get_merged_file(audio_file, video_file, output_file):
        # output_file = "output/testing_{}.mp4".format(uuid.uuid4().hex)
        # if not os.path.exists(output_file):
        # command = 'ffmpeg -y -i {} -i {} -map 0:0 -map 1:0 -vcodec copy -acodec copy -absf aac_adtstoasc {}'.format(video_file, audio_file, output_file)
        command = 'ffmpeg -y -i {} -i {} -c copy {}'.format(video_file, audio_file, output_file)
        subprocess.call(command,stdout=sys.stdout, stderr=sys.stderr,cwd=os.getcwd(),shell=True)

        return output_file

    def cleanup_tempfiles(self):
        for i in glob.glob('output/*.tmp*'):
            os.remove(i)

        for i in glob.glob('*.tmp*'):
            os.remove(i)

    def process(self, output_file):
        video_filepath = self.get_new_file_path()
        audio_filepath = self.get_audio_file()

        self.get_merged_file(audio_filepath,video_filepath, output_file)
        # self.cleanup_tempfiles()


if __name__ == '__main__':
    p = PostProcessor('input/00027.m4v', 'output/test3.avi')
    p.process()

