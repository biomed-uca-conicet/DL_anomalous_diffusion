from mongoengine import Document, StringField, FileField
import pandas as pd
import numpy as np
from . import experimental_tracks
from . import tracks_dict_parser
import sys


class File(Document):
    experimental_condition = StringField(choices=experimental_tracks.EXPERIMENTAL_CONDITIONS, required=True)
    labeling_method = StringField(choices=experimental_tracks.LABELING_METHODS, required=True)
    raw_file = FileField(required=True)
    file_fps = 58.333

    def add_raw_file(self, filename):
        self.parse_filename(filename)
        with open(filename, 'rb') as fd:
            self.raw_file.put(fd)

    def parse_filename(self, filename):

        # Remove folders from filename
        only_file = filename.split('/')
        only_file = only_file[len(only_file) - 1]

        # Get the file extension for validation
        file_extension = only_file.split('.')
        only_file = ''.join(file_extension[:len(file_extension) - 1])
        file_extension = file_extension[len(file_extension) - 1]

        # Check file extension
        assert file_extension == 'csv', "File format is not CSV"

        only_file_split = only_file.split('_')
        exp_cond_detected = False
        label_method_detected = False

        for substr in only_file_split:
            if experimental_tracks.EXPERIMENTAL_CONDITIONS[0] in substr:
                self.experimental_condition = experimental_tracks.EXPERIMENTAL_CONDITIONS[0]
                exp_cond_detected = True
                break
            if experimental_tracks.EXPERIMENTAL_CONDITIONS[1] in substr:
                self.experimental_condition = experimental_tracks.EXPERIMENTAL_CONDITIONS[1]
                exp_cond_detected = True
                break
            if experimental_tracks.EXPERIMENTAL_CONDITIONS[2] in substr:
                self.experimental_condition = experimental_tracks.EXPERIMENTAL_CONDITIONS[2]
                exp_cond_detected = True
                break

        for substr in only_file_split:
            if experimental_tracks.LABELING_METHODS[0] in substr:
                self.labeling_method = experimental_tracks.LABELING_METHODS[0]
                label_method_detected = True
                break
            if experimental_tracks.LABELING_METHODS[1] in substr:
                self.labeling_method = experimental_tracks.LABELING_METHODS[1]
                label_method_detected = True
                break

        # Check for correct detection
        assert exp_cond_detected, "Experimental condition not defined"
        assert label_method_detected, "Labeling method not defined"

    def load_local_file(self, filename):
        data = pd.read_csv(filename)
        tracks_dict = tracks_dict_parser.create_tracks_dict(data)
        tracks_list = self.create_tracks_list(tracks_dict)
        return tracks_list

    def create_tracks_list(self, tracks_dict):
        tracks_list = []
        progress = 0
        for key, value in tracks_dict.items():
            progress += 1
            sys.stdout.write('\r')
            new_track = self.create_track_from_track_dict(key, tracks_dict)
            tracks_list.append(new_track)
            sys.stdout.write('Loading tracks: {:.0f}%'.format(100 * progress / len(tracks_dict.items())))
            sys.stdout.flush()
        sys.stdout.write('\n')
        return tracks_list

    def create_track_from_track_dict(self, key, tracks_dict):
        x = np.asarray(tracks_dict[key]["x"])
        y = np.asarray(tracks_dict[key]["y"])
        frames = tracks_dict[key]["frame"]
        track_length = len(frames)
        n_axes = 2
        axes_data = np.zeros(shape=(n_axes, track_length))
        axes_data[0] = x
        axes_data[1] = y
        min_t = min(frames) * (1 / self.file_fps)
        max_t = max(frames) * (1 / self.file_fps)
        track_time = max_t - min_t
        time_axis = np.arange(min_t, max_t, (max_t - min_t) / track_length)[:track_length]
        new_track = experimental_tracks.ExperimentalTracks(track_length=track_length,
                                                           track_time=track_time,
                                                           n_axes=n_axes,
                                                           labeling_method=self.labeling_method,
                                                           experimental_condition=self.experimental_condition)
        new_track.set_axes_data(axes_data)
        new_track.set_time_axis(time_axis)
        return new_track