#!/bin/bash
P=$(grep path config.json | cut -d'"' -f4)
du -sh $P
