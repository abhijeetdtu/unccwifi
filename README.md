# Counting Campus Population Using Wi-Fi Logs

This project shows Wi-Fi is an effective means for counting campus population.

### Methodology

Wifi logs are made available via a shared network drive as zipped folders.
The zipped folders are moved to the processing computer, unzipped and parsed line by line.

Key log entries extracted from the logs are when a device associates with the access point. From the entry we use MAC address as the unique identifier for tracking movement and counts.

For each MAC address, each day is partitioned into 15 min slots and their location for that duration is calculated as the access point near which they spend most of the time. 

Once we have locations for each MAC, we can aggregate the information to get counts for each building for each time slot. Which is then aggregated to get campus wide numbers

### Overall Architecture for the Project

  <img src="https://user-images.githubusercontent.com/6872080/109057643-fcf1ee00-76af-11eb-8fd5-70a5dba928e2.png" width="60%"/>


### Using Information to Better Understand Movement Across Campus

1. Intra-day Numbers across campus
![image](https://user-images.githubusercontent.com/6872080/109058087-90c3ba00-76b0-11eb-859d-b00db81d46a1.png)
  
2. Building Wise Breakdown
![image](https://user-images.githubusercontent.com/6872080/109058229-b9e44a80-76b0-11eb-979a-d58e5bf3fd02.png)

3. Overall Trend through the Semester
![image](https://user-images.githubusercontent.com/6872080/109058367-e8622580-76b0-11eb-8dfc-10da1ea78163.png)
  
4. Contact Tracing
 ![image](https://user-images.githubusercontent.com/6872080/109058505-10ea1f80-76b1-11eb-9f99-dbfc4edb1a1e.png)


