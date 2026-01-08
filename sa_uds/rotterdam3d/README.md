## How to run
Download files below
* underpass_detection.py
* underpass_detection_main.py
* test_export.json

Run the code like below 
$\color{blue}{\text{python3 underpass_detection_main.py test_export.json --eps 20}}$ 
<span style="background-color:green">Mrs. Robinson</span>
> python3 underpass_detection_main.py test_export.json --eps 20

It takes 2 arguments as input
1) Input file to read, a JSON
2) Epsilon threshold for minimum difference between roof and ground areas to consider an underpass
   (default: 1e-8)
