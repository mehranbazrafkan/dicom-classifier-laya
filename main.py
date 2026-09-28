import os
import warnings
from pathlib import Path
from collections import defaultdict

# Disable Hugging Face / Transformers progress bars
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# Hide Laya's RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

import pydicom
from pydicom.multival import MultiValue
import laya


# ============================================================
# Load Laya
# ============================================================

agent = laya.load("convaiinnovations/laya")


# ============================================================
# DICOM file discovery
# ============================================================

def is_dicom_file(path: str) -> bool:
    """
    Check whether a file is likely to be a DICOM file.

    We do not rely only on the file extension because DICOM
    datasets often contain files without .dcm extensions.
    """

    path = Path(path)
    name = path.name.lower()

    if name.endswith((".dcm", ".ima")):
        return True

    non_dicom_extensions = (
        ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".csv", ".tsv", ".txt",
        ".zip", ".gz", ".bz2", ".xz", ".tar", ".7z", ".rar",
        ".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff",
        ".bmp", ".svg",
        ".mp4", ".mov", ".avi", ".mp3", ".wav",
        ".nii", ".nii.gz", ".mgz", ".mgh",
        ".json", ".yaml", ".yml", ".xml",
        ".py", ".sh", ".html", ".md", ".log",
    )

    if name.endswith(non_dicom_extensions):
        return False

    try:
        with open(path, "rb") as f:
            f.seek(128)
            return f.read(4) == b"DICM"
    except OSError:
        return False


# ============================================================
# DICOM helpers
# ============================================================

def normalize_image_type(value):
    """Convert DICOM ImageType into a normal Python list."""

    if value is None:
        return []

    if isinstance(value, (list, tuple, MultiValue)):
        return [str(x).strip() for x in value]

    text = str(value)

    if "\\" in text:
        return [x.strip() for x in text.split("\\")]

    return [text.strip()] if text.strip() else []


def get_value(ds, name, default=""):
    """Safely get a DICOM attribute."""

    value = getattr(ds, name, default)

    if value is None:
        return default

    return str(value).strip()


def get_numeric_value(ds, name, default=""):
    """
    Safely get a DICOM numeric value.

    Kept as a string here to remain consistent with the original
    Laya input representation.
    """

    return get_value(ds, name, default)


# ============================================================
# Read one DICOM
# ============================================================

def read_dicom(dicom_path: Path):
    """
    Read one DICOM header.

    Pixel data is never loaded.
    """

    try:
        return pydicom.dcmread(
            str(dicom_path),
            stop_before_pixels=True,
            force=True,
        )

    except Exception as e:
        print(
            f"[WARNING] Could not read DICOM "
            f"{dicom_path}: {e}"
        )
        return None


# ============================================================
# Extract metadata from one DICOM
# ============================================================

def extract_dicom_data(ds, dicom_path: Path) -> dict:
    """
    Extract metadata from one DICOM instance.

    This contains evidence only.
    No BIDS classification is performed here.
    """

    image_type = normalize_image_type(
        getattr(ds, "ImageType", None)
    )

    has_pixel_data = (
        "Rows" in ds and
        "Columns" in ds
    )

    return {

        # ----------------------------------------------------
        # File
        # ----------------------------------------------------

        "file": str(dicom_path),

        # ----------------------------------------------------
        # DICOM relationships
        # ----------------------------------------------------

        "study_instance_uid": get_value(
            ds,
            "StudyInstanceUID"
        ),

        "series_instance_uid": get_value(
            ds,
            "SeriesInstanceUID"
        ),

        "sop_instance_uid": get_value(
            ds,
            "SOPInstanceUID"
        ),

        # ----------------------------------------------------
        # Basic imaging information
        # ----------------------------------------------------

        "modality": get_value(
            ds,
            "Modality"
        ),

        # ----------------------------------------------------
        # Series information
        # ----------------------------------------------------

        "series_description": get_value(
            ds,
            "SeriesDescription"
        ),

        "protocol_name": get_value(
            ds,
            "ProtocolName"
        ),

        "series_number": get_value(
            ds,
            "SeriesNumber"
        ),

        "sequence_name": get_value(
            ds,
            "SequenceName"
        ),

        # ----------------------------------------------------
        # Sequence information
        # ----------------------------------------------------

        "scanning_sequence": get_value(
            ds,
            "ScanningSequence"
        ),

        "sequence_variant": get_value(
            ds,
            "SequenceVariant"
        ),

        "scan_options": get_value(
            ds,
            "ScanOptions"
        ),

        "mr_acquisition_type": get_value(
            ds,
            "MRAcquisitionType"
        ),

        "image_type": image_type,

        # ----------------------------------------------------
        # Study information
        # ----------------------------------------------------

        "study_description": (
            get_value(ds, "StudyDescription")
            or get_value(ds, "StudyName")
        ),

        "study_date": get_value(
            ds,
            "StudyDate"
        ),

        "study_time": get_value(
            ds,
            "StudyTime"
        ),

        "acquisition_time": get_value(
            ds,
            "AcquisitionTime"
        ),

        # ----------------------------------------------------
        # Acquisition information
        # ----------------------------------------------------

        "instance_number": get_value(
            ds,
            "InstanceNumber"
        ),

        "acquisition_number": get_value(
            ds,
            "AcquisitionNumber"
        ),

        "number_of_images": get_value(
            ds,
            "ImagesInAcquisition"
        ),

        "number_of_temporal_positions": get_value(
            ds,
            "NumberOfTemporalPositions"
        ),

        # ----------------------------------------------------
        # Echo information
        # ----------------------------------------------------

        "echo_time": get_numeric_value(
            ds,
            "EchoTime"
        ),

        "echo_number": get_value(
            ds,
            "EchoNumbers"
        ),

        # ----------------------------------------------------
        # MR parameters
        # ----------------------------------------------------

        "repetition_time": get_numeric_value(
            ds,
            "RepetitionTime"
        ),

        "flip_angle": get_numeric_value(
            ds,
            "FlipAngle"
        ),

        "inversion_time": get_numeric_value(
            ds,
            "InversionTime"
        ),

        "number_of_averages": get_numeric_value(
            ds,
            "NumberOfAverages"
        ),

        # ----------------------------------------------------
        # Image dimensions
        # ----------------------------------------------------

        "rows": get_value(
            ds,
            "Rows"
        ),

        "columns": get_value(
            ds,
            "Columns"
        ),

        # ----------------------------------------------------
        # Spatial information
        # ----------------------------------------------------

        "image_orientation_patient": get_value(
            ds,
            "ImageOrientationPatient"
        ),

        "image_position_patient": get_value(
            ds,
            "ImagePositionPatient"
        ),

        "slice_thickness": get_value(
            ds,
            "SliceThickness"
        ),

        "spacing_between_slices": get_value(
            ds,
            "SpacingBetweenSlices"
        ),

        # ----------------------------------------------------
        # Phase encoding
        # ----------------------------------------------------

        "in_plane_phase_encoding_direction": get_value(
            ds,
            "InPlanePhaseEncodingDirection"
        ),

        "in_plane_phase_encoding_direction_dicom": get_value(
            ds,
            "InPlanePhaseEncodingDirection"
        ),

        # ----------------------------------------------------
        # Scanner information
        # ----------------------------------------------------

        "magnetic_field_strength": get_value(
            ds,
            "MagneticFieldStrength"
        ),

        "manufacturer": get_value(
            ds,
            "Manufacturer"
        ),

        "manufacturer_model_name": get_value(
            ds,
            "ManufacturerModelName"
        ),

        "software_versions": get_value(
            ds,
            "SoftwareVersions"
        ),

        # ----------------------------------------------------
        # Image storage
        # ----------------------------------------------------

        "has_pixel_data": has_pixel_data,
    }


# ============================================================
# Utility: unique values
# ============================================================

def unique_values(values):
    """
    Return unique values while preserving order.
    """

    result = []

    for value in values:

        if value in ("", None, []):
            continue

        if value not in result:
            result.append(value)

    return result


# ============================================================
# Aggregate one DICOM series
# ============================================================

def aggregate_series(instances):
    """
    Convert many DICOM instances belonging to one
    SeriesInstanceUID into a single series-level object.
    """

    if not instances:
        return None

    series = {}

    # --------------------------------------------------------
    # Fields that describe the series
    # --------------------------------------------------------

    fields = [
        "modality",

        "series_description",
        "protocol_name",
        "series_number",
        "sequence_name",

        "scanning_sequence",
        "sequence_variant",
        "scan_options",
        "mr_acquisition_type",

        "study_description",

        "study_date",
        "study_time",

        "echo_time",
        "echo_number",
        "repetition_time",
        "flip_angle",
        "inversion_time",

        "number_of_averages",

        "rows",
        "columns",

        "image_orientation_patient",

        "slice_thickness",
        "spacing_between_slices",

        "in_plane_phase_encoding_direction",

        "magnetic_field_strength",
        "manufacturer",
        "manufacturer_model_name",
        "software_versions",
    ]

    for field in fields:

        values = unique_values(
            [
                instance.get(field)
                for instance in instances
            ]
        )

        if len(values) == 0:
            series[field] = ""

        elif len(values) == 1:
            series[field] = values[0]

        else:
            series[field] = values

    # --------------------------------------------------------
    # ImageType
    # --------------------------------------------------------

    image_types = []

    for instance in instances:

        for image_type in instance.get(
            "image_type",
            []
        ):

            if image_type not in image_types:
                image_types.append(image_type)

    series["image_type"] = image_types

    # --------------------------------------------------------
    # Acquisition times
    # --------------------------------------------------------

    series["acquisition_times"] = unique_values(
        [
            instance.get("acquisition_time")
            for instance in instances
        ]
    )

    # --------------------------------------------------------
    # Instance numbers
    # --------------------------------------------------------

    instance_numbers = []

    for instance in instances:

        value = instance.get(
            "instance_number"
        )

        if value:
            instance_numbers.append(value)

    series["instance_numbers"] = unique_values(
        instance_numbers
    )

    # --------------------------------------------------------
    # Number of DICOM instances
    # --------------------------------------------------------

    series["number_of_dicom_files"] = len(
        instances
    )

    # --------------------------------------------------------
    # DICOM relationships
    # --------------------------------------------------------

    series["study_instance_uid"] = (
        instances[0].get(
            "study_instance_uid",
            ""
        )
    )

    series["series_instance_uid"] = (
        instances[0].get(
            "series_instance_uid",
            ""
        )
    )

    # --------------------------------------------------------
    # Actual files
    # --------------------------------------------------------

    series["files"] = [
        instance["file"]
        for instance in instances
    ]

    return series


# ============================================================
# Discover all DICOM files
# ============================================================

def discover_dicom_files(root: str):
    """
    Recursively discover DICOM files.
    """

    root = Path(root)

    files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if is_dicom_file(path):
            files.append(path)

    return files


# ============================================================
# Build Study → Series hierarchy
# ============================================================

def discover_studies(root: str):
    """
    Discover the DICOM hierarchy:

        StudyInstanceUID
            └── SeriesInstanceUID
                    └── DICOM instances
    """

    dicom_files = discover_dicom_files(root)

    print(
        f"Found {len(dicom_files)} possible DICOM files."
    )

    # --------------------------------------------------------
    # Group instances by study + series
    # --------------------------------------------------------

    grouped = defaultdict(
        lambda: defaultdict(list)
    )

    for path in dicom_files:

        ds = read_dicom(path)

        if ds is None:
            continue

        study_uid = get_value(
            ds,
            "StudyInstanceUID",
            "__UNKNOWN_STUDY__"
        )

        series_uid = get_value(
            ds,
            "SeriesInstanceUID",
            "__UNKNOWN_SERIES__"
        )

        data = extract_dicom_data(
            ds,
            path
        )

        grouped[study_uid][series_uid].append(
            data
        )

    # --------------------------------------------------------
    # Aggregate each series
    # --------------------------------------------------------

    studies = {}

    for study_uid, series_dict in grouped.items():

        studies[study_uid] = {}

        for series_uid, instances in series_dict.items():

            series = aggregate_series(
                instances
            )

            if series is not None:
                studies[study_uid][series_uid] = series

    return studies


# ============================================================
# Create compact context for Laya
# ============================================================

def create_series_context(
    target_series,
    all_series,
):
    """
    Build the state given to Laya.

    The target series receives detailed metadata.

    Other series from the same study receive compact
    metadata so Laya can reason about relationships such
    as run number, fieldmaps, echoes, etc.
    """

    related_series = []

    target_uid = target_series[
        "series_instance_uid"
    ]

    for series_uid, series in all_series.items():

        if series_uid == target_uid:
            continue

        related_series.append({

            "series_instance_uid": (
                series.get(
                    "series_instance_uid",
                    ""
                )
            ),

            "series_number": (
                series.get(
                    "series_number",
                    ""
                )
            ),

            "series_description": (
                series.get(
                    "series_description",
                    ""
                )
            ),

            "protocol_name": (
                series.get(
                    "protocol_name",
                    ""
                )
            ),

            "sequence_name": (
                series.get(
                    "sequence_name",
                    ""
                )
            ),

            "modality": (
                series.get(
                    "modality",
                    ""
                )
            ),

            "scanning_sequence": (
                series.get(
                    "scanning_sequence",
                    ""
                )
            ),

            "sequence_variant": (
                series.get(
                    "sequence_variant",
                    ""
                )
            ),

            "mr_acquisition_type": (
                series.get(
                    "mr_acquisition_type",
                    ""
                )
            ),

            "image_type": (
                series.get(
                    "image_type",
                    []
                )
            ),

            "echo_time": (
                series.get(
                    "echo_time",
                    ""
                )
            ),

            "echo_number": (
                series.get(
                    "echo_number",
                    ""
                )
            ),

            "repetition_time": (
                series.get(
                    "repetition_time",
                    ""
                )
            ),

            "flip_angle": (
                series.get(
                    "flip_angle",
                    ""
                )
            ),

            "inversion_time": (
                series.get(
                    "inversion_time",
                    ""
                )
            ),

            "number_of_dicom_files": (
                series.get(
                    "number_of_dicom_files",
                    0
                )
            ),
        })

    return {

        # ====================================================
        # Target
        # ====================================================

        "target_series": {
            key: value
            for key, value in target_series.items()
            if key != "files"
        },

        # ====================================================
        # Other series belonging to the same study
        # ====================================================

        "related_series": related_series,

        # ====================================================
        # Study information
        # ====================================================

        "study": {
            "study_instance_uid": (
                target_series.get(
                    "study_instance_uid",
                    ""
                )
            ),

            "study_description": (
                target_series.get(
                    "study_description",
                    ""
                )
            ),

            "study_date": (
                target_series.get(
                    "study_date",
                    ""
                )
            ),

            "study_time": (
                target_series.get(
                    "study_time",
                    ""
                )
            ),

            "number_of_series": len(
                all_series
            ),
        },
    }


# ============================================================
# Print discovered structure
# ============================================================

def print_structure(studies):

    print("\n")
    print("=" * 80)
    print("DISCOVERED DICOM STRUCTURE")
    print("=" * 80)

    for study_index, (
        study_uid,
        series_dict
    ) in enumerate(
        studies.items(),
        start=1
    ):

        print(
            f"\nStudy {study_index}"
        )

        print(
            f"  StudyInstanceUID: "
            f"{study_uid}"
        )

        print(
            f"  Number of series: "
            f"{len(series_dict)}"
        )

        for series_index, (
            series_uid,
            series
        ) in enumerate(
            series_dict.items(),
            start=1
        ):

            print(
                f"\n  Series {series_index}"
            )

            print(
                f"    SeriesInstanceUID: "
                f"{series_uid}"
            )

            print(
                f"    SeriesNumber: "
                f"{series.get('series_number')}"
            )

            print(
                f"    Description: "
                f"{series.get('series_description')}"
            )

            print(
                f"    Protocol: "
                f"{series.get('protocol_name')}"
            )

            print(
                f"    Sequence: "
                f"{series.get('sequence_name')}"
            )

            print(
                f"    Modality: "
                f"{series.get('modality')}"
            )

            print(
                f"    ImageType: "
                f"{series.get('image_type')}"
            )

            print(
                f"    EchoTime: "
                f"{series.get('echo_time')}"
            )

            print(
                f"    EchoNumber: "
                f"{series.get('echo_number')}"
            )

            print(
                f"    FlipAngle: "
                f"{series.get('flip_angle')}"
            )

            print(
                f"    InversionTime: "
                f"{series.get('inversion_time')}"
            )

            print(
                f"    Instances: "
                f"{series.get('number_of_dicom_files')}"
            )


# ============================================================
# Questions for Laya
# ============================================================

questions = {

    "datatype": {
        "type": "choice",
        "instructions": (
            "What is the BIDS data type of this DICOM series?"
        ),
        "criteria": {
            "anat": (
                "Anatomical imaging data, including structural MRI "
                "such as T1-weighted, T2-weighted, FLAIR, proton-density, "
                "and other anatomical scans."
            ),

            "func": (
                "Functional imaging data, including BOLD fMRI, "
                "task-fMRI, and resting-state fMRI."
            ),

            "dwi": (
                "Diffusion-weighted imaging data, including diffusion "
                "MRI acquisitions used to characterize water diffusion."
            ),

            "fmap": (
                "Field-mapping data used to characterize magnetic-field "
                "inhomogeneity, including field maps, phase-difference "
                "maps, and spin-echo EPI field maps."
            ),

            "perf": (
                "Perfusion imaging data, including arterial spin labeling "
                "and other MRI perfusion acquisitions."
            ),

            "pet": (
                "Positron emission tomography imaging data."
            ),

            "mrs": (
                "Magnetic resonance spectroscopy data."
            ),
        },
    },

    "suffix": {
        "type": "choice",
        "instructions": (
            "What BIDS suffix best describes this DICOM series?"
        ),
        "criteria": {
            "T1w": (
                "T1-weighted anatomical MRI image."
            ),

            "T2w": (
                "T2-weighted anatomical MRI image."
            ),

            "T2starw": (
                "T2*-weighted anatomical MRI image."
            ),

            "T1rho": (
                "T1-rho MRI image."
            ),

            "FLAIR": (
                "Fluid-attenuated inversion recovery anatomical MRI image."
            ),

            "PD": (
                "Proton-density weighted anatomical MRI image."
            ),

            "inplaneT1": (
                "T1-weighted image acquired in-plane for another acquisition."
            ),

            "inplaneT2": (
                "T2-weighted image acquired in-plane for another acquisition."
            ),

            "PDT2": (
                "Combined proton-density/T2-weighted anatomical image."
            ),

            "UNIT1": (
                "UNIT1 anatomical MRI image."
            ),

            "angio": (
                "Angiographic imaging data."
            ),

            "defacemask": (
                "Defacing mask associated with an anatomical image."
            ),

            "bold": (
                "Blood-oxygen-level-dependent functional MRI image."
            ),

            "sbref": (
                "Single-band reference image associated with functional MRI."
            ),

            "dwi": (
                "Diffusion-weighted imaging data."
            ),

            "epi": (
                "Echo-planar imaging acquisition, commonly used for "
                "field mapping or other EPI-based acquisitions."
            ),

            "phasediff": (
                "Phase-difference field-map image."
            ),

            "magnitude1": (
                "First magnitude image associated with a field map."
            ),

            "magnitude2": (
                "Second magnitude image associated with a field map."
            ),

            "phase1": (
                "First phase image associated with a field map."
            ),

            "phase2": (
                "Second phase image associated with a field map."
            ),

            "magnitude": (
                "Magnitude image associated with a field-map acquisition."
            ),

            "fieldmap": (
                "Direct field-map image."
            ),

            "TB1map": (
                "B1 transmit-field mapping image."
            ),

            "TB1DAM": (
                "B1 transmit-field difference-angle map."
            ),

            "TB1TFL": (
                "B1 transmit-field TFL acquisition."
            ),

            "TB1RFM": (
                "B1 transmit-field RF mapping acquisition."
            ),

            "TB1AFI": (
                "B1 transmit-field AFI acquisition."
            ),

            "T2star": (
                "T2* mapping image."
            ),

            "T1map": (
                "T1 relaxation mapping image."
            ),

            "T2map": (
                "T2 relaxation mapping image."
            ),

            "ASL": (
                "Arterial spin labeling perfusion image."
            ),

            "m0scan": (
                "M0 calibration/reference scan associated with ASL."
            ),

            "phase": (
                "Phase image."
            ),
        },
    },

    "part": {
        "type": "choice",
        "instructions": (
            "What image part does this DICOM series represent?"
        ),
        "criteria": {
            "mag": (
                "Magnitude image."
            ),

            "phase": (
                "Phase image."
            ),

            "real": (
                "Real component of the complex-valued image."
            ),

            "imag": (
                "Imaginary component of the complex-valued image."
            ),
        },
    },

    "direction": {
        "type": "choice",
        "instructions": (
            "What phase-encoding direction does this acquisition use?"
        ),
        "criteria": {
            "i": "Phase encoding along the first image axis.",
            "i-": "Phase encoding along the negative first image axis.",
            "j": "Phase encoding along the second image axis.",
            "j-": "Phase encoding along the negative second image axis.",
            "k": "Phase encoding along the third image axis.",
            "k-": "Phase encoding along the negative third image axis.",
        },
    },

    "run": {
        "type": "choice",
        "instructions": (
            "What run number should be assigned to this acquisition?"
        ),
        "criteria": {
            "1": "First acquisition of this type.",
            "2": "Second acquisition of this type.",
            "3": "Third acquisition of this type.",
            "4": "Fourth acquisition of this type.",
            "5": "Fifth acquisition of this type.",
            "6": "Sixth acquisition of this type.",
            "7": "Seventh acquisition of this type.",
            "8": "Eighth acquisition of this type.",
            "9": "Ninth acquisition of this type.",
        },
    },

    "echo": {
        "type": "choice",
        "instructions": (
            "What echo number does this acquisition represent?"
        ),
        "criteria": {
            "1": "First echo.",
            "2": "Second echo.",
            "3": "Third echo.",
            "4": "Fourth echo.",
            "5": "Fifth echo.",
            "6": "Sixth echo.",
            "7": "Seventh echo.",
            "8": "Eighth echo.",
            "9": "Ninth echo.",
        },
    },

    "flip": {
        "type": "choice",
        "instructions": (
            "What flip-angle index does this acquisition represent?"
        ),
        "criteria": {
            "1": "First flip-angle acquisition.",
            "2": "Second flip-angle acquisition.",
            "3": "Third flip-angle acquisition.",
            "4": "Fourth flip-angle acquisition.",
            "5": "Fifth flip-angle acquisition.",
        },
    },

    "inversion": {
        "type": "choice",
        "instructions": (
            "What inversion index does this acquisition represent?"
        ),
        "criteria": {
            "1": "First inversion.",
            "2": "Second inversion.",
            "3": "Third inversion.",
            "4": "Fourth inversion.",
            "5": "Fifth inversion.",
        },
    },

    "mt": {
        "type": "choice",
        "instructions": (
            "Does this acquisition use magnetization transfer?"
        ),
        "criteria": {
            "on": (
                "Magnetization-transfer preparation was used."
            ),

            "off": (
                "Magnetization-transfer preparation was not used."
            ),
        },
    },
}


# ============================================================
# Run Laya for every series
# ============================================================

def classify_studies(studies):

    all_results = []

    for study_uid, series_dict in studies.items():

        print("\n")
        print("=" * 80)
        print(
            f"STUDY: {study_uid}"
        )
        print(
            f"Series: {len(series_dict)}"
        )
        print("=" * 80)

        for series_uid, target_series in series_dict.items():

            print("\n")
            print("-" * 80)
            print("TARGET SERIES")
            print("-" * 80)

            print(
                f"Series UID: "
                f"{series_uid}"
            )

            print(
                f"Series Number: "
                f"{target_series.get('series_number')}"
            )

            print(
                f"Description: "
                f"{target_series.get('series_description')}"
            )

            print(
                f"Protocol: "
                f"{target_series.get('protocol_name')}"
            )

            print(
                f"DICOM files: "
                f"{target_series.get('number_of_dicom_files')}"
            )

            # ------------------------------------------------
            # Build multi-series state
            # ------------------------------------------------

            state = create_series_context(
                target_series,
                series_dict,
            )

            print("\nState for Laya:")

            print(state)

            print("\n")

            # ------------------------------------------------
            # Ask Laya
            # ------------------------------------------------

            result = agent.predict(
                state,
                questions,
            )

            # ------------------------------------------------
            # Display result
            # ------------------------------------------------

            print(
                "# ----- Laya Result ----- #"
            )

            for question, answer in result[
                "answers"
            ].items():

                print(
                    f"Question: {question}"
                )

                print(
                    f"Answer: "
                    f"{answer['choice']}"
                )

                print(
                    "probabilities:"
                )

                for option, probability in answer[
                    "probabilities"
                ].items():

                    print(
                        f"  "
                        f"{option:<16} "
                        f"{probability:.4f}"
                    )

                print(
                    "# ----- ----- ----- #"
                )

            all_results.append({

                "study_instance_uid": study_uid,

                "series_instance_uid": series_uid,

                "series_number": (
                    target_series.get(
                        "series_number"
                    )
                ),

                "series_description": (
                    target_series.get(
                        "series_description"
                    )
                ),

                "result": result,
            })

    return all_results


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    # Directory containing your DICOM files.
    dicom_root = "./data/dicoms"

    # --------------------------------------------------------
    # Discover all relationships.
    # --------------------------------------------------------

    studies = discover_studies(
        dicom_root
    )

    # --------------------------------------------------------
    # Print discovered hierarchy.
    # --------------------------------------------------------

    print_structure(
        studies
    )

    # --------------------------------------------------------
    # Classify every discovered series.
    # --------------------------------------------------------

    results = classify_studies(
        studies
    )