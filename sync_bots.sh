#!/bin/bash
cd /sdcard/BOTS-CLEITI6966HUBS
cp -r /sdcard/download/bots2/* .
git add .
git commit -m "Transferindo arquivos do bots2"
git push origin main

