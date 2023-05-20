import json
import savestate
from pathlib import Path

def pack(output, chatgpt, debater):
    out_data = {}
    with open(chatgpt, 'r') as chatgpt_f:
        out_data['chatgpt'] = json.load(chatgpt_f)
    with savestate.open(Path(debater), 'r') as debater_f:
        out_data['debater'] = {}
        for key in debater_f:
            out_data['debater'][key] = debater_f[key]
    with open(output, 'w') as output_f:
        json.dump(out_data, output_f)
    print(f'Packed data from {chatgpt} and {debater} to {output}')

def unpack(input_file, chatgpt, debater):
    with open(input_file, 'r') as input_f:
        data = json.load(input_f)
    with open(chatgpt, 'w') as chatgpt_f:
        json.dump(data['chatgpt'], chatgpt_f)
    with savestate.open(Path(debater), 'c') as debater_f:
        for key in data['debater']:
            debater_f[key] = data['debater'][key]
    print(f'Unpacked data to {chatgpt} and {debater} from {input_file}')
