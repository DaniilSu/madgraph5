      program madspin
      implicit none

C---  integer    n_max_cg
      INCLUDE "ngraphs.inc"     !how many diagrams 
      double precision ZERO
      parameter (ZERO=0D0)
      !include 'genps.inc'
      include 'coupl.inc'
      include 'nexternal.inc'
      include 'nexternal_prod.inc'
      !include 'run.inc'

C     
C     LOCAL
C     
      INTEGER I,J,K
      REAL*8 P(0:3,NEXTERNAL_PROD) 
      REAL*8 PFULL(0:3,NEXTERNAL) 
      double precision x(36), Ecollider
      CHARACTER*120 BUFF(NEXTERNAL_PROD)
      integer iforest(2,-nexternal:-1,N_MAX_CG)
      integer itree(2,-nexternal:-1), iconfig
c      integer mapconfig(0:lmaxconfigs)
      integer sprop(1,-nexternal:-1,N_MAX_CG) ! first col has one entry, since we should have group_processes=false
      integer tprid(-nexternal:-1,N_MAX_CG)
      integer            mapconfig(0:N_MAX_CG), this_config
      common/to_mconfigs/mapconfig, this_config
      double precision prmass(-nexternal:0,N_MAX_CG)
      double precision prwidth(-nexternal:0,N_MAX_CG)
      integer pow(-nexternal:0,N_MAX_CG)
      double precision qmass(-nexternal:0),qwidth(-nexternal:0),jac
      double precision M_PROD, M_FULL
      logical notpass
      integer counter,mode,nbpoints
      double precision mean, variance, maxweight,weight,std
      double precision temp

      ! variables to keep track of the vegas numbers for the production part
      logical keep_inv(-nexternal:-1),no_gen
      integer ivar
      double precision fixedinv(-nexternal:0)
      double precision phi_tchan(-nexternal:0),m2_tchan(-nexternal:0)
      double precision cosphi_schan(-nexternal:0), phi_schan(-nexternal:0)
      common /to_fixed_kin/keep_inv,no_gen, ivar, fixedinv,
     & phi_tchan,m2_tchan,cosphi_schan, phi_schan 

       double precision BWcut, maxBW
       common /to_BWcut/BWcut, maxBW

c Conflicting BW stuff
      integer cBW_level_max,cBW(-nexternal:-1),cBW_level(-nexternal:-1)
      double precision cBW_mass(-nexternal:-1,-1:1),
     &     cBW_width(-nexternal:-1,-1:1)
      common/c_conflictingBW/cBW_mass,cBW_width,cBW_level_max,cBW
     $     ,cBW_level


      DOUBLE PRECISION AMP2(n_max_cg)
      COMMON/TO_AMPS/  AMP2


      call ntuple(x,0d0,1d0,1,2)  ! initialize the sequence of random
                                  ! numbers at the position reached 
                                  ! at the previous termination of the
                                  ! code

cccccccccccccccccccccccccccccccccccccccccccccccccccc
c   I. read momenta for the production events
c
cccccccccccccccccccccccccccccccccccccccccccccccccccc

      ! hard-code  for testing
c      buff(1)="1   0.5000000E+03  0.0000000E+00  0.0000000E+00  0.5000000E+03  0.0000000E+00"
c      buff(2)="2   0.5000000E+03  0.0000000E+00  0.0000000E+00 -0.5000000E+03  0.0000000E+00"
c      buff(3)="3   0.5000000E+03  0.1040730E+03  0.4173556E+03 -0.1872274E+03  0.1730000E+03"
c      buff(4)="4   0.5000000E+03 -0.1040730E+03 -0.4173556E+03  0.1872274E+03  0.1730000E+03"
c      do i=1,nexternal_prod
c         read (buff(i),*) k, P(0,i),P(1,i),P(2,i),P(3,i)
c      enddo

 
1     continue
      maxBW=0d0
      read(*,*) mode,  BWcut, Ecollider, temp

      if (mode.eq.1) then    ! calculate the maximum weight
         nbpoints=int(temp)
      elseif (mode.eq.2) then
         maxweight=temp      ! unweight decay config   
      elseif (mode.eq.3) then
         continue      ! just retrun the value of M_full   
      else
         call ntuple(x,0d0,1d0,1,1)  ! write down the position of the sequence of random nbs
         goto 2                      ! and close the program  
      endif

      do i=1,nexternal_prod
         read (*,*) P(0,i),P(1,i),P(2,i),P(3,i) 
      enddo

cccccccccccccccccccccccccccccccccccccccccccccccccccc      
c    II. initialization of masses and widths        c
c       also load production topology information  c
cccccccccccccccccccccccccccccccccccccccccccccccccccc  

      include 'configs_production.inc'

      call coup()

      include 'props_production.inc'

      ! set masses 
      call set_parameters(p,Ecollider)

      ! do not consider the case of conflicting BW
      do i = -nexternal, -1
         cBW(i)=0
         cBW_level(i)=0
      enddo

cccccccccccccccccccccccccccccccccccccccccccccccccccc
c   III. compute production matrix element         c 
cccccccccccccccccccccccccccccccccccccccccccccccccccc

      do i=1,n_max_cg
      amp2(i)=0d0
      enddo
      call coup()
      CALL SMATRIX_PROD(P,M_PROD)
c      write(*,*) 'M_prod ', M_prod
cccccccccccccccccccccccccccccccccccccccccccccccccccc
c   IV. select one topology                        c
cccccccccccccccccccccccccccccccccccccccccccccccccccc

      call get_config(iconfig)

      do i=-nexternal_prod+2,-1
         do j=1,2
            itree(j,i)=iforest(j,i,iconfig)
         enddo
      enddo

      do i=-nexternal_prod+3,-1
         qmass(i)=prmass(i,iconfig)
         qwidth(i)=prwidth(i,iconfig)
      enddo

cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c   V. load topology for the whole event select                c
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc

       call  merge_itree(itree,qmass,qwidth, p)
       !write(*,*) keep_inv(-5)
       !write(*,*) 'm2_tchan ',m2_tchan(-5)
       !write(*,*) 'fixedinv', fixedinv(-5)
       !write(*,*)  'phi_tchan', phi_tchan(-5)
 
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c   VIa. Calculate the max. weight                                      c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc

      if (mode.eq.1) then

        mean=0d0
        variance=0d0
        maxweight=0d0

        do i=1,nbpoints
           jac=1d0
           ivar=0
           no_gen=.false.
           do j = 1, 3*(nexternal-nexternal_prod)
              call  ntuple(x(j),0d0,1d0,j,0)
           enddo

c           do j=1,nexternal_prod
c              write (*,*) (p(k,j), k=0,3)  
c           enddo

           call generate_momenta_conf(jac,x,itree,qmass,qwidth,pfull) 

           !do j=1,nexternal
           !   write (*,*) (pfull(k,j), k=0,3)  
           !enddo
           call SMATRIX(pfull,M_full)
c           write(*,*) 'M_full ', M_full
c           write(*,*) 'jac',jac

           weight=M_full*jac/M_prod
           if (weight.gt.maxweight) maxweight=weight
           !mean=mean+weight
           !variance=variance+weight**2
        enddo
        !mean=mean/real(nbpoints)   
        !variance=variance/real(nbpoints)-mean**2
        !std=sqrt(variance)
        write (*,*) maxweight   ! ,mean,std  
        call flush()
        goto 1
      endif


ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c   VIb. generate unweighted decay config                               c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc

       if (mode.eq.2) then
         notpass=.true.
         counter=0
         do while (notpass) 
           counter=counter+1
           jac=1d0
           ivar=0
           no_gen=.false.
           do i = 1, 3*(nexternal-nexternal_prod)+1
              call  ntuple(x(i),0d0,1d0,i,0)
           enddo

           call generate_momenta_conf(jac,x,itree,qmass,qwidth,pfull) 

           call SMATRIX(pfull,M_full)

           if (M_full*jac/M_prod.gt.x(3*(nexternal-nexternal_prod)+1)*maxweight) notpass=.false.
        enddo

        write(*,*) nexternal,  counter, maxBW, M_full*jac/M_prod
        do i=1,nexternal
           write (*,*) (pfull(j,i), j=0,3)  
        enddo

        call flush()
        goto 1
      endif

ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c   VIc. return M_full^2                                                c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc

       if (mode.eq.3) then

           jac=1d0
           ivar=0
           no_gen=.false.

           do i = 1, 3*(nexternal-nexternal_prod)+1
              call  ntuple(x(i),0d0,1d0,i,0)
           enddo

           call generate_momenta_conf(jac,x,itree,qmass,qwidth,pfull) 

           call SMATRIX(pfull,M_full)

           write(*,*) M_full

        call flush()
        goto 1
      endif

2     continue
      end

      subroutine get_config(iconfig)
      implicit none

C---  integer    n_max_cg
      INCLUDE "ngraphs.inc"     !how many diagrams 

c     argument
      integer iconfig

c     local
      integer i
      double precision cumulweight(0:n_max_cg),random

c     common
      DOUBLE PRECISION AMP2(n_max_cg)
      COMMON/TO_AMPS/  AMP2

      integer            mapconfig(0:N_MAX_CG), this_config
      common/to_mconfigs/mapconfig, this_config

      cumulweight(0)=0d0
      do i=1,mapconfig(0)
         cumulweight(i)=amp2(mapconfig(i))+cumulweight(i-1)
      enddo

      !do i=1,100
      call  ntuple(random,0d0,1d0,24,0)
      !enddo

      do i=1,mapconfig(0)
         cumulweight(i)=cumulweight(i)/cumulweight(mapconfig(0))
         !write(*,*) random
         !write(*,*) cumulweight(i-1)
         !write(*,*) cumulweight(i)
         if (random.ge.cumulweight(i-1).and.random.le.cumulweight(i)) then 
           iconfig=i
           return
         endif 
      enddo

      write(*,*) 'Unable to generate iconfig'

      end


      subroutine set_parameters(p,Ecollider)
      implicit none

      double precision ZERO
      parameter (ZERO=0D0)
      include 'nexternal_prod.inc'
c     argument
      double precision p(0:3, nexternal_prod), Ecollider

c     local 
      integer i, j
      double precision ptot(0:3)

      include 'nexternal.inc'
      include 'coupl.inc'
      INCLUDE "input.inc"
      !include 'run.inc'
       ! variables associate with the PS generation
       double precision totmassin, totmass
       double precision shat, sqrtshat, stot, y, m(-nexternal:nexternal)
       integer nbranch, ns_channel,nt_channel
       common /to_topo/
     & totmassin, totmass,shat, sqrtshat, stot,y, m,
     & nbranch, ns_channel,nt_channel

c Masses of particles. Should be filled in setcuts.f
      double precision pmass(nexternal)
      common /to_mass/pmass

      double precision dot
      external dot

      include "../parameters.inc"
      stot=Ecollider**2

      include 'pmass.inc'

      ! m(i) pmass(i) already refer to the full kinematics
      do i=1,nexternal
            m(i)=pmass(i)
      enddo

      do j = 0,3
        ptot(j)=p(j,1)+p(j,2)
      enddo
      shat=dot(ptot,ptot)
      sqrtshat=sqrt(shat)
c      write(*,*) shat
c      write(*,*) sqrtshat


c Make sure have enough mass for external particles
      totmassin=0d0
      do i=3-nincoming,2
         totmassin=totmassin+pmass(i)
      enddo
      totmass=0d0

      do i=3,nexternal 
         totmass=totmass+m(i)
      enddo
      if (stot .lt. max(totmass,totmassin)**2) then
         write (*,*) 'Fatal error #0 in one_tree:'/
     &         /'insufficient collider energy'
         stop
      endif

      end


      subroutine merge_itree(itree,qmass,qwidth,  p_ext)
      implicit none
      !include 'genps.inc'
      include 'coupl.inc'
      include 'nexternal_prod.inc'
      include 'nexternal.inc'
c
c     arguments
c
      integer itree(2,-nexternal:-1)   ! PS structure for the production
      double precision qmass(-nexternal:0),qwidth(-nexternal:0) 
      double precision p_ext(0:3,nexternal_prod)
c
c     local
c
      double precision normp
      ! info for the full process
      integer itree_full(2,-nexternal:-1),i,j
      double precision qmass_full(-nexternal:0),qwidth_full(-nexternal:0) 
      ! info for the decay part
      double precision idecay(2,-nexternal:-1), prmass(-nexternal:-1),prwidth(-nexternal:-1) 
      integer ns_channel_decay
      integer  map_external2res(nexternal) ! map (index in production) -> index in the full structure
      double precision p(0:3,-nexternal:nexternal)
 
      integer idB, id1
      double precision pa(0:3), pb(0:3), p1(0:3), p2(0:3),pboost(0:3)
      double precision pb_cms(0:3), p1_cms(0:3), p1_rot(0:3)

c     common
      ! variables to keep track of the vegas numbers for the production part
      logical keep_inv(-nexternal:-1),no_gen
      integer ivar
      double precision fixedinv(-nexternal:0)
      double precision phi_tchan(-nexternal:0),m2_tchan(-nexternal:0)
      double precision cosphi_schan(-nexternal:0), phi_schan(-nexternal:0)
      common /to_fixed_kin/keep_inv,no_gen, ivar, fixedinv,
     & phi_tchan,m2_tchan,cosphi_schan, phi_schan 

       ! variables associate with the PS generation
       double precision totmassin, totmass
       double precision shat, sqrtshat, stot, y, m(-nexternal:nexternal)
       integer nbranch, ns_channel,nt_channel
       common /to_topo/
     & totmassin, totmass,shat, sqrtshat, stot,y, m,
     & nbranch, ns_channel,nt_channel

      double precision phi
      external phi
      double precision dot
      external dot

      !include 'run.inc'
      include  'configs_decay.inc'

c Determine number of s- and t-channel branches, at this point it
c includes the s-channel p1+p2
c      write(*,*) (itree(i,-1), i=1,2)
c      write(*,*) qmass(-1)
c      write(*,*) qwidth(-1)

         nbranch=nexternal_prod -2
         ns_channel=1
         do while(itree(1,-ns_channel).ne.1 .and.
     &        itree(1,-ns_channel).ne.2 .and. ns_channel.lt.nbranch)
         !   m(-ns_channel)=0d0
            ns_channel=ns_channel+1
         enddo
         ns_channel=ns_channel - 1
         nt_channel=nbranch-ns_channel-1
c If no t-channles, ns_channels is one less, because we want to exclude
c the s-channel p1+p2
         if (nt_channel .eq. 0 .and. nincoming .eq. 2) then
            ns_channel=ns_channel-1
         endif
c Set one_body to true if it s a 2->1 process at the Born (i.e. 2->2 for the n+1-body)
         if((nexternal-nincoming).eq.1)then
            !one_body=.true.
            ns_channel=0
            nt_channel=0
         elseif((nexternal-nincoming).gt.1)then
            continue
            !one_body=.false.
         else
            write(*,*)'Error #1 in genps_madspin.f',nexternal,nincoming
            stop
         endif

c      write(*,*) 'ns_channel ',ns_channel 
c      write(*,*) 'nt_channel ',nt_channel 

      ! first fill the new itree for the the legs in the decay part
      do i=-(ns_channel_decay),-1       
         itree_full(1,i) = idecay(1,i)
         itree_full(2,i) = idecay(2,i)
         qmass_full(i)=prmass(i)
         qwidth_full(i)=prwidth(i)
         keep_inv(i)=.FALSE.
      enddo
 
c      write(*,*) (itree_full(i,-1), i=1,2)
c      write(*,*) (itree_full(i,-2), i=1,2)
c      write(*,*) (itree_full(i,-3), i=1,2)
c      write(*,*) (itree_full(i,-4), i=1,2)
c      write(*,*) qmass_full(-1)
c      write(*,*) qmass_full(-2)
c      write(*,*) qmass_full(-3)
c      write(*,*) qmass_full(-4)
c      write(*,*) qwidth_full(-1)
c      write(*,*) qwidth_full(-2)
c      write(*,*) qwidth_full(-3)
c      write(*,*) qwidth_full(-4)
  
      ! store the external momenta in the production event a
      ! new variable p that has the same labeling system as the new itree
      do i=1, nexternal_prod
          do j=0,3
              p(j,map_external2res(i)) = p_ext(j,i)
          enddo
      enddo

      ! fill the new itree with the kinematics associated with the production
      do i=-1,-(ns_channel+nt_channel)-1,-1
         if (itree(1,i).lt.0 ) then
            itree_full(1,i-ns_channel_decay) = itree(1,i)-ns_channel_decay
         else 
             itree_full(1,i-ns_channel_decay) = map_external2res(itree(1,i))
         endif 
         if (itree(2,i).lt.0 ) then
             itree_full(2,i-ns_channel_decay) = itree(2,i)-ns_channel_decay
         else 
             itree_full(2,i-ns_channel_decay) = map_external2res(itree(2,i))
         endif
         
         ! record the momentum of the intermediate leg         
         do j=0,3
             if (nt_channel.ne.0.and.i .lt.-ns_channel) then
             p(j,i-ns_channel_decay)=p(j,itree_full(1,i-ns_channel_decay))-p(j,itree_full(2,i-ns_channel_decay))
             else 
             p(j,i-ns_channel_decay)=p(j,itree_full(1,i-ns_channel_decay))+p(j,itree_full(2,i-ns_channel_decay))
             endif
         enddo
         
         keep_inv(i-ns_channel_decay)=.TRUE.
 
         if (i.ne.(-ns_channel-nt_channel-1)) then
           fixedinv(i-ns_channel_decay)=dot(p(0,i-ns_channel_decay),p(0,i-ns_channel_decay))
           qmass_full(i-ns_channel_decay)=qmass(i)
           qwidth_full(i-ns_channel_decay)=qwidth(i)
         endif
      enddo 



 
      !write(*,*) -ns_channel-nt_channel-1
      !write(*,*) map_external2res(itree(2,-ns_channel-nt_channel-1))
      !write(*,*) itree(1,-ns_channel-nt_channel-1)
      !write(*,*) itree(2,-ns_channel-nt_channel-1)
      !write(*,*) nbranch
      !write(*,*) nt_channel
 

c      write(*,*) (itree_full(i,-1), i=1,2)
c      write(*,*) (itree_full(i,-2), i=1,2)
c      write(*,*) (itree_full(i,-3), i=1,2)
c      write(*,*) (itree_full(i,-4), i=1,2)
c      write(*,*) (itree_full(i,-5), i=1,2)
c      !write(*,*) (itree_full(i,-6), i=1,2)
c      write(*,*) qmass_full(-1)
c      write(*,*) qmass_full(-2)
c      write(*,*) qmass_full(-3)
c      write(*,*) qmass_full(-4)
c      write(*,*) qmass_full(-5)
c      write(*,*) qwidth_full(-1)
c      write(*,*) qwidth_full(-2)
c      write(*,*) qwidth_full(-3)
c      write(*,*) qwidth_full(-4)
c      write(*,*) qwidth_full(-5)


      !overwrite the previous information
      nbranch=nexternal-2
      ns_channel= ns_channel+ns_channel_decay
c      write(*,*) 'ns_channel ',ns_channel 
c      write(*,*) 'nt_channel ',nt_channel 
      do i =-(ns_channel+nt_channel)-1,-1
         itree(1,i) =itree_full(1,i)
         itree(2,i) =itree_full(2,i)
         qmass(i)=qmass_full(i)
         qwidth(i)=qwidth_full(i)
      enddo

      ! extract the phi and m2 numbers for each t-channel branching
      do i=-(ns_channel+nt_channel),-ns_channel-1
          ! the t-branching process has the structure A+B > 1 + 2 
          ! with A and 1 the two daughters in itree
         idB=itree(1,i)
         id1=itree(2,i)      
          do j=0,3
             pa(j)=p(j,2)
             pb(j)=p(j,idB) 
             p1(j)=p(j,id1)
             p2(j)=pa(j)+ pb(j)-p1(j) 
          enddo    
             m2_tchan(i)=dot(p2,p2)
             if (m2_tchan(i).gt.0d0) then 
                 m2_tchan(i)=sqrt(m2_tchan(i))
             elseif (m2_tchan(i).gt.-1d-2) then ! sometimes negative because of numerical instabilities
                 m2_tchan(i)=0d0
             else
        write(*,*) 'Warning: m_2^2 is negative in t-channel branching '
             endif

         ! extract phi
         do j=0,3
            pboost(j) = pa(j)+pb(j)
            if (j .gt. 0) then
               pboost(j) = -pboost(j)
            endif
         enddo
c
c        go to  pa+pb cms system
c
         call boostx(pb,pboost,pb_cms)
         call boostx(p1,pboost,p1_cms)
c        rotate such that pb is aligned with z axis
         call invrot(p1_cms, pb_cms,p1_rot)
         phi_tchan(i)=phi(p1_rot)
      enddo

      do i=-ns_channel-1, -1
          if (keep_inv(i)) then
            if (nt_channel.ne.0.and.i.eq.(ns_channel+1)) cycle
            pboost(0)=p(0,i) 
            do j=1,3
               pboost(j)=-p(j,i)
            enddo
            call boostx(p(0,itree(1,i)),pboost,p1)
            normp=sqrt(p1(1)**2+p1(2)**2+p1(3)**2)
            cosphi_schan(i)=p1(3)/normp
            phi_schan(i)=phi(p1) 
         endif
      enddo
      end


      subroutine generate_momenta_conf(jac,x,itree,qmass,qwidth,p)
c
c
      implicit none
      !include 'genps.inc'
      include 'nexternal.inc'
      !include 'run.inc'
c arguments
      double precision jac,x(36),p(0:3,nexternal)
      integer itree(2,-nexternal:-1)
      double precision qmass(-nexternal:0),qwidth(-nexternal:0)
c common

      ! variables to keep track of the vegas numbers for the production part
      logical keep_inv(-nexternal:-1),no_gen
      integer ivar
      double precision fixedinv(-nexternal:0)
      double precision phi_tchan(-nexternal:0),m2_tchan(-nexternal:0)
      double precision cosphi_schan(-nexternal:0), phi_schan(-nexternal:0)
      common /to_fixed_kin/keep_inv,no_gen, ivar, fixedinv,
     & phi_tchan,m2_tchan,cosphi_schan, phi_schan 

c     
       ! variables associate with the PS generation
       double precision totmassin, totmass
       double precision shat, sqrtshat, stot, y, m(-nexternal:nexternal)
       integer nbranch, ns_channel,nt_channel
       common /to_topo/
     & totmassin, totmass,shat, sqrtshat, stot,y, m,
     & nbranch, ns_channel,nt_channel


c Masses of particles. Should be filled in setcuts.f
      double precision pmass(nexternal)
      common /to_mass/pmass

c local
      integer i,j,
     &     imother
      double precision pb(0:3,-nexternal:nexternal)
     &     ,S(-nexternal:nexternal)
     &     ,xjac,xpswgt
     &     ,pwgt,p_born_CHECK(0:3,nexternal)
      logical pass
c external
      double precision lambda
      external lambda
c parameters
      real*8 pi
      parameter (pi=3.1415926535897932d0)
      logical firsttime
      data firsttime/.true./
      double precision zero
      parameter (zero=0d0)
c Conflicting BW stuff
      integer cBW_level_max,cBW(-nexternal:-1),cBW_level(-nexternal:-1)
      double precision cBW_mass(-nexternal:-1,-1:1),
     &     cBW_width(-nexternal:-1,-1:1)
      common/c_conflictingBW/cBW_mass,cBW_width,cBW_level_max,cBW
     $     ,cBW_level

      pass=.true.

c
      xjac=1d0
      xpswgt=1d0


c     STEP 1: generate the initial momenta
      s(-nbranch)  = shat
      m(-nbranch)  = sqrtshat
      pb(0,-nbranch)= m(-nbranch)
      pb(1,-nbranch)= 0d0
      pb(2,-nbranch)= 0d0
      pb(3,-nbranch)= 0d0

      if(nincoming.eq.2) then
        call mom2cx(sqrtshat,m(1),m(2),1d0,0d0,pb(0,1),pb(0,2))
      else
         pb(0,1)=sqrtshat
         do i=1,2
            pb(0,1)=0d0
         enddo
      endif
c
c    STEP 2:  generate all the invariant masses of the s-channels
      call generate_inv_mass_sch(ns_channel,itree,m,sqrtshat
     &     ,totmass,qwidth,qmass,cBW,cBW_mass,cBW_width,s,x,xjac,pass)

      !write(*,*) 'jac s-chan ', xjac
      if (.not.pass) then
        jac=-1d0
        return
      endif


c If only s-channels, also set the p1+p2 s-channel
      if (nt_channel .eq. 0 .and. nincoming .eq. 2) then
         s(-nbranch+1)=s(-nbranch) 
         m(-nbranch+1)=m(-nbranch)       !Basic s-channel has s_hat 
         pb(0,-nbranch+1) = m(-nbranch+1)!and 0 momentum
         pb(1,-nbranch+1) = 0d0
         pb(2,-nbranch+1) = 0d0
         pb(3,-nbranch+1) = 0d0
      endif

c
c     STEP 3:  do the T-channel branchings
c
      if (nt_channel.ne.0) then
         call generate_t_channel_branchings(ns_channel,nbranch,itree,m,s
     &        ,x,pb,xjac,xpswgt,pass)
         if (.not.pass) then
             jac=-1d0
             return 
         endif
      endif
      !write(*,*) 'jac t-chan ', xjac
c
c     STEP 4: generate momentum for all intermediate and final states
c     being careful to calculate from more massive to less massive states
c     so the last states done are the final particle states.
c
      call fill_momenta(nbranch,nt_channel
     &     ,x,itree,m,s,pb,xjac,xpswgt,pass)
      if (.not.pass) then
         jac=-1d0
         return
      endif 
      !write(*,*) 'jac fill ', xjac

      do i = 1, nexternal
       do j = 0, 3
         p(j,i)=pb(j,i)
       enddo
      enddo


      jac=xjac*xpswgt

      return
      end


      subroutine fill_momenta(nbranch,nt_channel
     &     ,x,itree,m,s,pb,xjac0,xpswgt0,pass)
      implicit none
      real*8 pi
      parameter (pi=3.1415926535897932d0)
      !include 'genps.inc'
      include 'nexternal.inc'
      integer nbranch,nt_channel,ionebody
      double precision M(-nexternal:nexternal),x(36)
      double precision s(-nexternal:nexternal)
      double precision pb(0:3,-nexternal:nexternal)
      integer itree(2,-nexternal:-1)
      double precision xjac0,xpswgt0
      logical pass,one_body
c
      double precision one
      parameter (one=1d0)
      double precision costh,phi,xa2,xb2
      integer i,ix,j
      double precision lambda,dot
      external lambda,dot
      double precision vtiny
      parameter (vtiny=1d-12)

      ! variables to keep track of the vegas numbers for the production part
      logical keep_inv(-nexternal:-1),no_gen
      integer ivar
      double precision fixedinv(-nexternal:0)
      double precision phi_tchan(-nexternal:0),m2_tchan(-nexternal:0)
      double precision cosphi_schan(-nexternal:0), phi_schan(-nexternal:0)
      common /to_fixed_kin/keep_inv,no_gen, ivar, fixedinv,
     & phi_tchan,m2_tchan,cosphi_schan, phi_schan 

      pass=.true.

      do i = -nbranch+nt_channel+(nincoming-1),-1
         if (keep_inv(i).or.no_gen) then 
           costh=cosphi_schan(i)
           phi=phi_schan(i)
         else    
           ivar=ivar+1
           costh= 2d0*x(ivar)-1d0
           ivar=ivar+1
           phi  = 2d0*pi*x(ivar)
           phi_schan(i)=phi
           cosphi_schan(i)=costh
           xjac0 = xjac0 * 4d0*pi
         endif
         xa2 = m(itree(1,i))*m(itree(1,i))/s(i)
         xb2 = m(itree(2,i))*m(itree(2,i))/s(i)
         if (m(itree(1,i))+m(itree(2,i)) .ge. m(i)) then
            xjac0=-8
            pass=.false.
            return
         endif

c         write(*,*) i
c         write(*,*) sqrt(s(i))
c         write(*,*) m(itree(1,i))
c         write(*,*) m(itree(2,i))
c         write(*,*)  xa2, xb2

         if (.not.keep_inv(i)) then 
           xpswgt0 = xpswgt0*.5D0*PI*SQRT(LAMBDA(ONE,XA2,XB2))/(4.D0*PI)
         endif
c         write(*,*)  xpswgt0

         call mom2cx(m(i),m(itree(1,i)),m(itree(2,i)),costh,phi,
     &        pb(0,itree(1,i)),pb(0,itree(2,i)))
c         write(*,*) 'i ', i
c         write(*,*) 'costh, phi ', costh,phi
c         write(*,*) 'm init ', m(i)
c         write(*,*) (pb(j,itree(1,i)), j=0,3)
c         write(*,*) (pb(j,itree(2,i)), j=0,3)
c If there is an extremely large boost needed here, skip the phase-space point
c because of numerical stabilities.
         if (dsqrt(abs(dot(pb(0,i),pb(0,i))))/pb(0,i) 
     &        .lt.vtiny) then
            xjac0=-81
            pass=.false.
            return
         else
            call boostx(pb(0,itree(1,i)),pb(0,i),pb(0,itree(1,i)))
            call boostx(pb(0,itree(2,i)),pb(0,i),pb(0,itree(2,i)))
         endif
      enddo
c
c
c Special phase-space fix for the one_body
c      if (one_body) then
c Factor due to the delta function in dphi_1
c         xpswgt0=pi/m(ionebody)
c Kajantie s normalization of phase space (compensated below in flux)
c         xpswgt0=xpswgt0/(2*pi)
c         do i=0,3
c            pb(i,3) = pb(i,1)+pb(i,2)
c         enddo
c      endif
      return
      end


      subroutine generate_inv_mass_sch(ns_channel,itree,m,sqrtshat
     &     ,totmass,qwidth,qmass,cBW,cBW_mass,cBW_width,s,x,xjac0,pass)
      implicit none
      real*8 pi
      parameter (pi=3.1415926535897932d0)
      !include 'genps.inc'
      include 'nexternal.inc'

      double precision  totmass,BWshift
      double precision sqrtshat,  m(-nexternal:nexternal)
      integer  ns_channel
      double precision qmass(-nexternal:0),qwidth(-nexternal:0)
      double precision x(36)
      double precision s(-nexternal:nexternal)
      double precision xjac0
      integer itree(2,-nexternal:-1)
      integer i,j
      double precision smin,smax,xm02,bwmdpl,bwmdmn,bwfmpl,bwfmmn,bwdelf
     &     ,totalmass
      double precision xbwmass3,bwfunc
      external xbwmass3,bwfunc
      logical pass
      integer cBW_level_max,cBW(-nexternal:-1),cBW_level(-nexternal:-1)
      double precision cBW_mass(-nexternal:-1,-1:1),
     &     cBW_width(-nexternal:-1,-1:1)
      double precision b(-1:1),x0

      ! variables to keep track of the vegas numbers for the production part
      logical keep_inv(-nexternal:-1),no_gen
      integer ivar
      double precision fixedinv(-nexternal:0)
      double precision phi_tchan(-nexternal:0),m2_tchan(-nexternal:0)
      double precision cosphi_schan(-nexternal:0), phi_schan(-nexternal:0)
      common /to_fixed_kin/keep_inv,no_gen, ivar, fixedinv,
     & phi_tchan,m2_tchan,cosphi_schan, phi_schan 

       double precision BWcut, maxBW
       common /to_BWcut/BWcut, maxBW

      pass=.true.
      totalmass=totmass
      do i = -1,-ns_channel,-1
c Generate invariant masses for all s-channel branchings of the Born
         if (keep_inv(i).or.no_gen) then 
            s(i)=fixedinv(i)
            goto 503
         endif
         smin = (m(itree(1,i))+m(itree(2,i)))**2
         smax = (sqrtshat-totalmass+sqrt(smin))**2
         if(smax.lt.smin.or.smax.lt.0.d0.or.smin.lt.0.d0)then
            write(*,*)'Error #13 in genps_madspin.f'
            write(*,*)smin,smax,i
            stop
         endif
         ivar=ivar+1
c Choose the appropriate s given our constraints smin,smax
         if(qwidth(i).ne.0.d0)then
c Breit Wigner
            if (cBW(i).eq.1 .and.
     &          cBW_width(i,1).gt.0d0 .and. cBW_width(i,-1).gt.0d0) then
c     conflicting BW on both sides
               do j=-1,1,2
                  b(j)=(cBW_mass(i,j)-qmass(i))/
     &                 (qwidth(i)+cBW_width(i,j))
                  b(j)=qmass(i)+b(j)*qwidth(i)
                  b(j)=b(j)**2
               enddo
               if (x(ivar).lt.1d0/3d0) then
                  x0=3d0*x(ivar)
                  s(i)=(b(-1)-smin)*x0+smin
                  xjac0=3d0*xjac0*(b(-1)-smin)
               elseif (x(ivar).gt.1d0/3d0 .and. x(ivar).lt.2d0/3d0) then
                  x0=3d0*x(ivar)-1d0
                  xm02=qmass(i)**2
                  bwmdpl=b(1)-xm02
                  bwmdmn=xm02-b(-1)
                  bwfmpl=atan(bwmdpl/(qmass(i)*qwidth(i)))
                  bwfmmn=atan(bwmdmn/(qmass(i)*qwidth(i)))
                  bwdelf=(bwfmpl+bwfmmn)/pi
                  s(i)=xbwmass3(x0,xm02,qwidth(i),bwdelf
     &                 ,bwfmmn)
                  xjac0=3d0*xjac0*bwdelf/bwfunc(s(i),xm02,qwidth(i))
               else
                  x0=3d0*x(ivar)-2d0
                  s(i)=(smax-b(1))*x0+b(1)
                  xjac0=3d0*xjac0*(smax-b(1))
               endif
            elseif (cBW(i).eq.1.and.cBW_width(i,1).gt.0d0) then
c     conflicting BW with alternative mass larger
               b(1)=(cBW_mass(i,1)-qmass(i))/
     &              (qwidth(i)+cBW_width(i,1))
               b(1)=qmass(i)+b(1)*qwidth(i)
               b(1)=b(1)**2
               if (x(ivar).lt.0.5d0) then
                  x0=2d0*x(ivar)
                  xm02=qmass(i)**2
                  bwmdpl=b(1)-xm02
                  bwmdmn=xm02-smin
                  bwfmpl=atan(bwmdpl/(qmass(i)*qwidth(i)))
                  bwfmmn=atan(bwmdmn/(qmass(i)*qwidth(i)))
                  bwdelf=(bwfmpl+bwfmmn)/pi
                  s(i)=xbwmass3(x0,xm02,qwidth(i),bwdelf
     &                 ,bwfmmn)
                  xjac0=2d0*xjac0*bwdelf/bwfunc(s(i),xm02,qwidth(i))
               else
                  x0=2d0*x(ivar)-1d0
                  s(i)=(smax-b(1))*x0+b(1)
                  xjac0=2d0*xjac0*(smax-b(1))
               endif
            elseif (cBW(i).eq.1.and.cBW_width(i,-1).gt.0d0) then
c     conflicting BW with alternative mass smaller
               b(-1)=(cBW_mass(i,-1)-qmass(i))/
     &              (qwidth(i)+cBW_width(i,-1)) ! b(-1) is negative here
               b(-1)=qmass(i)+b(-1)*qwidth(i)
               b(-1)=b(-1)**2
               if (x(ivar).lt.0.5d0) then
                  x0=2d0*x(ivar)
                  s(i)=(b(-1)-smin)*x0+smin
                  xjac0=2d0*xjac0*(b(-1)-smin)
               else
                  x0=2d0*x(ivar)-1d0
                  xm02=qmass(i)**2
                  bwmdpl=smax-xm02
                  bwmdmn=xm02-b(-1)
                  bwfmpl=atan(bwmdpl/(qmass(i)*qwidth(i)))
                  bwfmmn=atan(bwmdmn/(qmass(i)*qwidth(i)))
                  bwdelf=(bwfmpl+bwfmmn)/pi
                  s(i)=xbwmass3(x0,xm02,qwidth(i),bwdelf
     &                 ,bwfmmn)
                  xjac0=2d0*xjac0*bwdelf/bwfunc(s(i),xm02,qwidth(i))
               endif
            else
c     normal BW
               ! P.A.: introduce the BWcutoff here
               smax=min(smax,(qmass(i)+BWcut*qwidth(i))**2 )
               smin=max(smin,(qmass(i)-BWcut*qwidth(i))**2 )

               xm02=qmass(i)**2
               bwmdpl=smax-xm02
               bwmdmn=xm02-smin
               bwfmpl=atan(bwmdpl/(qmass(i)*qwidth(i)))
               bwfmmn=atan(bwmdmn/(qmass(i)*qwidth(i)))
               bwdelf=(bwfmpl+bwfmmn)/pi
               s(i)=xbwmass3(x(ivar),xm02,qwidth(i),bwdelf
     &              ,bwfmmn)
               xjac0=xjac0*bwdelf/bwfunc(s(i),xm02,qwidth(i))

            endif
         else
c not a Breit Wigner
            s(i) = (smax-smin)*x(ivar)+smin
            xjac0 = xjac0*(smax-smin)
         endif

c If numerical inaccuracy, quit loop
         if (xjac0 .lt. 0d0) then
            xjac0 = -6
            pass=.false.
            return
         endif
         if (s(i) .lt. smin) then
            xjac0=-5
            pass=.false.
            return
         endif
         fixedinv(i)=s(i)
c
c     fill masses, update totalmass
c
503      continue
         m(i) = sqrt(s(i))
         BWshift=abs(m(i)-qmass(i))/qwidth(i)
         if (BWshift.gt.maxBW) maxBW=BWshift
         totalmass=totalmass+m(i)-
     &        m(itree(1,i))-m(itree(2,i))
         if ( totalmass.gt.sqrtshat )then
            xjac0 = -4
            pass=.false.
            return
         endif
      enddo
      return
      end



      subroutine generate_t_channel_branchings(ns_channel,nbranch,itree
     &     ,m,s,x,pb,xjac0,xpswgt0,pass)
c First we need to determine the energy of the remaining particles this
c is essentially in place of the cos(theta) degree of freedom we have
c with the s channel decay sequence
      implicit none
      real*8 pi
      parameter (pi=3.1415926535897932d0)
      !include 'genps.inc'
      include 'nexternal.inc'
      double precision xjac0,xpswgt0
      double precision M(-nexternal:nexternal),x(36)
      double precision s(-nexternal:nexternal)
      double precision pb(0:3,-nexternal:nexternal)
      integer itree(2,-nexternal:-1)
      integer ns_channel,nbranch
      logical pass
c
      double precision totalmass,smin,smax,s1,ma2,mbq,m12,mnq,tmin,tmax
     &     ,t,tmax_temp,phi
      integer i,ibranch
      double precision lambda,dot
      external lambda,dot

      ! variables to keep track of the vegas numbers for the production part
      logical keep_inv(-nexternal:-1),no_gen
      integer ivar
      double precision fixedinv(-nexternal:0)
      double precision phi_tchan(-nexternal:0),m2_tchan(-nexternal:0)
      double precision cosphi_schan(-nexternal:0), phi_schan(-nexternal:0)
      common /to_fixed_kin/keep_inv,no_gen, ivar, fixedinv,
     & phi_tchan,m2_tchan,cosphi_schan, phi_schan 

c 
      pass=.true.
      totalmass=0d0
      do ibranch = -ns_channel-1,-nbranch,-1
         totalmass=totalmass+m(itree(2,ibranch))
      enddo
      m(-ns_channel-1) = dsqrt(S(-nbranch))
c     
c Choose invariant masses of the pseudoparticles obtained by taking together
c all final-state particles or pseudoparticles found from the current 
c t-channel propagator down to the initial-state particle found at the end
c of the t-channel line.
      do ibranch = -ns_channel-1,-nbranch+2,-1
         totalmass=totalmass-m(itree(2,ibranch))  
         smin = totalmass**2                    
         smax = (m(ibranch) - m(itree(2,ibranch)))**2
         if (smin .gt. smax) then
            xjac0=-3d0
            pass=.false.
            return
         endif
         if (keep_inv(ibranch).or.no_gen) then
            m(ibranch-1)=m2_tchan(ibranch)
         else
            ivar=ivar+1
            m(ibranch-1)=dsqrt((smax-smin)*
     &        x(ivar))
            m2_tchan(ibranch)=m(ibranch-1)
            xjac0 = xjac0*(smax-smin)
         endif
         if (m(ibranch-1)**2.lt.smin.or.m(ibranch-1)**2.gt.smax
     &        .or.m(ibranch-1).ne.m(ibranch-1)) then
            xjac0=-1d0
            pass=.false.
            return
         endif
      enddo
c     
c Set m(-nbranch) equal to the mass of the particle or pseudoparticle P
c attached to the vertex (P,t,p2), with t being the last t-channel propagator
c in the t-channel line, and p2 the incoming particle opposite to that from
c which the t-channel line starts
      m(-nbranch) = m(itree(2,-nbranch))
c
c     Now perform the t-channel decay sequence. Most of this comes from: 
c     Particle Kinematics Chapter 6 section 3 page 166
c
c     From here, on we can just pretend this is a 2->2 scattering with
c     Pa                    + Pb     -> P1          + P2
c     p(0,itree(ibranch,1)) + p(0,2) -> p(0,ibranch)+ p(0,itree(ibranch,2))
c     M(ibranch) is the total mass available (Pa+Pb)^2
c     M(ibranch-1) is the mass of P2  (all the remaining particles)

      do ibranch=-ns_channel-1,-nbranch+1,-1
         s1  = m(ibranch)**2    !Total mass available
         ma2 = m(2)**2
         mbq = dot(pb(0,itree(1,ibranch)),pb(0,itree(1,ibranch)))
         m12 = m(itree(2,ibranch))**2
         mnq = m(ibranch-1)**2
         call yminmax(s1,t,m12,ma2,mbq,mnq,tmin,tmax)
         tmax_temp = tmax
         if (keep_inv(ibranch).or.no_gen) then
             t = fixedinv(ibranch) 
         else 
             ivar=ivar+1
             t=(tmax_temp-tmin)*x(ivar)+tmin
             fixedinv(ibranch)=t 
             xjac0=xjac0*(tmax_temp-tmin)
         endif

         if (t .lt. tmin .or. t .gt. tmax) then
            xjac0=-3d0
            pass=.false.
            return
         endif
         if (keep_inv(ibranch).or.no_gen) then
            phi=phi_tchan(ibranch)
         else
            ivar=ivar+1
            phi = 2d0*pi*x(ivar)
            phi_tchan(ibranch)=phi
            xjac0 = xjac0*2d0*pi
         endif

c Finally generate the momentum. The call is of the form
c pa+pb -> p1+ p2; t=(pa-p1)**2;   pr = pa-p1
c gentcms(pa,pb,t,phi,m1,m2,p1,pr) 
         
         call gentcms(pb(0,itree(1,ibranch)),pb(0,2),t,phi,
     &        m(itree(2,ibranch)),m(ibranch-1),pb(0,itree(2,ibranch)),
     &        pb(0,ibranch),xjac0)
c
        if (xjac0 .lt. 0d0) then
            write(*,*) 'Failed gentcms',ibranch,xjac0
            pass=.false.
            return
         endif
         if (.not.keep_inv(ibranch)) then
         xpswgt0 = xpswgt0/(4d0*dsqrt(lambda(s1,ma2,mbq)))
         endif
      enddo
c We need to get the momentum of the last external particle.  This
c should just be the sum of p(0,2) and the remaining momentum from our
c last t channel 2->2
      do i=0,3
         pb(i,itree(2,-nbranch)) = pb(i,-nbranch+1)+pb(i,2)
      enddo
      return
      end

      subroutine gentcms(pa,pb,t,phi,m1,m2,p1,pr,jac)
c*************************************************************************
c     Generates 4 momentum for particle 1, and remainder pr
c     given the values t, and phi
c     Assuming incoming particles with momenta pa, pb
c     And outgoing particles with mass m1,m2
c     s = (pa+pb)^2  t=(pa-p1)^2
c*************************************************************************
      implicit none
c
c     Arguments
c
      double precision t,phi,m1,m2               !inputs
      double precision pa(0:3),pb(0:3),jac
      double precision p1(0:3),pr(0:3)           !outputs
c
c     local
c
      double precision ptot(0:3),E_acms,p_acms,pa_cms(0:3)
      double precision esum,ed,pp,md2,ma2,pt,ptotm(0:3)
      integer i
c
c     External
c
      double precision dot
      external dot
c-----
c  Begin Code
c-----
      do i=0,3
         ptot(i)  = pa(i)+pb(i)
         if (i .gt. 0) then
            ptotm(i) = -ptot(i)
         else
            ptotm(i) = ptot(i)
         endif
      enddo
      ma2 = dot(pa,pa)
c
c     determine magnitude of p1 in cms frame (from dhelas routine mom2cx)
c
      ESUM = sqrt(max(0d0,dot(ptot,ptot)))
      if (esum .eq. 0d0) then
         jac=-8d0             !Failed esum must be > 0
         return
      endif
      MD2=(M1-M2)*(M1+M2)
      ED=MD2/ESUM
      IF (M1*M2.EQ.0.) THEN
         PP=(ESUM-ABS(ED))*0.5d0
      ELSE
         PP=(MD2/ESUM)**2-2.0d0*(M1**2+M2**2)+ESUM**2
         if (pp .gt. 0) then
            PP=SQRT(pp)*0.5d0
         else
            write(*,*) 'Warning #12 in genps_madspin.f',pp
            jac=-1
            return
         endif
      ENDIF
c
c     Energy of pa in pa+pb cms system
c
      call boostx(pa,ptotm,pa_cms)
      E_acms = pa_cms(0)
      p_acms = dsqrt(pa_cms(1)**2+pa_cms(2)**2+pa_cms(3)**2)
c
      p1(0) = MAX((ESUM+ED)*0.5d0,0.d0)
      p1(3) = -(m1*m1+ma2-t-2d0*p1(0)*E_acms)/(2d0*p_acms)
      pt = dsqrt(max(pp*pp-p1(3)*p1(3),0d0))
      p1(1) = pt*cos(phi)
      p1(2) = pt*sin(phi)
c
      call rotxxx(p1,pa_cms,p1)          !Rotate back to pa_cms frame
      call boostx(p1,ptot,p1)            !boost back to lab fram
      do i=0,3
         pr(i)=pa(i)-p1(i)               !Return remainder of momentum
      enddo
      end




      function bwfunc(s,xm02,gah)
c Returns the Breit Wigner function, normalized in such a way that
c its integral in the range (-inf,inf) is one
      implicit none
      real*8 bwfunc,s,xm02,gah
      real*8 pi,xm0
      parameter (pi=3.1415926535897932d0)
c
      xm0=sqrt(xm02)
      bwfunc=xm0*gah/(pi*((s-xm02)**2+xm02*gah**2))
      return
      end


      SUBROUTINE YMINMAX(X,Y,Z,U,V,W,YMIN,YMAX)
C**************************************************************************
C     This is the G function from Particle Kinematics by
C     E. Byckling and K. Kajantie, Chapter 4 p. 91 eqs 5.28
C     It is used to determine physical limits for Y based on inputs
C**************************************************************************
      implicit none
c
c     Constant
c
      double precision tiny
      parameter       (tiny=1d-199)
c
c     Arguments
c
      Double precision x,y,z,u,v,w              !inputs  y is dummy
      Double precision ymin,ymax                !output
c
c     Local
c
      double precision y1,y2,yr,ysqr
c     
c     External
c
      double precision lambda
c-----
c  Begin Code
c-----
      ysqr = lambda(x,u,v)*lambda(x,w,z)
      if (ysqr .ge. 0d0) then
         yr = dsqrt(ysqr)
      else
         print*,'Error in yminymax sqrt(-x)',lambda(x,u,v),lambda(x,w,z)
         yr=0d0
      endif
      y1 = u+w -.5d0* ((x+u-v)*(x+w-z) - yr)/(x+tiny)
      y2 = u+w -.5d0* ((x+u-v)*(x+w-z) + yr)/(x+tiny)
      ymin = min(y1,y2)
      ymax = max(y1,y2)
      end


      function xbwmass3(t,xm02,ga,bwdelf,bwfmmn)
c Returns the boson mass squared, given 0<t<1, the nominal mass (xm0),
c and the mass range (implicit in bwdelf and bwfmmn). This function
c is the inverse of F(M^2), where
c   F(M^2)=\int_{xmlow2}^{M^2} ds BW(sqrt(s),M0,Ga)
c   BW(M,M0,Ga)=M0 Ga/pi 1/((M^2-M0^2)^2+M0^2 Ga^2
c and therefore eats up the Breit-Wigner when changing integration 
c variable M^2 --> t
      implicit none
      real*8 xbwmass3,t,xm02,ga,bwdelf,bwfmmn
      real*8 pi,xm0
      parameter (pi=3.1415926535897932d0)
c
      xm0=sqrt(xm02)
      xbwmass3=xm02+xm0*ga*tan(pi*bwdelf*t-bwfmmn)
      return
      end


      subroutine invrot(p,q, pp)
        ! inverse of the "rot" operation
        ! q is the four momentum that is aligned with z in the new frame 
        ! p is the four momentum to be rotated
        ! pp is rotated four momentum p 

        ! arguments
        double precision pp(0:3), p(0:3), q(0:3)
        ! local
        double precision qt2, qt, qq

        pp(0)=p(0)
        qt2 = (q(1))**2 + (q(2))**2

        if(qt2.eq.0.0d0) then
            if ( q(3).gt.0d0 ) then
                pp(1) = p(1)
                pp(2) = p(2)
                pp(3) = p(3)
            else
                pp(1) = -p(1)
                pp(2) = -p(2)
                pp(3) = -p(3)
            endif
        else
            qq = sqrt(qt2+q(3)**2)
            qt=sqrt(qt2)
            pp(2)=-q(2)/qt*p(1)+q(1)/qt*p(2)
            if (q(3).eq.0d0) then
                pp(1)=-qq/qt*p(3)
                if (q(2).ne.0d0) then
                    pp(3)=(p(2)-q(2)*q(3)/qq/qt-q(1)/qt*pp(2))*qq/q(2)
                else
                    pp(3)=(p(1)-q(1)*q(3)/qq/qt*pp(1)+q(2)/qt*pp(2))*qq/q(1)
                endif
            else
                if (q(2).ne.0d0) then
                    pp(3)=(qt**2*p(2)+q(2)*q(3)*p(3)-q(1)*qt*pp(2))/qq/q(2)
                else
                    pp(3)=(q(1)*p(1)+q(3)*p(3))/qq
                endif
                pp(1)=(-p(3)+q(3)/qq*pp(3))*qq/qt
            endif
        endif

        return
        end



      DOUBLE PRECISION  FUNCTION phi(p)
c************************************************************************
c     MODIF 16/11/06 : this subroutine defines phi angle
c                      phi is defined from 0 to 2 pi
c************************************************************************
      IMPLICIT NONE
c
c     Arguments
c
      double precision  p(0:3)
c
c     Parameter
c

      double precision pi,zero
      parameter (pi=3.141592654d0,zero=0d0)
c-----
c  Begin Code
c-----
c 
      if(p(1).gt.zero) then
      phi=datan(p(2)/p(1))
      else if(p(1).lt.zero) then
      phi=datan(p(2)/p(1))+pi
      else if(p(2).GE.zero) then !remind that p(1)=0
      phi=pi/2d0
      else if(p(2).lt.zero) then !remind that p(1)=0
      phi=-pi/2d0
      endif
      if(phi.lt.zero) phi=phi+2*pi
      return
      end

      double precision function dot(p1,p2)
C****************************************************************************
C     4-Vector Dot product
C****************************************************************************
      implicit none
      double precision p1(0:3),p2(0:3)
      dot=p1(0)*p2(0)-p1(1)*p2(1)-p1(2)*p2(2)-p1(3)*p2(3)

      if(dabs(dot).lt.1d-6)then ! solve numerical problem 
         dot=0d0
      endif

      end

      DOUBLE PRECISION FUNCTION LAMBDA(S,MA2,MB2)
      IMPLICIT NONE
C****************************************************************************
C     THIS IS THE LAMBDA FUNCTION FROM VERNONS BOOK COLLIDER PHYSICS P 662
C     MA2 AND MB2 ARE THE MASS SQUARED OF THE FINAL STATE PARTICLES
C     2-D PHASE SPACE = .5*PI*SQRT(1.,MA2/S^2,MB2/S^2)*(D(OMEGA)/4PI)
C****************************************************************************
      DOUBLE PRECISION MA2,MB2,S,tiny,tmp,rat
      parameter (tiny=1.d-8)
c
      tmp=S**2+MA2**2+MB2**2-2d0*S*MA2-2d0*MA2*MB2-2d0*S*MB2
      if(tmp.le.0.d0)then
        if(ma2.lt.0.d0.or.mb2.lt.0.d0)then
          write(6,*)'Error #1 in function Lambda:',s,ma2,mb2
          stop
        endif
        rat=1-(sqrt(ma2)+sqrt(mb2))/s
        if(rat.gt.-tiny)then
          tmp=0.d0
        else
          write(6,*)'Error #2 in function Lambda:',s,ma2,mb2
        endif
      endif
      LAMBDA=tmp
      RETURN
      END


