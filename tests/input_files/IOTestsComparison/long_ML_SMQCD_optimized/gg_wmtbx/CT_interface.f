C     ===========================================
C     ===== Beginning of CutTools Interface =====
C     ===========================================
      SUBROUTINE ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Interface between MG5 and CutTools.
C     
C     Process: g g > w- t b~ QED=1 QCD=2 [ virt = QCD ]
C     
C     
C     CONSTANTS 
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      LOGICAL CHECKPCONSERVATION
      PARAMETER (CHECKPCONSERVATION=.TRUE.)
      REAL*8 NORMALIZATION
      PARAMETER (NORMALIZATION = 1.D0/(16.D0*3.14159265358979323846D0*
     $ *2))
C     
C     ARGUMENTS 
C     
      INTEGER NLOOPLINE, RANK
      REAL*8 PL(0:3,NLOOPLINE)
      REAL*8 PCT(0:3,0:NLOOPLINE-1)
      COMPLEX*16 M2L(NLOOPLINE)
      COMPLEX*16 M2LCT(0:NLOOPLINE-1)
      COMPLEX*16 RES(3)
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      COMPLEX*16 R1, ACC
      INTEGER I, J, K
      LOGICAL CTINIT, TIRINIT, GOLEMINIT, SAMURAIINIT, NINJAINIT
      COMMON/REDUCTIONCODEINIT/CTINIT,TIRINIT,GOLEMINIT,SAMURAIINIT
     $ ,NINJAINIT
C     
C     EXTERNAL FUNCTIONS
C     
      EXTERNAL ML5_0_LOOPNUM
      EXTERNAL ML5_0_MPLOOPNUM
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'
      INTEGER CTMODE
      REAL*8 LSCALE
      COMMON/ML5_0_CT/LSCALE,CTMODE

      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

C     ----------
C     BEGIN CODE
C     ----------

C     INITIALIZE CUTTOOLS IF NEEDED
      IF (CTINIT) THEN
        CTINIT=.FALSE.
        CALL ML5_0_INITCT()
      ENDIF

C     YOU CAN FIND THE DETAILS ABOUT THE DIFFERENT CTMODE AT THE
C      BEGINNING OF THE FILE CTS_CUTS.F90 IN THE CUTTOOLS DISTRIBUTION

C     CONVERT THE MASSES TO BE COMPLEX
      DO I=1,NLOOPLINE
        M2LCT(I-1)=M2L(I)
      ENDDO

C     CONVERT THE MOMENTA FLOWING IN THE LOOP LINES TO CT CONVENTIONS
      DO I=0,3
        DO J=0,(NLOOPLINE-1)
          PCT(I,J)=0.D0
        ENDDO
      ENDDO
      DO I=0,3
        DO J=1,NLOOPLINE
          PCT(I,0)=PCT(I,0)+PL(I,J)
        ENDDO
      ENDDO
      IF (CHECKPCONSERVATION) THEN
        IF (PCT(0,0).GT.1.D-6) THEN
          WRITE(*,*) 'energy is not conserved ',PCT(0,0)
          STOP 'energy is not conserved'
        ELSEIF (PCT(1,0).GT.1.D-6) THEN
          WRITE(*,*) 'px is not conserved ',PCT(1,0)
          STOP 'px is not conserved'
        ELSEIF (PCT(2,0).GT.1.D-6) THEN
          WRITE(*,*) 'py is not conserved ',PCT(2,0)
          STOP 'py is not conserved'
        ELSEIF (PCT(3,0).GT.1.D-6) THEN
          WRITE(*,*) 'pz is not conserved ',PCT(3,0)
          STOP 'pz is not conserved'
        ENDIF
      ENDIF
      DO I=0,3
        DO J=1,(NLOOPLINE-1)
          DO K=1,J
            PCT(I,J)=PCT(I,J)+PL(I,K)
          ENDDO
        ENDDO
      ENDDO

      CALL CTSXCUT(CTMODE,LSCALE,MU_R,NLOOPLINE,ML5_0_LOOPNUM
     $ ,ML5_0_MPLOOPNUM,RANK,PCT,M2LCT,RES,ACC,R1,STABLE)
      RES(1)=NORMALIZATION*2.0D0*DBLE(RES(1))
      RES(2)=NORMALIZATION*2.0D0*DBLE(RES(2))
      RES(3)=NORMALIZATION*2.0D0*DBLE(RES(3))
C     WRITE(*,*) 'CutTools: Loop ID',ID,' =',RES(1),RES(2),RES(3)
      END

      SUBROUTINE ML5_0_INITCT()
C     
C     INITIALISATION OF CUTTOOLS
C     
C     LOCAL VARIABLES 
C     
      REAL*8 THRS
      LOGICAL EXT_NUM_FOR_R1
C     
C     GLOBAL VARIABLES 
C     
      INCLUDE 'MadLoopParams.inc'
C     ----------
C     BEGIN CODE
C     ----------

C     DEFAULT PARAMETERS FOR CUTTOOLS
C     -------------------------------  
C     THRS1 IS THE PRECISION LIMIT BELOW WHICH THE MP ROUTINES
C      ACTIVATES
      THRS=CTSTABTHRES
C     LOOPLIB SET WHAT LIBRARY CT USES
C     1 -> LOOPTOOLS
C     2 -> AVH
C     3 -> QCDLOOP
      LOOPLIB=CTLOOPLIBRARY
C     MADLOOP'S NUMERATOR IN THE OPEN LOOP IS MUCH FASTER THAN THE
C      RECONSTRUCTED ONE IN CT. SO WE BETTER USE MADLOOP ONE IN THIS
C      CASE.
      EXT_NUM_FOR_R1=.TRUE.
C     -------------------------------	  

C     The initialization below is for CT v1.8.+
      CALL CTSINIT(THRS,LOOPLIB,EXT_NUM_FOR_R1)
C     The initialization below is for the older stable CT v1.7, still
C      used for now in the beta release.
C     CALL CTSINIT(THRS,LOOPLIB)

      END

      SUBROUTINE ML5_0_BUILD_KINEMATIC_MATRIX(NLOOPLINE,P_LOOP,M2L
     $ ,S_MAT)
C     
C     Helper function that compute the loop kinematic matrix with
C      proper thresholds
C     NLOOPLINE : Number of loop lines
C     P_LOOP    : List of external momenta running in the loop, i.e.
C      q_i in the denominator (l_i+q_i)**2-m_i**2
C     M2L       : List of complex-valued masses running in the loop.
C     S_MAT(N,N): Kinematic matrix output.
C     
C     ARGUMENTS
C     
      INTEGER NLOOPLINE
      REAL*8 P_LOOP(NLOOPLINE,0:3)
      COMPLEX*16 M2L(NLOOPLINE)
      COMPLEX*16 S_MAT(NLOOPLINE,NLOOPLINE)
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J,K
      COMPLEX*16 DIFFSQ
      REAL*8 REF_NORMALIZATION

C     ----------
C     BEGIN CODE
C     ----------

      DO I=1,NLOOPLINE
        DO J=1,NLOOPLINE

          IF(I.EQ.J)THEN
            S_MAT(I,J)=-(M2L(I)+M2L(J))
          ELSE
            DIFFSQ = (DCMPLX(P_LOOP(I,0),0.0D0)-DCMPLX(P_LOOP(J,0)
     $       ,0.0D0))**2
            DO K=1,3
              DIFFSQ = DIFFSQ - (DCMPLX(P_LOOP(I,K),0.0D0)-DCMPLX(P_LOO
     $         P(J,K),0.0D0))**2
            ENDDO
C           Default value of the kinematic matrix
            S_MAT(I,J)=DIFFSQ-M2L(I)-M2L(J)
C           And we now test various thresholds. Normaly, at most one
C            applies.
            IF(ABS(M2L(I)).NE.0.0D0)THEN
              IF(ABS((DIFFSQ-M2L(I))/M2L(I)).LT.OSTHRES)THEN
                S_MAT(I,J)=-M2L(J)
              ENDIF
            ENDIF
            IF(ABS(M2L(J)).NE.0.0D0)THEN
              IF(ABS((DIFFSQ-M2L(J))/M2L(J)).LT.OSTHRES)THEN
                S_MAT(I,J)=-M2L(I)
              ENDIF
            ENDIF
C           Choose what seems the most appropriate way to compare
C           massless onshellness.
            REF_NORMALIZATION=0.0D0
C           Here, we chose to base the threshold only on the energy
C            component
            DO K=0,0
              REF_NORMALIZATION = REF_NORMALIZATION + ABS(P_LOOP(I
     $         ,K)) + ABS(P_LOOP(J,K))
            ENDDO
            REF_NORMALIZATION = (REF_NORMALIZATION/2.0D0)**2
            IF(REF_NORMALIZATION.NE.0.0D0)THEN
              IF(ABS(DIFFSQ/REF_NORMALIZATION).LT.OSTHRES)THEN
                S_MAT(I,J)=-(M2L(I)+M2L(J))
              ENDIF
            ENDIF
          ENDIF

        ENDDO
      ENDDO

      END



      SUBROUTINE ML5_0_LOOP_5(W1, W2, W3, W4, W5, M1, M2, M3, M4, M5
     $ ,  RANK, SQUAREDSOINDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=5)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=77)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=0)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4, W5
      COMPLEX*16 M1, M2, M3, M4, M5

      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(5)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/ML5_0_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/ML5_0_W/W
      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/ML5_0_CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/ML5_0_I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED).OR.GOODAMP(SQUAREDSOIND
     $ EX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        WE(4)=W4
        WE(5)=W5
        M2L(1)=M5**2
        M2L(2)=M1**2
        M2L(3)=M2**2
        M2L(4)=M3**2
        M2L(5)=M4**2
        DO I=1,NLOOPLINE
          PAIRING(I)=1
        ENDDO

        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Determine it uses qp or not
        DOING_QP=.FALSE.
        IF(CTMODE.GE.4)DOING_QP=.TRUE.
C       Choose the correct loop library
        CALL ML5_0_CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS
     $   ,ID,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOIN
     $     DEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSE
C         Tensor Integral Reduction is used 
          CALL ML5_0_TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL
     $     ,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE ML5_0_LOOP_4_5(P1, P2, P3, P4, W1, W2, W3, W4, W5, M1
     $ , M2, M3, M4,  RANK, SQUAREDSOINDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=4)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=77)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=0)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4, W5
      COMPLEX*16 M1, M2, M3, M4
      INTEGER P1, P2, P3, P4
      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(5)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/ML5_0_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/ML5_0_W/W
      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/ML5_0_CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/ML5_0_I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED).OR.GOODAMP(SQUAREDSOIND
     $ EX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        WE(4)=W4
        WE(5)=W5
        M2L(1)=M4**2
        M2L(2)=M1**2
        M2L(3)=M2**2
        M2L(4)=M3**2
        PAIRING(1)=P1
        PAIRING(2)=P2
        PAIRING(3)=P3
        PAIRING(4)=P4
        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Determine it uses qp or not
        DOING_QP=.FALSE.
        IF(CTMODE.GE.4)DOING_QP=.TRUE.
C       Choose the correct loop library
        CALL ML5_0_CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS
     $   ,ID,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOIN
     $     DEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSE
C         Tensor Integral Reduction is used 
          CALL ML5_0_TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL
     $     ,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE ML5_0_LOOP_4(W1, W2, W3, W4, M1, M2, M3, M4,  RANK
     $ , SQUAREDSOINDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=4)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=77)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=0)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4
      COMPLEX*16 M1, M2, M3, M4

      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(4)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/ML5_0_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/ML5_0_W/W
      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/ML5_0_CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/ML5_0_I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED).OR.GOODAMP(SQUAREDSOIND
     $ EX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        WE(4)=W4
        M2L(1)=M4**2
        M2L(2)=M1**2
        M2L(3)=M2**2
        M2L(4)=M3**2
        DO I=1,NLOOPLINE
          PAIRING(I)=1
        ENDDO

        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Determine it uses qp or not
        DOING_QP=.FALSE.
        IF(CTMODE.GE.4)DOING_QP=.TRUE.
C       Choose the correct loop library
        CALL ML5_0_CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS
     $   ,ID,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOIN
     $     DEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSE
C         Tensor Integral Reduction is used 
          CALL ML5_0_TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL
     $     ,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE ML5_0_LOOP_2_3(P1, P2, W1, W2, W3, M1, M2,  RANK
     $ , SQUAREDSOINDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=2)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=77)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=0)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3
      COMPLEX*16 M1, M2
      INTEGER P1, P2
      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(3)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/ML5_0_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/ML5_0_W/W
      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/ML5_0_CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/ML5_0_I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED).OR.GOODAMP(SQUAREDSOIND
     $ EX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        M2L(1)=M2**2
        M2L(2)=M1**2
        PAIRING(1)=P1
        PAIRING(2)=P2
        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Determine it uses qp or not
        DOING_QP=.FALSE.
        IF(CTMODE.GE.4)DOING_QP=.TRUE.
C       Choose the correct loop library
        CALL ML5_0_CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS
     $   ,ID,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOIN
     $     DEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSE
C         Tensor Integral Reduction is used 
          CALL ML5_0_TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL
     $     ,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE ML5_0_LOOP_2(W1, W2, M1, M2,  RANK, SQUAREDSOINDEX
     $ , LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=2)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=77)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=0)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2
      COMPLEX*16 M1, M2

      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(2)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/ML5_0_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/ML5_0_W/W
      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/ML5_0_CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/ML5_0_I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED).OR.GOODAMP(SQUAREDSOIND
     $ EX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        M2L(1)=M2**2
        M2L(2)=M1**2
        DO I=1,NLOOPLINE
          PAIRING(I)=1
        ENDDO

        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Determine it uses qp or not
        DOING_QP=.FALSE.
        IF(CTMODE.GE.4)DOING_QP=.TRUE.
C       Choose the correct loop library
        CALL ML5_0_CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS
     $   ,ID,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOIN
     $     DEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSE
C         Tensor Integral Reduction is used 
          CALL ML5_0_TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL
     $     ,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE ML5_0_LOOP_3_4(P1, P2, P3, W1, W2, W3, W4, M1, M2, M3
     $ ,  RANK, SQUAREDSOINDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=3)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=77)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=0)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4
      COMPLEX*16 M1, M2, M3
      INTEGER P1, P2, P3
      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(4)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/ML5_0_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/ML5_0_W/W
      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/ML5_0_CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/ML5_0_I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED).OR.GOODAMP(SQUAREDSOIND
     $ EX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        WE(4)=W4
        M2L(1)=M3**2
        M2L(2)=M1**2
        M2L(3)=M2**2
        PAIRING(1)=P1
        PAIRING(2)=P2
        PAIRING(3)=P3
        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Determine it uses qp or not
        DOING_QP=.FALSE.
        IF(CTMODE.GE.4)DOING_QP=.TRUE.
C       Choose the correct loop library
        CALL ML5_0_CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS
     $   ,ID,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOIN
     $     DEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSE
C         Tensor Integral Reduction is used 
          CALL ML5_0_TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL
     $     ,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE ML5_0_LOOP_3(W1, W2, W3, M1, M2, M3,  RANK, SQUAREDSOI
     $ NDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=3)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=77)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=0)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3
      COMPLEX*16 M1, M2, M3

      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(3)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/ML5_0_LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/ML5_0_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/ML5_0_W/W
      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/ML5_0_CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/ML5_0_I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED).OR.GOODAMP(SQUAREDSOIND
     $ EX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        M2L(1)=M3**2
        M2L(2)=M1**2
        M2L(3)=M2**2
        DO I=1,NLOOPLINE
          PAIRING(I)=1
        ENDDO

        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Determine it uses qp or not
        DOING_QP=.FALSE.
        IF(CTMODE.GE.4)DOING_QP=.TRUE.
C       Choose the correct loop library
        CALL ML5_0_CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS
     $   ,ID,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOIN
     $     DEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSE
C         Tensor Integral Reduction is used 
          CALL ML5_0_TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL
     $     ,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

