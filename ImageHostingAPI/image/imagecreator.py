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
