import io

from PIL import Image


def create_image(MEDIA_ROOT, root, path, height):
    with Image.open((MEDIA_ROOT + '/' + path)) as im:
        w, h = im.size
        new_size = (int(w * (int(height) / h)), int(height))
        im.thumbnail(new_size)
        im.convert('RGB')
        if im.mode in ('RGBA', 'P'):
            rgb_im = im.convert('RGB')
            rgb_im.save(root)
        elif im.mode in ('RGB', 'JPEG'):
            im.save(root)
    return


def create_binary_image(MEDIA_ROOT, path):
    with Image.open((MEDIA_ROOT + '/' + path)) as im:
        with io.BytesIO() as buffer:
            im.convert('RGB').save(buffer, 'JPEG')
            im_binary = buffer.getvalue()
    return im_binary
