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


## Test output 
Following images are from a test run.

* Area of Interest: Near the Rotterdam central library [Google Map](https://maps.app.goo.gl/Jbf8kTrSAJ9F8WbVA)
* eps: 1e-8

<img width="590" height="644" alt="Screenshot 2026-01-08 at 4 00 07 PM" src="https://github.com/user-attachments/assets/66c60250-0ecd-45d2-872a-33dc90da1ccb" />

### case 1 [Google Map](https://maps.app.goo.gl/fj1DfkWNB2VPPi8dA)
<img width="910" height="461" alt="Screenshot 2026-01-08 at 4 01 10 PM" src="https://github.com/user-attachments/assets/e07739ec-31b9-445c-9bc7-8ed06be2e692" />
<img width="599" height="615" alt="Screenshot 2026-01-08 at 4 00 43 PM" src="https://github.com/user-attachments/assets/ac6337af-9fc2-4be2-84d5-edf6571cd62f" />

### case 2 [Google Map](https://maps.app.goo.gl/aMC8U6ts1g64jLgf7)
<img width="776" height="627" alt="Screenshot 2026-01-08 at 4 03 17 PM" src="https://github.com/user-attachments/assets/b4793cce-95c1-4303-a5f1-a4fa018a6be8" />
<img width="599" height="615" alt="Screenshot 2026-01-08 at 4 02 48 PM" src="https://github.com/user-attachments/assets/e1793df4-64cb-4114-b181-03c37f5d1892" />

### case 3 [Google Map](https://maps.app.goo.gl/tzY4z9fz2f74AwyN9)
<img width="599" height="615" alt="Screenshot 2026-01-08 at 4 05 21 PM" src="https://github.com/user-attachments/assets/294d973b-0a29-4186-ab57-5333c17edf03" />
<img width="657" height="495" alt="Screenshot 2026-01-08 at 4 05 13 PM" src="https://github.com/user-attachments/assets/ad58ca1f-0807-422a-ae98-44dc390dc012" />

### case 4 [Google Map](https://maps.app.goo.gl/GvFp22FT1pKx5NcW7)
<img width="618" height="528" alt="Screenshot 2026-01-08 at 4 07 00 PM" src="https://github.com/user-attachments/assets/201b2571-906b-4a2d-b4d8-fda6c810ea75" />
<img width="599" height="615" alt="Screenshot 2026-01-08 at 4 06 23 PM" src="https://github.com/user-attachments/assets/9094f465-fb7f-4d79-b3df-ec988ef7142c" />


