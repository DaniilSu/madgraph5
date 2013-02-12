      SUBROUTINE SETCUTS
C**************************************************************************
C     SET THE CUTS 
C**************************************************************************
      IMPLICIT NONE
c
c     INCLUDE
c
      include 'genps.inc'
      include 'nexternal.inc'
      include 'coupl.inc'
      include 'run.inc'
      include 'cuts.inc'
c
c     Constants
c
      double precision zero
      parameter       (ZERO = 0d0)
      real*8 Pi
      parameter( Pi = 3.14159265358979323846d0 )
      integer    lun
      parameter (lun=22)
c
c     LOCAL
c
      integer i,j
      integer icollider,detail_level
      logical  do_cuts(nexternal)
      integer ncheck
      logical done,fopened
C     
C     GLOBAL
C
c--masses and poles
      double precision pmass(nexternal)
      common/to_mass/  pmass
      double precision      spole(maxinvar),swidth(maxinvar),bwjac
      common/to_brietwigner/spole          ,swidth          ,bwjac
c--cuts
      double precision etmin(nincoming+1:nexternal)
      double precision etamax(nincoming+1:nexternal)
      double precision emin(nincoming+1:nexternal)
      double precision r2min(nincoming+1:nexternal,nincoming+1:nexternal)
      double precision s_min(nexternal,nexternal)
      double precision etmax(nincoming+1:nexternal)
      double precision etamin(nincoming+1:nexternal)
      double precision emax(nincoming+1:nexternal)
      double precision r2max(nincoming+1:nexternal,nincoming+1:nexternal)
      double precision s_max(nexternal,nexternal)
      common/to_cuts/  etmin, emin, etamax, r2min, s_min,
     $     etmax, emax, etamin, r2max, s_max

      double precision ptjmin4(4),ptjmax4(4),htjmin4(2:4),htjmax4(2:4)
      logical jetor
      common/to_jet_cuts/ ptjmin4,ptjmax4,htjmin4,htjmax4,jetor

c
c     les houches accord stuff to identify neutrinos
c
      integer maxflow
      parameter (maxflow=999)
      integer idup(nexternal,maxproc),mothup(2,nexternal,maxproc),
     &     icolup(2,nexternal,maxflow)
c      include 'leshouche.inc'
      common /c_leshouche_inc/idup,mothup,icolup
C
      LOGICAL  IS_A_J(NEXTERNAL),IS_A_LP(NEXTERNAL),IS_A_LM(NEXTERNAL)
      COMMON /TO_SPECISA/IS_A_J,IS_A_LP,IS_A_LM
c
c
c     reading parameters
      integer maxpara
      parameter (maxpara=100)
      character*20 param(maxpara),value(maxpara)
      integer npara
c
c     setup masses for the final-state particles (fills the /to_mass/ common block)
c
      include 'pmass.inc'

C-----
C  BEGIN CODE
C-----
c
c     No pdfs for decay processes - set here since here we know the nincoming
c     Also set stot here, and use mass of incoming particle for ren scale
c
         if(nincoming.eq.1)then
            lpp(1)=0
            lpp(2)=0
            ebeam(1)=pmass(1)/2d0
            ebeam(2)=pmass(1)/2d0
            scale=pmass(1)
            fixed_ren_scale=.true.
         endif
c-check consistency of maxjetflavor in the run_card and with Nf
c specified in coupl.inc
      if (maxjetflavor.gt.int(Nf)) then
          write(*,*) "WARNING: the value of maxjetflavor specified in"//
     1   " the run_card is inconsistent with the number of light"//
     1   " flavours in the model."
          write(*,*)"Hence it will be set to ", int(Nf)
          maxjetflavor = int(Nf)
      endif
      


      do i=nincoming+1,nexternal
         is_a_j(i)=.false.
         is_a_lp(i)=.false.
         is_a_lm(i)=.false.

c-light-jets
         if (abs(idup(i,1)).le.min(maxjetflavor,5)) then
              is_a_j(i)=.true.
         endif
         if (abs(idup(i,1)).eq.21)  is_a_j(i)=.true. ! gluon is a jet

c-charged-leptons
         if (idup(i,1).eq.11)  is_a_lm(i)=.true. !  e-
         if (idup(i,1).eq.13)  is_a_lm(i)=.true. !  mu-
         if (idup(i,1).eq.15)  is_a_lm(i)=.true. !  ta-
         if (idup(i,1).eq.-11) is_a_lp(i)=.true. !  e-
         if (idup(i,1).eq.-13) is_a_lp(i)=.true. !  mu-
         if (idup(i,1).eq.-15) is_a_lp(i)=.true. !  ta-
      enddo

      RETURN
      END


      subroutine set_tau_min()
c Sets the lower bound for tau=x1*x2, using information on particle
c masses and on the jet minimum pt, as entered in run_card.dat, 
c variable ptj
      implicit none
      double precision zero,vtiny
      parameter (zero=0.d0,vtiny=1d-8)
      include 'cuts.inc'
      include 'run.inc'
      include 'genps.inc'
      include 'nexternal.inc'
      include 'coupl.inc'
      include 'nFKSconfigs.inc'
      include "fks_info.inc"
      LOGICAL  IS_A_J(NEXTERNAL),IS_A_LP(NEXTERNAL),IS_A_LM(NEXTERNAL)
      COMMON /TO_SPECISA/IS_A_J,IS_A_LP,IS_A_LM
c
      double precision pmass(-nexternal:0,lmaxconfigs)
      double precision pwidth(-nexternal:0,lmaxconfigs)
      integer pow(-nexternal:0,lmaxconfigs)
      integer itree(2,-max_branch:-1),iconfig
      common /to_itree/itree,iconfig
      INTEGER NFKSPROCESS
      COMMON/C_NFKSPROCESS/NFKSPROCESS
      double precision taumin(fks_configs),taumin_s(fks_configs)
     &     ,taumin_j(fks_configs),stot
      save  taumin,taumin_s,taumin_j,stot
      integer i,j,d1,d2,iFKS
      double precision xm(-nexternal:nexternal),xm1,xm2,xmi
      double precision xw(-nexternal:nexternal),xw1,xw2,xwi
      integer tsign,j_fks
      double precision tau_Born_lower_bound,tau_lower_bound_resonance
     &     ,tau_lower_bound
      common/ctau_lower_bound/tau_Born_lower_bound
     &     ,tau_lower_bound_resonance,tau_lower_bound
c
      real*8         emass(nexternal)
      common/to_mass/emass
      logical firsttime
      data firsttime /.true./
      include "born_props.inc"

      if(.not.IS_A_J(NEXTERNAL))then
        write(*,*)'Fatal error in set_tau_min'
        stop
      endif
c The following assumes that light QCD particles are at the end of the
c list. Exclude one of them to set tau bound at the Born level This
c sets a hard cut in the minimal shat of the Born phase-space
c generation.
c
c The contribution from ptj should be treated only as a 'soft lower
c bound' if j_fks is initial state: the real-emission i_fks parton is
c not necessarily the softest.  Therefore, it could be that even though
c the Born does not have enough energy to pass the cuts set by ptj, the
c event could.
      if (firsttime) then
         firsttime=.false.
         do iFKS=1,fks_configs
            j_fks=FKS_J_D(iFKS)
            taumin(iFKS)=0.d0
            taumin_s(iFKS)=0.d0
            taumin_j(iFKS)=0.d0
            do i=nincoming+1,nexternal
c Add the minimal jet pTs to tau
               if(IS_A_J(i) .and. i.ne.nexternal)then
                  if (abs(emass(i)).gt.vtiny) then
                     write (*,*) 'Error in set_tau_min in setcuts.f:'
                     write (*,*) 'mass of a jet should be zero',i
     &                    ,emass(i)
                     stop
                  endif
                  if  (j_fks.gt.nincoming .and. j_fks.lt.nexternal) then
                     taumin(iFKS)=taumin(iFKS)+ptj
                     taumin_s(iFKS)=taumin_s(iFKS)+ptj
                     taumin_j(iFKS)=taumin_j(iFKS)+ptj
                  elseif (j_fks.ge.1 .and. j_fks.le.nincoming) then
                     taumin_s(iFKS)=taumin_s(iFKS)+ptj
                     taumin_j(iFKS)=taumin_j(iFKS)+ptj
                  elseif (j_fks.eq.nexternal) then
                     write (*,*)
     &                    'ERROR, j_fks cannot be the final parton'
     &                    ,j_fks
                     stop
                  else
                     write (*,*) 'ERROR, j_fks not correctly defined'
     &                    ,j_fks
                     stop
                  endif
                  xm(i)=emass(i)+ptj
               elseif (is_a_lp(i)) then
c Add the postively charged lepton pTs to tau
                  taumin(iFKS)=taumin(iFKS)+emass(i)
                  if (j_fks.gt.nincoming)
     &                 taumin(iFKS)=taumin(iFKS)+ptl
                  taumin_s(iFKS)=taumin_s(iFKS)+emass(i)+ptl
                  taumin_j(iFKS)=taumin_j(iFKS)+emass(i)+ptl
                  xm(i)=emass(i)+ptl
c Add the lepton invariant mass to tau if there is at least another
c lepton of opposite charge. (Only add half of it, i.e. 'the part
c contributing from this lepton'). Remove possible overcounting with the
c lepton pT
                  do j=nincoming+1,nexternal
                     if (is_a_lm(j)) then
                        if (j_fks.gt.nincoming) taumin(iFKS)=
     &                       taumin(iFKS)-ptl+max(mll/2d0,ptl)
                        taumin_s(iFKS)=
     &                       taumin_s(iFKS)-ptl+max(mll/2d0,ptl)
                        taumin_j(iFKS)=
     &                       taumin_j(iFKS)-ptl+max(mll/2d0,ptl)
                        xm(i)=xm(i)-ptl+max(mll/2d0,ptl)
                        exit
                     endif
                  enddo
               elseif (is_a_lm(i)) then
c Add the negatively charged lepton pTs to tau
                  taumin(iFKS)=taumin(iFKS)+emass(i)
                  if (j_fks.gt.nincoming)
     &                 taumin(iFKS)=taumin(iFKS)+ptl
                  taumin_s(iFKS)=taumin_s(iFKS)+emass(i)+ptl
                  taumin_j(iFKS)=taumin_j(iFKS)+emass(i)+ptl
                  xm(i)=emass(i)+ptl
c Add the lepton invariant mass to tau if there is at least another
c lepton of opposite charge. (Only add half of it, i.e. 'the part
c contributing from this lepton'). Remove possible overcounting with the
c lepton pT
                  do j=nincoming+1,nexternal
                     if (is_a_lp(j)) then
                        if (j_fks.gt.nincoming) taumin(iFKS)=
     &                       taumin(iFKS)-ptl+max(mll/2d0,ptl)
                        taumin_s(iFKS)=
     &                       taumin_s(iFKS)-ptl+max(mll/2d0,ptl)
                        taumin_j(iFKS)=
     &                       taumin_j(iFKS)-ptl+max(mll/2d0,ptl)
                        xm(i)=xm(i)-ptl+max(mll/2d0,ptl)
                        exit
                     endif
                  enddo
               else
                  taumin(iFKS)=taumin(iFKS)+emass(i)
                  taumin_s(iFKS)=taumin_s(iFKS)+emass(i)
                  taumin_j(iFKS)=taumin_j(iFKS)+emass(i)
                  xm(i)=emass(i)
               endif
               xw(i)=0d0
            enddo
            stot = 4d0*ebeam(1)*ebeam(2)
            tau_Born_lower_bound=taumin(iFKS)**2/stot
            tau_lower_bound=taumin_j(iFKS)**2/stot
c         
c Also find the minimum lower bound if all internal s-channel particles
c were on-shell
            tsign=-1
            do i=-1,-(nexternal-3),-1 ! All propagators
               if ( itree(1,i) .eq. 1 .or. itree(1,i) .eq. 2 ) tsign=1
               if (tsign.eq.-1) then ! Only s-channels
                  d1=itree(1,i)
                  d2=itree(2,i)
c If daughter is a jet, we should treat the ptj as a mass. Except if
c d1=nexternal, because we check the Born, so final parton should be
c skipped. [This is already done above; also for the leptons]
                  xm1=xm(d1)
                  xm2=xm(d2)
                  xw1=xw(d1)
                  xw2=xw(d2)
c On-shell mass of the intermediate resonance
                  xmi=pmass(i,iconfig)
c Width of the intermediate resonance
                  xwi=pwidth(i,iconfig)
c Set the intermediate mass equal to the max of its actual mass and
c the sum of the masses of the two daugters.
                  if (xmi.gt.xm1+xm2) then
                     xm(i)=xmi
                     xw(i)=xwi
                  else
                     xm(i)=xm1+xm2
                     xw(i)=xw1+xw2 ! just sum the widths
                  endif
c Add the new mass to the bound. To avoid double counting, we should
c subtract the daughters, because they are already included above or in
c the previous iteration of the loop
                  taumin_s(iFKS)=taumin_s(iFKS)+xm(i)-xm1 -xm2
               else
                  xm(i)=0d0
               endif
            enddo
c$$$cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c$$$c Determine the conflicting Breit-Wigner's. Note that xm(i) contains the
c$$$c mass of the BW
c$$$            do i=nincoming+1,nexternal-1
c$$$               mass_min(i)=xm(i) ! minimal allowed resonance mass (including masses set by cuts)
c$$$            enddo
c$$$            cBW_FKS_level_max(iFKS)=0
c$$$            do i=-1,-(nexternal-3),-1 ! All propagators
c$$$               cBW_FKS_mass(iFKS,1,i)=0d0
c$$$               cBW_FKS_width(iFKS,1,i)=0d0
c$$$               cBW_FKS_mass(iFKS,-1,i)=0d0
c$$$               cBW_FKS_width(iFKS,-1,i)=0d0
c$$$               if ( itree(1,i) .eq. 1 .or. itree(1,i) .eq. 2 ) exit ! only s-channels
c$$$               mass_min(i)=mass_min(itree(1,i))+mass_min(itree(2,i))
c$$$               if (xm(i).lt.mass_min(i)) then
c$$$                  write (*,*)
c$$$     $                 'ERROR in the determination of conflicting BW',i
c$$$     $                 ,xm(i),mass_min(i)
c$$$                  stop
c$$$               endif
c$$$               if (qmass(i).lt.xm(i)) then
c$$$c     Possible conflict in BW
c$$$                  if (qmass(i).lt.mass_min(i)) then
c$$$c     Resonance can never go on-shell due to the kinematics of the event
c$$$                     cBW_FKS(iFKS,i)=2
c$$$                     cBW_FKS_level(iFKS,i)=0
c$$$                  elseif(qmass(i).lt.xm(i)) then
c$$$c     Conflicting Breit-Wigner
c$$$                     cBW_FKS(iFKS,i)=1
c$$$                     cBW_FKS_level(iFKS,i)=1
c$$$                     cBW_FKS_level_max(iFKS)=max(cBW_FKS_level_max(iFKS)
c$$$     $                    ,cBW_FKS_level(iFKS,i))
c$$$c     Set here the mass (and width) of the alternative mass; it's the
c$$$c     sum of daughter masses. (3rd argument is '1', because this
c$$$c     alternative mass is LARGER than the resonance mass).
c$$$                     cBW_FKS_mass(iFKS,i,1)=xm(i)
c$$$                     cBW_FKS_width(iFKS,i,1)=xw(i)
c$$$                  endif
c$$$c     set the daughters also as conflicting (recursively)
c$$$                  do j=i,-1,-1
c$$$                     if (cBW_FKS(iFKS,j).ne.0) then
c$$$                        do k=1,2 ! loop over the 2 daughters
c$$$                           if(cBW_FKS(iFKS,itree(j,k)).eq.0 .and.
c$$$     &                          itree(j,k).lt.0) then
c$$$                              cBW_FKS(iFKS,itree(j,k))=1
c$$$                              cBW_FKS_level(iFKS,itree(j,k))=
c$$$     &                             cBW_FKS_level(iFKS,j)+1
c$$$                              cBW_FKS_level_max(iFKS)=
c$$$     $                             max(cBW_FKS_level_max(iFKS)
c$$$     $                             ,cBW_FKS_level(iFKS,itree(j,k)))
c$$$c     Set here the mass (and width) of the alternative mass; it's the
c$$$c     difference between the mother and the sister masses. (3rd argument
c$$$c     is '-1', because this alternative mass is SMALLER than the
c$$$c     resonance mass).
c$$$                              cBW_FKS_mass(iFKS,itree(j,k),-1)=
c$$$     &                             xm(j)-xm(itree(j,3-k)) ! mass difference
c$$$                              cBW_FKS_width(iFKS,itree(j,k),-1)=
c$$$     &                             xw(j)+xw(itree(j,3-k)) ! sum of widths
c$$$                           endif
c$$$                        enddo
c$$$                     endif
c$$$                  enddo
c$$$               else
c$$$c     Normal Breit-Wigner
c$$$                  cBW_FKS(iFKS,i)=0
c$$$               endif
c$$$            enddo
c$$$c Conflicting BW's determined. They are saved in cBW_FKS
c$$$cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c
c If the lower bound found here is smaller than the hard bound,
c simply set the soft bound equal to the hard bound.
            taumin_s(iFKS)=
     &           max(taumin_j(iFKS),taumin_s(iFKS))
c
c For the bound, we have to square and divide by stot.
            tau_lower_bound_resonance=taumin_s(iFKS)**2/stot
c
            write (*,'(a,i3,a,3(e12.5,x))') 'nFKSprocess:',iFKS
     &           ,'. Absolute lower bound for tau at the Born is'
     &           ,tau_Born_lower_bound,taumin(iFKS),dsqrt(stot) 
            if (j_fks.le.nincoming) then
               write (*,'(a,i3,a,3(e12.5,x))') 'nFKSprocess:',iFKS
     &              ,'. Lower bound for tau is',tau_lower_bound
     &              ,taumin_j(iFKS),dsqrt(stot)
            endif
            write (*,'(a,i3,a,3(e12.5,x))') 'nFKSprocess:',iFKS
     &           ,'. Lower bound for tau is (taking resonances'/
     &           /' into account)' ,tau_lower_bound_resonance
     &           ,taumin_s(iFKS) ,dsqrt(stot)
         enddo
      endif
      tau_Born_lower_bound=taumin(nFKSprocess)**2/stot
      tau_lower_bound=taumin_j(nFKSprocess)**2/stot
      tau_lower_bound_resonance=taumin_s(nFKSprocess)**2/stot
      return
      end


