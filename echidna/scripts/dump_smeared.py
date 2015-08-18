""" Example smearing script

This script:
  * Reads in mc spectra from hdf5
  * Smears spectra, default is to use weighted Gaussian method, but can
    also use specify random Gaussian method via command line
  * Smeared spectrum is saved to the same directory with ``_smeared``
    added to the file name

Examples:
  To smear hdf5 file ``example.hdf5`` using the random Gaussian method::

    $ python dump_smeared.py --smear_method "random" /path/to/example.hdf5

  This will create the smeared hdf5 file ``/path/to/example_smeared.hdf5``.

.. note:: Valid smear methods include:

  * "weight", default
  * "random"
  * "weight_parallel"
  * "random_parallel"
"""

import echidna.output.store as store
import echidna.core.smear as smear
import time

if __name__ == "__main__":
    startTime = time.time()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--smear_method", nargs='?', const="weight",
                        type=str, default="weight",
                        help="specify the smearing method to use")
    parser.add_argument("-r", "--energy_resolution", default=None, type=float,
                        help="specify energy resolution "
                        "e.g. 0.05 for 5 percent")
    parser.add_argument("path", type=str,
                        help="specify path to hdf5 file")
    args = parser.parse_args()

    directory = args.path[:args.path.rfind("/")+1]  # strip filename
    # strip directory and extension
    filename = args.path[args.path.rfind("/")+1:args.path.rfind(".")]

    if args.energy_resolution is not None:
        smearer = smear.EResSmear(args.energy_resolution)
    else:  # use light yield
        smearer = smear.Smear()
    spectrum = store.load(args.path)

    if args.smear_method == "weight":  # Use default smear method
        smeared_spectrum = smearer.weight_gaussian_energy_spectra(spectrum)
        smeared_spectrum = smearer.weight_gaussian_radius_spectra(smeared_spectrum)
    elif args.smear_method == "weight_parallel":  # Use default smear method
        smeared_spectrum = smearer.weight_gaussian_energy_spectra_parallel(spectrum,4)
        smeared_spectrum = smearer.weight_gaussian_radius_spectra_parallel(smeared_spectrum,4)
    elif args.smear_method == "random":
        smeared_spectrum = smearer.random_gaussian_energy_spectra(spectrum)
        smeared_spectrum = smearer.random_gaussian_radius_spectra(smeared_spectrum)
    
    elif args.smear_method == "random_parallel":
        smeared_spectrum = smearer.random_gaussian_energy_spectra_parallel(spectrum,4)
        smeared_spectrum = smearer.random_gaussian_radius_spectra_parallel(smeared_spectrum,4)
    else:  # Not a valid smear method
        parser.error(args.smear_method + " is not a valid smear method")

    filename = directory + filename + "_smeared" + ".hdf5"
    store.dump(filename, smeared_spectrum)
    runTime = time.time()-startTime
    print "Total Runtime was: ",runTime
