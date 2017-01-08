import subprocess
import sys
import uuid
import os
import shutil


class PostProcessor(object):
    def __init__(self, output_file,original_file_path):
        self.output_file = output_file
        self.generated_video_files = []

        self.original_file_path = os.path.abspath(original_file_path)
        self.new_file_path = None

        # init an output directory where all processing will take place
        self.output_dir = 'output'
        working_dir = os.path.join(os.getcwd(), self.output_dir)
        if not os.path.isdir(working_dir):
            os.mkdir(working_dir)

        self.original_working_dir = os.getcwd()

    def generate_videofile_path(self, index):
        """
        Generate a temporary location to use for processing a part of the video
        :param index:
        :return:
        """
        filename = '{}-{}_tmp.avi'.format(self.output_file,index)
        path = os.path.join(self.output_dir,filename)
        return path

    def register_new_videofile(self):
        """
        Register an new temporary video file location
        and return the generated filepath
        :return:
        """
        index = len(self.generated_video_files)

        filename = self.generate_videofile_path(index)
        self.generated_video_files.append(os.path.basename(filename))

        return filename

    def get_new_file_path(self):
        """
        Create a new merged file if there are multiple output files
        :return:
        """
        if len(self.generated_video_files) > 0:
            filename = self._merge_files()
            self.new_file_path = filename

        return self.new_file_path

    def _merge_files(self):
        """
        Merge registered videofiles into a single video file and return the filepath of the merged file
        :return:
        """
        # change working directory to the temporary directory
        # because the ffmpeg call won't work with files in a separate directory
        os.chdir(self.output_dir)

        with open('files.tmp.txt','w') as f:
            for fp in self.generated_video_files:
                f.write("file '{}'\n".format(fp))

        filename = "{}.tmp.mp4".format(uuid.uuid1().hex)
        command = "ffmpeg -y -f concat -i files.tmp.txt -c copy {}".format(filename)
        self._execute_command(command)

        # and reset the original working directory
        os.chdir(self.original_working_dir)

        # filepath relative to the original working directory
        filepath = os.path.join(self.output_dir, filename)

        return filepath

    def get_audio_file(self):
        """
        Extract the audio from the original video file so we can merge it with the newly created video file
        :return:
        """
        audio_filename = self.original_file_path.rsplit('.',1)[0] + ".mp3"

        command = 'ffmpeg -y -i {0} {1}'.format(self.original_file_path, audio_filename)
        self._execute_command(command)

        return audio_filename

    def get_merged_file(self, audio_file, video_file):
        """
        Merge the audio file extracted from the original video and merge it with the newly created video file
        and save it as the output_file
        :param audio_file:
        :param video_file:
        :return:
        """
        command = 'ffmpeg -y -i {} -i {} -c copy {}'.format(video_file, audio_file, self.output_file)
        self._execute_command(command)

        return self.output_file

    def cleanup_tempfiles(self):
        """
        remove the temporary output directory
        :return:
        """
        shutil.rmtree(self.output_dir)

    def process(self):
        try:
            audio_filepath = self.get_audio_file()
            video_filepath = self.get_new_file_path()

            self.get_merged_file(audio_filepath,video_filepath)
        finally:
            self.cleanup_tempfiles()

    @staticmethod
    def _execute_command(command):
        """
        Helper method to execute ffmpeg commands
        :param command:
        :return:
        """
        print("executing : ".format(command))
        subprocess.call(command,stdout=sys.stdout, stderr=sys.stderr,cwd=os.getcwd(),shell=True)

if __name__ == '__main__':
    pass

