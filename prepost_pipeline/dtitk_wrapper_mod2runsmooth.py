__author__ = 'kjordan'

from nipype.interfaces.base import TraitedSpec, CommandLineInputSpec, CommandLine, File, traits

class dtitkResampleInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc="image to resample", exists=True, mandatory=True, position=0, argstr="-in %s")
    in_arraysz = traits.Str(desc='resampled array size', exists=True, mandatory=True, position=1, \
                            argstr="-size %s")
    in_voxsz = traits.Str(desc='resampled voxel size', exists=True, mandatory=True, position=2, \
                          argstr="-vsize %s")
    out_loc = traits.Str(desc='output path', exists=True, mandatory=True, position=3, \
                         argstr="-out %s")

class dtitkResampleTask(CommandLine):
    input_spec = dtitkResampleInputSpec
    _cmd = 'TVResample'

class dtitkTVtoolInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc="image to resample", exists=True, mandatory=True, position=0, argstr="-in %s")
    in_flag = traits.Enum('fa', 'tr', 'ad', 'rd', 'pd', 'rgb', exists=True, mandatory=True, position=1, \
                          argstr="-%s", desc='')

class dtitkTVtoolTask(CommandLine):
    input_spec = dtitkTVtoolInputSpec
    _cmd = 'TVtool'


class dtitkBinThreshInputSpec(CommandLineInputSpec):
    in_image = traits.Str(desc='', exists=True, mandatory=True, position=0, argstr="%s")
    out_path = traits.Str(desc='', exists=True, mandatory=True, position=1, argstr="%s")
    in_numbers = traits.Str(desc='LB UB inside_value outside_value', exists=True, mandatory=True, position=2, argstr="%s")

class dtitkBinThreshTask(CommandLine):
    input_spec = dtitkBinThreshInputSpec
    _cmd='BinaryThresholdImageFilter'


class dtitkRigidInputSpec(CommandLineInputSpec):
    in_fixed_tensor = traits.Str(desc="fixed diffusion tensor image", exists=True, mandatory=True, \
                    position=0, argstr="%s")
    in_moving_txt = traits.Str(desc="moving list of diffusion tensor image paths", exists=True, mandatory=True, \
                     position=1, argstr="%s")
    in_similarity_metric = traits.Enum('EDS', 'GDS', 'DDS', 'NMI', \
                                exists=True, mandatory=True, position=3, argstr="%s", desc="similarity metric")

class dtitkRigidTask(CommandLine):
    input_spec = dtitkRigidInputSpec
    _cmd = 'dti_rigid_sn'

class dtitkAffineInputSpec(CommandLineInputSpec):
    in_fixed_tensor = traits.Str(desc="fixed diffusion tensor image", exists=True, mandatory=True, \
                    position=0, argstr="%s")
    in_moving_txt = traits.Str(desc="moving list of diffusion tensor image paths", exists=True, mandatory=True, \
                     position=1, argstr="%s")
    in_similarity_metric = traits.Enum('EDS', 'GDS', 'DDS', 'NMI', \
                                exists=True, mandatory=True, position=3, argstr="%s", desc = "similarity metric")
    in_usetrans_flag = traits.Enum('--useTrans', '', exists=True, mandatory=False, position=4, argstr="%s", \
                                   desc="initialize using rigid transform??")

class dtitkAffineTask(CommandLine):
    input_spec = dtitkAffineInputSpec
    _cmd = 'dti_affine_sn'

class dtitkDiffeoInputSpec(CommandLineInputSpec):
    in_fixed_tensor = traits.Str(desc="fixed diffusion tensor image", exists=True, mandatory=True, \
                    position=0, argstr="%s")
    in_moving_txt = traits.Str(desc="moving list of diffusion tensor image paths", exists=True, mandatory=True, \
                     position=1, argstr="%s")
    in_mask = traits.Str(desc="mask", exists=True, mandatory=True, position=2, argstr="%s")
    in_numbers = traits.Str(desc='#iters ftol', exists=True, mandatory=True, position=3, argstr="%s")

class dtitkDiffeoTask(CommandLine):
    input_spec = dtitkDiffeoInputSpec
    _cmd = 'dti_diffeomorphic_sn'

class dtitkComposeXfmInputSpec(CommandLineInputSpec):
    in_df = traits.Str(desc='diffeomorphic file.df.nii.gz', exists=True, mandatory=True, position=1, argstr="-df %s")
    in_aff = traits.Str(desc='affine file.aff', exists=True, mandatory=True, position=0, argstr="-aff %s")
    out_path = traits.Str(desc='output_path', exists=True, mandatory=True, position=2, argstr="-out %s")

class dtitkComposeXfmOutputSpec(TraitedSpec):
    out_file = traits.File(desc='cheese', exists=True)

class dtitkComposeXfmTask(CommandLine):
    input_spec = dtitkComposeXfmInputSpec
    output_spec = dtitkComposeXfmOutputSpec
    _cmd = 'dfRightComposeAffine'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.in_df.replace()
        return outputs

class dtitkSymTensor3DVolInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc='moving tensor', exists=True, mandatory=True, position=0, argstr="-in %s")
    in_xfm = traits.Str(desc='transform to apply', exists=True, mandatory=True, position=1, argstr="-trans %s")
    in_target = traits.Str(desc='', exists=True, mandatory=True, position=2, argstr="-target %s")
    out_path = traits.Str(desc='', exists=True, mandatory=True, position=3, argstr="-out %s")

class dtitkComposeXfmOutputSpec(TraitedSpec):
    out_file = traits.File(desc='cheese', exists=True)

class dtitkSymTensor3DVolTask(CommandLine):
    input_spec = dtitkSymTensor3DVolInputSpec
    _cmd = 'deformationSymTensor3DVolume'

class dtitkScalarVolInputSpec(CommandLineInputSpec):
    in_volume = traits.Str(desc='moving volume', exists=True, mandatory=True, position=0, argstr="-in %s")
    in_xfm = traits.Str(desc='transform to apply', exists=True, mandatory=True, position=1, argstr="-trans %s")
    in_target = traits.Str(desc='', exists=True, mandatory=True, position=2, argstr="-target %s")
    out_path = traits.Str(desc='', exists=True, mandatory=True, position=3, argstr="-out %s")

class dtitkScalarVolTask(CommandLine):
    input_spec = dtitkScalarVolInputSpec
    _cmd = 'deformationScalarVolume'

class dtitkRotBvecInputSpec(CommandLineInputSpec):
    in_affxfm = traits.Str(desc='transform to apply', exists=True, mandatory=True, position=0, argstr="%s")
    in_bvecs = traits.Str(desc='bvec file', exists=True, mandatory=True, position=1, argstr="%s")

class dtitkRotBvecTask(CommandLine):
    input_spec = dtitkRotBvecInputSpec
    _cmd = '/home/kjordan/python_code/myscripts/prepost_pipeline/rotate_bvecs_dtitk_kmj'