      SUBROUTINE ML5_0_MP_HELAS_CALLS_AMPB_1(P,NHEL,H,IC)
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)

      INTEGER NBORNAMPS
      PARAMETER (NBORNAMPS=1)
      INTEGER    NLOOPS, NLOOPGROUPS, NCTAMPS
      PARAMETER (NLOOPS=11, NLOOPGROUPS=8, NCTAMPS=29)
      INTEGER    NLOOPAMPS
      PARAMETER (NLOOPAMPS=40)
      INTEGER    NWAVEFUNCS,NLOOPWAVEFUNCS
      PARAMETER (NWAVEFUNCS=6,NLOOPWAVEFUNCS=26)
      INCLUDE 'loop_max_coefs.inc'
      INCLUDE 'coef_specs.inc'
      REAL*16     ZERO
      PARAMETER (ZERO=0.0E0_16)
      COMPLEX*32     IZERO
      PARAMETER (IZERO=CMPLX(0.0E0_16,0.0E0_16,KIND=16))
C     These are constants related to the split orders
      INTEGER    NSO, NSQUAREDSO, NAMPSO
      PARAMETER (NSO=0, NSQUAREDSO=0, NAMPSO=0)
C     
C     ARGUMENTS
C     
      REAL*16 P(0:3,NEXTERNAL)
      INTEGER NHEL(NEXTERNAL), IC(NEXTERNAL)
      INTEGER H
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J,K
      COMPLEX*32 COEFS(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'mp_coupl_same_name.inc'

      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/ML5_0_FILTERS/GOODAMP,GOODHEL

      INTEGER SQSO_TARGET
      COMMON/ML5_0_SOCHOICE/SQSO_TARGET

      LOGICAL UVCT_REQ_SO_DONE,MP_UVCT_REQ_SO_DONE,CT_REQ_SO_DONE
     $ ,MP_CT_REQ_SO_DONE,LOOP_REQ_SO_DONE,MP_LOOP_REQ_SO_DONE
     $ ,CTCALL_REQ_SO_DONE,FILTER_SO
      COMMON/ML5_0_SO_REQS/UVCT_REQ_SO_DONE,MP_UVCT_REQ_SO_DONE
     $ ,CT_REQ_SO_DONE,MP_CT_REQ_SO_DONE,LOOP_REQ_SO_DONE
     $ ,MP_LOOP_REQ_SO_DONE,CTCALL_REQ_SO_DONE,FILTER_SO

      COMPLEX*32 AMP(NBORNAMPS)
      COMMON/ML5_0_MP_AMPS/AMP
      COMPLEX*32 W(20,NWAVEFUNCS)
      COMMON/ML5_0_MP_W/W

      COMPLEX*32 WL(MAXLWFSIZE,0:LOOPMAXCOEFS-1,MAXLWFSIZE
     $ ,0:NLOOPWAVEFUNCS)
      COMPLEX*32 PL(0:3,0:NLOOPWAVEFUNCS)
      COMMON/ML5_0_MP_WL/WL,PL

      COMPLEX*32 AMPL(3,NCTAMPS)
      COMMON/ML5_0_MP_AMPL/AMPL

C     
C     ----------
C     BEGIN CODE
C     ----------

C     The target squared split order contribution is already reached
C      if true.
      IF (FILTER_SO.AND.MP_CT_REQ_SO_DONE) THEN
        GOTO 1001
      ENDIF

      CALL MP_IXXXXX(P(0,1),ZERO,NHEL(1),+1*IC(1),W(1,1))
      CALL MP_OXXXXX(P(0,2),ZERO,NHEL(2),-1*IC(2),W(1,2))
      CALL MP_OXXXXX(P(0,3),MDL_MT,NHEL(3),+1*IC(3),W(1,3))
      CALL MP_IXXXXX(P(0,4),MDL_MT,NHEL(4),-1*IC(4),W(1,4))
      CALL MP_FFV1P0_3(W(1,1),W(1,2),GC_5,ZERO,ZERO,W(1,5))
C     Amplitude(s) for born diagram with ID 1
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),GC_5,AMP(1))
      CALL MP_FFV1P0_3(W(1,4),W(1,3),GC_5,ZERO,ZERO,W(1,6))
C     Counter-term amplitude(s) for loop diagram number 2
      CALL MP_R2_GG_1_0(W(1,5),W(1,6),R2_GGQ,AMPL(1,1))
      CALL MP_R2_GG_1_0(W(1,5),W(1,6),R2_GGQ,AMPL(1,2))
      CALL MP_R2_GG_1_0(W(1,5),W(1,6),R2_GGQ,AMPL(1,3))
      CALL MP_R2_GG_1_0(W(1,5),W(1,6),R2_GGQ,AMPL(1,4))
C     Counter-term amplitude(s) for loop diagram number 5
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQQ_1EPS,AMPL(2,5))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQQ_1EPS,AMPL(2,6))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQQ_1EPS,AMPL(2,7))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQQ_1EPS,AMPL(2,8))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQB,AMPL(1,9))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQQ_1EPS,AMPL(2,10))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQT,AMPL(1,11))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQQ_1EPS,AMPL(2,12))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),UV_GQQG_1EPS,AMPL(2,13))
      CALL MP_FFV1_0(W(1,1),W(1,2),W(1,6),R2_GQQ,AMPL(1,14))
C     Counter-term amplitude(s) for loop diagram number 7
      CALL MP_R2_GG_1_R2_GG_3_0(W(1,5),W(1,6),R2_GGQ,R2_GGB,AMPL(1,15))
C     Counter-term amplitude(s) for loop diagram number 8
      CALL MP_R2_GG_1_R2_GG_3_0(W(1,5),W(1,6),R2_GGQ,R2_GGT,AMPL(1,16))
C     Counter-term amplitude(s) for loop diagram number 9
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQQ_1EPS,AMPL(2,17))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQQ_1EPS,AMPL(2,18))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQQ_1EPS,AMPL(2,19))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQQ_1EPS,AMPL(2,20))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQB,AMPL(1,21))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQQ_1EPS,AMPL(2,22))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQT,AMPL(1,23))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQQ_1EPS,AMPL(2,24))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),UV_GQQG_1EPS,AMPL(2,25))
      CALL MP_FFV1_0(W(1,4),W(1,3),W(1,5),R2_GQQ,AMPL(1,26))
C     Counter-term amplitude(s) for loop diagram number 11
      CALL MP_R2_GG_1_R2_GG_2_0(W(1,5),W(1,6),R2_GGG_1,R2_GGG_2,AMPL(1
     $ ,27))

      GOTO 1001
 2000 CONTINUE
      MP_CT_REQ_SO_DONE=.TRUE.
 1001 CONTINUE
      END

