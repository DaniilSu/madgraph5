      subroutine HwU_output(idummy)
      integer idummy
      write (*,*) 'HwU_output should not be called',idummy
      stop 1
      end

      subroutine HwU_add_points
      end

      subroutine HwU_accum_iter(ldummy,idummy)
      logical ldummy
      integer idummy
      end
