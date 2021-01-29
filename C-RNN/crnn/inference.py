import run
import csv
import os
import torch

#config = json.load(open('saved_cv/0708_205545/checkpoints/config.json'))
#config['net_mode'] = 'init'
#config['cfg'] = 

checkpoint = torch.load('saved_cv/0708_205545/checkpoints/model_best.pth')
config = checkpoint['config']

path_dir='D:/urbansound8k-gunshot/' # TODO
path_list=os.listdir(path_dir)

for path_audio in path_list:
    if path_audio != '.DS_Store':
        try:
            #print(path_audio)
            print(path_dir+path_audio)
            run.infer_main(path_dir+path_audio, config, checkpoint)
            #python run.py path_dir+path_audio -r saved_cv/0708_205545/checkpoints/model_best.pth
        except:
            print('error')
            continue


headers = ['name','class','confidence','audio_time','program_time','percent']