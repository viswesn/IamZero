import subprocess
import shlex


def cmd(command):
    print command
    p = subprocess.Popen(shlex.split(command),
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    return (stdout, stderr)

if __name__ == "__main__":
    cmd("C://rclone//rclone.exe sync \"C://Go//doc//articles//wiki\" Gdrive:Sony -v")