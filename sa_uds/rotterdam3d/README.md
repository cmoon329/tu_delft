## How to Run

Download the following files:

* `underpass_detection.py`
* `underpass_detection_main.py`
* `test_export.json`

Run the script as follows:

```bash
python3 underpass_detection_main.py test_export.json --eps 20
```

### Input Arguments

The script takes two input arguments:

1. **Input file**
   A CityJSON file to be processed.

2. **Epsilon threshold (`--eps`)**
   The minimum difference between roof and ground areas required to identify an underpass.
   *(Default: `1e-8`)*
