import os
import numpy as np
import errno
import torchvision.utils as vutils
from tensorboardX import SummaryWriter
from IPython import display
from matplotlib import pyplot as plt
import torch

'''
    TensorBoard Data will be stored in './runs' path
'''


class Logger:

    def __init__(self, model_name, data_name):
        self.model_name = model_name
        self.data_name = data_name

        self.comment = '{}_{}'.format(model_name, data_name)
        self.data_subdir = '{}/{}'.format(model_name, data_name)

        # TensorBoard
        self.writer = SummaryWriter(comment=self.comment)

    def log(self, D_error, G_error, epoch, n_batch, num_batches):

        step = Logger._step(epoch, n_batch, num_batches)
        self.writer.add_scalar(
            '{}/D_error'.format(self.comment), D_error, step)
        self.writer.add_scalar(
            '{}/G_error'.format(self.comment), G_error, step)

    def log_images(self, images, num_images, epoch, n_batch, num_batches):
        '''
        input images are expected in format (NCHW)
        '''
        step = Logger._step(epoch, n_batch, num_batches)
        img_name = '{}/images{}'.format(self.comment, '')

        # Make grid from image tensor
        grid = vutils.make_grid(images, normalize=True, scale_each=True)
        # Add images to tensorboard
        self.writer.add_image(img_name, grid, step)
        # Display images in notebook
        fig = Logger._display_images(images.numpy())
        # Save plots
        self.save_images(fig, epoch, n_batch)
        # Close plots
        plt.close()

    def save_images(self, fig, epoch, n_batch):
        out_dir = './data/images/{}'.format(self.data_subdir)
        Logger._make_dir(out_dir)
        fig.savefig('{}/epoch_{}_batch_{}.png'.format(out_dir, epoch, n_batch))

    def display_status(self, epoch, num_epochs, n_batch, num_batches, d_error, g_error, d_pred_real, d_pred_fake):
        print('Epoch: [{}/{}], Batch Num: [{}/{}]'.format(epoch,
                                                          num_epochs, n_batch, num_batches))
        print('Discriminator Loss: {:.4f}, Generator Loss: {:.4f}'.format(
            d_error.data[0], g_error.data[0]))
        print('D(x): {:.4f}, D(G(z)): {:.4f}'.format(
            d_pred_real.data.mean(), d_pred_fake.data.mean()))

    def save_models(self, generator, discriminator, epoch):
        out_dir = './data/models/{}'.format(self.data_subdir)
        Logger._make_dir(out_dir)
        torch.save(generator.state_dict(),
                   '{}/G_epoch_{}'.format(out_dir, epoch))
        torch.save(discriminator.state_dict(),
                   '{}/D_epoch_{}'.format(out_dir, epoch))

    def close(self):
        self.writer.close()

    # Private Functionality

    @staticmethod
    def _step(epoch, n_batch, num_batches):
        return epoch * num_batches + n_batch

    @staticmethod
    def _process_images_for_display(images):
        '''
        input images are expected in format (NCHW)
        output images are formatted to (NHWC)
        '''
        # If image has more than 1 channel
        # Rescale values to range[-1,1]
        # channels = images.size()[1]
        # if (channels > 1):
        #     v_min = images.min(axis=(0, 2, 3), keepdims=True)
        #     v_max = v.max(axis=(0, 2, 3), keepdims=True)
        #     images = (images - v_min) / (v_max - v_min)

        # Reformat images as (NHWC)
        images = np.moveaxis(images, 1, -1)
        # Remove any single-dimensional entries
        images = np.squeeze(images)

        return images

    @staticmethod
    def _display_images(images):
        '''
        expects input images in format (NHWC)
        '''
        # Process images for display
        images = Logger._process_images_for_display(images)
        # Obtain num_images
        num_images = images.shape[0]

        # Create empty plot
        size_figure_grid = int(np.sqrt(num_images))
        fig, ax = plt.subplots(
            size_figure_grid, size_figure_grid, figsize=(8, 8)
        )

        # Display multiple images in plot
        for k in range(num_images):
            # Locate image position indexes (i:vertical, j:horizontal)
            i, j = k // 4, k % 4
            # Obtain current image
            img = images[k, :]
            # Remove axis lines
            ax[i, j].cla()
            ax[i, j].set_axis_off()

            if len(img.shape) == 3:
                ax[i, j].imshow(img)

            elif len(img.shape) == 2:
                ax[i, j].imshow(img, cmap='Greys')

        plt.axis('off')
        display.display(plt.gcf())

        return fig

    @staticmethod
    def _make_dir(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise