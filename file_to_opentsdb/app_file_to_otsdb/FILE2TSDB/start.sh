service ssh start

bash -c "while ! curl -s "db":4242 > /dev/null; do\
 echo waiting for opentsdb; sleep 3;\
 done;"
bash ./this_run.sh

while true;
  do sleep 600;
done
