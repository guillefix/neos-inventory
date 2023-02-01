#!/bin/bash

until python3 server.py; do
	        echo "Server crashed; Restarting.." >&2
		        sleep 1
		done
