
import os

class MrgGkkTask(Task):
    """Merge npert gkk.nc files for a single q-point."""

    def __init__(self, gkk_fnames, out_gkk_fname):
        self.gkk_fnames = gkk_fnames
        self.out_gkk_fname = out_gkk_fname

    def write(self):
        pass

    def run(self):
        from merge_gkk_nc import merge_gkk_nc
        merge_gkk_nc(self.gkk_fnames, self.out_gkk_fname)
        return self.get_status()

    def get_status(self):
        """
        Return the status of the task. Possible status are:
        Completed, Unstarted, Unfinished, Unknown.
        """
        if os.path.exists(self.out_gkk_fname):
            return self._STATUS_COMPLETED
        else:
            return self._STATUS_UNKNOWN

    @property
    def gkk_fname(self)
        return self.out_gkk_fname

# =========================================================================== #

class MrgGkkFlow(Workflow):
    """Merge npert gkk.nc files for a list of nqpt q-points."""

    def __init__(self, gkk_fnames_2D, out_fnames=None)
        """
        Executes a list of N MrgGkkTasks.

        Arguments
        ---------

        gkk_fnames_2D [nqpt, npert]
        """

        for i, gkk_fnames in enumerate(gkk_fnames_2D):

            d0 = os.path.dirname(gkk_fnames[0])
            if all([d == d0] for d in map(os.path.dirname, gkk_fnames)]):
                dirname = d0
            else:
                dirname = None

            if out_fnames is None:
                if dirname is not None:
                    out_fname = os.path.join(dirname, 'odat_GKK.nc')
                else raise Exception('output file name not provided')
            else:
                out_fname = out_fnames[i]

            task = MrgGkkTask(gkk_fnames, out_fname)
            self.add_task(task)



