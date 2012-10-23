################################################################################
#
# Copyright (c) 2009 The MadGraph Development team and Contributors
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

"""Unit test library for the spin correlated decay routines
in the madspin directory"""

import sys
import os
import string
import shutil
pjoin = os.path.join

from subprocess import Popen, PIPE, STDOUT

root_path = os.path.split(os.path.dirname(os.path.realpath( __file__ )))[0]
sys.path.insert(0, os.path.join(root_path,'..','..'))

import tests.unit_tests as unittest
import madgraph.interface.master_interface as Cmd

import copy
import array

import madgraph.core.base_objects as MG
import madgraph.various.misc as misc
import MadSpin.decay as madspin 

from madgraph import MG5DIR
#
class TestBanner(unittest.TestCase):
    """Test class for the reading of the banner"""

    def test_extract_info(self):
        """Test that the banner is read properly"""

        banner=pjoin(MG5DIR, 'tests', 'input_files', 'tt_banner.txt')
        inputfile = open(banner, 'r')
        mybanner=madspin.Banner(inputfile)
        mybanner.ReadBannerFromFile()
        process=mybanner.proc["generate"]
        model=mybanner.proc["model"]
        self.assertEqual(process,"p p > t t~ @1")
        self.assertEqual(model,"sm")

class Testtopo(unittest.TestCase):
    """Test the extraction of the topologies for the undecayed process"""

    def test_topottx(self):

        path_for_me=pjoin(MG5DIR, 'tests','unit_tests','madspin')
        shutil.copyfile(pjoin(MG5DIR, 'tests','input_files','param_card_sm.dat'),\
		pjoin(path_for_me,'param_card.dat'))
        curr_dir=os.getcwd()
        os.chdir('/tmp')
        temp_dir=os.getcwd()
        mgcmd=Cmd.MasterCmd()
        process_prod=" g g > t t~ "
        process_full=process_prod+", ( t > b w+ , w+ > mu+ vm ), "
        process_full+="( t~ > b~ w- , w- > mu- vm~ ) "
        decay_tools=madspin.decay_misc()
        topo=decay_tools.generate_fortran_me([process_prod],"sm",0, mgcmd, path_for_me)
        decay_tools.generate_fortran_me([process_full],"sm", 1,mgcmd, path_for_me)
	decay_name, prod_name = decay_tools.compile_fortran_me(path_for_me)


        topo_test={1: {'branchings': [{'index_propa': -1, 'type': 's',\
                'index_d2': 3, 'index_d1': 4}], 'get_id': {}, 'get_momentum': {}, \
                'get_mass2': {}}, 2: {'branchings': [{'index_propa': -1, 'type': 't', \
                'index_d2': 3, 'index_d1': 1}, {'index_propa': -2, 'type': 't', 'index_d2': 4,\
                 'index_d1': -1}], 'get_id': {}, 'get_momentum': {}, 'get_mass2': {}}, \
                   3: {'branchings': [{'index_propa': -1, 'type': 't', 'index_d2': 4, \
                'index_d1': 1}, {'index_propa': -2, 'type': 't', 'index_d2': 3, 'index_d1': -1}],\
                 'get_id': {}, 'get_momentum': {}, 'get_mass2': {}}}
        
        self.assertEqual(topo,topo_test)
  

        p_string='0.5000000E+03  0.0000000E+00  0.0000000E+00  0.5000000E+03  \n'
        p_string+='0.5000000E+03  0.0000000E+00  0.0000000E+00 -0.5000000E+03 \n'
        p_string+='0.5000000E+03  0.1040730E+03  0.4173556E+03 -0.1872274E+03 \n'
        p_string+='0.5000000E+03 -0.1040730E+03 -0.4173556E+03  0.1872274E+03 \n'        

       
        os.chdir(pjoin(path_for_me,'production_me','SubProcesses',prod_name))
        executable_prod="./check"
        external = Popen(executable_prod, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        prod_values=external.communicate(input=p_string)[0] 
        prod_values=prod_values.split()
        prod_values_test=['0.59366146660637686', '7.5713552297679376', '12.386583104018380', '34.882849897228873']
        self.assertEqual(prod_values,prod_values_test)               
        os.chdir(temp_dir)
        
        p_string='0.5000000E+03  0.0000000E+00  0.0000000E+00  0.5000000E+03 \n'
        p_string+='0.5000000E+03  0.0000000E+00  0.0000000E+00 -0.5000000E+03 \n'
        p_string+='0.8564677E+02 -0.8220633E+01  0.3615807E+02 -0.7706033E+02 \n'
        p_string+='0.1814001E+03 -0.5785084E+02 -0.1718366E+03 -0.5610972E+01 \n'
        p_string+='0.8283621E+02 -0.6589913E+02 -0.4988733E+02  0.5513262E+01 \n'
        p_string+='0.3814391E+03  0.1901552E+03  0.2919968E+03 -0.1550888E+03 \n'
        p_string+='0.5422284E+02 -0.3112810E+02 -0.7926714E+01  0.4368438E+02\n'
        p_string+='0.2144550E+03 -0.2705652E+02 -0.9850424E+02  0.1885624E+03\n'

        os.chdir(pjoin(path_for_me,'full_me','SubProcesses',decay_name))
        executable_decay="./check"
        external = Popen(executable_decay, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        decay_value=external.communicate(input=p_string)[0] 
        decay_value=decay_value.split()
        decay_value_test=['3.8420345719455465E-017']
        for i in range(len(decay_value)): 
            self.assertAlmostEqual(eval(decay_value[i]),eval(decay_value_test[i]))
        os.chdir(curr_dir)
        shutil.rmtree(pjoin(path_for_me,'production_me'))
        shutil.rmtree(pjoin(path_for_me,'full_me'))
        os.remove(pjoin(path_for_me,'param_card.dat'))
        os.remove(pjoin(path_for_me,'parameters.inc'))

        
