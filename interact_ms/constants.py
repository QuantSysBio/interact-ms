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
SLURM_SCRIPT_KEY = 'slurmScript'
CONTAM_FOLDER_KEY = 'contaminantsFolder'
EXTRA_PROT_KEY = 'expandedProteomeFolder'

QUEUE_PATH = '{home_key}/locks/interactQueue.csv'

ALL_CONFIG_KEYS = [
    CPUS_KEY,
    CONTAM_FOLDER_KEY,
    EXTRA_PROT_KEY,
    FRAGGER_PATH_KEY,
    FRAGGER_MEMORY_KEY,
    INTERACT_HOME_KEY,
    MHCPAN_KEY,
    RESCORE_COMMAND_KEY,
    SERVER_ADDRESS_KEY,
    SLURM_SCRIPT_KEY,
    SKYLINE_RUNNER_KEY,
    'apptainerImage',
    'casaSingImg', 'casaModel',
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
    'invitroPlots': 'outputFolder/spectralPlots.pdf',
    'piscesReport': 'outputFolder/pisces-report.html',
    'piscesQcReport': 'outputFolder/pisces-qc-report.html',
    'piscesPlots': 'outputFolder/nonCanonicalPlots.pdf',
    'piscesMetrics': 'outputFolder/nonCanonicalMetrics.csv',
    'piscesFinal': 'outputFolder/final.zip',
    'piscesDetails': 'outputFolder/details.zip',
}

ZIP_PATHS = {
    'quantification': 'outputFolder/quant',
    'PEPSeek': 'outputFolder/PEPSeek',
    'piscesFinal': 'outputFolder/final',
    'piscesDetails': 'outputFolder/details',
}
PISCES_TASK_NAMES = [
    'writeConfigs',
    'translateGenome',
    'runCasa',
    'canonical',
    'expanded',
    'scoreCandidates',
    'deltas',
    'permuteCandidates',
    'estimateFDR',
    'proteomeMap',
    'quantify',
    'createReport',
]
PISCES_TASK_DESCRIPTIONS = {
    'translateGenome': '6 frame genome translation',
    'writeConfigs': 'Creating inSPIRE configs',
    'runCasa': 'Running Casanovo',
    'canonical': 'inSPIRE on canonical PSMs',
    'expanded': 'inSPIRE on non-canonical PSMs',
    'scoreCandidates': 'Scoring non-canonical PSMs',
    'deltas': 'Reducing to top peptide.',
    'permuteCandidates': 'Permuting top peptides',
    'estimateFDR': 'Estimating FDR',
    'proteomeMap': 'Mapping hits to proteome(s)',
    'quantify': 'Quantifying peptides',
    'createReport': 'Creating report',
}
INVITRO_TASKS = [
    'generateDB', 'runMSFragger', 'inSPIRE_15', 'inSPIRE_combined', 'finaliseResults',
]
INVITRO_TASK_DESCRIPTIONS = {
    'generateDB': 'generating DB',
    'runMSFragger': 'running MSFragger',
    'inSPIRE_15': 'running inSPIRE 1.5',
    'inSPIRE_combined': 'running combined inSPIRE',
    'finaliseResults': 'finalising results',
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
