#!/usr/bin/env python
# encoding: utf-8
"""
SuperFlux with neural network based peak picking onset detection algorithm.

@author: Sebastian Böck <sebastian.boeck@jku.at>

"""

import argparse

from madmom.processors import IOProcessor, io_arguments
from madmom.features import ActivationsProcessor
from madmom.audio.signal import SignalProcessor, FramedSignalProcessor
from madmom.audio.spectrogram import (FilteredSpectrogramProcessor,
                                      LogarithmicSpectrogramProcessor,
                                      SpectrogramDifferenceProcessor,
                                      SuperFluxProcessor)
from madmom.features.onsets import (SpectralOnsetProcessor,
                                    NNPeakPickingProcessor)


def main():
    """SuperFluxNN"""

    # define parser
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description='''
    The software detects all onsets in an audio file with the SuperFlux
    algorithm with neural network based peak-picking as described in:

    "Enhanced peak picking for onset detection with recurrent neural networks"
    Sebastian Böck, Jan Schlüter and Gerhard Widmer
    Proceedings of the 6th International Workshop on Machine Learning and
    Music (MML), 2013.

    Please note that this implementation uses 100 frames per second (instead
    of 200), because it is faster and produces highly comparable results.

    ''')
    # add arguments
    io_arguments(p, suffix='.onsets.txt')
    ActivationsProcessor.add_arguments(p)
    SignalProcessor.add_arguments(p, norm=False, att=0)
    FramedSignalProcessor.add_arguments(p, fps=200, online=False)
    FilteredSpectrogramProcessor.add_arguments(p, num_bands=24, fmin=30,
                                               fmax=17000, norm_filters=False)
    LogarithmicSpectrogramProcessor.add_arguments(p, log=True, mul=1, add=1)
    SpectrogramDifferenceProcessor.add_arguments(p, diff_ratio=0.5,
                                                 diff_max_bins=3,
                                                 positive_diffs=True)
    NNPeakPickingProcessor.add_arguments(p)
    # version
    p.add_argument('--version', action='version', version='SuperFluxNN')
    # parse arguments
    args = p.parse_args()
    # print arguments
    if args.verbose:
        print args

    # input processor
    if args.load:
        # load the activations from file
        in_processor = ActivationsProcessor(mode='r', **vars(args))
    else:
        # define processing chain
        sig = SignalProcessor(num_channels=1, **vars(args))
        frames = FramedSignalProcessor(**vars(args))
        spec = SuperFluxProcessor(**vars(args))
        odf = SpectralOnsetProcessor(onset_method='superflux', **vars(args))
        in_processor = [sig, frames, spec, odf]

    # output processor
    if args.save:
        # save the Onset activations to file
        out_processor = ActivationsProcessor(mode='w', **vars(args))
    else:
        # perform peak picking of the onset function with a RNN
        peak_picking = NNPeakPickingProcessor(**vars(args))
        from madmom.utils import write_events as writer
        # sequentially process them
        out_processor = [peak_picking, writer]

    # create an IOProcessor
    processor = IOProcessor(in_processor, out_processor)

    # and call the processing function
    args.func(processor, **vars(args))


if __name__ == '__main__':
    main()
