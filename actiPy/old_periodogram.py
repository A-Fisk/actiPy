import pandas as pd
import numpy as np
from astropy.stats import LombScargle
import itertools

class split_by_period:
    
    '''
    split_by_period(data, period_list=24H * 6 by default)
    **kwarg = period_list
    Class to split dataframes up by internal period
    Takes DF with columns for PIR and rows for times
    Outputs list with each PIR separate
    DF in list is each day as one column, indexed to circadian time
    
    
    '''
    
    #init all variables
    def __init__(self, data, period_list=["24H" for i in range(6)]):
        #set period list and data to self variables
        self.data = data
        self.period_list = period_list
        
    #now put in our split function 
    def split_period(self):

        #set period list to passed self value
        Period_list = self.period_list
        
        #if any items are 0H, doesn't run
        #loop through items in list
        for loc, item in enumerate(Period_list):

            #if any = 0 do something
            if item == "0H 0T":
        
                #assign that number to be 24H (default)
                Period_list[loc] = "24H 0T"
        
        #set data 
        df = self.data
        
        #grab the index as a separate variable
        df_index = self.data.index

        #define start and end of index
        start, end = df_index[0], df_index[-1]

        #create list to append all the split dfs to later
        split_all_list = []

        #loop through PIRs and associated periods
        for PIRno, period in zip(df.columns, Period_list):

            #turn period into date_range 
            day_ends = pd.date_range(start=start, end=end, freq=period)

            #so what do we want to do now?
            #select each day in turn, can we put into a list and then concat together later?

            #define list to append to
            PIR_group_days_list = []

            #loop through start and end of the day_ends list
            for day_start, day_end in zip(day_ends, day_ends[1:]):

                #select just this part of the dataframe.
                day_data = df.loc[day_start:day_end, PIRno]
                #### problem as missing lastday

                #append into a list
                PIR_group_days_list.append(day_data)


            ##########################################    

            #can we put all values into list

            #list to append to later
            PIR_group_days_values = []

            #loop through each constructed day
            for day in PIR_group_days_list:

                #grab just the values by resetting index and taking first col
                values = day.reset_index().iloc[:,1]

                #append the values to a list
                PIR_group_days_values.append(values)


            #concat all together along columns
            #use value extracted list 
            PIR_grouped = pd.concat(PIR_group_days_values,
                                    axis=1
                                   )


            ##########################################    


            #now can we set index?

            #calculate the right frequency
            # 24 hours / number of rows
            base_freq = 86400/len(PIR_grouped)

            #grab seconds 
            secs = int(base_freq)

            #grab ms 
            ms = round((base_freq - secs) * 1000)
            
            #convert into useable format
            freq = str(secs) + "S " + str(ms) + "ms"

            #create timedelta range with right number of periods
            #freq calculated to go up to ~24 hours
            split_new_index = pd.timedelta_range(start = '0S',
                                                 periods = len(PIR_grouped),
                                                 freq = freq
                                                 )

            #set new index on dataframe
            PIR_grouped.set_index(split_new_index, inplace=True)

            split_all_list.append(PIR_grouped)
            
        self.split_completed_list = split_all_list
        
        
#Class for Analysis Equations

class Circadian_Analysis(split_by_period):
    '''
    Circadian_Analysis(label = '')
    label - string for type of light cycle 
    
    functions
    Enright_Periodogram(low, high) - low and high, numbers in hours for period to search for 
    
    LombScargle_Period(low, high) - low and high numbers to search for period between 
    
    Interdaily_Stability(period_list) - list of numbers to test IS at 
    
    Intraday_variability() - returns list of IV values 
    
    Light_percent_active_find() - finds light/dark percentage based on the LDR 
    
    '''
    
    #init with variables and inheritance
    #how do we deal with inheritance vs self done
    def __init__(self, data):
        split_by_period.__init__(self, data)
        self.data = data 
       
        
        #go through and check type
        for col in self.data.columns:

            #if object, remove! 
            if self.data.loc[:,col].dtype == 'O':
                data = data.drop(col, axis=1)
            
        self.data = data
        
        
    #define Periodogram function 
    def Enright_Periodogram(self, low, high):
        
        """
        Chi_Square(Period_list, data)
        Chi-Square periodogram class, function is Enright_Periodogram
        Requires input of low, and high values
        Returns df of Qp Values.
        Highly inefficient, not recommended.
        """
        
        #define data we are going to work with
        data = self.data

        #create list to append to of all tested periods
        Qp_group_list = []

        #create test_periods - don't even need df? yes we do
        test_periods=np.linspace(low,high,100)

        #loop through test periods 
        for test_period in test_periods:

            #expand into list 
            #Grabbing hours 
            hours = int(test_period)
            #calculating minutes 
            mins =   round(60 * round(test_period - hours, 2))
            #combining into list
            period = [str(hours) + "H " + str(mins) + "T"]*len(data.columns)

            #so first step is to split by test period.
            #only a single period passed so only done PIR 1 for now.
            split_by_test_period = split_by_period(data, period)

            #actually do the split
            split_by_test_period.split_period()

            #create list to hold IS
            Qp_single_list = []

            #loop through all PIRs
            for PIRno, split_list in zip(data.columns, split_by_test_period.split_completed_list):

                #next take the mean at each time point
                time_point_mean = split_list.mean(axis=1)

                #then take the variance of the mean
                period_variance = np.var(time_point_mean)

                #calculate N
                N = len(split_list)

                #take total variance 
                total_variance = np.var(data.loc[:,PIRno])

                #calculate the QP 
                Qp = (period_variance*N)/total_variance

                Qp_single_list.append(Qp)

            #next step is to do for multiple PIRs at once 
            #append into single list 

            Qp_group_list.append(Qp_single_list)


        self.Qp_DF = pd.DataFrame(Qp_group_list,
                                  index=test_periods,
                                  columns=data.columns[:len(period)])
 

    def LombScargle_period(self, low=20, high=30):
        
        '''
        LombScargle_period(low, high)
        
        low = in hours, shortest period to look for
        high = in hours, longest period to look for 
        
        My implementation of the LombScargle peiodogram
        Takes a Dataframe with columns=sensor no. and index = times.
        Returns Period_values Df with period and Pmax
        As well as Power_values for the test power statistics
        
        Much faster than my chi-square, gives the same values

        '''

        data = self.data

        a=data

        #first step is to define the period we are going to search over 
        #low and high period limits searching for put into 10s bins
        low_1=(low/24)/8640
        high_1=(high/24)/8640

        # convert into a range between that the algorithm will search through
        freq=np.linspace(low_1, high_1, 10000)

        #next define the sequence of observation times, just doing as a list
        observation_times=np.linspace(1, len(a), len(a))

        #now create a list to hold all the power arrays
        power_list=[]
        pmax_list=[]
        period_list=[]

        #now loop through each PIRno
        for PIR in a.columns:

            #select just that PIR
            observations = a.loc[:,PIR].values

            #do LombScargle on that PIR and put in the overall list
            power_temp= LombScargle(observation_times, observations).power(freq, method='auto')
            power_list.append(power_temp)

            #check if has actually produced something, if not put everything as 0
            if pd.isnull(power_temp[0])==True:
                pmax_list.append(0)
                period_list.append(0)

            #now to put the values into the useful lists
            else:

                #append pmax list with maximum power reached
                pmax_list.append(power_temp.max())

                #need to pull out the frequency value associated with the power_temp.max value
                #easiest to convert to temporary DataFrame and idxmax()
                hold=pd.DataFrame(power_temp, index=freq)
                period_list.append((1/hold.idxmax()[0])/360)

        #put these into DataFrame to make more useable. One for period and pmax values
        self.Period_values=pd.DataFrame([pmax_list, period_list],
                                        columns=a.columns,
                                        index=["Pmax","Period"])

        #another for all the power values associated with each test period
        self.Power_values=pd.DataFrame(power_list,
                                       index=a.columns,
                                       columns=((1/freq)/360)
                                      ).T.sort_index()
        
        
        #add in the "H" and make it a string so it's readable by my func
        # grab first two as hours, then complicated
        # take hours from total to = frac/hour, then multiply by 60 to get minutes
        # then round and take int to make whole integer number, add T 
        
        Period_list  = round(self.Period_values.xs("Period"), 2)
        
        self.LS_Period_list = [(str(int(item)) + "H "
                        + str(int(round((item - int(item))*60))) + "T"
                       ) for item in Period_list]

    
    #define IS function 
    def Interdaily_Stability(self, period_list):
        
        '''
        Interdaily sStability(period_list)
        Already using self.data
        IS = Variance by Period/Total Variance
        '''
        
        #set passed argument to be an attribute
        self.period_list = period_list
        
        #define period going to work with 
        period = self.period_list

        #define data we are going to work with
        data = self.data

        #so first step is to split by test period.
        #only a single period passed so only done PIR 1 for now.
        split_by_test_period = split_by_period(data, period)

        #actually do the split
        split_by_test_period.split_period()

        #create list to hold IS
        IS_list = []

        #loop through all PIRs
        for PIRno, split_list in zip(data.columns, split_by_test_period.split_completed_list):

            #next take the mean at each time point
            time_point_mean = split_list.mean(axis=1)

            #then take the variance of the mean
            period_variance = np.var(time_point_mean)

            #take total variance 
            total_variance = np.var(data.loc[:,PIRno])

            #divide the two! 
            IS = period_variance/total_variance
             
            #put into higher list
            IS_list.append(IS)

        #turn into series with correct index 
        IS_list = pd.Series(IS_list, index=data.columns[:len(period)])

        #add as an attribute
        self.IS_list = IS_list
        
        
    def Intraday_variability(self):
    
        data = self.data
    
        n=data.count()

        shift_minus_1 = data.shift(1)

        #sum of first squared derivatives
        first_square_sum=(((data[1:]-shift_minus_1[1:])**2).sum())

        #variance of data in total
        variance=data.var()

        # ratio of mean of first squared derivative to the  variance
        self.IV_List = first_square_sum / ((n-1)*variance)



    def Light_percent_active_find(self):
        
        '''
        Light_percent_active(self)
        returns list with just %active for each PIR
        '''

        
        df = self.data
        
        # sum activity in light phase 
        light_sum=df[df["LDR"]>10].sum()

        # sum activity in dark phase 
        dark_sum = df[df["LDR"]<10].sum()

        #calculate percentage
        percent_active_light=(light_sum/dark_sum)*100

        self.Percent_active_light = percent_active_light
        
        
        

#define class for creating mean_waveforms
#using inheritance of two other classes 
class Mean_Waveforms(Circadian_Analysis, split_by_period):
    
    
    '''
    Class method to generate mean and individual waveforms for activity based on 
    different periods requires datafram to be labelled into different periods

    Function for creating waveforms

    Inputs:
    Data - dataframe holding the time-series of data to be normalised
    **kwargs 
    Label_col = -1 default - float, which column contains labels
    baseline_label = "Baseline" - default - string
                                - which section want to use as the baseline for 
                                normalisation

    Returns:
    Individual mean waveforms - baseline, each period

    Group mean waveforms - baseline, each period

    Individual mean, group mean normalised waveforms - each period 
    '''
    
    #create init variables, only need data to create 
    def __init__(self, data):
        
        #call init on inherited classes 
        split_by_period.__init__(self, data)
        Circadian_Analysis.__init__(self, data)
        
        #create attribute of data 
        self.data = data 
        
    
    

    #define the function
    def waveform_define (self,
                         label_col = -1,
                         baseline_label = "Baseline",
                         LDR_label = "LDR"):
        
            #use the input data 
            data = self.data

            '''
            Class method to generate mean and individual waveforms for activity based on 
            different periods requires datafram to be labelled into different periods

            Function for creating waveforms

            Inputs:
            Data - dataframe holding the time-series of data to be normalised
            **kwargs 
            Label_col = -1 default - float, which column contains labels
            baseline_label = "Baseline" - default - string
                                        - which section want to use as the baseline for 
                                        normalisation

            Returns:
            Individual mean waveforms - baseline, each period

            Group mean waveforms - baseline, each period

            Individual mean, group mean normalised waveforms - each period 
            '''


            ###############
            # Step 1. Grab all the unique values in the light_period column 

            light_periods = data.iloc[:, label_col].unique()


            ##########################################################################################
            ##########################################################################################
            #Create dfs split by 24 (for baseline), and by internal period as determined by LS
            #for the other (non-baseline) periods
            #resample to 1 minute bins to ensure split by internal period and 24 hours have same length
            #save the means 
            ##########################################################################################
            ##########################################################################################

            #loop through all the different light periods and select those portions separately

            #list sto grab all the periods 
            sep_period_dfs = []
            #list to grab the strings of sections which contain enough data 
            light_periods_with_data = []

            #loop through all the unique values
            for period in light_periods:

                #slice by the light_period
                temp_df = data[data.iloc[:, label_col] == period]

                #make sure some data is there 
                if len(temp_df) > 10:
                    #put the sliced df into a list 
                    sep_period_dfs.append(temp_df)
                    #put the label for the sliced df into another list
                    light_periods_with_data.append(period)

            #select just the columns with numerical data to analyse
            #loop through all separate period_sections
            #list to hold
            sep_num_dfs = []

            #loop through dfs
            for df in sep_period_dfs:

                #slice just the columns with numerical data
                temp_num_df = df[df.columns[df.dtypes==np.float64]]
               
                
                #test whether the LDR label is in the axis, if not then ignore
                try:
                    #remove the LDR column from calculations 
                    temp_num_df_1 = temp_num_df.drop(LDR_label, axis=1)
                    
                except ValueError:
                    temp_num_df_1 = temp_num_df

                #append to list
                sep_num_dfs.append(temp_num_df_1)

            #next create class objects for each sep_df

            #list to hold class instances 
            split_24_class_list = []
            split_LS_class_list = []

            #loop through the dfs
            for df in sep_num_dfs:

                #create object for 24 hour split
                temp_object = split_by_period(df)

                #call split function 
                temp_object.split_period()

                #append to the 24 hour class list 
                split_24_class_list.append(temp_object)

                #create temporary analysis object
                temp_analysis_class = Circadian_Analysis(df)

                #call the LS function
                temp_analysis_class.LombScargle_period()

                #now create an object of split with LS period_list 
                temp_split_class =  split_by_period(
                                                df,
                                                period_list=temp_analysis_class.LS_Period_list[:-1]
                                            )
                #call the split function
                temp_split_class.split_period()

                #append object to LS class list
                split_LS_class_list.append(temp_split_class)


            #next step is to grab the mean waveforms of each day and section

            #loop through all the dfs in both lists - nested loop of lists
            for temp_class in itertools.chain(split_24_class_list, split_LS_class_list):

                #create new class attribute of a list 
                temp_class.resampled_split_list = []

                #create new class attribute to hold means 
                temp_class.resampled_split_mean = []

                #loop through all the dfs in the class:
                for df in temp_class.split_completed_list:

                    #resample and save as temporary name
                    hold_df = df.resample("T").mean()

                    #grab means 
                    hold_means = hold_df.mean(axis=1)

                    #append into new class attribute
                    temp_class.resampled_split_list.append(hold_df)

                    #append means into new class attribute
                    temp_class.resampled_split_mean.append(hold_means)


            #
            ##########################################################################################
            ##########################################################################################
            #Now to create the normalised waveforms, we will define the baseline section
            #then use all the disrupted parts and take the baseline from them. 
            ##########################################################################################
            ##########################################################################################

            #grab the baseline part 

            #select the index from unique vals and label
            baseline_index = light_periods_with_data.index(baseline_label)

            #select just the baseline based on the label index 
            baseline_dfs = split_24_class_list[baseline_index]



            # have inbuilt control of baseline = 0 
            #slight differences due to the tiny variations in period from the LS
            #and then resampling as a mean value

            #loop through each object in list and remove baseline

            #loop through all the classes 
            for temp_class in split_LS_class_list:

                #create new attribute to hold normalised data 
                temp_class.normalised_day = []

                #loop through each baseline and df
                for baseline, norm_day in zip(baseline_dfs.resampled_split_mean,
                                              temp_class.resampled_split_mean):

                    #take disruption from the baseline 
                    normalised_day = norm_day - baseline

                    temp_class.normalised_day.append(normalised_day)

                #run through the individual means and create a group mean
                #grab the individual means
                temp_arr = temp_class.resampled_split_mean

                #create the mean out of those values
                temp_mean = np.mean(temp_arr, axis=0)

                #create Series again so easier to plot and interpret
                #use original index 
                temp_series = pd.Series(temp_mean, index=temp_arr[0].index)

                #create new class attribute
                temp_class.group_mean_period = temp_series



            #now go through and create group means for all

            #loop through all classes required
            for temp_class in split_LS_class_list:

                #grab the data 
                temp_arr=temp_class.normalised_day

                #calculate mean
                temp_mean = np.mean(temp_arr, axis=0)

                #create Series out of array, using index of original series
                #index should be the same for all after resampling into 1 
                #minute bins.
                temp_series = pd.Series(temp_mean, index=temp_arr[0].index)

                #create new class attribute
                temp_class.norm_day_group_mean = temp_series


            #now do the same for baseline_dfs

            #grab the data 
            temp_arr=baseline_dfs.resampled_split_mean

            #calculate mean
            temp_mean = np.mean(temp_arr, axis=0)

            #create Series out of array, using index of original series
            temp_series = pd.Series(temp_mean, index=temp_arr[0].index)

            #create new class attribute
            baseline_dfs.baseline_group_mean = temp_series


            #lists for returns 
            #use list comprehension to do 
            self.individual_means_24 = [x.resampled_split_mean for
                                   x in split_24_class_list]

            self.individual_means_LS = [x.resampled_split_mean for
                                   x in split_LS_class_list]

            self.group_mean_baseline = baseline_dfs.baseline_group_mean

            self.group_mean_periods = [x.group_mean_period for 
                                 x in split_LS_class_list]

            self.individual_mean_normalised = [x.normalised_day for 
                                         x in split_LS_class_list]

            self.group_mean_normalised = [x.norm_day_group_mean for 
                                    x in split_LS_class_list]

