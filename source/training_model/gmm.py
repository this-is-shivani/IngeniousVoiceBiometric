from sklearn.mixture import GaussianMixture


def getVoicePrint(features):
    '''

    :param features:
    :return: User model (GMM)
    '''

    ################################################################
    # Step 5 : Train user model (GMM)#
    ################################################################

    # Train GMM
    gmm = GaussianMixture(n_components=3, covariance_type='full', n_init=1, init_params='random')
    gmm.fit(features)
    return gmm
