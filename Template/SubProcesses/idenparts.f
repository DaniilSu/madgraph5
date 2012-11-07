      subroutine idenparts(iden_part,itree,sprop,forcebw)
c     Keep track of identical particles to map radiation processes better. 
c     Only view the outermost identical particle as a BW, 
c     unless it is a required BW.
c
c     Constants
c
      include 'genps.inc'
      include 'maxconfigs.inc'
      include 'maxamps.inc'
      include 'nexternal.inc'
c
c     Arguments
c
      integer iden_part(-max_branch:-1)
      integer itree(2,-max_branch:-1),iconfig
      integer sprop(maxsproc,-max_branch:-1)  ! Propagator id
      integer forcebw(-max_branch:-1) ! Forced BW, for identical particle conflicts
c
c     local
c
      integer i,j,it
      double precision prwidth(-max_branch:-1,lmaxconfigs)  !Propagator width
      double precision prmass(-max_branch:-1,lmaxconfigs)   !Propagator mass
      double precision pow(-max_branch:-1,lmaxconfigs)    !Not used, in props.inc
      integer idup(nexternal,maxproc,maxsproc)
      integer mothup(2,nexternal)
      integer icolup(2,nexternal,maxflow,maxsproc)
      include 'leshouche.inc'
      integer ipdg(-nexternal+1:nexternal)
c
c     Global
c
      include 'coupl.inc'                     !Mass and width info
      double precision stot
      common/to_stot/stot

      do i=1,nexternal
         ipdg(i) = idup(i,1,1)
      enddo
      do i=1,nexternal-1
         iden_part(-i)=0
      enddo

      i=1
      do while (i .lt. nexternal-2 .and. itree(1,-i) .ne. 1)
         ipdg(-i)=sprop(1,-i)
         if (prwidth(-i,iconfig) .gt. 0d0) then
            if(ipdg(-i).eq.ipdg(itree(1,-i)).and.itree(1,-i).gt.0.or.
     $         ipdg(-i).eq.ipdg(itree(2,-i)).and.itree(2,-i).gt.0) then
               iden_part(-i) = ipdg(-i)
            else if(ipdg(-i).eq.ipdg(itree(1,-i)).and.
     $              iden_part(itree(1,-i)).ne.0.or.
     $         ipdg(-i).eq.ipdg(itree(2,-i)).and.
     $              iden_part(itree(2,-i)).ne.0) then
               iden_part(-i) = ipdg(-i)
            endif
         endif
         i=i+1
      enddo
      end
