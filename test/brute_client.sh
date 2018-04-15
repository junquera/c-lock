secret="$1"
while true; do 
    python3 client.py -s $secret; 
    echo; 
    sleep 0.2; 
done
