# MTAS Beam Rate Calculator
This script uses the counts of peaks in HPGe spectra, the absolute branching of those gammas, the energies of the gammas, the HPGe efficiency function, the halflife, the cycle time, the collection time, the voltage rampdown time, and the HPGe integration time to calculate the rate of radioactive ions reaching the tape station per second, for each gamma.

## Execution
Running this script can be accomplished in several ways:
- './calc_rate.py input_file_name.py'
- './calc_rate.py input_file_name'
- 'python calc_rate.py input_file_name.py'
- 'python calc_rate.py input_file_name

## Constraints
The script has very few constraints they are as follows:
- The input file, whatever the name, must have the `.py` extension.
- The input file must be in the same directory as the script.
- The **INPUT["Gamma Energies"]**, **INPUT["Gamma Branching"]**, and **INPUT["Gamma Areas"]** entries must all be lists with the same number of entries in each list.
- The **INPUT["HPGe Efficiency Function"]** entry must have six items, which correspond to the 6 parameters of the HPGe efficiency function.
- The **INPUT["Half Life"]**, **INPUT["Cycle Length"]**, **INPUT["Collection Time"]**, **INPUT["Voltage Rampdown Time"]**, and **INPUT["HPGe Integration Time"]** entries must all be floating point numbers.
- The **INPUT["Title Name"]** entry must be a string with 63 characters or less.
- The file must start with `INPUT = {}`.
- Comments in the input file must be in the standard python format.

## Input
### Listing
- **"Entry Name"**, *Type*, Information
- **"Title Name"**, *String*, Max 63 character string which is displayed in the output.
- **"Half Life"**, *Floating Point*, Half-life in seconds of the nucleus of interest.
- **"Cycle Length"**, *Floating Point*, Time in seconds of a complete cycle: Collection time + 3*(move time) + measure time + laser time + etc.
- **"Collection Time"**, *Floating Point*, Time in seconds of the collection phase in a cycle.
- **"Voltage Rampdown Time"**, *Floating Point*, Time in seconds for the HV on the kicker to go from 5000V to 0V, should be ***0.002*** with the new HV switch.
- **"HPGe Integration Time"**, *Floating Point* Time in seconds that the HPGe has been running.
- **"Gamma Energies"**, *List of n Floating Points*, List of n energies of fitted gamma rays (in MeV), n >= 1.
- **"Gamma Branchings"**, *List of n Floating Points*, List of n absolute branchings of the fitted gamma rays, n >= 1.
- **"Gamma Areas"**, *List of n Floating Points*, List of n peak areas of the fitted gamma rays, n >= 1.
- **"HPGe Efficiency Function"**, *List of six Floating Points*, List of the six parameters of the HPGe Efficiency function.

### Information
Entries in the input file appear as: INPUT["Entry Name"] = Stuff
The gamma efficiency function is:
```
Eff(En) = (a0 + a1*x + a2*x^2 + a3*x^3 + a5*x^5 + a7*x^7)/(En)
x = Log10(En)
En = Gamma-ray energy in MeV
```

###Example Input File
```
# do not touch this part
INPUT = {}  # ne pas toucher

# stores the title information you wish displayed
INPUT["Title Name"] = "Some Random Nucleus"
# stores the half life in seconds of the isotope in question
INPUT["Half Life"] = 172.2
# stores the cycle length in seconds
# this is: Collection time + 3*(move time) + measure time + laser time
INPUT["Cycle Length"] = 286.61
# stores the collection time in seconds
INPUT["Collection Time"] = 100.0
# stores the rampdown time of the high voltage kicker, lets the script account
# for the fact that beam collection does not start at the beginning of the
# collection time but instead after the voltage has ramped down enough for the
# beam to hit the tape
INPUT["Voltage Rampdown Time"] = 0.002
# stores the time the HPGe spectrum was accumulating, in seconds
INPUT["HPGe Integration Time"] = 609.0
# stores the energies (in MeV) of the gammas of interest
INPUT["Gamma Energies"] = [0.802, 1.173]
# stores the intensities of the gammas of interest
# if the intensity is 2.56% give 0.0256
INPUT["Gamma Branchings"] = [0.0256, 0.5000462]
# stores the counts of the peaks of interest
INPUT["Gamma Areas"] = [343.0, 4994.0]
# stores the parameters of the efficiency function
# the function is:
# eff(En) = (a0 + a1*x + a2*x^2 + a3*x^3 + a5*x^5 + a7*x^7)/(En)
# with x = Log_10(en) and En = (Gamma Energy in MeV)
# the format is: [a0, a1, a2, a3, a4, a5]
INPUT["HPGe Efficiency Function"] = [8.17090e-03, 1.84907e-03, -3.28729e-04,
                                     -7.60215e-04, 1.87004e-04, -1.16447e-05]
```
