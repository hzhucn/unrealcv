from unrealcv.automation import UE4Binary
from unrealcv.util import read_png, read_npy
from unrealcv import client
import matplotlib.pyplot as plt
import argparse, os

class Logger:
    def __init__(self, client, log_filename, output_folder):
        self.client = client
        self.log_filename = log_filename
        self.output_folder = output_folder
        self.log_file = open(log_filename, 'w')

    def writelines(self, text):
        self.log_file.writelines(str(text))

    def request(self, cmd):
        self.writelines('Request: ' + cmd + '\n')
        res = client.request(cmd)
        self.writelines('Response: ' + str(res[:50]) + '\n')
        # Trancate too long value
        return res

    def save_image(self, filename, img):
        abs_filename = os.path.join(self.output_folder, filename)
        plt.imsave(abs_filename, img)

def run_commands_demo(logger):
    logger.client.connect()
    logger.request('vget /unrealcv/status')
    res = logger.request('vget /camera/0/lit png')
    img = read_png(res)
    plt.imshow(img)

    res = logger.request('vget /camera/0/location')
    res = logger.request('vget /camera/0/rotation')

    # res = logger.request('vset /camera/0/location -162 -126 90')
    # res = logger.request('vset /camera/0/rotation 348 60 0')

    res = logger.request('vget /camera/0/lit png')
    img = read_png(res)
    res = logger.request('vget /camera/0/depth npy')
    depth = read_npy(res)
    clip_far = depth.mean() * 2
    depth[depth > clip_far] = clip_far
    # Trancate the depth of the window and sky to make it easier to see
    res = logger.request('vget /camera/0/normal npy')
    normal = read_npy(res)
    res = logger.request('vget /camera/0/object_mask png')
    object_mask = read_png(res)

    logger.save_image("img.png", img)
    logger.save_image("depth.png", depth)
    logger.save_image("surface_normal.png", normal)
    logger.save_image("object_mask.png", object_mask)

    res = logger.request('vget /camera/0/lit lit.png')
    res = logger.request('vget /camera/0/depth depth.png')
    res = logger.request('vget /camera/0/object_mask object_mask.png')

    res = logger.request('vget /objects')
    object_names = res.split(' ')
    logger.writelines(object_names[:5])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('binary_path', nargs='?', help = 'The UE4 binary to run, if this is empty, connect to the editor')
    parser.add_argument('--output_folder', help = 'Output folder for the log of this script')
    args = parser.parse_args()

    binary_path = args.binary_path
    # Use .exe file for windows.

    binary = None
    if binary_path:
        binary_name = os.path.basename(binary_path).split('.')[0]
        binary = UE4Binary(binary_path) # UE4Binary can support exe, linux and mac binary
    else:
        binary_name = editor


    if args.output_folder:
        output_folder = args.output_folder
    else:
        output_folder = binary_name

    if os.path.isdir(output_folder):
        print('Output folder %s already exists' % output_folder)
        return
    os.mkdir(output_folder)
    log_filename = os.path.join(output_folder, 'output.txt')

    logger = Logger(client, log_filename, output_folder)
    if binary:
        with binary:
            run_commands_demo(logger)
    else:
        run_commands_demo(logger)


if __name__ == '__main__':
    main()