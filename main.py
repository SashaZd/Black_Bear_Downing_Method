import os
import xlrd, xlwt
from copy import deepcopy
from xlutils.copy import copy


EXCEL_FILE_PATH = "downing.xls"
EXCEL_FILE_PATH_TEMP = "%s_temp.xls"%(EXCEL_FILE_PATH.split(".")[0])

class BlackBear: 

	def __init__(self):
		# Read only file 
		self.book = xlrd.open_workbook(EXCEL_FILE_PATH)

		# Write only file
		self.workbook = copy(self.book)
		# Remove all existing sheets except the Raw Data one
		self.workbook._Workbook__worksheets = [self.workbook._Workbook__worksheets[0]]
		self.workbook.save(EXCEL_FILE_PATH_TEMP)

		self.years, self.S, self.not_aged, self.H_t = self.getRawUncorrected_AllData()
		self.totals = {}


	def getRawUncorrected_AllData(self):
		sheet = self.book.sheet_by_name("Raw_Uncorrected")

		# Separately getting the years, not_aged, total from the raw data
		years, not_aged, total = [], [], []
		for row in range(1, sheet.nrows):
			years.append(int(sheet.cell(row,0).value))
			not_aged.append(sheet.cell(row,18).value)
			total.append(sheet.cell(row,19).value)

		# Getting S1 to S17 from the raw data
		S = [[0]*(sheet.ncols-3) for i in range(sheet.nrows-1)]
		for row in range(1,sheet.nrows):
			for col in range(1,sheet.ncols-2):
				if not sheet.cell(row, col).value:
					S[row-1][col-1] = 0
				else: 
					S[row-1][col-1] = sheet.cell(row, col).value

		return years, S, not_aged, total


	def getRawUncorrected_Cell(self, row, col):
		sheet = self.book.sheet_by_name("Raw_Uncorrected")
		if row <= sheet.nrows and col <= sheet.ncols:
			if not sheet.cell(row, col).value:
				return 0
			else: 
				return sheet.cell(row, col).value


	def findCollapsed(self, collapsed):
		# For every H_t find the A_t value
		# A_t = (H_t - not_aged)/H_t 
		A_t = []
		for index in range(len(self.H_t)):
			A_t.append((self.H_t[index] - self.not_aged[index])/self.H_t[index])

		# corrected_for_sub_sampling = [Divide S1 to S17 by A_t (if no data, then 0)] ---> Round to whole number
		corrected_for_sub_sampling = deepcopy(self.S)
		for i, row in enumerate(corrected_for_sub_sampling):
			for j, cell in enumerate(row):
				corrected_for_sub_sampling[i][j] = int(round(cell/A_t[i]))

		# H = Keep initial collapsed-1 columns, then collapse all others into last
		# To collapse a column, sum the remaining values from the cols into the collapsed column
		H = [[0]*collapsed for i in range(len(self.years))]
		for i, row in enumerate(corrected_for_sub_sampling):
			for j, cell in enumerate(row):
				if j < collapsed:
					H[i][j] = corrected_for_sub_sampling[i][j]
				else: 
					H[i][(collapsed-1)] += corrected_for_sub_sampling[i][j]

		# Calculate the C_collapsed value
		# C_collapsed[1] = For collapsed column, average of the last 3 years
		# C_collapsed[0] = For collapsed-1 column, average of the last 3 years
		C_collapsed = [0,0]
		
		for eachC in H[-3:]: 
			C_collapsed[-1] += eachC[-1]
			C_collapsed[-2] += eachC[-2]

		C_collapsed[0] /= float(3)
		C_collapsed[1] /= float(3)

		# Calculate, M = C_3plus[0] / (C_3plus[0] + C_3plus[1])
		M = C_collapsed[0] / (C_collapsed[0] + C_collapsed[1])

		# Calculate, Z = C_3plus[1] / M
		Z = int(round(C_collapsed[1] / M))

		return self.findAbundance(collapsed, Z, H)
		

	def findAbundance(self, collapsed, Z, H):
		N = [[0]*collapsed for i in range(len(self.years))]

		# Calculate, N[-1][-1] = H[-1][-1] / (1 - Z / (Z + H[-1][-1] + H[-1][-2]) )
		N[-1][-1] = int(round(float(H[-1][-1]) / (1 - Z / (Z + float(H[-1][-1]) + float(H[-1][-2])))))

		# Calculate, N[-1][-2] = H[-1][-2] / (1 - Z / (Z + H[-1][-1] + H[-1][-2]))
		N[-1][-2] = int(round(float(H[-1][-2]) / (1 - Z / (Z + float(H[-1][-1]) + float(H[-1][-2])))))

		# For the last row
		for j in range(len(N[-1])-2):
			N[-1][j] = H[-1][j]

		for i in range(len(self.years)-2, -1, -1):

			# For the last column
			# Calculate, N[i][-1] = H[i][-1] / (1 - N[i+1][-1] / (N[i+1][-1] + H[i][-1] + H[i][-2]) )
			N[i][-1] = int(round(float(H[i][-1]) / (1 - float(N[i+1][-1]) / (float(N[i+1][-1]) + float(H[i][-1]) + float(H[i][-2])))))

			# For the second last column
			# Calculate, N[i][-2] = H[i][-2] / (1 - N[i][-1] / (N[i][-1] + H[i][-1] + H[i][-2]) )
			N[i][-2] = int(round(float(H[i][-2]) / (1 - float(N[i+1][-1]) / (float(N[i+1][-1]) + float(H[i][-1]) + float(H[i][-2])))))

			# For all other columns
			# Calculate, N[i][j] = H[i][j] + N[i+1][j+1]
			for j in range(len(N[i])-3,-1,-1):
				N[i][j] = H[i][j] + N[i+1][j+1]

		return self.writeExcelSheet(collapsed, N)

	def writeExcelSheet(self, collapsed, N):
		sheet_name = "%d+ Collapsed"%(collapsed)

		sheet = self.workbook.add_sheet(sheet_name)

		# For Header Row
		h_style = xlwt.easyxf('font: bold 1')
		sheet.write(0,0, "Year", h_style)

		for col in range(collapsed): 
			head_title = ""
			if col+1 < collapsed:
				head_title = "Age Class %d"%(col+1)
			else: 
				head_title = "Age Class %d+"%(col+1)
			sheet.write(0, col+1, head_title, h_style)
		sheet.write(0, collapsed+1, "Total N", h_style)

		total = 0
		for index in range(0, len(self.years)):
			if self.years[index] not in self.totals:
				self.totals[self.years[index]] = 0

			sheet.write(index+1, 0, self.years[index])
			col = 0
			for col, value in enumerate(N[index]):
				sheet.write(index+1, col+1, value)
			total += sum(N[index])
			sheet.write(index+1, col+2, sum(N[index]))
			self.totals[self.years[index]] += sum(N[index])

		self.workbook.save(EXCEL_FILE_PATH_TEMP)


	def writeAverageN(self, n):
		sheet_name = "Average_Abundance"
		sheet = self.workbook.add_sheet(sheet_name)

		print self.totals

		# For Header Row
		h_style = xlwt.easyxf('font: bold 1')
		sheet.write(0,0, "Year", h_style)
		sheet.write(0,1, "Average N", h_style)

		for index, year in enumerate(self.years): 
			sheet.write(index+1, 0, year)
			avg_N = round(float(self.totals[year])/float(n))
			sheet.write(index+1, 1, avg_N)

		# avg_N = sum(self.totals)/len(self.totals)
		# sheet.write(1,0, avg_N)		

		self.workbook.save(EXCEL_FILE_PATH_TEMP)




bear = BlackBear()
collapse = [3,4,5]

for each in collapse: 
	bear.findCollapsed(each)

bear.writeAverageN(len(collapse))

os.remove(EXCEL_FILE_PATH)
os.rename(EXCEL_FILE_PATH_TEMP, EXCEL_FILE_PATH)










