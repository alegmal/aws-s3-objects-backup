# objects_backup

Hi there!

This script runs on amazon S3 bucket (you specify its name in code) and backs up files in it older than X days (you specify X).

You specify format of wanted backup folders.

Things to note:
<br>
* Script does not do anything to original files (life cycle should handle it)
* Script skips folders with matching format specified in try of the code
* Before copiying a file, script checks if file already there to reduce traffic costs (checking is cheaper than copying)
* Be aware of 5 minutes limiti on amazon lambda
<br>
**EXAMPLE** of running script on 22/02/2017 with days specified as 1 days or older and format being %d-%m-%Y (day, month, year)
<br>
BEFORE:

1. Amazing.txt modified on 20/2/2017
2. Potatoe.jpg modified on 21/2/2017
4. 19-02-2017/inside_job.zip modified 19/02/2017

<br>
AFTER running script:

1. Amazing.txt modified on 20/2/2017
2. Potatoe.jpg modified on 21/2/2017
3. 19-02-2017/inside_job.zip modified 19/02/2017
<br>
4. 20-02-2017/Amazing.txt modified on 22/02/2017
5. 21-02-2017/Potatoe.jpg modified on 22/02/2017
