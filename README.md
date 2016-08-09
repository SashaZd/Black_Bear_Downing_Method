# Black_Bear_Downing_Method

Key: 
	H_t = Total (Raw_Data chart)
	S1-S17 = Cols 1-17 of the Raw_Data chart
	A_t = Ratio of Aged to Total
	not_aged = Not Aged of the Raw_Data chart 


Steps: 
	### getRawUncorrected_AllData()
	Pulls the year, not_aged, totals and S1 to S17 from the raw_uncorrected data sheet in Excel



	- from Raw_Data ---> S1 - S17
		A_t = (H_t - not_aged)/H_t 
		corrected_for_sub_sampling = [Divide S1 to S17 by A_t (if no data, then 0)] ---> Round to whole number

		from the corrected_for_sub_sampl. data --->
			H = Keep S1, Keep S2, Collapse S3-S17 into S3+ 

			C_3plus[1] = For S_3plus average of the last 3 years 
			C_3plus[0] = For S_2 average for the last 3 years 

			
		M = C_3plus[0] / (C_3plus[0] + C_3plus[1])
		Z = C_3plus[1] / M

		N[-1][-1] = H[-1][-1] / (1 - Z / (Z + H[-1][-1] + H[-2][-1]) )
		N[-2][-1] = H[-2][-1] / (1 - Z / (Z + H[-1][-1] + H[-2][-1]) )
		
		<!-- For last column -->
		for all other i in N[i][-1]: 
			N[i][-1] = H[i][-1] / (1 - N[i+1][-1] / (N[i+1][-1] + H[i][-1] + H[i][-2]) )

		for i in N: #For 2nd last col 
			N[i][-2] = H[i][-2] / (1 - N[i][-1] / (N[i][-1] + H[i][-1] + H[i][-2]) )

		round(N)

		For all other cols (except last 2):
			for i, j in N that are empty: 
				N[i][j] = H[i][j] + N[i+1][j+1]







