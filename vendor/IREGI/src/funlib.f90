MODULE funlib
  USE global
  IMPLICIT NONE
CONTAINS
  RECURSIVE FUNCTION factorial(i) RESULT(fac)
    IMPLICIT NONE
    INTEGER::fac
    INTEGER,INTENT(IN)::i
    IF(i.LT.0)THEN
       WRITE(*,*)"ERROR: i<0 in factorial with i=",i
       STOP
    ENDIF
    IF(i.EQ.0)THEN
       fac=1
    ELSE
       fac=i*factorial(i-1)
    ENDIF
  END FUNCTION factorial

  SUBROUTINE PCL2PE(NLOOPLINE,PCL,PE)
    ! transfer the loop momenta q,q+p1,q+p1+p2,q+p1+p2+p3,... 
    ! to p1,p2,p3,p4,... 
    IMPLICIT NONE
    INTEGER,INTENT(IN)::NLOOPLINE
    REAL(KIND(1d0)),DIMENSION(NLOOPLINE,0:3),INTENT(IN)::PCL
    REAL(KIND(1d0)),DIMENSION(NLOOPLINE,0:3),INTENT(OUT)::PE
    INTEGER::i
    DO i=1,NLOOPLINE-1
       PE(i,0:3)=PCL(i+1,0:3)-PCL(i,0:3)
    ENDDO
    PE(NLOOPLINE,0:3)=PCL(1,0:3)-PCL(NLOOPLINE,0:3)
    RETURN
  END SUBROUTINE PCL2PE

  RECURSIVE SUBROUTINE calc_all_integers(n,ntot,i,sol)
    ! finds all the non-negative solutions to x1,...,xn
    ! that x1+x2+...+xn==i
    ! the number of solutions should be ntot=C(i+n-1)^(n-1)=(i+n-1)!/(n-1)!/i!
    ! it can be recycled for all phase space point
    IMPLICIT NONE
    INTEGER,INTENT(IN)::n,ntot,i
    INTEGER,DIMENSION(ntot,n),INTENT(OUT)::sol
    INTEGER::j,k,k0
    IF(i.EQ.0)THEN
       sol(1,1:n)=0
       RETURN
    ENDIF
    IF(n.EQ.1)THEN
       sol(1,1)=i
       RETURN
    ENDIF
    k0=0
    DO j=0,i
       k=factorial(i-j+n-2)/factorial(n-2)/factorial(i-j)
       sol(k0+1:k0+k,1)=j
       CALL calc_all_integers(n-1,k,i-j,sol(k0+1:k0+k,2:n))
       k0=k0+k
    ENDDO
    RETURN
  END SUBROUTINE calc_all_integers

  SUBROUTINE all_Integers(n,ntot,i,sol,factor)
    ! finds all the non-negative solutions to x1,...,xn 
    ! that x1+x2+...+xn==i 
    ! the number of solutions should be ntot=C(i+n-1)^(n-1)=(i+n-1)!/(n-1)!/i!
    ! it can be recycled for all phase space point 
    IMPLICIT NONE
    INTEGER,INTENT(IN)::n,ntot,i
    INTEGER,DIMENSION(ntot,n),INTENT(OUT)::sol
    REAL(KIND(1d0)),DIMENSION(ntot),INTENT(OUT)::factor
    INTEGER::ifirst=0,j,k,ntemptot
    SAVE ifirst
    ! calculate xiarray_i_n first
    IF(ifirst.EQ.0)THEN
       DO j=0,10
          x1array(j,1)=j
       ENDDO
       ! n=2
       CALL calc_all_integers(2,1,0,xiarray_0_2(1:1,1:2))
       factor_xiarray_0_2(1)=1d0
       CALL calc_all_integers(2,2,1,xiarray_1_2(1:2,1:2))
       DO j=1,2
          factor_xiarray_1_2(j)=DBLE(factorial(1))
          DO k=1,2
             factor_xiarray_1_2(j)=factor_xiarray_1_2(j)/&
                  DBLE(factorial(xiarray_1_2(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(2,3,2,xiarray_2_2(1:3,1:2))
       DO j=1,3
          factor_xiarray_2_2(j)=DBLE(factorial(2))
          DO k=1,2
             factor_xiarray_2_2(j)=factor_xiarray_2_2(j)/&
                  DBLE(factorial(xiarray_2_2(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(2,4,3,xiarray_3_2(1:4,1:2))
       DO j=1,4
          factor_xiarray_3_2(j)=DBLE(factorial(3))
          DO k=1,2
             factor_xiarray_3_2(j)=factor_xiarray_3_2(j)/&
                  DBLE(factorial(xiarray_3_2(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(2,5,4,xiarray_4_2(1:5,1:2))
       DO j=1,5
          factor_xiarray_4_2(j)=DBLE(factorial(4))
          DO k=1,2
             factor_xiarray_4_2(j)=factor_xiarray_4_2(j)/&
                  DBLE(factorial(xiarray_4_2(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(2,6,5,xiarray_5_2(1:6,1:2))
       DO j=1,6
          factor_xiarray_5_2(j)=DBLE(factorial(5))
          DO k=1,2
             factor_xiarray_5_2(j)=factor_xiarray_5_2(j)/&
                  DBLE(factorial(xiarray_5_2(j,k)))
          ENDDO
       ENDDO
       ntot_xiarray(0,2)=1
       ntot_xiarray(1,2)=2
       ntot_xiarray(2,2)=3
       ntot_xiarray(3,2)=4
       ntot_xiarray(4,2)=5
       ntot_xiarray(5,2)=6
       ! n=3
       CALL calc_all_integers(3,1,0,xiarray_0_3(1:1,1:3))
       factor_xiarray_0_3(1)=1d0
       CALL calc_all_integers(3,3,1,xiarray_1_3(1:3,1:3))
       DO j=1,3
          factor_xiarray_1_3(j)=DBLE(factorial(1))
          DO k=1,3
             factor_xiarray_1_3(j)=factor_xiarray_1_3(j)/&
                  DBLE(factorial(xiarray_1_3(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(3,6,2,xiarray_2_3(1:6,1:3))
       DO j=1,6
          factor_xiarray_2_3(j)=DBLE(factorial(2))
          DO k=1,3
             factor_xiarray_2_3(j)=factor_xiarray_2_3(j)/&
                  DBLE(factorial(xiarray_2_3(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(3,10,3,xiarray_3_3(1:10,1:3))
       DO j=1,10
          factor_xiarray_3_3(j)=DBLE(factorial(3))
          DO k=1,3
             factor_xiarray_3_3(j)=factor_xiarray_3_3(j)/&
                  DBLE(factorial(xiarray_3_3(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(3,15,4,xiarray_4_3(1:15,1:3))
       DO j=1,15
          factor_xiarray_4_3(j)=DBLE(factorial(4))
          DO k=1,3
             factor_xiarray_4_3(j)=factor_xiarray_4_3(j)/&
                  DBLE(factorial(xiarray_4_3(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(3,21,5,xiarray_5_3(1:21,1:3))
       DO j=1,21
          factor_xiarray_5_3(j)=DBLE(factorial(5))
          DO k=1,3
             factor_xiarray_5_3(j)=factor_xiarray_5_3(j)/&
                  DBLE(factorial(xiarray_5_3(j,k)))
          ENDDO
       ENDDO
       ntot_xiarray(0,3)=1
       ntot_xiarray(1,3)=3
       ntot_xiarray(2,3)=6
       ntot_xiarray(3,3)=10
       ntot_xiarray(4,3)=15
       ntot_xiarray(5,3)=21
       ! n=4
       CALL calc_all_integers(4,1,0,xiarray_0_4(1:1,1:4))
       factor_xiarray_0_4(1)=1d0
       CALL calc_all_integers(4,4,1,xiarray_1_4(1:4,1:4))
       DO j=1,4
          factor_xiarray_1_4(j)=DBLE(factorial(1))
          DO k=1,4
             factor_xiarray_1_4(j)=factor_xiarray_1_4(j)/&
                  DBLE(factorial(xiarray_1_4(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(4,10,2,xiarray_2_4(1:10,1:4))
       DO j=1,10
          factor_xiarray_2_4(j)=DBLE(factorial(2))
          DO k=1,4
             factor_xiarray_2_4(j)=factor_xiarray_2_4(j)/&
                  DBLE(factorial(xiarray_2_4(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(4,20,3,xiarray_3_4(1:20,1:4))
       DO j=1,20
          factor_xiarray_3_4(j)=DBLE(factorial(3))
          DO k=1,4
             factor_xiarray_3_4(j)=factor_xiarray_3_4(j)/&
                  DBLE(factorial(xiarray_3_4(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(4,35,4,xiarray_4_4(1:35,1:4))
       DO j=1,35
          factor_xiarray_4_4(j)=DBLE(factorial(4))
          DO k=1,4
             factor_xiarray_4_4(j)=factor_xiarray_4_4(j)/&
                  DBLE(factorial(xiarray_4_4(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(4,56,5,xiarray_5_4(1:56,1:4))
       DO j=1,56
          factor_xiarray_5_4(j)=DBLE(factorial(5))
          DO k=1,4
             factor_xiarray_5_4(j)=factor_xiarray_5_4(j)/&
                  DBLE(factorial(xiarray_5_4(j,k)))
          ENDDO
       ENDDO
       ntot_xiarray(0,4)=1
       ntot_xiarray(1,4)=4
       ntot_xiarray(2,4)=10
       ntot_xiarray(3,4)=20
       ntot_xiarray(4,4)=35
       ntot_xiarray(5,4)=56
       ! n=5
       CALL calc_all_integers(5,1,0,xiarray_0_5(1:1,1:5))
       factor_xiarray_0_5(1)=1d0
       CALL calc_all_integers(5,5,1,xiarray_1_5(1:5,1:5))
       DO j=1,5
          factor_xiarray_1_5(j)=DBLE(factorial(1))
          DO k=1,5
             factor_xiarray_1_5(j)=factor_xiarray_1_5(j)/&
                  DBLE(factorial(xiarray_1_5(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(5,15,2,xiarray_2_5(1:15,1:5))
       DO j=1,15
          factor_xiarray_2_5(j)=DBLE(factorial(2))
          DO k=1,5
             factor_xiarray_2_5(j)=factor_xiarray_2_5(j)/&
                  DBLE(factorial(xiarray_2_5(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(5,35,3,xiarray_3_5(1:35,1:5))
       DO j=1,35
          factor_xiarray_3_5(j)=DBLE(factorial(3))
          DO k=1,5
             factor_xiarray_3_5(j)=factor_xiarray_3_5(j)/&
                  DBLE(factorial(xiarray_3_5(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(5,70,4,xiarray_4_5(1:70,1:5))
       DO j=1,70
          factor_xiarray_4_5(j)=DBLE(factorial(4))
          DO k=1,5
             factor_xiarray_4_5(j)=factor_xiarray_4_5(j)/&
                  DBLE(factorial(xiarray_4_5(j,k)))
          ENDDO
       ENDDO
       CALL calc_all_integers(5,126,5,xiarray_5_5(1:126,1:5))
       DO j=1,126
          factor_xiarray_5_5(j)=DBLE(factorial(5))
          DO k=1,5
             factor_xiarray_5_5(j)=factor_xiarray_5_5(j)/&
                  DBLE(factorial(xiarray_5_5(j,k)))
          ENDDO
       ENDDO
       ntot_xiarray(0,5)=1
       ntot_xiarray(1,5)=5
       ntot_xiarray(2,5)=15
       ntot_xiarray(3,5)=35
       ntot_xiarray(4,5)=70
       ntot_xiarray(5,5)=126
       ifirst=1
    ENDIF
    IF(n.EQ.1.AND.i.GT.10)THEN
       WRITE(*,*)"ERROR:i is out of the range 10 for n=1 in all_integers"
       STOP
    ENDIF
    IF(n.EQ.1.AND.ntot.NE.1)THEN
       WRITE(*,*)"ERROR:ntot should be 1 when n=1 in all_integers"
       STOP
    ENDIF
    IF(n.GE.2.AND.n.LE.5.AND.i.GT.5)THEN
       WRITE(*,*)"ERROR: i is out of the range 5 for 2<=n<=5 in all_integers"
       STOP
    ENDIF
    IF(n.GE.2.AND.n.LE.5)THEN
       ! Make it work in MadLoop, otherwise it is wrong
       IF(ntot.NE.ntot_xiarray(i,n))THEN
          WRITE(*,*)"ERROR: ntot is not correct in all_integers"
          STOP
       ENDIF
    ENDIF
    IF(n.GT.5.OR.n.LT.1)THEN
       WRITE(*,*)"ERROR: n is out of range 1<=n<=5 in all_integers"
       STOP
    ENDIF
    SELECT CASE(n)
       CASE(1)
          sol(1:ntot,1:n)=x1array(i:i,1:n)
          factor(1)=1d0
       CASE(2)
          SELECT CASE(i)
             CASE(0)
                sol(1:ntot,1:n)=xiarray_0_2(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_0_2(1:ntot)
             CASE(1)
                sol(1:ntot,1:n)=xiarray_1_2(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_1_2(1:ntot)
             CASE(2)
                sol(1:ntot,1:n)=xiarray_2_2(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_2_2(1:ntot)
             CASE(3)
                sol(1:ntot,1:n)=xiarray_3_2(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_3_2(1:ntot)
             CASE(4)
                sol(1:ntot,1:n)=xiarray_4_2(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_4_2(1:ntot)
             CASE(5)
                sol(1:ntot,1:n)=xiarray_5_2(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_5_2(1:ntot)
          END SELECT
       CASE(3)
          SELECT CASE(i)
             CASE(0)
                sol(1:ntot,1:n)=xiarray_0_3(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_0_3(1:ntot)
             CASE(1)
                sol(1:ntot,1:n)=xiarray_1_3(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_1_3(1:ntot)
             CASE(2)
                sol(1:ntot,1:n)=xiarray_2_3(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_2_3(1:ntot)
             CASE(3)
                sol(1:ntot,1:n)=xiarray_3_3(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_3_3(1:ntot)
             CASE(4)
                sol(1:ntot,1:n)=xiarray_4_3(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_4_3(1:ntot)
             CASE(5)
                sol(1:ntot,1:n)=xiarray_5_3(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_5_3(1:ntot)
          END SELECT
       CASE(4)
          SELECT CASE(i)
             CASE(0)
                sol(1:ntot,1:n)=xiarray_0_4(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_0_4(1:ntot)
             CASE(1)
                sol(1:ntot,1:n)=xiarray_1_4(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_1_4(1:ntot)
             CASE(2)
                sol(1:ntot,1:n)=xiarray_2_4(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_2_4(1:ntot)
             CASE(3)
                sol(1:ntot,1:n)=xiarray_3_4(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_3_4(1:ntot)
             CASE(4)
                sol(1:ntot,1:n)=xiarray_4_4(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_4_4(1:ntot)
             CASE(5)
                sol(1:ntot,1:n)=xiarray_5_4(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_5_4(1:ntot)
          END SELECT
       CASE(5)
          SELECT CASE(i)
             CASE(0)
                sol(1:ntot,1:n)=xiarray_0_5(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_0_5(1:ntot)
             CASE(1)
                sol(1:ntot,1:n)=xiarray_1_5(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_1_5(1:ntot)
             CASE(2)
                sol(1:ntot,1:n)=xiarray_2_5(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_2_5(1:ntot)
             CASE(3)
                sol(1:ntot,1:n)=xiarray_3_5(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_3_5(1:ntot)
             CASE(4)
                sol(1:ntot,1:n)=xiarray_4_5(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_4_5(1:ntot)
             CASE(5)
                sol(1:ntot,1:n)=xiarray_5_5(1:ntot,1:n)
                factor(1:ntot)=factor_xiarray_5_5(1:ntot)
          END SELECT
    END SELECT
    RETURN
  END SUBROUTINE all_Integers

  SUBROUTINE calc_factorial_pair
    IMPLICIT NONE
    INTEGER::i,j
    factorial_pair(1:10,0)=1d0
    DO i=1,10
       DO j=1,10
          factorial_pair(i,j)=DBLE(factorial(i+j-1))&
               /DBLE(factorial(i-1))/DBLE(factorial(j))
       ENDDO
    ENDDO
    RETURN
  END SUBROUTINE calc_factorial_pair

  FUNCTION number_coefs_for_rank(rank) RESULT(res)
    IMPLICIT NONE
    INTEGER,INTENT(IN)::rank
    INTEGER::res,i
    IF(rank.LT.0)res=0
    res=0
    DO i=0,rank
       res=res+((3+i)*(2+i)*(1+i))/6
    ENDDO
    RETURN
  END FUNCTION number_coefs_for_rank

  SUBROUTINE timestamp
    IMPLICIT NONE    
    CHARACTER(len=8)::ampm
    INTEGER::d
    INTEGER::h
    INTEGER::m,n
    INTEGER::mm
    CHARACTER( len = 9 ),PARAMETER,DIMENSION(12) :: month = (/ &
         'January  ', 'February ', 'March    ', 'April    ', &
         'May      ', 'June     ', 'July     ', 'August   ', &
         'September', 'October  ', 'November ', 'December ' /)
    INTEGER::dn
    INTEGER::s
    INTEGER,DIMENSION(8)::values
    INTEGER::y
    CALL date_and_time(values=values)
    y = values(1)
    m = values(2)
    d = values(3)
    h = values(5)
    n = values(6)
    s = values(7)
    mm = values(8)
    IF( h.LT.12 )THEN
       ampm = 'AM'
    ELSEIF( h.EQ.12 )THEN
       IF( n.EQ.0 .AND. s.EQ.0 )THEN
          ampm = 'Noon'
       ELSE
          ampm = 'PM'
       ENDIF
    ELSE
       h = h - 12
       IF( h.LT.12 )THEN
          ampm = 'PM'
       ELSEIF( h.EQ.12 )THEN
          IF(n.EQ.0.AND.s.EQ.0)THEN
             ampm = 'Midnight'
          ELSE
             ampm = 'AM'
          ENDIF
       ENDIF
    ENDIF
    WRITE( *, '(i2,1x,a,1x,i4,2x,i2,a1,i2.2,a1,i2.2,a1,i3.3,1x,a)' ) &
         d, TRIM( month(m) ), y, h, ':', n, ':', s, '.', mm, TRIM( ampm )  
    RETURN
  END SUBROUTINE timestamp
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                                                                               !
! FOLLOWING SUBROUTINES/FUNCTIONS ARE ONLY FOR THE REORDERING THE TIR COEFS     !
!                                                                               !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  SUBROUTINE SORT_IREGICOEFS(RANK,NLOOPCOEFS,OLDCOEFS,NEWCOEFS)
    !
    ! CONVERT THE OUTPUT OF IREGI TO THAT OF (NEW) MADLOOP 
    !
    ! THE NEW OUTPUT OF COEFS FROM MADLOOP IS
    ! RANK=0: (,)
    ! RANK=1: (0,),(1,),(2,),(3,)
    ! RANK=2: (0,0),(0,1),(1,1),(0,2),(1,2),(2,2),(0,3),(1,3),(2,3),(3,3)
    ! ...
    ! THE OLD OUTPUT OF COEFS FROM MADLOOP IS
    ! RANK=0: (,)
    ! RANK=1: (0,),(1,),(2,),(3,)
    ! RANK=2: (0,0),(0,1),(0,2),(0,3),(1,1),(2,1),(3,1),(2,2),(2,3),(3,3)
    ! ...
    !
    ! ARGUMENTS
    IMPLICIT NONE
    INTEGER,INTENT(IN)::RANK,NLOOPCOEFS
    COMPLEX(KIND(1d0)),DIMENSION(0:NLOOPCOEFS-1,3),INTENT(IN)::OLDCOEFS
    COMPLEX(KIND(1d0)),DIMENSION(0:NLOOPCOEFS-1,3),INTENT(OUT)::NEWCOEFS
    !
    ! LOCAL VARIABLES
    !
    INTEGER::I
    ! MAX RANK SET AS 10
    ! Sum((3+r)*(2+r)*(1+r)/6,{r,0,10})=1001
    INTEGER,PARAMETER::LOOPMAXCOEFS_IREGI=1001
    INTEGER,DIMENSION(0:LOOPMAXCOEFS_IREGI-1)::POS
    SAVE POS
    LOGICAL::INIT=.TRUE.
    SAVE INIT
    ! ----------
    ! BEGIN CODE
    ! ----------
            
    IF(INIT)THEN
       IF(NLOOPCOEFS.GT.LOOPMAXCOEFS_IREGI)&
            STOP "ERROR:LOOPMAXCOEFS_IREGI IS TOO SMALL!!!"
       INIT=.FALSE.
       ! ASSIGN THE POSITION OF POS FOR SWAP
       CALL ASSIGN_PJPOS(POS)
    ENDIF
    
    DO I=0,NLOOPCOEFS-1
    !   NEWCOEFS(I,1:3)=OLDCOEFS(POS(I),1:3)
       NEWCOEFS(POS(I),1:3)=OLDCOEFS(I,1:3)
    ENDDO
    
  END SUBROUTINE SORT_IREGICOEFS

  SUBROUTINE ASSIGN_PJPOS(POS)
    !
    ! ASSIGN THE POSITION OF POS FOR SWAP
    !
    !
    IMPLICIT NONE
    !
    ! CONSTANS
    !
    ! MAX RANK SET AS 10
    ! Sum((3+r)*(2+r)*(1+r)/6,{r,0,10})=1001 
    INTEGER,PARAMETER::LOOPMAXCOEFS_IREGI=1001,MAXRANK=10
    ! 
    ! ARGUMENTS
    ! 
    INTEGER,DIMENSION(0:LOOPMAXCOEFS_IREGI-1),INTENT(OUT)::POS
    !
    ! LOCAL VARIABLES
    !
    INTEGER::I,J,K,SHIFT,DN
    INTEGER,DIMENSION(MAXRANK)::POSINDEX,PJPOSINDEX
    ! ----------
    ! BEGIN CODE
    ! ----------
    POS(0)=0
    DO I=1,4
       POS(I)=I
    ENDDO
    SHIFT=4
    DO J=2,MAXRANK
       DN=(J+3)*(J+2)*(J+1)/6
       POSINDEX(1:MAXRANK)=0
       PJPOSINDEX(1:MAXRANK)=0
       DO I=1,DN
          IF(I.GT.1)CALL NEXTINDEX(J,POSINDEX)
          CALL CONVERT_PJPOSINDEX(J,POSINDEX,PJPOSINDEX)
          K=DN-QPOLYPOS(J,PJPOSINDEX)+1+SHIFT
          !POS(K)=I+SHIFT
          POS(I+SHIFT)=K
       ENDDO
       SHIFT=SHIFT+DN
    ENDDO
    
  END SUBROUTINE ASSIGN_PJPOS

  SUBROUTINE NEXTINDEX(RANK,POSINDEX)
    !
    ! CALL FOR THE NEXT INDEX
    !
    IMPLICIT NONE
    !
    ! CONSTANTS
    !
    INTEGER,PARAMETER::MAXRANK=10
    !
    ! ARGUMENTS
    !
    INTEGER,INTENT(IN)::RANK
    INTEGER,DIMENSION(MAXRANK),INTENT(INOUT)::POSINDEX
    !
    ! LOCAL VARIABLES
    !
    INTEGER::I
    ! ----------
    ! BEGIN CODE
    ! ----------
    DO I=1,RANK
       POSINDEX(I)=POSINDEX(I)+1
       IF(POSINDEX(I).GT.3)THEN
          POSINDEX(I)=0
          IF(I.EQ.RANK)THEN
             RETURN
          ENDIF
       ELSE
          IF(I.GT.1)THEN
             POSINDEX(1:I-1)=POSINDEX(I)
          ENDIF
          RETURN
       ENDIF
    ENDDO
    
  END SUBROUTINE NEXTINDEX

  SUBROUTINE CONVERT_PJPOSINDEX(RANK,POSINDEX,PJPOSINDEX)
    !
    ! CONVERT POSINDEX TO PJPOSINDEX
    !
    IMPLICIT NONE
    !
    ! CONSTANTS
    !
    INTEGER,PARAMETER::MAXRANK=10
    !
    ! ARGUMENTS
    !
    INTEGER,INTENT(IN)::RANK
    INTEGER,DIMENSION(MAXRANK),INTENT(IN)::POSINDEX
    INTEGER,DIMENSION(MAXRANK),INTENT(OUT)::PJPOSINDEX
    !
    ! LOCAL VARIABLES
    !
    INTEGER::I
    ! ----------
    ! BEGIN CODE
    ! ----------
    DO I=1,RANK
       PJPOSINDEX(RANK+1-I)=3-POSINDEX(I)
    ENDDO
    RETURN
  END SUBROUTINE CONVERT_PJPOSINDEX

  FUNCTION QPOLYPOS(RANK,POSINDEX)
    !
    ! COMPUTATION THE RELATIVE POSITION OF INDEX WITH RANK
    ! IN THE *OLD* MADLOOP CONVENTION
    !
    IMPLICIT NONE
    !
    ! CONSTANTS
    !
    INTEGER,PARAMETER::MAXRANK=10
    !
    ! ARGUMENTS
    !
    INTEGER,INTENT(IN)::RANK
    INTEGER,DIMENSION(MAXRANK),INTENT(IN)::POSINDEX
    INTEGER::QPOLYPOS
    !
    ! LOCAL VARIABLES
    !
    INTEGER::I,J,IMIN
    ! ----------
    ! BEGIN CODE
    ! ----------

    IF(RANK.EQ.0)THEN
       QPOLYPOS=1
       RETURN
    ENDIF
    
    IF(RANK.EQ.1)THEN
       QPOLYPOS=POSINDEX(1)+1
       RETURN
    ENDIF
    
    QPOLYPOS=POSINDEX(1)-POSINDEX(2)+1
    DO I=2,RANK
       IF(I.EQ.RANK)THEN
          IMIN=0
       ELSE
          IMIN=POSINDEX(I+1)
       ENDIF
       DO J=IMIN,POSINDEX(I)-1
          QPOLYPOS=QPOLYPOS+QPOLYNUMBER(J,I-1)
       ENDDO
    ENDDO
    RETURN
  END FUNCTION QPOLYPOS

  FUNCTION NEWQPOLYPOS(RANK,POSINDEX)
    !
    ! COMPUTATION THE RELATIVE POSITION OF INDEX WITH RANK
    ! IN THE *NEW* MADLOOP CONVENTION
    !
    IMPLICIT NONE
    !
    ! CONSTANTS
    !
    INTEGER,PARAMETER::MAXRANK=10
    !
    ! ARGUMENTS
    !
    INTEGER,INTENT(IN)::RANK
    INTEGER,DIMENSION(MAXRANK),INTENT(IN)::POSINDEX
    INTEGER::NEWQPOLYPOS
    !
    ! LOCAL VARIABLES
    !
    INTEGER::I,J,IMIN
    ! ----------
    ! BEGIN CODE
    ! ----------                                                                                                                                                                                            

    IF(RANK.EQ.0)THEN
       NEWQPOLYPOS=1
       RETURN
    ENDIF

    IF(RANK.EQ.1)THEN
       NEWQPOLYPOS=POSINDEX(1)+1
       RETURN
    ENDIF

    NEWQPOLYPOS=1
    DO I=1,RANK
       IF(POSINDEX(RANK-I+1).EQ.0)THEN
          IMIN=0
       ELSE
          ! Eq.(3.4.6) in Valentin's PhD Thesis
          IMIN=factorial(POSINDEX(RANK-I+1)+I-1)/factorial(I)&
               /factorial(POSINDEX(RANK-I+1)-1)
       ENDIF
       NEWQPOLYPOS=NEWQPOLYPOS+IMIN
    ENDDO
    RETURN
  END FUNCTION NEWQPOLYPOS

  FUNCTION QPOLYNUMBER(I,RANK)
    !
    ! THE INDEPENDENT NUMBER OF Q POLY WITH \MU=I,...,3 AND RANK
    !
    IMPLICIT NONE
    !
    ! CONSTANTS
    !
    !
    ! ARGUMENTS
    !
    INTEGER,INTENT(IN)::I,RANK
    INTEGER::QPOLYNUMBER
    !
    ! LOCAL VARIABLES
    !
    ! ----------
    ! BEGIN CODE
    ! ----------
    SELECT CASE(I)
    CASE(0)
       QPOLYNUMBER=(3+RANK)*(2+RANK)*(1+RANK)/6
    CASE(1)
       QPOLYNUMBER=(2+RANK)*(1+RANK)/2
    CASE(2)
       QPOLYNUMBER=(1+RANK)
    CASE(3)
       QPOLYNUMBER=1
    CASE DEFAULT
       STOP 'I must be >= 0 and <=3 in QPOLYNUMBER.'
    END SELECT
    RETURN
  END FUNCTION QPOLYNUMBER

  FUNCTION POS2RANK(ipos)
    IMPLICIT NONE
    INTEGER,INTENT(IN)::ipos
    INTEGER::POS2RANK
    LOGICAL::INIT=.TRUE.
    ! NOW ITS MAX RANK IS 10
    INTEGER,PARAMETER::MAXRANK=10
    INTEGER,DIMENSION(0:MAXRANK)::IRANGE
    INTEGER::I
    SAVE IRANGE,INIT
    IF(INIT)THEN
       IRANGE(0)=0
       DO I=1,MAXRANK
          IRANGE(I)=IRANGE(I-1)+(I+3)*(I+2)*(I+1)/6
       ENDDO
       INIT=.FALSE.
    ENDIF
    IF(ipos.EQ.0)THEN
       POS2RANK=0
       RETURN
    ENDIF
    DO I=1,MAXRANK
       IF(ipos.LE.IRANGE(I))THEN
          POS2RANK=I
          RETURN
       ENDIF
    ENDDO
    WRITE(*,*)"ERROR in POS2RANK,ipos=",ipos
    STOP
  END FUNCTION POS2RANK
END MODULE FUNLIB
