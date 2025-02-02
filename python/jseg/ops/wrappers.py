import warnings
from jittor import nn
from jittor import Function


# TODO Save memory
class Resize(Function):
    def execute(self, input, size, scale_factor, mode, align_corners):
        self.input_size = input.shape[2:]
        self.scale_factor = scale_factor
        self.mode = mode
        self.align_corners = align_corners
        return nn.interpolate(input, size, scale_factor, mode, align_corners)

    def grad(self, grad_output):
        return nn.interpolate(grad_output, self.input_size, self.scale_factor, self.mode, self.align_corners)


interpolate = Resize.apply


def resize(input,
           size=None,
           scale_factor=None,
           mode='nearest',
           align_corners=None,
           warning=True):
    if warning:
        if size is not None and align_corners:
            input_h, input_w = tuple(int(x) for x in input.shape[2:])
            output_h, output_w = tuple(int(x) for x in size)
            if output_h > input_h or output_w > output_h:
                if ((output_h > 1 and output_w > 1 and input_h > 1
                     and input_w > 1) and (output_h - 1) % (input_h - 1)
                        and (output_w - 1) % (input_w - 1)):
                    warnings.warn(
                        f'When align_corners={align_corners}, '
                        'the output would more aligned if '
                        f'input size {(input_h, input_w)} is `x+1` and '
                        f'out size {(output_h, output_w)} is `nx+1`')

    size = tuple(int(x) for x in size)
    return interpolate(input, size, scale_factor, mode, align_corners)


class Upsample(nn.Module):
    def __init__(self,
                 size=None,
                 scale_factor=None,
                 mode='nearest',
                 align_corners=None):
        super(Upsample, self).__init__()
        self.size = size
        if isinstance(scale_factor, tuple):
            self.scale_factor = tuple(float(factor) for factor in scale_factor)
        else:
            self.scale_factor = float(scale_factor) if scale_factor else None
        self.mode = mode
        self.align_corners = align_corners

    def execute(self, x):
        if not self.size:
            size = [int(t * self.scale_factor) for t in x.shape[-2:]]
        else:
            size = self.size
        return resize(x, size, None, self.mode, self.align_corners)
