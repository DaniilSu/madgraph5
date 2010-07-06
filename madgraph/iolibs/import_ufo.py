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
""" How to import a UFO model to the MG5 format """

import sys
import logging

import madgraph
import madgraph.core.base_objects as base_objects
import madgraph.core.color_algebra as color

from madgraph.core.color_algebra import *


logger = logging.getLogger('madgraph.import_ufo')



def import_model(model=None, model_name=None):
    """ a practical and efficient way to import one of those models """

    if model_name:
        model_pos = 'models.%s' % model_name
        __import__(model_pos)   
        model = sys.modules[model_pos]
    elif not model:
        raise madgraph.MadGraph5Error( \
                    'import_ufo.import_model should have at least one argument')
    ufo2mg5_converter = converter_ufo_mg5(model, auto=False)
    return ufo2mg5_converter.load_model()
    

class converter_ufo_mg5(object):
    """Convert a UFO model to the MG5 format"""

    def __init__(self, model, auto=False):
        """ initialize empty list for particles/interactions """
        
        self.particles = base_objects.ParticleList()
        self.interactions = base_objects.InteractionList()
        self.model = base_objects.Model()
        self.model.set('particles', self.particles)
        self.model.set('interactions', self.interactions)
        
        self.ufomodel = model
        
        if auto:
            self.load_model()

    def load_model(self):
        """load the different of the model first particles then interactions"""

        logger.info('load particle')
        for particle_info in self.ufomodel.all_particles:            
            self.add_particle(particle_info)
            
        logger.info('load vertex')
        for interaction_info in self.ufomodel.all_vertices:
            self.add_interaction(interaction_info)
        
        return self.model
        
    
    def add_particle(self, particle_info):
        """ convert and add a particle in the particle list """
        
        # MG5 have only one entry for particle and anti particles.
        #UFO has two. use the color to avoid duplictions
        if particle_info.pdg_code < 0:
            return
        
        # MG5 doesn't use ghost (use unitary gauges)
        if particle_info.spin < 0:
            return 
        # MG5 doesn't use goldstone boson 
        if hasattr(particle_info, 'GoldstoneBoson'):
            if particle_info.GoldstoneBoson:
                return
               
        # Initialize a particles
        particle = base_objects.Particle()

        nb_property = 0   #basic check that the UFO information is complete
        # Loop over the element defining the UFO particles
        for key,value in particle_info.__dict__.items():
            # Check if we use it in the MG5 definition of a particles
            if key in base_objects.Particle.sorted_keys:
                nb_property +=1
                if key in ['name', 'antiname']:
                    particle.set(key, value.lower())
                elif key == 'charge':
                    particle.set(key, float(value))
                else:
                    particle.set(key, value)
            
        assert(12 == nb_property) #basic check that all the information is there         
        
        # Identify self conjugate particles
        if particle_info.name == particle_info.antiname:
            particle.set('self_antipart', True)
            
        # Add the particles to the list
        self.particles.append(particle)


    def add_interaction(self, interaction_info):
        """add an interaction in the MG5 model. interaction_info is the 
        UFO vertices information."""
        
        # Initialize a new interaction with a new id tag
        interaction = base_objects.Interaction({'id':len(self.interactions)+1})
        
        # Import particles content:
        particles = [self.model.get_particle(particle.pdg_code) \
                                    for particle in interaction_info.particles]

        if None in particles:
            # Interaction with a ghost/goldstone
            return 
            
        particles = base_objects.ParticleList(particles)
        
        interaction.set('particles', particles)       
        
        # Import Lorentz content:
        names = [helas.name for helas in interaction_info.lorentz]
        interaction.set('lorentz', names)
        
        # Import couplings/order information:
        mg5_coupling = {}
        mg5_order = {}
        for key, value in interaction_info.couplings.items():
            mg5_coupling[key] = value.name
            mg5_order.update(value.order)
        interaction.set('couplings', mg5_coupling)
        interaction.set('orders', mg5_order)

        # Import color information:
        colors = [self.treat_color(color_obj) for color_obj in \
                                    interaction_info.color]
        
        interaction.set('color', colors)

        # add to the interactions
        self.interactions.append(interaction)
        
    @staticmethod
    def treat_color(data_string):
        """ convert the string to ColorStirng"""
        
        # Convert the string in order to be able to evaluate it
        # Change identity in color.TC
        data_string = data_string.replace('Identity(','color.T(')
        # Change convention for summed indices
        data_string = data_string.replace(',a',',-')
        data_string = data_string.replace('(a','(-')
        data_string = data_string.replace(',\'a',',-')
        data_string = data_string.replace('(\'a','(-')
        data_string = data_string.replace('\'','')
            
        output = data_string.split('*')
        output = color.ColorString([eval(data).shift_indices() for data in output if data !='1'])
        for i in range(len(output)):
            if isinstance(output[i], color.T):
                output[i][-1], output[i][-2] = output[i][-2], output[i][-1] 
        return output
    
    def check_standard_name(self):
        """check that all SM particles have The same name as MG4 version"""
        
        sm_data = {
                # quark
                1: ['d', 'd~'], 2: ['u', 'u~'], 3: ['s', 's~'], 4: ['c', 'c~'],
                5: ['b', 'b~'], 6: ['t', 't~'],
                # lepton
                11: ['e-','e+'], 12: ['ve','ve~'], 13: ['mu-','mu+'],
                14: ['vm','vm~'], 15: ['ta-','ta+'],16: ['vt','vt~'], 
                # boson
                21: ['g'], 22: ['a'], 23: ['z'], 24: ['w+','w-'], 25: ['h']
                }
        to_add ={}
        
        for particle in self.particles:
            pdg = particle.get_pdg_code()
            names = [particle.get_name()]
            if particle.get('antiname') != particle.get_name():
                names.append(particle.get('antiname'))
                
            if sm_data.has_key(pdg):
                if names == sm_data[pdg]:
                    continue
                for i in range(len(names)):
                    to_add[sm_data[pdg][i]] = [(-1) ** i * pdg] 
                    
        return to_add
                    
                    
            
        
        
    
