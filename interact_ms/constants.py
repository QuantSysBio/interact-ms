""" Constants for the interact_ms package.
"""
INTERACT_HOME_KEY = 'interactHome'
SERVER_ADDRESS_KEY = 'serverAddress'
FRAGGER_PATH_KEY = 'fraggerPath'
FRAGGER_MEMORY_KEY = 'fraggerMemory'
CPUS_KEY = 'maxCpus'
MHCPAN_KEY = 'netMHCpan'
SKYLINE_RUNNER_KEY = 'skylineRunner'
RESCORE_COMMAND_KEY = 'rescoreCommand'

QUEUE_PATH = '{home_key}/locks/interactQueue.csv'

ALL_CONFIG_KEYS = [
    CPUS_KEY,
    FRAGGER_PATH_KEY,
    FRAGGER_MEMORY_KEY,
    INTERACT_HOME_KEY,
    MHCPAN_KEY,
    RESCORE_COMMAND_KEY,
    SERVER_ADDRESS_KEY,
    SKYLINE_RUNNER_KEY,
]

INTERMEDIATE_FILES = [
    # 'input_all_features.tab'
]

KEY_FILES = {
    'epitopePlots': 'outputFolder/PEPSeek/spectralPlots.pdf',
    'epitopeReport': 'outputFolder/PEPSeek/pepseek-report.html',
    'hostReport': 'outputFolder/PEPSeek/pepseek-host-report.html',
    'psms': 'outputFolder/finalPsmAssignments.csv',
    'peptides': 'outputFolder/finalPeptideAssignments.csv',
    'executionLog': 'execution_log.txt',
    'PEPSeek': 'outputFolder/PEPSeek.zip',
    'performance': 'outputFolder/inspire-report.html',
    'quantification': 'outputFolder/quant.zip',
    'quantReport': 'outputFolder/quant/quant-report.html',
}

ZIP_PATHS = {
    'quantification': 'outputFolder/quant',
    'PEPSeek': 'outputFolder/PEPSeek',
}

TASKS_NAMES = [
    'convert',
    'fragger',
    'prepare',
    'predictSpectra',
    'predictBinding',
    'featureGeneration',
    'featureSelection+',
    'generateReport',
    'quantify',
    'extractCandidates',
]
TASK_DESCRIPTIONS = {
    'convert': 'Converting MS Data',
    'fragger': 'Executing MSFragger',
    'prepare': 'Preparing initial PSMs',
    'predictSpectra': 'Predicting spectra',
    'predictBinding': 'Predicting binding',
    'featureGeneration': 'Generating features',
    'featureSelection+': 'Executing rescoring',
    'generateReport': 'Creating report',
    'quantify': 'Quantifying peptides',
    'extractCandidates': 'Finding pathogen peptides',
}
