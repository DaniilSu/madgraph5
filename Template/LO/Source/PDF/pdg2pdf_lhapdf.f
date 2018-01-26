 1    double precision function pdg2pdf(ih,ipdg,beamid,x,xmu)
c***************************************************************************
c     Based on pdf.f, wrapper for calling the pdf of MCFM
c***************************************************************************
      implicit none
c
c     Arguments
c
      DOUBLE  PRECISION x,xmu
      INTEGER IH,ipdg
      integer beamid
C
C     Include
C
      include 'pdf.inc'
C
      double precision tmp1, tmp2
      integer nb_proton1, nb_proton2
      integer nb_neutron1, nb_neutron2
      common/to_heavyion_pdg/ nb_proton1, nb_proton2, nb_neutron1, 
     &                        nb_neutron2
      integer nb_proton, nb_neutron      
c
      integer i,j,ihlast(2),ipart,iporg,ireuse,imemlast(2),iset,imem
      double precision xlast(2),xmulast(2),pdflast(-7:7,2)
      save ihlast,xlast,xmulast,pdflast,imemlast
      data ihlast/2*-99/
      data xlast/2*-99d9/
      data xmulast/2*-99d9/
      data pdflast/30*-99d9/
      data imemlast/2*-99/

      if (ih.eq.9) then
         pdg2pdf =1d0
         return
      endif

c     Make sure we have a reasonable Bjorken x. Note that even though
c     x=0 is not reasonable, we prefer to simply return pdg2pdf=0
c     instead of stopping the code, as this might accidentally happen.
      if (x.eq.0d0) then
         pdg2pdf=0d0
         return
      elseif (x.lt.0d0 .or. x.gt.1d0) then
         write (*,*) 'PDF not supported for Bjorken x ', x
         open(unit=26,file='../../../error',status='unknown')
         write(26,*) 'Error: PDF not supported for Bjorken x ',x
         stop 1
      endif

      ipart=ipdg
      if(ipart.eq.21) ipart=0
      if(iabs(ipart).eq.22) ipart=7
      iporg=ipart

c     This will be called for any PDG code, but we only support up to 7
      if(iabs(ipart).gt.7)then
         write(*,*) 'PDF not supported for pdg ',ipdg
         open(unit=26,file='../../../error',status='unknown')
         write(26,*) 'Error: PDF not supported for pdg ',ipdg
         stop 1
      endif

c     Determine the iset used in lhapdf
      call getnset(iset)
      if (iset.ne.1) then
         write (*,*) 'PDF not supported for Bjorken x ', x
         open(unit=26,file='../../../error',status='unknown')
         write(26,*) 'Error: PDF not supported for Bjorken x ',x
         stop 1
      endif

c     Determine the member of the set (function of lhapdf)
      call getnmem(iset,imem)

      ireuse = 0
      do i=1,2
c     Check if result can be reused since any of last two calls
         if (x.eq.xlast(i) .and. xmu.eq.xmulast(i) .and.
     $        imem.eq.imemlast(i) .and. ih.eq.ihlast(i)) then
            ireuse = i
         endif
      enddo

c     Reuse previous result, if possible
      if (ireuse.gt.0) then
         if (pdflast(iporg,ireuse).ne.-99d9) then
            pdg2pdf=pdflast(iporg,ireuse)
            return 
         endif
      endif

c     Bjorken x and/or facrorization scale and/or PDF set are not
c     identical to the saved values: this means a new event and we
c     should reset everything to compute new PDF values. Also, determine
c     if we should fill ireuse=1 or ireuse=2.
      if (ireuse.eq.0.and.xlast(1).ne.-99d9.and.xlast(2).ne.-99d9)then
         do i=1,2
            xlast(i)=-99d9
            xmulast(i)=-99d9
            do j=-7,7
               pdflast(j,i)=-99d9
            enddo
            imemlast(i)=-99
            ihlast(i)=-99
         enddo
c     everything has been reset. Now set ireuse=1 to fill the first
c     arrays of saved values below
         ireuse=1
      else if(ireuse.eq.0.and.xlast(1).ne.-99d9)then
c     This is first call after everything has been reset, so the first
c     arrays are already filled with the saved values (hence
c     xlast(1).ne.-99d9). Fill the second arrays of saved values (done
c     below) by setting ireuse=2
         ireuse=2
      else if(ireuse.eq.0)then
c     Special: only used for the very first call to this function:
c     xlast(i) are initialized as data statements to be equal to -99d9
         ireuse=1
      endif

c     Call lhapdf and give the current values to the arrays that should
c     be saved
      call pftopdglha(ih,x,xmu,pdflast(-7,ireuse))
c
c
c
      if (beamid.eq.1)then
         nb_proton = nb_proton1
         nb_neutron = nb_neutron1
      else
         nb_proton = nb_proton2
         nb_neutron = nb_neutron2
      endif
      if (nb_proton.gt.1.or.nb_neutron.ne.0)then
         tmp1 = pdflast(1, ireuse)
         tmp2 = pdflast(2, ireuse)
         pdflast(1, ireuse) = nb_proton * tmp1 + nb_neutron * tmp2
         pdflast(2, ireuse) = nb_proton * tmp2 + nb_neutron * tmp2
         tmp1 = pdflast(-1, ireuse)
         tmp2 = pdflast(-2, ireuse)
         pdflast(-1, ireuse) = nb_proton * tmp1 + nb_neutron * tmp2
         pdflast(-2, ireuse) = nb_proton * tmp2 + nb_neutron * tmp2
         do i=3,6
            pdflast(i, ireuse) = (nb_proton+nb_neutron)*pdflast(i, ireuse)
            pdflast(-i, ireuse) = (nb_proton+nb_neutron)*pdflast(-i, ireuse)
         enddo
      endif
      xlast(ireuse)=x
      xmulast(ireuse)=xmu
      ihlast(ireuse)=ih
      imemlast(ireuse)=imem
c
      pdg2pdf=pdflast(ipart,ireuse);
      return
      end

