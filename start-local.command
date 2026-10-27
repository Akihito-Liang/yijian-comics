#!/bin/zsh
cd "${0:A:h}"
print '漫画书架：http://127.0.0.1:8766/'
python3 -m http.server 8766 --bind 127.0.0.1
