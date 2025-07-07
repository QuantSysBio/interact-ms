# interact-ms

Easy GUI/webserver access for mass spectrometry identification and analysis tools, namely PEPSeek and inSPIRE.

<img src="https://raw.githubusercontent.com/QuantSysBio/inSPIRE/master/img/inSPIRE-logo.png" alt="drawing" width="200"/>


## Set Up

### Before Downloading

We recommend working with interact-ms through conda.

### Setting up your environment:

For basic interact-ms use.

1) To start with create a new conda environment with python version 3.11:

```
conda create --name interact_ms python=3.11 -c conda-forge
```

2) Activate this environment

```
conda activate interact_ms
```

3) You will then need to install the interact-ms package (this also installs inSPIRE and PEPSeek):

```
pip install interact_ms==2.0rc4
```

4) To check your installation, run the following command (it is normal for this call to hang for a few seconds on first execution)

```
interact-ms -h
```

5) You will require Percolator for rescoring. On Linux, Percolator can be installed via conda with the command below. Otherwise see https://github.com/percolator/percolator.

```
conda install -c bioconda percolator
```

6) Once you have successfully installed interact-ms you should run it specifying your pipeline and the mode of execution. Starting the web-server will then be achieved by:

```
interact-ms --config_file path-to-config-file
```

where the config file is a yaml file specifying configuration of your interact-ms server.


## Additional Features

In order to use raw files on Linux or Mac O.S. you will require the use of mono ([mono project](https://www.mono-project.com/download/stable/)) which is required by the ThermoRawFileParser. (The ThermoRawFileParser itself is open source and automatically downloaded.)

In order to use NetMHCpan for binding affinity prediction you should download the software from the [DTU site](https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/) (you must agree to the license agreement). On linux and maxos systems we typically use tcsh. If you are a windows user you should download the Linux distribution and will need to install docker (see [docker documentation](https://docs.docker.com/desktop/).

In order to use MSFragger you should download from [MSFragger](https://github.com/Nesvilab/MSFragger/wiki/Preparing-MSFragger#Downloading-MSFragger) (you must agree to the license agreements). You will also need java which can be installed using:

```
conda install -c conda-forge openjdk
```

In order to use Skyline you will need to download docker and insure can be executed. See instructions from [docker documentation](https://docs.docker.com/desktop/). (Skyline itself is open source).


## Writing the Config File.

The following configurations should be set for interact-ms:

| Key   | Description   |
|-------|---------------|
| maxCpus | The number of CPUs from your computer that you wish to dedicate to a single pipeline execution.  |
| fraggerPath    | The file path to the .jar file of MSFragger (e.g. for version 3.7 the end of this path should be: MSFragger-3.7/MSFragger-3.7.jar) |
| fraggerMemory  | The ammount of memory (GB) that is available for MSFragger execution. |
| netMHCpan      | The command that can be used to run NetMHCpan (e.g. on Linux we use [tcsh](https://www.cyberciti.biz/faq/howto-install-csh-shell-on-linux/) to execute NetMHCpan and so our config key is ```tcsh /data/interact-ms/netMHCpan-4.1/netMHCpan```). |


## Example of Windows Config


```
---
fraggerPath: C:/Users/username/Downloads/MSFragger-3.7/MSFragger-3.7.jar
netMHCpan: C:/Users/username/Downloads/netMHCpan-4.1
fraggerMemory: 60
maxCpus: 20
skylineRunner: C:/Program Files/Skyline/SkylineRunner.exe
rescoreCommand: C:/Program Files/percolator-v3-05/bin/percolator.exe
```
# Example of Linux/MacOS Config

```
---
fraggerPath: /Users/username/Downloads/MSFragger-3.7/MSFragger-3.7.jar
netMHCpan: /Users/username/Downloads/netMHCpan-4.1
fraggerMemory: 60
maxCpus: 20
```
