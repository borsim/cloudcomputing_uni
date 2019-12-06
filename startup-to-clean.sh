#!/bin/bash
read -p "Enter number of difficulty bits [default: 25]: " diffb
diffb=${diffb:-25}
echo "$diffb"
read -p "Enter number of vms to start [default: 1]: " vmnum
vmnum=${vmnum:-1}
echo "$vmnum"
read -p "Enter secret message to hash [default: deadbeef1234]: " secr
secr=${secr:-deadbeef1234}
echo "$secr"
read -p "Enter the safety margin - how many times above the expected value should nonces be checked [default: 2]: " prob
prob=${prob:-2}
echo "$prob"
read -p "Would you like a timeout scram y/n [default: n]?" tmoutbool
tmoutbool=${tmoutbool:-n}
echo "$tmoutbool"
if [ "$tmoutbool" = "y" ]; then
  read -p -r "Set time for timeout scram [default: 180s]: " tmoutval
  tmoutval=${tmoutval:-180}
  echo "$tmoutval"
fi

read -p -r "Would you like a spendout scram y/n [default: n]?" spoutbool
spoutbool=${spoutbool:-n}
echo "$spoutbool"
if [ "$spoutbool" = "y" ]; then
  read -p -r "Set time for spendout scram [default: 0.1 dollar]: " spoutval
  spoutval=${spoutval:-0.1}
  echo "$spoutval"
fi
NANO_COST_PER_HOUR=0.0052
RESERVATION_COST_PER_HOUR=NANO_COST_PER_HOUR*vmnum
RESERVATION_COST_PER_SECOND=RESERVATION_COST_PER_HOUR/3600
SPENDOUT_TIME=spoutval/RESERVATION_COST_PER_SECOND

SECONDS=0
python3 create_aws_environment.py "$vmnum"
sleep 10
python3 handle_sqs.py "$diffb" "$secr" "$vmnum" "$prob" &
PROC_ID=$!
scrumNotTriggered=true
processLive=true
while ((processLive)) && (( scrumNotTriggered )); do
    #processLive=$(kill -0 "$PROC_ID" 2>/dev/null)
    processLive=$(kill -0 $PROC_ID)
    if [ "$tmoutbool" ] && [ $SECONDS -gt "$tmoutval" ]; then
      scrumNotTriggered=false
    fi
    if [ "$spoutbool" ] && [ $SECONDS -gt "$SPENDOUT_TIME" ]; then
      scrumNotTriggered=false
    fi
done
#sleep 30
#python3 clean_aws_environment.py