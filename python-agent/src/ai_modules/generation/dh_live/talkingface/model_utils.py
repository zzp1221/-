import sys
import numpy as np
from scipy.io import wavfile
import torch
import torchaudio

device = "cuda" if torch.cuda.is_available() else "cpu"
# device = "cpu"
pca = None
def LoadAudioModel(ckpt_path):
    # if method == "lstm":
    #     ckpt_path = 'checkpoint/lstm/lstm_model_epoch_560.pth'
    #     Audio2FeatureModel = torch.load(model_path).to(device)
    #     Audio2FeatureModel.eval()
    from talkingface.models.audio2bs_lstm import Audio2Feature
    Audio2FeatureModel = Audio2Feature()  # 调用模型Model
    checkpoint = torch.load(ckpt_path, map_location=device)
    Audio2FeatureModel.load_state_dict(checkpoint)
    Audio2FeatureModel = Audio2FeatureModel.to(device)
    Audio2FeatureModel.eval()
    return Audio2FeatureModel

def LoadRenderModel(ckpt_path, model_name = "one_ref"):
    if model_name == "one_ref":
        from talkingface.models.DINet import LeeNet as DINet
        n_ref = 1
        source_channel = 3
        ref_channel = n_ref * 6
    else:
        from talkingface.models.DINet import DINet_five_Ref as DINet
        n_ref = 5
        source_channel = 6
        ref_channel = n_ref * 6
    net_g = DINet(source_channel, ref_channel).to(device)
    checkpoint = torch.load(ckpt_path)
    net_g_static = checkpoint['state_dict']['net_g']
    net_g.load_state_dict(net_g_static)
    net_g.eval()
    return net_g


def Audio2mouth(wavpath, Audio2FeatureModel,  method = "lstm"):
    waveform, sr = torchaudio.load(wavpath)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)

    fbank = torchaudio.compliance.kaldi.fbank(
        waveform,
        sample_frequency=16000,
        frame_length=50.0,
        frame_shift=20.0,
        num_mel_bins=80,
        dither=0.0,
        snip_edges=False,
    )
    seq_len = fbank.shape[0] // 2
    orig_mel = fbank[: 2 * seq_len, :].numpy()

    input = torch.from_numpy(orig_mel).unsqueeze(0).float().to(device)
    h0 = torch.zeros(2, 1, 192).to(device)
    c0 = torch.zeros(2, 1, 192).to(device)
    bs_array, hn, cn = Audio2FeatureModel(input, h0, c0)
    bs_array = bs_array[0].detach().cpu().float().numpy()
    bs_array = bs_array[4:]
    bs_array[:, :2] = bs_array[:, :2] / 8
    bs_array[:, 2] = - bs_array[:, 2] / 8

    return bs_array
def Audio2bs(wavpath, Audio2FeatureModel):
    # Read WAV with scipy (avoids torchcodec dependency)
    from scipy.io import wavfile

    sr, wav = wavfile.read(wavpath, mmap=False)
    if wav.ndim > 1:
        wav = wav.mean(axis=1)  # stereo → mono
    waveform = torch.from_numpy(wav.astype(np.float32) / 32768.0).unsqueeze(0)
    if sr != 8000:
        waveform = torchaudio.functional.resample(waveform, sr, 8000)

    # FBank features matching kaldi_native_fbank output
    fbank = torchaudio.compliance.kaldi.fbank(
        waveform,
        sample_frequency=8000,
        frame_length=50.0,
        frame_shift=20.0,
        num_mel_bins=80,
        dither=0.0,
        snip_edges=False,
    )
    seq_len = fbank.shape[0] // 2
    orig_mel = fbank[: 2 * seq_len, :].numpy()

    input_tensor = torch.from_numpy(orig_mel).unsqueeze(0).float().to(device)
    h0 = torch.zeros(2, 1, 192).to(device)
    c0 = torch.zeros(2, 1, 192).to(device)
    bs_array, hn, cn = Audio2FeatureModel(input_tensor, h0, c0)
    bs_array = bs_array[0].detach().cpu().float().numpy()
    return bs_array
