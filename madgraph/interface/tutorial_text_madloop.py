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

tutorial_MadLoop = """
You have entered tutorial mode. This will introduce you to the main
syntax options for MadLoop which are mostly similar to the MadGraph5 one. 
If you have not done so already, please follow MadGraph5 tutorial before 
this one.  

Remember that exactly as in MadGraph5, you can learn more about the different 
options for any command by typing
aMC@NLO> help A_CMD
And to see a list of all commands, use
aMC@NLO> help 

MadLoop is the part of MadGraph5 used by aMC@NLO to generate the code for
evaluating the loop diagrams. This tutorial teaches you how to use MadLoop
as standalone tool for studying loops within particular processes.
Therefore in this mode, you can only consider definite processes, meaning 
without multiparticle labels.

This tutorial has three parts:
a) How to generate a process.
b) How to cross-check / profile an output.
c) How to compute the loop matrix element squared for local phase-space points.

Let's start with the first point, how to generate a process with MadLoop in
standalone mode. Keep in mind that this means only the loop and born diagrams
are generated.

mgg5>generate g g > d d~ [virt=QCD]

Note that a space is mandatory between the particle names and that '[virt=QCD]' 
specifies that you want to consider QCD NLO corrections. The keyword option
'virt' before '=' within the squared brackets precisely specifies you are only
interested in the virtual contribution. 
You will notice that MG5 recognizes you want to use standalone MadLoop because
the header of your interface will change from 'mg5>' to 'ML5>'. 
"""

tutorial = tutorial_MadLoop

generate = """
You have just generated a new process.
You can find more information on supported syntax by using:
ML5>help generate
To list all defined processes, type
ML5>display processes

You can display a pictorial representation of the diagrams with 
ML5> display diagrams
Notice you can add the option 'loop' or 'born' if you only want those diagrams
to be displayed.

If you want to add a second process, you can use the add process command:
ML5>add process e+ e- > d d~ [virt=QCD]
But keep in mind that you must still consider only virtual corrections and 
cannot employ multiparticle labels. Also decay chains are not available for
loops.

At this stage you can export your processes.
This is done simply by typing:

ML5>output MY_FIRST_MADLOOP_RUN

Notice that the standalone output mode (implicit in the above) is the only
available for MadLoop standalone runs.
"""

display_processes = """
You have seen a list of the already defined processes.

At this stage you can export your processes to different formats. 
To create a MadLoop standalone output for these, simply type:

ML5>output MY_FIRST_MADLOOP_RUN
"""

display_diagrams = """
You have displayed the diagrams.
Notice you can add the 'born' or 'loop' option to this command to specify the
class of diagrams to be displayed.

At this stage you can export your processes to different formats. 
To create a MadLoop standalone output for these, simply type:

ML5>output MY_FIRST_MADLOOP_RUN
"""

add_process = """
You have added a process to your process list.

At this stage you can export your processes.
For this, simply type

ML5>output MY_FIRST_MADLOOP_RUN
"""

output = """
If you are following the tutorial, a directory MY_FIRST_MADLOOP_RUN has
been created under your MadGraph5 installation directory.

The code for the evaluation of the squared loop matrix element is in 
'SubProcesses/P0_<shell_proc_name>/'. There, you can compile and edit 
running parameters from 'MadloopParams.dat' and then run the code with './check'
Alternatively, for a simple quick run, type:

ML5>launch -f

This computes the squared matrix element for a given PS points.
For the purpose of this tutorial, the option '-f' is added to automatically skip
the edition of the cards and phase-space point specification.
"""

launch = """
You just launched the MadLoop standalone evalutation of the squared loop matrix
element for (a/many) specific process(es) for a random Phase-Space point.
The two processes proposed in this tutorial were g g > d d~ and e+ e- > d d~.
You can check that you get the right double pole normalized with respect to
the born*(alpha_s/2*pi), namely -26/3 and -8/3 respectively.

Now this tutorial will introduce you to two checking functionalities for the
evaluation of the contributions of virtual origin.
Start by typing:

ML5>check g g > d d~ [virt=QCD]

This will test lorentz and crossing invariance as well as of the gauge 
invariance check from the ward identity for the initial state gluon.
You can add an option after check to specify to perform only one definite check.
Notice that the check functionality is only available for MadLoop standalone
runs (those with the 'virt=' option).
"""

check = """
You have seen the results for the various consistency checks performed on the
MadGraph5 loop computation.
You can now use the check command to obtain a full profiling of a given process
including loop contributions.
Simply type:

ML5>check profile g g > d d~ [virt=QCD]

Notice that you can replace 'profile' by 'timing' or 'stability' if
you only want timing or stability benchmarks about this process.
"""

check_profile = """
You have seen detailed information about the stability, timings and code size
of a given process including loop.
Keep in mind that these check functionalities are only available for MadLoop
standalone runs.

You just learned the basic commands for the MadLoop runs (i.e. with the 
'virt=' option). You can close this tutorial by typing
ML5>tutorial stop
Or exit MG5 with
ML5>exit
"""
