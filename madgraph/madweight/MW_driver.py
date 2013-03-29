#! /usr/bin/env python
################################################################################
# Copyright (c) 2012 The MadGraph Development team and Contributors             
#
# This file is a part of the MadGraph 5 project, an application which           
# automatically generates Feynman diagrams and matrix elements for arbitrary    
# high-energy processes in the Standard Model and beyond.                       
#
# It is subject to the MadGraph license which should accompany this             
# distribution.                                                                 
#                                                                               
# For more information, please visit: http://madgraph.phys.ucl.ac.be            
#                                                                               
################################################################################

import math
import os 
import sys
import subprocess

class RunningMW(object):

    def __init__(self, card_nb, first_event, nb_events, evt_file, mw_int_points, \
                 log_level, sample_nb):
        """store the data"""
        
        self.card_nb = int(card_nb)
        self.first_event = int(first_event)
        self.evtfile = evt_file
        self.nb_events = int(nb_events) # number of events to run
        self.mw_int_points = int(mw_int_points)
        self.log_level = log_level # weight | permutation | channel | iteration | full_log
        self.sample_nb = int(sample_nb)
        
        self.current_event = -1
        self.last_line = ''
        self.nb_line_by_event = 0
        
        restrict_path = evt_file.replace('verif','restrict')
        if os.path.exists(restrict_path):
            allow = map(int, open(restrict_path).read().split())
            self.allow_event = lambda x: int(x) in allow
        else:
            self.allow_event = lambda x: True
    
    def run(self):
        """Run the computation"""

        fsock = open('param.dat','w')
        fsock.writelines('param_card_'+str(self.card_nb)+'.dat\n')
        fsock.writelines(str(self.mw_int_points)+'\n')
        fsock.close()

        self.fsock = open('output_%s_%s.xml' % (self.card_nb, self.sample_nb), 'w')
        self.fsock.write('<card id=\'%s\'>' % self.card_nb)
        while self.get_next_event(create=True):
            
            subprocess.call('./comp_madweight', stdout=open('log.txt','w'))
            self.get_one_job_result()
        self.fsock.write('</card>')
    
    def get_next_event(self, create=True):
        """prepare the verif.lhco"""
    
        self.current_event +=1
        if self.current_event >= self.first_event + self.nb_events:
            return False

        if self.current_event == 0:
            self.input_file = open(self.evtfile)
            for i in range(self.first_event):
                self.get_next_event(False)
        
        evt = self.last_line
        self.last_line = '' 
        if evt:
            nb_line = 1
        else:
            nb_line = 0    
        for line in self.input_file:
            nb_line +=1
            if not self.nb_line_by_event:
                if len(line.split()) == 3 and nb_line > 1:
                    self.last_line = line
                    self.nb_line_by_event = nb_line -1
                    break
                else:
                    evt += line
            else:
                evt += line
            if nb_line == self.nb_line_by_event:
                break


        if not evt:
            return False    
        
        # now write the verif.lhco event:
        if create:
            try:
                self.lhco_number = int(evt.split('\n')[0].split()[1])
            except:
                print [evt]
                raise
            if self.allow_event(self.lhco_number):
                fsock = open('verif.lhco', 'w')
                fsock.write(evt)
                fsock.close()
            else:
                return self.get_next_event(create)
            
        return evt

    def get_one_job_result(self):
        """collect the associate result and update the final output file"""
        
        #fsock = open('output_%s_%s.xml' % (self.card_nb, self.sample_nb), 'a')
        
        weight = Weight(self.lhco_number, log_level)
        weight.get()
        weight.write(self.fsock)




class Weight(list):
    
    def __init__(self, lhco_number, log_level):
        self.log_level = log_level
        self.value = 0
        self.error = 0
        self.lhco_number = lhco_number
        list.__init__(self)
        self.log = ''        
    
    def get(self):
        
        #1. get the weight, error for this object
        try:
            ff=open('weights.out','r')
        except Exception:
            return
        for line in ff:
            line = line.strip()
            if not line:
                continue
            value, error = line.split()
            self.value = float(value)
            self.error = float(error)
            break
        os.remove('weights.out')
        #2.
        if self.log_level in ['permutation', 'channel', 'iteration', 'full']:
            self.get_details()

            
        #3 full log
        if self.log_level == 'full':
             self.log = open('log.txt').read()
        
    def get_details(self):
        """ """
        try:
            ff=open('details.out', 'r')
        except Exception:
            return
        current = {}

        for line in ff:
            split = line.split()
            perm_id, channel_id, value, error = split[:4]
            perm_order = split[4:]
            if perm_id in current:
                perm_obj = curent[perm_id]
            else:
                perm_obj = Permutation(perm_id, perm_order)
                current[perm_id] = perm_obj
                self.append(perm_obj)
            perm_obj.add(channel_id, value, error)
        
    def write(self, fsock):
        
        fsock.write('<event id=\'%s\' value=\'%s\' error=\'%s\'>' % \
                                    (self.lhco_number, self.value, self.error))
        if self.log_level in ['permutation', 'channel', 'iteration', 'full']:
            fsock.write('\n')
            for permutation in self:
                permutation.write(fsock, self.log_level)
        if 'full' == self.log_level:
            fsock.write('\n    <log>\n%s\n</log>\n' % self.log)#.replace('\n','\n<br></br>')) 
        fsock.write('</event>\n')
    
    def __str__(self):
        return 'Weight(%s)' % self.value
    
    def __repr__(self):
        return 'Weight(%s)' % self.value
            
class Permutation(dict):
    
    def __init__(self, perm_id, perm_order):
        self.value = 0
        self.error = 0
        self.id = perm_id
        self.perm_order = ' '.join(perm_order)
        
        dict.__init__(self)
    
    def add(self, channel_id, value, error):
        
        self[channel_id] = Channel(channel_id, value, error) 
                
    def write(self, fsock, log_level):
        """ """
        
        self.value, self.error = self.calculate_total()
        
        fsock.write('    <permutation id=\'%s\' value=\'%s\' error=\'%s\'>\n        %s' % \
                             (self.id, self.value, self.error, self.perm_order))
        
        if log_level in ['channel', 'iterations', 'full']:
            fsock.write('\n')
            for channel in self.values():
                channel.write(fsock, log_level)
                fsock.write('\n')
            fsock.write('    </permutation>\n')
        else:
            fsock.write('</permutation>\n')
            
    def calculate_total(self):
        
        total = 0
        error = 0
        for channel in self.values():
            total += channel.value
            error += channel.error**2
            
        return total, math.sqrt(error)        
    
class Channel(object):
    """ """
    
    def __init__(self, channel_id, value, error):
        """ """
        self.channel_id = channel_id
        self.value = float(value)
        self.error = float(error)
    
    def write(self, fsock, log_level):
        
        fsock.write('        <channel id=\'%s\' value=\'%s\' error=\'%s\'></channel>' %
                    (self.channel_id, self.value, self.error))

if __name__ == '__main__':
    
    card_nb, first_event, nb_event, evt, mw_int_points, log_level, sample_nb = sys.argv[1:]
    fsock = open('MW_input','w')
    fsock.write(' '.join(sys.argv[1:]))
    fsock.close()
    running_mw = RunningMW(card_nb, first_event, nb_event, evt, mw_int_points, log_level, sample_nb)
    running_mw.run()
