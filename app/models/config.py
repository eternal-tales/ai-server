# Set dependency

# diffusers 모델 직접 다운로드 받는 것으로 대체

import subprocess
import os
import shutil
import requests


def install_dependencies():
    print('\033[1;32mInstalling dependencies...')

    # Change current working directory to '/content', create if doesn't exist
    os.makedirs('/content', exist_ok=True)
    os.chdir('/content')

    # Install accelerate without dependencies
    subprocess.run(['pip', 'install', '--quiet', '--no-deps',
                   'accelerate==0.12.0'], check=True)

    # Download and install Debian packages and other dependencies
    subprocess.run(
        ['wget', '-q', '-i', 'https://raw.githubusercontent.com/TheLastBen/fast-stable-diffusion/main/Dependencies/dbdeps.txt'], check=True, shell=True)
    subprocess.run(['dpkg', '-i', '*.deb'], shell=True, check=True)

    subprocess.run(['tar', '-C', '/', '--zstd', '-xf',
                   'gcolabdeps.tar.zst'], check=True)

    for file in os.listdir():
        if file.endswith('.deb') or file.endswith('.zst') or file.endswith('.txt'):
            os.remove(file)

    # Clone the diffusers repository
    subprocess.run(['git', 'clone', '--quiet', '--depth', '1', '--branch',
                   'main', 'https://github.com/TheLastBen/diffusers'], check=True)

    # Gradio 미사용 예정
    # Install Gradio without dependencies
    # subprocess.run(['pip', 'install', 'gradio==3.16.2',
    #               '--no-deps', '--quiet'], check=True)

    # Setup environment for gperftools
    gperftools_path = '/content/sd/libtcmalloc/libtcmalloc_minimal.so.4'
    if not os.path.exists(gperftools_path):
        os.environ['CXXFLAGS'] = '-std=c++14'
        subprocess.run(
            ['wget', '-q', 'https://github.com/gperftools/gperftools/releases/download/gperftools-2.5/gperftools-2.5.tar.gz'], check=True)
        subprocess.run(['tar', 'zxf', 'gperftools-2.5.tar.gz'], check=True)
        shutil.move('gperftools-2.5', 'gperftools')
        subprocess.run(
            ['wget', '-q', 'https://github.com/TheLastBen/fast-stable-diffusion/raw/main/AUTOMATIC1111_files/Patch'], check=True)
        os.chdir('/content/gperftools')
        subprocess.run(['patch', '-p1', '<', '/content/Patch'],
                       shell=True, check=True)
        subprocess.run(['./configure', '--enable-minimal', '--enable-libunwind', '--enable-frame-pointers',
                       '--enable-dynamic-sized-delete-support', '--enable-sized-delete', '--enable-emergency-malloc'], check=True)
        subprocess.run(['make', '-j4'], check=True)
        os.makedirs('/content/sd/libtcmalloc', exist_ok=True)
        shutil.copy('.libs/libtcmalloc*.so*',
                    '/content/sd/libtcmalloc', follow_symlinks=True)
        os.environ['LD_PRELOAD'] = gperftools_path
        os.chdir('/content')
        for file in os.listdir():
            if file.endswith('.tar.gz') or file == 'Patch':
                os.remove(file)
        shutil.rmtree('/content/gperftools', ignore_errors=True)
    else:
        os.environ['LD_PRELOAD'] = gperftools_path

    # Suppress TensorFlow warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['PYTHONWARNINGS'] = 'ignore'

    print('\033[1;32mDone, proceed')


if __name__ == '__main__':
    install_dependencies()
