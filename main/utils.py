from django.core.exceptions import ValidationError

def validate_image(image):
        file_size = image.file.size
        limit = 2
        if file_size > limit * 1024 *1024:
            raise ValidationError("Max size of file is %s MB" % limit)
