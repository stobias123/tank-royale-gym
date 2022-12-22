from torchvision import transforms
from ts.torch_handler.image_classifier import ImageClassifier
from ts.torch_handler.base_handler import BaseHandler
from torch.profiler import ProfilerActivity


class RobocodeClassifier(BaseHandler):
    """
    RobocdeClassifier handler class. This handler takes an image and
    returns the class of the object in the image.
    """

    def __init__(self):
        super(RobocodeClassifier, self).__init__()