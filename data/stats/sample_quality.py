#!  /usr/bin/python3
#----------------------------------------------------------
#   Name: sample_quality.py
#   Author: xyy15926
#   Created at: 2018-10-17 17:46:26
#   Updated at: 2018-10-17 17:49:40
#   Description: 
#----------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import weakref

DATA_PATH = "C:/Users/xyy15926/Downloads/data"

class Sampler:
    def __init__(self, df):
        self.df = df
        self.pop = {}
        for col in df.columns:
            self.pop[col] = None

    def _gen_sample_seq(self, n=100, least=0.01):
        '''generate n_i sequence
        generate sample quantity sequence with expenential function, 
        which helps with rarefying sequence at larger part
        
        Args:
            total: total of population
            n: length of the sequence, default 100
            least: the miniumn sample scale, defaut 0.01
    
        Return:
            list: sequence of n_i
        '''
        if hasattr(self, "spln_seq"):
            return self.spln_seq
        total = self.df.shape[1]
        if least >= 1:
            raise ValueError("samples scale be lighter than 1")
        sup = np.ceil(np.log(total))
        inf = np.ceil(np.log(total * least))
        seq = np.exp(np.linspace(inf, sup, n))
            # use np.exp to generate large-sparse seqences
        self.spl_n = seq
        return seq

    def _cal_col_kl(self, cols, spls):
        return np.sum(
            (self.pop[cols] - spls) *
            np.log(self.pop[cols] / spls)
        )
        
    def cal_quality(self, col, repeats=30):
        total = self.df.shape[1]
        spln_seq = _gen_sample_seq()
        kl_seq = []
        pplt_bins = np.histogram(self.df[col])
        for spln in spln_seq:
            kl_sum = 0
            for time in range(repeats):
                sample = df.loc(np.random.choice(rows, spln))
                
                
                

