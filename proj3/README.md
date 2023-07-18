# COMS6111 - Project3

### A clear description of how to run your program.

run the command

    python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>

### A detailed description explaining: (a) which NYC Open Data data set(s) you used to generate the INTEGRATED-DATASET file; (b) what (high-level) procedure you used to map the original NYC Open Data data set(s) into your INTEGRATED-DATASET file; (c) what makes your choice of INTEGRATED-DATASET file compelling (in other words, justify your choice of NYC Open Data data set(s)). The explanation should be detailed enough to allow us to recreate your INTEGRATED-DATASET file exactly from scratch from the NYC Open Data site.

(a) We choose "NYPD Complaint Data Historic". 

(b) The original data contains 35 columns, and we only keep 8 columns: Suspect’s Sex, Suspect’s Race, Suspect’s Age Group, The name of the borough in which the incident occurred, Description of offense corresponding with key code, Date, Days of Week, Time of day. We got the first 6 columns directly from the original database, and for the last two, we map the Date columns to days of week and time of day. Then, we drop all empty data or Unknown data.

(c) We interpret the generated rules to identify patterns and insights, such as "Assaults are more likely to occur in Brooklyn than in Manhattan", or "Robberies are more likely to occur on Fridays than on Sundays". We use the generated association rules to make predictions and inform decision-making in areas such as law enforcement and public safety.

### A clear description of the internal design of your project

I implement the basic version of apriori algorithm. 

- Firstly, use the get_data() function to get data from the INTEGRATED-DATASET.csv file. Specifically, Each row of the data is presented by a set.

- Secondly, use the get_frequent_itemsets() function to get frequent itemsets by generating new sets from last generated sets with enough support.

- Lastly, use the get_rules() function to get the rules from each itemset with enough confidence.

### The command line specification of a compelling sample run

    python3 AR_main.py INTEGRATED-DATASET.csv 0.05 0.3

  From the result, we can see lots of associate rules regarding NYPD complaint.

For example:

    ['DANGEROUS DRUGS'] => ['M'] (Conf: 90.18%, Supp: 5.27%)

shows that male have higher rates of drug-related crime, and we also have a lot of examples like this which states the relationship of public safety.
