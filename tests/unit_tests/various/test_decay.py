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
"""Unit test Library for the objects in decay module."""
from __future__ import division

import copy
import os
import sys
import time
import math
import cmath

import tests.unit_tests as unittest
import madgraph.core.base_objects as base_objects
import models.import_ufo as import_ufo
import models.model_reader as model_reader
import madgraph.iolibs.save_model as save_model
import madgraph.iolibs.drawing_eps as drawing_eps
import madgraph.iolibs.import_v4 as import_v4
from madgraph import MG5DIR
import decay.decay_objects as decay_objects
import tests.input_files.import_vertexlist as import_vertexlist


_file_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]

#===============================================================================
# DecayParticleTest
#===============================================================================
class Test_DecayParticle(unittest.TestCase):
    """Test class for the DecayParticle object"""

    mydict = {}
    mypart = None
    sm_path = import_ufo.find_ufo_path('sm')
    my_testmodel_base = import_ufo.import_model(sm_path)
    my_2bodyvertexlist = base_objects.VertexList()
    my_3bodyvertexlist = base_objects.VertexList()
    my_2bodyvertexlist_wrongini = base_objects.VertexList()
    my_3bodyvertexlist_wrongini = base_objects.VertexList()

    def setUp(self):

        #Import a model from my_testmodel
        self.my_testmodel = decay_objects.DecayModel(self.my_testmodel_base, True)
        param_path = os.path.join(_file_path,'../input_files/param_card_sm.dat')
        self.my_testmodel.read_param_card(param_path)
        #print len(self.my_testmodel_base.get('interactions')), len(self.my_testmodel.get('interactions'))

        # Simplify the model
        particles = self.my_testmodel.get('particles')
        #print 'Here\n', self.my_testmodel['particles']
        interactions = self.my_testmodel.get('interactions')
        inter_list = copy.copy(interactions)
        no_want_pid = [1, 2, 3, 4, 13, 14, 15, 16, 21, 23]
        for pid in no_want_pid:
            particles.remove(self.my_testmodel.get_particle(pid))

        for inter in inter_list:
            if any([p.get('pdg_code') in no_want_pid for p in \
                        inter.get('particles')]):
                interactions.remove(inter)

        # Set a new name
        self.my_testmodel.set('name', 'my_smallsm')
        self.my_testmodel.set('particles', particles)
        self.my_testmodel.set('interactions', interactions)

        #Setup the vertexlist for my_testmodel and save this model
        import_vertexlist.make_vertexlist(self.my_testmodel)
        #save_model.save_model(os.path.join(MG5DIR, 'tests/input_files', self.my_testmodel['name']), self.my_testmodel)

        # Setup vertexlist for test
        full_vertexlist = import_vertexlist.full_vertexlist

        self.my_2bodyvertexlist = base_objects.VertexList([
                full_vertexlist[(41, 24)], full_vertexlist[(63, 24)]])
        fake_vertex = copy.deepcopy(full_vertexlist[(41, 24)])
        fake_vertex['legs'].append(base_objects.Leg({'id':22}))
        fake_vertex2 = copy.deepcopy(full_vertexlist[(63, 24)])
        fake_vertex2['legs'].append(base_objects.Leg({'id': 11}))
        self.my_3bodyvertexlist = base_objects.VertexList([
                fake_vertex, fake_vertex2])

        self.my_2bodyvertexlist_wrongini = base_objects.VertexList([
                full_vertexlist[(50, -24)], full_vertexlist[(41, -6)]])
        fake_vertex3 = copy.deepcopy(full_vertexlist[(50, -24 )])
        fake_vertex3['legs'].append(base_objects.Leg({'id':12}))
        self.my_3bodyvertexlist_wrongini = base_objects.VertexList([
                fake_vertex3])

        fake_vertex4 = copy.deepcopy(full_vertexlist[(41, 24 )])
        fake_vertex4['legs'].append(base_objects.Leg({'id':24}))
        self.my_3bodyvertexlist_radiactive = base_objects.VertexList([
                fake_vertex4])
        
        self.mydict = {'name':'w+',
                      'antiname':'w-',
                      'spin':3,
                      'color':1,
                      'mass':'MW',
                      'width':'WW',
                      'texname':'W+',
                      'antitexname':'W-',
                      'line':'wavy',
                      'charge': 1.00,
                      'pdg_code': 24,
                      'propagating':True,
                      'is_part': True,
                      'self_antipart': False,
                       # decay_vertexlist must have two lists, one for on-shell,
                       # one for off-shell
                      'decay_vertexlist': {\
                           (2, False): self.my_2bodyvertexlist,
                           (2, True) : self.my_2bodyvertexlist,
                           (3, False): self.my_3bodyvertexlist,
                           (3, True) : self.my_3bodyvertexlist},
                       'is_stable': False,
                       'vertexlist_found': False,
                       'max_vertexorder': 0,
                       'apx_decaywidth': 0.,
                       'apx_decaywidth_err': 0.
                       }

        self.mypart = decay_objects.DecayParticle(self.mydict)



    def test_setgetinit_correct(self):
        """Test __init__, get, and set functions of DecayParticle
           mypart should give the dict as my dict
        """
        
        mypart2 = decay_objects.DecayParticle()

        #To avoid the error raised when setting the vertexlist
        #because of the wrong particle id.
        mypart2.set('pdg_code', self.mydict['pdg_code'])
        for key in self.mydict:
            #Test for the __init__ assign values as mydict
            self.assertEqual(self.mydict[key], self.mypart[key])

            #Test the set function
            mypart2.set(key, self.mydict[key])
            #print key, mypart2[key]
            self.assertEqual(mypart2[key], self.mydict[key])

        for key in self.mypart:
            #Test the get function return the value as in mypart
            # Note: for apx_decaywidth_err, .get will call 
            # estimate_decaywidth_error to recalculate
            # so the result will be one for zero width
            self.assertEqual(self.mypart.get(key), self.mypart[key])


    def test_setgetinit_exceptions(self):
        """Test the exceptions raised by __init__, get, and set."""
        
        myNondict = 1.
        myWrongdict = self.mydict
        myWrongdict['Wrongkey'] = 'wrongvalue'

        #Test __init__
        self.assertRaises(AssertionError, decay_objects.DecayParticle,myNondict)
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          decay_objects.DecayParticle, myWrongdict)
                          
        #Test get
        self.assertRaises(AssertionError, self.mypart.get, myNondict)

        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          self.mypart.get, 'WrongParameter')
                          
        #Test set
        self.assertRaises(AssertionError, self.mypart.set, myNondict, 1)

        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          self.mypart.set, 'WrongParameter', 1)

    def test_values_for_prop(self):
        """Test filters for DecayParticle properties."""

        test_values = [
                       {'prop':'name',
                        'right_list':['h', 'e+', 'e-', 'u~',
                                      'k++', 'k--', 'T', 'u+~'],
                        'wrong_list':['', 'x ', 'e?', '{}', '9x', 'd~3', 'd+g',
                                      'u~+', 'u~~']},
                       {'prop':'spin',
                        'right_list':[1, 2, 3, 4, 5],
                        'wrong_list':[-1, 0, 'a', 6]},
                       {'prop':'color',
                        'right_list':[1, 3, 6, 8],
                        'wrong_list':[2, 0, 'a', 23, -1, -3, -6]},
                       {'prop':'mass',
                        'right_list':['me', 'zero', 'mm2'],
                        'wrong_list':['m+', '', ' ', 'm~']},
                       {'prop':'pdg_code',
                        #The last pdg_code must be 6 to be consistent with
                        #vertexlist
                        'right_list':[1, 12, 80000000, -1, 24],
                        'wrong_list':[1.2, 'a']},
                       {'prop':'line',
                        'right_list':['straight', 'wavy', 'curly', 'dashed'],
                        'wrong_list':[-1, 'wrong']},
                       {'prop':'charge',
                        'right_list':[1., -1., -2. / 3., 0.],
                        'wrong_list':[1, 'a']},
                       {'prop':'propagating',
                        'right_list':[True, False],
                        'wrong_list':[1, 'a', 'true', None]},
                       {'prop':'is_part',
                        #Restore the is_part to be consistent with vertexlist
                        'right_list':[True, False, True],
                        'wrong_list':[1, 'a', 'true', None]},
                       {'prop':'self_antipart',
                        'right_list':[True, False],
                        'wrong_list':[1, 'a', 'true', None]},
                       {'prop':'is_stable',
                        'right_list':[True, False],
                        'wrong_list':[1, 'a', 'true', None]},
                       {'prop':'vertexlist_found',
                        'right_list':[True, False],
                        'wrong_list':[1, 'a', 'true', None]},
                       {'prop':'max_vertexorder',
                        'right_list':[3, 4, 0],
                        'wrong_list':['a', 'true', None]},
                       {'prop':'apx_decaywidth',
                        'right_list':[3., 4.5, 0.2],
                        'wrong_list':['a', [12,2], None]},
                       {'prop':'apx_decaywidth_err',
                        'right_list':[3., 4.5, 0.2],
                        'wrong_list':['a', [12,2], None]},
                       {'prop':'2body_massdiff',
                        'right_list':[3., 4.5, 0.2],
                        'wrong_list':['a', [12,2], None]},
                       {'prop':'decay_vertexlist',
                        'right_list':[{(2, False):self.my_2bodyvertexlist,
                                       (2, True) :self.my_2bodyvertexlist,
                                       (3, False):self.my_3bodyvertexlist,
                                       (3, True) :self.my_3bodyvertexlist}],
                        'wrong_list':[1, 
                                      {'a': self.my_2bodyvertexlist},
                                      {(24, 2, False): self.my_2bodyvertexlist},
                                      {(5, True):self.my_2bodyvertexlist,
                                       (5, False):self.my_3bodyvertexlist},
                                      {(2, 'Not bool'):self.my_2bodyvertexlist},
                                      {(2, False): 'hey'},
                                      {(2, False): self.my_2bodyvertexlist, 
                                       (2, True) : self.my_3bodyvertexlist},
                                      {(2, False):self.my_2bodyvertexlist_wrongini, 
                                       (2, True): self.my_2bodyvertexlist,
                                       (3, False):self.my_3bodyvertexlist,
                                       (3, True): self.my_3bodyvertexlist},
                                      {(2, False):self.my_2bodyvertexlist, 
                                       (2, True): self.my_2bodyvertexlist,
                                       (3, False):self.my_3bodyvertexlist_wrongini,
                                       (3, True): self.my_3bodyvertexlist},
                                      {(2, False):self.my_2bodyvertexlist, 
                                       (2, True): self.my_2bodyvertexlist,
                                       (3, False):self.my_3bodyvertexlist,
                                       (3, True): self.my_3bodyvertexlist_radiactive}
                                      
                                     ]},
                       ]

        temp_part = self.mypart

        for test in test_values:
            for x in test['right_list']:
                self.assertTrue(temp_part.set(test['prop'], x))
            for x in test['wrong_list']:
                self.assertFalse(temp_part.set(test['prop'], x))

    def test_getsetvertexlist_correct(self):
        """Test the get and set for vertexlist is correct"""
        temp_part = self.mypart
        #Reset the off-shell '2_body_decay_vertexlist'
        templist = self.my_2bodyvertexlist
        templist.extend(templist)
        temp_part.set_vertexlist(2, False, templist)
        #Test for equality from get_vertexlist
        self.assertEqual(temp_part.get_vertexlist(2, False), \
                             templist)

        #Reset the on-shell '2_body_decay_vertexlist'
        templist.extend(templist)
        temp_part.set_vertexlist(2, True, templist)
        #Test for equality from get_vertexlist
        self.assertEqual(temp_part.get_vertexlist(2, True), \
                             templist)

        #Reset the off-shell '3_body_decay_vertexlist'
        templist = self.my_3bodyvertexlist
        templist.extend(templist)
        temp_part.set_vertexlist(3, False, templist)
        #Test for equality from get_vertexlist
        self.assertEqual(temp_part.get_vertexlist(3, False), \
                             templist)

        #Reset the on-shell '3_body_decay_vertexlist'
        templist.extend(templist)
        temp_part.set_vertexlist(3, True, templist)
        #Test for equality from get_vertexlist
        self.assertEqual(temp_part.get_vertexlist(3, True), \
                             templist)

    def test_getsetvertexlist_exceptions(self):
        """Test for the exceptions raised by the get_ or set_vertexlist"""

        #Test of get_ and set_vertexlist
        #Test the exceptions raised from partnum and onshell
        for wrongpartnum in ['string', 1.5]:
            self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                              self.mypart.get_vertexlist, wrongpartnum, True)
            self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                              self.mypart.set_vertexlist, wrongpartnum, True,
                              self.my_2bodyvertexlist, self.my_testmodel)

        for wrongbool in [15, 'NotBool']:           
            self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                              self.mypart.get_vertexlist, 2, wrongbool)
            self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                              self.mypart.set_vertexlist, 3, wrongbool,
                              self.my_3bodyvertexlist, self.my_testmodel)

        

        #Test the exceptions raised from value in set_vertexlist
        #Test for non vertexlist objects
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          self.mypart.set_vertexlist,
                          2, True, ['not', 'Vertexlist'], self.my_testmodel)

        #Test for vertexlist not consistent with partnum
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          self.mypart.set_vertexlist,
                          2, True, self.my_3bodyvertexlist, self.my_testmodel)
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          self.mypart.set_vertexlist,
                          3, True, self.my_2bodyvertexlist, self.my_testmodel)

        #Test for vertexlist not consistent with initial particle
        #for both number and id
        #Use the vertexlist from test_getsetvertexlist_exceptions

        Wrong_vertexlist = [self.my_2bodyvertexlist_wrongini,
                            self.my_3bodyvertexlist_wrongini,
                            self.my_3bodyvertexlist_radiactive]

        for item in Wrong_vertexlist:
            for partnum in [2,3]:
                self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError
                             , self.mypart.set_vertexlist, partnum, False, item)
                

    def test_reset_decaywidth(self):
        """ Test for the reset and update of apx_decaywidth, branching ratio
            for amplitudes, and apx_decaywidth_err."""

        self.my_testmodel.find_all_channels(3)
        tquark = self.my_testmodel.get_particle(6)
        amp = tquark.get_amplitudes(2)[0]
        old_width = amp.get('apx_decaywidth')

        # Add a new channel to tquark
        tquark.get_amplitudes(2).append(amp)

        # Total width doubles. Update the width, br should remain the same.
        amp.get('apx_br')
        tquark.update_decay_attributes(True, True, False)
        self.assertAlmostEqual(tquark.get('apx_decaywidth'),old_width*2)
        self.assertAlmostEqual(amp.get('apx_br'), 1)

        # Update the br now. It should be 0.5.
        tquark.update_decay_attributes(False, True, True)
        self.assertAlmostEqual(tquark.get('apx_decaywidth'),old_width*2)
        self.assertAlmostEqual(amp.get('apx_br'), 0.5)

        # Test the estimate_width_error
        w = self.my_testmodel.get_particle(24)
        width_err = w.get('apx_decaywidth_err')
        offshell_clist = w.get_channels(3, False)
        w.get_channels(3, False).extend(offshell_clist)

        # Test if the width_err doubles after the update
        w.update_decay_attributes(False, True, False)
        self.assertAlmostEqual(w.get('apx_decaywidth_err'),width_err*2)

    def test_find_vertexlist(self):
        """ Test for the find_vertexlist function and 
            the get_max_vertexorder"""
        #undefine object: my_testmodel, mypart, extra_part
        
        #Test validity of arguments
        #Test if the calling particle is in the model
        extra_part = copy.copy(self.mypart)
        extra_part.set('pdg_code', 2)
        extra_part.set('name', 'u')
        # Test the return of get_max_vertexorder if  vertexlist_found = False
        self.assertEqual(None, extra_part.get_max_vertexorder())

        #print self.my_testmodel
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          extra_part.find_vertexlist, self.my_testmodel)

        #Test if option is boolean
        wronglist=[ 'a', 5, {'key': 9}, [1,5]]
        for wrongarg in wronglist:
            self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                              self.mypart.find_vertexlist, self.my_testmodel,\
                              wrongarg)

        #Import the vertexlist from import_vertexlist
        full_vertexlist = import_vertexlist.full_vertexlist

        #Test the correctness of vertexlist by t quark
        tquark = decay_objects.DecayParticle(self.my_testmodel.get_particle(6),True)
        tquark.find_vertexlist(self.my_testmodel)
        #Name convention: 'pdg_code'+'particle #'+'on-shell'
        my_vertexlist620 = base_objects.VertexList()
        # t > b w+
        my_vertexlist621 = base_objects.VertexList([full_vertexlist[(50, 6)]])
        my_vertexlist630 = base_objects.VertexList()
        my_vertexlist631 = base_objects.VertexList()
        rightlist6 = [my_vertexlist620, my_vertexlist621, my_vertexlist630, my_vertexlist631]

        #Test the find_vertexlist for W+
        wboson_p = decay_objects.DecayParticle(self.my_testmodel.get_particle(24), True)
        wboson_p.find_vertexlist(self.my_testmodel)
        #List must follow the order of interaction id so as to be consistent
        #with the find_vertexlist function
        # 
        my_vertexlist2420 = base_objects.VertexList([full_vertexlist[(41, 24)]])
        my_vertexlist2421 = base_objects.VertexList([full_vertexlist[(63, 24)]])
        my_vertexlist2430 = base_objects.VertexList()
        my_vertexlist2431 = base_objects.VertexList()
        #List of the total decay vertex list for W+
        rightlist24 =[my_vertexlist2420, my_vertexlist2421, my_vertexlist2430, my_vertexlist2431]

        #Test the find_vertexlist for A (photon)
        photon = decay_objects.DecayParticle(self.my_testmodel.get_particle(22), True)
        photon.find_vertexlist(self.my_testmodel)
        #vertex is in the order of interaction id
        my_vertexlist2220 = base_objects.VertexList()
        my_vertexlist2221 = base_objects.VertexList()
        my_vertexlist2230 = base_objects.VertexList()
        my_vertexlist2231 = base_objects.VertexList()
        #List of the total decay vertex list for photon
        rightlist22 =[my_vertexlist2220, my_vertexlist2221, my_vertexlist2230, my_vertexlist2231]

        i=0
        for partnum in [2,3]:
            for onshell in [False, True]:
                self.assertEqual(tquark.get_vertexlist(partnum, onshell),
                                 rightlist6[i])
                self.assertEqual(wboson_p.get_vertexlist(partnum, onshell),
                                 rightlist24[i])
                self.assertEqual(photon.get_vertexlist(partnum, onshell),
                                 rightlist22[i])
                i +=1

        # Test for correct get_max_vertexorder()
        self.assertEqual(0, photon.get_max_vertexorder())
        self.assertEqual(2, tquark.get_max_vertexorder())
        self.mypart['vertexlist_found'] = True
        self.assertEqual(3, self.mypart.get_max_vertexorder())

    def test_setget_channel(self):
        """ Test of the get_channel set_channel functions (and the underlying
            check_channels.)"""
        # Prepare the channel
        full_vertexlist = import_vertexlist.full_vertexlist

        vert_0 = base_objects.Vertex({'id': 0, 'legs': base_objects.LegList([\
                 base_objects.Leg({'id':25, 'number':1, 'state': False}),
                 base_objects.Leg({'id':25, 'number':2})])})
        # h > t t~
        vert_1 = copy.deepcopy(full_vertexlist[(59, 25)])
        vert_1['legs'][0]['number'] = 2
        vert_1['legs'][1]['number'] = 3
        vert_1['legs'][2]['number'] = 2
        # t > b w+
        vert_2 = copy.deepcopy(full_vertexlist[(41, -6)])
        vert_2['legs'][0]['number'] = 2
        vert_2['legs'][1]['number'] = 4
        vert_2['legs'][2]['number'] = 2
        # t~ > b~ w-
        vert_3 = copy.deepcopy(full_vertexlist[(50, 6)])
        vert_3['legs'][0]['number'] = 3
        vert_3['legs'][1]['number'] = 5
        vert_3['legs'][2]['number'] = 3

        h_tt_bbww = decay_objects.Channel({'vertices': \
                                           base_objects.VertexList([
                                           vert_3, vert_2, 
                                           vert_1, vert_0])})
        channellist = decay_objects.ChannelList([h_tt_bbww])

        # Test set and get
        higgs = self.my_testmodel.get_particle(25)
        higgs.set('decay_channels', {(4, True): channellist})
        self.assertEqual(higgs.get('decay_channels'), {(4, True): channellist})
                
        # Test set_channel and get_channel
        higgs = self.my_testmodel.get_particle(25)
        higgs.set_channels(4, True, [h_tt_bbww])
        self.assertEqual(higgs.get_channels(4, True), channellist)

        # Test for exceptions
        # Wrong final particle number
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError, 
                          higgs.set_channels, 'non_int', True, [h_tt_bbww])
        # Test from the filter function
        self.assertFalse(higgs.set('decay_channels', 
                                   {('non_int', True): channellist}))
        # Wrong onshell
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError, 
                          higgs.get_channels, 3, 5)
        # Wrong channel
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError, 
                          higgs.set_channels, 3, True, ['non', 'channellist'])
        # Wrong initial particle
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError, 
                          self.my_testmodel.get_particle(24).set_channels, 3,
                          True, [h_tt_bbww])
        # Wrong onshell condition (h is lighter than ww pair)
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError, 
                          higgs.set_channels, 3, True, [h_tt_bbww],
                          self.my_testmodel)
        non_sm = copy.copy(higgs)
        non_sm.set('pdg_code', 26)
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError, 
                          higgs.set_channels, 3, False, [h_tt_bbww],
                          self.my_testmodel)

    def test_get_max_level(self):
        """ Test the get_max_level function. """

        higgs = self.my_testmodel.get_particle(25)
        higgs.find_channels(2, self.my_testmodel)
        self.assertEqual(higgs.get_max_level(), 2)
        higgs.find_channels_nextlevel(self.my_testmodel)
        self.assertEqual(higgs.get_max_level(), 3)
        higgs.find_channels_nextlevel(self.my_testmodel)
        higgs.set_amplitudes(4, decay_objects.DecayAmplitudeList())
        self.assertEqual(higgs.get_max_level(), 4)

#===============================================================================
# TestDecayParticleList
#===============================================================================
class Test_DecayParticleList(unittest.TestCase):
    """Test the DecayParticleList"""
    def setUp(self):
        self.mg5_part = base_objects.Particle({'pdg_code':6, 'is_part':True})
        self.mg5_partlist = base_objects.ParticleList([self.mg5_part]*5)

    def test_convert(self):
        #Test the conversion in __init__
        decay_partlist = decay_objects.DecayParticleList(self.mg5_partlist)
        for i in range(0, 5):
            self.assertTrue(isinstance(decay_partlist[i], 
                                       decay_objects.DecayParticle))

        #Test the conversion in append
        decay_partlist.append(self.mg5_part)
        self.assertTrue(isinstance(decay_partlist[-1], 
                                   decay_objects.DecayParticle))
        self.assertTrue(isinstance(decay_partlist,
                                   decay_objects.DecayParticleList))
        
        #Test the conversion in generate_dict
        for num, part in decay_partlist.generate_dict().items():
            self.assertTrue(isinstance(part, decay_objects.DecayParticle))
#===============================================================================
# TestDecayModel
#===============================================================================
class Test_DecayModel(unittest.TestCase):
    """Test class for the DecayModel object"""

    base_model = import_ufo.import_model('mssm')
    my_testmodel_base = import_ufo.import_model('sm')
    def setUp(self):
        """Set up decay model"""
        #Full SM DecayModel
        self.decay_model = decay_objects.DecayModel(self.base_model, True)

        #My_small sm DecayModel
        self.my_testmodel = decay_objects.DecayModel(self.my_testmodel_base, True)
        param_path = os.path.join(_file_path,'../input_files/param_card_sm.dat')
        self.my_testmodel.read_param_card(param_path)

        # Simplify the model
        particles = self.my_testmodel.get('particles')
        interactions = self.my_testmodel.get('interactions')
        inter_list = copy.copy(interactions)
        no_want_pid = [1, 2, 3, 4, 13, 14, 15, 16, 21, 23, 25]
        for pid in no_want_pid:
            particles.remove(self.my_testmodel.get_particle(pid))

        for inter in inter_list:
            if any([p.get('pdg_code') in no_want_pid for p in \
                        inter.get('particles')]):
                interactions.remove(inter)

        # Set a new name
        self.my_testmodel.set('name', 'my_smallsm')
        self.my_testmodel.set('particles', particles)
        self.my_testmodel.set('interactions', interactions)

        import_vertexlist.make_vertexlist(self.my_testmodel)

        #import madgraph.iolibs.export_v4 as export_v4
        #writer = export_v4.UFO_model_to_mg4(self.base_model,'temp')
        #writer.build()

    def test_read_param_card(self):
        """Test reading a param card"""
        param_path = os.path.join(_file_path, '../input_files/param_card_mssm.dat')
        self.decay_model.read_param_card(os.path.join(param_path))

        for param in sum([self.base_model.get('parameters')[key] for key \
                              in self.base_model.get('parameters')], []):
            value = eval("decay_objects.%s" % param.name)
            self.assertTrue(isinstance(value, int) or \
                            isinstance(value, float) or \
                            isinstance(value, complex))

    def test_setget(self):
        """ Test the set and get for special properties"""

        self.my_testmodel.set('vertexlist_found', True)
        self.assertEqual(self.my_testmodel.get('vertexlist_found'), True)
        self.my_testmodel.set('vertexlist_found', False)
        self.assertRaises(self.my_testmodel.PhysicsObjectError,
                          self.my_testmodel.filter, 'max_vertexorder', 'a')
        self.assertRaises(self.my_testmodel.PhysicsObjectError,
                          self.my_testmodel.filter, 'stable_particles', 
                          [self.my_testmodel.get('particles'), ['a']])
        self.assertRaises(decay_objects.DecayModel.PhysicsObjectError,
                          self.my_testmodel.filter, 'vertexlist_found', 4)
                          
    
    def test_particles_type(self):
        """Test if the DecayModel can convert the assign particle into
           decay particle"""

        #Test the particle is DecayParticle during generator stage
        #Test the default_setup first
        temp_model = decay_objects.DecayModel()
        self.assertTrue(isinstance(temp_model.get('particles'),
                              decay_objects.DecayParticleList))

        #Test the embeded set in __init__
        self.assertTrue(isinstance(self.decay_model.get('particles'), 
                                   decay_objects.DecayParticleList))

        #Test the conversion into DecayParticle explicitly
        #by the set function
        mg5_particlelist = self.base_model['particles']

        result = self.decay_model.set('particles', mg5_particlelist, True)

        #Using ParticleList to set should be fine, the result is converted
        #into DecayParticleList.
        self.assertTrue(result)
        self.assertTrue(isinstance(self.decay_model['particles'],
                              decay_objects.DecayParticleList))

        #particle_dict should contain DecayParticle
        self.assertTrue(isinstance(self.decay_model.get('particle_dict')[6],
                                   decay_objects.DecayParticle))

        #Test if the set function returns correctly when assign a bad value
        try:
            self.assertFalse(self.decay_model.set('particles', 'NotParticleList'))
        except:
            self.assertRaises(AssertionError, self.decay_model.set, 'particles', 'NotParticleList')

        #Test if the particls in interaction is converted to DecayParticle
        self.assertTrue(isinstance(self.decay_model['interactions'][-1]['particles'], decay_objects.DecayParticleList))
                        

    def test_find_vertexlist(self):
        """Test of the find_vertexlist"""

        # Test the exception of get_max_vertexorder
        self.assertEqual(None, self.my_testmodel.get_max_vertexorder())
        self.my_testmodel.find_vertexlist()
        self.my_testmodel.get('particle_dict')[5]['charge'] = 8
        full_vertexlist = import_vertexlist.full_vertexlist_newindex

        for part in self.my_testmodel.get('particles'):
            for partnum in [2, 3]:
                for onshell in [True, False]:
                    #print part.get_pdg_code(), partnum, onshell
                    self.assertEqual(part.get_vertexlist(partnum, onshell),
                                     full_vertexlist[(part.get_pdg_code(),
                                                      partnum, onshell)])
        
        self.assertEqual(2, self.my_testmodel.get_max_vertexorder())
        self.my_testmodel['max_vertexorder'] = 0
        self.assertEqual(2, self.my_testmodel.get('max_vertexorder'))
        # Test the get from particle
        self.assertEqual(2, 
                        self.my_testmodel.get_particle(6).get_max_vertexorder())

        # Test the assignment of vertexlist_found property
        self.assertTrue(self.my_testmodel.get('vertexlist_found'))
        self.assertTrue(all([p.get('vertexlist_found') for p in \
                                self.my_testmodel.get('particles')]))

    def test_find_mssm_decay_groups_modified_mssm(self):
        """Test finding the decay groups of the MSSM"""

        mssm = import_ufo.import_model('mssm')
        particles = mssm.get('particles')
        no_want_particle_codes = [1000022, 1000023, 1000024, -1000024, 
                                  1000025, 1000035, 1000037, -1000037]
        no_want_particles = [p for p in particles if p.get('pdg_code') in \
                                 no_want_particle_codes]

        for particle in no_want_particles:
            particles.remove(particle)

        interactions = mssm.get('interactions')
        inter_list = copy.copy(interactions)
        for interaction in inter_list:
            if any([p.get('pdg_code') in no_want_particle_codes for p in \
                        interaction.get('particles')]):
                interactions.remove(interaction)
        
        mssm.set('particles', particles)
        mssm.set('interactions', interactions)
        decay_mssm = decay_objects.DecayModel(mssm, True)

        decay_mssm.find_decay_groups()
        goal_groups = set([(25, 35, 36, 37),
                           (1000001, 1000002, 1000003, 1000004, 1000005, 
                            1000006, 1000021, 2000001, 2000002, 2000003, 
                            2000004, 2000005, 2000006), 
                           (1000011, 1000012), 
                           (1000013, 1000014), 
                           (1000015, 1000016, 2000015), 
                           (2000011,), 
                           (2000013,)])

        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in \
                                                group])) \
                                  for group in decay_mssm['decay_groups']]),
                         goal_groups)

    def test_find_mssm_decay_groups(self):
        """Test finding the decay groups of the MSSM"""

        mssm = import_ufo.import_model('mssm')
        decay_mssm = decay_objects.DecayModel(mssm, True)
        decay_mssm.find_decay_groups()
        goal_groups = [[25, 35, 36, 37],
                       [1000001, 1000002, 1000003, 1000004, 1000005, 1000006, 1000011, 1000012, 1000013, 1000014, 1000015, 1000016, 1000021, 1000022, 1000023, 1000024, 1000025, 1000035, 1000037, 2000001, 2000002, 2000003, 2000004, 2000005, 2000006, 2000011, 2000013, 2000015]]

        # find_decay_groups_general should be run automatically
        for i, group in enumerate(decay_mssm['decay_groups']):
            self.assertEqual(sorted([p.get('pdg_code') for p in group]),
                             goal_groups[i])
    def test_find_mssm_decay_groups_general(self):
        """Test finding the decay groups of the MSSM"""

        mssm = import_ufo.import_model('mssm')
        decay_mssm = decay_objects.DecayModel(mssm, True)
        # Read data to find massless SM-like particle
        param_path = os.path.join(_file_path,
                                  '../input_files/param_card_mssm.dat')
        decay_mssm.read_param_card(param_path)

        goal_groups = [[1,2,3,4,11,12,13,14, 15, 16,21,22, 
                        23, 24, 25, 35, 36, 37], # 15 and from 23 are calculated
                       # others are massless default
                       [1000001, 1000002, 1000003, 1000004, 1000011, 1000012, 1000013, 1000014, 1000015, 1000016, 1000021, 1000022, 1000023, 1000024, 1000025, 1000035, 1000037, 2000001, 2000002, 2000003, 2000004, 2000011, 2000013, 2000015], [1000005, 1000006, 2000005, 2000006], [5, 6]]
        goal_stable_particle_ids = set([(1,2,3,4,11,12,13,14,16,21,22),
                                        (5,),
                                        (1000022,)])

        for i, group in enumerate(decay_mssm.get('decay_groups')):
            self.assertEqual(sorted([p.get('pdg_code') for p in group]),
                             goal_groups[i])

        # Test if all useless interactions are deleted.
        for inter in decay_mssm['reduced_interactions']:
            self.assertTrue(len(inter['particles']))

        # Reset decay_groups, test the auto run from find_stable_particles
        decay_mssm['decay_groups'] = []
        
        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in plist])) for plist in decay_mssm.get('stable_particles')]), goal_stable_particle_ids)

            

    def test_find_mssm_decay_groups_modified_mssm_general(self):
        """Test finding the decay groups of the MSSM using general way.
           Test to get decay_groups and stable_particles from get."""
        # Setup the mssm with parameters read in.
        mssm = import_ufo.import_model('mssm')
        decay_mssm = decay_objects.DecayModel(mssm, True)
        particles = decay_mssm.get('particles')
        param_path = os.path.join(_file_path,
                                  '../input_files/param_card_mssm.dat')
        decay_mssm.read_param_card(param_path)
        
        # Set no want particles
        no_want_particle_codes = [1000022, 1000023, 1000024, -1000024, 
                                  1000025, 1000035, 1000037, -1000037]
        no_want_particles = [p for p in particles if p.get('pdg_code') in \
                                 no_want_particle_codes]

        for particle in no_want_particles:
            particles.remove(particle)

        interactions = decay_mssm.get('interactions')
        inter_list = copy.copy(interactions)

        for interaction in inter_list:
            if any([p.get('pdg_code') in no_want_particle_codes for p in \
                        interaction.get('particles')]):
                interactions.remove(interaction)
        
        decay_mssm.set('particles', particles)
        decay_mssm.set('interactions', interactions)

        # Set sd4, sd5 quark mass the same as b quark, so that 
        # degeneracy happens and can be tested 
        # (both particle and anti-particle must be changed)
        # This reset of particle mass must before the reset of particles
        # so that the particles of all interactions can change simutaneuosly.
        decay_mssm.get_particle(2000003)['mass'] = \
            decay_mssm.get_particle(5).get('mass')
        decay_mssm.get_particle(2000001)['mass'] = \
            decay_mssm.get_particle(5).get('mass')
        decay_mssm.get_particle(1000012)['mass'] = \
            decay_mssm.get_particle(1000015).get('mass')

        decay_mssm.get_particle(-2000003)['mass'] = \
            decay_mssm.get_particle(5).get('mass')
        decay_mssm.get_particle(-2000001)['mass'] = \
            decay_mssm.get_particle(5).get('mass')


        # New interactions that mix different groups
        new_interaction = base_objects.Interaction({\
                'id': len(decay_mssm.get('interactions'))+1,
                'particles': base_objects.ParticleList(
                             [decay_mssm.get_particle(1000001),
                              decay_mssm.get_particle(1000011),
                              decay_mssm.get_particle(1000003),
                              decay_mssm.get_particle(1000013),
                              # This new SM particle should be removed
                              # In the reduction level
                              decay_mssm.get_particle(2000013),
                              decay_mssm.get_particle(1000015)])})
        new_interaction_add_sm = base_objects.Interaction({\
                'id': len(decay_mssm.get('interactions'))+2,
                'particles': base_objects.ParticleList(
                             [decay_mssm.get_particle(25),
                              decay_mssm.get_particle(2000013)])})

        decay_mssm.get('interactions').append(new_interaction)
        decay_mssm.get('interactions').append(new_interaction_add_sm)

        goal_groups = set([(1,2,3,4,11,12,13,14, 15, 16,21,22,
                            23, 24, 25, 35, 36, 37, 2000013), # 15 and from 23
                           # are calculated, others are massless default
                           (1000005, 1000006, 2000005, 2000006),
                           (1000015, 1000016, 2000015),                        
                           (1000001, 1000002, 1000003, 1000004, 
                            1000021, 2000001, 2000002, 2000003, 2000004),
                           (5, 6),
                           (1000011, 1000012), 
                           (1000013, 1000014), 
                           # 2000013 originally should be here, but the
                           # the new_interaction_add_sm change it to SM group
                           (2000011,)
                           ])

        # the stable_candidates that should appear in 1st stage of
        # find stable_particles
        goal_stable_candidates = [[1,2,3,4,11,12,13,14,16,21,22],
                                  [1000006], [1000015], [2000001, 2000003],
                                  [5], [1000012], [1000014],[2000011]]
        # Group 1,3,4 mixed; group 2, 5, 6 mixed
        goal_stable_particle_ids = set([(1,2,3,4,11,12,13,14,16,21,22),
                                        (1000015,),
                                        # 5 mass = squark
                                        # will be set later
                                        (2000001, 2000003),
                                        (5,),
                                        (1000012,),
                                        (1000014,),
                                        # all sleptons are combine
                                        (2000011,)])

        # Get the decay_groups (this should run find_decay_groups_general)
        # automatically.
        mssm_decay_groups = decay_mssm.get('decay_groups')

        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in \
                                            group])) \
                              for group in mssm_decay_groups]),
                         goal_groups)
 
        # Test if all useless interactions are deleted.
        for inter in decay_mssm['reduced_interactions']:
            self.assertTrue(len(inter['particles']))

        # Test stable particles
        # Reset the decay_groups, test the auto-run of find_decay_groups_general
        decay_mssm['decay_groups'] = []
        decay_mssm.find_stable_particles()

        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in plist])) for plist in decay_mssm['stable_particles']]), goal_stable_particle_ids)
        
        # Test the assignment of is_stable to particles
        goal_stable_pid = [1,2,3,4,5,11,12,13,14,16,21,22,1000012,1000014,
                           1000015, 2000001, 2000003, 2000011]
        self.assertEqual(sorted([p.get_pdg_code() \
                                     for p in decay_mssm.get('particles') \
                                     if p.get('is_stable')]), goal_stable_pid)
        self.assertTrue(decay_mssm.get_particle(-goal_stable_pid[0]).get('is_stable'))

        # Test the advance search of stable particles
        for p in decay_mssm['particles']:
            p['is_stable'] = False
        decay_mssm['stable_particles'] = []
        decay_mssm.find_stable_particles_advance()
        self.assertEqual(sorted([p.get_pdg_code() \
                                     for p in decay_mssm.get('particles') \
                                     if p.get('is_stable')]), goal_stable_pid)

        goal_stable_particles_ad = set([(1,),(2,),(3,),(4,),(5,),
                                        (11,),(12,),(13,),(14,),(16,),
                                        (21,),(22,),
                                        (1000012,),(1000014,),(1000015,),
                                        (2000001,),( 2000003,),( 2000011,)])
        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in plist])) for plist in decay_mssm['stable_particles']]), goal_stable_particles_ad)
        
    def test_find_full_sm_decay_groups(self):
        """ Test the algorithm in find stable particle in full sm.
            First, test the full sm with massive neutrinos.
            Second, set the neutrinos as massless."""

        # Import the full sm with param_card
        # NO massless particle, i.e. neutrinos, leptons, quarks all have masses.
        full_sm_base = import_ufo.import_full_model(\
            os.path.join(MG5DIR,
                         'tests', 'input_files',
                         'full_sm_UFO'))
        full_sm = decay_objects.DecayModel(full_sm_base, True)
        param_path = os.path.join(_file_path,
                                  '../input_files/param_card_full_sm.dat')
        full_sm.read_param_card(param_path)
        

        # Stage 1: nonzero neutrino masses 
        # the stable particles are the ones with lightest mass in
        # their group
        goal_groups_1 = set([(21,22, 23,25), # 23 and 25 are calculated
                             # others are massless default
                             (1,), (2,), (3,), (4,), (5,), (6,),
                             (11,), (12,), (13,), (14,), (15,), (16,),
                             (24,)])
        goal_stable_particles_1 = set([(21,22),
                                       (2,),
                                       (11,), (12,), (14,), (16,)])

        # Test decay groups
        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in \
                                            group])) \
                                  for group in full_sm.get('decay_groups')]),
                         goal_groups_1)
        # Test stable particles
        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in \
                                            group])) \
                                 for group in full_sm.get('stable_particles')]),
                         goal_stable_particles_1)


        # Stage 2: turn off the neutrino mass
        full_sm.get_particle(12)['mass'] = 'ZERO'
        full_sm.get_particle(14)['mass'] = 'ZERO'
        full_sm.get_particle(16)['mass'] = 'ZERO'
        full_sm.get_particle(-12)['mass'] = 'ZERO'
        full_sm.get_particle(-14)['mass'] = 'ZERO'
        full_sm.get_particle(-16)['mass'] = 'ZERO'

        full_sm['decay_groups'] = []
        full_sm['stable_particles'] = []
        for p in full_sm['particles']:
            p['is_stable'] = False

        goal_groups_2 = set([(12,14,16,21,22, 23,25), # 23,25 are
                             # calculated, others are massless
                             (1,), (2,), (3,), (4,), (5,), (6,),
                             (11,13,15,24)])
        goal_stable_particles_2 = set([(12,14,16,21,22),
                                       (2,),
                                       (11,)])
        goal_stable_pid_2 = [2, 11, 12,14,16,21,22]

        # Test decay groups
        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in \
                                            group])) \
                                  for group in full_sm.get('decay_groups')]),
                         goal_groups_2)

        # Test stable particles
        self.assertEqual(set([tuple(sorted([p.get('pdg_code') for p in \
                                            group])) \
                                 for group in full_sm.get('stable_particles')]),
                         goal_stable_particles_2)

        # Test the assignment of is_stable
        self.assertEqual(sorted([p.get_pdg_code() \
                                     for p in full_sm.get('particles') \
                                     if p.get('is_stable')]), goal_stable_pid_2)


    def test_find_full_sm_decay_groups_advance(self):
        """ Test the algorithm in find_stable_particles_advance in full sm.
            First, test the full sm with massive neutrinos.
            Second, set the neutrinos as massless."""

        # Import the full sm with param_card
        sm_path = import_ufo.find_ufo_path('sm')
        full_sm_base = import_ufo.import_full_model(sm_path)
        full_sm = decay_objects.DecayModel(full_sm_base, True)
        param_path = os.path.join(_file_path,
                                  '../input_files/param_card_full_sm.dat')
        full_sm.read_param_card(param_path)

        # Stage 1: nonzero neutrino masses 
        goal_stable_pid_1 = [2, 11, 12,14,16,21,22]
        full_sm.find_stable_particles_advance()
        
        # Test the assignment of is_stable
        self.assertEqual(sorted([p.get_pdg_code() \
                                     for p in full_sm.get('particles') \
                                     if p.get('is_stable')]), goal_stable_pid_1)
        
        
        # Stage 2: turn off the neutrino mass
        full_sm.get_particle(12)['mass'] = 'ZERO'
        full_sm.get_particle(14)['mass'] = 'ZERO'
        full_sm.get_particle(16)['mass'] = 'ZERO'
        full_sm.get_particle(-12)['mass'] = 'ZERO'
        full_sm.get_particle(-14)['mass'] = 'ZERO'
        full_sm.get_particle(-16)['mass'] = 'ZERO'

        full_sm['decay_groups'] = []
        full_sm['stable_particles'] = []
        for p in full_sm['particles']:
            p['is_stable'] = False
        full_sm.find_stable_particles_advance()

        goal_stable_pid_2 = [2, 11, 12,14,16,21,22]
        
        # Test the assignment of is_stable
        self.assertEqual(sorted([p.get_pdg_code() \
                                     for p in full_sm.get('particles') \
                                     if p.get('is_stable')]), goal_stable_pid_2)
            

    def test_running_couplings(self):
        """ Test the running coupling constants in DecayModel."""

        # Read mssm
        model_base = import_ufo.import_model('mssm')
        model = decay_objects.DecayModel(model_base, True)
        param_path = os.path.join(_file_path,'../input_files/param_card_mssm.dat')
        model.read_param_card(param_path)
        #print decay_objects.MZ

        # Test for exception
        self.assertRaises(decay_objects.DecayModel.PhysicsObjectError,
                          self.my_testmodel.running_externals, "not i")

        # Test for running_externals
        # No reference value for q higher than top quark mass

        # Set b quark mass to be consistent with SM model
        decay_objects.MB = 4.7
        
        # q=400., Nf = 5 quarks
        model.running_externals(400., 1)
        self.assertAlmostEqual(decay_objects.aS, 0.0972887598, 5)
        model.running_externals(400.)
        self.assertAlmostEqual(decay_objects.aS, 0.096563954696, 5)

        # q=170., Nf = 5 quarks
        model.running_externals(170., 1)
        self.assertAlmostEqual(decay_objects.aS, 0.1082883202, 6)
        model.running_externals(170.)
        self.assertAlmostEqual(decay_objects.aS, 0.10788637604, 6)

        # q=10., Nf = 5 quarks
        model.running_externals(10., 1)
        self.assertAlmostEqual(decay_objects.aS, 0.1730836377, 6)
        model.running_externals(10.)
        self.assertAlmostEqual(decay_objects.aS, 0.17787426379, 6)

        # q=4., Nf = 4 quarks
        model.running_externals(4., 1)
        self.assertAlmostEqual(decay_objects.aS, 0.215406025, 6)
        model.running_externals(4.)
        self.assertAlmostEqual(decay_objects.aS, 0.22772914557, 6)

        # q=1., Nf = 3 quarks
        model.running_externals(1., 1)
        self.assertAlmostEqual(decay_objects.aS, 0.36145974008, 5)
        model.running_externals(1.)
        self.assertAlmostEqual(decay_objects.aS, 0.45187971053, 5)

        # Test for running_internals
        temp_aS = 100
        decay_objects.aS = temp_aS
        Ru11_old = decay_objects.Ru11
        # coupling of no running dependence
        try:
            coup0 = model['couplings'][('aEWM1',)][0]
        except KeyError:
            coup0 = model['couplings'][()][0]        
        # coupling depend on aS
        coup_aS = model['couplings'][('aS',)][0]
        # coupling depend on both aS and aEWM1
        try:
            coup_both = model['couplings'][('aS', 'aEWM1')][0]
        except KeyError:
            coup_both = model['couplings'][('aEWM1', 'aS')][0]

        coup0_old = eval('decay_objects.'+coup0.name)
        #print coup_aS.name
        #print coup_both.name
        model.running_internals()


        # Test for parameters
        # Ru11 should not change
        self.assertAlmostEqual(decay_objects.Ru11, Ru11_old)
        # G should change
        self.assertAlmostEqual(decay_objects.G, \
                                   2*cmath.sqrt(temp_aS)*cmath.sqrt(cmath.pi))
        # Test for couplings
        # GC_365 should not change
        self.assertAlmostEqual(eval('decay_objects.'+coup0.name), coup0_old)
        # Both of GC_114 ('aS',) and GC_15 ('aEWSM1', 'aS') should change
        self.assertAlmostEqual(eval('decay_objects.'+coup_aS.name), \
                                   -decay_objects.G)
        # copying the expr of 
        self.assertAlmostEqual(eval('decay_objects.'+coup_both.name), \
                                   (-2*decay_objects.ee*complex(0,1)*decay_objects.G*decay_objects.I1233)/3. - (2*decay_objects.ee*complex(0,1)*decay_objects.G*decay_objects.I1333)/3.)


#===============================================================================
# Test_Channel
#===============================================================================
class Test_Channel(unittest.TestCase):
    """ Test for the channel object"""

    my_testmodel_base = import_ufo.import_model('sm')
    my_channel = decay_objects.Channel()
    h_tt_bbmmvv = decay_objects.Channel()

    def setUp(self):
        """ Set up necessary objects for the test"""
        #Import a model from my_testmodel
        self.my_testmodel = decay_objects.DecayModel(self.my_testmodel_base, True)
        param_path = os.path.join(_file_path,'../input_files/param_card_sm.dat')
        self.my_testmodel.read_param_card(param_path)

        # Simplify the model
        particles = self.my_testmodel.get('particles')
        interactions = self.my_testmodel.get('interactions')
        inter_list = copy.copy(interactions)
        # Pids that will be removed
        no_want_pid = [1, 2, 3, 4, 15, 16, 21]
        for pid in no_want_pid:
            particles.remove(self.my_testmodel.get_particle(pid))

        for inter in inter_list:
            if any([p.get('pdg_code') in no_want_pid for p in \
                        inter.get('particles')]):
                interactions.remove(inter)

        # Set a new name
        self.my_testmodel.set('name', 'my_smallsm')
        self.my_testmodel.set('particles', particles)
        self.my_testmodel.set('interactions', interactions)

        #Setup the vertexlist for my_testmodel and save this model (optional)
        import_vertexlist.make_vertexlist(self.my_testmodel)
        #save_model.save_model(os.path.join(MG5DIR, 'tests/input_files', 
        #self.my_testmodel['name']), self.my_testmodel)
    
        full_vertexlist = import_vertexlist.full_vertexlist
        vert_0 = base_objects.Vertex({'id': 0, 'legs': base_objects.LegList([\
                    base_objects.Leg({'id':25, 'number':1, 'state': False}), \
                    base_objects.Leg({'id':25, 'number':2})])})
        # h > t t~ > b b~ w+ w-
        vert_1 = copy.deepcopy(full_vertexlist[(59, 25)])
        vert_1['legs'][0]['number'] = 2
        vert_1['legs'][1]['number'] = 3
        vert_1['legs'][2]['number'] = 2
        vert_2 = copy.deepcopy(full_vertexlist[(50, 6)])
        vert_2['id'] = -vert_2['id']
        vert_2['legs'][0]['number'] = 2
        vert_2['legs'][0]['id'] = -vert_2['legs'][0]['id']
        vert_2['legs'][1]['number'] = 4
        vert_2['legs'][1]['id'] = -vert_2['legs'][1]['id']
        vert_2['legs'][2]['number'] = 2
        vert_2['legs'][2]['id'] = -vert_2['legs'][2]['id']
        vert_3 = copy.deepcopy(full_vertexlist[(50, 6)])
        vert_3['legs'][0]['number'] = 3
        vert_3['legs'][1]['number'] = 5
        vert_3['legs'][2]['number'] = 3
        vert_4 = copy.deepcopy(full_vertexlist[(63, 24)])
        vert_4['id'] = -vert_4['id']
        vert_4['legs'][0]['number'] = 4
        vert_4['legs'][0]['id'] = -vert_4['legs'][0]['id']
        vert_4['legs'][1]['number'] = 6
        vert_4['legs'][1]['id'] = -vert_4['legs'][1]['id']
        vert_4['legs'][2]['number'] = 4
        vert_4['legs'][2]['id'] = -vert_4['legs'][2]['id']
        vert_5 = copy.deepcopy(full_vertexlist[(63, 24)])
        vert_5['legs'][0]['number'] = 5
        vert_5['legs'][1]['number'] = 7
        vert_5['legs'][2]['number'] = 5

        #temp_vertices = base_objects.VertexList
        self.h_tt_bbmmvv = decay_objects.Channel({'vertices': \
                                             base_objects.VertexList([
                                             vert_5, vert_4, vert_3, vert_2, \
                                             vert_1, vert_0])})

        #print self.h_tt_bbmmvv.nice_string()
        #pic = drawing_eps.EpsDiagramDrawer(self.h_tt_bbmmvv, 'h_tt_bbmmvv', self.my_testmodel)
        #pic.draw()

    def test_get_initialfinal(self):
        """ test the get_initial_id and get_final_legs"""
        # Test the get_initial_id
        self.assertEqual(self.h_tt_bbmmvv.get_initial_id(), 25)
        
        # Test the get_final_legs
        vertexlist = self.h_tt_bbmmvv.get('vertices')
        goal_final_legs = base_objects.LegList([vertexlist[0]['legs'][0],
                                                vertexlist[0]['legs'][1],
                                                vertexlist[1]['legs'][0],
                                                vertexlist[1]['legs'][1],
                                                vertexlist[2]['legs'][0],
                                                vertexlist[3]['legs'][0]])
        self.assertEqual(self.h_tt_bbmmvv.get_final_legs(), goal_final_legs)

    def test_get_onshell(self):
        """ test the get_onshell function"""
        vertexlist = self.h_tt_bbmmvv.get('vertices')
        h_tt_bbww = decay_objects.Channel({'vertices': \
                                           base_objects.VertexList(\
                                           vertexlist[2:])})
        print h_tt_bbww.nice_string()
        # Test for on shell decay ( h > b b~ mu+ mu- vm vm~)
        self.assertTrue(self.h_tt_bbmmvv.get_onshell(self.my_testmodel))

        # Test for off-shell decay (h > b b~ w+ w-)
        # Raise the mass of higgs
        decay_objects.MH = 220
        self.assertTrue(h_tt_bbww.get_onshell(self.my_testmodel))

    def test_helper_find_channels(self):
        """ Test of the find_channels function of DecayParticle.
            Also the test for some helper function for find_channels."""

        higgs = self.my_testmodel.get_particle(25)
        
        vertexlist = self.h_tt_bbmmvv.get('vertices')
        h_tt_bbww = decay_objects.Channel({'vertices': \
                                           base_objects.VertexList(\
                                           vertexlist[2:])})
        h_tt_bbww.calculate_orders(self.my_testmodel)
        self.my_testmodel.find_vertexlist()
        # Artificially add 4 body decay vertex to w boson
        self.my_testmodel.get_particle(24)['decay_vertexlist'][(4, True)] =\
            vertexlist[2]        
        # The two middle are for wboson (see h_tt_bbww.get_final_legs()).
        """goal_configlist = set([(2, 4, 1, 2), (2, 4, 2, 1), (2, 3, 1, 3),
                               (2, 3, 2, 2), (2, 2, 1, 4), (2, 2, 2, 3),
                               (2, 1, 2, 4), (1, 4, 2, 2), (1, 4, 1, 3),
                               (1, 3, 1, 4), (1, 3, 2, 3), (1, 2, 2, 4),])
        self.assertEqual(set([tuple(i) \
                              for i in higgs.generate_configlist(h_tt_bbww,
                                                                 9, 
                                                           self.my_testmodel)]),
                         goal_configlist)"""
        # Reset the decay_vertexlist of w boson.
        self.my_testmodel.get_particle(24)['decay_vertexlist'].pop((4, True))


        # Test the connect_channel_vertex
        h_tt_bwbmuvm = decay_objects.Channel({'vertices': \
                                              base_objects.VertexList(\
                                              vertexlist[1:])})
        #int_leg = h_tt_bbww.get_final_legs()[-1]
        #print int_leg, h_tt_bbww.get_final_legs()
        w_muvm = self.my_testmodel.get_particle(24).get_vertexlist(2, True)[0]
        #print w_muvm
        new_channel = higgs.connect_channel_vertex(h_tt_bbww, 3, w_muvm,
                                                   self.my_testmodel)
        #print 'c1:', new_channel.nice_string(), '\nc2:', h_tt_bwbmuvm.nice_string(), '\n'
        #print self.h_tt_bbmmvv.nice_string()
        h_tt_bwbmuvm.get_onshell(self.my_testmodel)
        #h_tt_bwbmuvm.calculate_orders(self.my_testmodel)
        self.assertEqual(new_channel, h_tt_bwbmuvm)

        # Test of check_idlegs
        temp_vert = copy.deepcopy(vertexlist[2])
        temp_vert['legs'].insert(2, temp_vert['legs'][1])
        temp_vert['legs'][2]['number'] = 4
        #print temp_vert
        self.assertEqual(decay_objects.Channel.check_idlegs(vertexlist[2]), {})
        self.assertEqual(decay_objects.Channel.check_idlegs(temp_vert),
                         {24: [1, 2]})

        # Test of get_idpartlist
        temp_vert2 = copy.deepcopy(temp_vert)
        temp_vert2['legs'].insert(3, temp_vert['legs'][0])
        temp_vert2['legs'].insert(4, temp_vert['legs'][0])
        #print temp_vert2
        idpart_c = decay_objects.Channel({'vertices': \
                              base_objects.VertexList([temp_vert])})
        idpart_c = higgs.connect_channel_vertex(idpart_c, 1, temp_vert2, 
                                                self.my_testmodel)
        #print idpart_c.nice_string()
        self.assertEqual(idpart_c.get_idpartlist(),
                         {(1, temp_vert['id'], 24): [1, 2], 
                          (0, temp_vert['id'], 24): [1, 2],
                          (0, temp_vert['id'], 5):  [0,3,4]})
        self.assertTrue(idpart_c.get('has_idpart'))

        # Test of generate_configs
        test_list = {21: [1,4,6], 25: [2, 3, 7, 9]}
        goal_configs = {21: [[1,4,6], [1,6,4], [4,1,6], [4,6,1], 
                             [6,1,4], [6,4,1]],
                        25: [[2,3,7,9], [2,3,9,7], [2,7,3,9], [2,7,9,3],
                             [2,9,3,7], [2,9,7,3],
                             [3,2,7,9], [3,2,9,7], [3,7,2,9], [3,7,9,2],
                             [3,9,2,7], [3,9,7,2],
                             [7,2,3,9], [7,2,9,3], [7,3,2,9], [7,3,9,2],
                             [7,9,2,3], [7,9,3,2],
                             [9,2,3,7], [9,2,7,3], [9,3,2,7], [9,3,7,2],
                             [9,7,2,3], [9,7,3,2]]}
        self.assertEqual(decay_objects.Channel.generate_configs(test_list),
                         goal_configs)

        # Test of check_channels_equiv
        # Create several non-realistic vertex
        vert_1_id = copy.deepcopy(vertexlist[4])
        vert_1_id.set('id', 80)
        vert_1_id.get('legs').insert(2, copy.copy(vert_1_id.get('legs')[1]))
        vert_1_id.get('legs').insert(3, copy.copy(vert_1_id.get('legs')[0]))
        vert_1_id.get('legs').insert(4, copy.copy(vert_1_id.get('legs')[0]))
        vert_1_id.get('legs')[2]['number'] = 4
        vert_1_id.get('legs')[3]['number'] = 5
        vert_1_id.get('legs')[4]['number'] = 6

        vert_2_id = copy.deepcopy(vertexlist[2])
        vert_2_id.set('id', 90)
        vert_2_id.get('legs').insert(2, copy.copy(vert_2_id.get('legs')[1]))
        vert_2_id.get('legs')[2]['number'] = 0

        w_muvmu = copy.deepcopy(vertexlist[0])
        w_muvmu.set('id', 100)
        w_muvmu.get('legs')[0].set('id', -13)
        w_muvmu.get('legs')[1].set('id', 14)

        self.my_testmodel.get('interactions').append(\
            base_objects.Interaction({'id':80}))
        self.my_testmodel.get('interactions').append(\
            base_objects.Interaction({'id':90}))
        self.my_testmodel.get('interactions').append(\
            base_objects.Interaction({'id':100}))
        self.my_testmodel.reset_dictionaries()

        # Nice string for channel_a:
        # ((8(13),12(-14)>8(-24),id:-100), (7(11),11(-12)>7(-24),id:-44),
        #  (5(-5),10(-24)>5(-6),id:-35),(4(5),9(24)>4(6),id:35),
        #  (2(-5),7(-24),8(-24)>2(-6),id:-90),
        #  (2(-6),3(6),4(6),5(-6),6(6)>2(25),id:80),(2(25),1(25),id:0)) ()
        
        # Nice string of channel_b:
        #((10(11),12(-12)>10(-24),id:-44),(9(13),11(-14)>9(-24),id:-100),
        # (6(-5),9(-24),10(-24)>6(-6),id:-90),(3(5),8(24)>3(6),id:35),
        # (2(-5),7(-24)>2(-6),id:-35),
        # (2(-6),3(6),4(6),5(-6),6(-6)>2(25),id:80),(2(25),1(25),id:0)) ()

        # Nice string of channel_c:
        #((10(13),12(-14)>10(-24),id:-100),(9(13),11(-14)>9(-24),id:-100),
        # (6(-5),9(-24),10(-24)>6(-6),id:-90),(3(5),8(24)>3(6),id:35),
        # (2(-5),7(-24)>2(-6),id:-35),
        # (2(-6),3(6),4(6),5(-6),6(-6)>2(25),id:80),(2(25),1(25),id:0)) ()

        # Initiate channel_a
        # h > t~ t t t~ t~
        channel_a = decay_objects.Channel({'vertices': base_objects.VertexList(\
                    [vert_1_id, vertexlist[5]])})
        # Add t~ > b~ w- w- to first t~
        channel_a = higgs.connect_channel_vertex(channel_a, 0,
                                                 vert_2_id,
                                                 self.my_testmodel)
        #print channel_a.nice_string()
        # Add t > b w+ to 2nd t
        channel_a = higgs.connect_channel_vertex(channel_a, 4,
                                                 vertexlist[2],
                                                 self.my_testmodel)
        #print channel_a.nice_string()
        # Add t~ > b~ w- to 2nd t~
        channel_a = higgs.connect_channel_vertex(channel_a, 6,
                                                 vertexlist[2],
                                                 self.my_testmodel)
        #print channel_a.nice_string()
        # Add w- > e- ve~ to first w- in t~ decay chain
        channel_a = higgs.connect_channel_vertex(channel_a, 5,
                                                 vertexlist[0],
                                                 self.my_testmodel)
        #print channel_a.nice_string()
        # Add w- > mu vm~ to 2nd w- in t~ decay chain
        channel_a = higgs.connect_channel_vertex(channel_a, 7,
                                                 w_muvmu,
                                                 self.my_testmodel)
        #print 'Channel_a:\n', channel_a.nice_string()
        
        # Initiate channel_b
        # h > t~ t t t~ t~
        channel_b = decay_objects.Channel({'vertices': base_objects.VertexList(\
                    [vert_1_id, vertexlist[5]])})

        # Add t > b w+ to 1st t
        channel_b = higgs.connect_channel_vertex(channel_b, 0,
                                                 vertexlist[2],
                                                 self.my_testmodel)
        #print '\n', channel_b.nice_string()

        # Add t~ > b~ w- to 1st t~
        channel_b = higgs.connect_channel_vertex(channel_b, 2,
                                                 vertexlist[2],
                                                 self.my_testmodel)
        #print channel_b.nice_string()

        # Add t~ > b~ w- w- to final t~
        channel_b = higgs.connect_channel_vertex(channel_b, 6,
                                                 vert_2_id,
                                                 self.my_testmodel)
        #print channel_b.nice_string()

        # Add w- > e- ve~ to 2nd w- in t~ decay chain
        channel_b = higgs.connect_channel_vertex(channel_b, 1,
                                                 w_muvmu,
                                                 self.my_testmodel)
        #print channel_b.nice_string()

        # Add w- > mu vm~ to 1st w- in t~ decay chain
        channel_b = higgs.connect_channel_vertex(channel_b, 3,
                                                 vertexlist[0],
                                                 self.my_testmodel)
        #print 'Channel_b:\n', channel_b.nice_string()

        # h > t~ t t t~ t~
        channel_c = decay_objects.Channel({'vertices': base_objects.VertexList(\
                    [vert_1_id, vertexlist[5]])})

        # Add t > b w+ to 1st t
        channel_c = higgs.connect_channel_vertex(channel_c, 0,
                                                 vertexlist[2],
                                                 self.my_testmodel)
        #print '\n', channel_c.nice_string()

        # Initiate channel_c
        # Add t~ > b~ w- to 1st t~
        channel_c = higgs.connect_channel_vertex(channel_c, 2,
                                                 vertexlist[2],
                                                 self.my_testmodel)
        #print channel_c.nice_string()

        # Add t~ > b~ w- w- to final t~
        channel_c = higgs.connect_channel_vertex(channel_c, 6,
                                                 vert_2_id,
                                                 self.my_testmodel)
        #print channel_c.nice_string()

        # Add w- > e- ve~ to 2nd w- in t~ decay chain
        channel_c = higgs.connect_channel_vertex(channel_c, 1,
                                                 w_muvmu,
                                                 self.my_testmodel)
        #print channel_c.nice_string()

        # Add w- > mu vm~ to 1st w- in t~ decay chain
        channel_c = higgs.connect_channel_vertex(channel_c, 3,
                                                 w_muvmu,
                                                 self.my_testmodel)
        #print 'Channel_c:\n', channel_c.nice_string()
        self.assertTrue(decay_objects.Channel.check_channels_equiv_rec(channel_a, 4, channel_b, 2))                        
        self.assertTrue(decay_objects.Channel.check_channels_equiv_rec(channel_a, -1, channel_b, -1))
        self.assertFalse(decay_objects.Channel.check_channels_equiv_rec(channel_a, -1, channel_c, -1))

        self.assertTrue(decay_objects.Channel.check_channels_equiv(channel_a,
                                                                   channel_b))
        self.assertFalse(decay_objects.Channel.check_channels_equiv(channel_a,
                                                                    channel_c))
    def test_findchannels(self):
        """ Test of the find_channels functions."""

        higgs = self.my_testmodel.get_particle(25)
        # Test exceptions of find_channels
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.find_channels,
                          'non_int', self.my_testmodel)
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.find_channels,
                          4, higgs)
        non_sm = copy.copy(higgs)
        non_sm.set('pdg_code', 800)
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.find_channels,
                          non_sm, self.my_testmodel)
        
        # Create two equivalent channels
        # h > z (z > e e~)
        vert_0 = self.h_tt_bbmmvv.get('vertices')[-1] 
        vert_1 = import_vertexlist.full_vertexlist[(13, 25)]
        vert_2 = import_vertexlist.full_vertexlist[(60, 23)]
        #print vert_1, vert_2
        channel_a = decay_objects.Channel({'vertices': base_objects.VertexList(\
                    [vert_0])})
        channel_b = decay_objects.Channel({'vertices': base_objects.VertexList(\
                    [vert_0])})        
        channel_a = higgs.connect_channel_vertex(channel_a, 0, vert_1,
                                                self.my_testmodel)
        channel_a = higgs.connect_channel_vertex(channel_a, 0, vert_2,
                                                self.my_testmodel)
        channel_b = higgs.connect_channel_vertex(channel_b, 0, vert_1,
                                                self.my_testmodel)
        channel_b = higgs.connect_channel_vertex(channel_b, 1, vert_2,
                                                self.my_testmodel)
        channel_a.calculate_orders(self.my_testmodel)
        channel_b.calculate_orders(self.my_testmodel)
        channel_a.get_apx_decaywidth(self.my_testmodel)
        channel_b.get_apx_decaywidth(self.my_testmodel)
        #print channel_a.nice_string(), '\n', channel_b.nice_string()

        # Create two equivalent channels
        # h > w+ w- > e+ ve~ e- ve
        vert_3 = import_vertexlist.full_vertexlist[(7, 25)]
        vert_4 = import_vertexlist.full_vertexlist[(63, 24)]
        channel_c = decay_objects.Channel({'vertices': base_objects.VertexList(\
                    [vert_0])})
        channel_d = decay_objects.Channel({'vertices': base_objects.VertexList(\
                    [vert_0])})        
        channel_c = higgs.connect_channel_vertex(channel_c, 0, vert_3,
                                                self.my_testmodel)
        channel_c = higgs.connect_channel_vertex(channel_c, 1, vert_4,
                                                self.my_testmodel)
        channel_c = higgs.connect_channel_vertex(channel_c, 2, vert_4,
                                                self.my_testmodel)
        channel_d = higgs.connect_channel_vertex(channel_d, 0, vert_3,
                                                self.my_testmodel)
        channel_d = higgs.connect_channel_vertex(channel_d, 0, vert_4,
                                                self.my_testmodel)
        channel_d = higgs.connect_channel_vertex(channel_d, 2, vert_4,
                                                self.my_testmodel)
        print channel_c.nice_string(), '\n', channel_d.nice_string()
        channel_c.calculate_orders(self.my_testmodel)
        channel_d.calculate_orders(self.my_testmodel)
        
        # Test of find_channels
        # Without running find_vertexlist before, but the program should run it
        # automatically. Also for find_stable_particles
        self.my_testmodel.find_channels(self.my_testmodel.get_particle(5), 3)
        self.assertFalse(self.my_testmodel.get_particle(5).get_channels(3, True))
        self.assertTrue(self.my_testmodel['stable_particles'])

        higgs.find_channels(3, self.my_testmodel)
        higgs.find_channels_nextlevel(self.my_testmodel)
        result1 = higgs.get_channels(3, True)
        print result1.nice_string()
        # Test if the equivalent channels appear only once.

        # For both has_idpart and not has_idpart channels
        self.assertEqual((result1.count(channel_b)+ result1.count(channel_a)),1)

        # Test if the 2bodymassdiff calculated during
        # find_channels_nextlevel is right.
        self.assertAlmostEqual(higgs.get('2body_massdiff'), decay_objects.MH-2*decay_objects.MB)

        # Set MH < MW to get the desire channels.
        decay_objects.MH = 50
        channel_c.get_apx_decaywidth(self.my_testmodel)
        channel_d.get_apx_decaywidth(self.my_testmodel)
        higgs['decay_channels'] = {}
        higgs.find_channels(3, self.my_testmodel)
        higgs.find_channels_nextlevel(self.my_testmodel)
        result2 = higgs.get_channels(4, True)
        print result2.nice_string()
        self.assertEqual((result2.count(channel_c)+ result2.count(channel_d)),1)

        """ Test on MSSM, to get a feeling on the execution time. """        
        mssm = import_ufo.import_model('mssm')
        param_path = os.path.join(_file_path,'../input_files/param_card_mssm.dat')
        decay_mssm = decay_objects.DecayModel(mssm, force=True)
        decay_mssm.read_param_card(param_path)
        
        susy_higgs = decay_mssm.get_particle(25)
        susy_higgs.find_channels(3, decay_mssm)
        #susy_higgs.find_channels_nextlevel(decay_mssm)
        #decay_mssm.find_all_channels(3)

        # Test the calculation of branching ratios
        # The total br should be unity
        total_br = sum([amp['apx_br'] for amp in susy_higgs.get_amplitudes(2)])
        total_br += sum([amp['apx_br'] for amp in susy_higgs.get_amplitudes(3)])
        self.assertAlmostEqual(total_br, 1.)

        # Test if the err is from the off-shell 3-body channels
        err = sum([c['apx_decaywidth_nextlevel'] \
                       for c in susy_higgs.get_channels(3, False)])
        self.assertAlmostEqual(err, susy_higgs['apx_decaywidth_err'])

                                           
    def test_apx_decaywidth(self):
        """ Test for the approximation of decay rate"""

        full_sm_base = import_ufo.import_model('sm')
        full_sm = decay_objects.DecayModel(full_sm_base, True)

        higgs = self.my_testmodel.get_particle(25)
        # Set the higgs mass < Z-boson mass so that identicle particles appear
        # in final state
        MH_new = 91
        decay_objects.MH = MH_new
        higgs.find_channels(4, self.my_testmodel)


        # Test of the symmetric factor
        print higgs.get_channels(3, False).nice_string()
        #print higgs.get_channels(4, True).nice_string()
        h_zz_llll_1 = higgs.get_channels(4, True)[5]
        h_zz_llll_2 = higgs.get_channels(4, True)[6]
        # higgs > w (w > l vl)
        channel_1 = higgs.get_channels(3, True)[0]
        print 'h_zz_llll_symm:', h_zz_llll_1.nice_string(), '\n',\
            'h_zz_llll_no_symm:', h_zz_llll_2.nice_string(), '\n',\
            'channel_1:', channel_1.nice_string()

        h_zz_llll_1.get_apx_psarea(self.my_testmodel)
        h_zz_llll_2.get_apx_psarea(self.my_testmodel)
        self.assertEqual(4, h_zz_llll_1['s_factor'])
        self.assertEqual(1, h_zz_llll_2['s_factor'])


        # Test of the get_apx_fnrule

        MW = channel_1.get('final_mass_list')[-1]
        #print channel_1.get('final_mass_list')
        #print channel_1.get_apx_matrixelement_sq(self.my_testmodel)
        #print 'Vertor boson, onshell:', \
        #    channel_1.get_apx_fnrule(24, 0.5,
        #                            False, self.my_testmodel)
        q_offshell = 10
        q_offshell_2 = 88
        q_onshell = 200
        self.assertAlmostEqual(channel_1.get_apx_fnrule(24, q_onshell, 
                                                  True, self.my_testmodel),
                         (1+1/(MW ** 2)*q_onshell **2))
        self.assertAlmostEqual(channel_1.get_apx_fnrule(24, q_offshell, 
                                                  False, self.my_testmodel),
                          ((1-2*((q_offshell/MW) ** 2)+(q_offshell/MW) ** 4)/ \
                               ((q_offshell**2-MW **2)**2)))
        # Fermion
        self.assertEqual(channel_1.get_apx_fnrule(11, q_onshell, 
                                                  True, self.my_testmodel),
                         q_onshell*2)
        self.assertEqual(channel_1.get_apx_fnrule(6, q_onshell, 
                                                  True, self.my_testmodel),
                         q_onshell*2)
        self.assertAlmostEqual(channel_1.get_apx_fnrule(6, q_offshell, 
                                                  False, self.my_testmodel),
                         q_offshell**2/(q_offshell ** 2 - decay_objects.MT **2)\
                             ** 2)
        # Scalar
        self.assertEqual(channel_1.get_apx_fnrule(25, q_onshell, 
                                                  True, self.my_testmodel),
                         1)

        self.assertAlmostEqual(channel_1.get_apx_fnrule(25, q_offshell_2, 
                                                  False, self.my_testmodel),
                               1/(q_offshell_2 ** 2 - MH_new ** 2)**2)

        # Test of matrix element square calculation

        E_mean = (MH_new-MW)/3
        #print channel_1.get_apx_fnrule(-24, 2*E_mean, False, full_sm)
        #print abs(decay_objects.GC_11) **2
        #print channel_1.get_apx_fnrule(24, E_mean+MW, True, self.my_testmodel)
        #print abs(decay_objects.GC_22) **2
        # couplings: h > w w, w > e ve
        #print self.my_testmodel.get_interaction(7), self.my_testmodel.get_interaction(63)
        self.assertAlmostEqual(
            channel_1.get_apx_matrixelement_sq(self.my_testmodel),
            ((E_mean**2*4*(1-2*(2*E_mean/MW)**2+(2*E_mean/MW)**4)\
                  /(((2*E_mean)**2-MW **2)**2))*\
                 (1+(1/MW*(E_mean+MW))**2)*\
                 abs(decay_objects.GC_64) **2*\
                 abs(decay_objects.GC_33) **2)
            )
        
        tau = full_sm.get_particle(15)
        tau.find_channels(3, full_sm)
        tau_qdecay = tau.get_channels(3, True)[0]
        tau_ldecay = tau.get_channels(3, True)[2]
        #print tau_qdecay.nice_string()
        self.assertAlmostEqual(tau_qdecay.get_apx_decaywidth(full_sm)/ \
                                   tau_ldecay.get_apx_decaywidth(full_sm), 3)
        MTAU = abs(eval('decay_objects.' + tau.get('mass')))
        # Using the coupling constant of w > e ve
        self.assertAlmostEqual(tau_qdecay.get_apx_matrixelement_sq(full_sm),
                               ((MTAU/3) **3 *8*3*MTAU*
                                (1-2*(2*MTAU/(3*MW))**2 +(2*MTAU/(3*MW))**4)/ \
                                    ((2*MTAU/3) ** 2 - MW **2) **2 *\
                                    abs(decay_objects.GC_33) **4))

        # Test for off-shell estimation of matrix element
        h_ww_wtb = higgs.get_channels(3, False)[0]
        E_est_mean = MH_new/4
        #h_ww_wtb.get_apx_decaywidth_nextlevel(full_sm)
        #print h_ww_wtb.nice_string()
        # coupl: as the onshell case
        self.assertAlmostEqual(h_ww_wtb.get_apx_matrixelement_sq(full_sm),
                               h_ww_wtb.get_apx_fnrule(5, E_est_mean,
                                                       True, full_sm)* \
                                   h_ww_wtb.get_apx_fnrule(-6, E_est_mean,
                                                      True, full_sm)* \
                                   h_ww_wtb.get_apx_fnrule(24, E_est_mean,
                                                           True, full_sm)* \
                                   h_ww_wtb.get_apx_fnrule(24, MH_new,
                                                           False, full_sm, \
                                                               est = True)*\
                                   h_ww_wtb.get_apx_fnrule(25, MH_new,
                                                           True, full_sm)*\
                                   abs(decay_objects.GC_64) **2 *\
                                   abs(decay_objects.GC_33) **2)

        # Test of phase space area calculation
        #print 'Tau decay ps_area', tau_qdecay.get_apx_psarea(full_sm)
        self.assertAlmostEqual(tau_qdecay.calculate_apx_psarea(1.777, [0,0]),
                                1/(8*math.pi))
        self.assertAlmostEqual(tau_qdecay.calculate_apx_psarea(1.777, [0,0,0]),
                               0.000477383, 5)
        self.assertAlmostEqual(channel_1.get_apx_psarea(full_sm), 0.0042786859,5)

        # Test for estimation of off-shell case
        self.assertAlmostEqual(h_ww_wtb.get_apx_psarea(full_sm),
                                1/512/math.pi **3 * 0.8 * MH_new **2)


        # Test of decay width
        self.assertAlmostEqual(tau_qdecay.get_apx_decaywidth(full_sm),
                               (0.5/1.777)*tau_qdecay.get_apx_psarea(full_sm)*\
                                   tau_qdecay.get_apx_matrixelement_sq(full_sm))


        # Test of the estimated further decay width of off shell channel
        # Channels impossible for next-level decay
        self.assertEqual(h_ww_wtb.get_apx_decaywidth_nextlevel(full_sm), 0.)
        # Channels possible for next-level decay
        full_sm.find_all_channels(3)
        h_zz_zbb = higgs.get_channels(3, False)[2]
        #print "h_zz_zbb:", h_zz_zbb.nice_string()
        WZ = full_sm.get_particle(23).get('apx_decaywidth')
        WW = full_sm.get_particle(24).get('apx_decaywidth')

        ratio = (1+ WZ*abs(decay_objects.MZ)/MH_new*\
                     (1/4/math.pi)*MH_new **3 *0.8/ \
                     h_zz_zbb.get_apx_fnrule(23, decay_objects.MZ,
                                             True, full_sm)/ \
                     h_zz_zbb.get_apx_fnrule(23, 0.5*MH_new,
                                             True, full_sm)* \
                     h_zz_zbb.get_apx_fnrule(23, MH_new,
                                             False, full_sm, True))

        self.assertAlmostEqual(\
            h_zz_zbb.get_apx_decaywidth(full_sm)*(ratio-1),
            h_zz_zbb.get_apx_decaywidth_nextlevel(full_sm), 5)




        # Test of the Brett-Wigner correction of propagator
        self.assertAlmostEqual(channel_1.get_apx_fnrule(24, q_offshell, 
                                                 False, full_sm),
                               ((1-2*((q_offshell/MW) ** 2)+(q_offshell/MW) ** 4)/ \
                             (((q_offshell**2-MW **2)**2+MW**2*WW**2)))
                               )


        model_base = import_ufo.import_model('mssm')
        param_path = os.path.join(_file_path,'../input_files/param_card_mssm.dat')
        model = decay_objects.DecayModel(model_base, force=True)
        model.read_param_card(param_path)
        model.find_all_channels(2)

        channel_2 = copy.deepcopy(channel_1)
        channel_2['vertices'][0]['legs'][0]['id'] = -1000024
        channel_2['vertices'][0]['legs'][1]['id'] = 1000024
        channel_2['vertices'][0]['legs'][2]['id'] = 23
        channel_2['vertices'][0]['id'] = 128
        channel_2['vertices'][1]['legs'][0]['id'] = 1000035
        channel_2['vertices'][1]['legs'][1]['id'] = 23
        channel_2['vertices'][1]['legs'][2]['id'] = 1000025
        channel_2['vertices'][1]['id'] = 516
        channel_2['vertices'][2]['legs'][0]['id'] = 1000025
        channel_2['vertices'][2]['legs'][1]['id'] = 1000025
        channel_2['vertices'][2]['id'] = 0
        channel_2['onshell'] = 0
        #print channel_2.get_onshell(model)
        channel_2.get_final_legs()
        #print channel_2.nice_string()
        #print channel_2.get_apx_matrixelement_sq(model)
        #print channel_2.get_apx_psarea(model)
        #print channel_2.get_apx_decaywidth(model)
        #print channel_2.get_apx_decaywidth_nextlevel(model)
        #print channel_2.nice_string()

    def test_colormultiplicity(self):
        """ Test the color_multiplicity_def of the DecayModel object and
            the get_color_multiplicity function of Channel object. """

        # Test for exception 
        self.assertRaises(decay_objects.DecayModel.PhysicsObjectError,
                          self.my_testmodel.color_multiplicity_def,
                          'a')

        self.assertRaises(decay_objects.DecayModel.PhysicsObjectError,
                          self.my_testmodel.color_multiplicity_def,
                          [1, 'a'])

        # Test the color_multiplicity_def
        self.assertEqual(self.my_testmodel.color_multiplicity_def([6,3]),
                         [(3, 2), (8, 3./4)])
        
        # Test the get_color_multiplicity
        # Two-body decay
        self.assertEqual(self.h_tt_bbmmvv.get_color_multiplicity(\
                8, [3,3], self.my_testmodel, True),
                         0.5)


    def test_apx_decaywidth_full_read_MG4_paramcard(self):
        """ The test to show the estimation of decay width.
            and also read the param_card of MG4. 
            Also test the find_all_channels including:
            1. unity of total branching ratio
            2. the apx_decaywidth_nextlevel comes from the right level."""

        model_name = 'mssm'
        test_param_card = False
        test_param_card_suffix = 'test1'
        smart_find = True
        prec = 5E-3
        channel_number = 2


        # Read model_name
        model_base = import_ufo.import_model(model_name)
        model = decay_objects.DecayModel(model_base, True)

        # Read MG5 param_card
        if test_param_card:
            MG5_param_path = os.path.join(_file_path,
                                        '../input_files/param_card_'\
                                            +model_name \
                                            +'_'\
                                            +test_param_card_suffix
                                            +'.dat')
        else:
            MG5_param_path = os.path.join(_file_path,
                                        '../input_files/param_card_'\
                                            +model_name \
                                            +'.dat')
        model.read_param_card(MG5_param_path)
        
        # Find channels before read MG4 param_card (use smart function)
        if smart_find:
            model.find_all_channels_smart(prec)
        else:
            model.find_all_channels(channel_number)

        # Read MG4 param_card
        if model_name == "mssm":
            if test_param_card:
                MG4_param_path = os.path.join(_file_path,
                                              '../input_files/param_card_test1.dat')
            else:
                MG4_param_path = os.path.join(_file_path,
                                              '../input_files/param_card_0.dat')

            model.read_MG4_param_card_decay(MG4_param_path)

        # Write decay summary and the decay table
        if test_param_card:
            """model.write_summary_decay_table(model_name\
                                                + '_decay_summary_'\
                                                + test_param_card_suffix \
                                                + '.dat')"""
            model.write_decay_table(MG5_param_path, 'cmp', 
                                    model_name\
                                        + '_decaytable_'\
                                        + test_param_card_suffix \
                                        + '.dat')
        else:
            # file name 1: default name
            #model.write_summary_decay_table()
            model.write_decay_table(MG5_param_path, 'cmp')


        # Test the sum of branching ratios is unity
        part = model.get_particle(25)
        total_br = sum([sum([amp['apx_br'] for amp in part.get_amplitudes(i)]) \
                            for i in range(2, part.get_max_level()+1)])
        self.assertAlmostEqual(total_br, 1.)

        # Test if the err is from the off-shell 3-body channels
        if part.get_max_level() > 2:
            err = sum([c['apx_decaywidth_nextlevel'] \
                           for c in part.get_channels(part.get_max_level(), 
                                                      False)])
            self.assertAlmostEqual(err/part.get('apx_decaywidth'), part['apx_decaywidth_err'])

        """# Test if the channels are find wisely
        for part in model['particles']:
            self.assertTrue(prec > part.get('apx_decaywidth_err'))

        # Check if the max_level is expected.
        self.assertEqual(model.get_particle(1000016).get_max_level(), 2)
        self.assertEqual(model.get_particle(25).get_max_level(), 3)"""

        # Miscellaneous
        # Test if the calculated ratio is float or None
        """for part in model.get('particles'):
            print part.get_pdg_code(), part.get('2body_massdiff')
            #n_max = len(part['decay_amplitudes'].keys())
            for n in range(2,n_max+2):
                for amp in part.get_amplitudes(n):
                    self.assertTrue(isinstance(amp['exa_decaywidth'], bool) or \
                                        isinstance(amp['exa_decaywidth'], float))
        """
        particle = model.get_particle(1000035)
        particleb = model.get_particle(2000001)
        #channels = particleb.get_channels(3, False)
        #channels.sort(decay_objects.channelcmp_width)
        #print [c.nice_string() for c in channels[:100]]
        a = particle.get_amplitudes(3)[2]
        print a.nice_string()#, a['diagrams']
        print model.get_interaction(166)
        print decay_objects.GC_415, decay_objects.GC_681

        """
        #print particle.get_amplitude([-11, 2000011])['diagrams'].nice_string()
        print model.get_interaction(390)
        print decay_objects.GC_780, decay_objects.GC_752
        print model.get_interaction(388)
        print decay_objects.GC_757, decay_objects.GC_785
        
        print particle.get_amplitude([2000001, -1]).decaytable_string()
        print particle.get_amplitude([2000001, -1])['diagrams'][0].get_apx_psarea(model)
        print particle.get_amplitude([2000001, -1])['apx_decaywidth']
        print particle.get_amplitude([2000001, -1])['exa_decaywidth']

        #print particleb.get_amplitude([-1000024, 16, 22]).nice_string()

        #print particle.get_amplitude([-11, 2000011])['diagrams'][0].get_apx_matrixelement_sq(model)        
        #print particle.get_amplitude([-11, 2000011])['exa_decaywidth']

        #for part in model.get('particles'):
        #    print part['pdg_code'], part['decay_width']

        #particle.calculate_branch_ratio()
        #print decay_objects.MT, decay_objects.MW
        #print decay_objects.GC_857, decay_objects.GC_733, decay_objects.GC_437, decay_objects.GC_665
        #print particle.estimate_width_error()
        #print len(particle.get_channels(3, False))
        #print particle.get_channels(3, False)[0].nice_string(),\
        #    particle.get('apx_decaywidth')
        """



#===============================================================================
# Test_DecayAmplitude
#===============================================================================
class Test_DecayAmplitude(unittest.TestCase):
    """ Test for the DecayAmplitude and DecayAmplitudeList object."""

    def setUp(self):
        """ Set up necessary objects for the test"""
        self.my_testmodel_base = import_ufo.import_model('sm')
        #Import a model from my_testmodel
        self.my_testmodel = decay_objects.DecayModel(self.my_testmodel_base, True)
        param_path = os.path.join(_file_path,'../input_files/param_card_sm.dat')
        self.my_testmodel.read_param_card(param_path)

        my_channel = decay_objects.Channel()
        h_tt_bbmmvv = decay_objects.Channel()

        # Simplify the model
        particles = self.my_testmodel.get('particles')
        interactions = self.my_testmodel.get('interactions')
        inter_list = copy.copy(interactions)
        # Pids that will be removed
        no_want_pid = [1, 2, 3, 4, 15, 16, 21]
        for pid in no_want_pid:
            particles.remove(self.my_testmodel.get_particle(pid))

        for inter in inter_list:
            if any([p.get('pdg_code') in no_want_pid for p in \
                        inter.get('particles')]):
                interactions.remove(inter)

        # Set a new name
        self.my_testmodel.set('name', 'my_smallsm')
        self.my_testmodel.set('particles', particles)
        self.my_testmodel.set('interactions', interactions)

        #Setup the vertexlist for my_testmodel and save this model (optional)
        import_vertexlist.make_vertexlist(self.my_testmodel)
        #save_model.save_model(os.path.join(MG5DIR, 'tests/input_files', 
        #self.my_testmodel['name']), self.my_testmodel)
    

    def test_init_setget(self):
        """ Test the set and get function of"""

        # Setup higgs and lower its mass
        higgs = self.my_testmodel.get_particle(25)
        decay_objects.MH = 50

        # Set channels
        self.my_testmodel.find_all_channels(4)
        #print higgs.get_channels(4, True).nice_string()
        h_mmvv_1 = higgs.get_channels(4, True)[5]
        h_mmvv_2 = higgs.get_channels(4, True)[9]

        # Test the initialization
        amplt_h_mmvv = decay_objects.DecayAmplitude(h_mmvv_1,
                                                      self.my_testmodel)
        # goal id list for legs in process
        goal_id_list = [-12, -11, 11, 12, 25]
        self.assertEqual(sorted([l.get('id') for l in amplt_h_mmvv.get('process').get('legs')]), goal_id_list)

        # Check the legs in process
        for l in amplt_h_mmvv.get('process').get('legs'):
            if l.get('id') != 25:
                self.assertTrue(l.get('state'))
            else:
                self.assertFalse(l.get('state'))
            self.assertEqual(0, l.get('number'))

        # Test the set and get in Amplitude
        goal_width = h_mmvv_1.get('apx_decaywidth')
        self.assertEqual(amplt_h_mmvv.get('apx_decaywidth'), goal_width)
        goal_width += h_mmvv_2.get('apx_decaywidth')
        amplt_h_mmvv.get('diagrams').append(h_mmvv_2)
        amplt_h_mmvv.reset_width_br()

        # Test if the reset works.
        self.assertEqual(amplt_h_mmvv['apx_decaywidth'], 0.)
        # Test the get for decaywidth and branch ratio.
        self.assertEqual(amplt_h_mmvv.get('apx_decaywidth'), goal_width)
        self.assertEqual(amplt_h_mmvv.get('apx_br'),
                         goal_width/higgs.get('apx_decaywidth'))
        WH = higgs['apx_decaywidth']
        higgs['apx_decaywidth'] = 0.
        amplt_h_mmvv.reset_width_br()
        # WARNING should show for getting br from zero-width particle.
        amplt_h_mmvv.get('apx_br')

        # Test for exceptions in set get of Amplitude
        wrong_prop_list = {'process': [1, 'a', base_objects.Diagram()],
                           'diagrams': [1, 'a', base_objects.Diagram()]}
        for key, proplist in wrong_prop_list.items():
            for prop in proplist:
                self.assertRaises(decay_objects.DecayAmplitude.PhysicsObjectError,
                                  amplt_h_mmvv.filter,
                                  key, prop)

        # Test for set and get in DecayParticle
        my_amplist = decay_objects.DecayAmplitudeList([amplt_h_mmvv])
        higgs.set('decay_amplitudes', {4: my_amplist})
        self.assertEqual(higgs.get('decay_amplitudes'), {4: my_amplist})

        # Test for exceptions
        valuelist = ['nondict', {'a': my_amplist}, {4: base_objects.Process()}]
        for value in valuelist:
            self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                              higgs.filter,
                              'decay_amplitudes', value)            

        # Test for set_amplitudes and get_amplitudes
        higgs.set_amplitudes(4, decay_objects.DecayAmplitudeList())
        self.assertEqual(higgs.get_amplitudes(4), 
                         decay_objects.DecayAmplitudeList())

        # Test the set from normal list of Amplitude
        higgs.set_amplitudes(4, [amplt_h_mmvv])
        self.assertEqual(higgs.get_amplitudes(4), my_amplist)
        self.assertEqual(higgs.get_amplitudes(6), None)

        # Test for exceptions
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.get_amplitudes, 'a')
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.set_amplitudes,
                          'a', decay_objects.DecayAmplitudeList())
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.set_amplitudes,
                          4, decay_objects.DecayAmplitude())

        # Test for get_amplitude
        #higgs.get_amplitudes(4)
        self.assertEqual(higgs.get_amplitude([12, -11, -12, 11]),
                         amplt_h_mmvv)
        self.assertEqual(higgs.get_amplitude([-12, -12, 11, 12]),
                         None)

        # Test for exception
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.get_amplitude,
                          'Non-list')
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.get_amplitude,
                          ['a', 1.23])

    def test_group_channels2amplitudes(self):
        """ Test the group_channels_2_amplitudes function."""

        # Setup higgs and lower its mass
        higgs = self.my_testmodel.get_particle(25)
        decay_objects.MH = 50

        # Set channels and amplitude
        self.my_testmodel.find_all_channels(4)
        print higgs.get_channels(4, True).nice_string()
        h_mmvv_1 = higgs.get_channels(4, True)[0]
        h_mmvv_2 = higgs.get_channels(4, True)[9]
        amplt_h_mmvv = decay_objects.DecayAmplitude(h_mmvv_1,
                                                      self.my_testmodel)
        # Test for exceptions in arguments.
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.group_channels_2_amplitudes,
                          'a', self.my_testmodel)
        self.assertRaises(decay_objects.DecayParticle.PhysicsObjectError,
                          higgs.group_channels_2_amplitudes,
                          3, 'a')

        # Test if the group works
        higgs.find_channels(4, self.my_testmodel)
        higgs.group_channels_2_amplitudes(4, self.my_testmodel)
        #print higgs.get_amplitudes(4).nice_string()

        # Grouping will calculate the decaywidth but not the apx_br
        amplt_h_mmvv.get('apx_decaywidth')

        self.assertTrue(amplt_h_mmvv in higgs.get_amplitudes(4))


    def test_decaytable_string(self):
        """ Test the decaytable_string """

        # Setup higgs and lower its mass
        higgs = self.my_testmodel.get_particle(25)
        decay_objects.MH = 50

        # Set channels and amplitude
        self.my_testmodel.find_all_channels(4)
        amp_list = higgs.get_amplitudes(4)
        # Test for exception
        self.assertRaises(decay_objects.DecayAmplitude.PhysicsObjectError,
                          amp_list.decaytable_string,'wrongformat')
        # Test for type
        self.assertTrue(isinstance(amp_list.decaytable_string('full'), str))
        self.assertTrue(isinstance(amp_list.decaytable_string(), str))

        # Test for decaytable_string from DecayParticle
        self.assertTrue(isinstance(higgs.decaytable_string(), str))

        self.my_testmodel.write_decay_table(os.path.join(_file_path,'../input_files/param_card_sm.dat'), 
                                            'full', 'mysmallmodel')

        #print self.my_testmodel['parameters'], '\n',\
        #    self.my_testmodel['functions']

        
if __name__ == '__main__':
    unittest.unittest.main()
