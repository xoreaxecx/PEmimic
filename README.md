# PEmimic
A PE morphing tool that allows you to mimic one executable file to another.
  
  
Installing dependencies:
```
pip install colorama capstone
```
  
---  
### Principle of operation:

* takes an executable file as input and analyzes it;
* identifies parts of the input file (rich header, sign, resources, etc);
* searches and analyzes files in the specified directory;
* transplants parts of the parsed files into the input file.

---

Due to the low speed of calculating the checksum in python, two versions of the [checksum library](https://github.com/xoreaxecx/ChecksumDll)  
are included in the project (for [32 bit](https://github.com/xoreaxecx/PEmimic/blob/main/checksum32.dll) and [64 bit](https://github.com/xoreaxecx/PEmimic/blob/main/checksum64.dll) python interpreter). To force the  
script to use its own function, rename or remove the dll files from the directory.  

---

### Example  
Replace or add all possible parts of the input file, shuffle its imports, fix the new Rich header and update the checksum. Get one sample output.  
```
python PEmimic.py -in "C:\tmp\hi_64.exe" -limit 1
```  
<details>
  <summary>Spoiler results</summary>

  Total before:  
  ![sample before](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_work_before.jpg)  
  
  Total after:  
  ![sample after](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_work_after.jpg)  
  
  ---
  
  Rich before:  
  ![rich_before](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_rich_before.jpg)  
  
  Rich after:  
  ![rich_after](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_rich_after.jpg)  
  
  ---
  
  Sign before:  
  ![sign_before](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_sign_before.jpg)  
  
  Sign after:  
  ![sign_after](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_sign_after.jpg)  
  
  ---
  
  VersionInfo before:  
  ![vi_before](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_vi_before.jpg)  
  
  VersionInfo after:  
  ![vi_after](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_vi_after.jpg)  
  
  ---
  
  Resources before:  
  ![res_before](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_res_before.jpg)  
  
  Resources after:  
  ![res_after](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_res_after.jpg)  
  
  ---
  
  DebugInfo before:  
  ![dbg_before](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_dbg_before.jpg)  
  
  DebugInfo after:  
  ![dbg_after](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_dbg_after.jpg)  
  
  ---
  
  Imports before:  
  ![imp_before](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_imp_before.jpg)  
  
  Imports after:  
  ![imp_after](https://github.com/xoreaxecx/PEmimic/blob/main/examples/pic_imp_after.jpg)  
  
</details>  

---

### Other examples:  
  
Replace or add the authenticode signature and Rich header without updating the checksum. Get one sample to the "C:\output" directory.  
```
python PEmimic.py -in "C:\tmp\hi_64.exe" -out "C:\output" -rich -sign -no-checksum -limit 1  
```
Replace or add all possible parts of the input file except version information, shuffle its imports, fix the new Rich header and update the checksum. Get one sample output.  
```
python PEmimic.py -in "C:\tmp\hi_64.exe" -no-vi -limit 1  
```
Replace or add only the Rich header from all possible donors from the "C:\donors" directory without fixing it. Update sample checksum.  
```
python PEmimic.py -in "C:\tmp\hi_64.exe" -sd "C:\donors" -rich -no-rich-fix  
```
Remove the version information, update the checksum and place in the "C:\cleared" directory.  
```
python PEmimic.py -in "C:\tmp\hi_64.exe" -out "C:\cleared" -rem-vi  
```
Remove Rich header, PE TimeDateStamp, authenticode signature, overlay, version information, debug information, update checksum and place in "C:\cleared" directory.  
```
python PEmimic.py -in "C:\tmp\hi_64.exe" -out "C:\cleared" -clear  
```

---

### Help:
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
  -sd search/dir/path  path to the donor or to the directory to search for a donor. "C:\Windows" is default.
  -d depth             directory search depth. 5 is default.
  -limit int           required number of samples to create. all found variants is default.
  -ext .extension      file extensions to process. multiple "-ext" supported. Default: ".exe" & ".dll".
  -with-donor          create copy of the donor in the "-out" directory.
  -approx              use of variants with incomplete match.
                       -------------------------------------------------------------------------------------
  -rich                add Rich Header to the search.
  -no-rich             remove Rich Header from the search.
  -rem-rich            remove Rich Header from the original file.
  -timePE              add TimeDateStamp from File Header to the search.
  -no-timePE           remove TimeDateStamp from the search.
  -rem-timePE          remove TimeDateStamp from the original file.
  -sign                add file sign to the search.
  -no-sign             remove file sign from the search.
  -rem-sign            remove file sign from the original file.
  -rem-ovl             remove overlay from the original file.
  -vi                  add VersionInfo to the search.
  -no-vi               remove VersionInfo from the search.
  -rem-vi              remove VersionInfo from the original file.
  -res                 add resournces to the search.
  -no-res              remove resournces from the search.
  -dbg                 add Debug Info to the search.
  -no-dbg              remove Debug Info from the search.
  -rem-dbg             remove Debug Info from the original file.
  -imp                 shuffle original PE imports.
  -no-imp              do not shuffle original PE imports.
  -names               change section names as in the donor.
  -no-names            do not change section names.
                       -------------------------------------------------------------------------------------
  -clear               combines all "-rem-*" commands into one.
  -no-rich-fix         disable modifying Rich Header values.
  -no-dbg-rsrc         do not add Debug Info to the resources if it is missing or does not fit in size.
  -no-checksum         do not update the checksum.
```

---
