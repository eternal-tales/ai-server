import os
import shutil
import subprocess
import time
import wget
from subprocess import check_output
from os import listdir

# Create/Load a Session

Session_Name = "test0"  # param{type: 'string'}
MODEL_NAME = ""  # param{type: 'string'}
PT = ""

while Session_Name == "":
    print('[1;31mInput the Session Name:')
    Session_Name = input('')
Session_Name = Session_Name.replace(" ", "_")
print(f"Session Name is {Session_Name}")

# Enter the session name, it if it exists, it will load it, otherwise it'll create an new session.
Session_Link_optional = ""  # @param{type: 'string'}
# Import a session from another gdrive, the shared gdrive link must point to the specific session's folder that contains the trained CKPT, remove any intermediary CKPT if any.

WORKSPACE = '/content/Fast-Dreambooth'

INSTANCE_NAME = Session_Name

OUTPUT_DIR = "/content/models/"+Session_Name
SESSION_DIR = WORKSPACE+'/Sessions/'+Session_Name
INSTANCE_DIR = SESSION_DIR+'/instance_images'
CAPTIONS_DIR = SESSION_DIR+'/captions'
MDLPTH = str(SESSION_DIR+"/"+Session_Name+'.ckpt')

if os.path.exists(str(SESSION_DIR)):
    mdls = [ckpt for ckpt in listdir(
        SESSION_DIR) if ckpt.split(".")[-1] == "ckpt"]
    if not os.path.exists(MDLPTH) and '.ckpt' in str(mdls):

        def f(n):
            k = 0
            for i in mdls:
                if k == n:
                    # !mv "$SESSION_DIR/$i" $MDLPTH
                    source_path = os.path.join(SESSION_DIR, i)
                    shutil.move(source_path, MDLPTH)
                k = k+1

        k = 0
        print('[1;33mNo final checkpoint model found, select which intermediary checkpoint to use, enter only the number, (000 to skip):\n[1;34m')

        for i in mdls:
            print(str(k)+'- '+i)
            k = k+1
        n = input()
        while int(n) > k-1:
            n = input()
        if n != "000":
            f(int(n))
            print('[1;32mUsing the model ' + mdls[int(n)]+" ...")
            time.sleep(2)
        else:
            print('[1;32mSkipping the intermediary checkpoints.')
        del n

if os.path.exists(str(SESSION_DIR)) and not os.path.exists(MDLPTH):
    print('[1;32mLoading session with no previous model, using the original model or the custom downloaded model')
    if MODEL_NAME == "":
        print(
            '[1;31mNo model found, use the "Model Download" cell to download a model.')
    else:
        print('[1;32mSession Loaded, proceed to uploading instance images')

elif os.path.exists(MDLPTH):

    print('\033[1;32mSession found, loading the trained model ...')
    # Download and run the model version detection script
    det_script_url = 'https://github.com/TheLastBen/fast-stable-diffusion/raw/main/Dreambooth/det.py'
    det_script_path = wget.download(det_script_url)
    print('\033[1;33mDetecting model version...')
    Model_Version = subprocess.check_output(
        ['python', det_script_path, '--MODEL_PATH', MDLPTH], text=True).strip()
    os.remove(det_script_path)  # Remove the det.py script after use
    print('\033[1;32m' + Model_Version + ' Detected')

    if Model_Version == '1.5':
        config_yaml_url = 'https://github.com/CompVis/stable-diffusion/raw/main/configs/stable-diffusion/v1-inference.yaml'
        config_yaml_path = wget.download(config_yaml_url)
        print('\033[1;32mSession found, loading the trained model ...')
        subprocess.run(['python', '/content/diffusers/scripts/convert_original_stable_diffusion_to_diffusers.py',
                        '--checkpoint_path', MDLPTH, '--dump_path', OUTPUT_DIR, '--original_config_file', config_yaml_path])
        os.remove(config_yaml_path)  # Remove the config file after use

    if os.path.exists(OUTPUT_DIR+'/unet/diffusion_pytorch_model.bin'):
        resume = True
        print('[1;32mSession loaded.')
    else:
        if not os.path.exists(OUTPUT_DIR+'/unet/diffusion_pytorch_model.bin'):
            print(
                '[1;31mConversion error, if the error persists, remove the CKPT file from the current session folder')

elif not os.path.exists(str(SESSION_DIR)):
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    print('[1;32mCreating session...')
    if MODEL_NAME == "":
        print(
            '[1;31mNo model found, use the "Model Download" cell to download a model.')
    else:
        print('[1;32mSession created, proceed to uploading instance images')
