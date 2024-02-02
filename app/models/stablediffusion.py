# Model Download
import os
import requests
import wget
import re
import six
import subprocess
import urllib.request
from urllib.parse import urlparse, parse_qs, unquote
from subprocess import check_output
from IPython.display import clear_output
import time
import shutil


def getsrc(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'civitai.com':
        src = 'civitai'
    elif parsed_url.netloc == 'drive.google.com':
        src = 'gdrive'
    elif parsed_url.netloc == 'huggingface.co':
        src = 'huggingface'
    else:
        src = 'others'
    return src


def get_name(url, gdrive):
    if not gdrive:
        response = requests.get(url, allow_redirects=False)
        if "Location" in response.headers:
            redirected_url = response.headers["Location"]
            quer = parse_qs(urlparse(redirected_url).query)
            if "response-content-disposition" in quer:
                disp_val = quer["response-content-disposition"][0].split(";")
                for vals in disp_val:
                    if vals.strip().startswith("filename="):
                        filenm = unquote(vals.split("=", 1)[1].strip())
                        return filenm.replace("\"", "")
    else:  # 오류 시 gdrive 부분 수정 필요
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
        lnk = "https://drive.google.com/uc?id={id}&export=download".format(
            id=url[url.find("/d/")+3:url.find("/view")])
        res = requests.session().get(lnk, headers=headers, stream=True, verify=True)
        res = requests.session().get(get_url_from_gdrive_confirmation(
            res.text), headers=headers, stream=True, verify=True)
        content_disposition = six.moves.urllib_parse.unquote(
            res.headers["Content-Disposition"])
        filenm = re.search(r"filename\*=UTF-8''(.*)",
                           content_disposition).groups()[0].replace(os.path.sep, "_")
        return filenm

# @markdown - Skip this cell if you are loading a previous session that contains a trained model.


# @markdown - Choose which version to finetune.
Model_Version = "1.5"  # @param [ "1.5", "V2.1-512px", "V2.1-768px"]

# @param {type:"string"}
Path_to_HuggingFace = "runwayml/stable-diffusion-v1-5"

# with capture.capture_output() as cap:
#    os.chdir('/content')

# Load and finetune a model from Hugging Face, use the format "profile/model" like : runwayml/stable-diffusion-v1-5
# If the custom model is private or requires a token, create token.txt containing the token in "Fast-Dreambooth" folder in your gdrive.

MODEL_PATH = ""  # @param {type:"string"}
MODEL_LINK = ""  # @param {type:"string"}


if os.path.exists('/content/gdrive/MyDrive/Fast-Dreambooth/token.txt'):
    with open("/content/gdrive/MyDrive/Fast-Dreambooth/token.txt") as f:
        token = f.read()
    authe = f'https://USER:{token}@'
else:
    authe = "https://"


def downloadmodel():
    model_dir = '/content/stable-diffusion-v1-5'

    # Remove the existing model directory if it exists
    if os.path.exists(model_dir):
        subprocess.run(['rm', '-r', model_dir], check=True)

    # Create a new model directory
    os.makedirs(model_dir, exist_ok=True)
    os.chdir(model_dir)

    # Configure git and sparse checkout
    subprocess.run(['git', 'config', '--global',
                   'init.defaultBranch', 'main'], check=True)
    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'lfs', 'install', '--system',
                   '--skip-repo'], check=True)
    subprocess.run(['git', 'remote', 'add', '-f', 'origin',
                   'https://huggingface.co/runwayml/stable-diffusion-v1-5'], check=True)
    subprocess.run(
        ['git', 'config', 'core.sparsecheckout', 'true'], check=True)

    # Setup sparse checkout
    with open('.git/info/sparse-checkout', 'w') as f:
        f.write("scheduler\ntext_encoder\ntokenizer\nunet\nvae\nmodel_index.json\n!vae/diffusion_pytorch_model.bin\n!*.safetensors\n!*.fp16.bin\n!*.non_ema.bin")

    # Pull the repository
    subprocess.run(['git', 'pull', 'origin', 'main'], check=True)

    # Check if the unet model bin exists and download the VAE model bin if needed
    if os.path.exists(os.path.join(model_dir, 'unet/diffusion_pytorch_model.bin')):
        model_vae_url = 'https://huggingface.co/stabilityai/sd-vae-ft-mse/resolve/main/diffusion_pytorch_model.bin'
        wget.download(model_vae_url, out='vae/diffusion_pytorch_model.bin')
        # Clean up git artifacts
        subprocess.run(['rm', '-r', '.git'], check=True)
        # Remove the model index.json
        subprocess.run(['rm', 'model_index.json'], check=True)
        model_index_json_url = 'https://raw.githubusercontent.com/TheLastBen/fast-stable-diffusion/main/Dreambooth/model_index.json'
        wget.download(model_index_json_url)  # Download a new model index.json
        os.chdir('/content')
        print('\033[1;32mDONE !')
    else:
        print('\033[1;31mSomething went wrong')
        # Implement retry or error handling logic as needed


def newdownloadmodel():
    model_dir = '/content/stable-diffusion-v2-768'

    # Ensure the working directory is /content
    os.chdir('/content')

    # Create the model directory
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    os.chdir(model_dir)

    # Configure git for the model repository
    subprocess.run(['git', 'config', '--global',
                   'init.defaultBranch', 'main'], check=True)
    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'lfs', 'install', '--system',
                   '--skip-repo'], check=True)
    subprocess.run(['git', 'remote', 'add', '-f', 'origin',
                   'https://huggingface.co/stabilityai/stable-diffusion-2-1'], check=True)
    subprocess.run(
        ['git', 'config', 'core.sparsecheckout', 'true'], check=True)

    # Setup sparse checkout
    with open('.git/info/sparse-checkout', 'w') as f:
        f.write("scheduler\ntext_encoder\ntokenizer\nunet\nvae\nfeature_extractor\nmodel_index.json\n!*.safetensors\n!*.fp16.bin")

    # Pull the repository
    subprocess.run(['git', 'pull', 'origin', 'main'], check=True)

    # Clean up git artifacts
    subprocess.run(['rm', '-r', '.git'], shell=True, check=True)

    # Return to the /content directory
    os.chdir('/content')
    print('\033[1;32mDONE !')


def newdownloadmodelb():
    model_dir = '/content/stable-diffusion-v2-512'

    # Ensure the working directory is /content and create the model directory if it doesn't exist
    os.chdir('/content')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # Change into the model directory
    os.chdir(model_dir)

    # Configure git for cloning
    subprocess.run(['git', 'config', '--global',
                   'init.defaultBranch', 'main'], check=True)
    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'lfs', 'install', '--system',
                   '--skip-repo'], check=True)
    subprocess.run(['git', 'remote', 'add', '-f', 'origin',
                   'https://huggingface.co/stabilityai/stable-diffusion-2-1-base'], check=True)
    subprocess.run(
        ['git', 'config', 'core.sparsecheckout', 'true'], check=True)

    # Write the sparse-checkout configuration
    with open('.git/info/sparse-checkout', 'w') as f:
        f.write("scheduler\ntext_encoder\ntokenizer\nunet\nvae\nfeature_extractor\nmodel_index.json\n!*.safetensors\n!*.fp16.bin")

    # Pull the specified branch from the repository
    subprocess.run(['git', 'pull', 'origin', 'main'], check=True)

    # Clean up by removing the .git directory
    subprocess.run(['rm', '-r', os.path.join(model_dir, '.git')],
                   shell=True, check=True)

    # Return to the /content directory
    os.chdir('/content')
    print('\033[1;32mDONE !')


# 복잡한 if-else 구문

# 허깅페이스
if Path_to_HuggingFace != "":

    model_dir = '/content/stable-diffusion-custom'
    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.makedirs(model_dir)
    os.chdir(model_dir)

    if authe == "https://":
        textenc = f"{authe}huggingface.co/{Path_to_HuggingFace}/resolve/main/text_encoder/pytorch_model.bin"
        txtenc_size = urllib.request.urlopen(
            textenc).info().get('Content-Length', None)
    else:
        textenc = f"https://huggingface.co/{Path_to_HuggingFace}/resolve/main/text_encoder/pytorch_model.bin"
        req = urllib.request.Request(textenc)
        req.add_header('Authorization', f'Bearer {token}')
        txtenc_size = urllib.request.urlopen(
            req).info().get('Content-Length', None)

    if int(txtenc_size) > 670000000:
        if os.path.exists('/content/stable-diffusion-custom'):
            subprocess.run(['rm', '-r', '/content/stable-diffusion-custom'])
        clear_output()
        os.chdir('/content')
        clear_output()
        print("[1;32mV2")

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        os.chdir(model_dir)

        # Git configuration and cloning
        subprocess.run(['git', 'config', '--global',
                       'init.defaultBranch', 'main'])
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'lfs', 'install', '--system', '--skip-repo'])
        subprocess.run(['git', 'remote', 'add', '-f', 'origin',
                       f"{authe}huggingface.co/{Path_to_HuggingFace}"])
        subprocess.run(['git', 'config', 'core.sparsecheckout', 'true'])

        # Write the sparse-checkout configuration
        sparse_checkout_content = "scheduler\ntext_encoder\ntokenizer\nunet\nvae\nfeature_extractor\nmodel_index.json\n!*.safetensors"
        with open('.git/info/sparse-checkout', 'w') as sparse_checkout_file:
            sparse_checkout_file.write(sparse_checkout_content)

        subprocess.run(['git', 'pull', 'origin', 'main'])

        if os.path.exists(f'{model_dir}/unet/diffusion_pytorch_model.bin'):
            subprocess.run(['rm', '-r', f'{model_dir}/.git'], shell=True)
            os.chdir('/content')
            MODEL_NAME = "/content/stable-diffusion-custom"
            clear_output()
            print('[1;32mDONE !')
        else:
            while not os.path.exists('/content/stable-diffusion-custom/unet/diffusion_pytorch_model.bin'):
                print('[1;31mCheck the link you provided')
                time.sleep(5)

    else:
        model_dir = '/content/stable-diffusion-custom'

        # Create the model directory if it doesn't exist
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        os.chdir(model_dir)

        # Initialize a new Git repository and configure it
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'lfs', 'install', '--system', '--skip-repo'])
        subprocess.run(['git', 'remote', 'add', '-f', 'origin',
                       f"{authe}huggingface.co/{Path_to_HuggingFace}"])
        subprocess.run(['git', 'config', 'core.sparsecheckout', 'true'])

        sparse_checkout_config = "scheduler\ntext_encoder\ntokenizer\nunet\nvae\nmodel_index.json\n!*.safetensors"
        with open('.git/info/sparse-checkout', 'w') as f:
            f.write(sparse_checkout_config)

        subprocess.run(['git', 'pull', 'origin', 'main'])

        # Post-download steps
        if os.path.exists('/content/stable-diffusion-custom/unet/diffusion_pytorch_model.bin'):
            # Cleanup git artifacts
            subprocess.run(['rm', '-r', f'{model_dir}/.git'], shell=True)
            # Remove existing model_index.json if present
            os.remove(f'{model_dir}/model_index.json')
            time.sleep(1)
            wget.download(
                'https://raw.githubusercontent.com/TheLastBen/fast-stable-diffusion/main/Dreambooth/model_index.json')
            os.chdir('/content')
            # MODEL_NAME="/content/stable-diffusion-custom"
            clear_output()
            print('[1;32mDONE !')
        else:
            while not os.path.exists('/content/stable-diffusion-custom/unet/diffusion_pytorch_model.bin'):
                print('[1;31mCheck the link you provided')
                time.sleep(5)


# 모델 패스
elif MODEL_PATH != "":

    modelname = os.path.basename(MODEL_PATH)
    sftnsr = ""
    if modelname.split('.')[-1] == 'safetensors':
        sftnsr = "--from_safetensors"

    # %cd /content
    os.chdir('/content')

    clear_output()
    if os.path.exists(str(MODEL_PATH)):
        wget.download(
            'https://github.com/TheLastBen/fast-stable-diffusion/raw/main/Dreambooth/det.py')
        print('[1;33mDetecting model version...')
        Custom_Model_Version = check_output('python det.py '+sftnsr+' --MODEL_PATH '+str(
            MODEL_PATH), shell=True).decode('utf-8').replace('\n', '')
        clear_output()
        print('[1;32m'+Custom_Model_Version+' Detected')

        # !rm det.py
        # Run the detection script
        result = subprocess.run(['python', 'det.py'] + sftnsr.split() +
                                ['--MODEL_PATH', MODEL_PATH], capture_output=True, text=True)
        Custom_Model_Version = result.stdout.strip()
        os.remove('det.py')  # Remove the detection script

        print('\033[1;32m' + Custom_Model_Version + ' Detected')

        if Custom_Model_Version == '1.5':
            # Download the V1 config file
            config_url = 'https://github.com/CompVis/stable-diffusion/raw/main/configs/stable-diffusion/v1-inference.yaml'
            wget.download(config_url, out='config.yaml')

            # Run the conversion script for V1
            subprocess.run(['python', '/content/diffusers/scripts/convert_original_stable_diffusion_to_diffusers.py',
                            '--checkpoint_path', MODEL_PATH, '--dump_path', 'stable-diffusion-custom',
                            '--original_config_file', 'config.yaml'] + sftnsr.split())
            os.remove('config.yaml')  # Remove the config file

        elif Custom_Model_Version == 'V2.1-512px':
            subprocess.run(['python', '/content/diffusers/scripts/convert_original_stable_diffusion_to_diffusers.py',
                            '--checkpoint_path', MODEL_PATH, '--dump_path', 'stable-diffusion-custom',
                            '--original_config_file', 'config.yaml'] + sftnsr.split())
            os.remove('config.yaml')  # Remove the config file

        elif Custom_Model_Version in ['V2.1-512px', 'V2.1-768px']:
            # Determine the correct conversion script based on the model version
            convert_script_url = 'https://raw.githubusercontent.com/TheLastBen/fast-stable-diffusion/main/Dreambooth/convertodiffv2.py' if Custom_Model_Version == 'V2.1-512px' else 'https://github.com/TheLastBen/fast-stable-diffusion/raw/main/Dreambooth/convertodiffv2-768.py'
            convert_script_name = 'convertodiff.py'
            wget.download(convert_script_url, out=convert_script_name)

            # Run the conversion script for V2
            reference_model = 'stabilityai/stable-diffusion-2-1-base' if Custom_Model_Version == 'V2.1-512px' else 'stabilityai/stable-diffusion-2-1'
            subprocess.run(['python', convert_script_name, MODEL_PATH, '/content/stable-diffusion-custom',
                            '--v2', '--reference_model', reference_model] + sftnsr.split())
            os.remove(convert_script_name)  # Remove the conversion script

            # 이하 불필요한 코드 삭제


# 모델 링크 구현 생략

# 마지막 else 문
else:
    if Model_Version == "1.5":
        if not os.path.exists('/content/stable-diffusion-v1-5'):
            downloadmodel()
            MODEL_NAME = "/content/stable-diffusion-v1-5"
        else:
            MODEL_NAME = "/content/stable-diffusion-v1-5"
            print("[1;32mThe v1.5 model already exists, using this model.")
    elif Model_Version == "V2.1-512px":
        if not os.path.exists('/content/stable-diffusion-v2-512'):
            newdownloadmodelb()
            MODEL_NAME = "/content/stable-diffusion-v2-512"
        else:
            MODEL_NAME = "/content/stable-diffusion-v2-512"
            print("[1;32mThe v2-512px model already exists, using this model.")
    elif Model_Version == "V2.1-768px":
        if not os.path.exists('/content/stable-diffusion-v2-768'):
            newdownloadmodel()
            MODEL_NAME = "/content/stable-diffusion-v2-768"
        else:
            MODEL_NAME = "/content/stable-diffusion-v2-768"
            print("[1;32mThe v2-768px model already exists, using this model.")
