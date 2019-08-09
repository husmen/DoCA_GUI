# DoCA_GUI
DoCA (Document Classification and Analysis)

Submission for "PARDUS Dosya Sınıflandırma ve Analiz ([DoSA](https://inovasyon.havelsan.com.tr/havelsan/#/competition-open/4))" Competition in which we won the first place: [source](https://www.linkedin.com/feed/update/urn:li:activity:6432215954771496960).

# Contributors
### Team

Houssem Menhour

Kübra Köksal

### Supervisors

Assoc. Prof. Dr. Ahmet Sayar

Res. Asst. Dr. Süleyman Eken


# Usage

### Install the following requirements
libreoffice-dev

libmagickwand-dev

ffmpeg

couchdb

### Clone, setup environment and run

    git clone https://github.com/husmen/DoCA_GUI.git
    cd DoCA_GUI
    conda env create -f pardus.yml
    source activate pardus
    # edit settings.ini if necessary
    python main_gui.py

# Screenshot
![Screenshot](https://github.com/husmen/DoCA_GUI/blob/master/screenshot.png)

# Citing
This work has been published in IEEE Open Access. You can cite it in your publication:

    @ARTICLE{8768370,
    author={S. {Eken} and H. {Menhour} and K. {Köksal}},
    journal={IEEE Access},
    title={DoCA: A Content-Based Automatic Classification System Over Digital Documents},
    year={2019},
    volume={7},
    number={},
    pages={97996-98004},
    keywords={Task analysis;Feature extraction;Text analysis;Optical character recognition software;Libraries;Pattern matching;Organizations;Document analysis;document classification;OCR;video-audio analysis},
    doi={10.1109/ACCESS.2019.2930339},
    ISSN={2169-3536},
    month={},}
    
