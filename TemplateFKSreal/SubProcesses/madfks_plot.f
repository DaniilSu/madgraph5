c
c
c Plotting routines
c
c
      subroutine initplot
      implicit none
c Book histograms in this routine. Use mbook or bookup. The entries
c of these routines are real*8
      double precision emax,ebin,etamin,etamax,etabin
      integer i,kk
      include 'run.inc'
      character*5 cc(2)
      data cc/' NLO ',' Born'/
c
      emax=dsqrt(ebeam(1)*ebeam(2))
      ebin=emax/50.d0
      etamin=-5.d0
      etamax=5.d0
      etabin=0.2d0
c resets histograms
      call inihist
c
      do i=1,2
        kk=(i-1)*50
        call bookup(kk+1,'total rate'//cc(i),1.0d0,0.5d0,5.5d0)
        call bookup(kk+2,'e+e- pair rapidity'//cc(i),0.5d0,-5d0,5d0)
        call bookup(kk+3,'e+e- invariant mass'//cc(i), 10d0, 0d0, 300d0)
      enddo
      return
      end


      subroutine topout
      implicit none
      character*14 ytit
      logical usexinteg,mint
      common/cusexinteg/usexinteg,mint
      integer itmax,ncall
      common/citmax/itmax,ncall
      real*8 xnorm1,xnorm2
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt
      integer i,kk
c
      if (unwgt) then
         ytit='events per bin'
      else
         ytit='sigma per bin '
      endif
      xnorm1=1.d0/float(itmax)
      xnorm2=1.d0/float(ncall*itmax)
      do i=1,500
        if(usexinteg.and..not.mint) then
           call mopera(i,'+',i,i,xnorm1,0.d0)
        elseif(mint) then
           call mopera(i,'+',i,i,xnorm2,0.d0)
        endif
        call mfinal(i)
      enddo
      do i=1,2
        kk=(i-1)*50
        call multitop(kk+1,3,2,'total rate',ytit,'LIN')
        call multitop(kk+2,3,2,'e+e- pair rapidity',ytit,'LOG')
        call multitop(kk+3,3,2,'e+e- invariant mass',ytit,'LOG')
c$$$        call mtop(kk+1,'total rate',ytit,'LIN')
      enddo
      return                
      end


      subroutine outfun(pp,ybst_til_tolab,www,itype)
C
C *WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING*
C
C In MadFKS, the momenta PP given in input to this function are in the
C reduced parton c.m. frame. If need be, boost them to the lab frame.
C The rapidity of this boost is
C
C       YBST_TIL_TOLAB
C
C also given in input
C
C This is the rapidity that enters in the arguments of the sinh() and
C cosh() of the boost, in such a way that
C       ylab = ycm - ybst_til_tolab
C where ylab is the rapidity in the lab frame and ycm the rapidity
C in the center-of-momentum frame.
C
C *WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING*
      implicit none
      include 'nexternal.inc'
      real*8 pp(0:3,nexternal),ybst_til_tolab,www
      integer itype
      real*8 var
      real*8 ppevs(0:3,nexternal)
      double precision djet,ecut,ycut
      double precision ppcl(4,nexternal),y(nexternal)
      double precision pjet(4,nexternal)
      double precision cthjet(nexternal)
      integer nn,njet,nsub,jet(nexternal)
      real*8 emax,getcth,cpar,dpar,thrust,dot,shat, getrapidity
      integer i,j,kk,imax

      LOGICAL  IS_A_J(NEXTERNAL),IS_A_L(NEXTERNAL)
      LOGICAL  IS_A_B(NEXTERNAL),IS_A_A(NEXTERNAL)
      LOGICAL  IS_A_NU(NEXTERNAL),IS_HEAVY(NEXTERNAL)
      COMMON /TO_SPECISA/IS_A_J,IS_A_A,IS_A_L,IS_A_B,IS_A_NU,IS_HEAVY
c masses
      double precision pmass(nexternal)
      common/to_mass/pmass
      real *8 pplab(0:3, nexternal)
      double precision shybst, chybst, chybstmo
      real*8 xd(1:3)
      data (xd(i), i=1,3) /0,0,1/
      real*8 yz, pz(0:3), mz
c
      if(itype.eq.11.or.itype.eq.12)then
        kk=0
      elseif(itype.eq.20)then
        kk=50
      else
        write(*,*)'Error in outfun: unknown itype',itype
        stop
      endif
c
      chybst=cosh(ybst_til_tolab)
      shybst=sinh(ybst_til_tolab)
      chybstmo= chybst-1.d0
      do i=3,nexternal
      call boostwdir2(chybst, shybst, chybstmo,xd,pp(0,i), pplab(0,i))
      enddo
      do i=0,3
        pz(i)=pplab(i,3)+pplab(i,4)
      enddo

      mz = sqrt(dot(pz,pz))
      yz=getrapidity(pz(0), pz(3))




      shat=2d0*dot(pp(0,1),pp(0,2))

      var=1.d0
      call mfill(kk+1,var,www)
      call mfill(kk+2,yz,www)
      call mfill(kk+3,mz,www)
 999  return      
      end



            function getrapidity(en,pl)
            implicit none
            real*8 getrapidity,en,pl,tiny,xplus,xminus,y
            parameter (tiny=1.d-8)
            xplus=en+pl
            xminus=en-pl
            if(xplus.gt.tiny.and.xminus.gt.tiny)then
            if( (xplus/xminus).gt.tiny.and.(xminus/xplus).gt.tiny)then
              y=0.5d0*log( xplus/xminus  )
             else
             y=sign(1.d0,pl)*1.d8
             endif
            else 
            y=sign(1.d0,pl)*1.d8
             endif
             getrapidity=y
             return
             end

