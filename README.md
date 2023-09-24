# 16fatten
An audio tool that specializes in "fattening" wave files!

## What?
It's an effect that I devised in my head one day, and after a minute of thought, decided to turn into a fully-fledged tool. The basic concept of "fattening" is that you have 3 different versions of the same audio file: the original, a low-passed version, and a high-passed version (achieved by inverting the low-passed version into the original). These versions are then combined together to create the resulting file.

The idea was to boost the low and high frequencies, while reducing the mids. However, this program offers lots of options that allow you to "shape" the sound in unintentional ways, creating all sorts of dips and peaks, which can result in some pretty interesting effects!

## But how does EH work?
It supports a variety of options:

* **Passes** (-p/--passes) - How many times to filter the file. Because the low-pass filter is a simple one that finds the difference between the current and previous bytes, more passes will make the filter steeper. This will also affect the high-pass, which means that more passes will create a bigger dip in frequencies.
* **Lowpass fraction** (-l/--lowpass) - The fraction of passes for the low-pass filter. For example, if this is set to 4, the amount of passes for the low-pass filter will be divided by 4, leaving the high-pass unaffected. This will adjust the different slopes for each filter.
* **Distortion** (-d/--distort) - If the file is a bit quiet, or you just want to crunch it up, you can apply cubic distortion with varying intensity. Cubic distortion is unlike normal clipping, in that it rounds out the waveform instead of just clipping it.
* **Wave formats** - It supports 8-bit unsigned and 16-bit signed wave files, both mono and stereo!