# Transfer data from different instances 

Sometimes, partners collect real data using Kobo but forget to use the correct(production) instance of Kobo and instead use the training instance. Hope admin can transfer data from one instance to another using an open source python script available here at this link https://github.com/kobotoolbox/kobo-transfer  

The process is self-explanatory :   

 

From the source Kobo form with data on training, download the excel template of the project and recreate it on the destination production instance. Take notice of the uid of the two forms in the url.  

 Git clone the repo on your local machine and cd into it 

Install the required libraries with pip install -r requirements.txt 

Edit the config.json file where the source  and destination where the token is from the user authentication settings. The asset_uid is obtained by reading the  
```
{
    "src": { 
        "kc_url": "https://kc-hope.unitst.org", 
        "kf_url": "https://kf-hope.unitst.org", 
        "token": "bf084e1cpa56901d5za939c0764044c1ad11fcac", 
        "asset_uid": "a3SHPv3xGyGLL26Ujqn8jQ" 
    }, 
     "dest": { 
        "kc_url": "https://kc.hope.unicef.org", 
        "kf_url": "https://kf.hope.unicef.org", 
        "token": "51610683d430960e5bb065d30907470e697a968", 
        "asset_uid": "aTAzgN9e5NeizA24py4976" 
    } 
} 
```

Run python3 run.py, it should be Ok until the whole process is finished with successful messages. 
