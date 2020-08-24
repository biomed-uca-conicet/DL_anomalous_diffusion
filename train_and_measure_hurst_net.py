from networks.hurst_exp_network_model import HurstExponentNetworkModel
from tracks.experimental_tracks import ExperimentalTracks

from tools.db_connection import connect_to_db, disconnect_to_db
import matplotlib.pyplot as plt
from keras import backend as K


def train_net(track):
    K.clear_session()
    model_hurst_net = HurstExponentNetworkModel(track_length=track.track_length,
                                                track_time=track.track_time,
                                                fbm_type=track.l2_classified_as)
    model_hurst_net.train_network(batch_size=64)
    model_hurst_net.save()


def train(range_track_length):
    tracks = ExperimentalTracks.objects(track_length__in=range_track_length,
                                        l1_classified_as='fBm',
                                        l2_classified_as__in=["Subdiffusive", "Superdiffusive"])
    for track in tracks:
        networks = HurstExponentNetworkModel.objects(track_length=track.track_length,
                                                     fbm_type=track.l2_classified_as)
        net_available = False
        for net in networks:
            if net.is_valid_network_track_time(track.track_time):
                net_available = True

        if not net_available:
            print("Training network for track_length:{}, fbm type{} and track_time:{}".format(track.track_length,
                                                                                              track.l2_classified_as,
                                                                                              track.track_time))
            train_net(track)


def classify(range_track_length):
    print('Classifying tracks')
    networks = HurstExponentNetworkModel.objects(track_length__in=range_track_length)
    tracks = ExperimentalTracks.objects(track_length__in=range_track_length, l1_classified_as='fBm')
    for net in networks:
        net.load_model_from_file()
        for track in tracks.filter(l2_classified_as=net.fbm_type):
            if net.is_valid_network_track_time(track.track_time) and track.track_length == net.track_length:
                output = net.evaluate_track_input(track)
                track.set_hurst_exponent(output)
    for track in tracks:
        track.save()


if __name__ == '__main__':
    track_length_range = list(range(20, 21))
    label = 'mAb'
    exp_cond = 'CDx'

    connect_to_db()
    # Train, classify and show results
    train(range_track_length=track_length_range)
    classify(range_track_length=track_length_range)

    disconnect_to_db()