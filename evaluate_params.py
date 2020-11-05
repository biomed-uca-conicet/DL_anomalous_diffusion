from Networks.classification_network import L1NetworkModel
from Networks.fbm_network import L2NetworkModel
from Networks.states_detection_network import StateDetectionNetworkModel
from Networks.hurst_exponent_network import HurstExponentNetworkModel
from Networks.diffusion_coefficient_network import DiffusionCoefficientNetworkModel
from Tools.db_connection import connect_to_db, disconnect_to_db
import matplotlib.pyplot as plt
import numpy as np
from keras import backend as K


def create_model(net_name):
    if net_name == 'L1Network':
        network = L1NetworkModel(track_length=track_length,
                                 track_time=track_time,
                                 hiperparams_opt=True)
    elif net_name == 'L2Network':
        network = L2NetworkModel(track_length=track_length,
                                 track_time=track_time,
                                 hiperparams_opt=True)
    elif net_name == 'StateDetectionNetwork':
        network = StateDetectionNetworkModel(track_length=track_length,
                                             track_time=track_time,
                                             hiperparams_opt=True)
    elif net_name == 'HurstExponentNetwork':
        network = HurstExponentNetworkModel(track_length=track_length,
                                            track_time=track_time,
                                            fbm_type=fbm_type_net,
                                            hiperparams_opt=True)
    else:
        network = DiffusionCoefficientNetworkModel(track_length=track_length,
                                                   track_time=track_time,
                                                   hiperparams_opt=True)

    return network


def scan_params(net_name):
    # Stack names and lists position
    if len(analysis_params) > 0:
        stack_names = [k for k, v in analysis_params.items()]
        stack = [0 for i in stack_names]
        tos = len(stack) - 1
        analysis_ended = False
        increasing = True

        # Compute and print number of combinations
        number_of_combinations = len(analysis_params[stack_names[0]])
        for i in range(1, len(stack_names)):
            number_of_combinations *= len(analysis_params[stack_names[i]])
        print("Total of combinations:{}".format(number_of_combinations))

        # Run the analysis
        while not analysis_ended:
            if tos == (len(stack) - 1) and stack[tos] < len(analysis_params[stack_names[tos]]):
                K.clear_session()
                network = create_model(net_name)
                for i in range(len(stack_names)):
                    network.net_params[stack_names[i]] = analysis_params[stack_names[i]][stack[i]]
                print('Evaluating params: {}'.format(network.net_params))

                network.train_network(batch_size=network.net_params['batch_size'])
                network.load_model_from_file()
                network.save_model_file_to_db()
                network.save()
                stack[tos] += 1
            elif tos == (len(stack) - 1) and stack[tos] == len(analysis_params[stack_names[tos]]):
                stack[tos] = 0
                tos -= 1
                increasing = False

            elif 0 < tos < (len(stack) - 1) and increasing:
                tos += 1
                increasing = True
            elif 0 < tos < (len(stack) - 1) and not increasing and stack[tos] + 1 <= len(
                    analysis_params[stack_names[tos]]) - 1:
                stack[tos] += 1
                tos += 1
                increasing = True
            elif 0 < tos < (len(stack) - 1) and not increasing and stack[tos] + 1 > len(
                    analysis_params[stack_names[tos]]) - 1:
                stack[tos] = 0
                tos -= 1
                increasing = False
            elif tos == 0 and not increasing and stack[tos] + 1 < len(analysis_params[stack_names[tos]]):
                stack[tos] += 1
                tos += 1
                increasing = True
            else:
                analysis_ended = True


def get_params(net_name):
    net_params = {
        'L1Network': L1NetworkModel.analysis_params,
        'L2Network': L2NetworkModel.analysis_params,
        'StateDetectionNetwork': StateDetectionNetworkModel.analysis_params,
        'HurstExponentNetwork': HurstExponentNetworkModel.analysis_params,
        'DiffusionCoefficientNetwork': DiffusionCoefficientNetworkModel.analysis_params
    }
    params = net_params[net_name]
    return params


def sort_results(e):
    return e[0]


def plot_analysis():
    networks = L1NetworkModel.objects(hiperparams_opt=True)
    results = [[np.mean(network.history['categorical_accuracy'][40:51]),
                np.std(network.history['categorical_accuracy'][40:51]),
                network.id]
               for network in networks]
    results.sort(key=sort_results, reverse=True)
    best_results = results[0:10]
    print("Training")
    for network in networks:
        epochs = [(i + 1) for i in range(len(network.history['categorical_accuracy']))]
        plt.plot(epochs, network.history['categorical_accuracy'])
        [print('{}, {} ,{}'.format(network.params_training, result[0], result[1])) for result in best_results if
         result[2] == network.id]

    plt.show()

    networks = L1NetworkModel.objects(hiperparams_opt=True)
    results = [[np.mean(network.history['val_categorical_accuracy'][40:51]),
                np.std(network.history['val_categorical_accuracy'][40:51]),
                network.id]
               for network in networks]
    results.sort(key=sort_results, reverse=True)
    best_results = results[0:10]
    print("Validation")
    for network in networks:
        epochs = [(i + 1) for i in range(len(network.history['val_categorical_accuracy']))]
        plt.plot(epochs, network.history['val_categorical_accuracy'])
        [print('{}, {} ,{}'.format(network.params_training, result[0], result[1])) for result in best_results if
         result[2] == network.id]
    plt.show()


if __name__ == '__main__':
    track_length = 50
    track_time = 1.0
    fbm_type_net = 'Subdiffusive'

    net = 'L1Network'

    connect_to_db()
    analysis_params = get_params(net)
    scan_params(net)
    plot_analysis()
    disconnect_to_db()
