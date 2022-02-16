# PEmimic
A python tool that allows you to mimic one executable file to another.
  
  
Installing dependencies:
```
pip install colorama
```
  
  
### Principle of operation:
---

* takes an executable file as input and analyzes it;
* identifies parts of the input file (rich header, sign, resources, etc);
* searches and analyzes files in the specified directory;
* transplants parts of the parsed files into the input file.

---

Due to the low speed of calculating the checksum in python, two versions of the [library](https://github.com/xoreaxecx/ChecksumDll)  
are included in the project (for [32 bit](https://github.com/xoreaxecx/PEmimic/blob/main/checksum32.dll) and [64 bit](https://github.com/xoreaxecx/PEmimic/blob/main/checksum64.dll) python interpreter). To force the  
script to use its own function, rename or remove the dll files from the directory.  

---

Before:  
![sample before](https://github.com/xoreaxecx/PEmimic/blob/main/sample_before.png)

After:  
![sample after](https://github.com/xoreaxecx/PEmimic/blob/main/sample_after.png)

---

Help:
```
usage: pemimic.py [-h] -in path/to/file [-out path/to/dir] [-sd search/dir/path] 
                  [-d depth] [-limit int] [-approx] [-rich] [-no-rich-fix] [-no-rich] 
                  [-timePE] [-no-timePE] [-sign] [-no-sign] [-vi] [-no-vi] [-res] [-no-res] 
                  [-dbg] [-no-dbg] [-ext .extension] [-no-checksum] [-no-names] [-with-donor]

By default the script includes all attributes for search.

optional arguments:
  -h, --help           show this help message and exit
  -in path/to/file     path to input file.
  -out path/to/dir     path to output dir. "-in" file path is default.
  -sd search/dir/path  path to directory to search. "C:\Windows" is default.
  -d depth             directory search depth. 5 is default.
  -limit int           required number of samples to create. all found variants is default.
  -approx              use of variants with incomplete match.
  -rich                adds Rich Header to the search.
  -no-rich-fix         disable modifying Rich Header values.
  -no-rich             removes Rich Header from the search.
  -timePE              adds TimeDateStamp from File Header to the search.
  -no-timePE           removes TimeDateStamp from the search.
  -sign                adds file sign to the search.
  -no-sign             removes file sign from the search.
  -vi                  adds VersionInfo to the search.
  -no-vi               removes VersionInfo from the search.
  -res                 adds resournces to the search.
  -no-res              removes resournces from the search.
  -dbg                 adds Debug Directory to the search.
  -no-dbg              removes Debug Directory from the search.
  -names               change section names as in the donor.
  -no-names            do not change section names.
  -ext .extension      file extensions to process. multiple "-ext" supported. Default: ".exe", ".dll".
  -no-checksum         do not update the checksum.
  -with-donor          creates copy of donor in the "-out" directory.
```

---
