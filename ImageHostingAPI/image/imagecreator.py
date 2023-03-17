import io

import PIL


def create_image(MEDIA_ROOT, root, path, height):
    with PIL.Image.open((MEDIA_ROOT + '/' + path)) as im:
        w, h = im.size
        new_size = (int(w * (int(height) / h)), int(height))
        im.thumbnail(new_size)
        im.save(root)
    return


def create_binary_image(MEDIA_ROOT, path):
    with PIL.Image.open((MEDIA_ROOT + '/' + path)) as im:
        with io.BytesIO() as buffer:
            im.convert('RGB').save(buffer, 'JPEG')
            im_binary = buffer.getvalue()
    return im_binary
