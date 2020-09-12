import csv
import pandas as pd
import numpy as np
import datetime as dt

"""
Module to initialize the value
"""

class Initialize():
    """
    IMPORTANT NOTES
        - Indicators to test are in the indicator.py file
        To improve the program, the indicators should be initialized in this module (initialize.py)
        - In entry_fibo, some improvements could be done... (see not in module entry_fibo.py)
    """

    def __init__(self,class_method=False):

        """ Initialize all the values here we want, and in the darkness bind them (well, not really bind,
        but anyway...)

        It is the values that are initialized here and used through the system


        Values to initialize
        --------------------

        Exit
        -----
            Extension
            ---------
            self.exit_ext_name : str
                name of the dictionary key to try to exit the market with Fibonnacci extensions
            self.exit_ext : bool
                tells the system if tries to exit (or not) the market using the largest extension as a reference.
                Ex : largest extension from preivous trend is 1, the system takes profit when it is 2.618 this size. So,
                when this value is reached, it takes the profit.
            self.profit_ext :float
                 % of the largest extension from previous trend that the system uses to exit the market to take profit
                 (default value is 2.618)
            self.stop_ext : float
                    % of the largest extension from previous trend that the system uses as a stop loss
                 (default value is 1.618)


        Return
        ------
        DataFrame list : Return a pandas dataframe `cls.series` with the none empty min or max value
            (if both are empty, nothing is returned. If one of
            them has a value, return the local min or max with index no)
        """


        #directory where our data are
        self.directory = '/Users/philippeostiguy/Desktop/Trading/Programmation_python/Trading/'

        #No need to change them
        self.date_name = 'Date'
        self.open_name = 'Open'
        self.high_name = 'High'
        self.low_name = 'Low'
        self.close_name = 'Close'
        self.adj_close_name = 'Adj Close'

        self.rel_low= 'min'
        self.rel_high = 'max'

        #Decide which data type we need in our testing
        self.__name_col={
            self.date_name:[],
            self.open_name:[],
            self.high_name:[],
            self.low_name:[],
            self.adj_close_name:[]
        }

        #Value we use by default for chart, extremum, etc.
        self.default_data=self.adj_close_name

        #Number of data (points) we check before and after to find a local min and max
        #By default, value is 6, but could be optimized between 5 and 7
        self.window = 6

        #Can't touch this
        self.name = pd.DataFrame(self.__name_col)
        self.date_ordinal_name = 'date_ordinal'
        self.point_data=0

        #PARAMS TO OPTIMIZE STARTS HERE
        #------------------------------


        # Set desired value to test the indicator
        self.date_debut = '2000-01-20'
        self.date_fin = '2008-04-20'
        self.asset = "MSFT"
        self.nb_data = 100  # nb of data on which data are tested
        self.buffer_extremum = self.nb_data/2  #when trying to enter in the market, we give a buffer trying to find the
                                              #the global max or min (half of self.nb_data by default)

        # Indicator value to trigger a signal
        self.r_square_level = .8
        self.min_data = 100  # nb of data between a signal

        #ENTRY
        #-----

        self.enter_bool = 'enter_bool' #same key name for all the exit strategy (located in different dictionary)

        self.enter_ext_name = 'enter_ext_name'
        self.enter_ext = 'enter_ext'
        self.stop_ext = 'stop_ext'

        self.enter_dict = {self.enter_ext_name :
                              {self.enter_bool : True,
                               self.enter_ext: 1, #could be .882 or .764
                               }
                          }


        #These params are conditions to stop trying entering the market if the current
        # price reach a % of the largest extension
        self.bol_st_ext = True  #Tells the system if it has to stop trying enter the market
        self.fst_cdt_ext = .618 #% of largest extension at which if the market reaches, the system
                            # stops trying to enter in the market
        self.sec_cdt_ext = .882 #% if the system triggers the first condition, then if it reaches this level in the
                                #opposite direction, the system brings the stop loss closer to the last peak or low (default
                                #value = adj. close

        # EXIT
        # -----

        self.exit_bool = 'exit_bool' #same key name for all the exit strategy (located in different dictionary)

        self.exit_ext_name = 'exit_ext_name'
        self.profit_ext = 'profit_ext'
        self.stop_ext = 'stop_ext'

        self.exit_dict = {self.exit_ext_name :
                              {self.exit_bool : True,
                               self.profit_ext : 2.618,
                               self.stop_ext : 1.618
                               }
                          }


        # Extension
        #-----------



        #No need to change them here- should not
        self.__name_tempor = "_tempo"
        self.__index_nb = 0

        if not class_method:
            self.series=self.ordinal_date()


    def reverse_csv(self):
        """
        fonction pour inverse l'ordre des lignes dans un csv (dernière devient la première), etc.
        la première ligne qui contient le nom des colonnes n'est pas touchée
        """

        with open(self.asset + ".csv") as fr, open(self.asset + self.__name_tempor + ".csv","w") as fw:
            cr = csv.reader(fr,delimiter=",")
            cw = csv.writer(fw,delimiter=",")
            cw.writerow(next(cr))  # write title as-is
            cw.writerows(reversed(list(cr)))


    def col_numb(self):
        """
        Determine column number based on header name in file + header we want to use (in initialize.py)
        """

        with open(self.asset + ".csv") as file:
            reader = csv.reader(file,delimiter=",")
            col_name = next(reader)

        for col_number in range(len(self.name.columns)):
            for col_number_ in range(len(col_name)):
                if self.name.columns[col_number]==col_name[col_number_]:
                    self.name.loc[self.__index_nb,self.name.columns[col_number]]=int(col_number_)
                    break

            if self.name[self.name.columns[col_number]].empty:
                raise Exception('Column name "{}" odoes not exist in database'.format(self.name.columns[col_number]))

    def __data_frame(self):
        """
         fonction pour retourner le csv sous forme de data frame selon le range désiré avec une colonne
         numérique pour les dates
         Le csv est un format standard Date,Open,High,Low,Close,Adj Close,Volume
         par défaut retourne le close seulement, mais on pourrait changer la possibilité avec usecols
         (4 est pour le close)
        """

        self.col_numb()
        __series = pd.read_csv(self.directory
                               + self.asset + '.csv', usecols=list(self.name.columns),
                               names=list(self.name.columns), header=0)
        self.series=__series.loc[(__series[self.date_name] >= self.date_debut) & (__series[self.date_name]
                                                                                        <= self.date_fin)]

        self.series=self.series.reset_index(drop=True)
        return self.series

    def ordinal_date(self):
        """
        dataframe pour ajouter une colonne avec les dates en numérique (pas timestamp), ce qui rend plus facile dans
        le calcul des indicateurs
        """
        
        self.series=self.__data_frame()
        self.series.Date=pd.to_datetime(self.series.Date)
        self.series[self.date_ordinal_name] = pd.to_datetime(self.series[self.date_name]).map(dt.datetime.toordinal)

        return self.series


    def sous_series_(self,point_data=0):
        """
        Retourne la serie selon la qté de données nécessaires pour la calcul de l'indicateur (itération)
        """

        self.sous_series=self.series.iloc[point_data:point_data+self.nb_data,:]

        if self.nb_data > len(self.series):
            raise Exception("Number of necessary data to calculate the indicator lower than available data")
        return self.sous_series