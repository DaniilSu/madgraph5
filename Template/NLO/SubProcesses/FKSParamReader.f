      subroutine FKSParamReader(filename, printParam, force) 

      implicit none

      logical HasReadOnce, force
      data HasReadOnce/.FALSE./


      CHARACTER*64 fileName, buff, buff2, mode
      include "FKSParams.inc"

      logical printParam, couldRead, paramPrinted
      data paramPrinted/.FALSE./
      couldRead=.False.
!     Default parameters

      if (HasReadOnce.and..not.force) then
          goto 901
      endif

      open(666, file=fileName, err=676, action='READ')
      do
         read(666,*,end=999) buff
         if(index(buff,'#').eq.1) then

           if (buff .eq. '#IRPoleCheckThreshold') then
             read(666,*,end=999) IRPoleCheckThreshold
             if (IRPoleCheckThreshold .lt. -1.01d0 ) then
               stop 'IRPoleCheckThreshold must be >= -1.0d0.'
             endif 

           else if (buff .eq. '#NHelForMCoverHels') then
             read(666,*,end=999) NHelForMCoverHels
             if (NHelForMCoverHels .lt. -1) then
               stop 'NHelForMCoverHels must be >= -1.'
             endif 
           else if (buff .eq. '#VirtualFraction') then
             read(666,*,end=999) Virt_fraction
             if ((Virt_fraction .lt. 0 .or. virt_fraction .gt.1) .and.
     $            virt_fraction.ne.-1) then
                stop 'VirtualFraction should be a fraction'/
     $               /' between 0 and 1 (or equal to -1)'
             endif 
           else
             write(*,*) 'The parameter name ',buff(2:),
     &' is not reckognized.'
             stop
           endif
         endif
      enddo
  999 continue
      couldRead=.True.
      goto 998      

  676 continue
      write(*,*) 'ERROR :: MadFKS parameter file ',fileName,
     &' could not be found or is malformed. Please specify it.'
      stop 
C     Below is the code if one desires to let the code continue with
C     a non existing or malformed parameter file
      write(*,*) 'WARNING :: The file ',fileName,' could not be ',
     & ' open or did not contain the necessary information. The ',
     & ' default MadFKS parameters will be used.'
      call DefaultFKSParam()
      goto 998

  998 continue

      if(printParam.and..not.paramPrinted) then
      write(*,*)
     & '==============================================================='
      if (couldRead) then      
        write(*,*) 'INFO: MadFKS read these parameters from '
     &,filename
      else
        write(*,*) 'INFO: MadFKS used the default parameters.'
      endif
      write(*,*)
     & '==============================================================='
      write(*,*) ' > IRPoleCheckThreshold      = ',IRPoleCheckThreshold
      write(*,*) ' > NHelForMCoverHels         = ',NHelForMCoverHels
      write(*,*) ' > VirtualFraction           = ',Virt_fraction
      write(*,*)
     & '==============================================================='
      paramPrinted=.TRUE.
      endif

      close(666)
      HasReadOnce=.TRUE.
  901 continue
      end

      subroutine DefaultFKSParam() 

      implicit none
      
      include "FKSParams.inc"

      IRPoleCheckThreshold=1.0d-5
      NHelForMCoverHels=5

      end
