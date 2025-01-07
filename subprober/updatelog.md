# SubProber V3.0.1 Updates

### Whats Changed

   - **Fixed the issue in response html content parsing**
   - **Handled the parser exception, if `lxml` parser is missed then automatically errors handled**
   - **Improved the requirements of packages to install missing pacakges**
  
### Information:

**If any of our users faced empty titles in output then indicates that `lxml` and `bs4` packages are not installed properly, We request that users to install the missing packages with the following command**

```
pip install -U beautifulsoup4 lxml bs4 --break-system-packages
```

