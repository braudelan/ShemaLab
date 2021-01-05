#!/bin/bash


# String we want to analyze
var=$1
echo "this is the string we are going to analyze:"
echo "$var"
echo "  "

# Regular expression we'll use to analyze the string
regex=$2
echo "This is the regex we will use to try analyzing the text:"
echo $regex
echo "  "

# Perform regex check and determine match / no match
if [[ $var =~ $regex ]]
then
        echo "matched the following text:"
            echo ${BASH_REMATCH[0]}
        else
                echo "didn't match!"
            fi
