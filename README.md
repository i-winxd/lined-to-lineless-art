# Lined to Lineless art

Title is self-explanatory.

- You need Python 3.9 or later installed. Really, you should have the latest version installed.
- You need `Pillow` installed: `python -m pip install pillow`. Things could get messy if you have more than one version of python installed. I discourage getting Python from the Windows 10 store.

If you haven't run a Python program before, look up a basic hello world tutorial.

## Inputs

Running `main.py` will open a UI that prompts you to select two files:

- A stroke PNG file. Your drawing with only the stroke layer visible. Everything else should be transparent.
- A color PNG file. Your drawing with only the color layer visible; no background. Everything else should be transparent.

When clicking the run button, the program will be unresponsive until it finishes. Depending on the size of your image file, the program will take a while to run. Medium-sized (1000x1000) files take a minute or two; large files (3000x3000) should take less than 30 minutes. Don't force close it.

## Outputs

- `exportFC_#.png`: Your "final" line-less art
  - Modify the source code if you want to change the background color.
- `exportST_#.png`: Your stroke layer with the colors overlaid on it

## What this does

For each transparent pixel on the color image, if the stroke image isn't transparent there, then our target pixel on the color image will take the color of the nearest non-transparent pixel on the image.

## Sample inputs

Note that I use Clip Studio Paint's vector layers, so the paint bucket treats each stroke as being 1px wide. This means that the transparent artifacts are very small. *Do NOT worry about this*, all that is required is that your stroke layer mask all white parts completely. You may need to expand the fill region (either native to the paint bucket settings, or use the Magic wand -> expand selection).

![sONLY](https://github.com/i-winxd/lined-to-lineless-art/assets/31808925/8b97625e-afb3-44a8-90a1-969204bbb406)

![cONLY](https://github.com/i-winxd/lined-to-lineless-art/assets/31808925/bdac0474-4364-4071-90b0-e162d221ecd0)
