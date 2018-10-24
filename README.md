This is the implementation of the technique proposed in our ESEC/FSE'18 paper "[Scalability-First Pointer Analysis with Self-Tuning Context-Sensitivity](https://silverbullettt.bitbucket.io/papers/fse2018.pdf)", called SCALER. 
SCALER is the first pointer analysis that ensures scalability (as good as context insensitivity) while achieving great precision (comparable to, or better than the best scalable context-sensitive variants).
The artifact of our paper can be downloaded from [here](http://www.brics.dk/scaler/FSE18-Artifact-Scaler.tar.gz).

To demonstrate the usefulness of SCALER to pointer analysis, we have integrated SCALER with [DOOP](https://bitbucket.org/yanniss/doop) ([PLDI'14 artifact version](http://cgi.di.uoa.gr/~smaragd/pldi14ae/pldi14-ae.tgz)), a state-of-the-art context-sensitive points-to analysis framework for Java. For your convenience, this repository also contains the DOOP framework with SCALER integrated.

This tutorial introduces how to build and use SCALER together with DOOP.


## Requirements

- A 64-bit Ubuntu system
- A Java 8 (or later) distribution
- A Python 2.x interpreter

It is recommended to set your JAVA_HOME environment variable to point to your Java installation.


## Building SCALER

We have provided a pre-compiled jar of SCALER, i.e., `scaler.jar`, in the directory `scaler/build/`. To build SCALER by yourself, you just need to switch to the `scaler/` directory and run script:

`$ ./compile.sh`

The generated `scaler.jar` will be placed in `scaler/build/` and overwrite the previous one.


## DOOP Framework

Now we introduce how to use DOOP together with SCALER.

### Installing Datalog Engine

To run DOOP framework, you need to install a LogicBlox engine for interpreting the Datalog rules used in DOOP. If you already have such engine installed (e.g., LogicBlox v3.9.0), you can skip this section. Otherwise, you can use PA-Datalog engine, a port available for academic use. The download link and installation instructions of PA-Datalog can be found on [this page](http://snf-705535.vm.okeanos.grnet.gr/agreement.html) (We recommend `.deb` package installation).

### Running DOOP

Please first change your current directory to `doop/` folder.

The command of running DOOP is:

`$ ./run -jre1.6 <analysis> <program-jar-to-analyze>`

For example, to analyze `foo.jar` with 2-object-sensitive analysis, just type:

`$ ./run -jre1.6 2-object-sensitive+heap foo.jar`

You can check all the supported `<analysis>` and other options with `./run -h`.


### Running DOOP with SCALER

The usage of running SCALER-guided pointer analysis is exactly same as the DOOP's usage, except that 1) you need to change the driver script from `run` to `run-scaler.py`; 2) you don't need to specify `<analysis>` as `run-scaler.py` script will automatically select the SCALER-guided analysis.

For example, the command to run SCALER-guided analysis for `foo.jar` is:

`$ ./run-scaler.py -jre1.6 foo.jar`

Such command first runs a context-insensitive pointer analysis as pre-analysis, then executes SCALER to select the appropriate context-sensitivity variants for all methods, and finally runs the main analysis, which applies different context-sensitivity variants to different methods according to the results output by SCALER.

SCALER is parameterized by a total scalability threshold (TST), which is related to the available memory space. The default value of TST is 30M (million), and you can use `-tst` option to specify a different TST value based on your needs and available memory.

For example, to analyze `foo.jar` with TST value of 60M, just type:

`$ ./run-scaler.py -tst 60M -jre1.6 foo.jar`
