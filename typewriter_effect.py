import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

settings = {
    'font': './fonts/Darling.ttf', # https://www.dafont.com/darling.font
    'fontsize': 80,
    'video_fps': 30,
    'video_duration': 10,
    'video_width': 1080,
    'video_height': 1920,
    'text_fade_duration': 9,
    'text_color': (127, 127, 127, 127),
    'background_color': (200, 200, 200),
    'background_color_mode': 'RGB',
    'text_color': (170, 20, 57, 200), # Nice purple color
    'fade_background_color_mode': 'RGB',
    'fade_background_color': (200, 200, 200),
    'output_filename': 'typewriter_animation.mp4',
    'text_xy': (10, 500),
}
class ImageText(object):
    def __init__(self, filename_or_size, mode='RGBA', background=(0, 0, 0, 0),
                 encoding='utf8'):
        if isinstance(filename_or_size, str):
            self.filename = filename_or_size
            self.image = Image.open(self.filename, color=background)
            self.size = self.image.size
        elif isinstance(filename_or_size, (list, tuple)):
            self.size = filename_or_size
            self.image = Image.new(mode, self.size, color=background)
            self.filename = None
        self.draw = ImageDraw.Draw(self.image)
        self.encoding = encoding

    def save(self, filename=None):
        self.image.save(filename or self.filename)

    def get_font_size(self, text, font, max_width=None, max_height=None):
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        font_size = 1
        text_size = self.get_text_size(font, font_size, text)
        if (max_width is not None and text_size[0] > max_width) or \
           (max_height is not None and text_size[1] > max_height):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" % \
                    text_size)
        while True:
            if (max_width is not None and text_size[0] >= max_width) or \
               (max_height is not None and text_size[1] >= max_height):
                return font_size - 1
            font_size += 1
            text_size = self.get_text_size(font, font_size, text)

    def write_text(self, xy, text, font_filename, font_size=11,
                   color=(0, 0, 0), max_width=None, max_height=None):
        x, y = xy
        if font_size == 'fill' and \
           (max_width is not None or max_height is not None):
            font_size = self.get_font_size(text, font_filename, max_width,
                                           max_height)
        text_size = self.get_text_size(font_filename, font_size, text)
        font = ImageFont.truetype(font_filename, font_size)
        if x == 'center':
            x = (self.size[0] - text_size[0]) / 2
        if y == 'center':
            y = (self.size[1] - text_size[1]) / 2
        self.draw.text((x, y), text, font=font, fill=color)
        return text_size

    def get_text_size(self, font_filename, font_size, text):
        font = ImageFont.truetype(font_filename, font_size)
        (left, top, right, bottom) = font.getbbox(text)
        return [abs(right - left), abs(top - bottom) + 8]   # return [length, height] of the text, add some offset for height

    def write_text_box(self, xy, text, box_width, font_filename,
                       font_size=11, color=(0, 0, 0), place='left',
                       justify_last_line=False):
        x, y = xy
        lines = []
        line = []
        init_lines = text.split('\n')   # initial lines in the text
        text_height = 0
        for line_text in init_lines:
            words_in_line = line_text.split()
            if words_in_line == []:     # empty line
                lines.append([' '])
                continue
            for idx, word in enumerate(words_in_line):
                new_line = ' '.join(line + [word])
                size = self.get_text_size(font_filename, font_size, new_line)
                text_height = size[1]
                if size[0] <= box_width:
                    line.append(word)
                else:
                    lines.append(line)
                    line = [word]
                if idx == len(words_in_line) - 1:
                    lines.append(line)
            line = []

        if line:
            lines.append(line)
        lines = [' '.join(line) for line in lines if line]
        height = y
        for index, line in enumerate(lines):
            height += text_height
            if place == 'left':
                self.write_text((x, height), line, font_filename, font_size,
                                color)
            elif place == 'right':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = x + box_width - total_size[0]
                self.write_text((x_left, height), line, font_filename,
                                font_size, color)
            elif place == 'center':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = int(x + ((box_width - total_size[0]) / 2))
                self.write_text((x_left, height), line, font_filename,
                                font_size, color)
            elif place == 'justify':
                words = line.split()
                if (index == len(lines) - 1 and not justify_last_line) or \
                   len(words) == 1:
                    self.write_text((x, height), line, font_filename, font_size,
                                    color)
                    continue
                line_without_spaces = ''.join(words)
                total_size = self.get_text_size(font_filename, font_size,
                                                line_without_spaces)
                space_width = (box_width - total_size[0]) / (len(words) - 1.0)
                start_x = x
                for word in words[:-1]:
                    self.write_text((start_x, height), word, font_filename,
                                    font_size, color)
                    word_size = self.get_text_size(font_filename, font_size,
                                                    word)
                    start_x += word_size[0] + space_width
                last_word_size = self.get_text_size(font_filename, font_size,
                                                    words[-1])
                last_word_x = x + box_width - last_word_size[0]
                self.write_text((last_word_x, height), words[-1], font_filename,
                                font_size, color)
        return (box_width, height - y)

def create_video_with_typewriter_effect(text, output_filename, fontsize=30, video_fps=30, video_duration=10):
    font_filename = settings.get('font')
    font = ImageFont.truetype(font_filename, fontsize)
 
    # dimensions of video
    video_width = settings.get('video_width', 1080)
    video_height = settings.get('video_height', 1920)
    video_size = (video_width, video_height)
 
    video = cv2.VideoWriter(output_filename, 
                            cv2.VideoWriter_fourcc(*'mp4v'), 
                            video_fps, 
                            video_size)
 
    text_xy = settings.get('text_xy', (10, 10))
    # Video settings
    text_fade_duration = settings.get('text_fade_duration')  # seconds
    text_typing_duration = video_duration - text_fade_duration
 
    # Calculate the number of frames for the typewriter effect
    num_typing_frames = int(text_typing_duration * video_fps)
    num_fade_frames = int(text_fade_duration * video_fps)
    
    text_color = settings.get('text_color', (255, 255, 255, 255))
    background_color = settings.get('background_color', (0, 0, 0))
    # Typing effect
    for frame_idx in range(num_typing_frames):
        frame_image_text = ImageText(video_size, mode='RGB', background=background_color)
        current_text = text[:int(len(text) * frame_idx / num_typing_frames)]
        frame_image_text.write_text_box(text_xy, current_text, video_width - 20, font_filename, fontsize, text_color, place='center')
 
        video.write(np.array(frame_image_text.image))
 
    # Fade out effect
    for frame_idx in range(num_fade_frames):
 
        alpha = 255 - int(255 * frame_idx / num_fade_frames)
        text_color_with_alpha = text_color[:3] + (alpha,)
        frame_image_text = ImageText(video_size, mode='RGB', background=background_color)
        frame_image_text.write_text_box(text_xy, text, video_width - 20, font_filename, fontsize, text_color_with_alpha, place='center')
 
        video.write(np.array(frame_image_text.image))
 
    video.release()

text = "Hello \n\n World!"
output_filename = "typewriter_animation.mp4"
create_video_with_typewriter_effect(text, output_filename, fontsize=settings.get('fontsize', 30), video_fps=settings.get('video_fps', 30), video_duration=settings.get('video_duration', 10))