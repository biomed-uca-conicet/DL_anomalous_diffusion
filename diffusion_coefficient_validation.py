import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error
from physical_models.models_two_state_diffusion import TwoStateDiffusion
from tools.analysis_tools import mean_squared_displacement


def coefficient_validation(track_length, track_time, state_diff):
    mse_d = np.zeros(shape=100)
    d = np.zeros(shape=100)
    beta = np.zeros(shape=100)

    for i in range(100):
        phys_model = TwoStateDiffusion.create_random()
        if state_diff == 0:
            x_noisy, y_noisy, x, y, t = phys_model.simulate_track_only_state0(track_length=track_length,
                                                                              track_time=track_time)
            ground_truth = phys_model.get_d_state0()
        else:
            x_noisy, y_noisy, x, y, t = phys_model.simulate_track_only_state1(track_length=track_length,
                                                                              track_time=track_time)
            ground_truth = phys_model.get_d_state1()

        t_vec, msd, a = mean_squared_displacement(x_noisy, y_noisy, track_time)

        beta[i] = a[0]
        d[i] = a[1] / 1000000

        mse_d[i] = mean_squared_error([ground_truth], [d[i]])
    plt.title("D")
    plt.hist(d, bins=30)
    plt.show()
    plt.title("Beta")
    plt.hist(beta, bins=30)
    plt.show()
    return mse_d


if __name__ == '__main__':
    # Set this params
    tl = 15
    state = 0

    T = tl / 50
    mse = np.mean(coefficient_validation(tl, T, state))
    print('RMSE: {:.6}'.format(np.sqrt(mse)))

