#!/usr/bin/python
"""This program takes an input file with a number of parameters required to
calculate the beam rate on the collection point"""

import sys
import math
import types

# first we check the command line and grab the module name
if len(sys.argv) != 2:
    print "\nUsage:\n\t./mda.py configuration_file\n\t  or"
    print "\tpython mda.py configuration_file\n"
    sys.exit()
# strip off the .py if it exists
CF_FILE_NAME = None
if sys.argv[1][-3:] == ".py":
    CF_FILE_NAME = sys.argv[1][0:-3]
else:
    CF_FILE_NAME = sys.argv[1]
# prevent bytecode generation for the config file
ORIGINAL_SYS_DONT_WRITE_BYTECODE = sys.dont_write_bytecode
sys.dont_write_bytecode = True
# import the config file
INPUT = __import__(CF_FILE_NAME).INPUT
# restore the dont_write_bytecode variable to its original value
sys.dont_write_bytecode = ORIGINAL_SYS_DONT_WRITE_BYTECODE


def main():
    """check the input file for sane values then do work"""
    # fatal sanity checks
    test_list_types()
    test_scalar_types()
    test_list_lengths()
    # add the input entry of effective collection time
    INPUT["Effective Collection Time"] = INPUT["Collection Time"] -\
        INPUT["Voltage Rampdown Time"]
    # non-fatal sanity checks:
    test_value_sanity()
    # now call the function that does stuff
    calculate_beam_rates()


def calculate_beam_rates():
    """This function takes the information in the input file and calculates
    the resulting beam rates from that information"""
    # construct the efficiency object
    eff_obj = HPGeEfficiency(INPUT["HPGe Efficiency Function"])
    # calculate the effeciencies
    eff_set = [eff_obj.calculate_frac_eff(energy) for energy in
               INPUT["Gamma Energies"]]
    # calculate the total number of decays
    total_decays = [area/(inten*eff) for (area, inten, eff) in
                    zip(INPUT["Gamma Areas"], INPUT["Gamma Branchings"],
                        eff_set)]
    # now calculate the number of collection periods
    num_collections = calc_collections()
    # calculate the number of decays per cycle
    decays_per_cycle = [decays / num_collections for decays in total_decays]
    # calculate the decay constant
    dec_const = math.log(2)/INPUT["Half Life"]
    # calculate the activity integral
    act_int = act_integral(dec_const, INPUT["Effective Collection Time"])
    # calculate the beam rates
    beam_rates = [decays / act_int for decays in decays_per_cycle]
    # output everything for the users
    print HEADER_STRING.format(INPUT["Title Name"])
    for info in zip(INPUT["Gamma Energies"], INPUT["Gamma Branchings"], eff_set,
                    total_decays, decays_per_cycle, beam_rates):
        print ROW_STRING.format(*info)
    print FOOTER_STRING


def act_integral(dec_const, time):
    """calculate the integral of the time dependant portion of the activity"""
    temp = math.exp(-dec_const*time)
    temp -= 1.0
    temp /= dec_const
    return temp + time


def calc_collections():
    """Calculate the number of cycles in a sane way"""
    # calc the number of full cycles (each of which had a full collection)
    full_cycle_count = math.floor(INPUT["HPGe Integration Time"] /
                                  INPUT["Cycle Length"])
    # calculate the unaccounted for time
    extra_collection = INPUT["HPGe Integration Time"] - (full_cycle_count *
                                                         INPUT["Cycle Length"])
    # if the unaccounted for time exceeded an effectiove collection time,
    # return the full_cycle_count + 1
    if extra_collection > INPUT["Collection Time"]:
        return full_cycle_count + 1
    else:  # otherwise return the appropriate fraction
        return (full_cycle_count + ((extra_collection -
                                     INPUT["Voltage Rampdown Time"]) /
                                    INPUT["Collection Time"]))


class HPGeEfficiency(object):
    """Object to hold efficiency function information and calculate the gamma
    efficiencies given an energy"""
    def __init__(self, param_list):
        # store the parameters
        self.par = [0.0]*8
        self.par[0] = param_list[0]
        self.par[1] = param_list[1]
        self.par[2] = param_list[2]
        self.par[3] = param_list[3]
        self.par[5] = param_list[4]
        self.par[7] = param_list[5]

    def calculate_frac_eff(self, energy):
        """Returns the efficiency as a fraction"""
        logx = math.log(energy)
        # calculate logx to various powers
        exp_vals = [math.pow(logx, float(i)) for i in range(8)]
        # calculate the products of parameters and the logx powers
        prod_values = [exp_vals[i]*self.par[i] for i in range(8)]
        return sum(prod_values) / energy

    def calculate_perc_eff(self, energy):
        """Returns the efficiency as a fraction"""
        logx = math.log(energy)
        # calculate logx to various powers
        exp_vals = [math.pow(logx, float(i)) for i in range(8)]
        # calculate the products of parameters and the logx powers
        prod_values = [exp_vals[i]*self.par[i] for i in range(8)]
        return 100.0 * sum(prod_values) / energy


def test_value_sanity():
    """Trys to weed out silly mistakes"""
    # check to make sure that all the values in the HPGE efficiency are small
    for param in INPUT["HPGe Efficiency Function"]:
        if abs(param) > 0.1:
            print "Warning, efficiency parameters might be too large\n"
    # check to make sure the integration time is not too small
    if INPUT["HPGe Integration Time"] < 20.0:
        print "Warning, you might not have counted in the HPGe spectrum long"
        print "enough for a statistically significant result\n"
    # check to make sure the gamma energy is not too small or too large
    for energy in INPUT["Gamma Energies"]:
        if energy < 0.02 or energy > 3.0:
            print "Warning energy {0:8.4f} is well outside the"\
                  " usual efficiency".format(energy)
            print "calibration range\n"
    # check to make sure the areas are not too small
    for area in INPUT["Gamma Areas"]:
        if (math.sqrt(float(area))/float(area)) >= 0.50:
            print "Warning, gamma ray area statistical errors are >= 50%\n"


def test_list_lengths():
    """Tests input list lengths for correctness"""
    # check to make sure that the lists contain the appropriate numbers of
    # elements
    if len(INPUT["Gamma Energies"]) != len(INPUT["Gamma Branchings"]) or\
       len(INPUT["Gamma Energies"]) != len(INPUT["Gamma Areas"]):
        print 'The "Gamma Energies", "Gamma Branchings", and "Gamma Areas"'
        print 'entries must all have equal length'
        sys.exit()
    if len(INPUT["Gamma Energies"]) == 0:
        print 'The "Gamma Energies", "Gamma Branchings", and "Gamma Areas"'
        print 'entries must all have length > 0'
        sys.exit()
    if len(INPUT["HPGe Efficiency Function"]) != 6:
        print 'The "HPGe Efficiency Function" entry must contain exactly 6'
        print 'parameters, a0 through a5'
        sys.exit()


def test_scalar_types():
    """Tests input values to make sure the appropriate ones are numbers"""
    # check to make sure that the scalar values are in fact scalars
    if not isinstance(INPUT["Half Life"], types.FloatType):
        print 'The "Half Life" entry must be a floating point'
        print 'number. Consider adding ".0" to the end if it is an integer'
        sys.exit()
    if not isinstance(INPUT["Cycle Length"], types.FloatType):
        print 'The "Cycle Length" entry must be a floating point'
        print 'number. Consider adding ".0" to the end if it is an integer'
        sys.exit()
    if not isinstance(INPUT["Collection Time"], types.FloatType):
        print 'The "Effective Collection Time" entry must be a floating point'
        print 'number. Consider adding ".0" to the end if it is an integer'
        sys.exit()
    if not isinstance(INPUT["Voltage Rampdown Time"], types.FloatType):
        print 'The "Effective Collection Time" entry must be a floating point'
        print 'number. Consider adding ".0" to the end if it is an integer'
        sys.exit()
    if not isinstance(INPUT["HPGe Integration Time"], types.FloatType):
        print 'The "HPGe Integration Time" entry must be a floating point'
        print 'number. Consider adding ".0" to the end if it is an integer'
        sys.exit()
    if INPUT["Voltage Rampdown Time"] > INPUT["Collection Time"]:
        print 'The "Voltage Rampdown Time" entry excedes the "Collection Time"'
        print 'entry, therefor collection is not happening'
        sys.exit()
    if not isinstance(INPUT["Title Name"], types.StringType):
        print 'The "Title Name" entry must be a string'
        sys.exit()
    if len(INPUT["Title Name"]) > 63:
        print 'The "Title Name" entry must is too long'
        print '"Title Name" must not exceed 63 characters'
        sys.exit()


def test_list_types():
    """Tests input values to make sure the appropriate ones are lists"""
    # check to make certain that certain parameters are lists, even if they
    # only contain one element
    if not isinstance(INPUT["Gamma Energies"], types.ListType):
        print 'The "Gamma Energies" entry must be a list'
        sys.exit()
    if not isinstance(INPUT["Gamma Branchings"], types.ListType):
        print 'The "Gamma Intensities" entry must be a list'
        sys.exit()
    if not isinstance(INPUT["Gamma Areas"], types.ListType):
        print 'The "Gamma Areas" entry must be a list'
        sys.exit()
    if not isinstance(INPUT["HPGe Efficiency Function"], types.ListType):
        print 'The "HPGe Efficiency Function" entry must be a list'
        sys.exit()
    for element in INPUT["Gamma Energies"]:
        if not isinstance(element, types.FloatType):
            print 'All elements of the "Gamma Energies" entry must be'
            print 'floating point numbers. Consider adding ".0" to the end if'
            print 'it is an integer'
            sys.exit()
    for element in INPUT["Gamma Branchings"]:
        if not isinstance(element, types.FloatType):
            print 'All elements of the "Gamma Branchings" entry must be'
            print 'floating point numbers. Consider adding ".0" to the end if'
            print 'it is an integer'
            sys.exit()
    for element in INPUT["Gamma Areas"]:
        if not isinstance(element, types.FloatType):
            print 'All elements of the "Gamma Areas" entry must be'
            print 'floating point numbers. Consider adding ".0" to the end if'
            print 'it is an integer'
            sys.exit()
    for element in INPUT["HPGe Efficiency Function"]:
        if not isinstance(element, types.FloatType):
            print 'All elements of the "HPGe Efficiency Function" entry must'
            print 'be floating point numbers. Consider adding ".0" to the end'
            print 'if it is an integer'
            sys.exit()


HEADER_STRING = """

|-----------------------------------------------------------------------------|
| RESULTS FOR: {0:63s}|
|-----------------------------------------------------------------------------|
|                 GAMMA                |     DECAYS AT HPGE    | BEAM RATE    |
| ENERGY(MeV) | BRANCHING | EFFICIENCY |   TOTAL   | PER CYCLE |  (HZ)        |"""

ROW_STRING = """|-------------|-----------|------------|-----------|-----------|--------------|
| {0: ^11.4f} | {1:4.3e} | {2:5.4e} | {3:4.3e} | {4:4.3e} | {5:7.6e} |"""

FOOTER_STRING = """|-------------|-----------|------------|-----------|-----------|--------------|

"""

if __name__ == "__main__":
    main()
