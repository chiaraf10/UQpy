import pytest
from beartype.roar import BeartypeCallHintPepParamException

from UQpy.utilities.MinimizeOptimizer import MinimizeOptimizer
from UQpy.sampling.stratified_sampling.refinement.GradientEnhancedRefinement import GradientEnhancedRefinement
from UQpy.distributions.collection.Uniform import Uniform
from UQpy.sampling.stratified_sampling.RefinedStratifiedSampling import *
from UQpy.sampling.stratified_sampling.refinement.RandomRefinement import *
from UQpy.sampling.stratified_sampling.strata.VoronoiStrata import *
from UQpy.run_model.RunModel import *
from UQpy.surrogates.kriging.Kriging import Kriging


def test_rss_simple_rectangular():
    marginals = [Uniform(loc=0., scale=1.), Uniform(loc=0., scale=1.)]
    strata = RectangularStrata(strata_number=[4, 4])
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata,
                               nsamples_per_stratum=1, random_state=1)
    algorithm = RandomRefinement(strata)
    y = RefinedStratifiedSampling(stratified_sampling=x,
                                  nsamples=18,
                                  samples_per_iteration=2,
                                  refinement_algorithm=algorithm,
                                  random_state=2)
    assert y.samples[16, 0] == 0.06614276178462988
    assert y.samples[16, 1] == 0.7836449863362334
    assert y.samples[17, 0] == 0.1891972651582183
    assert y.samples[17, 1] == 0.2961099664117288


def test_rss_simple_voronoi():
    marginals = [Uniform(loc=0., scale=1.), Uniform(loc=0., scale=1.)]
    strata = VoronoiStrata(seeds_number=16, dimension=2, random_state=1)
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata,
                               nsamples_per_stratum=1, random_state=1)
    algorithm = RandomRefinement(strata)
    y = RefinedStratifiedSampling(stratified_sampling=x,
                                  nsamples=18,
                                  samples_per_iteration=2,
                                  refinement_algorithm=algorithm,
                                  random_state=2)
    assert y.samples[16, 0] == 0.3637932367281488
    assert y.samples[16, 1] == 0.4676253860574614
    assert y.samples[17, 0] == 0.4245856389630922
    assert y.samples[17, 1] == 0.21730082648922827


def test_rect_rss():
    """
    Test the 6 samples generated by RSS using rectangular stratification
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata = RectangularStrata(strata_number=[2, 2], random_state=1)
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata, nsamples_per_stratum=1, )
    y = RefinedStratifiedSampling(stratified_sampling=x, nsamples=6, samples_per_iteration=2, random_state=2,
                                  refinement_algorithm=RandomRefinement(strata=strata))
    assert np.allclose(y.samples, np.array([[0.417022, 0.36016225], [1.00011437, 0.15116629],
                                            [0.14675589, 0.5461693], [1.18626021, 0.67278036],
                                            [0.77483124, 0.7176612], [1.7101839, 0.66516741]]))
    assert np.allclose(np.array(y.samplesU01), np.array([[0.208511, 0.36016225], [0.50005719, 0.15116629],
                                                         [0.07337795, 0.5461693], [0.59313011, 0.67278036],
                                                         [0.38741562, 0.7176612], [0.85509195, 0.66516741]]))


def test_rect_gerss():
    """
    Test the 6 samples generated by GE-RSS using rectangular stratification
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata = RectangularStrata(strata_number=[2, 2], random_state=1)
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata, nsamples_per_stratum=1)
    rmodel = RunModel(model_script='python_model_function.py', vec=False)
    from UQpy.surrogates.kriging.regression_models import LineaRegression
    from UQpy.surrogates.kriging.correlation_models import ExponentialCorrelation

    K = Kriging(regression_model=LineaRegression(), correlation_model=ExponentialCorrelation(), optimizations_number=20, random_state=0,
                correlation_model_parameters=[1, 1], optimizer=MinimizeOptimizer('l-bfgs-b'), )
    K.fit(samples=x.samples, values=rmodel.qoi_list)
    refinement = GradientEnhancedRefinement(strata=x.strata_object, runmodel_object=rmodel,
                                            surrogate=K, nearest_points_number=4)
    z = RefinedStratifiedSampling(stratified_sampling=x, random_state=2, refinement_algorithm=refinement)
    z.run(nsamples=6)
    assert np.allclose(z.samples, np.array([[0.417022, 0.36016225], [1.00011437, 0.15116629],
                                            [0.14675589, 0.5461693], [1.18626021, 0.67278036],
                                            [1.59254104, 0.96577043], [1.97386531, 0.24237455]]))
    # assert np.allclose(z.samples, np.array([[0.417022, 0.36016225], [1.00011437, 0.15116629],
    #                                         [0.14675589, 0.5461693], [1.18626021, 0.67278036],
    #                                         [1.59254104, 0.96577043], [1.7176612, 0.2101839]]))
    assert np.allclose(z.samplesU01, np.array([[0.208511, 0.36016225], [0.50005719, 0.15116629],
                                               [0.07337795, 0.5461693], [0.59313011, 0.67278036],
                                               [0.79627052, 0.96577043], [0.98693265, 0.24237455]]))
    # assert np.allclose(z.samplesU01, np.array([[0.208511, 0.36016225], [0.50005719, 0.15116629],
    #                                            [0.07337795, 0.5461693], [0.59313011, 0.67278036],
    #                                            [0.79627052, 0.96577043], [0.8588306 , 0.2101839]]))


def test_vor_rss():
    """
    Test the 6 samples generated by RSS using voronoi stratification
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata_vor = VoronoiStrata(seeds_number=4, dimension=2, random_state=10)
    x_vor = TrueStratifiedSampling(distributions=marginals, strata_object=strata_vor, nsamples_per_stratum=1, )
    y_vor = RefinedStratifiedSampling(stratified_sampling=x_vor, nsamples=6, samples_per_iteration=2,
                                      refinement_algorithm=RandomRefinement(strata=x_vor.strata_object))
    assert np.allclose(y_vor.samples, np.array([[1.78345908, 0.01640854], [1.46201137, 0.70862104],
                                                [0.4021338, 0.05290083], [0.1062376, 0.88958226],
                                                [0.61246269, 0.47160095], [0.85778034, 0.72123075]]))

    assert np.allclose(y_vor.samplesU01, np.array([[0.89172954, 0.01640854], [0.73100569, 0.70862104],
                                                   [0.2010669, 0.05290083], [0.0531188, 0.88958226],
                                                   [0.30623134, 0.47160095], [0.42889017, 0.72123075]]))


def test_vor_gerss():
    """
    Test the 6 samples generated by GE-RSS using voronoi stratification
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata_vor = VoronoiStrata(seeds_number=4, dimension=2, random_state=10)
    x_vor = TrueStratifiedSampling(distributions=marginals, strata_object=strata_vor, nsamples_per_stratum=1, )
    from UQpy.surrogates.kriging.regression_models.LinearRegression import LinearRegression
    from UQpy.surrogates.kriging.correlation_models.ExponentialCorrelation import ExponentialCorrelation
    rmodel_ = RunModel(model_script='python_model_function.py', vec=False)
    K_ = Kriging(regression_model=LinearRegression(), correlation_model=ExponentialCorrelation(), optimizations_number=20,
                 optimizer=MinimizeOptimizer('l-bfgs-b'), random_state=0,
                 correlation_model_parameters=[1, 1])

    K_.fit(samples=x_vor.samples, values=rmodel_.qoi_list)
    z_vor = RefinedStratifiedSampling(stratified_sampling=x_vor, nsamples=6, random_state=x_vor.random_state,
                                      refinement_algorithm=GradientEnhancedRefinement(strata=x_vor.strata_object,
                                                                                      runmodel_object=rmodel_,
                                                                                      surrogate=K_,
                                                                                      nearest_points_number=4))
    assert np.allclose(z_vor.samples, np.array([[1.78345908, 0.01640854], [1.46201137, 0.70862104],
                                                [0.4021338, 0.05290083], [0.1062376, 0.88958226],
                                                [0.61246269, 0.47160095], [1.16609055, 0.30832536]]))
    assert np.allclose(z_vor.samplesU01, np.array([[0.89172954, 0.01640854], [0.73100569, 0.70862104],
                                                   [0.2010669, 0.05290083], [0.0531188, 0.88958226],
                                                   [0.30623134, 0.47160095], [0.58304527, 0.30832536]]))


def test_rss_random_state():
    """
        Check 'random_state' is an integer or RandomState object.
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata = RectangularStrata(strata_number=[2, 2])
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata, nsamples_per_stratum=1, random_state=1)
    with pytest.raises(BeartypeCallHintPepParamException):
        RefinedStratifiedSampling(stratified_sampling=x, samples_number=6, samples_per_iteration=2, random_state='abc',
                                  refinement_algorithm=RandomRefinement(x.strata_object))


def test_rss_runmodel_object():
    """
        Check 'runmodel_object' should be a UQpy.RunModel class object.
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata = RectangularStrata(strata_number=[2, 2])
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata, nsamples_per_stratum=1, random_state=1)
    from UQpy.surrogates.kriging.regression_models import LineaRegression
    from UQpy.surrogates.kriging.correlation_models import ExponentialCorrelation

    K = Kriging(regression_model=LineaRegression(), correlation_model=ExponentialCorrelation(), optimizations_number=20,
                correlation_model_parameters=[1, 1], optimizer=MinimizeOptimizer('l-bfgs-b'), )
    rmodel = RunModel(model_script='python_model_function.py', vec=False)
    K.fit(samples=x.samples, values=rmodel.qoi_list)
    with pytest.raises(BeartypeCallHintPepParamException):
        refinement = GradientEnhancedRefinement(strata=x.strata_object, runmodel_object='abc',
                                                surrogate=K)
        RefinedStratifiedSampling(stratified_sampling=x, samples_number=6, samples_per_iteration=2,
                                  refinement_algorithm=refinement)


def test_rss_kriging_object():
    """
        Check 'kriging_object', it should have 'fit' and 'predict' methods.
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata = RectangularStrata(strata_number=[2, 2])
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata, nsamples_per_stratum=1, random_state=1)
    rmodel_ = RunModel(model_script='python_model_function.py', vec=False)
    with pytest.raises(NotImplementedError):
        refinement = GradientEnhancedRefinement(strata=x.strata_object, runmodel_object=rmodel_,
                                                surrogate="abc")
        RefinedStratifiedSampling(stratified_sampling=x, nsamples=6, samples_per_iteration=2,
                                  refinement_algorithm=refinement)


def test_nsamples():
    """
        Check 'nsamples' attributes, it should be an integer.
    """
    marginals = [Uniform(loc=0., scale=2.), Uniform(loc=0., scale=1.)]
    strata = RectangularStrata(strata_number=[2, 2])
    x = TrueStratifiedSampling(distributions=marginals, strata_object=strata, nsamples_per_stratum=1, random_state=1)
    with pytest.raises(BeartypeCallHintPepParamException):
        RefinedStratifiedSampling(stratified_sampling=x, nsamples='a', samples_per_iteration=2,
                                  refinement_algorithm=RandomRefinement(x.strata_object))
