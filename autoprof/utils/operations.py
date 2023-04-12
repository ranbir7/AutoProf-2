import torch
import matplotlib.pyplot as plt
import numpy as np
from astropy.convolution import convolve, convolve_fft
from scipy.fft import next_fast_len

def fft_convolve_torch(img, psf, psf_fft=False, img_prepadded=False):
    # Ensure everything is tensor
    img = torch.as_tensor(img)
    psf = torch.as_tensor(psf)

    if img_prepadded:
        s = img.size()
    else:
        s = tuple(next_fast_len(int(d+(p+1)/2), real = True) for d,p in zip(img.size(), psf.size())) #list(int(d + (p + 1) / 2) for d, p in zip(img.size(), psf.size()))

    img_f = torch.fft.rfft2(img, s=s)

    if not psf_fft:
        psf_f = torch.fft.rfft2(psf, s=s)
    else:
        psf_f = psf

    conv_f = img_f * psf_f
    conv = torch.fft.irfft2(conv_f, s=s)

    # Roll the tensor to correct centering and crop to original image size
    return torch.roll(
        conv,
        shifts=(-int((psf.size()[0] - 1) / 2), -int((psf.size()[1] - 1) / 2)),
        dims=(0, 1),
    )[: img.size()[0], : img.size()[1]]


def fft_convolve_multi_torch(
    img, kernels, kernel_fft=False, img_prepadded=False, dtype=None, device=None
):
    # Ensure everything is tensor
    img = torch.as_tensor(img, dtype=dtype, device=device)
    for k in range(len(kernels)):
        kernels[k] = torch.as_tensor(kernels[k], dtype=dtype, device=device)

    if img_prepadded:
        s = img.size()
    else:
        s = list(int(d + (p + 1) / 2) for d, p in zip(img.size(), kernels[0].size()))

    img_f = torch.fft.rfft2(img, s=s)

    if not kernel_fft:
        kernels_f = list(torch.fft.rfft2(kernel, s=s) for kernel in kernels)
    else:
        psf_f = psf

    conv_f = img_f

    for kernel_f in kernels_f:
        conv_f *= kernel_f

    conv = torch.fft.irfft2(conv_f, s=s)

    # Roll the tensor to correct centering and crop to original image size
    return torch.roll(
        conv,
        shifts=(
            -int((sum(kernel.size()[0] for kernel in kernels) - 1) / 2),
            -int((sum(kernel.size()[1] for kernel in kernels) - 1) / 2),
        ),
        dims=(0, 1),
    )[: img.size()[0], : img.size()[1]]

def displacement_spacing(N, dtype = torch.float64, device = "cpu"):
    return torch.linspace(-(N - 1)/(2*N), (N - 1)/(2*N), N, dtype = dtype, device = device)
    
def displacement_grid(*N, pixelscale = 1., dtype = torch.float64, device = "cpu"):
    return torch.meshgrid(*tuple(displacement_spacing(n, dtype = dtype, device = device)*pixelscale for n in N), indexing = "xy")
    
