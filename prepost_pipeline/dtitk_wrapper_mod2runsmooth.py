__author__ = 'kjordan'

from nipype.interfaces.base import TraitedSpec, CommandLineInputSpec, CommandLine, File, traits, isdefined, split_filename
import os

#TODO: fix all wrappers to reflect the one with dtitkScalarVol

class dtitkTVAdjustVoxSpInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc="image to resample", exists=True, mandatory=True, position=0, argstr="-in %s")
    in_target = traits.Str(desc='target volume', exists=True, mandatory=False, position=2, \
                            argstr="-target %s")
    in_voxsz = traits.Str(desc='resampled voxel size', exists=True, mandatory=False, position=3, \
                          argstr="-vsize %s")
    out_path = traits.Str(desc='output path', exists=True, mandatory=True, position=1, \
                         argstr="-out %s")
    origin = traits.Str(desc='xyz voxel size', exists=True, mandatory=False, position=4, argstr='-origin %s')

class dtitkTVAdjustVoxSpOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)

class dtitkTVAdjustVoxSpTask(CommandLine):
    input_spec = dtitkTVAdjustVoxSpInputSpec
    output_spec = dtitkTVAdjustVoxSpOutputSpec
    _cmd = 'TVAdjustVoxelspace'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs

class dtitkSVAdjustVoxSpInputSpec(CommandLineInputSpec):
    in_volume = traits.Str(desc="image to resample", exists=True, mandatory=True, position=0, argstr="-in %s")
    in_target = traits.Str(desc='target volume', exists=True, mandatory=False, position=2, \
                            argstr="-target %s")
    in_voxsz = traits.Str(desc='resampled voxel size', exists=True, mandatory=False, position=3, \
                          argstr="-vsize %s")
    out_path = traits.Str(desc='output path', exists=True, mandatory=True, position=1, \
                         argstr="-out %s")
    origin = traits.Str(desc='xyz voxel size', exists=True, mandatory=False, position=4, argstr='-origin %s')

class dtitkSVAdjustVoxSpOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)

class dtitkSVAdjustVoxSpTask(CommandLine):
    input_spec = dtitkSVAdjustVoxSpInputSpec
    output_spec = dtitkSVAdjustVoxSpOutputSpec
    _cmd = 'SVAdjustVoxelspace'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs

class dtitkTVResampleInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc="image to resample", exists=True, mandatory=True, position=0, argstr="-in %s")
    in_arraysz = traits.Str(desc='resampled array size', exists=True, mandatory=True, position=1, \
                            argstr="-size %s")
    in_voxsz = traits.Str(desc='resampled voxel size', exists=True, mandatory=True, position=2, \
                          argstr="-vsize %s")
    out_path = traits.Str(desc='output path', exists=True, mandatory=True, position=3, \
                         argstr="-out %s")

class dtitkTVResampleOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)

class dtitkTVResampleTask(CommandLine):
    input_spec = dtitkTVResampleInputSpec
    output_spec = dtitkTVResampleOutputSpec
    _cmd = 'TVResample'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs

class dtitkSVResampleInputSpec(CommandLineInputSpec):
    in_volume = traits.Str(desc="image to resample", exists=True, mandatory=True, position=0, argstr="-in %s")
    in_arraysz = traits.Str(desc='resampled array size', exists=True, mandatory=True, position=1, \
                            argstr="-size %s")
    in_voxsz = traits.Str(desc='resampled voxel size', exists=True, mandatory=True, position=2, \
                          argstr="-vsize %s")
    out_path = traits.Str(desc='output path', exists=True, mandatory=True, position=3, \
                         argstr="-out %s")

class dtitkSVResampleOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)

class dtitkSVResampleTask(CommandLine):
    input_spec = dtitkSVResampleInputSpec
    output_spec = dtitkSVResampleOutputSpec
    _cmd = 'SVResample'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs

class dtitkTVtoolInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc="image to resample", exists=True, mandatory=True, position=0, argstr="-in %s")
    in_flag = traits.Enum('fa', 'tr', 'ad', 'rd', 'pd', 'rgb', exists=True, mandatory=True, position=1, \
                          argstr="-%s", desc='')

class dtitkTVtoolOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)

class dtitkTVtoolTask(CommandLine):
    input_spec = dtitkTVtoolInputSpec
    output_spec = dtitkTVtoolOutputSpec
    _cmd = 'TVtool'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.in_tensor.replace('.nii.gz', '_'+self.inputs.in_flag+'.nii.gz')
        return outputs

class dtitkBinThreshInputSpec(CommandLineInputSpec):
    in_image = traits.Str(desc='', exists=True, mandatory=True, position=0, argstr="%s")
    out_path = traits.Str(desc='', exists=True, mandatory=True, position=1, argstr="%s")
    in_numbers = traits.Str(desc='LB UB inside_value outside_value', exists=True, mandatory=True, position=2, argstr="%s")

class dtitkBinThreshOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)

class dtitkBinThreshTask(CommandLine):
    input_spec = dtitkBinThreshInputSpec
    output_spec = dtitkBinThreshOutputSpec
    _cmd='BinaryThresholdImageFilter'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs

class dtitkRigidInputSpec(CommandLineInputSpec):
    in_fixed_tensor = traits.Str(desc="fixed diffusion tensor image", exists=True, mandatory=True, \
                    position=0, argstr="%s")
    in_moving_txt = traits.Str(desc="moving list of diffusion tensor image paths", exists=True, mandatory=True, \
                     position=1, argstr="%s")
    in_similarity_metric = traits.Enum('EDS', 'GDS', 'DDS', 'NMI', \
                                exists=True, mandatory=True, position=3, argstr="%s", desc="similarity metric")

class dtitkRigidOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)
    out_file_xfm = traits.File(exists=True)

class dtitkRigidTask(CommandLine):
    input_spec = dtitkRigidInputSpec
    output_spec = dtitkRigidOutputSpec
    _cmd = 'dti_rigid_sn'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file_xfm'] = self.inputs.in_fixed_tensor.replace('.nii.gz','.aff')
        outputs['out_file'] = self.inputs.in_fixed_tensor.replace('.nii.gz', '_aff.nii.gz')
        return outputs

class dtitkAffineInputSpec(CommandLineInputSpec):
    in_fixed_tensor = traits.Str(desc="fixed diffusion tensor image", exists=True, mandatory=True, \
                    position=0, argstr="%s")
    in_moving_txt = traits.Str(desc="moving list of diffusion tensor image paths", exists=True, mandatory=True, \
                     position=1, argstr="%s")
    in_similarity_metric = traits.Enum('EDS', 'GDS', 'DDS', 'NMI', \
                                exists=True, mandatory=True, position=3, argstr="%s", desc = "similarity metric")
    in_usetrans_flag = traits.Enum('--useTrans', '', exists=True, mandatory=False, position=4, argstr="%s", \
                                   desc="initialize using rigid transform??")

class dtitkAffineOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)
    out_file_xfm = traits.File(exists=True)

class dtitkAffineTask(CommandLine):
    input_spec = dtitkAffineInputSpec
    output_spec = dtitkAffineOutputSpec
    _cmd = 'dti_affine_sn'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file_xfm'] = self.inputs.in_fixed_tensor.replace('.nii.gz','.aff')
        outputs['out_file'] = self.inputs.in_fixed_tensor.replace('.nii.gz', '_aff.nii.gz')
        return outputs

class dtitkDiffeoInputSpec(CommandLineInputSpec):
    in_fixed_tensor = traits.Str(desc="fixed diffusion tensor image", exists=True, mandatory=True, \
                    position=0, argstr="%s")
    in_moving_txt = traits.Str(desc="moving list of diffusion tensor image paths", exists=True, mandatory=True, \
                     position=1, argstr="%s")
    in_mask = traits.Str(desc="mask", exists=True, mandatory=True, position=2, argstr="%s")
    in_numbers = traits.Str(desc='#iters ftol', exists=True, mandatory=True, position=3, argstr="%s")

class dtitkDiffeoOutputSpec(TraitedSpec):
    out_file = traits.File(exists=True)
    out_file_xfm = traits.File(exists=True)

class dtitkDiffeoTask(CommandLine):
    input_spec = dtitkDiffeoInputSpec
    output_spec = dtitkDiffeoOutputSpec
    _cmd = 'dti_diffeomorphic_sn'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file_xfm'] = self.inputs.in_fixed_tensor.replace('.nii.gz','_aff_diffeo.df.nii.gz')
        outputs['out_file'] = self.inputs.in_fixed_tensor.replace('.nii.gz', '_aff_diffeo.nii.gz')
        return outputs

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
        outputs['out_file'] = self.inputs.in_df.replace('.df.nii.gz', '_combo.df.nii.gz')
        return outputs

class dtitkdiffeoSymTensor3DVolInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc='moving tensor', exists=True, mandatory=True, position=0, argstr="-in %s")
    in_xfm = traits.Str(desc='transform to apply', exists=True, mandatory=True, position=1, argstr="-trans %s")
    in_target = traits.Str(desc='', exists=True, mandatory=True, position=2, argstr="-target %s")
    out_path = traits.Str(desc='', exists=True, mandatory=True, position=3, argstr="-out %s")

class dtitkdiffeoSymTensor3DVolOutputSpec(TraitedSpec):
    out_file = traits.File(desc='cheese', exists=True)

class dtitkdiffeoSymTensor3DVolTask(CommandLine):
    input_spec = dtitkdiffeoSymTensor3DVolInputSpec
    output_spec = dtitkdiffeoSymTensor3DVolOutputSpec
    _cmd = 'deformationSymTensor3DVolume'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs

class dtitkaffSymTensor3DVolInputSpec(CommandLineInputSpec):
    in_tensor = traits.Str(desc='moving tensor', exists=True, mandatory=True, position=0, argstr="-in %s")
    in_xfm = traits.Str(desc='transform to apply', exists=True, mandatory=True, position=1, argstr="-trans %s")
    in_target = traits.Str(desc='', exists=True, mandatory=True, position=2, argstr="-target %s")
    out_path = traits.Str(desc='', exists=True, mandatory=True, position=3, argstr="-out %s")

class dtitkaffSymTensor3DVolOutputSpec(TraitedSpec):
    out_file = traits.File(desc='cheese', exists=True)

class dtitkaffSymTensor3DVolTask(CommandLine):
    input_spec = dtitkaffSymTensor3DVolInputSpec
    output_spec = dtitkaffSymTensor3DVolOutputSpec
    _cmd = 'affineSymTensor3DVolume'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs

class dtitkaffScalarVolInputSpec(CommandLineInputSpec):
    in_volume = traits.Str(desc='moving volume', exists=True, mandatory=True, position=0, argstr="-in %s")
    in_xfm = traits.Str(desc='transform to apply', exists=True, mandatory=True, position=1, argstr="-trans %s")
    in_target = traits.Str(desc='', exists=True, mandatory=True, position=2, argstr="-target %s")
    out_path = traits.Str(desc='', mandatory=False, position=3, argstr="-out %s",
                          name_source="in_volume", name_template="%s_affxfmd.nii.gz")

class dtitkaffScalarVolOutputSpec(TraitedSpec):
    out_file = traits.File(desc='moved volume', exists=True)

class dtitkaffScalarVolTask(CommandLine):
    input_spec = dtitkaffScalarVolInputSpec
    output_spec = dtitkaffScalarVolOutputSpec
    _cmd = 'affineScalarVolume'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        if not isdefined(outputs['out_file']) and isdefined(self.inputs.in_volume):
            #outputs['out_file'] = os.path.abspath(self._gen_outfilename())
            outputs['out_file'] = os.path.abspath(self.inputs.in_volume).replace('.nii.gz', '_affxfmd.nii.gz')
        else:
            outputs['out_file'] = os.path.abspath(outputs['out_file'] )
        return outputs



class dtitkdiffeoScalarVolInputSpec(CommandLineInputSpec):
    in_volume = traits.Str(desc='moving volume', exists=True, mandatory=True, position=0, argstr="-in %s")
    in_xfm = traits.Str(desc='transform to apply', exists=True, mandatory=True, position=2, argstr="-trans %s")
    in_target = traits.Str(desc='', exists=True, mandatory=True, position=3, argstr="-target %s")
    out_path = traits.Str(desc='', position=1, argstr="-out %s")
    in_vsize = traits.Str(desc='', exists=True, mandatory=False, position=4, argstr="-vsize %s")
    in_flip = traits.Str(desc='', exists=True, mandatory=False, position=5, argstr="-flip %s")
    in_type = traits.Str(desc='', exists=True, mandatory=False, position=6, argstr="-type %s")
    in_interp = traits.Str(desc='0 trilin, 1 NN', exists=True, mandatory=False, position=7, argstr="-interp %s")

class dtitkdiffeoScalarVolOutputSpec(TraitedSpec):
    out_file = traits.File(desc='moved volume', exists=True)

class dtitkdiffeoScalarVolTask(CommandLine):
    input_spec = dtitkdiffeoScalarVolInputSpec
    output_spec = dtitkdiffeoScalarVolOutputSpec
    _cmd = 'deformationScalarVolume'

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        if not isdefined(outputs['out_file']) and isdefined(self.inputs.in_volume):
            outputs['out_file'] = os.path.abspath(self._gen_outfilename())
        else:
            outputs['out_file'] = os.path.abspath(outputs['out_file'] )
        return outputs

    def _gen_filename(self, name):
        if name is 'out_file':
            return self._gen_outfilename()
        else:
            return None

    def _gen_outfilename(self):
        print "diff worked"
        _, name, _ = split_filename(self.inputs.out_path)
        if isdefined(self.inputs.out_path):
            outname = self.inputs.out_path
        else:
            outname = 'TESTINGdiffeo.nii.gz'
        return outname


    '''
    def _gen_filename(self, name):
        print "diffeo worked"
        out_file = self.inputs.out_file
        if not isdefined(out_file) and isdefined(self.inputs.in_volume):
            out_file = self._gen_filename(self.inputs.in_file, suffix='_diffeoxfmd')
        return os.path.abspath(out_file)

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs['out_file'] = self.inputs.out_path
        return outputs'''