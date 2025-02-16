# Image Processing Tools
### 1. Image_Adjustment_by_Multiplier.py
  this script, makes sure all images have 2.5 times the hieght than width for example to have (720*1800) ---> 1800 = 720 * 2.5
  it crops and adds from the next image in the folder to the image that is being processed to get the desired height

> [!NOTE]
> there is a tolerance variable here for width, meaning, if the width is 720px in the current image but the next image is 721px, it overlook it and still vertically merge them

> [!NOTE]
> if the width of the images are significantly different then the merging doesn't happen, instead the image gets ignored UNLESS the next image after that has the same width, the the merging with the new width starts







WHY?
to make them readable, there are so many Comic books, Manga, Manhwa,... that are not cropped correctly when you download them <br>
Apps like HakuNeko, download them in a really bad format

below is an example, of what will happen to the images, (left) the original images, (right) after running the script and getting the output <br>
as you can see, i dropped a big image (2000*2000) in there to make you see what will happen to unfit images, as you can see, it skips it (the reason for adding this, is because of Ads that are thrown in these Mangas), we don't want them getting merged with the work


<table>
  <tr>
    <td><img src="Docs/Images/Original.png" alt="Original Image" width="500" /></td>
    <td><img src="Docs/Images/Output.png" alt="Output Image" width="500" /></td>
  </tr>
</table>
