import numpy

import echidna.limit.chi_squared as chi_squared

import unittest


class TestChiSquared(unittest.TestCase):

    def test_pearson_chi_squared(self):
        """ Test the pearson chi squared function

        Tests that the function calculates accurate values
        """
        array1 = numpy.array([100.0])
        array2 = numpy.array([110.0])
        self.assertEqual(chi_squared.pearson_chi_squared(array1, array2),
                         (10.0 / 11.0))
        array1 = numpy.array([100.0])
        array2 = numpy.array([90.0])
        self.assertEqual(chi_squared.pearson_chi_squared(array1, array2),
                         (10.0 / 9.0))
        array1 = numpy.array([100.0])
        array2 = numpy.array([100.0])
        self.assertEqual(chi_squared.pearson_chi_squared(array1, array2), 0.0)
        array1 = numpy.array([1])
        array2 = numpy.array([1, 2])
        self.assertRaises(ValueError, chi_squared.pearson_chi_squared,
                          array1, array2)

    def test_neyman_chi_squared(self):
        """ Test the neyman chi squared function

        Tests that the function calculates accurate values
        """
        array1 = numpy.array([100.0])
        array2 = numpy.array([110.0])
        self.assertEqual(chi_squared.neyman_chi_squared(array1, array2), 1.0)
        array1 = numpy.array([100.0])
        array2 = numpy.array([90.0])
        self.assertEqual(chi_squared.neyman_chi_squared(array1, array2), 1.0)
        array1 = numpy.array([100.0])
        array2 = numpy.array([100.0])
        self.assertEqual(chi_squared.neyman_chi_squared(array1, array2), 0.0)
        array1 = numpy.array([1])
        array2 = numpy.array([1, 2])
        self.assertRaises(ValueError, chi_squared.neyman_chi_squared,
                          array1, array2)

    def test_log_likelihood(self):
        """ Test the log likelihood function

        Tests that the function calculates accurate values
        """
        array1 = numpy.array([100.0])
        array2 = numpy.array([110.0])
        log_likelihood = chi_squared.log_likelihood(array1, array2)
            # Just total, not ll per bin
        self.assertAlmostEqual(2.0 * log_likelihood, 0.9379640391350215)
        array1 = numpy.array([100.0])
        array2 = numpy.array([90.0])
        log_likelihood = chi_squared.log_likelihood(array1, array2)
            # Just total, not ll per bin
        self.assertAlmostEqual(2.0 * log_likelihood, 1.072103131565271)
        array1 = numpy.array([100.0])
        array2 = numpy.array([100.0])
        self.assertEqual(chi_squared.log_likelihood(array1, array2), 0.0)
        array1 = numpy.array([1])
        array2 = numpy.array([1, 2])
        self.assertRaises(ValueError, chi_squared.log_likelihood,
                          array1, array2)

    def test_get_chi_squared(self):
        """ Tests get chi squared method

        Tests functionality of the ChiSquared class and its principal
        method in different use case scenarios
        """
        # create mock data spectrum
        n_bins = 10
        energy_low = 0.0
        energy_high = 10.0
        data_spectrum = numpy.ndarray(shape=(n_bins), dtype=float)
        data_spectrum.fill(0)

        # fill mock data spectrum from random gaussian
        entries = 1000
        numpy.random.seed()
        mu = 5.0
        sigma = 1.5
        for energy in numpy.random.normal(mu, sigma, entries):
            if (energy >= energy_low) and (energy < energy_high):
                energy_bin = int((energy-energy_low) /
                                 (energy_high-energy_low) * n_bins)
                data_spectrum[energy_bin] += 1

        # create mock MC spectrum
        mc_spectrum = data_spectrum * 1.1

        # set-up chi squared calculators
        pearson_calculator = chi_squared.ChiSquared("pearson")
        neyman_calculator = chi_squared.ChiSquared("neyman")
        likelihood_calculator = chi_squared.ChiSquared("poisson_likelihood")
        penalty_calculator = chi_squared.ChiSquared(
            "poisson_likelihood",
            penalty_terms={
                "bkg1": {
                    "parameter_value": 0.5,
                    "sigma": 1.0
                    }
                })

        pearson_chi_squared = pearson_calculator.get_chi_squared(data_spectrum,
                                                                 mc_spectrum)
        neyman_chi_squared = neyman_calculator.get_chi_squared(data_spectrum,
                                                               mc_spectrum)
        likelihood_chi_squared = likelihood_calculator.get_chi_squared(
            data_spectrum,
            mc_spectrum)

        self.assertNotEqual(pearson_chi_squared, neyman_chi_squared)
        self.assertNotEqual(neyman_chi_squared, likelihood_chi_squared)
        self.assertNotEqual(likelihood_chi_squared, pearson_chi_squared)

        penalty_chi_squared = penalty_calculator.get_chi_squared(data_spectrum,
                                                                 mc_spectrum)
        self.assertNotEqual(likelihood_chi_squared, penalty_chi_squared)
        self.assertNotEqual(
            penalty_chi_squared,
            penalty_calculator.get_chi_squared(
                data_spectrum,
                mc_spectrum,
                penalty_terms={
                    "bkg1": {
                        "parameter_value": 1.0
                        }
                    }))
        self.assertEqual(
            likelihood_chi_squared,
            penalty_calculator.get_chi_squared(
                data_spectrum,
                mc_spectrum,
                penalty_terms={
                    "bkg1": {
                        "parameter_value": 0.0,
                        "sigma": 0.5
                        }
                    }))
        self.assertEqual(
            penalty_chi_squared,
            likelihood_calculator.get_chi_squared(
                data_spectrum,
                mc_spectrum,
                penalty_terms={
                    "bkg1": {
                        "parameter_value": 0.5,
                        "sigma": 1.0
                        }
                    }))
