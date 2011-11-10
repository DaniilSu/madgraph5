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
"""A user friendly command line interface to access MadGraph features.
   Uses the cmd package for command interpretation and tab completion.
"""

import atexit
import logging
import optparse
import os
import pydoc
import re
import subprocess
import sys
import traceback
import time

try:
    import readline
    GNU_SPLITTING = ('GNU' in readline.__doc__)
except:
    GNU_SPLITTING = True


import madgraph
from madgraph import MG4DIR, MG5DIR, MadGraph5Error


import madgraph.core.base_objects as base_objects
import madgraph.core.diagram_generation as diagram_generation
import madgraph.core.drawing as draw_lib
import madgraph.core.helas_objects as helas_objects

import madgraph.iolibs.drawing_eps as draw
import madgraph.iolibs.export_cpp as export_cpp
import madgraph.iolibs.export_v4 as export_v4
import madgraph.iolibs.helas_call_writers as helas_call_writers
import madgraph.iolibs.file_writers as writers
import madgraph.iolibs.files as files
import madgraph.iolibs.group_subprocs as group_subprocs
import madgraph.iolibs.import_v4 as import_v4
import madgraph.iolibs.misc as misc
import madgraph.iolibs.save_load_object as save_load_object

import madgraph.interface.extended_cmd as cmd
import madgraph.interface.tutorial_text as tutorial_text
import madgraph.interface.launch_ext_program as launch_ext
import madgraph.interface.madevent_interface as madevent_interface

import madgraph.various.process_checks as process_checks

import models as ufomodels
import models.import_ufo as import_ufo

# Special logger for the Cmd Interface
logger = logging.getLogger('cmdprint') # -> stdout
logger_stderr = logging.getLogger('fatalerror') # ->stderr
logger_tuto = logging.getLogger('tutorial') # -> stdout include instruction in  
                                            #order to learn MG5

#===============================================================================
# CmdExtended
#===============================================================================
class CmdExtended(cmd.Cmd):
    """Particularisation of the cmd command for MG5"""

    #suggested list of command
    next_possibility = {
        'start': ['import model ModelName', 'import command PATH',
                      'import proc_v4 PATH', 'tutorial'],
        'import model' : ['generate PROCESS','define MULTIPART PART1 PART2 ...', 
                                   'display particles', 'display interactions'],
        'define': ['define MULTIPART PART1 PART2 ...', 'generate PROCESS', 
                                                    'display multiparticles'],
        'generate': ['add process PROCESS','output [OUTPUT_TYPE] [PATH]','draw .'],
        'add process':['output [OUTPUT_TYPE] [PATH]', 'display processes'],
        'output':['launch','open index.html','history PATH', 'exit'],
        'display': ['generate PROCESS', 'add process PROCESS', 'output [OUTPUT_TYPE] [PATH]'],
        'import proc_v4' : ['launch','exit'],
        'launch': ['open index.html','exit'],
        'tutorial': ['generate PROCESS', 'import model MODEL', 'help TOPIC']
    }
    
    debug_output = 'MG5_debug'
    error_debug = 'Please report this bug on https://bugs.launchpad.net/madgraph5\n'
    error_debug += 'More information is found in \'%s\'.\n' 
    error_debug += 'Please attach this file to your report.'
    
    config_debug = 'If you need help with this issue please contact us on https://answers.launchpad.net/madgraph5\n'

    keyboard_stop_msg = """stopping all operation
            in order to quit mg5 please enter exit"""
    
    # Define the Error Class # Define how error are handle
    InvalidCmd = madgraph.InvalidCmd
    ConfigurationError = MadGraph5Error

    def __init__(self, *arg, **opt):
        """Init history and line continuation"""
        
        # If possible, build an info line with current version number 
        # and date, from the VERSION text file
        info = misc.get_pkg_info()
        info_line = ""

        if info.has_key('version') and  info.has_key('date'):
            len_version = len(info['version'])
            len_date = len(info['date'])
            if len_version + len_date < 30:
                info_line = "#*         VERSION %s %s %s         *\n" % \
                            (info['version'],
                            (30 - len_version - len_date) * ' ',
                            info['date'])

        # Create a header for the history file.
        # Remember to fill in time at writeout time!
        self.history_header = \
        '#************************************************************\n' + \
        '#*                        MadGraph 5                        *\n' + \
        '#*                                                          *\n' + \
        "#*                *                       *                 *\n" + \
        "#*                  *        * *        *                   *\n" + \
        "#*                    * * * * 5 * * * *                     *\n" + \
        "#*                  *        * *        *                   *\n" + \
        "#*                *                       *                 *\n" + \
        "#*                                                          *\n" + \
        "#*                                                          *\n" + \
        info_line + \
        "#*                                                          *\n" + \
        "#*    The MadGraph Development Team - Please visit us at    *\n" + \
        "#*    https://server06.fynu.ucl.ac.be/projects/madgraph     *\n" + \
        '#*                                                          *\n' + \
        '#************************************************************\n' + \
        '#*                                                          *\n' + \
        '#*               Command File for MadGraph 5                *\n' + \
        '#*                                                          *\n' + \
        '#*     run as ./bin/mg5  filename                           *\n' + \
        '#*                                                          *\n' + \
        '#************************************************************\n'
        
        if info_line:
            info_line = info_line[1:]

        logger.info(\
        "************************************************************\n" + \
        "*                                                          *\n" + \
        "*           W E L C O M E  to  M A D G R A P H  5          *\n" + \
        "*                                                          *\n" + \
        "*                                                          *\n" + \
        "*                 *                       *                *\n" + \
        "*                   *        * *        *                  *\n" + \
        "*                     * * * * 5 * * * *                    *\n" + \
        "*                   *        * *        *                  *\n" + \
        "*                 *                       *                *\n" + \
        "*                                                          *\n" + \
        info_line + \
        "*                                                          *\n" + \
        "*    The MadGraph Development Team - Please visit us at    *\n" + \
        "*    https://server06.fynu.ucl.ac.be/projects/madgraph     *\n" + \
        "*                                                          *\n" + \
        "*               Type 'help' for in-line help.              *\n" + \
        "*           Type 'tutorial' to learn how MG5 works         *\n" + \
        "*                                                          *\n" + \
        "************************************************************")
        
        cmd.Cmd.__init__(self, *arg, **opt)
    
    def postcmd(self,stop, line):
        """ finishing a command
        This looks if we have to write an additional text for the tutorial."""
        
        # Print additional information in case of routines fails
        if stop == False:
            return False
        
        args=line.split()
        # Return for empty line
        if len(args)==0:
            return stop
        
        # try to print linked to the first word in command 
        #as import_model,... if you don't find then try print with only
        #the first word.
        if len(args)==1:
            command=args[0]
        else:
            command = args[0]+'_'+args[1].split('.')[0]
        
        try:
            logger_tuto.info(getattr(tutorial_text, command).replace('\n','\n\t'))
        except:
            try:
                logger_tuto.info(getattr(tutorial_text, args[0]).replace('\n','\n\t'))
            except:
                pass
        
        return stop

     
    def get_history_header(self):
        """return the history header""" 
        return self.history_header % misc.get_time_info()

#===============================================================================
# HelpToCmd
#===============================================================================
class HelpToCmd(object):
    """ The Series of help routine for the MadGraphCmd"""    
    
    def help_save(self):
        logger.info("syntax: save %s FILENAME" % "|".join(self._save_opts))
        logger.info("-- save information as file FILENAME")


    def help_load(self):
        logger.info("syntax: load %s FILENAME" % "|".join(self._save_opts))
        logger.info("-- load information from file FILENAME")

    def help_import(self):
        logger.info("syntax: import " + "|".join(self._import_formats) + \
              " FILENAME")
        logger.info("-- imports file(s) in various formats")
        logger.info("")
        logger.info("   import model MODEL[-RESTRICTION] [-modelname]:")
        logger.info("      Import a UFO model.")
        logger.info("      MODEL should be a valid UFO model name")
        logger.info("      Model restrictions are specified by MODEL-RESTRICTION")
        logger.info("        with the file restrict_RESTRICTION.dat in the model dir.")
        logger.info("        By default, restrict_default.dat is used.")
        logger.info("        Specify model_name-full to get unrestricted model.")
        logger.info("      -modelname keeps the original particle names for the model")
        logger.info("")
        logger.info("   import model_v4 MODEL [-modelname] :")
        logger.info("      Import an MG4 model.")
        logger.info("      Model should be the name of the model")
        logger.info("      or the path to theMG4 model directory")
        logger.info("      -modelname keeps the original particle names for the model")
        logger.info("")
        logger.info("   import proc_v4 [PATH] :"  )
        logger.info("      Execute MG5 based on a proc_card.dat in MG4 format.")
        logger.info("      Path to the proc_card is optional if you are in a")
        logger.info("      madevent directory")
        logger.info("")
        logger.info("   import command PATH :")
        logger.info("      Execute the list of command in the file at PATH")
 
    def help_install(self):
        logger.info("syntax: install " + "|".join(self._install_opts))
        logger.info("-- Download the last version of the program and install it")
        logger.info("   localy in the current Madgraph version. In order to have")
        logger.info("   a sucessfull instalation, you will need to have up-to-date")
        logger.info("   F77 and/or C and Root compiler.")
        
    def help_display(self):
        logger.info("syntax: display " + "|".join(self._display_opts))
        logger.info("-- display a the status of various internal state variables")
        logger.info("   for particles/interactions you can specify the name or id of the")
        logger.info("   particles/interactions to receive more details information.")
        logger.info("   Example: display particles e+.")
        logger.info("   For \"checks\", can specify only to see failed checks.")
        logger.info("   For \"diagrams\", you can specify where the file will be written.")
        logger.info("   Example: display diagrams ./")
        
        
    def help_launch(self):
        """help for launch command"""
        _launch_parser.print_help()

    def help_tutorial(self):
        logger.info("syntax: tutorial [" + "|".join(self._tutorial_opts) + "]")
        logger.info("-- start/stop the tutorial mode")

    def help_open(self):
        logger.info("syntax: open FILE  ")
        logger.info("-- open a file with the appropriate editor.")
        logger.info('   If FILE belongs to index.html, param_card.dat, run_card.dat')
        logger.info('   the path to the last created/used directory is used')
        logger.info('   The program used to open those files can be chosen in the')
        logger.info('   configuration file ./input/mg5_configuration.txt')
        
    def help_output(self):
        logger.info("syntax: output [" + "|".join(self._export_formats) + \
                    "] [path|.|auto] [options]")
        logger.info("-- Output any generated process(es) to file.")
        logger.info("   mode: Default mode is madevent. Default path is \'.\' or auto.")
        logger.info("   - If mode is madevent, create a MadEvent process directory.")
        logger.info("   - If mode is standalone, create a Standalone directory")
        logger.info("   - If mode is matrix, output the matrix.f files for all")
        logger.info("     generated processes in directory \"path\".")
        logger.info("   - If mode is standalone_cpp, create a standalone C++")
        logger.info("     directory in \"path\".")
        logger.info("   - If mode is pythia8, output all files needed to generate")
        logger.info("     the processes using Pythia 8. Directory \"path\"")
        logger.info("     should be a Pythia 8 main directory (v. 8.150 or later).")
        logger.info("   path: The path of the process directory.")
        logger.info("     If you put '.' as path, your pwd will be used.")
        logger.info("     If you put 'auto', an automatic directory PROC_XX_n will be created.")
        logger.info("   options:")
        logger.info("      -f: force cleaning of the directory if it already exists")
        logger.info("      -d: specify other MG/ME directory")
        logger.info("      -noclean: no cleaning performed in \"path\".")
        logger.info("      -nojpeg: no jpeg diagrams will be generated.")
        logger.info("      -name: the postfix of the main file in pythia8 mode.")
        logger.info("   Examples:")
        logger.info("       output")
        logger.info("       output standalone MYRUN -f")
        logger.info("       output pythia8 ../pythia8/ -name qcdprocs")
        
    def help_check(self):

        logger.info("syntax: check " + "|".join(self._check_opts) + " [param_card] process_definition")
        logger.info("-- check a process or set of processes. Options:")
        logger.info("full: Perform all three checks described below:")
        logger.info("   permutation, gauge and lorentz_invariance.")
        logger.info("permutation: Check that the model and MG5 are working")
        logger.info("   properly by generating permutations of the process and")
        logger.info("   checking that the resulting matrix elements give the")
        logger.info("   same value.")
        logger.info("gauge: Check that processes with massless gauge bosons")
        logger.info("   are gauge invariant")
        logger.info("lorentz_invariance: Check that the amplitude is lorentz")
        logger.info("   invariant by comparing the amplitiude in different frames")        
        logger.info("If param_card is given, that param_card is used instead")
        logger.info("   of the default values for the model.")
        logger.info("For process syntax, please see help generate")

    def help_generate(self):

        logger.info("syntax: generate INITIAL STATE > REQ S-CHANNEL > FINAL STATE $ EXCL S-CHANNEL / FORBIDDEN PARTICLES COUP1=ORDER1 COUP2=ORDER2 @N")
        logger.info("-- generate diagrams for a given process")
        logger.info("   Syntax example: l+ vl > w+ > l+ vl a $ z / a h QED=3 QCD=0 @1")
        logger.info("   Alternative required s-channels can be separated by \"|\":")
        logger.info("   b b~ > W+ W- | H+ H- > ta+ vt ta- vt~")
        logger.info("   If no coupling orders are given, MG5 will try to determine")
        logger.info("   orders to ensure maximum number of QCD vertices.")
        logger.info("   Note that if there are more than one non-QCD coupling type,")
        logger.info("   coupling orders need to be specified by hand.")
        logger.info("Decay chain syntax:")
        logger.info("   core process, decay1, (decay2, (decay2', ...)), ...  etc")
        logger.info("   Example: p p > t~ t QED=0, (t~ > W- b~, W- > l- vl~), t > j j b @2")
        logger.info("   Note that identical particles will all be decayed.")
        logger.info("To generate a second process use the \"add process\" command")

    def help_add(self):

        logger.info("syntax: add process INITIAL STATE > REQ S-CHANNEL > FINAL STATE $ EXCL S-CHANNEL / FORBIDDEN PARTICLES COUP1=ORDER1 COUP2=ORDER2")
        logger.info("-- generate diagrams for a process and add to existing processes")
        logger.info("   Syntax example: l+ vl > w+ > l+ vl a $ z / a h QED=3 QCD=0 @1")
        logger.info("   Alternative required s-channels can be separated by \"|\":")
        logger.info("   b b~ > W+ W- | H+ H- > ta+ vt ta- vt~")
        logger.info("   If no coupling orders are given, MG5 will try to determine")
        logger.info("   orders to ensure maximum number of QCD vertices.")
        logger.info("Decay chain syntax:")
        logger.info("   core process, decay1, (decay2, (decay2', ...)), ...  etc")
        logger.info("   Example: p p > t~ t QED=0, (t~ > W- b~, W- > l- vl~), t > j j b @2")
        logger.info("   Note that identical particles will all be decayed.")

    def help_define(self):
        logger.info("syntax: define multipart_name [=] part_name_list")
        logger.info("-- define a multiparticle")
        logger.info("   Example: define p = g u u~ c c~ d d~ s s~ b b~")
        

    def help_set(self):
        logger.info("syntax: set %s argument" % "|".join(self._set_options))
        logger.info("-- set options for generation or output")
        logger.info("   group_subprocesses True/False: ")
        logger.info("     (default True) Smart grouping of subprocesses into ")
        logger.info("     directories, mirroring of initial states, and ")
        logger.info("     combination of integration channels.")
        logger.info("     Example: p p > j j j w+ gives 5 directories and 184 channels")
        logger.info("     (cf. 65 directories and 1048 channels for regular output)")
        logger.info("   ignore_six_quark_processes multi_part_label")
        logger.info("     (default none) ignore processes with at least 6 of any")
        logger.info("     of the quarks given in multi_part_label.")
        logger.info("     These processes give negligible contribution to the")
        logger.info("     cross section but have subprocesses/channels.")
        logger.info("   stdout_level DEBUG|INFO|WARNING|ERROR|CRITICAL")
        logger.info("     change the default level for printed information")
        logger.info("   fortran_compiler NAME")
        logger.info("      (default None) Force a specific fortran compiler.")
        logger.info("      If None, it tries first g77 and if not present gfortran.")
        


#===============================================================================
# CheckValidForCmd
#===============================================================================
class CheckValidForCmd(object):
    """ The Series of help routine for the MadGraphCmd"""
    
    class RWError(MadGraph5Error):
        """a class for read/write errors"""
    
    def check_add(self, args):
        """check the validity of line
        syntax: add process PROCESS 
        """
    
        if len(args) < 2:
            self.help_add()
            raise self.InvalidCmd('\"add\" requires two arguments')
        
        if args[0] != 'process':
            raise self.InvalidCmd('\"add\" requires the argument \"process\"')

        if not self._curr_model:
            logger.info("No model currently active, so we import the Standard Model")
            self.do_import('model sm')
    
        self.check_process_format(' '.join(args[1:]))

    def check_define(self, args):
        """check the validity of line
        syntax: define multipart_name [ part_name_list ]
        """  

        
        if len(args) < 2:
            self.help_define()
            raise self.InvalidCmd('\"define\" command requires at least two arguments')

        if args[1] == '=':
            del args[1]
            if len(args) < 2:
                self.help_define()
                raise self.InvalidCmd('\"define\" command requires at least one particles name after \"=\"')
        
        if '=' in args:
            self.help_define()
            raise self.InvalidCmd('\"define\" command requires symbols \"=\" at the second position')
        
        if not self._curr_model:
            logger.info('No model currently active. Try with the Standard Model')
            self.do_import('model sm')

        if self._curr_model['particles'].find_name(args[0]):
            raise self.InvalidCmd("label %s is a particle name in this model\n\
            Please retry with another name." % args[0])

    def check_display(self, args):
        """check the validity of line
        syntax: display XXXXX
        """
            
        if len(args) < 1 or args[0] not in self._display_opts:
            self.help_display()
            raise self.InvalidCmd

        if not self._curr_model:
            raise self.InvalidCmd("No model currently active, please import a model!")

        if args[0] in ['processes', 'diagrams'] and not self._curr_amps:
            raise self.InvalidCmd("No process generated, please generate a process!")
        if args[0] == 'checks' and not self._comparisons:
            raise self.InvalidCmd("No check results to display.")
        
        if args[0] == 'mg5_variable' and len(args) !=2:
            raise self.InvalidCmd('mg5_variable need a variable name')


    def check_draw(self, args):
        """check the validity of line
        syntax: draw DIRPATH [option=value]
        """
        
        if len(args) < 1:
            args.append('/tmp')
        
        if not self._curr_amps:
            raise self.InvalidCmd("No process generated, please generate a process!")
            
        if not os.path.isdir(args[0]):
            raise self.InvalidCmd( "%s is not a valid directory for export file" % args[0])
            
    def check_check(self, args):
        """check the validity of args"""
        
        if  not self._curr_model:
            raise self.InvalidCmd("No model currently active, please import a model!")

        if self._model_v4_path:
            raise self.InvalidCmd(\
                "\"check\" not possible for v4 models")

        if len(args) < 2:
            self.help_check()
            raise self.InvalidCmd("\"check\" requires an argument and a process.")

        param_card = None
        if os.path.isfile(args[1]):
            param_card = args.pop(1)

        if args[0] not in self._check_opts:
            args.insert(0, 'full')
        
        if any([',' in elem for elem in args]):
            raise self.InvalidCmd('Decay chains not allowed in check')
        
        self.check_process_format(" ".join(args[1:]))

        return param_card
    
    def check_generate(self, args):
        """check the validity of args"""
        # Not called anymore see check_add
        return self.check_add(args)
    
    def check_process_format(self, process):
        """ check the validity of the string given to describe a format """
        
        #check balance of paranthesis
        if process.count('(') != process.count(')'):
            raise self.InvalidCmd('Invalid Format, no balance between open and close parenthesis')
        #remove parenthesis for fututre introspection
        process = process.replace('(',' ').replace(')',' ')
        
        # split following , (for decay chains)
        subprocesses = process.split(',')
        if len(subprocesses) > 1:
            for subprocess in subprocesses:
                self.check_process_format(subprocess)
            return
        
        # request that we have one or two > in the process
        if process.count('>') not in [1,2]:
            raise self.InvalidCmd(
               'wrong format for \"%s\" this part requires one or two symbols \'>\', %s found' 
               % (process, process.count('>')))
        
        # we need at least one particles in each pieces
        particles_parts = process.split('>')
        for particles in particles_parts:
            if re.match(r'^\s*$', particles):
                raise self.InvalidCmd(
                '\"%s\" is a wrong process format. Please try again' % process)  
        
        # '/' and '$' sould be used only after the process definition
        for particles in particles_parts[:-1]:
            if re.search('\D/', particles):
                raise self.InvalidCmd(
                'wrong process format: restriction should be place after the final states')
            if re.search('\D\$', particles):
                raise self.InvalidCmd(
                'wrong process format: restriction should be place after the final states')
        
    
    def check_import(self, args):
        """check the validity of line"""
        
        modelname = False
        if '-modelname' in args:
            args.remove('-modelname')
            modelname = True    
                
        if not args:
            self.help_import()
            raise self.InvalidCmd('wrong \"import\" format')
        
        if len(args) >= 2 and args[0] not in self._import_formats:
            self.help_import()
            raise self.InvalidCmd('wrong \"import\" format')            
        elif len(args) == 1:
            if args[0] in self._import_formats:
                if args[0] != "proc_v4":
                    self.help_import()
                    raise self.InvalidCmd('wrong \"import\" format')
                elif not self._export_dir:
                    self.help_import()
                    raise self.InvalidCmd('PATH is mandatory in the current context\n' + \
                                  'Did you forget to run the \"output\" command')
            # The type of the import is not given -> guess it
            format = self.find_import_type(args[0])
            logger.info('The import format was not given, so we guess it as %s' % format)
            args.insert(0, format)
            if self.history[-1].startswith('import'):
                self.history[-1] = 'import %s %s' % \
                                (format, ' '.join(self.history[-1].split()[1:]))
                                    
        if modelname:
            args.append('-modelname') 
        
        
          
    def check_install(self, args):
        """check that the install command is valid"""
        
        if len(args) != 1:
            self.help_install()
            raise self.InvalidCmd('install command require at least one argument')
        
        if args[0] not in self._install_opts:
            if not args[0].startswith('td'):
                self.help_install()
                raise self.InvalidCmd('Not recognize program %s ' % args[0])
            
        if args[0] in ["ExRootAnalysis", "Delphes"]:
            if not misc.which('root'):
                raise self.InvalidCmd(
'''In order to install ExRootAnalysis, you need to install Root on your computer first.
please follow information on http://root.cern.ch/drupal/content/downloading-root''')
            if 'ROOTSYS' not in os.environ:
                raise self.InvalidCmd(
'''The environment variable ROOTSYS is not configured.
You can set it by adding the following lines in your .bashrc [.bash_profile for mac]:
export ROOTSYS=%s
export PATH=$PATH:$ROOTSYS/bin
This will take effect only in a NEW terminal
''' % os.path.realpath(os.path.join(misc.which('root'), \
                                               os.path.pardir, os.path.pardir)))

                
    def check_launch(self, args, options):
        """check the validity of the line"""
        # modify args in order to be MODE DIR
        # mode being either standalone or madevent
        if not( 0 <= int(options.cluster) <= 2):
            return self.InvalidCmd, 'cluster mode should be between 0 and 2'
        
        if not args:
            if self._done_export:
                mode = self.find_output_type(self._done_export[0])
                if mode != self._done_export[1]:
                    raise self.InvalidCmd, \
                          '%s not valid directory for launch' % self._done_export[0]
                args.append(self._done_export[1])
                args.append(self._done_export[0])
                return
            else:
                self.help_launch()
                raise self.InvalidCmd, \
                       'No default location available, please specify location.'
        
        if len(args) != 1:
            self.help_launch()
            return self.InvalidCmd, 'Invalid Syntax: Too many argument'
        
        # search for a valid path
        if os.path.sep in args[0] and os.path.isdir(args[0]):
            path = args[0]
        elif os.path.isdir(os.path.join(MG5DIR,args[0])):
            path = os.path.join(MG5DIR,args[0])
        elif  MG4DIR and os.path.isdir(os.path.join(MG4DIR,args[0])):
            path = os.path.join(MG4DIR,args[0])
        elif os.path.isdir(args[0]):
            path = args[0]
        else:    
            raise self.InvalidCmd, '%s is not a valid directory' % args[0]
            
        mode = self.find_output_type(path)
        args[0] = mode
        args.append(path)
        # inform where we are for future command
        self._done_export = [path, mode]
        

    def find_import_type(self, path):
        """ identify the import type of a given path 
        valid output: model/model_v4/proc_v4/command"""
        
        possibility = [os.path.join(MG5DIR,'models',path), \
                     os.path.join(MG5DIR,'models',path+'_v4'), path]
        if '-' in path:
            name = path.rsplit('-',1)[0]
            possibility = [os.path.join(MG5DIR,'models',name), name] + possibility
        # Check if they are a valid directory
        for name in possibility:
            if os.path.isdir(name):
                if os.path.exists(os.path.join(name,'particles.py')):
                    return 'model'
                elif os.path.exists(os.path.join(name,'particles.dat')):
                    return 'model_v4'
        
        # Not valid directory so maybe a file
        if os.path.isfile(path):
            text = open(path).read()
            if 'Begin PROCESS' in text:
                return 'proc_v4'
            else:
                return 'command'
        else:
            return 'proc_v4'
        
        

    
    def find_output_type(self, path):
        """ identify the type of output of a given directory:
        valid output: madevent/standalone/standalone_cpp"""
        
        card_path = os.path.join(path,'Cards')
        bin_path = os.path.join(path,'bin')
        src_path = os.path.join(path,'src')
        include_path = os.path.join(path,'include')
        subproc_path = os.path.join(path,'SubProcesses')

        if os.path.isfile(os.path.join(include_path, 'Pythia.h')):
            return 'pythia8'
        elif os.path.isdir(src_path):
            return 'standalone_cpp'
        elif os.path.isfile(os.path.join(bin_path,'generate_events')):
            return 'madevent'
        elif os.path.isdir(card_path):
            return 'standalone'

        raise self.InvalidCmd, '%s : Not a valid directory' % path
        
    def check_load(self, args):
        """ check the validity of the line"""
        
        if len(args) != 2 or args[0] not in self._save_opts:
            self.help_load()
            raise self.InvalidCmd('wrong \"load\" format')
            
        
    def check_save(self, args):
        """ check the validity of the line"""
        if len(args) != 2 or args[0] not in self._save_opts:
            self.help_save()
            raise self.InvalidCmd('wrong \"save\" format')
    
    def check_set(self, args):
        """ check the validity of the line"""
        
        if len(args) < 2:
            self.help_set()
            raise self.InvalidCmd('set needs an option and an argument')

        if args[0] not in self._set_options:
            self.help_set()
            raise self.InvalidCmd('Possible options for set are %s' % \
                                  self._set_options)

        if args[0] in ['group_subprocesses']:
            if args[1] not in ['False', 'True']:
                raise self.InvalidCmd('%s needs argument False or True' % \
                                      args[0])
        if args[0] in ['ignore_six_quark_processes']:
            if args[1] not in self._multiparticles.keys():
                raise self.InvalidCmd('ignore_six_quark_processes needs ' + \
                                      'a multiparticle name as argument')
        
        if args[0] in ['stdout_level']:
            if args[1] not in ['DEBUG','INFO','WARNING','ERROR','CRITICAL']:
                raise self.InvalidCmd('output_level needs ' + \
                                      'a valid level')       
    
    def check_open(self, args):
        """ check the validity of the line """
        
        if len(args) != 1:
            self.help_open()
            raise self.InvalidCmd('OPEN command requires exactly one argument')

        if args[0].startswith('./'):
            if not os.path.isfile(args[0]):
                raise self.InvalidCmd('%s: not such file' % args[0])
            return True

        # if special : create the path.
        if not self._done_export:
            if not os.path.isfile(args[0]):
                self.help_open()
                raise self.InvalidCmd('No command \"output\" or \"launch\" used. Impossible to associate this name to a file')
            else:
                return True
            
        path = self._done_export[0]
        if os.path.isfile(os.path.join(path,args[0])):
            args[0] = os.path.join(path,args[0])
        elif os.path.isfile(os.path.join(path,'Cards',args[0])):
            args[0] = os.path.join(path,'Cards',args[0])
        elif os.path.isfile(os.path.join(path,'HTML',args[0])):
            args[0] = os.path.join(path,'HTML',args[0])
        # special for card with _default define: copy the default and open it
        elif '_card.dat' in args[0]:   
            name = args[0].replace('_card.dat','_card_default.dat')
            if os.path.isfile(os.path.join(path,'Cards', name)):
                files.cp(path + '/Cards/' + name, path + '/Cards/'+ args[0])
                args[0] = os.path.join(path,'Cards', args[0])
            else:
                raise self.InvalidCmd('No default path for this file')
        elif not os.path.isfile(args[0]):
            raise self.InvalidCmd('No default path for this file')
                
                
    def check_output(self, args):
        """ check the validity of the line"""
          
        if args and args[0] in self._export_formats:
            self._export_format = args.pop(0)
        else:
            self._export_format = 'madevent'

        if not self._curr_amps:
            text = 'No processes generated. Please generate a process first.'
            raise self.InvalidCmd(text)

        if not self._curr_model:
            text = 'No model found. Please import a model first and then retry.'
            raise self.InvalidCmd(text)

        if self._model_v4_path and \
               (self._export_format not in self._v4_export_formats):
            text = " The Model imported (MG4 format) does not contain enough\n "
            text += " information for this type of output. In order to create\n"
            text += " output for " + args[0] + ", you have to use a UFO model.\n"
            text += " Those model can be imported with mg5> import model NAME."
            logger.warning(text)
            raise self.InvalidCmd('')

        if args and args[0][0] != '-':
            # This is a path
            path = args.pop(0)
            # Check for special directory treatment
            if path == 'auto' and self._export_format in \
                     ['madevent', 'standalone', 'standalone_cpp']:
                self.get_default_path()
            else:
                self._export_dir = path
        else:
            # No valid path
            self.get_default_path()

        self._export_dir = os.path.realpath(self._export_dir)

    def get_default_path(self):
        """Set self._export_dir to the default (\'auto\') path"""

        if self._export_format in ['madevent', 'standalone']:
            # Detect if this script is launched from a valid copy of the Template,
            # if so store this position as standard output directory
            if 'TemplateVersion.txt' in os.listdir('.'):
                #Check for ./
                self._export_dir = os.path.realpath('.')
                return
            elif 'TemplateVersion.txt' in os.listdir('..'):
                #Check for ../
                self._export_dir = os.path.realpath('..')
                return
            elif self.stdin != sys.stdin:
                #Check for position defined by the input files
                input_path = os.path.realpath(self.stdin.name).split(os.path.sep)
                print "Not standard stdin, use input path"
                if input_path[-2] == 'Cards':
                    self._export_dir = os.path.sep.join(input_path[:-2])
                    if 'TemplateVersion.txt' in self._export_dir:
                        return
        
        if self._export_format.startswith('madevent'):            
            name_dir = lambda i: 'PROC_%s_%s' % \
                                    (self._curr_model['name'], i)
            auto_path = lambda i: os.path.join(self.writing_dir,
                                               name_dir(i))
        elif self._export_format == 'standalone':
            name_dir = lambda i: 'PROC_SA_%s_%s' % \
                                    (self._curr_model['name'], i)
            auto_path = lambda i: os.path.join(self.writing_dir,
                                               name_dir(i))                
        elif self._export_format == 'standalone_cpp':
            name_dir = lambda i: 'PROC_SA_CPP_%s_%s' % \
                                    (self._curr_model['name'], i)
            auto_path = lambda i: os.path.join(self.writing_dir,
                                               name_dir(i))
        elif self._export_format == 'pythia8':
            if self.pythia8_path:
                self._export_dir = self.pythia8_path
            else:
                self._export_dir = '.'
            return
        else:
            self._export_dir = '.'
            return
        for i in range(500):
            if os.path.isdir(auto_path(i)):
                continue
            else:
                self._export_dir = auto_path(i) 
                break
        if not self._export_dir:
            raise self.InvalidCmd('Can\'t use auto path,' + \
                                  'more than 500 dirs already')    
            
        
#===============================================================================
# CheckValidForCmdWeb
#===============================================================================
class CheckValidForCmdWeb(CheckValidForCmd):
    """ Check the validity of input line for web entry
    (no explicit path authorized)"""
    
    class WebRestriction(MadGraph5Error):
        """class for WebRestriction"""
    
    def check_draw(self, args):
        """check the validity of line
        syntax: draw FILEPATH [option=value]
        """
        raise self.WebRestriction('direct call to draw is forbidden on the web')
    
    def check_display(self, args):
        """ check the validity of line in web mode """
        
        if args[0] == 'mg5_variable':
            raise self.WebRestriction('Display internal variable is forbidden on the web')
        
        CheckValidForCmd.check_history(self, args)
    
    def check_check(self, args):
        """ Not authorize for the Web"""
        
        raise self.WebRestriction('Check call is forbidden on the web')
    
    def check_history(self, args):
        """check the validity of line
        No Path authorize for the Web"""
        
        CheckValidForCmd.check_history(self, args)

        if len(args) == 2 and args[1] not in ['.', 'clean']:
            raise self.WebRestriction('Path can\'t be specify on the web.')

        
    def check_import(self, args):
        """check the validity of line
        No Path authorize for the Web"""
        
        if not args:
            raise self.WebRestriction, 'import requires at least one option'
        
        if args[0] not in self._import_format:
            self.help_import()
            raise self.WebRestriction, 'No implicit format on the web. Please modify your card.'

        if args[0] == 'proc_v4':
            args[:] = [args[0], './Cards/proc_card.dat']
        elif args[0] == 'command':
            args[:] = [args[0], './Cards/proc_card_mg5.dat']

        CheckValidForCmd.check_import(self, args)
        
    def check_install(self, args):
        """ No possibility to install new software on the web """
        raise self.WebRestriction('Impossible to install program on the cluster')
        
    def check_load(self, args):
        """ check the validity of the line
        No Path authorize for the Web"""

        CheckValidForCmd.check_load(self, args)        

        if len(args) == 2:
            if args[0] != 'model':
                raise self.WebRestriction('only model can be loaded online')
            if 'model.pkl' not in args[1]:
                raise self.WebRestriction('not valid pkl file: wrong name')
            if not os.path.realpath(args[1]).startswith(os.path.join(MG4DIR, \
                                                                    'Models')):
                raise self.WebRestriction('Wrong path to load model')
        
    def check_save(self, args):
        """ not authorize on web"""
        raise self.WebRestriction('\"save\" command not authorize online')
    
    def check_open(self, args):
        """ not authorize on web"""
        raise self.WebRestriction('\"open\" command not authorize online')
    
    def check_output(self, args):
        """ check the validity of the line"""

        
        # first pass to the default
        CheckValidForCmd.check_output(self, args)
        
        args[:] = [self._export_format, '.', '-f']

        # Check that we output madevent
        if 'madevent' != self._export_format:
                raise self.WebRestriction, 'only available output format is madevent (at current stage)'

        # In web mode, can only do forced, automatic madevent output
        CheckValidForCmd.check_output(self, args)

#===============================================================================
# CompleteForCmd
#===============================================================================
class CompleteForCmd(CheckValidForCmd):
    """ The Series of help routine for the MadGraphCmd"""
    
 
    def model_completion(self, text, process):
        """ complete the line with model information """

        while ',' in process:
            process = process[process.index(',')+1:]
        args = self.split_arg(process)
        couplings = []

        # Force '>' if two initial particles.
        if len(args) == 2 and args[-1] != '>':
                return self.list_completion(text, '>')
            
        # Add non-particle names
        if len(args) > 0 and args[-1] != '>':
            couplings = ['>']
        if '>' in args and args.index('>') < len(args) - 1:
            couplings = [c + "=" for c in self._couplings] + \
                        ['@','$','/','>',',']
        return self.list_completion(text, self._particle_names + \
                                    self._multiparticles.keys() + couplings)
        
                    
    def complete_generate(self, text, line, begidx, endidx):
        "Complete the add command"

        # Return list of particle names and multiparticle names, as well as
        # coupling orders and allowed symbols
        args = self.split_arg(line[0:begidx])
        if len(args) > 2 and args[-1] == '@' or args[-1].endswith('='):
            return

        try:
            return self.model_completion(text, ' '.join(args[1:]))
        except Exception as error:
            print error
            
        #if len(args) > 1 and args[-1] != '>':
        #    couplings = ['>']
        #if '>' in args and args.index('>') < len(args) - 1:
        #    couplings = [c + "=" for c in self._couplings] + ['@','$','/','>']
        #return self.list_completion(text, self._particle_names + \
        #                            self._multiparticles.keys() + couplings)
        
    def complete_add(self, text, line, begidx, endidx):
        "Complete the add command"

        args = self.split_arg(line[0:begidx])

        # Format
        if len(args) == 1:
            return self.list_completion(text, self._add_opts)

        return self.complete_generate(text, " ".join(args[1:]), begidx, endidx)

        # Return list of particle names and multiparticle names, as well as
        # coupling orders and allowed symbols
        couplings = []
        if len(args) > 2 and args[-1] != '>':
            couplings = ['>']
        if '>' in args and args.index('>') < len(args) - 1:
            couplings = [c + "=" for c in self._couplings] + ['@','$','/','>']
        return self.list_completion(text, self._particle_names + \
                                    self._multiparticles.keys() + couplings)
          
    def complete_check(self, text, line, begidx, endidx):
        "Complete the add command"

        args = self.split_arg(line[0:begidx])

        # Format
        if len(args) == 1:
            return self.list_completion(text, self._check_opts)

        


        # Directory continuation
        if args[-1].endswith(os.path.sep):
            return self.path_completion(text,
                                        os.path.join('.',*[a for a in args \
                                                    if a.endswith(os.path.sep)]))
        # autocompletion for particles/couplings
        model_comp = self.model_completion(text, ' '.join(args[2:]))

        if len(args) == 2:
            return model_comp + self.path_completion(text)

        if len(args) > 2:
            return model_comp
            
        
    def complete_tutorial(self, text, line, begidx, endidx):
        "Complete the tutorial command"

        # Format
        if len(self.split_arg(line[0:begidx])) == 1:
            return self.list_completion(text, self._tutorial_opts)
        
    def complete_define(self, text, line, begidx, endidx):
        """Complete particle information"""
        return self.model_completion(text, line[6:])

    def complete_display(self, text, line, begidx, endidx):
        "Complete the display command"

        args = self.split_arg(line[0:begidx])
        # Format
        if len(args) == 1:
            return self.list_completion(text, self._display_opts)

        if len(args) == 2 and args[1] == 'checks':
            return self.list_completion(text, 'failed')

        if len(args) == 2 and args[1] == 'particles':
            return self.model_completion(text, line[begidx:])

    def complete_draw(self, text, line, begidx, endidx):
        "Complete the draw command"

        args = self.split_arg(line[0:begidx])

        # Directory continuation
        if args[-1].endswith(os.path.sep):
            return self.path_completion(text,
                                        os.path.join('.',*[a for a in args if a.endswith(os.path.sep)]),
                                        only_dirs = True)
        # Format
        if len(args) == 1:
            return self.path_completion(text, '.', only_dirs = True)


        #option
        if len(args) >= 2:
            opt = ['horizontal', 'external=', 'max_size=', 'add_gap=',
                                'non_propagating', '--']
            return self.list_completion(text, opt)

    def complete_launch(self, text, line, begidx, endidx):
        """ complete the launch command"""

        args = self.split_arg(line[0:begidx])

        # Directory continuation
        if args[-1].endswith(os.path.sep):
            return self.path_completion(text,
                                        os.path.join('.',*[a for a in args if a.endswith(os.path.sep)]),
                                        only_dirs = True)
        # Format
        if len(args) == 1:
            complete = self.path_completion(text, '.', only_dirs = True)
            if MG5DIR != os.path.realpath('.'):
                complete += self.path_completion(text, MG5DIR, only_dirs = True, 
                                                                 relative=False)
            if MG4DIR and MG4DIR != os.path.realpath('.') and MG4DIR != MG5DIR:
                complete += self.path_completion(text, MG4DIR, only_dirs = True,
                                                                 relative=False)
            
        #option
        if len(args) >= 2:
            complete = []

        if line[0:begidx].endswith('--laststep='):
            opt = ['parton', 'pythia', 'pgs','delphes','auto']
        else:
            opt = ['--cluster', '--multicore', '-i', '--name=', '-f','-m', '-n', 
               '--interactive', '--laststep=parton', '--laststep=pythia',
               '--laststep=pgs', '--laststep=delphes','--laststep=auto']
        
        complete += self.list_completion(text, opt, line)
        return complete

    def complete_load(self, text, line, begidx, endidx):
        "Complete the load command"

        args = self.split_arg(line[0:begidx])        

        # Format
        if len(args) == 1:
            return self.list_completion(text, self._save_opts)

        # Directory continuation
        if args[-1].endswith(os.path.sep):
            return self.path_completion(text,
                                        os.path.join('.',*[a for a in args if \
                                                      a.endswith(os.path.sep)]))

        # Filename if directory is not given
        if len(args) == 2:
            return self.path_completion(text)

    def complete_save(self, text, line, begidx, endidx):
        "Complete the save command"

        args = self.split_arg(line[0:begidx])

        # Format
        if len(args) == 1:
            return self.list_completion(text, self._save_opts)

        # Directory continuation
        if args[-1].endswith(os.path.sep):
            return self.path_completion(text,
                                        os.path.join('.',*[a for a in args if a.endswith(os.path.sep)]),
                                        only_dirs = True)

        # Filename if directory is not given
        if len(args) == 2:
            return self.path_completion(text)
        
    def complete_open(self, text, line, begidx, endidx): 
        """ complete the open command """

        args = self.split_arg(line[0:begidx])
        
        # Directory continuation
        if os.path.sep in args[-1] + text:
            return self.path_completion(text,
                                    os.path.join('.',*[a for a in args if \
                                                      a.endswith(os.path.sep)]))

        possibility = []
        if self._done_export:
            path = self._done_export[0]
            possibility = ['index.html']
            if os.path.isfile(os.path.join(path,'README')):
                possibility.append('README')
            if os.path.isdir(os.path.join(path,'Cards')):
                possibility += [f for f in os.listdir(os.path.join(path,'Cards')) 
                                    if f.endswith('.dat')]
            if os.path.isdir(os.path.join(path,'HTML')):
                possibility += [f for f in os.listdir(os.path.join(path,'HTML')) 
                                  if f.endswith('.html') and 'default' not in f]
        else:
            possibility.extend(['./','../'])
        if os.path.exists('MG5_debug'):
            possibility.append('MG5_debug')
        if os.path.exists('ME5_debug'):
            possibility.append('ME5_debug')            

        return self.list_completion(text, possibility)
       
    def complete_output(self, text, line, begidx, endidx,
                        possible_options = ['f', 'noclean', 'nojpeg'],
                        possible_options_full = ['-f', '-noclean', '-nojpeg']):
        "Complete the output command"

        possible_format = self._export_formats
        #don't propose directory use by MG_ME
        forbidden_names = ['MadGraphII', 'Template', 'pythia-pgs', 'CVS',
                            'Calculators', 'MadAnalysis', 'SimpleAnalysis',
                            'mg5', 'DECAY', 'EventConverter', 'Models',
                            'ExRootAnalysis', 'HELAS', 'Transfer_Fct']
        #name of the run =>proposes old run name
        args = self.split_arg(line[0:begidx])
        if len(args) >= 1: 
            # Directory continuation
            if args[-1].endswith(os.path.sep):
                return [name for name in self.path_completion(text,
                        os.path.join('.',*[a for a in args if a.endswith(os.path.sep)]),
                        only_dirs = True) if name not in forbidden_names]
            # options
            if args[-1][0] == '-' or len(args) > 1 and args[-2] == '-':
                return self.list_completion(text, possible_options)
            if len(args) > 2:
                return self.list_completion(text, possible_options_full)
            # Formats
            if len(args) == 1:
                if any([p.startswith(text) for p in possible_format]):
                    return [name for name in \
                            self.list_completion(text, possible_format) + \
                            ['.' + os.path.sep, '..' + os.path.sep, 'auto'] \
                            if name.startswith(text)]

            # directory names
            content = [name for name in self.path_completion(text, '.', only_dirs = True) \
                       if name not in forbidden_names]
            content += ['auto']
            return self.list_completion(text, content)


    def complete_set(self, text, line, begidx, endidx):
        "Complete the set command"

        args = self.split_arg(line[0:begidx])

        # Format
        if len(args) == 1:
            return self.list_completion(text, self._set_options)

        if len(args) == 2:
            if args[1] in ['group_subprocesses']:
                return self.list_completion(text, ['False', 'True'])
            
            elif args[1] in ['ignore_six_quark_processes']:
                return self.list_completion(text, self._multiparticles.keys())
            
            elif args[1] == 'stdout_level':
                return self.list_completion(text, ['DEBUG','INFO','WARNING','ERROR','CRITICAL'])
        
            elif args[1] == 'fortran_compiler':
                return self.list_completion(text, ['f77','g77','gfortran'])
        
    def complete_import(self, text, line, begidx, endidx):
        "Complete the import command"

        args=self.split_arg(line[0:begidx])
        
        # Format
        if len(args) == 1:
            opt =  self.list_completion(text, self._import_formats)
            if opt:
                return opt
            mode = 'all'
        elif args[1] in self._import_formats:
            mode = args[1]
        else:
            mode = 'all'

        # restriction continuation (for UFO)
        if mode in ['model', 'all'] and ('-' in args[-1] + text):
            # deal with - in readline splitting (different on some computer)
            if not GNU_SPLITTING:
                prefix = '-'.join([part for part in text.split('-')[:-1]])+'-'
                args.append(prefix)
                text = text.split('-')[-1]
            #model name
            path = args[-1][:-1] # remove the final - for the model name
            # find the different possibilities
            all_name = self.find_restrict_card(path, no_restrict=False)
            all_name += self.find_restrict_card(path, no_restrict=False,
                                        base_dir=os.path.join(MG5DIR,'models'))

            # select the possibility according to the current line            
            all_name = [name.split('-')[-1] for name in  all_name ]
            all_name = [name+' ' for name in  all_name if name.startswith(text)
                                                       and name.strip() != text]
            # adapt output for python2.7 (due to different splitting)
            if not GNU_SPLITTING:
                all_name = [prefix + name for name in  all_name ]
                
            if all_name:
                return all_name

        # Path continuation
        if os.path.sep in args[-1] + text and text:
            if mode.startswith('model'):
                # Directory continuation
                cur_path = os.path.join('.',*[a for a in args \
                                                   if a.endswith(os.path.sep)])
                all_dir = self.path_completion(text, cur_path, only_dirs = True)
                if mode == 'model_v4':
                    return all_dir
                new = []
                data =   [new.__iadd__(self.find_restrict_card(name, base_dir=cur_path))
                                                            for name in all_dir]
                if data:
                    return data[0]
                else:
                    return []
            else:
                cur_path = os.path.join('.',*[a for a in args \
                                                   if a.endswith(os.path.sep)])
                all_path =  self.path_completion(text, cur_path)
                if mode == 'all':
                    new = [] 
                    data =   [new.__iadd__(self.find_restrict_card(name, base_dir=cur_path)) 
                                                           for name in all_path]
                    if data:
                        return data[0]
                    else:
                        return []
                else:
                    return all_path


        # Model directory name if directory is not given
        if (mode != 'all' and len(self.split_arg(line[0:begidx])) == 2) or \
            (mode =='all' and len(self.split_arg(line[0:begidx]))==1):
            if mode == 'model':
                file_cond = lambda p : os.path.exists(os.path.join(MG5DIR,'models',p,'particles.py'))
                mod_name = lambda name: name
            elif mode == 'model_v4':
                file_cond = lambda p :  (os.path.exists(os.path.join(MG5DIR,'models',p,'particles.dat')) 
                                      or os.path.exists(os.path.join(self._mgme_dir,'Models',p,'particles.dat')))
                mod_name = lambda name :(name[-3:] != '_v4' and name or name[:-3]) 
            elif mode == 'all':
                mod_name = lambda name: name
                file_cond = lambda p : os.path.exists(os.path.join(MG5DIR,'models',p,'particles.py')) \
                                      or os.path.exists(os.path.join(MG5DIR,'models',p,'particles.dat')) \
                                      or os.path.exists(os.path.join(self._mgme_dir,'Models',p,'particles.dat')) 
            else:
                cur_path = os.path.join('.',*[a for a in args \
                                                   if a.endswith(os.path.sep)])
                all_path =  self.path_completion(text, cur_path)
                return all_path
                
            model_list = [mod_name(name) for name in \
                                            self.path_completion(text,
                                            os.path.join(MG5DIR,'models'),
                                            only_dirs = True) \
                                            if file_cond(name)]
            
            if mode == 'model_v4':
                return model_list
            else:
                # need to update the  list with the possible restriction
                all_name = []
                for model_name in model_list:
                    all_name += self.find_restrict_card(model_name, 
                                        base_dir=os.path.join(MG5DIR,'models'))
            if mode == 'all':
                cur_path = os.path.join('.',*[a for a in args \
                                                    if a.endswith(os.path.sep)])
                all_path =  self.path_completion(text, cur_path)
                return all_path + all_name 
            else:
                return all_name                

        # Options
        if mode == 'all' and len(args)>1:
            mode = self.find_import_type(args[1])
            opt_len = 1
        else:
            opt_len =2        
        
        
        if len(args) > opt_len and mode.startswith('model') and args[-1][0] != '-':
                return ['-modelname']
            
        if len(args) > (opt_len+1) and mode[1].startswith('model') and args[-1][0] == '-':
           if GNU_SPLITTING:
               return ['modelname']
           else: 
               return ['-modelname']
        
        
            
    def find_restrict_card(self, model_name, base_dir='./', no_restrict=True):
        """find the restriction file associate to a given model"""

        # check if the model_name should be keeped as a possibility
        if no_restrict:
            output = [model_name]
        else:
            output = []
        
        # check that the model is a valid model
        if not os.path.exists(os.path.join(base_dir, model_name, 'couplings.py')):
            # not valid UFO model
            return output
        
        if model_name.endswith(os.path.sep):
            model_name = model_name[:-1]
        
        # look for _default and treat this case
        if os.path.exists(os.path.join(base_dir, model_name, 'restrict_default.dat')):
            output.append('%s-full' % model_name)
        
        # look for other restrict_file
        for name in os.listdir(os.path.join(base_dir, model_name)):
            if name.startswith('restrict_') and not name.endswith('default.dat') \
                and name.endswith('.dat'):
                tag = name[9:-4] #remove restrict and .dat
                while model_name.endswith(os.path.sep):
                    model_name = model_name[:-1]
                output.append('%s-%s' % (model_name, tag))

        # return
        return output
    
    def complete_install(self, text, line, begidx, endidx):
        "Complete the import command"

        args = self.split_arg(line[0:begidx])
        
        # Format
        if len(args) == 1:
            return self.list_completion(text, self._install_opts)     

#===============================================================================
# MadGraphCmd
#===============================================================================
class MadGraphCmd(CmdExtended, HelpToCmd):
    """The command line processor of MadGraph"""    

    # Options and formats available
    _display_opts = ['particles', 'interactions', 'processes', 'diagrams', 
                     'diagrams_text', 'multiparticles', 'couplings', 'lorentz', 
                     'checks', 'parameters', 'options', 'coupling_order','variable']
    _add_opts = ['process']
    _save_opts = ['model', 'processes']
    _tutorial_opts = ['start', 'stop']
    _check_opts = ['full', 'permutation', 'gauge', 'lorentz_invariance']
    _import_formats = ['model_v4', 'model', 'proc_v4', 'command']
    _install_opts = ['pythia-pgs', 'Delphes', 'MadAnalysis', 'ExRootAnalysis']
    _v4_export_formats = ['madevent', 'standalone', 'matrix'] 
    _export_formats = _v4_export_formats + ['standalone_cpp', 'pythia8']
    _set_options = ['group_subprocesses',
                    'ignore_six_quark_processes',
                    'stdout_level',
                    'fortran_compiler']
    # Variables to store object information
    _curr_model = None  #base_objects.Model()
    _curr_amps = diagram_generation.AmplitudeList()
    _curr_matrix_elements = helas_objects.HelasMultiProcess()
    _curr_fortran_model = None
    _curr_cpp_model = None
    _curr_exporter = None
    _done_export = False

    # Configuration variable
    pythia8_path = None
    
    def __init__(self, mgme_dir = '', *completekey, **stdin):
        """ add a tracker of the history """

        CmdExtended.__init__(self, *completekey, **stdin)
        
        # Set MG/ME directory path
        if mgme_dir:
            if os.path.isdir(os.path.join(mgme_dir, 'Template')):
                self._mgme_dir = mgme_dir
                logger.info('Setting MG/ME directory to %s' % mgme_dir)
            else:
                logger.warning('Warning: Directory %s not valid MG/ME directory' % \
                             mgme_dir)
                self._mgme_dir = MG4DIR

        # Variables to store state information
        self._multiparticles = {}
        self._options = {}
        self._generate_info = "" # store the first generated process
        self._model_format = None
        self._model_v4_path = None
        self._use_lower_part_names = False
        self._export_dir = None
        self._export_format = 'madevent'
        self._mgme_dir = MG4DIR
        self._comparisons = None
    
        # Set defaults for options
        self._options['group_subprocesses'] = True
        self._options['ignore_six_quark_processes'] = False
        
        # Load the configuration file
        self.set_configuration()

    def do_quit(self, line):
        """Do quit"""
        
        if os.path.exists(os.path.join(self._done_export[0],'RunWeb')):
            os.remove(os.path.join(self._done_export[0],'RunWeb'))
        
        return super(MadGraphCmd, self).do_quit(line)
        
    # Add a process to the existing multiprocess definition
    # Generate a new amplitude
    def do_add(self, line):
        """Generate an amplitude for a given process and add to
        existing amplitudes
        """

        args = self.split_arg(line)
        
        # Check the validity of the arguments
        self.check_add(args)

        if args[0] == 'process':            
            # Rejoin line
            line = ' '.join(args[1:])
            
            # store the first process (for the perl script)
            if not self._generate_info:
                self._generate_info = line
                
            # Reset Helas matrix elements
            self._curr_matrix_elements = helas_objects.HelasMultiProcess()

            # Extract process from process definition
            if ',' in line:
                myprocdef, line = self.extract_decay_chain_process(line)
            else:
                myprocdef = self.extract_process(line)

            # Check that we have something    
            if not myprocdef:
                raise self.InvalidCmd("Empty or wrong format process, please try again.")
                
            cpu_time1 = time.time()

            # Generate processes
            collect_mirror_procs = self._options['group_subprocesses']
            ignore_six_quark_processes = \
                           self._options['ignore_six_quark_processes'] if \
                           "ignore_six_quark_processes" in self._options \
                           else []

            myproc = diagram_generation.MultiProcess(myprocdef,
                                          collect_mirror_procs =\
                                          collect_mirror_procs,
                                          ignore_six_quark_processes = \
                                          ignore_six_quark_processes)

            for amp in myproc.get('amplitudes'):
                if amp not in self._curr_amps:
                    self._curr_amps.append(amp)
                else:
                    warning = "Warning: Already in processes:\n%s" % \
                                                amp.nice_string_processes()
                    logger.warning(warning)


            # Reset _done_export, since we have new process
            self._done_export = False

            cpu_time2 = time.time()

            nprocs = len(myproc.get('amplitudes'))
            ndiags = sum([amp.get_number_of_diagrams() for \
                              amp in myproc.get('amplitudes')])
            logger.info("%i processes with %i diagrams generated in %0.3f s" % \
                  (nprocs, ndiags, (cpu_time2 - cpu_time1)))
            ndiags = sum([amp.get_number_of_diagrams() for \
                              amp in self._curr_amps])
            logger.info("Total: %i processes with %i diagrams" % \
                  (len(self._curr_amps), ndiags))                
  
    # Define a multiparticle label
    def do_define(self, line, log=True):
        """Define a multiparticle"""

        if self._use_lower_part_names:
            # Particle names lowercase
            line = line.lower()
        # Make sure there are spaces around = and |
        line = line.replace("=", " = ")
        line = line.replace("|", " | ")
        args = self.split_arg(line)
        # check the validity of the arguments
        self.check_define(args)

        label = args[0]
        
        pdg_list = self.extract_particle_ids(args[1:])
        self.optimize_order(pdg_list)
        self._multiparticles[label] = pdg_list
        if log:
            logger.info("Defined multiparticle %s" % \
                                             self.multiparticle_string(label))
    
    # Display
    def do_display(self, line):
        """Display current internal status"""

        args = self.split_arg(line)
        #check the validity of the arguments
        self.check_display(args)

        if args[0] == 'diagrams':
            self.draw(' '.join(args[1:]))

        if args[0] == 'particles' and len(args) == 1:
            propagating_particle = []
            nb_unpropagating = 0
            for particle in self._curr_model['particles']:
                if particle.get('propagating'):
                    propagating_particle.append(particle)
                else:
                    nb_unpropagating += 1
                    
            print "Current model contains %i particles:" % \
                    len(propagating_particle)
            part_antipart = [part for part in propagating_particle \
                             if not part['self_antipart']]
            part_self = [part for part in propagating_particle \
                             if part['self_antipart']]
            for part in part_antipart:
                print part['name'] + '/' + part['antiname'],
            print ''
            for part in part_self:
                print part['name'],
            print ''
            if nb_unpropagating:
                print 'In addition of %s un-physical particle mediating new interactions.' \
                                     % nb_unpropagating

        elif args[0] == 'particles':
            for arg in args[1:]:
                if arg.isdigit() or (arg[0] == '-' and arg[1:].isdigit()):
                    particle = self._curr_model.get_particle(abs(int(arg)))
                else:
                    particle = self._curr_model['particles'].find_name(arg)
                if not particle:
                    raise self.InvalidCmd, 'no particle %s in current model' % arg

                print "Particle %s has the following properties:" % particle.get_name()
                print str(particle)
            
        elif args[0] == 'interactions' and len(args) == 1:
            text = "Current model contains %i interactions\n" % \
                    len(self._curr_model['interactions'])
            for i, inter in enumerate(self._curr_model['interactions']):
                text += str(i+1) + ':'
                for part in inter['particles']:
                    if part['is_part']:
                        text += part['name']
                    else:
                        text += part['antiname']
                    text += " "
                text += " ".join(order + '=' + str(inter['orders'][order]) \
                                 for order in inter['orders'])
                text += '\n'
            pydoc.pager(text)

        elif args[0] == 'interactions':
            for arg in args[1:]:
                if int(arg) > len(self._curr_model['interactions']):
                    raise self.InvalidCmd, 'no interaction %s in current model' % arg
                if int(arg) == 0:
                    print 'Special interactions which identify two particles'
                else:
                    print "Interactions %s has the following property:" % arg
                    print self._curr_model['interactions'][int(arg)-1]

        elif args[0] == 'parameters' and len(args) == 1:
            text = "Current model contains %i parameters\n" % \
                    sum([len(part) for part in 
                                       self._curr_model['parameters'].values()])
            
            for key, item in self._curr_model['parameters'].items():
                text += '\nparameter type: %s\n' % str(key)
                for value in item:
                    if hasattr(value, 'expr'):
                        if value.value is not None:
                            text+= '        %s = %s = %s\n' % (value.name, value.expr ,value.value)
                        else:
                            text+= '        %s = %s\n' % (value.name, value.expr)
                    else:
                        if value.value is not None:
                            text+= '        %s = %s\n' % (value.name, value.value)
                        else:
                            text+= '        %s \n' % (value.name)
            pydoc.pager(text)
            
        elif args[0] == 'processes':
            for amp in self._curr_amps:
                print amp.nice_string_processes()

        elif args[0] == 'diagrams_text':
            text = "\n".join([amp.nice_string() for amp in self._curr_amps])
            pydoc.pager(text)

        elif args[0] == 'multiparticles':
            print 'Multiparticle labels:'
            for key in self._multiparticles:
                print self.multiparticle_string(key)
                
        elif args[0] == 'coupling_order':
            hierarchy = self._curr_model.get_order_hierarchy().items()
            def order(first, second):
                if first[1] < second[1]:
                    return -1
                else:
                    return 1
            hierarchy.sort(order)
            for order in hierarchy:
                print ' %s : weight = %s' % order 
            
        elif args[0] == 'couplings' and len(args) == 1:
            if self._model_v4_path:
                print 'No couplings information available in V4 model'
                return
            text = ''
            try:
                ufomodel = ufomodels.load_model(self._curr_model.get('name'))
            except:
                raise self.InvalidCmd, 'no couplings %s in current model' % args[1]
            for coup in ufomodel.all_couplings:
                order = ', '.join(['%s=%s' %val for val in coup.order.items()])
                text += '%s = %s\t( %s)\n' % (coup.name, coup.value, order)
            pydoc.pager(text)
            
        elif args[0] == 'couplings':
            if self._model_v4_path:
                print 'No couplings information available in V4 model'
                return
            try:
                ufomodel = ufomodels.load_model(self._curr_model.get('name'))
                print eval('ufomodel.couplings.%s.nice_string()'%args[1])
            except:
                raise self.InvalidCmd, 'no couplings %s in current model' % args[1]
        
        elif args[0] == 'lorentz':
            if self._model_v4_path:
                print 'No lorentz information available in V4 model'
                return
            elif len(args) == 1: 
                raise self.InvalidCmd,\
                     'display lorentz require an argument: the name of the lorentz structure.'
                return
            try:
                ufomodel = ufomodels.load_model(self._curr_model.get('name'))
                print eval('ufomodel.lorentz.%s.nice_string()'%args[1])
            except:
                raise self.InvalidCmd, 'no lorentz %s in current model' % args[1]
            
        elif args[0] == 'checks':
            comparisons = self._comparisons[0]
            if len(args) > 1 and args[1] == 'failed':
                comparisons = [c for c in comparisons if not c['passed']]
            outstr = "Process check results:"
            for comp in comparisons:
                outstr += "\n%s:" % comp['process'].nice_string()
                outstr += "\n   Phase space point: (px py pz E)"
                for i, p in enumerate(comp['momenta']):
                    outstr += "\n%2s    %+.9e  %+.9e  %+.9e  %+.9e" % tuple([i] + p)
                outstr += "\n   Permutation values:"
                outstr += "\n   " + str(comp['values'])
                if comp['passed']:
                    outstr += "\n   Process passed (rel. difference %.9e)" % \
                          comp['difference']
                else:
                    outstr += "\n   Process failed (rel. difference %.9e)" % \
                          comp['difference']

            used_aloha = sorted(self._comparisons[1])
            outstr += "\nChecked ALOHA routines:"
            for aloha in used_aloha:
                aloha_str = aloha[0]
                if aloha[1]:
                    aloha_str += 'C' + 'C'.join([str(ia) for ia in aloha[1]])
                aloha_str += "_%d" % aloha[2]
                outstr += "\n" + aloha_str

            pydoc.pager(outstr)            
        
        elif args[0] in  ["options", "variable"]:
            super(MadGraphCmd, self).do_display(line)
                
            
    def multiparticle_string(self, key):
        """Returns a nicely formatted string for the multiparticle"""

        if self._multiparticles[key] and \
               isinstance(self._multiparticles[key][0], list):
            return "%s = %s" % (key, "|".join([" ".join([self._curr_model.\
                                     get('particle_dict')[part_id].get_name() \
                                                     for part_id in id_list]) \
                                  for id_list in self._multiparticles[key]]))
        else:
            return "%s = %s" % (key, " ".join([self._curr_model.\
                                    get('particle_dict')[part_id].get_name() \
                                    for part_id in self._multiparticles[key]]))
            
  

    def do_tutorial(self, line):
        """Activate/deactivate the tutorial mode."""

        args = self.split_arg(line)
        if len(args) > 0 and args[0] == "stop":
            logger_tuto.info("\n\tThanks for using the tutorial!")
            logger_tuto.setLevel(logging.ERROR)
        else:
            logger_tuto.setLevel(logging.INFO)

        if not self._mgme_dir:
            logger_tuto.info(\
                       "\n\tWarning: To use all features in this tutorial, " + \
                       "please run from a" + \
                       "\n\t         valid MG_ME directory.")

    def draw(self, line):
        """ draw the Feynman diagram for the given process """

        args = self.split_arg(line)
        # Check the validity of the arguments
        self.check_draw(args)
        
        # Check if we plot a decay chain 
        if any([isinstance(a, diagram_generation.DecayChainAmplitude) for \
               a in self._curr_amps]) and not self._done_export:
            warn = 'WARNING: You try to draw decay chain diagrams without first running output.\n'
            warn += '\t  The decay processes will be drawn separately'
            logger.warning(warn)

        (options, args) = _draw_parser.parse_args(args)
        options = draw_lib.DrawOption(options)
        start = time.time()
        
        # Collect amplitudes
        amplitudes = diagram_generation.AmplitudeList()

        for amp in self._curr_amps:
            amplitudes.extend(amp.get_amplitudes())            

        for amp in amplitudes:
            filename = os.path.join(args[0], 'diagrams_' + \
                                    amp.get('process').shell_string() + ".eps")
            plot = draw.MultiEpsDiagramDrawer(amp['diagrams'],
                                          filename,
                                          model=self._curr_model,
                                          amplitude='',
                                          legend=amp.get('process').input_string())

            logger.info("Drawing " + \
                         amp.get('process').nice_string())
            plot.draw(opt=options)
            logger.info("Wrote file " + filename)
            self.exec_cmd('open %s' % filename)

        stop = time.time()
        logger.info('time to draw %s' % (stop - start)) 
    
    # Generate a new amplitude
    def do_check(self, line):
        """Check a given process or set of processes"""

        args = self.split_arg(line)

        # Check args validity
        param_card = self.check_check(args)

        line = " ".join(args[1:])
        myprocdef = self.extract_process(line)

        # Check that we have something    
        if not myprocdef:
            raise self.InvalidCmd("Empty or wrong format process, please try again.")

        # Disable diagram generation logger
        diag_logger = logging.getLogger('madgraph.diagram_generation')
        old_level = diag_logger.getEffectiveLevel()
        diag_logger.setLevel(logging.WARNING)

        # run the check
        cpu_time1 = time.time()
        # Run matrix element generation check on processes

        comparisons = []
        gauge_result = []
        lorentz_result =[]
        nb_processes = 0
        
        if args[0] in  ['permutation', 'full']:
            comparisons = process_checks.check_processes(myprocdef,
                                                        param_card = param_card,
                                                        quick = True)
            nb_processes += len(comparisons[0])
            
        if args[0] in  ['gauge', 'full']:
            gauge_result = process_checks.check_gauge(myprocdef,
                                                      param_card = param_card)
            nb_processes += len(gauge_result)
            
        if args[0] in ['lorentz_invariance', 'full']:
            lorentz_result = process_checks.check_lorentz(myprocdef,
                                                      param_card = param_card)
            nb_processes += len(lorentz_result)
            
        cpu_time2 = time.time()

        logger.info("%i processes checked in %0.3f s" \
                    % (nb_processes,
                      (cpu_time2 - cpu_time1)))

        text = ""

        if gauge_result:
            text += 'Gauge results:\n'
            text += process_checks.output_gauge(gauge_result) + '\n'

        if lorentz_result:
            text += 'Lorentz invariance results:\n'
            text += process_checks.output_lorentz_inv(lorentz_result) + '\n'

        if comparisons:
            text += 'Process permutation results:\n'
            text += process_checks.output_comparisons(comparisons[0]) + '\n'
            self._comparisons = comparisons

        logger.info(text)
        pydoc.pager(text)
        # Restore diagram logger
        diag_logger.setLevel(old_level)

        return
    
    # Generate a new amplitude
    def do_generate(self, line):
        """Generate an amplitude for a given process"""

        # Reset amplitudes
        self._curr_amps = diagram_generation.AmplitudeList()
        # Reset Helas matrix elements
        self._curr_matrix_elements = None
        self._generate_info = line
        # Reset _done_export, since we have new process
        self._done_export = False
        # Also reset _export_format and _export_dir
        self._export_format = None

        # Remove previous generations from history
        self.clean_history(to_remove=['add process'], remove_bef_lb1='generate',
                           to_keep=['add','import','set','load'])

        # Call add process
        args = self.split_arg(line)
        args.insert(0, 'process')
        
        self.do_add(" ".join(args))
    
    def extract_process(self, line, proc_number = 0, overall_orders = {}):
        """Extract a process definition from a string. Returns
        a ProcessDefinition."""

        # Check basic validity of the line
        if not line.count('>') in [1,2]:
            self.do_help('generate')
            print
            raise self.InvalidCmd('Wrong use of \">\" special character.')
        

        # Perform sanity modifications on the lines:
        # Add a space before and after any > , $ / |
        space_before = re.compile(r"(?P<carac>\S)(?P<tag>[/\,\\$\\>|])(?P<carac2>\S)")
        line = space_before.sub(r'\g<carac> \g<tag> \g<carac2>', line)       
        
        # Use regular expressions to extract s-channel propagators,
        # forbidden s-channel propagators/particles, coupling orders
        # and process number, starting from the back

        # Start with process number (identified by "@")
        proc_number_pattern = re.compile("^(.+)@\s*(\d+)\s*(.*)$")
        proc_number_re = proc_number_pattern.match(line)
        if proc_number_re:
            proc_number = int(proc_number_re.group(2))
            line = proc_number_re.group(1) + \
                   proc_number_re.group(3)

        # Then take coupling orders (identified by "=")
        order_pattern = re.compile("^(.+)\s+(\w+)\s*=\s*(\d+)\s*$")
        order_re = order_pattern.match(line)
        orders = {}
        while order_re:
            orders[order_re.group(2)] = int(order_re.group(3))
            line = order_re.group(1)
            order_re = order_pattern.match(line)

        if self._use_lower_part_names:
            # Particle names lowercase
            line = line.lower()

        # Now check for forbidden particles, specified using "/"
        slash = line.find("/")
        dollar = line.find("$")
        forbidden_particles = ""
        if slash > 0:
            if dollar > slash:
                forbidden_particles_re = re.match("^(.+)\s*/\s*(.+\s*)(\$.*)$", line)
            else:
                forbidden_particles_re = re.match("^(.+)\s*/\s*(.+\s*)$", line)
            if forbidden_particles_re:
                forbidden_particles = forbidden_particles_re.group(2)
                line = forbidden_particles_re.group(1)
                if len(forbidden_particles_re.groups()) > 2:
                    line = line + forbidden_particles_re.group(3)

        # Now check for forbidden schannels, specified using "$"
        forbidden_schannels_re = re.match("^(.+)\s*\$\s*(.+)\s*$", line)
        forbidden_schannels = ""
        if forbidden_schannels_re:
            forbidden_schannels = forbidden_schannels_re.group(2)
            line = forbidden_schannels_re.group(1)

        # Now check for required schannels, specified using "> >"
        required_schannels_re = re.match("^(.+?)>(.+?)>(.+)$", line)
        required_schannels = ""
        if required_schannels_re:
            required_schannels = required_schannels_re.group(2)
            line = required_schannels_re.group(1) + ">" + \
                   required_schannels_re.group(3)

        args = self.split_arg(line)

        myleglist = base_objects.MultiLegList()
        state = False

        # Extract process
        for part_name in args:
            if part_name == '>':
                if not myleglist:
                    raise self.InvalidCmd, "No final state particles"
                state = True
                continue

            mylegids = []
            if part_name in self._multiparticles:
                if isinstance(self._multiparticles[part_name][0], list):
                    raise self.InvalidCmd,\
                          "Multiparticle %s is or-multiparticle" % part_name + \
                          " which can be used only for required s-channels"
                mylegids.extend(self._multiparticles[part_name])
            else:
                mypart = self._curr_model['particles'].find_name(part_name)
                if mypart:
                    mylegids.append(mypart.get_pdg_code())

            if mylegids:
                myleglist.append(base_objects.MultiLeg({'ids':mylegids,
                                                        'state':state}))
            else:
                raise self.InvalidCmd, \
                      "No particle %s in model" % part_name

        if filter(lambda leg: leg.get('state') == True, myleglist):
            # We have a valid process

            # Now extract restrictions
            forbidden_particle_ids = \
                              self.extract_particle_ids(forbidden_particles)
            if forbidden_particle_ids and \
               isinstance(forbidden_particle_ids[0], list):
                raise self.InvalidCmd,\
                      "Multiparticle %s is or-multiparticle" % part_name + \
                      " which can be used only for required s-channels"
            forbidden_schannel_ids = \
                              self.extract_particle_ids(forbidden_schannels)
            if forbidden_schannel_ids and \
               isinstance(forbidden_schannel_ids[0], list):
                raise self.InvalidCmd,\
                      "Multiparticle %s is or-multiparticle" % part_name + \
                      " which can be used only for required s-channels"
            required_schannel_ids = \
                               self.extract_particle_ids(required_schannels)
            if required_schannel_ids and not \
                   isinstance(required_schannel_ids[0], list):
                required_schannel_ids = [required_schannel_ids]
            

            return \
                base_objects.ProcessDefinition({'legs': myleglist,
                              'model': self._curr_model,
                              'id': proc_number,
                              'orders': orders,
                              'forbidden_particles': forbidden_particle_ids,
                              'forbidden_s_channels': forbidden_schannel_ids,
                              'required_s_channels': required_schannel_ids,
                              'overall_orders': overall_orders
                              })
      #                       'is_decay_chain': decay_process\

    def extract_particle_ids(self, args):
        """Extract particle ids from a list of particle names. If
        there are | in the list, this corresponds to an or-list, which
        is represented as a list of id lists. An or-list is used to
        allow multiple required s-channel propagators to be specified
        (e.g. Z/gamma)."""

        if isinstance(args, basestring):
            args.replace("|", " | ")
            args = self.split_arg(args)
        all_ids = []
        ids=[]
        for part_name in args:
            mypart = self._curr_model['particles'].find_name(part_name)
            if mypart:
                ids.append([mypart.get_pdg_code()])
            elif part_name in self._multiparticles:
                ids.append(self._multiparticles[part_name])
            elif part_name == "|":
                # This is an "or-multiparticle"
                if ids:
                    all_ids.append(ids)
                ids = []
            else:
                raise self.InvalidCmd("No particle %s in model" % part_name)
        all_ids.append(ids)
        # Flatten id list, to take care of multiparticles and
        # or-multiparticles
        res_lists = []
        for i, id_list in enumerate(all_ids):
            res_lists.extend(diagram_generation.expand_list_list(id_list))
        # Trick to avoid duplication while keeping ordering
        for ilist, idlist in enumerate(res_lists):
            set_dict = {}
            res_lists[ilist] = [set_dict.setdefault(i,i) for i in idlist \
                         if i not in set_dict]

        if len(res_lists) == 1:
            res_lists = res_lists[0]

        return res_lists

    def optimize_order(self, pdg_list):
        """Optimize the order of particles in a pdg list, so that
        similar particles are next to each other. Sort according to:
        1. pdg > 0, 2. spin, 3. color, 4. mass > 0"""

        if not pdg_list:
            return
        if not isinstance(pdg_list[0], int):
            return
        
        model = self._curr_model
        pdg_list.sort(key = lambda i: i < 0)
        pdg_list.sort(key = lambda i: model.get_particle(i).is_fermion())
        pdg_list.sort(key = lambda i: model.get_particle(i).get('color'),
                      reverse = True)
        pdg_list.sort(key = lambda i: \
                      model.get_particle(i).get('mass').lower() != 'zero')

    def extract_decay_chain_process(self, line, level_down=False):
        """Recursively extract a decay chain process definition from a
        string. Returns a ProcessDefinition."""

        # Start with process number (identified by "@") and overall orders
        proc_number_pattern = re.compile("^(.+)@\s*(\d+)\s*((\w+\s*=\s*\d+\s*)*)$")
        proc_number_re = proc_number_pattern.match(line)
        proc_number = 0
        overall_orders = {}
        if proc_number_re:
            proc_number = int(proc_number_re.group(2))
            line = proc_number_re.group(1)
            if proc_number_re.group(3):
                order_pattern = re.compile("^(.*?)\s*(\w+)\s*=\s*(\d+)\s*$")
                order_line = proc_number_re.group(3)
                order_re = order_pattern.match(order_line)
                while order_re:
                    overall_orders[order_re.group(2)] = int(order_re.group(3))
                    order_line = order_re.group(1)
                    order_re = order_pattern.match(order_line)
            logger.info(line)            
            
        index_comma = line.find(",")
        index_par = line.find(")")
        min_index = index_comma
        if index_par > -1 and (index_par < min_index or min_index == -1):
            min_index = index_par
        
        if min_index > -1:
            core_process = self.extract_process(line[:min_index], proc_number,
                                                overall_orders)
        else:
            core_process = self.extract_process(line, proc_number,
                                                overall_orders)

        #level_down = False

        while index_comma > -1:
            line = line[index_comma + 1:]
            if not line.strip():
                break
            index_par = line.find(')')
            if line.lstrip()[0] == '(':
                # Go down one level in process hierarchy
                #level_down = True
                line = line.lstrip()[1:]
                # This is where recursion happens
                decay_process, line = \
                            self.extract_decay_chain_process(line,
                                                             level_down=True)
                index_comma = line.find(",")
                index_par = line.find(')')
            else:
                index_comma = line.find(",")
                min_index = index_comma
                if index_par > -1 and \
                       (index_par < min_index or min_index == -1):
                    min_index = index_par
                if min_index > -1:
                    decay_process = self.extract_process(line[:min_index])
                else:
                    decay_process = self.extract_process(line)

            core_process.get('decay_chains').append(decay_process)

            if level_down:
                if index_par == -1:
                    raise self.InvalidCmd, \
                      "Missing ending parenthesis for decay process"

                if index_par < index_comma:
                    line = line[index_par + 1:]
                    level_down = False
                    break

        if level_down:
            index_par = line.find(')')
            if index_par == -1:
                raise self.InvalidCmd, \
                      "Missing ending parenthesis for decay process"
            line = line[index_par + 1:]
            
        # Return the core process (ends recursion when there are no
        # more decays)
        return core_process, line
    

    # Import files
    def do_import(self, line):
        """Import files with external formats"""

        args = self.split_arg(line)
        # Check argument's validity
        self.check_import(args)
        
        if args[0].startswith('model'):
            self._model_v4_path = None
            # Clear history, amplitudes and matrix elements when a model is imported
            # Remove previous imports, generations and outputs from history
            self.clean_history(remove_bef_lb1='import')
            # Reset amplitudes and matrix elements
            self._curr_amps = diagram_generation.AmplitudeList()
            self._curr_matrix_elements = helas_objects.HelasMultiProcess()
            # Import model
            if args[0].endswith('_v4'):
                self._curr_model, self._model_v4_path = \
                                 import_v4.import_model(args[1], self._mgme_dir)
                self._curr_fortran_model = \
                      helas_call_writers.FortranHelasCallWriter(\
                                                               self._curr_model)
            else:
                try:
                    self._curr_model = import_ufo.import_model(args[1])
                except import_ufo.UFOImportError, error:
                    logger_stderr.warning('WARNING: %s' % error)
                    logger_stderr.info('Trying to run `import model_v4 %s` instead.' \
                                                                      % args[1])
                    self.exec_cmd('import model_v4 %s ' % args[1], precmd=True)
                    return
                self._curr_fortran_model = \
                      helas_call_writers.FortranUFOHelasCallWriter(\
                                                               self._curr_model)
                self._curr_cpp_model = \
                      helas_call_writers.CPPUFOHelasCallWriter(\
                                                               self._curr_model)

            if '-modelname' not in args:
                self._curr_model.pass_particles_name_in_mg_default()

            # Do post-processing of model
            self.process_model()

            # Reset amplitudes and matrix elements and global checks
            self._curr_amps = diagram_generation.AmplitudeList()
            self._curr_matrix_elements = helas_objects.HelasMultiProcess()
            process_checks.store_aloha = []
            
        elif args[0] == 'command':
            # Remove previous imports, generations and outputs from history
            self.clean_history(to_remove=['import', 'generate', 'add process',
                                          'open','display','launch'])

            if not os.path.isfile(args[1]):
                raise self.InvalidCmd("Path %s is not a valid pathname" % args[1])
            else:
                # Check the status of export and try to use file position if no
                #self._export dir are define
                self.check_for_export_dir(args[1])
                # Execute the card
                self.use_rawinput = False
                self.import_command_file(args[1])
                self.use_rawinput = True    
        
        elif args[0] == 'proc_v4':
            
            # Remove previous imports, generations and outputs from history
            self.clean_history(to_remove=['import', 'generate', 'add process',
                                          'open','display','launch'])

            if len(args) == 1 and self._export_dir:
                proc_card = os.path.join(self._export_dir, 'Cards', \
                                                                'proc_card.dat')
            elif len(args) == 2:
                proc_card = args[1]
                # Check the status of export and try to use file position is no
                # self._export dir are define
                self.check_for_export_dir(os.path.realpath(proc_card))
            else:
                raise MadGraph5('No default directory in output')

 
            #convert and excecute the card
            self.import_mg4_proc_card(proc_card)

    
    def import_ufo_model(self, model_name):
        """ import the UFO model """
        
        self._curr_model = import_ufo.import_model(model_name)
        self._curr_fortran_model = \
                helas_call_writers.FortranUFOHelasCallWriter(self._curr_model)
        self._curr_cpp_model = \
                helas_call_writers.CPPUFOHelasCallWriter(self._curr_model)
                
    def process_model(self):
        """Set variables _particle_names and _couplings for tab
        completion, define multiparticles"""

         # Set variables for autocomplete
        self._particle_names = [p.get('name') for p in self._curr_model.get('particles')\
                                                    if p.get('propagating')] + \
                 [p.get('antiname') for p in self._curr_model.get('particles') \
                                                    if p.get('propagating')]
        
        self._couplings = list(set(sum([i.get('orders').keys() for i in \
                                        self._curr_model.get('interactions')], [])))
        # Check if we can use case-independent particle names
        self._use_lower_part_names = \
            (self._particle_names == \
             [p.get('name').lower() for p in self._curr_model.get('particles')] + \
             [p.get('antiname').lower() for p in self._curr_model.get('particles')])

        self.add_default_multiparticles()
        
    
    def import_mg4_proc_card(self, filepath):
        """ read a V4 proc card, convert it and run it in mg5"""
        
        # change the status of this line in the history -> pass in comment
        self.history[-1] = '#%s' % self.history[-1]
         
        # read the proc_card.dat
        reader = files.read_from_file(filepath, import_v4.read_proc_card_v4)
        if not reader:
            raise self.InvalidCmd('\"%s\" is not a valid path' % filepath)
        
        if self._mgme_dir:
            # Add comment to history
            self.exec_cmd("# Import the model %s" % reader.model, precmd=True)
            line = self.exec_cmd('import model_v4 %s -modelname' % \
                                 (reader.model), precmd=True)
        else:
            logging.error('No MG_ME installation detected')
            return    


        # Now that we have the model we can split the information
        lines = reader.extract_command_lines(self._curr_model)

        for line in lines:
            self.exec_cmd(line, precmd=True)
    
        return 
    
    def add_default_multiparticles(self):
        """ add default particle from file interface.multiparticles_default.txt
        """
        
        defined_multiparticles = self._multiparticles.keys()
        removed_multiparticles = []
        # First check if the defined multiparticles are allowed in the
        # new model
        for key in self._multiparticles.keys():
            try:
                for part in self._multiparticles[key]:
                    self._curr_model.get('particle_dict')[part]
            except:
                del self._multiparticles[key]
                defined_multiparticles.remove(key)
                removed_multiparticles.append(key)
        
        # Now add default multiparticles
        for line in open(os.path.join(MG5DIR, 'input', \
                                      'multiparticles_default.txt')):
            if line.startswith('#'):
                continue
            try:
                if self._use_lower_part_names:
                    multipart_name = line.lower().split()[0]
                else:
                    multipart_name = line.split()[0]
                if multipart_name not in self._multiparticles:
                    self.do_define(line)
                    
            except self.InvalidCmd, why:
                logger_stderr.warning('impossible to set default multiparticles %s because %s' %
                                        (line.split()[0],why))
        if defined_multiparticles:
            logger.info("Kept definitions of multiparticles %s unchanged" % \
                                         " / ".join(defined_multiparticles))

        for removed_part in removed_multiparticles:
            if removed_part in self._multiparticles:
                removed_multiparticles.remove(removed_part)

        if removed_multiparticles:
            logger.info("Removed obsolete multiparticles %s" % \
                                         " / ".join(removed_multiparticles))

    def do_install(self, line):
        """Install optional package from the MG suite."""
        
        args = self.split_arg(line)
        #check the validity of the arguments
        self.check_install(args)

        if sys.platform == "darwin":
            program = "curl"
        else:
            program = "wget"
            
        # Load file with path of the different program:
        import urllib
        path = {}
        try:
            data = urllib.urlopen('http://madgraph.phys.ucl.ac.be/package_info.dat')
        except:
            raise MadGraph5Error, '''Impossible to connect the server. 
            Please check your internet connection or retry later'''
        for line in data: 
            split = line.split()   
            path[split[0]] = split[1]
        
        name = {'td_mac': 'td', 'td_linux':'td', 'Delphes':'Delphes', 
                'pythia-pgs':'pythia-pgs', 'ExRootAnalysis': 'ExRootAnalysis',
                'MadAnalysis':'MadAnalysis'}
        name = name[args[0]]
        
        try:
            os.system('rm -rf %s' % name)
        except:
            pass
        
        # Load that path
        logger.info('Downloading %s' % path[args[0]])
        if sys.platform == "darwin":
            subprocess.call(['curl', path[args[0]], '-o%s.tgz' % name], cwd=MG5DIR)
        else:
            subprocess.call(['wget', path[args[0]], '--output-document=%s.tgz'% name], cwd=MG5DIR)
        # Untar the file
        returncode = subprocess.call(['tar', '-xzpvf', '%s.tgz' % name], cwd=MG5DIR)
        if returncode:
            raise MadGraph5Error, 'Fail to download correctly the File. Stop'
        
        # Check that the directory has the correct name
        if not os.path.exists(os.path.join(MG5DIR, name)):
            created_name = [n for n in os.listdir(MG5DIR) if n.startswith(name) 
                                                  and not n.endswith('gz')]
            if not created_name:
                raise MadGraph5Error, 'The file was not loaded correctly. Stop'
            else:
                created_name = created_name[0]
            files.mv(os.path.join(MG5DIR, created_name), os.path.join(MG5DIR, name))
        logger.info('compile %s. This might takes a while.' % name)
        
        # Modify Makefile for pythia-pgs on Mac 64 bit
        if args[0] == "pythia-pgs" and sys.maxsize > 2**32:
            for path in [os.path.join(MG5DIR, 'pythia-pgs', 'libraries', \
                         'PGS4', 'src', 'stdhep-dir', 'src', 'stdhep_Arch'),
                         os.path.join(MG5DIR, 'pythia-pgs', 'libraries', \
                         'PGS4', 'src', 'stdhep-dir', 'mcfio', 'arch_mcfio')]:
                text = open(path).read()
                text = text.replace('-m32','-m64')
                open(path, 'w').writelines(text)
            
        # Compile the file
        # Check for F77 compiler
        if 'FC' not in os.environ or not os.environ['FC']:
            if misc.which('g77'):
                os.environ['FC'] = 'g77'
            elif misc.which('gfortran'):
                os.environ['FC'] = 'gfortran'
            else:
                raise self.InvalidCmd('Require g77 or Gfortran compiler')
        subprocess.call(['make', 'clean'], cwd = os.path.join(MG5DIR, name))
        subprocess.call(['make'], cwd = os.path.join(MG5DIR, name))


        # Special treatment for TD program (require by MadAnalysis)
        if args[0] == 'MadAnalysis':
            try:
                os.system('rm -rf td')
                os.mkdir(os.path.join(MG5DIR, 'td'))
            except Exception, error:
                print error
                pass
            
            if sys.platform == "darwin":
                logger.info('Downloading TD for Mac')
                target = 'http://theory.fnal.gov/people/parke/TD/td_mac_intel.tar.gz'
                subprocess.call(['curl', target, '-otd.tgz'], 
                                                  cwd=os.path.join(MG5DIR,'td'))      
                subprocess.call(['tar', '-xzpvf', 'td.tgz'], 
                                                  cwd=os.path.join(MG5DIR,'td'))
                files.mv(MG5DIR + '/td/td_mac_intel',MG5DIR+'/td/td')
            else:
                logger.info('Downloading TD for Linux 32 bit')
                target = 'http://cp3wks05.fynu.ucl.ac.be/twiki/pub/Software/TopDrawer/td'
                subprocess.call(['wget', target], cwd=os.path.join(MG5DIR,'td'))      
                os.chmod(os.path.join(MG5DIR,'td','td'), 0775)
                if sys.maxsize > 2**32:
                    logger.warning('''td program (needed by MadAnalysis) is not compile for 64 bit computer
                Please follow instruction in http://cp3wks05.fynu.ucl.ac.be/twiki/bin/view/Software/TopDrawer.''')


    
    def set_configuration(self, config_path=None):
        """ assign all configuration variable from file 
            ./input/mg5_configuration.txt. assign to default if not define """
            
        self.configuration = {'pythia8_path': './pythia8',
                              'web_browser':None,
                              'eps_viewer':None,
                              'text_editor':None,
                              'fortran_compiler':None}
        
        if not config_path:
            try:
                config_file = open(os.path.join(os.environ['HOME'],'.mg5', 'mg5_configuration.txt'))
            except:
                config_file = open(os.path.relpath(
                          os.path.join(MG5DIR,'input','mg5_configuration.txt')))
        else:
            config_file = open(config_path)

        # read the file and extract information
        logger.info('load MG5 configuration from %s ' % config_file.name)
        for line in config_file:
            if '#' in line:
                line = line.split('#',1)[0]
            line = line.replace('\n','').replace('\r\n','')
            try:
                name, value = line.split('=')
            except ValueError:
                pass
            else:
                name = name.strip()
                value = value.strip()
                self.configuration[name] = value
                if value.lower() == "none":
                    self.configuration[name] = None

        # Treat each expected input
        # 1: Pythia8_path
        # try relative path
        for key in self.configuration:
            if key == 'pythia8_path':
                pythia8_dir = os.path.join(MG5DIR, self.configuration['pythia8_path'])
                if not os.path.isfile(os.path.join(pythia8_dir, 'include', 'Pythia.h')):
                    if os.path.isfile(os.path.join(self.configuration['pythia8_path'], 'include', 'Pythia.h')):
                        pythia8_dir = self.configuration['pythia8_path']
                    else:
                        pythia8_dir = None
                self.pythia8_path = pythia8_dir
            elif key.endswith('path'):
                pass
            elif key in ['cluster_type', 'automatic_html_opening']:
                pass
            elif key not in ['text_editor','eps_viewer','web_browser']:
                # Default: try to set parameter
                try:
                    self.do_set("%s %s" % (key, self.configuration[key]))
                except MadGraph5Error:
                    logger.warning("Option %s from config file not understood" \
                                   % key)
        
        # Configure the way to open a file:
        launch_ext.open_file.configure(self.configuration)
          
        return self.configuration
     
    def check_for_export_dir(self, filepath):
        """Check if the files is in a valid export directory and assign it to
        export path if if is"""

        # keep previous if a previous one is defined
        if self._export_dir:
            return
        
        if os.path.exists(os.path.join(os.getcwd(), 'Cards')):    
            self._export_dir = os.getcwd()
            return
    
        path_split = filepath.split(os.path.sep)
        if len(path_split) > 2 and path_split[-2] == 'Cards':
            self._export_dir = os.path.sep.join(path_split[:-2])
            return

    def do_launch(self, line):
        """Ask for editing the parameter and then 
        Execute the code (madevent/standalone/...)
        """
        start_cwd = os.getcwd()
        
        args = self.split_arg(line)
        # check argument validity and normalise argument
        (options, args) = _launch_parser.parse_args(args)
        self.check_launch(args, options)
        options = options.__dict__
        # args is now MODE PATH
        
        if args[0].startswith('standalone'):
            ext_program = launch_ext.SALauncher(args[1], self.timeout,
                                                **options)
        elif args[0] == 'madevent':
            if options['interactive']:
                if hasattr(self, 'do_shell'):
                    ME = madevent_interface.MadEventCmdShell(me_dir=args[1])
                else:
                     ME = madevent_interface.MadEventCmdShell(me_dir=args[1])
                self.define_child_cmd_interface(ME)
                return
            
            #check if this is a cross-section
            if len(self._generate_info.split('>')[0].strip().split())>1:
                ext_program = launch_ext.MELauncher(args[1], self.timeout, self,
                                pythia=self.configuration['pythia-pgs_path'],
                                delphes=self.configuration['delphes_path'],
                                shell = hasattr(self, 'do_shell'),
                                **options)
            else:
                # This is a width computation
                ext_program = launch_ext.MELauncher(args[1], self.timeout, self, 
                                unit='GeV',
                                pythia=self.configuration['pythia-pgs_path'],
                                delphes=self.configuration['delphes_path'],
                                shell = hasattr(self, 'do_shell'),
                                **options)
        elif args[0] == 'pythia8':
            ext_program = launch_ext.Pythia8Launcher(args[1], self.timeout,
                                                **options)
        else:
            os.chdir(start_cwd) #ensure to go to the initial path
            raise self.InvalidCmd , '%s cannot be run from MG5 interface' % args[0]
        
        
        ext_program.run()
        os.chdir(start_cwd) #ensure to go to the initial path
        
        
        
    
    def do_load(self, line):
        """Not in help: Load information from file"""

        args = self.split_arg(line)
        # check argument validity
        self.check_load(args)

        cpu_time1 = time.time()
        if args[0] == 'model':
            self._curr_model = save_load_object.load_from_file(args[1])
            if self._curr_model.get('parameters'):
                # This is a UFO model
                self._model_v4_path = None
                self._curr_fortran_model = \
                  helas_call_writers.FortranUFOHelasCallWriter(self._curr_model)
            else:
                # This is a v4 model
                self._model_v4_path = import_v4.find_model_path(\
                    self._curr_model.get('name').replace("_v4", ""),
                    self._mgme_dir)
                self._curr_fortran_model = \
                  helas_call_writers.FortranHelasCallWriter(self._curr_model)

            # Do post-processing of model
            self.process_model()
                
            #save_model.save_model(args[1], self._curr_model)
            if isinstance(self._curr_model, base_objects.Model):
                cpu_time2 = time.time()
                logger.info("Loaded model from file in %0.3f s" % \
                      (cpu_time2 - cpu_time1))
            else:
                raise self.RWError('Could not load model from file %s' \
                                      % args[1])
        elif args[0] == 'processes':
            amps = save_load_object.load_from_file(args[1])
            if isinstance(amps, diagram_generation.AmplitudeList):
                cpu_time2 = time.time()
                logger.info("Loaded processes from file in %0.3f s" % \
                      (cpu_time2 - cpu_time1))
                if amps:
                    model = amps[0].get('process').get('model')
                    if not model.get('parameters'):
                        # This is a v4 model.  Look for path.
                        self._model_v4_path = import_v4.find_model_path(\
                                   model.get('name').replace("_v4", ""),
                                   self._mgme_dir)
                        self._curr_fortran_model = \
                                helas_call_writers.FortranHelasCallWriter(\
                                                              model)
                    else:
                        self._model_v4_path = None
                        self._curr_fortran_model = \
                                helas_call_writers.FortranUFOHelasCallWriter(\
                                                              model)
                    # If not exceptions from previous steps, set
                    # _curr_amps and _curr_model
                    self._curr_amps = amps                    
                    self._curr_model = model
                    logger.info("Model set from process.")
                    # Do post-processing of model
                    self.process_model()
                self._done_export = None
            else:
                raise self.RWError('Could not load processes from file %s' % args[1])
    
    def do_save(self, line):
        """Not in help: Save information to file"""

        args = self.split_arg(line)
        # Check argument validity
        self.check_save(args)

        if args[0] == 'model':
            if self._curr_model:
                #save_model.save_model(args[1], self._curr_model)
                if save_load_object.save_to_file(args[1], self._curr_model):
                    logger.info('Saved model to file %s' % args[1])
            else:
                raise self.InvalidCmd('No model to save!')
        elif args[0] == 'processes':
            if self._curr_amps:
                if save_load_object.save_to_file(args[1], self._curr_amps):
                    logger.info('Saved processes to file %s' % args[1])
            else:
                raise self.InvalidCmd('No processes to save!')
    
    # Set an option
    def do_set(self, line):
        """Set an option, which will be default for coming generations/outputs
        """

        args = self.split_arg(line)
        
        # Check the validity of the arguments
        self.check_set(args)

        if args[0] == 'ignore_six_quark_processes':
            self._options[args[0]] = list(set([abs(p) for p in \
                                      self._multiparticles[args[1]]\
                                      if self._curr_model.get_particle(p).\
                                      is_fermion() and \
                                      self._curr_model.get_particle(abs(p)).\
                                      get('color') == 3]))
            logger.info('Ignore processes with >= 6 quarks (%s)' % \
                        ",".join([\
                            self._curr_model.get_particle(q).get('name') \
                            for q in self._options[args[0]]]))
            
        elif args[0] == 'group_subprocesses':
            self._options[args[0]] = eval(args[1])
            logger.info('Set group_subprocesses to %s' % \
                        str(self._options[args[0]]))
            logger.info('Note that you need to regenerate all processes')
            self._curr_amps = diagram_generation.AmplitudeList()
            self._curr_matrix_elements = helas_objects.HelasMultiProcess()

        elif args[0] == "stdout_level":
            logging.root.setLevel(eval('logging.' + args[1]))
            logging.getLogger('madgraph').setLevel(eval('logging.' + args[1]))
            logger.info('set output information to level: %s' % args[1])
        
        elif args[0] == 'fortran_compiler':
            if args[1] != 'None':
                logger.info('set fortran compiler to %s' % args[1])
                self.configuration['fortran_compiler'] = args[1]
            else:
                self.configuration['fortran_compiler'] = None
    
    def do_open(self, line):
        """Open a text file/ eps file / html file"""
        
        args = self.split_arg(line)
        # Check Argument validity and modify argument to be the real path
        self.check_open(args)
        file_path = args[0]
        
        launch_ext.open_file(file_path)
                 
    def do_output(self, line):
        """Initialize a new Template or reinitialize one"""

        args = self.split_arg(line)
        # Check Argument validity
        self.check_output(args)

        # Remove previous outputs from history
        self.clean_history(to_remove=['display','open','history','launch','output'],
                           remove_bef_lb1='generate',
                           keep_last=True)
        
        noclean = '-noclean' in args
        force = '-f' in args 
        nojpeg = '-nojpeg' in args
        main_file_name = ""
        try:
            main_file_name = args[args.index('-name') + 1]
        except:
            pass
            
        if not force and not noclean and os.path.isdir(self._export_dir)\
               and self._export_format in ['madevent', 'standalone']:
            # Don't ask if user already specified force or noclean
            logger.info('INFO: directory %s already exists.' % self._export_dir)
            logger.info('If you continue this directory will be cleaned')
            answer = self.ask('Do you want to continue? [y/n]', 'y')
            if answer != 'y':
                raise self.InvalidCmd('Stopped by user request')

        group_subprocesses = self._export_format == 'madevent' and \
                             self._options['group_subprocesses']
        # Make a Template Copy
        if self._export_format == 'madevent':
            if group_subprocesses:
                self._curr_exporter = export_v4.ProcessExporterFortranMEGroup(\
                                      self._mgme_dir, self._export_dir,
                                      not noclean)
            else:
                self._curr_exporter = export_v4.ProcessExporterFortranME(\
                                      self._mgme_dir, self._export_dir,
                                      not noclean)
        elif self._export_format in ['standalone', 'matrix']:
            self._curr_exporter = export_v4.ProcessExporterFortranSA(\
                                  self._mgme_dir, self._export_dir,not noclean)
        elif self._export_format == 'standalone_cpp':
            export_cpp.setup_cpp_standalone_dir(self._export_dir, self._curr_model)
        elif not os.path.isdir(self._export_dir):
            os.makedirs(self._export_dir)

        if self._export_format in ['madevent', 'standalone']:
            self._curr_exporter.copy_v4template(modelname=self._curr_model.get('name'))            

        # Reset _done_export, since we have new directory
        self._done_export = False

        # Perform export and finalize right away
        self.export(nojpeg, main_file_name)

        # Automatically run finalize
        self.finalize(nojpeg)
            
        # Remember that we have done export
        self._done_export = (self._export_dir, self._export_format)

        # Reset _export_dir, so we don't overwrite by mistake later
        self._export_dir = None

    # Export a matrix element
    def export(self, nojpeg = False, main_file_name = ""):
        """Export a generated amplitude to file"""

        def generate_matrix_elements(self):
            """Helper function to generate the matrix elements before
            exporting"""

            # Sort amplitudes according to number of diagrams,
            # to get most efficient multichannel output
            self._curr_amps.sort(lambda a1, a2: a2.get_number_of_diagrams() - \
                                 a1.get_number_of_diagrams())

            cpu_time1 = time.time()
            ndiags = 0
            if not self._curr_matrix_elements.get_matrix_elements():
                if self._options['group_subprocesses']:
                    cpu_time1 = time.time()
                    dc_amps = [amp for amp in self._curr_amps if isinstance(amp, \
                                        diagram_generation.DecayChainAmplitude)]
                    non_dc_amps = diagram_generation.AmplitudeList(\
                             [amp for amp in self._curr_amps if not \
                              isinstance(amp, \
                                         diagram_generation.DecayChainAmplitude)])
                    subproc_groups = group_subprocs.SubProcessGroupList()
                    if non_dc_amps:
                        subproc_groups.extend(\
                                   group_subprocs.SubProcessGroup.group_amplitudes(\
                                                                       non_dc_amps))
                    for dc_amp in dc_amps:
                        dc_subproc_group = \
                                 group_subprocs.DecayChainSubProcessGroup.\
                                                           group_amplitudes(dc_amp)
                        subproc_groups.extend(\
                                  dc_subproc_group.\
                                        generate_helas_decay_chain_subproc_groups())

                    ndiags = sum([len(m.get('diagrams')) for m in \
                              subproc_groups.get_matrix_elements()])
                    self._curr_matrix_elements = subproc_groups
                    # assign a unique id number to all groups
                    uid = 0 
                    for group in subproc_groups:
                        uid += 1 # update the identification number
                        for me in group.get('matrix_elements'):
                            me.get('processes')[0].set('uid', uid)
                else:
                    self._curr_matrix_elements = \
                                 helas_objects.HelasMultiProcess(\
                                               self._curr_amps)
                    ndiags = sum([len(me.get('diagrams')) for \
                                  me in self._curr_matrix_elements.\
                                  get_matrix_elements()])
                    # assign a unique id number to all process
                    uid = 0 
                    for me in self._curr_matrix_elements.get_matrix_elements():
                        uid += 1 # update the identification number
                        me.get('processes')[0].set('uid', uid)

            cpu_time2 = time.time()
            return ndiags, cpu_time2 - cpu_time1

        # Start of the actual routine

        ndiags, cpu_time = generate_matrix_elements(self)

        calls = 0

        path = self._export_dir
        if self._export_format in ['standalone_cpp', 'madevent', 'standalone']:
            path = os.path.join(path, 'SubProcesses')
            
        cpu_time1 = time.time()

        # First treat madevent and pythia8 exports, where we need to
        # distinguish between grouped and ungrouped subprocesses

        # MadEvent
        if self._export_format == 'madevent':
            if isinstance(self._curr_matrix_elements, group_subprocs.SubProcessGroupList):
                for (group_number, me_group) in enumerate(self._curr_matrix_elements):
                    calls = calls + \
                         self._curr_exporter.generate_subprocess_directory_v4(\
                                me_group, self._curr_fortran_model,
                                group_number)
            else:
                for me_number, me in \
                   enumerate(self._curr_matrix_elements.get_matrix_elements()):
                    calls = calls + \
                            self._curr_exporter.generate_subprocess_directory_v4(\
                                me, self._curr_fortran_model, me_number)


            # Write the procdef_mg5.dat file with process info
            card_path = os.path.join(path, os.path.pardir, 'SubProcesses', \
                                     'procdef_mg5.dat')
            if self._generate_info:
                self._curr_exporter.write_procdef_mg5(card_path,
                                self._curr_model['name'],
                                self._generate_info)
                try:
                    cmd.Cmd.onecmd(self, 'history .')
                except:
                    pass
                
        # Pythia 8
        if self._export_format == 'pythia8':
            # Output the process files
            process_names = []
            if isinstance(self._curr_matrix_elements, group_subprocs.SubProcessGroupList):
                for (group_number, me_group) in enumerate(self._curr_matrix_elements):
                    exporter = export_cpp.generate_process_files_pythia8(\
                            me_group.get('matrix_elements'), self._curr_cpp_model,
                            process_string = me_group.get('name'),
                            process_number = group_number, path = path)
                    process_names.append(exporter.process_name)
            else:
                exporter = export_cpp.generate_process_files_pythia8(\
                            self._curr_matrix_elements, self._curr_cpp_model,
                            process_string = self._generate_info, path = path)
                process_names.append(exporter.process_file_name)

            # Output the model parameter and ALOHA files
            model_name, model_path = export_cpp.convert_model_to_pythia8(\
                            self._curr_model, self._export_dir)

            # Generate the main program file
            filename, make_filename = \
                      export_cpp.generate_example_file_pythia8(path,
                                                               model_path,
                                                               process_names,
                                                               exporter,
                                                               main_file_name)

        # Pick out the matrix elements in a list
        matrix_elements = \
                        self._curr_matrix_elements.get_matrix_elements()

        # Fortran MadGraph Standalone
        if self._export_format == 'standalone':
            for me in matrix_elements:
                calls = calls + \
                        self._curr_exporter.generate_subprocess_directory_v4(\
                            me, self._curr_fortran_model)

        # Just the matrix.f files
        if self._export_format == 'matrix':
            for me in matrix_elements:
                filename = os.path.join(path, 'matrix_' + \
                           me.get('processes')[0].shell_string() + ".f")
                if os.path.isfile(filename):
                    logger.warning("Overwriting existing file %s" % filename)
                else:
                    logger.info("Creating new file %s" % filename)
                calls = calls + self._curr_exporter.write_matrix_element_v4(\
                    writers.FortranWriter(filename),\
                    me, self._curr_fortran_model)

        # C++ standalone
        if self._export_format == 'standalone_cpp':
            for me in matrix_elements:
                export_cpp.generate_subprocess_directory_standalone_cpp(\
                              me, self._curr_cpp_model,
                              path = path)
                
        cpu_time2 = time.time() - cpu_time1

        logger.info(("Generated helas calls for %d subprocesses " + \
              "(%d diagrams) in %0.3f s") % \
              (len(matrix_elements),
               ndiags, cpu_time))

        if calls:
            if "cpu_time2" in locals():
                logger.info("Wrote files for %d helas calls in %0.3f s" % \
                            (calls, cpu_time2))
            else:
                logger.info("Wrote files for %d helas calls" % \
                            (calls))
                
        if self._export_format == 'pythia8':
            logger.info("- All necessary files for Pythia 8 generated.")
            logger.info("- Run \"launch\" and select %s.cc," % filename)
            logger.info("  or go to %s/examples and run" % path)
            logger.info("      make -f %s" % make_filename)
            logger.info("  (with process_name replaced by process name).")
            logger.info("  You can then run ./%s to produce events for the process" % \
                        filename)

        # Replace the amplitudes with the actual amplitudes from the
        # matrix elements, which allows proper diagram drawing also of
        # decay chain processes
        self._curr_amps = diagram_generation.AmplitudeList(\
               [me.get('base_amplitude') for me in \
                matrix_elements])

    def finalize(self, nojpeg, online = False):
        """Make the html output, write proc_card_mg5.dat and create
        madevent.tar.gz for a MadEvent directory"""
        
        # For v4 models, copy the model/HELAS information.
        if self._model_v4_path:
            logger.info('Copy %s model files to directory %s' % \
                        (os.path.basename(self._model_v4_path), self._export_dir))
            self._curr_exporter.export_model_files(self._model_v4_path)
            self._curr_exporter.export_helas(os.path.join(self._mgme_dir,'HELAS'))
        elif self._export_format in ['madevent', 'standalone']:
            logger.info('Export UFO model to MG4 format')
            # wanted_lorentz are the lorentz structures which are
            # actually used in the wavefunctions and amplitudes in
            # these processes
            wanted_lorentz = self._curr_matrix_elements.get_used_lorentz()
            wanted_couplings = self._curr_matrix_elements.get_used_couplings()
            self._curr_exporter.convert_model_to_mg4(self._curr_model,
                                           wanted_lorentz,
                                           wanted_couplings)
        if self._export_format == 'standalone_cpp':
            logger.info('Export UFO model to C++ format')
            # wanted_lorentz are the lorentz structures which are
            # actually used in the wavefunctions and amplitudes in
            # these processes
            wanted_lorentz = self._curr_matrix_elements.get_used_lorentz()
            wanted_couplings = self._curr_matrix_elements.get_used_couplings()
            export_cpp.convert_model_to_cpp(self._curr_model,
                                            os.path.join(self._export_dir),
                                            wanted_lorentz,
                                            wanted_couplings)
            export_cpp.make_model_cpp(self._export_dir)

        if self._export_format in ['madevent', 'standalone']:
            
            self._curr_exporter.finalize_v4_directory( \
                                           self._curr_matrix_elements,
                                           [self.history_header] + \
                                           self.history,
                                           not nojpeg,
                                           online,
                                           self.configuration['fortran_compiler'])

        if self._export_format in ['madevent', 'standalone', 'standalone_cpp']:
            logger.info('Output to directory ' + self._export_dir + ' done.')
        if self._export_format == 'madevent':
            logger.info('Type \"launch\" to generate events from this process, or see')
            logger.info(self._export_dir + '/README')
            logger.info('Run \"open index.html\" to see more information about this process.')

    def do_help(self, line):
        """ propose some usefull possible action """
        
        super(MadGraphCmd,self).do_help(line)
        
        if line:
            return
        
        if len(self.history) == 0:
            last_action_2 = 'mg5_start'
            last_action = 'mg5_start'
        else:
            args = self.history[-1].split()
            last_action = args[0]
            if len(args)>1: 
                last_action_2 = '%s %s' % (last_action, args[1])
            else: 
                last_action_2 = 'none'
        

#===============================================================================
# MadGraphCmd
#===============================================================================
class MadGraphCmdWeb(MadGraphCmd, CheckValidForCmdWeb):
    """The command line processor of MadGraph"""
 
    timeout = 1 # time authorize to answer question [0 is no time limit]
    
    def __init__(self, *arg, **opt):
    
        if os.environ.has_key('_CONDOR_SCRATCH_DIR'):
            self.writing_dir = os.path.join(os.environ['_CONDOR_SCRATCH_DIR'], \
                                                                 os.path.pardir)
        else:
            self.writing_dir = os.path.join(os.environ['MADGRAPH_DATA'],
                               os.environ['REMOTE_USER'])
            
        
        #standard initialization
        MadGraphCmd.__init__(self, mgme_dir = '', *arg, **opt)
    
    def finalize(self, nojpeg):
        """Finalize web generation""" 
        
        MadGraphCmd.finalize(self, nojpeg, online = True)

    # Generate a new amplitude
    def do_generate(self, line):
        """Generate an amplitude for a given process"""

        try:
           MadGraphCmd.do_generate(self, line)
        except:
            # put the stop logo on the web
            files.cp(self._export_dir+'/HTML/stop.jpg',self._export_dir+'/HTML/card.jpg')
            raise
    
    # Add a process to the existing multiprocess definition
    def do_add(self, line):
        """Generate an amplitude for a given process and add to
        existing amplitudes
        syntax:
        """
        try:
           MadGraphCmd.do_add(self, line)
        except:
            # put the stop logo on the web
            files.cp(self._export_dir+'/HTML/stop.jpg',self._export_dir+'/HTML/card.jpg')
            raise

#===============================================================================
# MadGraphCmd
#===============================================================================
class MadGraphCmdShell(MadGraphCmd, CompleteForCmd, CheckValidForCmd, cmd.CmdShell):
    """The command line processor of MadGraph""" 
    
    writing_dir = '.'
    timeout = 0 # time authorize to answer question [0 is no time limit]
    
    def preloop(self):
        """Initializing before starting the main loop"""

        self.prompt = 'mg5>'
        
        # By default, load the UFO Standard Model
        logger.info("Loading default model: sm")
        self.do_import('model sm')
        self.history.append('import model sm')


#===============================================================================
# Command Parser
#=============================================================================== 
# DRAW
_draw_usage = "draw FILEPATH [options]\n" + \
         "-- draw the diagrams in eps format\n" + \
         "   Files will be FILEPATH/diagrams_\"process_string\".eps \n" + \
         "   Example: draw plot_dir . \n"
_draw_parser = optparse.OptionParser(usage=_draw_usage)
_draw_parser.add_option("", "--horizontal", default=False,
                   action='store_true', help="force S-channel to be horizontal")
_draw_parser.add_option("", "--external", default=0, type='float',
                    help="authorizes external particles to end at top or " + \
                    "bottom of diagram. If bigger than zero this tune the " + \
                    "length of those line.")
_draw_parser.add_option("", "--max_size", default=1.5, type='float',
                         help="this forbids external line bigger than max_size")
_draw_parser.add_option("", "--non_propagating", default=True, \
                          dest="contract_non_propagating", action='store_false',
                          help="avoid contractions of non propagating lines") 
_draw_parser.add_option("", "--add_gap", default=0, type='float', \
                          help="set the x-distance between external particles")  

# LAUNCH PROGRAM
_launch_usage = "launch [DIRPATH] [options]\n" + \
         "-- execute the madevent/standalone/standalone_cpp/pythia8 output present in DIRPATH\n" + \
         "   By default DIRPATH is the latest created directory \n" + \
         "   (for pythia8, it should be the Pythia 8 main directory) \n" + \
         "   Example: launch PROC_sm_1 --name=run2 \n" + \
         "   Example: launch ../pythia8 \n"
_launch_parser = optparse.OptionParser(usage=_launch_usage)
_launch_parser.add_option("-f", "--force", default=False, action='store_true',
                                help="Use the card present in the directory in order to launch the different program")
_launch_parser.add_option("-n", "--name", default='', type='str',
                                help="Provide a name to the run (for madevent run)")
_launch_parser.add_option("-c", "--cluster", default=False, action='store_true',
                                help="submit the job on the cluster")
_launch_parser.add_option("-m", "--multicore", default=False, action='store_true',
                                help="submit the job on multicore core")

_launch_parser.add_option("-i", "--interactive", default=False, action='store_true',
                                help="Use Interactive Console [if available]")
_launch_parser.add_option("-s", "--laststep", default='', 
                                help="last program run in MadEvent run. [auto|parton|pythia|pgs|delphes]")
    
    
#===============================================================================
# __main__
#===============================================================================

if __name__ == '__main__':
    
    run_option = sys.argv
    if len(run_option) > 1:
        # The first argument of sys.argv is the name of the program
        input_file = open(run_option[1], 'rU')
        cmd_line = MadGraphCmd(stdin=input_file)
        cmd_line.use_rawinput = False #put it in non interactive mode
        cmd_line.cmdloop()
    else:
        # Interactive mode
        MadGraphCmd().cmdloop()    
